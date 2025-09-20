"""
Activity Recommendations for Mental Health Support
Provides personalized activities based on mood and crisis level to help users feel better.
"""

import random
from typing import List, Dict, Any
from datetime import datetime

class ActivityRecommendationEngine:
    def __init__(self):
        self.activities = {
            # For Crisis Situations (Immediate Grounding)
            "crisis": {
                "grounding": [
                    {
                        "title": "5-4-3-2-1 Grounding Technique",
                        "description": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste",
                        "duration": "2-3 minutes",
                        "type": "grounding",
                        "icon": "🧘"
                    },
                    {
                        "title": "Deep Breathing Exercise",
                        "description": "Breathe in for 4 counts, hold for 4, breathe out for 6. Repeat 5 times",
                        "duration": "3-5 minutes",
                        "type": "breathing",
                        "icon": "🫁"
                    },
                    {
                        "title": "Cold Water on Wrists",
                        "description": "Run cold water over your wrists or splash on your face to activate your nervous system",
                        "duration": "1-2 minutes",
                        "type": "physical",
                        "icon": "💧"
                    },
                    {
                        "title": "Call Someone You Trust",
                        "description": "Reach out to a friend, family member, or counselor. You don't have to face this alone",
                        "duration": "10-30 minutes",
                        "type": "social",
                        "icon": "📞"
                    }
                ],
                "immediate_comfort": [
                    {
                        "title": "Wrap Yourself in a Blanket",
                        "description": "Find a soft blanket or comfort item. Physical comfort can help emotional comfort",
                        "duration": "As long as needed",
                        "type": "comfort",
                        "icon": "🛋️"
                    },
                    {
                        "title": "Listen to Calming Music",
                        "description": "Put on gentle, soothing music or nature sounds to help regulate your emotions",
                        "duration": "10-20 minutes",
                        "type": "audio",
                        "icon": "🎵"
                    }
                ]
            },
            
            # For Moderate Negative Moods (Mood Lifting)
            "moderate_negative": {
                "physical": [
                    {
                        "title": "Take a 10-Minute Walk",
                        "description": "Step outside or walk around your home. Movement releases endorphins naturally",
                        "duration": "10-15 minutes",
                        "type": "exercise",
                        "icon": "🚶"
                    },
                    {
                        "title": "Gentle Stretching",
                        "description": "Do simple stretches - neck rolls, shoulder shrugs, touch your toes",
                        "duration": "5-10 minutes",
                        "type": "exercise",
                        "icon": "🤸"
                    },
                    {
                        "title": "Dance to Your Favorite Song",
                        "description": "Put on an upbeat song and move your body however feels good",
                        "duration": "3-5 minutes",
                        "type": "exercise",
                        "icon": "💃"
                    }
                ],
                "creative": [
                    {
                        "title": "Draw or Doodle",
                        "description": "Grab paper and draw anything - patterns, faces, or whatever comes to mind",
                        "duration": "10-20 minutes",
                        "type": "art",
                        "icon": "🎨"
                    },
                    {
                        "title": "Write in a Journal",
                        "description": "Write about your feelings, or write a story, poem, or letter to yourself",
                        "duration": "10-15 minutes",
                        "type": "writing",
                        "icon": "📝"
                    },
                    {
                        "title": "Take Photos of Beautiful Things",
                        "description": "Use your phone to capture something beautiful around you - flowers, clouds, pets",
                        "duration": "5-15 minutes",
                        "type": "photography",
                        "icon": "📸"
                    }
                ],
                "mindful": [
                    {
                        "title": "Mindful Tea/Coffee Break",
                        "description": "Make a warm drink and focus on the smell, warmth, and taste mindfully",
                        "duration": "10-15 minutes",
                        "type": "mindfulness",
                        "icon": "☕"
                    },
                    {
                        "title": "Gratitude List",
                        "description": "Write down 3 things you're grateful for today, no matter how small",
                        "duration": "5-10 minutes",
                        "type": "gratitude",
                        "icon": "🙏"
                    }
                ],
                "social": [
                    {
                        "title": "Text a Friend Something Positive",
                        "description": "Send a compliment, funny meme, or just say hi to someone you care about",
                        "duration": "2-5 minutes",
                        "type": "social",
                        "icon": "💬"
                    },
                    {
                        "title": "Watch Funny Videos",
                        "description": "Look up comedy clips, cute animals, or funny TikToks to get some laughs",
                        "duration": "10-15 minutes",
                        "type": "entertainment",
                        "icon": "😂"
                    }
                ]
            },
            
            # For Neutral/Slightly Negative Moods (Mood Enhancement)
            "neutral": {
                "productive": [
                    {
                        "title": "Organize One Small Space",
                        "description": "Clean your desk, organize a drawer, or tidy up one corner of your room",
                        "duration": "10-20 minutes",
                        "type": "organization",
                        "icon": "🧹"
                    },
                    {
                        "title": "Learn Something New",
                        "description": "Watch a tutorial, read an article, or practice a skill for 10 minutes",
                        "duration": "10-30 minutes",
                        "type": "learning",
                        "icon": "📚"
                    },
                    {
                        "title": "Plan Something Fun",
                        "description": "Plan a future activity, trip, or goal. Having something to look forward to helps mood",
                        "duration": "10-15 minutes",
                        "type": "planning",
                        "icon": "📅"
                    }
                ],
                "self_care": [
                    {
                        "title": "Take a Relaxing Shower/Bath",
                        "description": "Enjoy warm water, use nice soap or bubbles, and focus on the sensation",
                        "duration": "15-30 minutes",
                        "type": "hygiene",
                        "icon": "🛁"
                    },
                    {
                        "title": "Do Skincare or Grooming",
                        "description": "Wash your face, moisturize, brush your teeth, or do your hair nicely",
                        "duration": "10-15 minutes",
                        "type": "grooming",
                        "icon": "🧴"
                    },
                    {
                        "title": "Make Your Bed",
                        "description": "Start your day with one accomplished task. It sets a positive tone",
                        "duration": "2-5 minutes",
                        "type": "organization",
                        "icon": "🛏️"
                    }
                ],
                "nature": [
                    {
                        "title": "Sit Outside for 10 Minutes",
                        "description": "Get some fresh air and sunlight. Even a balcony or window works",
                        "duration": "10-15 minutes",
                        "type": "nature",
                        "icon": "🌞"
                    },
                    {
                        "title": "Water Your Plants",
                        "description": "Care for plants or flowers. If you don't have any, look at plants outside",
                        "duration": "5-10 minutes",
                        "type": "nature",
                        "icon": "🌱"
                    }
                ]
            },
            
            # For Positive Moods (Maintain & Enhance)
            "positive": {
                "social": [
                    {
                        "title": "Share Your Good Mood",
                        "description": "Call someone you love and share something positive that happened today",
                        "duration": "10-20 minutes",
                        "type": "social",
                        "icon": "📞"
                    },
                    {
                        "title": "Do Something Kind",
                        "description": "Send an encouraging message, help someone, or do a small act of kindness",
                        "duration": "5-15 minutes",
                        "type": "kindness",
                        "icon": "💝"
                    }
                ],
                "creative": [
                    {
                        "title": "Start a Creative Project",
                        "description": "Begin something you've been wanting to try - art, writing, music, crafts",
                        "duration": "20-60 minutes",
                        "type": "creative",
                        "icon": "🎨"
                    },
                    {
                        "title": "Take on a Fun Challenge",
                        "description": "Try a puzzle, brain teaser, or learn a new skill while you're feeling motivated",
                        "duration": "15-30 minutes",
                        "type": "challenge",
                        "icon": "🧩"
                    }
                ],
                "celebration": [
                    {
                        "title": "Celebrate Small Wins",
                        "description": "Acknowledge something you accomplished recently, even if it seems small",
                        "duration": "5-10 minutes",
                        "type": "reflection",
                        "icon": "🎉"
                    },
                    {
                        "title": "Treat Yourself",
                        "description": "Have a favorite snack, watch a good movie, or do something you enjoy",
                        "duration": "30-60 minutes",
                        "type": "reward",
                        "icon": "🍰"
                    }
                ]
            }
        }
    
    def get_recommendations(self, mood_score: float, crisis_level: str = "none", 
                          num_activities: int = 3, user_preferences: List[str] = None) -> Dict[str, Any]:
        """
        Get personalized activity recommendations based on mood and crisis level.
        
        Args:
            mood_score: Float between -1 (very negative) and 1 (very positive)
            crisis_level: 'critical', 'high', 'moderate', or 'none'
            num_activities: Number of activities to recommend
            user_preferences: List of preferred activity types
        
        Returns:
            Dictionary with recommended activities and explanation
        """
        
        # Determine mood category
        if crisis_level in ['critical', 'high']:
            category = "crisis"
            explanation = "🚨 Right now, focus on immediate comfort and grounding techniques."
        elif mood_score < -0.5:
            category = "moderate_negative"
            explanation = "💙 Here are some gentle activities to help lift your mood."
        elif mood_score < 0.1:
            category = "neutral"
            explanation = "🌱 These activities can help enhance your day and boost your energy."
        else:
            category = "positive"
            explanation = "✨ You're feeling good! Here are ways to maintain and celebrate your positive mood."
        
        # Get activities from the appropriate category
        available_activities = []
        for subcategory, activities in self.activities[category].items():
            available_activities.extend(activities)
        
        # Filter by user preferences if provided
        if user_preferences:
            filtered_activities = []
            for activity in available_activities:
                if any(pref.lower() in activity['type'].lower() or 
                      pref.lower() in activity['title'].lower() for pref in user_preferences):
                    filtered_activities.append(activity)
            if filtered_activities:
                available_activities = filtered_activities
        
        # Randomly select activities
        selected_activities = random.sample(
            available_activities, 
            min(num_activities, len(available_activities))
        )
        
        return {
            "mood_category": category,
            "explanation": explanation,
            "activities": selected_activities,
            "mood_score": mood_score,
            "crisis_level": crisis_level,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_emergency_activities(self) -> List[Dict[str, Any]]:
        """Get immediate grounding activities for crisis situations."""
        return self.activities["crisis"]["grounding"] + self.activities["crisis"]["immediate_comfort"]
    
    def get_daily_activity(self) -> Dict[str, Any]:
        """Get a random daily wellness activity."""
        all_activities = []
        for category in self.activities.values():
            for subcategory in category.values():
                all_activities.extend(subcategory)
        
        activity = random.choice(all_activities)
        return {
            "daily_activity": activity,
            "message": "💡 Daily Wellness Suggestion",
            "timestamp": datetime.now().isoformat()
        }

# Global instance
activity_engine = ActivityRecommendationEngine()

def get_activity_recommendations(mood_score: float, crisis_level: str = "none", 
                               num_activities: int = 3) -> Dict[str, Any]:
    """Convenience function to get activity recommendations."""
    return activity_engine.get_recommendations(mood_score, crisis_level, num_activities)

def get_crisis_activities() -> List[Dict[str, Any]]:
    """Get immediate activities for crisis situations."""
    return activity_engine.get_emergency_activities()
