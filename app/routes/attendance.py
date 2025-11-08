from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from app.models.student import Student
from app.models.class_model import Class
from app.services.face_recognition_service import FaceRecognitionService
from app.services.attendance_service import AttendanceService
import base64
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')


@bp.route('/sessions/start', methods=['POST'])
@login_required
def start_session():
    """Start attendance session"""
    data = request.get_json()

    try:
        class_id = data.get('class_id')
        session_name = data.get('session_name', 'Session')
        notes = data.get('notes')

        # Verify class ownership
        class_obj = Class.query.get_or_404(class_id)
        if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
            return jsonify({'error': 'Akses ditolak'}), 403

        # Create session
        session = AttendanceService.start_session(
            class_id=class_id,
            session_name=session_name,
            created_by_id=current_user.id,
            notes=notes
        )

        return jsonify({
            'message': 'Session dimulai',
            'session': session.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error start session: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/sessions/<int:session_id>/end', methods=['POST'])
@login_required
def end_session(session_id):
    """End attendance session"""
    session = AttendanceSession.query.get_or_404(session_id)

    # Verify ownership
    if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        session = AttendanceService.end_session(session_id)
        return jsonify({
            'message': 'Session ditutup',
            'session': session.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error end session: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/sessions/<int:session_id>/status', methods=['GET'])
@login_required
def get_session_status(session_id):
    """Get real-time session status"""
    session = AttendanceSession.query.get_or_404(session_id)

    # Verify ownership
    if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        report = AttendanceService.get_session_attendance(session_id)
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error get status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/capture', methods=['POST'])
@login_required
def capture_face():
    """
    Capture dan recognize face dari webcam frame
    Expects: {
        'session_id': int,
        'image_data': base64 encoded image
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        image_data = data.get('image_data')

        if not session_id or not image_data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Get session
        session = AttendanceSession.query.get_or_404(session_id)

        # Verify ownership
        if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
            return jsonify({'error': 'Akses ditolak'}), 403

        # Decode base64 image
        try:
            # Remove data URL header jika ada
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Error decode image: {str(e)}")
            return jsonify({'error': 'Invalid image format'}), 400

        # Extract face encoding dari frame
        unknown_encoding = FaceRecognitionService.encode_face(image)

        if unknown_encoding is None:
            return jsonify({
                'detected': False,
                'message': 'Tidak ada wajah terdeteksi'
            }), 200

        # Get all active students di kelas
        class_id = session.class_id
        students = Student.query.filter_by(
            class_id=class_id,
            is_active=True
        ).all()

        # Filter students dengan face encoding
        known_students = []
        for student in students:
            encoding = student.get_face_encoding()
            if encoding is not None:
                known_students.append((student, encoding))

        if not known_students:
            return jsonify({
                'detected': False,
                'message': 'Tidak ada mahasiswa dengan face encoding di kelas'
            }), 200

        # Compare faces
        matched_student, confidence = FaceRecognitionService.compare_faces(
            unknown_encoding,
            known_students
        )

        if matched_student is None:
            return jsonify({
                'detected': True,
                'matched': False,
                'message': 'Wajah tidak dikenal'
            }), 200

        # Check confidence threshold
        min_confidence = current_app.config.get('MIN_CONFIDENCE_SCORE', 0.4)
        if confidence < min_confidence:
            return jsonify({
                'detected': True,
                'matched': False,
                'message': f'Confidence {confidence:.2f} di bawah threshold',
                'confidence': confidence
            }), 200

        # Record attendance
        try:
            record = AttendanceService.record_attendance(
                student_id=matched_student.id,
                session_id=session_id,
                confidence_score=confidence,
                is_manual=False
            )

            return jsonify({
                'detected': True,
                'matched': True,
                'message': f'Kehadiran tercatat: {matched_student.name}',
                'student': {
                    'id': matched_student.id,
                    'student_id': matched_student.student_id,
                    'name': matched_student.name
                },
                'confidence': f"{confidence:.2f}",
                'timestamp': record.timestamp.isoformat()
            }), 200

        except Exception as e:
            # Duplicate entry - sudah tercatat
            logger.warning(f"Duplikat attendance: {matched_student.student_id}")
            return jsonify({
                'detected': True,
                'matched': True,
                'message': f'{matched_student.name} sudah tercatat',
                'student': {
                    'id': matched_student.id,
                    'student_id': matched_student.student_id,
                    'name': matched_student.name
                },
                'confidence': f"{confidence:.2f}",
                'duplicate': True
            }), 200

    except Exception as e:
        logger.error(f"Error capture face: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/manual/<int:student_id>', methods=['POST'])
@login_required
def manual_entry(student_id):
    """Manual attendance entry (fallback)"""
    data = request.get_json()
    session_id = data.get('session_id')
    notes = data.get('notes')

    try:
        # Get session
        session = AttendanceSession.query.get_or_404(session_id)

        # Verify ownership
        if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
            return jsonify({'error': 'Akses ditolak'}), 403

        # Get student
        student = Student.query.get_or_404(student_id)

        # Check if student is in class
        if student.class_id != session.class_id:
            return jsonify({'error': 'Mahasiswa bukan dari kelas ini'}), 400

        # Record manual attendance
        record = AttendanceService.manual_entry(
            student_id=student_id,
            session_id=session_id,
            notes=notes or 'Manual entry'
        )

        return jsonify({
            'message': 'Kehadiran manual tercatat',
            'record': record.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error manual entry: {str(e)}")
        return jsonify({'error': str(e)}), 500
