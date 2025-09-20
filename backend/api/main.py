from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
import shutil
import os
import tempfile
import time
from typing import Optional, Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model import analyze_mood
from utils.cbt_tips import cbt_tips
from utils.activity_recommendations import get_activity_recommendations, get_crisis_activities
from utils.daily_questions import get_daily_questions, calculate_daily_wellness_score
from services.crisis_detection import check_crisis
from services.emergency_notifications import send_emergency_alert, notification_system
from services.monitoring import monitor, log_request
# Temporarily disable problematic imports
# from voice_emotion import analyze_voice_emotion
# from face_emotion import analyze_face_emotion
# from multimodal_fusion import fuse_multimodal_emotions

app = FastAPI(title="Mental Health AI API - Multi-modal Edition")

# Enable CORS for local development and embedded-mobile localhost access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    location: Optional[str] = "international"
    emergency_contacts: Optional[Dict] = None

class MultimodalInput(BaseModel):
    text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    location: Optional[str] = "international"
    emergency_contacts: Optional[Dict] = None
    user_name: Optional[str] = "User"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze_text")
def analyze_text(data: TextInput):
    """Enhanced text-only analysis endpoint with crisis detection."""
    start_time = time.time()
    
    # Start session if not provided
    session_id = data.session_id or monitor.start_session(data.user_id)
    user_id = data.user_id or f"anonymous_{int(time.time())}"
    
    try:
        # Analyze mood
        mood_score, mood_label = analyze_mood(data.text)
        
        # Check for crisis
        crisis_result = check_crisis(data.text, mood_score, data.location, user_id)
        
        # Get CBT tip
        tip = random.choice(cbt_tips)
        
        # Get activity recommendations based on mood and crisis level
        activities = get_activity_recommendations(
            mood_score=mood_score,
            crisis_level=crisis_result["analysis"]["crisis_level"],
            num_activities=3
        )
        
        # Prepare response
        response = {
            "session_id": session_id,
            "mood_score": round(mood_score, 2),
            "mood_label": mood_label,
            "cbt_tip": tip,
            "crisis_detected": crisis_result["analysis"]["is_crisis"],
            "crisis_level": crisis_result["analysis"]["crisis_level"],
            "recommended_activities": activities
        }
        
        # Handle crisis response
        if crisis_result["analysis"]["is_crisis"]:
            crisis_response = crisis_result["response"]
            response.update({
                "status": crisis_response["status"],
                "priority": crisis_response["priority"],
                "message": crisis_response["message"],
                "helplines": crisis_response["helplines"],
                "immediate_steps": crisis_response["immediate_steps"]
            })
            
            # Send emergency notifications if contacts provided
            if data.emergency_contacts and crisis_response["priority"] in ["immediate", "urgent"]:
                try:
                    notification_result = send_emergency_alert(
                        emergency_contacts=data.emergency_contacts,
                        user_name=getattr(data, 'user_name', 'User'),
                        crisis_level=crisis_result["analysis"]["crisis_level"],
                        additional_context=f"User input: '{data.text}'"
                    )
                    response["emergency_notifications"] = notification_result
                except Exception as e:
                    response["emergency_notifications"] = {"error": str(e)}
        
        # Log the interaction
        processing_time = int((time.time() - start_time) * 1000)
        log_request(
            session_id=session_id,
            user_id=user_id,
            input_data={"text": data.text, "type": "text", "location": data.location},
            analysis_result={
                "mood_score": mood_score,
                "mood_label": mood_label,
                "is_crisis": crisis_result["analysis"]["is_crisis"],
                "crisis_level": crisis_result["analysis"]["crisis_level"],
                "crisis_keywords": crisis_result["analysis"]["found_keywords"],
                "response_type": "crisis" if crisis_result["analysis"]["is_crisis"] else "standard",
                "emergency_contacts_notified": "emergency_notifications" in response,
                "follow_up_required": crisis_result["response"]["follow_up_required"]
            },
            processing_time_ms=processing_time
        )
        
        return response
        
    except Exception as e:
        # Log error
        monitor.log_system_metric("error_rate", 1, "count", {"error": str(e), "endpoint": "analyze_text"})
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze_multimodal")
async def analyze_multimodal(
    text: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    location: Optional[str] = Form("international"),
    emergency_contacts: Optional[str] = Form(None),  # JSON string
    user_name: Optional[str] = Form("User")
):
    """
    Enhanced multi-modal emotion analysis endpoint with crisis detection.
    Accepts text, optional audio file, and optional image file.
    Currently simplified to work with text analysis only.
    """
    start_time = time.time()
    
    # Parse emergency contacts if provided
    emergency_contacts_dict = None
    if emergency_contacts:
        try:
            import json
            emergency_contacts_dict = json.loads(emergency_contacts)
        except:
            pass
    
    # Start session if not provided
    session_id = session_id or monitor.start_session(user_id)
    user_id = user_id or f"anonymous_{int(time.time())}"
    
    # Initialize results
    text_score = None
    text_confidence = 1.0
    
    # 1. Text Analysis
    if text and text.strip():
        try:
            text_score, text_label = analyze_mood(text)
            # Convert text label to confidence (simple heuristic)
            text_confidence = min(0.9, abs(text_score) + 0.5)
        except Exception as e:
            print(f"Text analysis error: {e}")
            text_score = 0.0
            text_confidence = 0.3
    
    # 2. Voice Analysis (simplified - just acknowledge file received)
    voice_label = None
    voice_confidence = 0.0
    if audio and audio.filename:
        print(f"Audio file received: {audio.filename}")
        voice_label = "neutral"  # Placeholder
        voice_confidence = 0.5
        # Clean up the uploaded file
        audio.file.close()
    
    # 3. Face Analysis (simplified - just acknowledge file received)
    face_label = None
    face_confidence = 0.0
    if image and image.filename:
        print(f"Image file received: {image.filename}")
        face_label = "neutral"  # Placeholder
        face_confidence = 0.5
        # Clean up the uploaded file
        image.file.close()
    
    # 4. Simple fusion (primarily text-based for now)
    final_mood_score = text_score if text_score is not None else 0.0
    final_confidence = text_confidence
    
    fusion_result = {
        "final_mood_score": final_mood_score,
        "final_confidence": final_confidence,
        "primary_modality": "text"
    }
    
    # 5. Get CBT tip based on final mood
    tip = random.choice(cbt_tips)
    
    # 6. Crisis detection
    crisis_result = check_crisis(text, final_mood_score, location, user_id)
    
    # 7. Prepare comprehensive response
    response = {
        "session_id": session_id,
        "multimodal_analysis": fusion_result,
        "individual_results": {
            "text": {
                "score": text_score,
                "confidence": text_confidence,
                "original_text": text
            } if text_score is not None else None,
            "voice": {
                "emotion": voice_label,
                "confidence": voice_confidence
            } if voice_label else None,
            "face": {
                "emotion": face_label,
                "confidence": face_confidence
            } if face_label else None
        },
        "cbt_tip": tip,
        "recommendation": _get_recommendation(final_mood_score),
        "crisis_detected": crisis_result["analysis"]["is_crisis"],
        "crisis_level": crisis_result["analysis"]["crisis_level"]
    }
    
    # Handle crisis response
    if crisis_result["analysis"]["is_crisis"]:
        crisis_response = crisis_result["response"]
        response.update({
            "status": crisis_response["status"],
            "priority": crisis_response["priority"],
            "message": crisis_response["message"],
            "helplines": crisis_response["helplines"],
            "immediate_steps": crisis_response["immediate_steps"]
        })
        
        # Send emergency notifications if contacts provided
        if emergency_contacts_dict and crisis_response["priority"] in ["immediate", "urgent"]:
            try:
                notification_result = send_emergency_alert(
                    emergency_contacts=emergency_contacts_dict,
                    user_name=user_name,
                    crisis_level=crisis_result["analysis"]["crisis_level"],
                    additional_context=f"User input: '{text}'"
                )
                response["emergency_notifications"] = notification_result
            except Exception as e:
                response["emergency_notifications"] = {"error": str(e)}
    
    # Log the interaction
    processing_time = int((time.time() - start_time) * 1000)
    log_request(
        session_id=session_id,
        user_id=user_id,
        input_data={"text": text, "type": "multimodal", "location": location},
        analysis_result={
            "mood_score": final_mood_score,
            "mood_label": "POSITIVE" if final_mood_score > 0 else "NEGATIVE",
            "is_crisis": crisis_result["analysis"]["is_crisis"],
            "crisis_level": crisis_result["analysis"]["crisis_level"],
            "crisis_keywords": crisis_result["analysis"]["found_keywords"],
            "response_type": "crisis" if crisis_result["analysis"]["is_crisis"] else "multimodal",
            "emergency_contacts_notified": "emergency_notifications" in response,
            "follow_up_required": crisis_result["response"]["follow_up_required"]
        },
        processing_time_ms=processing_time
    )
    
    return response

