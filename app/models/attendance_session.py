from app import db
from datetime import datetime


class AttendanceSession(db.Model):
    """Attendance session model - represents satu kali sesi pengambilan absensi"""
    __tablename__ = 'attendance_sessions'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    session_name = db.Column(db.String(120), nullable=False)  # e.g., "Pertemuan 1", "Quiz"
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def end_session(self):
        """End attendance session"""
        self.end_time = datetime.utcnow()
        self.is_active = False

    @property
    def summary(self):
        """Get attendance summary as property"""
        total_records = self.attendance_records.count()
        unique_students = len(set(
            record.student_id for record in self.attendance_records.all()
        ))
        return {
            'total_records': total_records,
            'unique_students': unique_students
        }

    def get_summary(self):
        """Get attendance summary (deprecated, use summary property)"""
        return self.summary

    def __repr__(self):
        return f'<AttendanceSession {self.id}: {self.session_name}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'session_name': self.session_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'notes': self.notes,
            'summary': self.get_summary(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
