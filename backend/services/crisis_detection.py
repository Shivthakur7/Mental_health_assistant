"""
Crisis Detection System for Mental Health Assistant
Detects crisis-level emotions and provides appropriate responses.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrisisDetector:
    def __init__(self):
        # Crisis keywords - comprehensive list
        self.crisis_keywords = [
            # Suicide-related
            "suicide", "kill myself", "end it all", "end my life", "take my life",
            "don't want to live", "better off dead", "want to die", "kill me",
            "suicide plan", "suicidal", "end it", "no point living",
            
            # Self-harm related
            "hurt myself", "cut myself", "harm myself", "self harm", "self-harm",
            "cutting", "burning myself", "punish myself",
            
            # Hopelessness indicators
            "hopeless", "no hope", "nothing matters", "pointless", "worthless",
            "useless", "failure", "can't go on", "give up", "no way out",
            "trapped", "stuck forever", "never get better",
            
            # Despair and isolation
            "nobody cares", "alone forever", "no one understands", "abandoned",
            "empty inside", "numb", "can't feel anything", "dead inside",
            
            # Crisis escalation phrases
            "can't take it anymore", "at my limit", "breaking point", "lost everything",
            "nothing left", "final straw", "had enough", "over it"
        ]
        
        # Severity levels for different keywords
        self.high_severity_keywords = [
            "suicide", "kill myself", "end my life", "want to die", "better off dead",
            "suicide plan", "take my life", "end it all"
        ]
        
        self.medium_severity_keywords = [
            "hurt myself", "cut myself", "self harm", "hopeless", "worthless",
            "can't go on", "give up", "no way out"
        ]
        
        # Helpline resources
        self.helplines = {
            "international": {
                "name": "Find A Helpline",
                "url": "https://findahelpline.com",
                "description": "International crisis helpline directory"
            },
            "us": {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "url": "https://988lifeline.org",
                "description": "24/7 crisis support in the United States"
            },
            "uk": {
                "name": "Samaritans",
                "phone": "116 123",
                "url": "https://www.samaritans.org",
                "description": "24/7 crisis support in the United Kingdom"
            },
            "india": {
                "name": "AASRA",
                "phone": "91-22-27546669",
                "url": "http://www.aasra.info",
                "description": "24/7 crisis support in India"
            }
        }

    def analyze_crisis_level(self, text: str, mood_score: float) -> Dict:
        """
        Analyze text and mood score for crisis indicators.
        
        Args:
            text: User input text
            mood_score: Sentiment analysis score (-1 to 1)
            
        Returns:
            Dictionary with crisis analysis results
        """
        text_lower = text.lower()
        
        # Check for crisis keywords
        found_keywords = []
        severity_level = "none"
        
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
                
                if keyword in self.high_severity_keywords:
                    severity_level = "high"
                elif keyword in self.medium_severity_keywords and severity_level != "high":
                    severity_level = "medium"
                elif severity_level == "none":
                    severity_level = "low"
        
        # Sentiment-based crisis detection
        sentiment_crisis = mood_score < -0.8
        
        # Combined crisis assessment
        is_crisis = (
            sentiment_crisis or 
            len(found_keywords) > 0 or
            severity_level in ["high", "medium"]
        )
        
        # Determine crisis level
        if severity_level == "high" or (sentiment_crisis and len(found_keywords) > 0):
            crisis_level = "critical"
        elif severity_level == "medium" or sentiment_crisis or len(found_keywords) >= 2:
            crisis_level = "high"
        elif len(found_keywords) > 0 or mood_score < -0.6:
            crisis_level = "moderate"
        else:
            crisis_level = "none"
        
        return {
            "is_crisis": is_crisis,
            "crisis_level": crisis_level,
            "found_keywords": found_keywords,
            "sentiment_crisis": sentiment_crisis,
            "mood_score": mood_score,
            "severity_assessment": severity_level,
            "timestamp": datetime.now().isoformat()
        }

    def get_crisis_response(self, crisis_analysis: Dict, user_location: str = "international") -> Dict:
        """
        Generate appropriate crisis response based on analysis.
        
        Args:
            crisis_analysis: Result from analyze_crisis_level
            user_location: User's location for localized helplines
            
        Returns:
            Crisis response with messages and resources
        """
        crisis_level = crisis_analysis["crisis_level"]
        
        if crisis_level == "critical":
            return {
                "status": "CRITICAL_CRISIS",
                "priority": "immediate",
                "message": "🚨 I'm very concerned about you. You're not alone, and your life has value. Please reach out for immediate help.",
                "action_required": "immediate_intervention",
                "helplines": self._get_helplines(user_location),
                "immediate_steps": [
                    "Call emergency services (911, 999, 112) if in immediate danger",
                    "Contact a crisis helpline immediately",
                    "Reach out to a trusted friend, family member, or mental health professional",
                    "Go to your nearest emergency room if you feel unsafe"
                ],
                "follow_up_required": True
            }
        
        elif crisis_level == "high":
            return {
                "status": "HIGH_CRISIS",
                "priority": "urgent",
                "message": "I'm concerned about how you're feeling. Please know that you're not alone and help is available.",
                "action_required": "professional_support",
                "helplines": self._get_helplines(user_location),
                "immediate_steps": [
                    "Consider calling a crisis helpline to talk to someone",
                    "Reach out to a trusted person in your life",
                    "Contact your mental health provider if you have one",
                    "Consider visiting a mental health professional"
                ],
                "follow_up_required": True
            }
        
        elif crisis_level == "moderate":
            return {
                "status": "MODERATE_CONCERN",
                "priority": "elevated",
                "message": "I notice you might be going through a difficult time. It's important to take care of yourself.",
                "action_required": "self_care_and_support",
                "helplines": self._get_helplines(user_location),
                "immediate_steps": [
                    "Consider talking to someone you trust",
                    "Practice self-care activities",
                    "If feelings persist, consider professional support",
                    "Remember that difficult feelings are temporary"
                ],
                "follow_up_required": False
            }
        
        else:
            return {
                "status": "NO_CRISIS",
                "priority": "normal",
                "message": None,
                "action_required": "none",
                "helplines": None,
                "immediate_steps": None,
                "follow_up_required": False
            }

    def _get_helplines(self, location: str = "international") -> Dict:
        """Get relevant helplines based on user location."""
        location_lower = location.lower()
        
        # Return location-specific helplines if available
        if location_lower in self.helplines:
            primary_helpline = self.helplines[location_lower]
        else:
            primary_helpline = self.helplines["international"]
        
        return {
            "primary": primary_helpline,
            "international": self.helplines["international"],
            "additional": [
                self.helplines["us"],
                self.helplines["uk"],
                self.helplines["india"]
            ]
        }

    def log_crisis_event(self, crisis_analysis: Dict, user_id: Optional[str] = None):
        """Log crisis events for monitoring and follow-up."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id or "anonymous",
            "crisis_level": crisis_analysis["crisis_level"],
            "is_crisis": crisis_analysis["is_crisis"],
            "found_keywords": crisis_analysis["found_keywords"],
            "mood_score": crisis_analysis["mood_score"]
        }
        
        if crisis_analysis["is_crisis"]:
            logger.warning(f"CRISIS DETECTED: {log_data}")
        else:
            logger.info(f"Crisis check completed: {log_data}")
        
        return log_data

