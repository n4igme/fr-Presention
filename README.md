# 📸 Sistem Absensi Mahasiswa Berbasis Face Recognition

Sistem absensi real-time berbasis pengenalan wajah (Face Recognition) yang dirancang untuk mengotomatisasi pengambilan kehadiran mahasiswa di kelas secara cepat, akurat, dan efisien.

![Status](https://img.shields.io/badge/Status-Development-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## ✨ Fitur Utama

- 🔐 **Sistem Login Dosen**: Autentikasi aman dengan password hashing
- 📚 **Manajemen Kelas**: Dosen dapat membuat dan mengelola kelas
- 👤 **Registrasi Wajah Mahasiswa**: Capture dan encode wajah mahasiswa via webcam
- 🎥 **Real-time Face Detection**: Deteksi dan pengenalan wajah real-time menggunakan face-api.js
- 📱 **Responsive Web Interface**: UI modern dengan Bootstrap 5
- 📊 **Laporan Kehadiran**: View dan download attendance reports dalam format CSV
- 🔄 **Hybrid Approach**: Client-side detection (face-api.js) + Server-side verification (Python)
- 🐳 **Docker Support**: Deployment mudah dengan Docker dan Docker Compose
- ✅ **Proses Absensi Manual**: Pendekatan sederhana untuk absensi manual yang lebih akurat

## 🛠️ Technology Stack

| Komponen | Teknologi |
|----------|-----------|
| **Backend** | Flask 2.3.3, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite (Development), PostgreSQL (Production) |
| **Face Recognition** | Python face_recognition, OpenCV |
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, face-api.js |
| **Webcam** | WebRTC (getUserMedia API) |
| **Deployment** | Docker, Docker Compose, Gunicorn |

## 📋 Requirements

### Local Development
- Python 3.8+
- pip (Python package manager)
- Webcam/kamera laptop
- Browser modern (Chrome, Firefox, Edge)

### Docker Deployment
- Docker 20.10+
- Docker Compose 1.29+

## 🚀 Quick Start

### Option 1: Local Development

#### 1. Clone Repository & Setup
```bash
# Clone repository
git clone <repository-url>
cd fr-Presention

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env sesuai kebutuhan Anda
# Set SECRET_KEY, DATABASE_URL, dll
```

#### 3. Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

#### 4. Run Development Server
```bash
python app.py
# or: flask run
# Server running at http://localhost:5000
```

### Option 2: Docker Deployment

```bash
# Build dan start services
docker-compose up --build

# Atau run in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

**Aplikasi akan tersedia di**: `http://localhost:8000`

## 🔑 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **PENTING**: Ubah password default setelah login pertama kali!

## 📖 Panduan Penggunaan

### 1️⃣ Login
- Buka http://localhost:5000 atau http://localhost:8000 (Docker)
- Masukkan username dan password

### 2️⃣ Buat Kelas
- Dari dashboard, klik "Tambah Kelas"
- Isi informasi kelas (nama, kode, tahun ajaran, semester)
- Klik "Simpan"

### 3️⃣ Tambah Mahasiswa
- Klik kelas → "Kelola Mahasiswa"
- Input data mahasiswa (NIM, nama, email)
- Klik "Tambah"

### 4️⃣ Registrasi Wajah Mahasiswa
- Di halaman kelas, klik tombol "Upload Foto" untuk setiap mahasiswa
- Upload foto atau capture via webcam
- Sistem akan extract face encoding dan menyimpannya
- Status akan berubah menjadi "Terdaftar"

### 5️⃣ Mulai Sesi Absensi
- Dari dashboard, pilih kelas dan klik "Mulai Absensi"
- Beri nama sesi (misal: "Pertemuan 1")
- Klik "Mulai Sesi Absensi"
- Sistem akan mengakses webcam laptop
- Mahasiswa memasuki frame kamera
- Wajah terdeteksi otomatis dan kehadiran tercatat

### 6️⃣ Akhiri Sesi & Download Laporan
- Klik "Akhiri Sesi Absensi" ketika selesai
- Klik "Download CSV" untuk export data kehadiran

## 📁 Struktur Proyek

```
fr-Presention/
├── app.py                              # Main Flask app entry
├── config.py                           # Configuration settings
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── Dockerfile                          # Docker image config
├── docker-compose.yml                  # Docker Compose config
├── ARCHITECTURE.md                     # Detailed architecture docs
├── README.md                           # This file
│
├── app/
│   ├── __init__.py                     # Flask app factory
│   ├── models/                         # Database models
│   │   ├── user.py                     # User/Dosen model
│   │   ├── student.py                  # Student model
│   │   ├── class_model.py              # Class model
│   │   ├── attendance_session.py       # Attendance session
│   │   └── attendance_record.py        # Attendance record
│   ├── routes/                         # API endpoints
│   │   ├── auth.py                     # Auth routes
│   │   ├── lecturer.py                 # Lecturer routes
│   │   ├── student.py                  # Student routes
│   │   ├── attendance.py               # Attendance routes
│   │   ├── face_api.py                 # Face detection API
│   │   └── report.py                   # Report routes
│   ├── services/                       # Business logic
│   │   ├── face_recognition_service.py # Face recognition logic
│   │   ├── attendance_service.py       # Attendance logic
│   │   └── report_service.py           # Report generation
│   ├── utils/                          # Utilities
│   └── templates/                      # HTML templates
│       ├── base.html                   # Base template
│       ├── auth/                       # Auth templates
│       └── lecturer/                   # Lecturer templates
│
├── static/                             # Static assets
│   ├── css/                            # Stylesheets
│   │   ├── style.css                   # Main styles
│   │   └── face_capture.css            # Face capture styles
│   └── js/                             # JavaScript
│       ├── utils.js                    # Utility functions
│       └── api_client.js               # API client
│
├── uploads/                            # Upload directories
│   ├── student_photos/                 # Original photos
│   └── face_encodings/                 # Face encodings (JSON)
│
└── logs/                               # Application logs
```

## 🚀 Panduan Penggunaan Proses Absensi Baru

### 1️⃣ Pendekatan Manual (Dianjurkan)
Sistem kini menyediakan pendekatan absensi yang lebih sederhana dan terstruktur:

1. **Login sebagai Dosen** di sistem
2. **Pilih kelas** dan klik "Mulai Sesi Absensi"
3. **Mahasiswa datang satu-persatu** ke depan kelas
4. **Tampilkan wajah** di depan webcam
5. **Klik "Ambil Wajah"** untuk verifikasi identitas
6. **Sistem akan mengenali wajah** dan menampilkan nama mahasiswa
7. **Klik "Konfirmasi Hadir"** untuk mencatat kehadiran
8. **Ulangi untuk mahasiswa berikutnya**

### 2️⃣ Fitur Pendekatan Manual
- **Verifikasi Visual**: Dosen dapat memverifikasi bahwa wajah yang terdeteksi benar-benar milik mahasiswa tersebut
- **Pengurangan Kesalahan**: Mengurangi kebingungan saat banyak wajah terdeteksi sekaligus
- **Kontrol Lebih Baik**: Dosen memiliki kontrol penuh atas proses absensi
- **Umpan Balik Langsung**: Status verifikasi ditampilkan dengan jelas (hijau untuk sukses, merah untuk error)

### 3️⃣ Endpoint Baru
Sistem kini memiliki dua endpoint untuk capture face:
- `/api/attendance/capture-single` - untuk verifikasi identitas tanpa langsung mencatat kehadiran
- `/api/attendance/record-attendance` - untuk mencatat kehadiran setelah konfirmasi manual
- `/api/attendance/capture` - endpoint lama (masih tersedia untuk kompatibilitas)

### 4️⃣ Keunggulan Pendekatan Baru
- **Lebih Akurat**: Pengurangan kesalahan identifikasi karena verifikasi manual
- **Lebih Transparan**: Proses terstruktur dan mudah dipahami
- **Lebih Mudah Diverifikasi**: Dosen dapat mengonfirmasi secara visual sebelum mencatat kehadiran
- **Kontrol Lebih Baik**: Dosen memiliki kendali penuh atas proses absensi

## 🔐 Keamanan & Privacy

### Data Protection
- ✅ Password di-hash dengan bcrypt (cost=12)
- ✅ Face encoding stored as JSON (bukan image)
- ✅ Original photos disimpan terpisah (encrypted optional)
- ✅ Session-based authentication

### Access Control
- ✅ Role-based access (lecturer, admin)
- ✅ Dosen hanya akses kelas mereka sendiri
- ✅ CSRF protection untuk forms

### Recommendations
- Ganti `SECRET_KEY` di .env sebelum production
- Gunakan HTTPS jika deploy di internet
- Backup database secara regular
- Monitor access logs

## 🐛 Troubleshooting

### Webcam tidak terdeteksi
```
✓ Check browser permission untuk camera access
✓ Chrome/Firefox/Edge settings → Camera permissions
✓ Ensure HTTPS jika di production (beberapa browser require)
✓ Restart browser dan refresh halaman
```

### Face tidak terdeteksi
```
✓ Pastikan pencahayaan ruangan cukup terang
✓ Face sejajar dengan camera (tidak miring)
✓ Jarak ideal 0.3-1 meter dari kamera
✓ Reduce capture interval jika perlu (settings di .env)
```

### Performance lambat
```
✓ Reduce frame resolution (FRAME_RESIZE_SCALE di .env)
✓ Increase capture interval (CAPTURE_INTERVAL_MS)
✓ Check sistem memory dan CPU usage
✓ Enable GPU acceleration jika punya NVIDIA GPU
```

### Database locked (development)
```
✓ Ensure hanya 1 Flask process running
✓ Kill existing Flask processes: lsof -ti :5000 | xargs kill
✓ Restart Flask development server
```

## 📊 Database Schema

Lihat `ARCHITECTURE.md` untuk detail lengkap database schema dan Entity Relationship Diagram.

### Tabel Utama
- `users` - Dosen dan admin
- `classes` - Kelas/mata kuliah
- `students` - Data mahasiswa + face encoding
- `attendance_sessions` - Sesi pengambilan absensi
- `attendance_records` - Record kehadiran per mahasiswa

## 🔧 API Endpoints

Lihat `ARCHITECTURE.md` untuk daftar lengkap API endpoints.

### Contoh:
```
POST   /api/auth/login
GET    /api/students
POST   /api/attendance/capture
GET    /api/report/session/{id}
```

## 📈 Next Features & Improvements

- [ ] Email notifications untuk attendance
- [ ] Mobile app untuk mahasiswa
- [ ] QR Code attendance (fallback)
- [ ] Integration dengan Siakad/academic system
- [ ] ML untuk detect proxy attendance
- [ ] Advanced analytics & visualizations
- [ ] Multi-language support (EN/ID)
- [ ] Dark mode theme
- [ ] Biometric analysis (age, emotion detection)

## 🤝 Contributing

Contributions welcome! Silakan fork repository dan buat pull request.

## 📄 License

Project ini menggunakan MIT License.

## 👨‍💻 Author & Support

Dibuat dengan ❤️ menggunakan Flask & Face Recognition

Untuk pertanyaan atau issue, silakan buat GitHub issue.

---

**Made with ❤️ for better attendance management**