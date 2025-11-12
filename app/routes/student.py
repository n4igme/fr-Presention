from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.class_model import Class
from app.services.face_recognition_service import FaceRecognitionService
import logging
import uuid

logger = logging.getLogger(__name__)

bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/register/<token>')
def register_with_token(token):
    """Student registration page dengan invite token"""
    # TODO: Implement token validation
    # Untuk sekarang, menggunakan query param sederhana
    student_id = request.args.get('id')
    if not student_id:
        flash('Invalid registration link', 'error')
        return redirect(url_for('auth.login'))

    student = Student.query.get_or_404(student_id)
    return render_template('student/registration.html', student=student)


@bp.route('/api/upload-photo', methods=['POST'])
def api_upload_photo():
    """Upload dan process photo untuk face registration"""
    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada foto'}), 400

    if 'student_id' not in request.form:
        return jsonify({'error': 'student_id harus dikirim'}), 400

    try:
        student_id = int(request.form.get('student_id'))
        file = request.files['photo']

        student = Student.query.get_or_404(student_id)

        # Read image
        image_data = file.read()

        # Extract face encoding
        encoding = FaceRecognitionService.encode_face(image_data)

        if encoding is None:
            return jsonify({'error': 'Tidak ada wajah terdeteksi di foto'}), 400

        # Save face encoding
        student.set_face_encoding(encoding)

        # Save photo
        photo_path = f"uploads/student_photos/{student.student_id}_{student.id}.jpg"
        with open(photo_path, 'wb') as f:
            f.write(image_data)

        student.photo_path = photo_path

        from datetime import datetime
        student.registration_date = datetime.utcnow()

        db.session.commit()

        logger.info(f"Face terdaftar untuk mahasiswa: {student.student_id}")
        return jsonify({
            'message': 'Face registration berhasil',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error upload photo: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/create', methods=['POST'])
@login_required
def api_create_student():
    """API untuk create student (untuk lecturer)"""
    if current_user.role not in ('lecturer', 'admin'):
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()

    try:
        # Validate required fields
        required_fields = ['student_id', 'name', 'class_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Field required tidak lengkap'}), 400

        # Check duplicate
        existing = Student.query.filter_by(student_id=data['student_id']).first()
        if existing:
            return jsonify({'error': 'NIM sudah terdaftar'}), 400

        # Verify class ownership
        class_obj = Class.query.get(data['class_id'])
        if not class_obj or (class_obj.lecturer_id != current_user.id and not current_user.is_admin()):
            return jsonify({'error': 'Akses ditolak'}), 403

        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            class_id=data['class_id']
        )

        db.session.add(student)
        db.session.commit()

        logger.info(f"Mahasiswa baru dibuat: {student.student_id}")
        return jsonify({
            'message': 'Mahasiswa berhasil dibuat',
            'student': student.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error create student: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/class/<int:class_id>', methods=['POST'])
@login_required
def api_create_student_for_class(class_id):
    """API untuk create student secara langsung untuk kelas tertentu (untuk frontend consistency)"""
    if current_user.role not in ('lecturer', 'admin'):
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()

    try:
        # Validate required fields
        required_fields = ['student_id', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Field required tidak lengkap'}), 400

        # Check duplicate
        existing = Student.query.filter_by(student_id=data['student_id']).first()
        if existing:
            return jsonify({'error': 'NIM sudah terdaftar'}), 400

        # Verify class ownership
        class_obj = Class.query.get(class_id)
        if not class_obj or (class_obj.lecturer_id != current_user.id and not current_user.is_admin()):
            return jsonify({'error': 'Akses ditolak'}), 403

        # Add class_id to data
        data['class_id'] = class_id

        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            class_id=class_id
        )

        db.session.add(student)
        db.session.commit()

        logger.info(f"Mahasiswa baru dibuat untuk kelas {class_id}: {student.student_id}")
        return jsonify({
            'message': 'Mahasiswa berhasil dibuat',
            'student': student.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error create student: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:student_id>', methods=['GET'])
def api_get_student(student_id):
    """Get student details"""
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict()), 200


@bp.route('/api/<int:student_id>', methods=['PUT'])
@login_required
def api_update_student(student_id):
    """Update student"""
    student = Student.query.get_or_404(student_id)

    # Check ownership
    if current_user.role not in ('admin',) and student.class_record.lecturer_id != current_user.id:
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()

    try:
        if 'name' in data:
            student.name = data['name']
        if 'email' in data:
            student.email = data['email']
        if 'phone' in data:
            student.phone = data['phone']
        if 'is_active' in data:
            student.is_active = bool(data['is_active'])

        db.session.commit()

        logger.info(f"Mahasiswa diupdate: {student.student_id}")
        return jsonify({
            'message': 'Mahasiswa berhasil diupdate',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error update student: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:student_id>', methods=['DELETE'])
@login_required
def api_delete_student(student_id):
    """Delete student"""
    student = Student.query.get_or_404(student_id)

    # Check ownership
    if current_user.role not in ('admin',) and student.class_record.lecturer_id != current_user.id:
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        db.session.delete(student)
        db.session.commit()

        logger.info(f"Mahasiswa dihapus: {student_id}")
        return jsonify({'message': 'Mahasiswa berhasil dihapus'}), 200

    except Exception as e:
        logger.error(f"Error delete student: {str(e)}")
        return jsonify({'error': str(e)}), 500
