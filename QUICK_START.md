# 🚀 Quick Start Guide - Sistem Absensi Face Recognition

## ⚡ Setup Tercepat (5 Menit)

### Local Development

```bash
# 1. Clone & navigate
cd fr-Presention

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run application
python app.py

# Buka: http://localhost:5000
# Login: admin / admin123
```

### Docker (Recommended)

```bash
# 1. Build & run
docker-compose up --build

# Buka: http://localhost:8000
# Login: admin / admin123

# 2. Stop
docker-compose down
```

---

## 📋 Checklist Pertama Kali

### Step 1: Login
- [ ] Open http://localhost:5000
- [ ] Enter: admin / admin123

### Step 2: Buat Kelas
- [ ] Klik "Tambah Kelas" di dashboard
- [ ] Isi: Nama, Kode, Tahun Ajaran
- [ ] Klik Simpan

### Step 3: Tambah Mahasiswa
- [ ] Klik kelas → "Kelola Mahasiswa"
- [ ] Input: NIM, Nama, Email (optional)
- [ ] Klik Tambah

### Step 4: Register Wajah Mahasiswa
- [ ] Klik "Upload Foto" untuk setiap mahasiswa
- [ ] Upload foto atau capture via webcam
- [ ] Tunggu face encoding berhasil

### Step 5: Ambil Absensi
- [ ] Dari dashboard, klik "Mulai Absensi"
- [ ] Beri nama sesi (misal: "Pertemuan 1")
- [ ] Klik "Mulai Sesi Absensi"
- [ ] Mahasiswa ke depan kamera
- [ ] Kehadiran tercatat otomatis

### Step 6: Download Laporan
- [ ] Klik "Akhiri Sesi" ketika selesai
- [ ] Klik "Download CSV" untuk export data

---

## 🔑 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Ubah password setelah login!**

---

## 🛠️ Troubleshooting Cepat

| Problem | Solution |
|---------|----------|
| Webcam tidak bekerja | Chrome → Settings → Camera permissions → Enable |
| Face tidak terdeteksi | Pastikan pencahayaan bagus, face sejajar |
| Port sudah dipakai | Change PORT in .env atau kill existing process |
| DB error | Delete `attendance_system.db` dan restart |

---

## 📁 File Penting

- `app.py` - Main entry point
- `app/__init__.py` - Flask factory
- `config.py` - Configuration
- `.env` - Environment variables
- `requirements.txt` - Dependencies
- `ARCHITECTURE.md` - Detailed docs

---

## 🌐 URL Penting

- **Local Dev**: http://localhost:5000
- **Docker**: http://localhost:8000
- **API Docs**: Lihat ARCHITECTURE.md

---

## 📚 Dokumentasi Lengkap

- `README.md` - Overview & features
- `ARCHITECTURE.md` - Technical details
- `SCHEMA.md` - Database schema

---

## ✅ Next Steps

1. Ubah password admin
2. Buat 2-3 kelas test
3. Register 5-10 mahasiswa
4. Test face recognition
5. Download CSV report

---

**Selamat! Sistem siap digunakan. Untuk help lebih lanjut, buka ARCHITECTURE.md**