# Global crisis detector instance
crisis_detector = CrisisDetector()

def check_crisis(text: str, mood_score: float, user_location: str = "international", user_id: Optional[str] = None) -> Dict:
    """
    Convenience function to perform complete crisis check.
    
    Args:
        text: User input text
        mood_score: Sentiment analysis score
        user_location: User's location for localized resources
        user_id: Optional user identifier for logging
        
    Returns:
        Complete crisis analysis and response
    """
    # Analyze crisis level
    crisis_analysis = crisis_detector.analyze_crisis_level(text, mood_score)
    
    # Get appropriate response
    crisis_response = crisis_detector.get_crisis_response(crisis_analysis, user_location)
    
    # Log the event
    crisis_detector.log_crisis_event(crisis_analysis, user_id)
    
    # Combine analysis and response
    return {
        "analysis": crisis_analysis,
        "response": crisis_response
    }

if __name__ == "__main__":
    # Test the crisis detection system
    test_cases = [
        ("I want to kill myself", -0.9),
        ("I feel hopeless and worthless", -0.7),
        ("I'm having a bad day", -0.3),
        ("I'm feeling great today!", 0.8),
        ("I can't take it anymore, I want to end it all", -0.95)
    ]
    
    print("Testing Crisis Detection System:")
    print("=" * 50)
    
    for text, score in test_cases:
        result = check_crisis(text, score)
        print(f"\nText: '{text}'")
        print(f"Mood Score: {score}")
        print(f"Crisis Level: {result['analysis']['crisis_level']}")
        print(f"Status: {result['response']['status']}")
        if result['response']['message']:
            print(f"Message: {result['response']['message']}")
        print("-" * 30)
