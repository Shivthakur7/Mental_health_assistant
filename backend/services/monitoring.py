"""
Monitoring and Logging System for Mental Health Assistant
Provides comprehensive logging, analytics, and monitoring capabilities.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mental_health_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MentalHealthMonitor:
    def __init__(self, db_path: str = "mental_health_analytics.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for analytics and monitoring."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_start TIMESTAMP,
                    session_end TIMESTAMP,
                    total_interactions INTEGER DEFAULT 0,
                    crisis_events INTEGER DEFAULT 0,
                    average_mood_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Individual interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    input_text TEXT,
                    input_type TEXT,  -- 'text', 'voice', 'multimodal'
                    mood_score REAL,
                    mood_label TEXT,
                    is_crisis BOOLEAN,
                    crisis_level TEXT,
                    crisis_keywords TEXT,  -- JSON array
                    response_type TEXT,
                    processing_time_ms INTEGER,
                    user_location TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions (id)
                )
            ''')
            
            # Crisis events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crisis_events (
                    id TEXT PRIMARY KEY,
                    interaction_id TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    crisis_level TEXT,
                    crisis_keywords TEXT,  -- JSON array
                    mood_score REAL,
                    emergency_contacts_notified BOOLEAN DEFAULT FALSE,
                    notification_results TEXT,  -- JSON
                    follow_up_required BOOLEAN DEFAULT FALSE,
                    follow_up_completed BOOLEAN DEFAULT FALSE,
                    resolution_status TEXT,
                    FOREIGN KEY (interaction_id) REFERENCES interactions (id)
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_unit TEXT,
                    additional_data TEXT  -- JSON
                )
            ''')
            
            # Daily check-ins table for streak system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_checkins (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    date DATE,
                    questions_data TEXT,  -- JSON of questions asked
                    answers_data TEXT,    -- JSON of user answers
                    wellness_score REAL,
                    wellness_category TEXT,
                    category_scores TEXT, -- JSON of category breakdowns
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, date)
                )
            ''')
            
            # User streaks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_streaks (
                    user_id TEXT PRIMARY KEY,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_checkin_date DATE,
                    total_checkins INTEGER DEFAULT 0,
                    streak_milestones TEXT,  -- JSON array of achieved milestones
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def start_session(self, user_id: str = None) -> str:
        """Start a new user session."""
        session_id = str(uuid.uuid4())
        user_id = user_id or f"anonymous_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (id, user_id, session_start)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Started session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return session_id

    def log_interaction(self, 
                       session_id: str,
                       user_id: str,
                       input_text: str,
                       input_type: str,
                       mood_score: float,
                       mood_label: str,
                       is_crisis: bool = False,
                       crisis_level: str = None,
                       crisis_keywords: List[str] = None,
                       response_type: str = "standard",
                       processing_time_ms: int = 0,
                       user_location: str = "unknown") -> str:
        """Log a user interaction."""
        interaction_id = str(uuid.uuid4())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interactions (
                    id, session_id, user_id, input_text, input_type,
                    mood_score, mood_label, is_crisis, crisis_level,
                    crisis_keywords, response_type, processing_time_ms, user_location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction_id, session_id, user_id, input_text, input_type,
                mood_score, mood_label, is_crisis, crisis_level,
                json.dumps(crisis_keywords) if crisis_keywords else None,
                response_type, processing_time_ms, user_location
            ))
            
            # Update session statistics
            cursor.execute('''
                UPDATE user_sessions 
                SET total_interactions = total_interactions + 1,
                    crisis_events = crisis_events + ?,
                    average_mood_score = (
                        SELECT AVG(mood_score) 
                        FROM interactions 
                        WHERE session_id = ?
                    )
                WHERE id = ?
            ''', (1 if is_crisis else 0, session_id, session_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Logged interaction {interaction_id} for session {session_id}")
            return interaction_id
            
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
            return interaction_id

    def log_crisis_event(self,
                        interaction_id: str,
                        user_id: str,
                        crisis_level: str,
                        crisis_keywords: List[str],
                        mood_score: float,
                        emergency_contacts_notified: bool = False,
                        notification_results: Dict = None,
                        follow_up_required: bool = False) -> str:
        """Log a crisis event."""
        crisis_id = str(uuid.uuid4())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crisis_events (
                    id, interaction_id, user_id, crisis_level, crisis_keywords,
                    mood_score, emergency_contacts_notified, notification_results,
                    follow_up_required
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                crisis_id, interaction_id, user_id, crisis_level,
                json.dumps(crisis_keywords), mood_score,
                emergency_contacts_notified,
                json.dumps(notification_results) if notification_results else None,
                follow_up_required
            ))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"CRISIS EVENT LOGGED: {crisis_id} - Level: {crisis_level}")
            return crisis_id
            
        except Exception as e:
            logger.error(f"Failed to log crisis event: {e}")
            return crisis_id

    def log_system_metric(self, metric_name: str, metric_value: float, metric_unit: str = "", additional_data: Dict = None):
        """Log system performance metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics (id, metric_name, metric_value, metric_unit, additional_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), metric_name, metric_value, metric_unit,
                json.dumps(additional_data) if additional_data else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log system metric: {e}")

    def end_session(self, session_id: str):
        """End a user session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET session_end = ?
                WHERE id = ?
            ''', (datetime.now(), session_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ended session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")

    def get_analytics_summary(self, days: int = 7) -> Dict:
        """Get analytics summary for the specified number of days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Total interactions
            cursor.execute('''
                SELECT COUNT(*) FROM interactions 
                WHERE timestamp >= ?
            ''', (start_date,))
            total_interactions = cursor.fetchone()[0]
            
            # Crisis events
            cursor.execute('''
                SELECT COUNT(*) FROM crisis_events 
                WHERE timestamp >= ?
            ''', (start_date,))
            total_crisis_events = cursor.fetchone()[0]
            
            # Average mood score
            cursor.execute('''
                SELECT AVG(mood_score) FROM interactions 
                WHERE timestamp >= ? AND mood_score IS NOT NULL
            ''', (start_date,))
            avg_mood_score = cursor.fetchone()[0] or 0
            
            # Crisis levels breakdown
            cursor.execute('''
                SELECT crisis_level, COUNT(*) 
                FROM crisis_events 
                WHERE timestamp >= ?
                GROUP BY crisis_level
            ''', (start_date,))
            crisis_breakdown = dict(cursor.fetchall())
            
            # Daily interaction counts
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM interactions 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date,))
            daily_interactions = dict(cursor.fetchall())
            
            # Unique users
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM interactions 
                WHERE timestamp >= ?
            ''', (start_date,))
            unique_users = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "period_days": days,
                "total_interactions": total_interactions,
                "total_crisis_events": total_crisis_events,
                "crisis_rate": (total_crisis_events / total_interactions * 100) if total_interactions > 0 else 0,
                "average_mood_score": round(avg_mood_score, 3),
                "unique_users": unique_users,
                "crisis_breakdown": crisis_breakdown,
                "daily_interactions": daily_interactions,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics summary: {e}")
            return {"error": str(e)}

    def get_user_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get analytics specific to a user for the specified number of days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # User's total interactions
            cursor.execute('''
                SELECT COUNT(*) FROM interactions 
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, start_date))
            user_interactions = cursor.fetchone()[0]
            
            # User's crisis events
            cursor.execute('''
                SELECT COUNT(*) FROM crisis_events 
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, start_date))
            user_crisis_events = cursor.fetchone()[0]
            
            # User's average mood score
            cursor.execute('''
                SELECT AVG(mood_score) FROM interactions 
                WHERE user_id = ? AND timestamp >= ? AND mood_score IS NOT NULL
            ''', (user_id, start_date))
            user_avg_mood = cursor.fetchone()[0] or 0
            
            # User's mood trend (daily averages)
            cursor.execute('''
                SELECT DATE(timestamp) as date, AVG(mood_score) as avg_mood
                FROM interactions 
                WHERE user_id = ? AND timestamp >= ? AND mood_score IS NOT NULL
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (user_id, start_date))
            mood_trend = dict(cursor.fetchall())
            
            # User's crisis levels breakdown
            cursor.execute('''
                SELECT crisis_level, COUNT(*) 
                FROM crisis_events 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY crisis_level
            ''', (user_id, start_date))
            user_crisis_breakdown = dict(cursor.fetchall())
            
            # User's daily activity pattern
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as interactions
                FROM interactions 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (user_id, start_date))
            daily_activity = dict(cursor.fetchall())
            
            # User's most active hours
            cursor.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM interactions 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id, start_date))
            active_hours = cursor.fetchall()
            
            # User's session count
            cursor.execute('''
                SELECT COUNT(DISTINCT session_id) FROM interactions 
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, start_date))
            session_count = cursor.fetchone()[0]
            
            # User's improvement indicators
            if len(mood_trend) >= 2:
                mood_values = list(mood_trend.values())
                recent_mood = sum(mood_values[-3:]) / min(3, len(mood_values[-3:]))  # Last 3 days average
                earlier_mood = sum(mood_values[:3]) / min(3, len(mood_values[:3]))   # First 3 days average
                mood_improvement = recent_mood - earlier_mood
            else:
                mood_improvement = 0
            
            conn.close()
            
            return {
                "user_id": user_id,
                "period_days": days,
                "personal_stats": {
                    "total_interactions": user_interactions,
                    "crisis_events": user_crisis_events,
                    "crisis_rate": (user_crisis_events / user_interactions * 100) if user_interactions > 0 else 0,
                    "average_mood_score": round(user_avg_mood, 3),
                    "session_count": session_count,
                    "mood_improvement": round(mood_improvement, 3)
                },
                "trends": {
                    "daily_mood_trend": mood_trend,
                    "daily_activity": daily_activity,
                    "crisis_breakdown": user_crisis_breakdown,
                    "most_active_hours": [{"hour": f"{int(h):02d}:00", "interactions": c} for h, c in active_hours]
                },
                "insights": {
                    "mood_trending": "improving" if mood_improvement > 0.1 else "declining" if mood_improvement < -0.1 else "stable",
                    "activity_level": "high" if user_interactions > days * 2 else "moderate" if user_interactions > days else "low",
                    "crisis_frequency": "concerning" if user_crisis_events > days * 0.3 else "moderate" if user_crisis_events > 0 else "none"
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate user analytics for {user_id}: {e}")
            return {"error": str(e)}

    def save_daily_checkin(self, user_id: str, questions_data: Dict, answers_data: List[Dict], 
                          wellness_score: float, wellness_category: str, category_scores: Dict) -> str:
        """Save daily check-in data and update streak."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            checkin_id = str(uuid.uuid4())
            today = datetime.now().date()
            
            # Save daily check-in
            cursor.execute('''
                INSERT OR REPLACE INTO daily_checkins 
                (id, user_id, date, questions_data, answers_data, wellness_score, 
                 wellness_category, category_scores, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                checkin_id, user_id, today,
                json.dumps(questions_data), json.dumps(answers_data),
                wellness_score, wellness_category, json.dumps(category_scores),
                datetime.now()
            ))
            
            # Update user streak
            self._update_user_streak(cursor, user_id, today)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Daily check-in saved for user {user_id}")
            return checkin_id
            
        except Exception as e:
            logger.error(f"Failed to save daily check-in: {e}")
            return None

    def _update_user_streak(self, cursor, user_id: str, checkin_date):
        """Update user streak information."""
        # Get current streak data
        cursor.execute('''
            SELECT current_streak, longest_streak, last_checkin_date, total_checkins, streak_milestones
            FROM user_streaks WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            current_streak, longest_streak, last_checkin_str, total_checkins, milestones_str = result
            last_checkin = datetime.strptime(last_checkin_str, '%Y-%m-%d').date() if last_checkin_str else None
            milestones = json.loads(milestones_str) if milestones_str else []
        else:
            current_streak, longest_streak, last_checkin, total_checkins, milestones = 0, 0, None, 0, []
        
        # Calculate new streak
        if last_checkin is None:
            # First check-in
            new_streak = 1
        elif checkin_date == last_checkin:
            # Same day, no change
            new_streak = current_streak
        elif checkin_date == last_checkin + timedelta(days=1):
            # Consecutive day
            new_streak = current_streak + 1
        else:
            # Streak broken
            new_streak = 1
        
        # Update longest streak
        new_longest = max(longest_streak, new_streak)
        
        # Check for new milestones
        milestone_days = [7, 14, 30, 60, 100, 365]
        for milestone in milestone_days:
            if new_streak >= milestone and milestone not in milestones:
                milestones.append(milestone)
        
        # Update or insert streak record
        cursor.execute('''
            INSERT OR REPLACE INTO user_streaks 
            (user_id, current_streak, longest_streak, last_checkin_date, 
             total_checkins, streak_milestones, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, new_streak, new_longest, checkin_date,
            total_checkins + 1, json.dumps(milestones), datetime.now()
        ))

    def get_user_streak_info(self, user_id: str) -> Dict[str, Any]:
        """Get user's streak information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT current_streak, longest_streak, last_checkin_date, 
                       total_checkins, streak_milestones
                FROM user_streaks WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                current_streak, longest_streak, last_checkin_str, total_checkins, milestones_str = result
                milestones = json.loads(milestones_str) if milestones_str else []
                
                # Check if streak is still active (checked in today or yesterday)
                today = datetime.now().date()
                last_checkin = datetime.strptime(last_checkin_str, '%Y-%m-%d').date() if last_checkin_str else None
                
                if last_checkin and (today - last_checkin).days > 1:
                    # Streak is broken
                    current_streak = 0
                
                return {
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "last_checkin_date": last_checkin_str,
                    "total_checkins": total_checkins,
                    "milestones_achieved": milestones,
                    "checked_in_today": last_checkin == today if last_checkin else False
                }
            else:
                return {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "last_checkin_date": None,
                    "total_checkins": 0,
                    "milestones_achieved": [],
                    "checked_in_today": False
                }
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to get streak info for {user_id}: {e}")
            return {"error": str(e)}

    def get_user_daily_scores(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's daily wellness scores for trend analysis."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT date, wellness_score, wellness_category, category_scores
                FROM daily_checkins 
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC
            ''', (user_id, start_date.date()))
            
            results = cursor.fetchall()
            
            daily_scores = []
            for date_str, score, category, category_scores_str in results:
                daily_scores.append({
                    "date": date_str,
                    "overall_score": score,
                    "wellness_category": category,
                    "category_scores": json.loads(category_scores_str) if category_scores_str else {}
                })
            
            conn.close()
            return daily_scores
            
        except Exception as e:
            logger.error(f"Failed to get daily scores for {user_id}: {e}")
            return []

    def get_crisis_alerts(self, unresolved_only: bool = True) -> List[Dict]:
        """Get crisis alerts that may need follow-up."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT ce.*, i.input_text, i.user_location
                FROM crisis_events ce
                JOIN interactions i ON ce.interaction_id = i.id
                WHERE ce.follow_up_required = TRUE
            '''
            
            if unresolved_only:
                query += ' AND ce.follow_up_completed = FALSE'
            
            query += ' ORDER BY ce.timestamp DESC'
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            alerts = [dict(zip(columns, row)) for row in results]
            
            conn.close()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get crisis alerts: {e}")
            return []

    def mark_crisis_resolved(self, crisis_id: str, resolution_status: str = "resolved"):
        """Mark a crisis event as resolved."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE crisis_events 
                SET follow_up_completed = TRUE, resolution_status = ?
                WHERE id = ?
            ''', (resolution_status, crisis_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Crisis {crisis_id} marked as {resolution_status}")
            
        except Exception as e:
            logger.error(f"Failed to mark crisis as resolved: {e}")

    def export_analytics(self, output_file: str = None) -> str:
        """Export analytics data to JSON file."""
        if not output_file:
            output_file = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            analytics = self.get_analytics_summary(days=30)  # Last 30 days
            crisis_alerts = self.get_crisis_alerts(unresolved_only=False)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "analytics_summary": analytics,
                "crisis_alerts": crisis_alerts
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Analytics exported to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")
            return None

# Global monitor instance
monitor = MentalHealthMonitor()

def log_request(session_id: str, user_id: str, input_data: Dict, analysis_result: Dict, processing_time_ms: int = 0) -> str:
    """
    Convenience function to log a complete request.
    
    Args:
        session_id: User session ID
        user_id: User identifier
        input_data: Input data (text, type, etc.)
        analysis_result: Analysis results including mood and crisis info
        processing_time_ms: Processing time in milliseconds
        
    Returns:
        Interaction ID
    """
    interaction_id = monitor.log_interaction(
        session_id=session_id,
        user_id=user_id,
        input_text=input_data.get("text", ""),
        input_type=input_data.get("type", "text"),
        mood_score=analysis_result.get("mood_score", 0),
        mood_label=analysis_result.get("mood_label", "unknown"),
        is_crisis=analysis_result.get("is_crisis", False),
        crisis_level=analysis_result.get("crisis_level"),
        crisis_keywords=analysis_result.get("crisis_keywords", []),
        response_type=analysis_result.get("response_type", "standard"),
        processing_time_ms=processing_time_ms,
        user_location=input_data.get("location", "unknown")
    )
    
    # Log crisis event if detected
    if analysis_result.get("is_crisis", False):
        monitor.log_crisis_event(
            interaction_id=interaction_id,
            user_id=user_id,
            crisis_level=analysis_result.get("crisis_level", "unknown"),
            crisis_keywords=analysis_result.get("crisis_keywords", []),
            mood_score=analysis_result.get("mood_score", 0),
            emergency_contacts_notified=analysis_result.get("emergency_contacts_notified", False),
            notification_results=analysis_result.get("notification_results"),
            follow_up_required=analysis_result.get("follow_up_required", False)
        )
    
    return interaction_id

if __name__ == "__main__":
    # Test the monitoring system
    print("Mental Health Monitoring System Test")
    print("=" * 40)
    
    # Start a test session
    session_id = monitor.start_session("test_user")
    print(f"Started session: {session_id}")
    
    # Log a test interaction
    interaction_id = monitor.log_interaction(
        session_id=session_id,
        user_id="test_user",
        input_text="I'm feeling sad today",
        input_type="text",
        mood_score=-0.6,
        mood_label="NEGATIVE",
        is_crisis=False
    )
    print(f"Logged interaction: {interaction_id}")
    
    # Get analytics
    analytics = monitor.get_analytics_summary(days=1)
    print(f"Analytics: {analytics}")
    
    # End session
    monitor.end_session(session_id)
    print("Session ended")