@app.post("/start_session")
def start_session(user_id: Optional[str] = None):
    """Start a new user session."""
    session_id = monitor.start_session(user_id)
    return {
        "session_id": session_id,
        "user_id": user_id or f"anonymous_{int(time.time())}",
        "started_at": time.time()
    }

@app.post("/end_session")
def end_session(session_id: str):
    """End a user session."""
    monitor.end_session(session_id)
    return {"status": "session_ended", "session_id": session_id}

@app.get("/analytics")
def get_analytics(days: int = 7, user_id: str = None):
    """Get analytics for the specified number of days. If user_id provided, returns user-specific analytics."""
    try:
        if user_id:
            return monitor.get_user_analytics(user_id=user_id, days=days)
        else:
            return monitor.get_analytics_summary(days=days)
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/user_analytics/{user_id}")
def get_user_specific_analytics(user_id: str, days: int = 7):
    """Get analytics specific to a user."""
    try:
        return monitor.get_user_analytics(user_id=user_id, days=days)
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/crisis_alerts")
def get_crisis_alerts(unresolved_only: bool = True):
    """Get crisis alerts that may need follow-up."""
    return monitor.get_crisis_alerts(unresolved_only)

@app.post("/mark_crisis_resolved")
def mark_crisis_resolved(crisis_id: str, resolution_status: str = "resolved"):
    """Mark a crisis event as resolved."""
    monitor.mark_crisis_resolved(crisis_id, resolution_status)
    return {"status": "crisis_marked_resolved", "crisis_id": crisis_id}

