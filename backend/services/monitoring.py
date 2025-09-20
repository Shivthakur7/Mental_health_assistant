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
