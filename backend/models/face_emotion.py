"""
Facial Emotion Detection using OpenCV and TensorFlow
Analyzes facial expressions to detect emotional states.
"""

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Tuple, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceEmotionAnalyzer:
    def __init__(self):
        self.emotion_model = None
        self.face_cascade = None
        self.emotion_labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        self._load_models()
    
    def _load_models(self):
        """Load face detection and emotion classification models."""
        try:
            # Load face detection cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Try to load a pre-trained emotion model or create a simple one
            self._load_or_create_emotion_model()
            
            logger.info("Face emotion analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize face emotion analyzer: {e}")
    
    def _load_or_create_emotion_model(self):
        """Load existing emotion model or create a simple one for demonstration."""
        model_path = "emotion_model.h5"
        
        if os.path.exists(model_path):
            try:
                self.emotion_model = keras.models.load_model(model_path)
                logger.info("Loaded existing emotion model")
                return
            except Exception as e:
                logger.warning(f"Failed to load existing model: {e}")
        
        # Create a simple CNN model for emotion detection
        logger.info("Creating simple emotion detection model")
        self.emotion_model = self._create_simple_model()
    
    def _create_simple_model(self):
        """Create a simple CNN model for emotion detection (for demonstration)."""
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(7, activation='softmax')  # 7 emotions
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Initialize with random weights (in a real scenario, you'd train this)
        model.build(input_shape=(None, 48, 48, 1))
        
        return model
    
    def detect_faces(self, image):
        """Detect faces in the image."""
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def analyze_face_emotion(self, image_path: str) -> Tuple[str, float]:
        """
        Analyze facial emotion from image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return "neutral", 0.3
            
            # Detect faces
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                logger.warning("No faces detected in image")
                return "neutral", 0.4
            
            # Use the largest face
            face = max(faces, key=lambda x: x[2] * x[3])  # largest by area
            x, y, w, h = face
            
            # Extract face region
            face_roi = image[y:y+h, x:x+w]
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Preprocess for emotion model
            face_resized = cv2.resize(gray_face, (48, 48))
            face_normalized = face_resized.astype('float32') / 255.0
            face_input = np.expand_dims(face_normalized, axis=[0, -1])  # (1, 48, 48, 1)
            
            # Predict emotion
            if self.emotion_model is not None:
                predictions = self.emotion_model.predict(face_input, verbose=0)
                emotion_idx = np.argmax(predictions[0])
                confidence = predictions[0][emotion_idx]
                emotion_label = self.emotion_labels[emotion_idx]
            else:
                # Fallback analysis
                return self._fallback_face_analysis(gray_face)
            
            logger.info(f"Face emotion detected: {emotion_label} (confidence: {confidence:.2f})")
            return emotion_label, float(confidence)
            
        except Exception as e:
            logger.error(f"Error analyzing face emotion: {e}")
            return self._fallback_face_analysis(None)
    
    def _fallback_face_analysis(self, face_image) -> Tuple[str, float]:
        """
        Fallback analysis using basic image features when the main model fails.
        """
        try:
            if face_image is not None:
                # Simple heuristic based on image brightness and contrast
                mean_brightness = np.mean(face_image)
                std_contrast = np.std(face_image)
                
                # Basic emotion classification based on image characteristics
                if mean_brightness > 120 and std_contrast > 40:
                    return "happy", 0.6
                elif mean_brightness < 80:
                    return "sad", 0.6
                elif std_contrast > 60:
                    return "surprise", 0.6
                else:
                    return "neutral", 0.5
            else:
                return "neutral", 0.3
                
        except Exception as e:
            logger.error(f"Fallback face analysis failed: {e}")
            return "neutral", 0.3

# Global instance
face_analyzer = FaceEmotionAnalyzer()

def analyze_face_emotion(image_path: str) -> Tuple[str, float]:
    """
    Convenience function to analyze facial emotion.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (emotion_label, confidence_score)
    """
    return face_analyzer.analyze_face_emotion(image_path)

if __name__ == "__main__":
    # Test the face emotion analyzer
    print("Face Emotion Analyzer initialized")
    print("Available emotions:", face_analyzer.emotion_labels)
