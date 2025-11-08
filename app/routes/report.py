from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from app.models.attendance_session import AttendanceSession
from app.models.class_model import Class
from app.models.student import Student
from app.services.attendance_service import AttendanceService
import csv
import io
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('report', __name__, url_prefix='/api/report')


@bp.route('/class/<int:class_id>/sessions', methods=['GET'])
@login_required
def get_class_sessions(class_id):
    """Get all attendance sessions untuk satu kelas"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify ownership
    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        sessions = AttendanceSession.query.filter_by(class_id=class_id).order_by(
            AttendanceSession.start_time.desc()
        ).all()

        return jsonify({
            'class': class_obj.to_dict(),
            'sessions': [session.to_dict() for session in sessions]
        }), 200

    except Exception as e:
        logger.error(f"Error get sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/session/<int:session_id>', methods=['GET'])
@login_required
def get_session_report(session_id):
    """Get detailed attendance report untuk satu sesi"""
    session = AttendanceSession.query.get_or_404(session_id)

    # Verify ownership
    if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        report = AttendanceService.get_session_attendance(session_id)
        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Error get session report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/session/<int:session_id>/csv', methods=['GET'])
@login_required
def download_session_csv(session_id):
    """Download attendance report sebagai CSV"""
    session = AttendanceSession.query.get_or_404(session_id)

    # Verify ownership
    if session.class_record.lecturer_id != current_user.id and not current_user.is_admin():
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
        response_data = output.getvalue().encode('utf-8-sig')

        return send_file(
            io.BytesIO(response_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"attendance_{session.id}_{session.session_name}.csv"
        )

    except Exception as e:
        logger.error(f"Error download CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/student/<int:student_id>/class/<int:class_id>', methods=['GET'])
@login_required
def get_student_attendance(student_id, class_id):
    """Get attendance summary untuk satu mahasiswa di kelas"""
    student = Student.query.get_or_404(student_id)
    class_obj = Class.query.get_or_404(class_id)

    # Verify ownership
    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    # Verify student is in class
    if student.class_id != class_id:
        return jsonify({'error': 'Mahasiswa bukan dari kelas ini'}), 400

    try:
        summary = AttendanceService.get_student_attendance_summary(student_id, class_id)
        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"Error get student attendance: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/class/<int:class_id>/export', methods=['GET'])
@login_required
def export_class_attendance(class_id):
    """Export semua attendance untuk satu kelas sebagai CSV"""
    class_obj = Class.query.get_or_404(class_id)

    # Verify ownership
    if class_obj.lecturer_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Akses ditolak'}), 403

    try:
        # Get all sessions
        sessions = AttendanceSession.query.filter_by(class_id=class_id).order_by(
            AttendanceSession.start_time.asc()
        ).all()

        # Get all students
        students = Student.query.filter_by(class_id=class_id, is_active=True).all()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        header = ['NIM', 'Nama', 'Email']
        header.extend([session.session_name for session in sessions])
        writer.writerow(header)

        # Data
        for student in students:
            row = [student.student_id, student.name, student.email or '']

            for session in sessions:
                from app.models.attendance_record import AttendanceRecord
                record = AttendanceRecord.query.filter_by(
                    student_id=student.id,
                    session_id=session.id
                ).first()

                if record:
                    row.append('✓')
                else:
                    row.append('✗')

            writer.writerow(row)

        # Create response
        output.seek(0)
        response_data = output.getvalue().encode('utf-8-sig')

        return send_file(
            io.BytesIO(response_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"attendance_{class_obj.code}_summary.csv"
        )

    except Exception as e:
        logger.error(f"Error export class attendance: {str(e)}")
        return jsonify({'error': str(e)}), 500
