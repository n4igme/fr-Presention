# Sistem Absensi Mahasiswa Berbasis Face Recognition

## Dokumentasi Lengkap Arsitektur Sistem

---

## 1. RINGKASAN PROYEK

Sistem absensi mahasiswa berbasis face recognition ini dirancang untuk otomatisasi pengambilan kehadiran di kelas melalui pengenalan wajah real-time. Sistem ini mengintegrasikan:
- **Frontend responsif** untuk dosen (dashboard + webcam capture)
- **Backend REST API** untuk manajemen data
- **Face Recognition** dengan hybrid approach (client + server)
- **Database terstruktur** untuk menyimpan data mahasiswa dan kehadiran

---

## 2. TECH STACK

### Backend
- **Framework**: Flask 2.3.3 (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Face Recognition**: Python `face_recognition` library
- **Image Processing**: OpenCV, Pillow
- **Security**: Flask-Login, Werkzeug, JWT untuk API auth

### Frontend
- **Framework**: HTML5, CSS3, Bootstrap 5.3
- **JavaScript**:
  - `face-api.js` untuk client-side face detection
  - `axios` untuk API calls
  - `chart.js` untuk visualisasi data
- **Webcam Access**: WebRTC (getUserMedia API)

### Deployment
- **Containerization**: Docker & Docker Compose
- **Server**: Gunicorn (production)

---

## 3. STRUKTUR PROYEK

```
fr-Presention/
│
├── app.py                              # Main Flask application
├── config.py                           # Configuration settings
├── requirements.txt                    # Python dependencies
├── setup.py                            # Setup script
│
├── app/
│   ├── __init__.py                     # Flask app factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                     # User/Dosen model
│   │   ├── student.py                  # Student model
│   │   ├── class_model.py              # Class model
│   │   ├── attendance_session.py       # Attendance session model
│   │   └── attendance_record.py        # Attendance record model
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                     # Authentication routes
│   │   ├── lecturer.py                 # Lecturer dashboard routes
│   │   ├── student.py                  # Student management routes
│   │   ├── attendance.py               # Attendance session routes
│   │   ├── face_api.py                 # Face recognition API routes
│   │   └── report.py                   # Reporting routes
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_recognition_service.py # Face recognition logic
│   │   ├── attendance_service.py       # Attendance logic
│   │   ├── report_service.py           # Report generation
│   │   └── email_service.py            # Email notifications
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py               # Custom decorators
│   │   ├── helpers.py                  # Helper functions
│   │   └── validators.py               # Data validators
│   │
│   └── templates/
│       ├── base.html                   # Base template
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── lecturer/
│       │   ├── dashboard.html
│       │   ├── class_list.html
│       │   ├── class_detail.html
│       │   ├── student_management.html
│       │   ├── attendance_session.html # Main face capture interface
│       │   ├── attendance_history.html
│       │   └── reports.html
│       └── student/
│           ├── registration.html
│           └── profile.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   └── face_capture.css
│   ├── js/
│   │   ├── face_api.min.js
│   │   ├── face_detection.js           # Client-side face detection
│   │   ├── attendance_capture.js       # Attendance capture logic
│   │   ├── api_client.js               # API client wrapper
│   │   └── utils.js
│   ├── images/
│   └── fonts/
│
├── uploads/
│   ├── student_photos/                 # Unencrypted original photos
│   └── face_encodings/                 # Stored face encodings (JSON)
│
├── tests/
│   ├── test_auth.py
│   ├── test_face_recognition.py
│   ├── test_attendance.py
│   └── test_reports.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md

```

---

## 4. DATABASE SCHEMA

### Tabel: `users`
```
id (PK)
username (UNIQUE)
email (UNIQUE, OPTIONAL)
password_hash
name
role ('lecturer' | 'admin')
created_at
updated_at
is_active
```

### Tabel: `classes`
```
id (PK)
name
code (UNIQUE)
description
lecturer_id (FK -> users)
academic_year
semester
created_at
updated_at
```

### Tabel: `students`
```
id (PK)
student_id (UNIQUE)
name
email
phone (OPTIONAL)
class_id (FK -> classes)
photo_path (path to uploaded image)
face_encoding_json (128-dim vector as JSON array)
face_encoding_hash (SHA-256 hash for quick comparison)
registration_date
is_active
created_at
updated_at
```

### Tabel: `attendance_sessions`
```
id (PK)
class_id (FK -> classes)
session_name (e.g., "Pertemuan 1", "Quiz")
start_time
end_time
is_active (boolean)
created_by (FK -> users)
created_at
updated_at
notes (OPTIONAL)
```

### Tabel: `attendance_records`
```
id (PK)
student_id (FK -> students)
session_id (FK -> attendance_sessions)
timestamp
confidence_score (0.0 - 1.0)
is_manual (boolean - for manual entry)
photo_evidence (OPTIONAL - path to proof image)
created_at
```

---

## 5. FLOW SISTEM

### 5.1 User Registration & Face Enrollment
```
1. Dosen login ke sistem
2. Dosen menambahkan mahasiswa baru (input: nama, NIM, email)
3. Sistem generate link/invite untuk mahasiswa
4. Mahasiswa akses halaman registrasi dengan token
5. Mahasiswa upload foto atau capture wajah via webcam
6. Sistem ekstrak face encoding (128 dimensions)
7. Menyimpan encoding di database + foto original
8. Mahasiswa mendapat konfirmasi registrasi sukses
```

### 5.2 Attendance Session
```
1. Dosen login ke dashboard
2. Dosen klik "Mulai Sesi Absensi" di class tertentu
3. Sistem buat record attendance_session (is_active=true)
4. Halaman attendance capture terbuka dengan webcam
5. Browser capture frame setiap 500ms (configurable)
6. Client-side: Deteksi wajah menggunakan face-api.js
7. Client send captured face encoding ke server
8. Server: Lakukan face matching dengan encoding mahasiswa terdaftar
9. Server: Jika match (confidence > threshold), catat di attendance_records
10. Client display hasil real-time (mahasiswa terdeteksi, timestamp)
11. Dosen klik "Selesai Sesi" untuk menutup session
12. Sistem compile laporan absensi untuk pertemuan itu
```

### 5.3 Report & Export
```
1. Dosen ke halaman "Riwayat Kehadiran"
2. Pilih kelas dan pertemuan
3. Lihat daftar mahasiswa + status kehadiran (Hadir/Tidak Hadir)
4. Klik "Download CSV" atau "Download Excel"
5. File diunduh dengan format: NIM | Nama | Kehadiran | Waktu Datang | Confidence
```

---

## 6. API ENDPOINTS

### Authentication
```
POST   /api/auth/login          - Dosen login
POST   /api/auth/logout         - Logout
POST   /api/auth/refresh        - Refresh token
GET    /api/auth/me             - Current user info
```

### Student Management
```
GET    /api/students            - List semua mahasiswa (per dosen)
POST   /api/students            - Tambah mahasiswa baru
GET    /api/students/<id>       - Detail mahasiswa
PUT    /api/students/<id>       - Update data mahasiswa
DELETE /api/students/<id>       - Hapus mahasiswa
POST   /api/students/<id>/photo - Upload/update foto mahasiswa
GET    /api/students/<id>/register-token - Generate registration link
```

### Class Management
```
GET    /api/classes             - List kelas (untuk dosen logged-in)
POST   /api/classes             - Buat kelas baru
GET    /api/classes/<id>        - Detail kelas
PUT    /api/classes/<id>        - Update kelas
DELETE /api/classes/<id>        - Hapus kelas
GET    /api/classes/<id>/students - List mahasiswa di kelas
```

### Attendance Session
```
POST   /api/attendance/sessions/start      - Start sesi absensi
POST   /api/attendance/sessions/<id>/end   - End sesi absensi
GET    /api/attendance/sessions/<id>      - Detail sesi (status, mahasiswa terdeteksi)
GET    /api/attendance/sessions            - List sesi (per class)
```

### Face Recognition & Capture
```
POST   /api/attendance/capture             - Process frame + detect face
POST   /api/attendance/manual/<student_id> - Manual entry (fallback)
GET    /api/attendance/session/<id>/status - Real-time status sesi
```

### Reporting
```
GET    /api/attendance/reports/<class_id>       - List semua pertemuan
GET    /api/attendance/reports/<session_id>     - Detail attendance 1 sesi
GET    /api/attendance/reports/<session_id>/csv - Download CSV
GET    /api/attendance/reports/<session_id>/excel - Download Excel
```

---

## 7. KEAMANAN & PRIVACY

### Data Protection
- **Password**: Hash dengan bcrypt (cost=12)
- **Face Encoding**: Stored as JSON (128 float values) - bukan image
- **Original Photos**: Stored separately, encrypted at rest (optional: AES-256)
- **Database**: SQLite untuk dev, PostgreSQL untuk production

### Authentication
- **Dosen**: Username + password (session-based atau JWT)
- **API**: Bearer token (JWT) untuk mobile apps
- **CSRF Protection**: Flask-WTF for forms

### Access Control
- Dosen hanya bisa akses data kelas yang dia ajar
- Student hanya bisa edit profile mereka sendiri
- Admin only endpoints untuk user management

### Audit & Logging
- Log setiap face detection attempt
- Log manual attendance entry dengan user yang input
- Timestamp untuk semua activity

---

## 8. FACE RECOGNITION STRATEGY

### Hybrid Approach (Recommended)

#### Client-Side (Browser)
- Use `face-api.js` untuk:
  - Real-time face detection di webcam
  - Extract face descriptor (128-dimensional)
  - Show visual feedback (bounding box)
  - Reduce server load
- Benefit: Low latency, better UX

#### Server-Side (Python)
- Use `face_recognition` library untuk:
  - Face matching dengan confidence scoring
  - Final verification sebelum record attendance
  - Backup jika client-side gagal
- Benefit: More robust, access to GPU, dapat fine-tune threshold

### Face Comparison Logic
```python
def compare_faces(unknown_encoding, known_encodings, tolerance=0.6):
    """
    unknown_encoding: 128-dim array dari webcam
    known_encodings: list of 128-dim arrays dari database
    tolerance: threshold (0.6 default, lower = stricter matching)

    Returns:
        (matched_student_id, confidence_score) or (None, 0.0)
    """
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    matches = distances <= tolerance

    if matches.any():
        best_match_index = distances.argmin()
        confidence = 1 - distances[best_match_index]
        return (student_ids[best_match_index], confidence)

    return (None, 0.0)
```

### Configuration
- **Face Detection Model**: dlib (default di face_recognition)
- **Encoding Model**: ResNet-based (pre-trained)
- **Tolerance**: 0.6 (dapat di-tune per institusi)
- **Capture Interval**: 500ms (every 0.5 second)
- **Min Confidence**: 0.4 (untuk recording)

---

## 9. CARA MENJALANKAN SISTEM

### Local Development

#### Prerequisites
```bash
- Python 3.8+
- Node.js 14+ (optional, hanya jika custom webpack)
- SQLite3
```

#### Setup
```bash
# 1. Clone repository
git clone https://github.com/yourrepo/attendance-system.git
cd attendance-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env dan set SECRET_KEY, DATABASE_URL, dll

# 5. Initialize database
python
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     # Insert default admin user
>>> exit()

# 6. Download face_recognition models
python -c "import face_recognition; print('Models downloaded')"

# 7. Run development server
python app.py
# or: flask run
# Server berjalan di http://localhost:5000
```

### Docker Deployment

```bash
# Build dan run dengan Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f web

# Access aplikasi di http://localhost:8000
```

---

## 10. DEFAULT CREDENTIALS (Development Only)

```
Username: admin
Password: admin123
```

⚠️ **CHANGE IMMEDIATELY IN PRODUCTION!**

---

## 11. TROUBLESHOOTING

### Webcam tidak terdeteksi
- Check browser permissions (chrome://settings/content/camera)
- Ensure HTTPS jika deployed (some browsers require HTTPS for getUserMedia)

### Face tidak terdeteksi
- Pastikan pencahayaan cukup
- Face harus sejajar dengan camera (tidak miring)
- Update face_recognition library: `pip install --upgrade face_recognition`

### Slow performance
- Reduce capture interval dari 500ms ke 1000ms
- Resize frame sebelum processing (dari 1920x1080 ke 640x480)
- Enable GPU acceleration (CUDA untuk NVIDIA)

### Database locked
- Pastikan hanya 1 Flask process yang running
- Jika development: `export FLASK_ENV=development`

---

## 12. NEXT STEPS & IMPROVEMENTS

- [ ] Email notifications untuk attendance
- [ ] Mobile app untuk mahasiswa melihat riwayat kehadiran
- [ ] QR Code attendance (fallback)
- [ ] Integration dengan Siakad/Academic System
- [ ] Machine Learning untuk detect proxy attendance
- [ ] Advanced analytics & visualization
- [ ] Multi-language support (EN/ID)
- [ ] Dark mode

---

**Dibuat oleh**: AI Assistant
**Versi**: 1.0
**Last Updated**: 2025-11-08
