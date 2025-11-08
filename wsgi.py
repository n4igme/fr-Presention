"""
Sistem Absensi Mahasiswa Berbasis Face Recognition
Main Application Entry Point
"""

import os
import sys

# Configure OpenCV to avoid GPU/display issues
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_VIDEOIO_LOG_LEVEL'] = 'OFF'

from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

# Create app
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Add models to shell context"""
    from app.models.user import User
    from app.models.student import Student
    from app.models.class_model import Class
    from app.models.attendance_session import AttendanceSession
    from app.models.attendance_record import AttendanceRecord

    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Class': Class,
        'AttendanceSession': AttendanceSession,
        'AttendanceRecord': AttendanceRecord
    }


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return {
        'error': 'Not Found',
        'message': 'Halaman atau resource tidak ditemukan'
    }, 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    app.logger.error(f'Server error: {str(error)}')
    return {
        'error': 'Server Error',
        'message': 'Terjadi kesalahan pada server'
    }, 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return {
        'error': 'Forbidden',
        'message': 'Anda tidak memiliki akses ke resource ini'
    }, 403


if __name__ == '__main__':
    # Development server
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=debug_mode
    )
