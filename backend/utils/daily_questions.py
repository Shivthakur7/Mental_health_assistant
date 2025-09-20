"""
Daily Questions System for Mental Health Streak
Provides daily mental health check-in questions to track user progress and engagement.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class DailyQuestionsEngine:
    def __init__(self):
        self.questions = {
            "mood_check": [
                {
                    "id": "mood_1",
                    "question": "How are you feeling today overall?",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 10,
                    "scale_labels": {1: "Very Bad", 5: "Neutral", 10: "Excellent"},
                    "category": "mood"
                },
                {
                    "id": "energy_1",
                    "question": "How is your energy level today?",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 10,
                    "scale_labels": {1: "Exhausted", 5: "Moderate", 10: "Very Energetic"},
                    "category": "energy"
                },
                {
                    "id": "stress_1",
                    "question": "How stressed do you feel right now?",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 10,
                    "scale_labels": {1: "Very Calm", 5: "Moderate", 10: "Very Stressed"},
                    "category": "stress"
                }
            ],
            "wellbeing_check": [
                {
                    "id": "sleep_1",
                    "question": "How well did you sleep last night?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": 4, "text": "Excellent - 8+ hours, felt rested"},
                        {"value": 3, "text": "Good - 6-8 hours, mostly rested"},
                        {"value": 2, "text": "Fair - 4-6 hours, somewhat tired"},
                        {"value": 1, "text": "Poor - Less than 4 hours, very tired"}
                    ],
                    "category": "sleep"
                },
                {
                    "id": "social_1",
                    "question": "Did you have meaningful social interaction today?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": 4, "text": "Yes, quality time with friends/family"},
                        {"value": 3, "text": "Yes, some good conversations"},
                        {"value": 2, "text": "A little, brief interactions"},
                        {"value": 1, "text": "No, felt isolated today"}
                    ],
                    "category": "social"
                },
                {
                    "id": "activity_1",
                    "question": "Did you do any physical activity today?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": 4, "text": "Yes, intense exercise (30+ min)"},
                        {"value": 3, "text": "Yes, moderate activity (15-30 min)"},
                        {"value": 2, "text": "Yes, light activity (walking, etc.)"},
                        {"value": 1, "text": "No, mostly sedentary today"}
                    ],
                    "category": "physical"
                }
            ],
            "reflection": [
                {
                    "id": "gratitude_1",
                    "question": "What's one thing you're grateful for today?",
                    "type": "text",
                    "placeholder": "I'm grateful for...",
                    "category": "gratitude"
                },
                {
                    "id": "achievement_1",
                    "question": "What's one small thing you accomplished today?",
                    "type": "text",
                    "placeholder": "Today I accomplished...",
                    "category": "achievement"
                },
                {
                    "id": "challenge_1",
                    "question": "What was the biggest challenge you faced today?",
                    "type": "text",
                    "placeholder": "My biggest challenge was...",
                    "category": "challenge"
                },
                {
                    "id": "tomorrow_1",
                    "question": "What's one thing you're looking forward to tomorrow?",
                    "type": "text",
                    "placeholder": "Tomorrow I'm looking forward to...",
                    "category": "future"
                }
            ],
            "coping_check": [
                {
                    "id": "coping_1",
                    "question": "How well did you handle stress today?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": 4, "text": "Very well - used healthy coping strategies"},
                        {"value": 3, "text": "Pretty well - managed most situations"},
                        {"value": 2, "text": "Okay - struggled but got through it"},
                        {"value": 1, "text": "Poorly - felt overwhelmed most of the day"}
                    ],
                    "category": "coping"
                },
                {
                    "id": "support_1",
                    "question": "Did you reach out for support when needed today?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": 4, "text": "Yes, and got the help I needed"},
                        {"value": 3, "text": "Yes, reached out to someone"},
                        {"value": 2, "text": "Thought about it but didn't"},
                        {"value": 1, "text": "No, handled everything alone"}
                    ],
                    "category": "support"
                }
            ]
        }
    
    def get_daily_questions(self, user_id: str, date: str = None) -> Dict[str, Any]:
        """
        Get daily questions for a user. Returns different questions based on the date
        to ensure variety while maintaining consistency.
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Use date as seed for consistent daily questions
        random.seed(f"{user_id}_{date}")
        
        # Select one question from each category
        selected_questions = []
        
        # Always include mood check
        selected_questions.append(random.choice(self.questions["mood_check"]))
        
        # Rotate through other categories based on day of week
        day_of_week = datetime.strptime(date, '%Y-%m-%d').weekday()
        
        if day_of_week in [0, 3, 6]:  # Monday, Thursday, Sunday
            selected_questions.extend(random.sample(self.questions["wellbeing_check"], 2))
        elif day_of_week in [1, 4]:  # Tuesday, Friday
            selected_questions.append(random.choice(self.questions["reflection"]))
            selected_questions.append(random.choice(self.questions["coping_check"]))
        else:  # Wednesday, Saturday
            selected_questions.append(random.choice(self.questions["wellbeing_check"]))
            selected_questions.append(random.choice(self.questions["reflection"]))
        
        return {
            "date": date,
            "user_id": user_id,
            "questions": selected_questions,
            "total_questions": len(selected_questions),
            "estimated_time": "2-3 minutes"
        }
    
    def calculate_daily_score(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate daily wellness score based on answers.
        """
        if not answers:
            return {"score": 0, "category": "no_data"}
        
        total_score = 0
        max_possible = 0
        category_scores = {}
        
        for answer in answers:
            question_id = answer.get("question_id")
            value = answer.get("value", 0)
            category = answer.get("category", "general")
            
            # Find the question to get max value
            question = self._find_question_by_id(question_id)
            if question:
                if question["type"] == "scale":
                    max_val = question["scale_max"]
                    total_score += value
                    max_possible += max_val
                elif question["type"] == "multiple_choice":
                    max_val = max([opt["value"] for opt in question["options"]])
                    total_score += value
                    max_possible += max_val
                elif question["type"] == "text":
                    # Text answers get a base score of 3/4 for completion
                    total_score += 3
                    max_possible += 4
                
                # Track category scores
                if category not in category_scores:
                    category_scores[category] = {"total": 0, "max": 0, "count": 0}
                category_scores[category]["total"] += value if question["type"] != "text" else 3
                category_scores[category]["max"] += max_val if question["type"] != "text" else 4
                category_scores[category]["count"] += 1
        
        # Calculate overall score (0-100)
        overall_score = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        # Determine wellness category
        if overall_score >= 80:
            wellness_category = "excellent"
        elif overall_score >= 65:
            wellness_category = "good"
        elif overall_score >= 50:
            wellness_category = "fair"
        elif overall_score >= 35:
            wellness_category = "concerning"
        else:
            wellness_category = "critical"
        
        # Calculate category percentages
        category_percentages = {}
        for cat, data in category_scores.items():
            category_percentages[cat] = (data["total"] / data["max"] * 100) if data["max"] > 0 else 0
        
        return {
            "overall_score": round(overall_score, 1),
            "wellness_category": wellness_category,
            "category_scores": category_percentages,
            "total_answers": len(answers),
            "completion_rate": 100.0  # Since they answered all presented questions
        }
    
    def _find_question_by_id(self, question_id: str) -> Dict[str, Any]:
        """Find a question by its ID across all categories."""
        for category in self.questions.values():
            for question in category:
                if question["id"] == question_id:
                    return question
        return None
    
    def get_streak_insights(self, daily_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze streak data to provide insights and recommendations.
        """
        if not daily_scores:
            return {"message": "Start your daily check-in streak to get insights!"}
        
        # Calculate trends
        scores = [score["overall_score"] for score in daily_scores[-7:]]  # Last 7 days
        
        if len(scores) >= 2:
            trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
            avg_score = sum(scores) / len(scores)
        else:
            trend = "stable"
            avg_score = scores[0] if scores else 0
        
        # Determine recommendations
        recommendations = []
        if avg_score < 50:
            recommendations.extend([
                "Consider reaching out to a mental health professional",
                "Focus on basic self-care: sleep, nutrition, hydration",
                "Try gentle activities like short walks or deep breathing"
            ])
        elif avg_score < 70:
            recommendations.extend([
                "Maintain your current positive habits",
                "Consider adding one new wellness activity",
                "Connect with friends or family for support"
            ])
        else:
            recommendations.extend([
                "Great job maintaining your mental wellness!",
                "Consider helping others or volunteering",
                "Keep up your excellent self-care routine"
            ])
        
        return {
            "current_streak": len(daily_scores),
            "average_score": round(avg_score, 1),
            "trend": trend,
            "wellness_level": daily_scores[-1]["wellness_category"] if daily_scores else "unknown",
            "recommendations": recommendations,
            "next_milestone": self._get_next_milestone(len(daily_scores))
        }
    
    def _get_next_milestone(self, current_streak: int) -> Dict[str, Any]:
        """Get the next streak milestone."""
        milestones = [7, 14, 30, 60, 100, 365]
        
        for milestone in milestones:
            if current_streak < milestone:
                return {
                    "days": milestone,
                    "days_remaining": milestone - current_streak,
                    "reward": self._get_milestone_reward(milestone)
                }
        
        return {
            "days": current_streak + 100,
            "days_remaining": 100,
            "reward": "Mental Health Champion Badge!"
        }
    
    def _get_milestone_reward(self, days: int) -> str:
        """Get reward message for milestone."""
        rewards = {
            7: "Week Warrior Badge! 🏆",
            14: "Two Week Champion! 🌟",
            30: "Monthly Master Badge! 🎯",
            60: "Wellness Warrior! 💪",
            100: "Hundred Day Hero! 🚀",
            365: "Year-Long Legend! 👑"
        }
        return rewards.get(days, "Amazing Streak Badge! 🎉")

# Global instance
daily_questions_engine = DailyQuestionsEngine()

def get_daily_questions(user_id: str, date: str = None) -> Dict[str, Any]:
    """Convenience function to get daily questions."""
    return daily_questions_engine.get_daily_questions(user_id, date)

def calculate_daily_wellness_score(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convenience function to calculate daily score."""
    return daily_questions_engine.calculate_daily_score(answers)
