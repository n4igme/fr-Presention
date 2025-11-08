from app import db
from datetime import datetime


class AttendanceRecord(db.Model):
    """Attendance record model - mencatat kehadiran seorang mahasiswa"""
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)  # 0.0 - 1.0
    is_manual = db.Column(db.Boolean, default=False)  # True jika manual entry
    photo_evidence = db.Column(db.String(255))  # Path ke foto bukti
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('student_id', 'session_id', name='unique_attendance_per_session'),
    )

    def __repr__(self):
        return f'<AttendanceRecord {self.student_id} at {self.session_id}>'

    def to_dict(self, include_student=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'confidence_score': self.confidence_score,
            'is_manual': self.is_manual,
            'photo_evidence': self.photo_evidence,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

        if include_student:
            data['student'] = {
                'id': self.student.id,
                'student_id': self.student.student_id,
                'name': self.student.name,
                'email': self.student.email
            }

        return data
