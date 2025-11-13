# 📸 Face Recognition Attendance System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)](https://github.com/your-repo/fr-presention)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A modern, real-time attendance system that leverages face recognition technology to automate and streamline the process of tracking student attendance in a classroom environment. Built with Flask and a powerful hybrid face detection model, this project aims to provide an accurate, efficient, and user-friendly solution for educators.

---

## 🌟 Key Features

This system is packed with features designed to make attendance management seamless:

-   🔐 **Secure Authentication**: Role-based access control for lecturers and administrators with secure password hashing.
-   📚 **Class and Student Management**: Easily create classes, enroll students, and manage their information.
-   👤 **Effortless Face Registration**: A simple one-time process for students to register their face using a webcam or by uploading a photo.
-   🎥 **Real-time Attendance Capture**: Utilizes a hybrid approach for fast and accurate face detection.
    -   **Client-Side Detection**: `face-api.js` runs in the browser for instant face detection without server lag.
    -   **Server-Side Verification**: Python's `face_recognition` library provides robust verification and matching against the database.
-   📊 **Comprehensive Reporting**: View detailed attendance records for each session and export them to CSV format for easy record-keeping.
-   🕹️ **Manual Override**: Lecturers can manually mark attendance, providing a fallback for any situation.
-   🐳 **Dockerized Deployment**: Comes with `Dockerfile` and `docker-compose.yml` for quick and consistent deployment.
-   📱 **Responsive UI**: A clean and modern web interface built with Bootstrap 5 that works on any device.

---

## ⚙️ How It Works

The system uses a sophisticated yet straightforward workflow for taking attendance.

1.  **Setup**: The lecturer creates a class and enrolls students.
2.  **Face Enrollment**: Each student provides a photo of their face, which the system converts into a unique mathematical representation (a "face encoding"). This encoding is stored securely, not the photo itself.
3.  **Start Session**: The lecturer starts an attendance session from their dashboard. This activates the webcam interface.
4.  **Recognition**:
    -   As students appear before the camera, the browser's JavaScript (`face-api.js`) detects faces in real-time.
    -   A snapshot of the detected face is sent to the Flask backend.
    -   The backend compares the captured face encoding with the stored encodings of enrolled students.
5.  **Record Keeping**: If a match is found with high confidence, the student is marked as "Present," and a record is created with a timestamp.
6.  **Reporting**: The lecturer can end the session at any time and immediately view or download the attendance report.

---

## 🛠️ Technology Stack

The project is built with a combination of modern and reliable technologies:

| Category      | Technology                                                              |
| :------------ | :---------------------------------------------------------------------- |
| **Backend**   | Python, Flask, Flask-SQLAlchemy, Flask-Login                            |
| **Database**  | SQLite (for development), PostgreSQL (recommended for production)       |
| **Face Reco** | `face-recognition` (dlib), OpenCV, Pillow                               |
| **Frontend**  | HTML5, CSS3, JavaScript, Bootstrap 5, `face-api.js`                     |
| **Webcam**    | WebRTC (via `getUserMedia` API)                                         |
| **Deployment**| Gunicorn, Docker, Docker Compose                                        |

---

## 🚀 Getting Started

You can get the system up and running in minutes using either Docker (recommended) or a traditional local setup.

### Prerequisites

-   Git
-   Python 3.8+ and `pip`
-   A modern web browser (e.g., Chrome, Firefox)
-   Docker and Docker Compose (for containerized deployment)

### Option 1: Docker Deployment (Recommended)

This is the easiest and fastest way to get started.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/fr-presention.git
    cd fr-presention
    ```

2.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```

3.  **Access the application:**
    Open your browser and navigate to `http://localhost:8000`.

4.  **To stop the application:**
    ```bash
    docker-compose down
    ```

### Option 2: Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/fr-presention.git
    cd fr-presention
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment:**
    Copy the example environment file and edit it if needed. The default settings are suitable for local development.
    ```bash
    cp .env.example .env
    ```

5.  **Initialize the database:**
    Run the following commands to create the database schema.
    ```bash
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

6.  **Run the application:**
    ```bash
    flask run
    ```

7.  **Access the application:**
    Open your browser and navigate to `http://localhost:5000`.

---

## 📖 Usage Guide

### 1. Login
-   Use the default credentials to log in for the first time.
-   **Username**: `admin`
-   **Password**: `admin123`
-   **Important**: Change the default password after your first login for security.

### 2. Create a Class
-   From the lecturer dashboard, click on "Tambah Kelas".
-   Fill in the class details, such as name, code, and academic year.

### 3. Enroll Students
-   Navigate to the class details page.
-   Add students by providing their Student ID (NIM) and name.

### 4. Register Student Faces
-   For each student, click "Upload Foto".
-   The student can either upload a clear portrait photo or use the webcam to capture their face.
-   The system will process the image and store the face encoding. The status will change to "Terdaftar".

### 5. Take Attendance
-   From the dashboard, select a class and click "Mulai Absensi".
-   Give the session a name (e.g., "Week 1 Lecture") and start the session.
-   The webcam will activate. Students simply need to look at the camera.
-   Their attendance will be recorded automatically in real-time.

### 6. View and Export Reports
-   After the class, click "Akhiri Sesi".
-   You can then view the attendance list for that session or download it as a CSV file.

---

## 📂 Project Structure

The project follows a standard Flask application structure, keeping code organized and modular.

```
/fr-presention
├── app/
│   ├── __init__.py             # Application factory
│   ├── models/                 # SQLAlchemy database models
│   ├── routes/                 # Application routes and views
│   ├── services/               # Business logic (face recognition, etc.)
│   ├── static/                 # CSS, JS, and image assets
│   └── templates/              # Jinja2 HTML templates
├── .env.example                # Environment variable template
├── config.py                   # Configuration loading
├── wsgi.py                       # WSGI entry point for Gunicorn
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Instructions to build the Docker image
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

---

## ⚙️ Configuration

The application is configured via environment variables. Create a `.env` file in the project root (you can copy `.env.example`) to customize these settings:

-   `FLASK_ENV`: Set to `development` or `production`.
-   `SECRET_KEY`: A strong, unique secret key for session security.
-   `DATABASE_URL`: The connection string for your database (defaults to SQLite).
-   `FACE_RECOGNITION_TOLERANCE`: The strictness of the face matching. Lower is stricter. `0.6` is a good starting point.
-   `UPLOAD_FOLDER`: The directory where student photos are stored.

---

## 🔐 Security & Privacy

-   **Passwords**: All user passwords are securely hashed using `bcrypt`.
-   **Face Data**: The system **does not** store photos of faces directly for comparison. Instead, it stores a mathematical `face encoding` (a vector of 128 numbers). This encoding cannot be reverse-engineered back into a photo, ensuring student privacy.
-   **Access Control**: The application uses role-based access to ensure lecturers can only manage their own classes.
-   **CSRF Protection**: Forms are protected against Cross-Site Request Forgery attacks.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please feel free to:
1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
