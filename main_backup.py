from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
import shutil
import os
import tempfile
from typing import Optional
from model import analyze_mood
from cbt_tips import cbt_tips
from voice_emotion import analyze_voice_emotion
from face_emotion import analyze_face_emotion
from multimodal_fusion import fuse_multimodal_emotions

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze_text")
def analyze_text(data: TextInput):
    """Legacy text-only analysis endpoint for backward compatibility."""
    mood_score, mood_label = analyze_mood(data.text)
    tip = random.choice(cbt_tips)
    return {
        "mood_score": round(mood_score, 2),
        "mood_label": mood_label,
        "cbt_tip": tip
    }

@app.post("/analyze_multimodal")
async def analyze_multimodal(
    text: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Multi-modal emotion analysis endpoint.
    Accepts text, optional audio file, and optional image file.
    """
    
    # Initialize results
    text_score = None
    text_confidence = 1.0
    voice_label = None
    voice_confidence = 0.0
    face_label = None
    face_confidence = 0.0
    
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
    
    # 2. Voice Analysis (if audio provided)
    if audio and audio.filename:
        temp_audio_path = None
        try:
            # Save uploaded audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                shutil.copyfileobj(audio.file, temp_audio)
                temp_audio_path = temp_audio.name
            
            # Analyze voice emotion
            voice_label, voice_confidence = analyze_voice_emotion(temp_audio_path)
            
        except Exception as e:
            print(f"Voice analysis error: {e}")
            voice_label = "neutral"
            voice_confidence = 0.3
        finally:
            # Clean up temporary file
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
    
    # 3. Face Analysis (if image provided)
    if image and image.filename:
        temp_image_path = None
        try:
            # Save uploaded image to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                shutil.copyfileobj(image.file, temp_image)
                temp_image_path = temp_image.name
            
            # Analyze facial emotion
            face_label, face_confidence = analyze_face_emotion(temp_image_path)
            
        except Exception as e:
            print(f"Face analysis error: {e}")
            face_label = "neutral"
            face_confidence = 0.3
        finally:
            # Clean up temporary file
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
    
    # 4. Fuse all modalities
    fusion_result = fuse_multimodal_emotions(
        text_score=text_score,
        text_confidence=text_confidence,
        voice_label=voice_label,
        voice_confidence=voice_confidence,
        face_label=face_label,
        face_confidence=face_confidence
    )
    
    # 5. Get CBT tip based on final mood
    tip = random.choice(cbt_tips)
    
    # 6. Prepare comprehensive response
    response = {
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
        "recommendation": _get_recommendation(fusion_result["final_mood_score"])
    }
    
    return response

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