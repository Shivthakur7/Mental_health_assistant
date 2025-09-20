"""
Multi-modal Emotion Fusion
Combines text, voice, and facial emotion analysis into a unified mood score.
"""

import logging
from typing import Dict, Optional, Tuple, Any
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiModalFusion:
    def __init__(self):
        # Weights for different modalities (can be adjusted based on reliability)
        self.weights = {
            "text": 0.5,    # Text analysis is usually most reliable
            "voice": 0.3,   # Voice carries emotional information
            "face": 0.2     # Facial expressions can be misleading in photos
        }
        
        # Mapping categorical emotions to numerical mood values
        self.emotion_to_score = {
            # Positive emotions
            "happy": 1.0,
            "joy": 1.0,
            "surprise": 0.8,
            "excitement": 0.9,
            
            # Neutral emotions
            "neutral": 0.0,
            "calm": 0.1,
            
            # Negative emotions
            "sad": -0.7,
            "sadness": -0.7,
            "fear": -0.8,
            "angry": -0.9,
            "anger": -0.9,
            "disgust": -1.0,
            "anxiety": -0.6,
            "stress": -0.5,
            "depression": -0.8,
            
            # Fallback
            "unknown": 0.0
        }
        
        # Confidence thresholds for reliability assessment
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def normalize_emotion_label(self, label: str) -> str:
        """Normalize emotion labels to standard format."""
        if not label:
            return "neutral"
        
        label = label.lower().strip()
        
        # Handle common variations
        label_mapping = {
            "happiness": "happy",
            "sadness": "sad",
            "anger": "angry",
            "fearful": "fear",
            "surprised": "surprise",
            "disgusted": "disgust",
            "joyful": "happy",
            "excited": "excitement",
            "anxious": "anxiety",
            "stressed": "stress",
            "depressed": "depression"
        }
        
        return label_mapping.get(label, label)
    
    def get_emotion_score(self, emotion_label: str, confidence: float = 1.0) -> float:
        """Convert emotion label to numerical score, weighted by confidence."""
        normalized_label = self.normalize_emotion_label(emotion_label)
        base_score = self.emotion_to_score.get(normalized_label, 0.0)
        
        # Weight the score by confidence
        weighted_score = base_score * confidence
        
        return weighted_score
    
    def assess_reliability(self, confidence: float) -> str:
        """Assess the reliability of a prediction based on confidence."""
        if confidence >= self.confidence_thresholds["high"]:
            return "high"
        elif confidence >= self.confidence_thresholds["medium"]:
            return "medium"
        elif confidence >= self.confidence_thresholds["low"]:
            return "low"
        else:
            return "very_low"
    
    def adjust_weights_by_reliability(self, modality_data: Dict[str, Dict]) -> Dict[str, float]:
        """Dynamically adjust weights based on prediction reliability."""
        adjusted_weights = self.weights.copy()
        
        # Calculate total reliability
        total_reliability = 0
        reliability_scores = {}
        
        for modality, data in modality_data.items():
            if data and 'confidence' in data:
                confidence = data['confidence']
                reliability = confidence  # Simple reliability metric
                reliability_scores[modality] = reliability
                total_reliability += reliability
        
        # Adjust weights based on reliability
        if total_reliability > 0:
            for modality in adjusted_weights:
                if modality in reliability_scores:
                    # Increase weight for more reliable predictions
                    reliability_factor = reliability_scores[modality] / (total_reliability / len(reliability_scores))
                    adjusted_weights[modality] *= reliability_factor
        
        # Normalize weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for modality in adjusted_weights:
                adjusted_weights[modality] /= total_weight
        
        return adjusted_weights
    
    def fuse_emotions(
        self,
        text_score: Optional[float] = None,
        text_confidence: float = 1.0,
        voice_label: Optional[str] = None,
        voice_confidence: float = 1.0,
        face_label: Optional[str] = None,
        face_confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Fuse multi-modal emotion data into a unified mood assessment.
        
        Args:
            text_score: Numerical sentiment score from text analysis
            text_confidence: Confidence in text analysis
            voice_label: Emotion label from voice analysis
            voice_confidence: Confidence in voice analysis
            face_label: Emotion label from face analysis
            face_confidence: Confidence in face analysis
            
        Returns:
            Dictionary containing fused results and analysis details
        """
        
        # Prepare modality data
        modality_data = {}
        
        if text_score is not None:
            modality_data['text'] = {
                'score': text_score,
                'confidence': text_confidence,
                'reliability': self.assess_reliability(text_confidence)
            }
        
        if voice_label is not None:
            voice_score = self.get_emotion_score(voice_label, voice_confidence)
            modality_data['voice'] = {
                'label': voice_label,
                'score': voice_score,
                'confidence': voice_confidence,
                'reliability': self.assess_reliability(voice_confidence)
            }
        
        if face_label is not None:
            face_score = self.get_emotion_score(face_label, face_confidence)
            modality_data['face'] = {
                'label': face_label,
                'score': face_score,
                'confidence': face_confidence,
                'reliability': self.assess_reliability(face_confidence)
            }
        
        # Adjust weights based on reliability
        adjusted_weights = self.adjust_weights_by_reliability(modality_data)
        
        # Calculate weighted fusion
        final_score = 0.0
        total_weight = 0.0
        
        for modality, weight in adjusted_weights.items():
            if modality in modality_data:
                score = modality_data[modality]['score']
                final_score += score * weight
                total_weight += weight
        
        # Normalize if we have any data
        if total_weight > 0:
            final_score = final_score  # Already weighted
        
        # Clamp final score to [-1, 1] range
        final_score = max(-1.0, min(1.0, final_score))
        
        # Determine overall mood label
        mood_label = self._score_to_mood_label(final_score)
        
        # Calculate overall confidence
        overall_confidence = np.mean([
            data['confidence'] for data in modality_data.values()
        ]) if modality_data else 0.0
        
        # Prepare detailed results
        result = {
            "final_mood_score": round(final_score, 3),
            "mood_label": mood_label,
            "overall_confidence": round(overall_confidence, 3),
            "modalities_used": list(modality_data.keys()),
            "weights_used": {k: round(v, 3) for k, v in adjusted_weights.items() if k in modality_data},
            "detailed_analysis": modality_data
        }
        
        logger.info(f"Multi-modal fusion result: {mood_label} ({final_score:.3f})")
        
        return result
    
    def _score_to_mood_label(self, score: float) -> str:
        """Convert numerical mood score to descriptive label."""
        if score >= 0.7:
            return "Very Positive"
        elif score >= 0.3:
            return "Positive"
        elif score >= 0.1:
            return "Slightly Positive"
        elif score >= -0.1:
            return "Neutral"
        elif score >= -0.3:
            return "Slightly Negative"
        elif score >= -0.7:
            return "Negative"
        else:
            return "Very Negative"

# Global instance
fusion_engine = MultiModalFusion()

def fuse_multimodal_emotions(
    text_score: Optional[float] = None,
    text_confidence: float = 1.0,
    voice_label: Optional[str] = None,
    voice_confidence: float = 1.0,
    face_label: Optional[str] = None,
    face_confidence: float = 1.0
) -> Dict[str, Any]:
    """
    Convenience function for multi-modal emotion fusion.
    """
    return fusion_engine.fuse_emotions(
        text_score=text_score,
        text_confidence=text_confidence,
        voice_label=voice_label,
        voice_confidence=voice_confidence,
        face_label=face_label,
        face_confidence=face_confidence
    )

if __name__ == "__main__":
    # Test the fusion engine
    print("Multi-modal Fusion Engine initialized")
    
    # Example fusion
    result = fuse_multimodal_emotions(
        text_score=-0.5,
        text_confidence=0.8,
        voice_label="sad",
        voice_confidence=0.7,
        face_label="neutral",
        face_confidence=0.6
    )
    
    print("Example fusion result:", result)
