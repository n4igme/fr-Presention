from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__)

    # Load configuration
    from config import config
    app.config.from_object(config.get(config_name, 'default'))

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu'

    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'student_photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'face_encodings'), exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Configure logging
    setup_logging(app)

    # Register blueprints
    from app.routes import auth_bp, lecturer_bp, student_bp, attendance_bp, face_api_bp, report_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(lecturer_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(face_api_bp)
    app.register_blueprint(report_bp)

    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
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

    # Create tables
    with app.app_context():
        db.create_all()

        # Create default admin user jika belum ada
        from app.models.user import User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@attendance.local',
                name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created (admin/admin123)")

    return app


def setup_logging(app):
    """Setup application logging"""
    log_file = app.config.get('LOG_FILE', 'logs/app.log')
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(log_level)
