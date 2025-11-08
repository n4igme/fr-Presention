from app import db
from app.models.attendance_record import AttendanceRecord
from app.models.attendance_session import AttendanceSession
from app.models.student import Student
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service untuk attendance operations"""

    @staticmethod
    def start_session(class_id, session_name, created_by_id, notes=None):
        """
        Mulai sesi absensi baru

        Args:
            class_id: ID kelas
            session_name: Nama sesi (e.g., "Pertemuan 1")
            created_by_id: User ID yang membuat sesi
            notes: Optional notes

        Returns:
            AttendanceSession object
        """
        # Jika ada session aktif, close terlebih dahulu
        active_session = AttendanceSession.query.filter_by(
            class_id=class_id,
            is_active=True
        ).first()

        if active_session:
            logger.warning(f"Ada session aktif, tutup terlebih dahulu: {active_session.id}")
            active_session.end_session()

        # Create new session
        session = AttendanceSession(
            class_id=class_id,
            session_name=session_name,
            created_by=created_by_id,
            notes=notes,
            is_active=True
        )

        db.session.add(session)
        db.session.commit()

        logger.info(f"✓ Sesi absensi dimulai: {session.id}")
        return session

    @staticmethod
    def end_session(session_id):
        """
        Akhiri sesi absensi

        Args:
            session_id: ID sesi

        Returns:
            AttendanceSession object atau None
        """
        session = AttendanceSession.query.get(session_id)
        if not session:
            logger.error(f"✗ Session tidak ditemukan: {session_id}")
            return None

        session.end_session()
        db.session.commit()

        logger.info(f"✓ Sesi absensi ditutup: {session_id}")
        return session

    @staticmethod
    def record_attendance(student_id, session_id, confidence_score, is_manual=False, notes=None):
        """
        Catat kehadiran mahasiswa

        Args:
            student_id: ID mahasiswa
            session_id: ID sesi
            confidence_score: Confidence score (0.0-1.0)
            is_manual: Apakah manual entry
            notes: Optional notes

        Returns:
            AttendanceRecord object atau None
        """
        # Check duplikat attendance dalam sesi yang sama
        existing = AttendanceRecord.query.filter_by(
            student_id=student_id,
            session_id=session_id
        ).first()

        if existing:
            logger.warning(f"Mahasiswa {student_id} sudah tercatat di sesi {session_id}")
            return existing

        # Create attendance record
        record = AttendanceRecord(
            student_id=student_id,
            session_id=session_id,
            confidence_score=confidence_score,
            is_manual=is_manual,
            notes=notes
        )

        db.session.add(record)
        db.session.commit()

        logger.info(f"✓ Kehadiran tercatat: Student {student_id} at Session {session_id}")
        return record

    @staticmethod
    def get_session_attendance(session_id):
        """
        Ambil data kehadiran untuk satu sesi

        Args:
            session_id: ID sesi

        Returns:
            dict dengan attendance summary dan records
        """
        session = AttendanceSession.query.get(session_id)
        if not session:
            return None

        # Get semua student di kelas
        class_students = Student.query.filter_by(
            class_id=session.class_id,
            is_active=True
        ).all()

        # Get attendance records untuk sesi ini
        attendance_records = AttendanceRecord.query.filter_by(
            session_id=session_id
        ).all()

        attended_students = {record.student_id for record in attendance_records}

        # Compile report
        report = {
            'session': session.to_dict(),
            'total_students': len(class_students),
            'present_count': len(attended_students),
            'absent_count': len(class_students) - len(attended_students),
            'attendance_details': []
        }

        for student in class_students:
            if student.id in attended_students:
                record = next(r for r in attendance_records if r.student_id == student.id)
                status = 'Hadir'
                time_in = record.timestamp.strftime('%H:%M:%S')
                confidence = f"{record.confidence_score:.2f}" if record.confidence_score else '-'
            else:
                status = 'Tidak Hadir'
                time_in = '-'
                confidence = '-'

            report['attendance_details'].append({
                'student_id': student.student_id,
                'name': student.name,
                'email': student.email,
                'status': status,
                'time_in': time_in,
                'confidence': confidence
            })

        return report

    @staticmethod
    def get_class_attendance_history(class_id, limit=10):
        """
        Ambil history sesi absensi untuk satu kelas

        Args:
            class_id: ID kelas
            limit: Jumlah record yang diambil

        Returns:
            list of sessions
        """
        sessions = AttendanceSession.query.filter_by(
            class_id=class_id
        ).order_by(AttendanceSession.start_time.desc()).limit(limit).all()

        return [session.to_dict() for session in sessions]

    @staticmethod
    def get_student_attendance_summary(student_id, class_id, period_days=30):
        """
        Ambil summary kehadiran mahasiswa dalam periode tertentu

        Args:
            student_id: ID mahasiswa
            class_id: ID kelas
            period_days: Jumlah hari ke belakang

        Returns:
            dict dengan attendance summary
        """
        # Get sessions dalam periode
        start_date = datetime.utcnow() - timedelta(days=period_days)
        sessions = AttendanceSession.query.filter(
            AttendanceSession.class_id == class_id,
            AttendanceSession.start_time >= start_date
        ).all()

        # Get attendance records
        attended_sessions = set()
        total_confidence = 0
        count = 0

        for session in sessions:
            record = AttendanceRecord.query.filter_by(
                student_id=student_id,
                session_id=session.id
            ).first()

            if record:
                attended_sessions.add(session.id)
                if record.confidence_score:
                    total_confidence += record.confidence_score
                    count += 1

        avg_confidence = (total_confidence / count) if count > 0 else 0

        return {
            'student_id': student_id,
            'class_id': class_id,
            'period_days': period_days,
            'total_sessions': len(sessions),
            'present_count': len(attended_sessions),
            'absent_count': len(sessions) - len(attended_sessions),
            'attendance_rate': (len(attended_sessions) / len(sessions) * 100) if sessions else 0,
            'avg_confidence': f"{avg_confidence:.2f}"
        }

    @staticmethod
    def manual_entry(student_id, session_id, notes=None):
        """
        Manual attendance entry (fallback)

        Args:
            student_id: ID mahasiswa
            session_id: ID sesi
            notes: Alasan manual entry

        Returns:
            AttendanceRecord object
        """
        return AttendanceService.record_attendance(
            student_id=student_id,
            session_id=session_id,
            confidence_score=0.0,  # No confidence score untuk manual
            is_manual=True,
            notes=notes or "Manual entry"
        )
