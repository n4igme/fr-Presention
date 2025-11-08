from app import db
from datetime import datetime
import json


class Student(db.Model):
    """Student model untuk menyimpan data mahasiswa dan face encoding"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    photo_path = db.Column(db.String(255))  # Path ke foto original
    face_encoding_json = db.Column(db.Text)  # JSON string of 128-dimensional vector
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def get_face_encoding(self):
        """Get face encoding as numpy array"""
        if not self.face_encoding_json:
            return None
        import numpy as np
        try:
            encoding_list = json.loads(self.face_encoding_json)
            return np.array(encoding_list, dtype=np.float64)
        except (json.JSONDecodeError, TypeError):
            return None

    def set_face_encoding(self, encoding):
        """Set face encoding from numpy array"""
        import numpy as np
        if isinstance(encoding, np.ndarray):
            self.face_encoding_json = json.dumps(encoding.tolist())
        else:
            self.face_encoding_json = json.dumps(encoding)

    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'

    def to_dict(self, include_encoding=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'class_id': self.class_id,
            'photo_path': self.photo_path,
            'is_active': self.is_active,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_encoding and self.face_encoding_json:
            data['has_face_encoding'] = True
        else:
            data['has_face_encoding'] = bool(self.face_encoding_json)

        return data
