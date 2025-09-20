"""
Voice Emotion Analysis using Wav2Vec2
Analyzes audio files to detect emotional states from speech patterns.
"""

import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceEmotionAnalyzer:
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "superb/wav2vec2-base-superb-er"
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained Wav2Vec2 model for speech emotion recognition."""
        try:
            logger.info(f"Loading voice emotion model: {self.model_name}")
            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()  # Set to evaluation mode
            logger.info("Voice emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load voice emotion model: {e}")
            # Fallback to a simpler approach if the model fails to load
            self.model = None
            self.processor = None
    
    def analyze_voice(self, audio_path: str) -> Tuple[str, float]:
        """
        Analyze voice emotion from audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        if self.model is None or self.processor is None:
            logger.warning("Voice emotion model not available, using fallback")
            return self._fallback_analysis(audio_path)
        
        try:
            # Load and preprocess audio
            speech, sr = librosa.load(audio_path, sr=16000)
            
            # Handle empty or very short audio
            if len(speech) < 1600:  # Less than 0.1 seconds at 16kHz
                logger.warning("Audio too short for analysis")
                return "neutral", 0.5
            
            # Process input
            inputs = self.processor(
                speech, 
                sampling_rate=sr, 
                return_tensors="pt", 
                padding=True,
                truncation=True,
                max_length=16000 * 10  # Max 10 seconds
            )
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get prediction
            predicted_id = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][predicted_id].item()
            
            # Map to emotion label
            if hasattr(self.model.config, 'id2label'):
                label = self.model.config.id2label[predicted_id]
            else:
                # Fallback emotion mapping
                emotion_map = {0: "neutral", 1: "happy", 2: "sad", 3: "angry", 4: "fear"}
                label = emotion_map.get(predicted_id, "neutral")
            
            logger.info(f"Voice emotion detected: {label} (confidence: {confidence:.2f})")
            return label, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing voice emotion: {e}")
            return self._fallback_analysis(audio_path)
    
    def _fallback_analysis(self, audio_path: str) -> Tuple[str, float]:
        """
        Fallback analysis using basic audio features when the main model fails.
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Extract basic features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Simple heuristic based on audio characteristics
            mean_mfcc = np.mean(mfccs)
            mean_spectral = np.mean(spectral_centroids)
            mean_zcr = np.mean(zero_crossing_rate)
            
            # Basic emotion classification based on audio features
            if mean_spectral > 2000 and mean_zcr > 0.1:
                return "happy", 0.6
            elif mean_spectral < 1000 and mean_mfcc < -20:
                return "sad", 0.6
            elif mean_zcr > 0.15:
                return "angry", 0.6
            else:
                return "neutral", 0.5
                
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return "neutral", 0.3

# Global instance
voice_analyzer = VoiceEmotionAnalyzer()

def analyze_voice_emotion(audio_path: str) -> Tuple[str, float]:
    """
    Convenience function to analyze voice emotion.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Tuple of (emotion_label, confidence_score)
    """
    return voice_analyzer.analyze_voice(audio_path)

if __name__ == "__main__":
    # Test the voice emotion analyzer
    print("Voice Emotion Analyzer initialized")
    print("Available emotions: happy, sad, angry, fear, neutral")
