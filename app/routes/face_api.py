from flask import Blueprint, request, jsonify, current_app
import base64
import io
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('face_api', __name__, url_prefix='/api/face')


@bp.route('/detect', methods=['POST'])
def detect_faces():
    """
    Detect faces dalam image (client-side support)
    Expects: {'image_data': base64 encoded image}

    Returns: {
        'detected': bool,
        'face_count': int,
        'faces': [{'top': int, 'right': int, 'bottom': int, 'left': int}]
    }
    """
    try:
        from app.services.face_recognition_service import FaceRecognitionService

        data = request.get_json()
        image_data = data.get('image_data')

        if not image_data:
            return jsonify({'error': 'Missing image_data'}), 400

        # Decode base64
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Error decode image: {str(e)}")
            return jsonify({'error': 'Invalid image format'}), 400

        # Detect faces
        face_locations = FaceRecognitionService.detect_faces_in_frame(image)

        return jsonify({
            'detected': len(face_locations) > 0,
            'face_count': len(face_locations),
            'faces': [
                {'top': top, 'right': right, 'bottom': bottom, 'left': left}
                for top, right, bottom, left in face_locations
            ]
        }), 200

    except Exception as e:
        logger.error(f"Error detect faces: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/encode', methods=['POST'])
def encode_face():
    """
    Extract face encoding dari image

    Returns: {
        'encoded': bool,
        'encoding': [128 float values] jika berhasil
    }
    """
    try:
        from app.services.face_recognition_service import FaceRecognitionService

        data = request.get_json()
        image_data = data.get('image_data')

        if not image_data:
            return jsonify({'error': 'Missing image_data'}), 400

        # Decode base64
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Error decode image: {str(e)}")
            return jsonify({'error': 'Invalid image format'}), 400

        # Encode face
        encoding = FaceRecognitionService.encode_face(image)

        if encoding is None:
            return jsonify({
                'encoded': False,
                'message': 'Tidak ada wajah terdeteksi'
            }), 200

        return jsonify({
            'encoded': True,
            'encoding': encoding.tolist()
        }), 200

    except Exception as e:
        logger.error(f"Error encode face: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/compare', methods=['POST'])
def compare_faces():
    """
    Compare dua face encodings

    Expects: {
        'encoding1': [128 values],
        'encoding2': [128 values],
        'tolerance': float (optional)
    }

    Returns: {
        'distance': float,
        'match': bool,
        'confidence': float
    }
    """
    try:
        import face_recognition

        data = request.get_json()
        enc1 = data.get('encoding1')
        enc2 = data.get('encoding2')
        tolerance = data.get('tolerance', current_app.config.get('FACE_RECOGNITION_TOLERANCE', 0.6))

        if not enc1 or not enc2:
            return jsonify({'error': 'Missing encodings'}), 400

        # Convert to numpy arrays
        enc1 = np.array(enc1)
        enc2 = np.array(enc2)

        # Compare
        distance = face_recognition.face_distance([enc2], enc1)[0]
        confidence = 1 - distance

        return jsonify({
            'distance': float(distance),
            'confidence': float(confidence),
            'match': bool(distance <= tolerance)
        }), 200

    except Exception as e:
        logger.error(f"Error compare faces: {str(e)}")
        return jsonify({'error': str(e)}), 500
