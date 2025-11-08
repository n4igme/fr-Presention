import face_recognition
import numpy as np
import cv2
import io
from PIL import Image
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """Service untuk face recognition operations"""

    @staticmethod
    def encode_face(image_data):
        """
        Extract face encoding dari image data

        Args:
            image_data: bytes atau PIL Image atau file path

        Returns:
            numpy array (128-dimensional) atau None jika tidak ada wajah
        """
        try:
            # Load image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                image = image_data

            # Convert PIL to numpy array
            image_array = np.array(image)

            # Convert RGBA to RGB jika perlu
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)

            # Resize untuk performance (0.25x dari config)
            resize_scale = current_app.config.get('FRAME_RESIZE_SCALE', 0.25)
            if resize_scale != 1.0:
                height = int(image_array.shape[0] * resize_scale)
                width = int(image_array.shape[1] * resize_scale)
                small_image = cv2.resize(image_array, (width, height))
            else:
                small_image = image_array

            # Detect faces
            face_locations = face_recognition.face_locations(small_image)

            if not face_locations:
                logger.warning("Tidak ada wajah terdeteksi di image")
                return None

            # Extract encoding dari wajah pertama (terbesar)
            # Scale kembali ke size original
            if resize_scale != 1.0:
                scaled_locations = [
                    (int(top / resize_scale),
                     int(right / resize_scale),
                     int(bottom / resize_scale),
                     int(left / resize_scale))
                    for top, right, bottom, left in face_locations
                ]
            else:
                scaled_locations = face_locations

            face_encodings = face_recognition.face_encodings(
                image_array,
                scaled_locations,
                model='small'
            )

            if face_encodings:
                logger.info(f"✓ Berhasil extract {len(face_encodings)} face encoding(s)")
                return face_encodings[0]  # Return encoding pertama (terbesar)

            logger.warning("Tidak ada face encoding yang bisa dihasilkan")
            return None

        except Exception as e:
            logger.error(f"✗ Error saat encode_face: {str(e)}")
            return None

    @staticmethod
    def compare_faces(unknown_encoding, known_students):
        """
        Compare unknown face dengan list known students

        Args:
            unknown_encoding: 128-dim array dari webcam
            known_students: list of tuples (Student object, encoding_array)

        Returns:
            tuple: (matched_student, confidence_score) atau (None, 0.0)
        """
        if unknown_encoding is None or not known_students:
            return (None, 0.0)

        try:
            # Extract encodings dari students
            known_encodings = [encoding for _, encoding in known_students]
            known_students_list = [student for student, _ in known_students]

            # Compare
            tolerance = current_app.config.get('FACE_RECOGNITION_TOLERANCE', 0.6)
            distances = face_recognition.face_distance(known_encodings, unknown_encoding)

            # Find best match
            if len(distances) > 0:
                best_match_index = distances.argmin()
                confidence = 1 - distances[best_match_index]

                # Check if passes tolerance
                if distances[best_match_index] <= tolerance:
                    matched_student = known_students_list[best_match_index]
                    logger.info(f"✓ Face matched dengan {matched_student.name} (confidence: {confidence:.2f})")
                    return (matched_student, confidence)

            logger.warning(f"Tidak ada match atau confidence < threshold (min distance: {min(distances):.2f})")
            return (None, 0.0)

        except Exception as e:
            logger.error(f"✗ Error saat compare_faces: {str(e)}")
            return (None, 0.0)

    @staticmethod
    def detect_faces_in_frame(frame_data, resize_scale=None):
        """
        Detect faces dalam webcam frame (client-side helper)

        Args:
            frame_data: image data (bytes atau numpy array)
            resize_scale: scale untuk resize (dari config jika None)

        Returns:
            list of face_locations atau []
        """
        if resize_scale is None:
            resize_scale = current_app.config.get('FRAME_RESIZE_SCALE', 0.25)

        try:
            # Load image
            if isinstance(frame_data, bytes):
                image = Image.open(io.BytesIO(frame_data))
                image_array = np.array(image)
            else:
                image_array = frame_data

            # Ensure RGB
            if len(image_array.shape) == 3:
                if image_array.shape[2] == 4:  # RGBA
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
                elif image_array.shape[2] == 3:
                    # BGR ke RGB
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            # Resize untuk performance
            if resize_scale != 1.0:
                height = int(image_array.shape[0] * resize_scale)
                width = int(image_array.shape[1] * resize_scale)
                small_image = cv2.resize(image_array, (width, height))
            else:
                small_image = image_array

            # Detect faces
            face_locations = face_recognition.face_locations(small_image)

            # Scale back if resized
            if resize_scale != 1.0:
                face_locations = [
                    (int(top / resize_scale),
                     int(right / resize_scale),
                     int(bottom / resize_scale),
                     int(left / resize_scale))
                    for top, right, bottom, left in face_locations
                ]

            return face_locations

        except Exception as e:
            logger.error(f"✗ Error saat detect_faces_in_frame: {str(e)}")
            return []

    @staticmethod
    def get_face_encodings_from_frame(frame_data, face_locations=None, resize_scale=None):
        """
        Extract face encodings dari frame

        Args:
            frame_data: image data
            face_locations: list of face locations (akan di-detect jika None)
            resize_scale: scale factor

        Returns:
            list of 128-dim arrays
        """
        if resize_scale is None:
            resize_scale = current_app.config.get('FRAME_RESIZE_SCALE', 0.25)

        try:
            # Load image
            if isinstance(frame_data, bytes):
                image = Image.open(io.BytesIO(frame_data))
                image_array = np.array(image)
            else:
                image_array = frame_data

            # Ensure RGB
            if len(image_array.shape) == 3:
                if image_array.shape[2] == 4:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
                elif image_array.shape[2] == 3:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            # Resize
            if resize_scale != 1.0:
                height = int(image_array.shape[0] * resize_scale)
                width = int(image_array.shape[1] * resize_scale)
                small_image = cv2.resize(image_array, (width, height))
            else:
                small_image = image_array

            # Detect faces jika tidak provided
            if face_locations is None:
                face_locations = face_recognition.face_locations(small_image)
                # Scale back
                if resize_scale != 1.0:
                    face_locations = [
                        (int(top / resize_scale),
                         int(right / resize_scale),
                         int(bottom / resize_scale),
                         int(left / resize_scale))
                        for top, right, bottom, left in face_locations
                    ]

            # Extract encodings
            if face_locations:
                face_encodings = face_recognition.face_encodings(
                    image_array,
                    face_locations,
                    model='small'
                )
                return face_encodings

            return []

        except Exception as e:
            logger.error(f"✗ Error saat get_face_encodings_from_frame: {str(e)}")
            return []
