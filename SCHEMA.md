# Database Schema

## Tables

### users
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `username`: TEXT UNIQUE NOT NULL
- `password_hash`: TEXT NOT NULL
- `name`: TEXT NOT NULL

### classes
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `code`: TEXT UNIQUE NOT NULL
- `lecturer_id`: INTEGER (foreign key to users.id)

### students
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `student_id`: TEXT UNIQUE NOT NULL
- `class_id`: INTEGER (foreign key to classes.id)
- `face_encoding`: BLOB

### attendance_sessions
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `class_id`: INTEGER (foreign key to classes.id)
- `start_time`: TEXT NOT NULL
- `end_time`: TEXT
- `is_active`: BOOLEAN DEFAULT 1

### attendance_records
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `student_id`: INTEGER (foreign key to students.id)
- `session_id`: INTEGER (foreign key to attendance_sessions.id)
- `timestamp`: TEXT NOT NULL