from app import db
from datetime import datetime


class Class(db.Model):
    """Class model untuk menyimpan data kelas/mata kuliah"""
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2024/2025"
    semester = db.Column(db.Integer, nullable=False)  # 1 or 2
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    students = db.relationship('Student', backref='class_record', lazy='dynamic', cascade='all, delete-orphan')
    attendance_sessions = db.relationship('AttendanceSession', backref='class_record', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Class {self.code}: {self.name}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'lecturer_id': self.lecturer_id,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'student_count': self.students.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
