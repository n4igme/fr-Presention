from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.class_model import Class
from app.models.student import Student
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from app.services.attendance_service import AttendanceService
import csv
import io
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('lecturer', __name__, url_prefix='/lecturer')


def lecturer_required(f):
    """Decorator untuk memastikan user adalah lecturer"""
    from functools import wraps

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in ('lecturer', 'admin'):
            flash('Akses ditolak', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/dashboard')
@lecturer_required
def dashboard():
    """Dashboard lecturer - melihat daftar kelas"""
    classes = Class.query.filter_by(lecturer_id=current_user.id).all()

    # Prepare data for template - eagerly load student counts
    classes_data = []
    total_students = 0
    for cls in classes:
        student_count = cls.students.count()
        classes_data.append({
            'id': cls.id,
            'name': cls.name,
            'code': cls.code,
            'description': cls.description,
            'academic_year': cls.academic_year,
            'semester': cls.semester,
            'students_count': student_count,
            'students': cls.students,  # Keep relationship for detail view
            'created_at': cls.created_at
        })
        total_students += student_count

    return render_template('lecturer/dashboard.html',
                         classes=classes_data,
                         total_classes=len(classes_data),
                         total_students=total_students)


@bp.route('/class/<int:class_id>')
@lecturer_required
def class_detail(class_id):
    """Detail kelas - melihat mahasiswa dan history absensi"""
    class_obj = Class.query.get_or_404(class_id)

    # Check ownership
    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        flash('Akses ditolak', 'error')
        return redirect(url_for('lecturer.dashboard'))

    students = Student.query.filter_by(class_id=class_id, is_active=True).all()
    sessions = AttendanceSession.query.filter_by(class_id=class_id).order_by(
        AttendanceSession.start_time.desc()
    ).limit(10).all()

    return render_template(
        'lecturer/class_detail.html',
        class_obj=class_obj,
        students=students,
        sessions=sessions
    )


@bp.route('/class/<int:class_id>/students')
@lecturer_required
def student_management(class_id):
    """Manage students di kelas"""
    class_obj = Class.query.get_or_404(class_id)

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        flash('Akses ditolak', 'error')
        return redirect(url_for('lecturer.dashboard'))

    students = Student.query.filter_by(class_id=class_id).all()
    return render_template('lecturer/student_management.html', class_obj=class_obj, students=students)


@bp.route('/class/<int:class_id>/attendance/<int:session_id>')
@lecturer_required
def attendance_detail(class_id, session_id):
    """Detail attendance untuk satu sesi"""
    class_obj = Class.query.get_or_404(class_id)
    session = AttendanceSession.query.get_or_404(session_id)

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        flash('Akses ditolak', 'error')
        return redirect(url_for('lecturer.dashboard'))

    report = AttendanceService.get_session_attendance(session_id)
    return render_template('lecturer/attendance_detail.html', report=report, session=session)


@bp.route('/class/<int:class_id>/attendance/new', methods=['GET', 'POST'])
@lecturer_required
def start_attendance(class_id):
    """Mulai sesi absensi baru"""
    class_obj = Class.query.get_or_404(class_id)

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        flash('Akses ditolak', 'error')
        return redirect(url_for('lecturer.dashboard'))

    if request.method == 'POST':
        session_name = request.form.get('session_name')
        notes = request.form.get('notes')

        if not session_name:
            flash('Nama sesi harus diisi', 'error')
            return redirect(url_for('lecturer.start_attendance', class_id=class_id))

        # Create session
        session = AttendanceService.start_session(
            class_id=class_id,
            session_name=session_name,
            created_by_id=current_user.id,
            notes=notes
        )

        logger.info(f"Sesi absensi dimulai: {session.id} di kelas {class_id}")
        return redirect(url_for('lecturer.attendance_capture', session_id=session.id))

    return render_template('lecturer/start_attendance.html', class_obj=class_obj)


@bp.route('/attendance/<int:session_id>/capture')
@lecturer_required
def attendance_capture(session_id):
    """Main attendance capture page dengan webcam"""
    session = AttendanceSession.query.get_or_404(session_id)
    class_obj = session.class_record

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        flash('Akses ditolak', 'error')
        return redirect(url_for('lecturer.dashboard'))

    # Get students di kelas
    students = Student.query.filter_by(class_id=class_obj.id, is_active=True).all()

    return render_template(
        'lecturer/attendance_capture.html',
        session=session,
        class_obj=class_obj,
        students=students
    )


@bp.route('/api/class/create', methods=['POST'])
@lecturer_required
def api_create_class():
    """API untuk create class"""
    data = request.get_json()

    try:
        class_obj = Class(
            name=data.get('name'),
            code=data.get('code'),
            description=data.get('description'),
            lecturer_id=current_user.id,
            academic_year=data.get('academic_year'),
            semester=int(data.get('semester', 1))
        )

        db.session.add(class_obj)
        db.session.commit()

        logger.info(f"Kelas baru dibuat: {class_obj.id}")
        return jsonify({'message': 'Kelas berhasil dibuat', 'class': class_obj.to_dict()}), 201

    except Exception as e:
        logger.error(f"Error membuat kelas: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/api/student/<int:student_id>/register', methods=['POST'])
@lecturer_required
def api_register_student_face(student_id):
    """API untuk register face mahasiswa"""
    from app.services.face_recognition_service import FaceRecognitionService

    student = Student.query.get_or_404(student_id)

    # Check ownership
    if student.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada foto'}), 400

    file = request.files['photo']

    try:
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
        student.registration_date = __import__('datetime').datetime.utcnow()

        db.session.commit()

        logger.info(f"Face terdaftar untuk mahasiswa: {student.student_id}")
        return jsonify({'message': 'Face registration berhasil'}), 200

    except Exception as e:
        logger.error(f"Error registrasi face: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/attendance/<int:session_id>/end', methods=['POST'])
@lecturer_required
def api_end_attendance(session_id):
    """API untuk akhiri sesi absensi"""
    session = AttendanceSession.query.get_or_404(session_id)
    class_obj = session.class_record

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        session = AttendanceService.end_session(session_id)
        logger.info(f"Sesi absensi ditutup: {session_id}")
        return jsonify({'message': 'Sesi absensi ditutup', 'session': session.to_dict()}), 200

    except Exception as e:
        logger.error(f"Error tutup sesi: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/attendance/<int:session_id>/report/csv')
@lecturer_required
def download_attendance_csv(session_id):
    """Download attendance report sebagai CSV"""
    session = AttendanceSession.query.get_or_404(session_id)
    class_obj = session.class_record

    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        report = AttendanceService.get_session_attendance(session_id)

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['NIM', 'Nama', 'Email', 'Status', 'Waktu Datang', 'Confidence'])

        # Data
        for detail in report['attendance_details']:
            writer.writerow([
                detail['student_id'],
                detail['name'],
                detail['email'],
                detail['status'],
                detail['time_in'],
                detail['confidence']
            ])

        # Create response
        output.seek(0)
        response_data = output.getvalue().encode('utf-8-sig')  # BOM untuk Excel

        return send_file(
            io.BytesIO(response_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"attendance_{session.id}.csv"
        )

    except Exception as e:
        logger.error(f"Error download CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/student/class/<int:class_id>', methods=['POST'])
@lecturer_required
def api_add_student_to_class(class_id):
    """API untuk tambah mahasiswa ke kelas"""
    class_obj = Class.query.get_or_404(class_id)

    # Check ownership
    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    data = request.get_json()

    try:
        # Validate required fields
        required_fields = ['student_id', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Field student_id dan name harus diisi'}), 400

        # Check duplicate
        existing = Student.query.filter_by(student_id=data['student_id']).first()
        if existing:
            return jsonify({'error': 'NIM sudah terdaftar'}), 400

        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data.get('email'),
            class_id=class_id
        )

        db.session.add(student)
        db.session.commit()

        logger.info(f"Mahasiswa baru ditambah ke kelas {class_id}: {student.student_id}")
        return jsonify({
            'message': 'Mahasiswa berhasil ditambahkan',
            'student': student.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error tambah mahasiswa: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/student/<int:student_id>/upload-photo', methods=['POST'])
@lecturer_required
def api_upload_student_photo(student_id):
    """API untuk upload foto mahasiswa dan register face"""
    from app.services.face_recognition_service import FaceRecognitionService

    student = Student.query.get_or_404(student_id)

    # Check ownership
    if student.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada foto'}), 400

    file = request.files['photo']

    try:
        # Read image
        image_data = file.read()

        # Extract face encoding
        encoding = FaceRecognitionService.encode_face(image_data)

        if encoding is None:
            return jsonify({'error': 'Tidak ada wajah terdeteksi di foto. Pastikan wajah jelas dan pencahayaan cukup'}), 400

        # Save face encoding
        student.set_face_encoding(encoding)

        # Save photo
        import os
        os.makedirs("uploads/student_photos", exist_ok=True)
        photo_path = f"uploads/student_photos/{student.student_id}_{student.id}.jpg"
        with open(photo_path, 'wb') as f:
            f.write(image_data)

        student.photo_path = photo_path
        student.registration_date = __import__('datetime').datetime.utcnow()

        db.session.commit()

        logger.info(f"Face terdaftar untuk mahasiswa: {student.student_id}")
        return jsonify({
            'message': 'Foto berhasil diupload dan face encoding selesai',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error upload foto: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/student/<int:student_id>', methods=['DELETE'])
@lecturer_required
def api_delete_student(student_id):
    """API untuk hapus mahasiswa"""
    student = Student.query.get_or_404(student_id)

    # Check ownership
    if student.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        db.session.delete(student)
        db.session.commit()

        logger.info(f"Mahasiswa dihapus: {student_id}")
        return jsonify({'message': 'Mahasiswa berhasil dihapus', 'success': True}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error hapus mahasiswa: {str(e)}")
        return jsonify({'error': str(e)}), 500