@app.get("/system_status")
def get_system_status():
    """Get system status and health metrics."""
    try:
        # Test database connection
        analytics = monitor.get_analytics_summary(days=1)
        
        return {
            "status": "healthy",
            "database": "connected",
            "crisis_detection": "enabled",
            "emergency_notifications": {
                "sms": notification_system.twilio_client is not None,
                "email": notification_system.email_address is not None
            },
            "today_stats": {
                "interactions": analytics.get("total_interactions", 0),
                "crisis_events": analytics.get("total_crisis_events", 0),
                "unique_users": analytics.get("unique_users", 0)
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }, 500

@app.get("/daily_activity")
def get_daily_activity():
    """Get a random daily wellness activity suggestion."""
    from utils.activity_recommendations import activity_engine
    return activity_engine.get_daily_activity()

@app.post("/get_activities")
def get_personalized_activities(request: dict):
    """Get personalized activity recommendations."""
    mood_score = request.get("mood_score", 0.0)
    crisis_level = request.get("crisis_level", "none")
    num_activities = request.get("num_activities", 3)
    user_preferences = request.get("preferences", [])
    
    from utils.activity_recommendations import activity_engine
    return activity_engine.get_recommendations(
        mood_score=mood_score,
        crisis_level=crisis_level,
        num_activities=num_activities,
        user_preferences=user_preferences
    )

@app.get("/daily_questions/{user_id}")
def get_user_daily_questions(user_id: str):
    """Get daily questions for a user."""
    try:
        return get_daily_questions(user_id)
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/submit_daily_checkin")
def submit_daily_checkin(data: dict):
    """Submit daily check-in answers and update streak."""
    try:
        user_id = data.get("user_id", "flutter_user")
        questions_data = data.get("questions_data", {})
        answers_data = data.get("answers", [])
        
        # Calculate wellness score
        score_result = calculate_daily_wellness_score(answers_data)
        
        # Save to database
        checkin_id = monitor.save_daily_checkin(
            user_id=user_id,
            questions_data=questions_data,
            answers_data=answers_data,
            wellness_score=score_result["overall_score"],
            wellness_category=score_result["wellness_category"],
            category_scores=score_result["category_scores"]
        )
        
        # Get updated streak info
        streak_info = monitor.get_user_streak_info(user_id)
        
        # Get daily scores for insights
        daily_scores = monitor.get_user_daily_scores(user_id, days=30)
        
        # Generate insights and recommendations
        from utils.daily_questions import daily_questions_engine
        insights = daily_questions_engine.get_streak_insights(daily_scores)
        
        # Check if user needs intervention
        needs_intervention = score_result["wellness_category"] in ["concerning", "critical"]
        
        return {
            "checkin_id": checkin_id,
            "wellness_score": score_result,
            "streak_info": streak_info,
            "insights": insights,
            "needs_intervention": needs_intervention,
            "message": "Daily check-in completed successfully!"
        }
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/streak_info/{user_id}")
def get_streak_info(user_id: str):
    """Get user's streak information."""
    try:
        return monitor.get_user_streak_info(user_id)
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/daily_scores/{user_id}")
def get_user_daily_scores(user_id: str, days: int = 30):
    """Get user's daily wellness scores."""
    try:
        return monitor.get_user_daily_scores(user_id, days)
    except Exception as e:
        return {"error": str(e)}, 500

def _get_recommendation(mood_score: float) -> str:
    """Generate personalized recommendation based on mood score."""
    if mood_score <= -0.7:
        return "Consider reaching out to a mental health professional. Your wellbeing is important."
    elif mood_score <= -0.3:
        return "Try some relaxation techniques or talk to someone you trust."
    elif mood_score <= 0.1:
        return "Consider engaging in activities that usually make you feel good."
    elif mood_score <= 0.5:
        return "You seem to be doing well. Keep up the positive momentum!"
    else:
        return "Great to see you're feeling positive! Share your good energy with others."