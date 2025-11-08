# Routes package
from . import auth as auth_bp_module
from . import lecturer as lecturer_bp_module
from . import student as student_bp_module
from . import attendance as attendance_bp_module
from . import face_api as face_api_bp_module
from . import report as report_bp_module

# Export blueprints
auth_bp = auth_bp_module.bp
lecturer_bp = lecturer_bp_module.bp
student_bp = student_bp_module.bp
attendance_bp = attendance_bp_module.bp
face_api_bp = face_api_bp_module.bp
report_bp = report_bp_module.bp

__all__ = ['auth_bp', 'lecturer_bp', 'student_bp', 'attendance_bp', 'face_api_bp', 'report_bp']
