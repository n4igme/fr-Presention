import face_recognition
import cv2
import numpy as np
import sqlite3


class FaceRecognition:
    def __init__(self, db_path='attendance_system.db'):
        self.db_path = db_path
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        self.load_known_faces()

    def load_known_faces(self):
        """Load all known face encodings from the database"""
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.name, s.student_id, s.face_encoding 
            FROM students s 
            WHERE s.face_encoding IS NOT NULL
        ''')
        
        for row in cursor.fetchall():
            student_id, name, student_id_db, encoding_blob = row
            if encoding_blob:
                encoding = np.frombuffer(encoding_blob, dtype=np.float64)
                if encoding.size == 128:  # face_recognition encodings are 128-dim
                    self.known_encodings.append(encoding)
                    self.known_names.append(name)
                    self.known_ids.append(student_id)
        
        conn.close()

    def encode_face_from_image(self, image):
        """Encode a face from an image file"""
        # Convert image to RGB (face_recognition uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) != 1:
            return None, f"Found {len(face_locations)} faces in image, need exactly 1"
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return None, "Could not extract face encoding"
        
        return face_encodings[0], None

    def recognize_face(self, image, tolerance=0.6):
        """Recognize a face in an image and return the student information"""
        if len(self.known_encodings) == 0:
            return None, "No known faces loaded"
        
        # Convert image to RGB (face_recognition uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and encodings in the image
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return None, "No faces found in image"
        
        # Compare with known encodings
        recognized_faces = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=tolerance)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    recognized_faces.append({
                        'id': self.known_ids[best_match_index],
                        'name': self.known_names[best_match_index],
                        'distance': float(face_distances[best_match_index])
                    })
        
        return recognized_faces, None

    def add_known_face(self, image, student_name, student_id):
        """Add a new face to the known faces"""
        encoding, error = self.encode_face_from_image(image)
        if error:
            return False, error
        
        # Add to DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encoding_bytes = encoding.tobytes()
        cursor.execute(
            'UPDATE students SET face_encoding = ? WHERE student_id = ?',
            (encoding_bytes, student_id)
        )
        conn.commit()
        
        # Update internal lists
        self.load_known_faces()  # Reload to include new face
        
        conn.close()
        return True, "Face added successfully"