from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
from model import analyze_mood
from cbt_tips import cbt_tips

app = FastAPI(title="Mental Health AI API")

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
    mood_score, mood_label = analyze_mood(data.text)
    tip = random.choice(cbt_tips)
    return {
        "mood_score": round(mood_score, 2),
        "mood_label": mood_label,
        "cbt_tip": tip
    }