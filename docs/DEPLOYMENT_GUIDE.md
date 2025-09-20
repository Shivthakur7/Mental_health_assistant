# 🚀 Mental Health Assistant - Deployment Guide

This guide covers deploying your Mental Health AI Assistant to various cloud platforms and setting up the complete Stage 4 real-world integration features.

## 📋 Prerequisites

1. **ONNX Model**: Ensure you have run `export_onnx.py` and optionally `quantize_onnx.py`
2. **Dependencies**: Install all requirements with `pip install -r requirements.txt`
3. **Environment Variables**: Configure your `.env` file (see `.env.example`)

## 🔧 Local Development Setup

### 1. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# - Twilio credentials for SMS notifications
# - Email credentials for email notifications
# - Other configuration options
```

### 2. Start the FastAPI Server

```bash
# Start the main API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### 3. Start the Gradio Demo

```bash
# In a separate terminal, start the Gradio interface
python gradio_demo.py

# The demo will be available at http://localhost:7860
# A public sharing link will also be generated
```

## ☁️ Cloud Deployment Options

### Option 1: Hugging Face Spaces (Recommended for Demos)

1. **Create a new Space** on [Hugging Face Spaces](https://huggingface.co/spaces)
2. **Choose Gradio** as the SDK
3. **Upload your files**:
   ```
   app.py (rename gradio_demo.py to app.py)
   requirements.txt
   onnx_model/ (your ONNX model directory)
   *.py (all your Python files)
   ```
4. **Set environment variables** in Space settings:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN` 
   - `TWILIO_PHONE_NUMBER`
   - `EMAIL_ADDRESS`
   - `EMAIL_PASSWORD`
   - `API_BASE_URL=http://localhost:8000`

5. **Create app.py** for Hugging Face Spaces:
   ```python
   # app.py for Hugging Face Spaces
   import subprocess
   import threading
   import time
   import os
   
   # Start FastAPI server in background
   def start_fastapi():
       subprocess.run(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
   
   # Start FastAPI in a separate thread
   threading.Thread(target=start_fastapi, daemon=True).start()
   time.sleep(5)  # Wait for FastAPI to start
   
   # Import and run Gradio demo
   from gradio_demo import create_interface
   
   if __name__ == "__main__":
       interface = create_interface()
       interface.launch()
   ```

### Option 2: Render (Full-Stack Deployment)

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Set environment variables** in Render dashboard
5. **Deploy**: Render will automatically deploy your app

### Option 3: Railway

1. **Create a new project** on [Railway](https://railway.app)
2. **Connect your GitHub repository**
3. **Railway will auto-detect** your Python app
4. **Set environment variables** in Railway dashboard
5. **Deploy**: Railway will handle the rest

### Option 4: Google Cloud Run

1. **Create a Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8080
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Build and deploy**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/mental-health-ai
   gcloud run deploy --image gcr.io/PROJECT_ID/mental-health-ai --platform managed
   ```

## 🔐 Security Configuration

### 1. Environment Variables

**Never commit sensitive credentials to version control!**

Required environment variables:
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token  
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number
- `EMAIL_ADDRESS`: SMTP email address
- `EMAIL_PASSWORD`: SMTP password (use app passwords for Gmail)

### 2. CORS Configuration

For production, update CORS settings in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

Consider adding rate limiting for production:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze_text")
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def analyze_text(request: Request, data: TextInput):
    # ... existing code
```

## 📊 Monitoring and Analytics

### 1. Database Setup

The system uses SQLite by default, which works for demos but consider PostgreSQL for production:

```python
# For PostgreSQL (update monitoring.py)
DATABASE_URL = "postgresql://user:password@localhost/mental_health_db"
```

### 2. Log Management

Logs are written to `mental_health_assistant.log`. For production:
- Use log rotation
- Send logs to centralized logging (e.g., CloudWatch, Datadog)
- Set up alerts for crisis events

### 3. Analytics Dashboard

Access analytics via API endpoints:
- `GET /analytics?days=30` - Usage statistics
- `GET /crisis_alerts` - Crisis events requiring follow-up
- `GET /system_status` - System health

## 🚨 Crisis Management Workflow

### 1. Crisis Detection Flow

```
User Input → Sentiment Analysis → Crisis Keywords Check → Crisis Level Assessment
     ↓
Crisis Detected → Emergency Notifications → Log Crisis Event → Provide Resources
```

### 2. Emergency Contact Setup

Users can provide emergency contacts via:
```json
{
  "emergency_contacts": {
    "phone": "+1234567890",
    "email": "emergency@example.com"
  }
}
```

### 3. Follow-up Management

Mental health professionals can:
1. View crisis alerts: `GET /crisis_alerts`
2. Mark crises as resolved: `POST /mark_crisis_resolved`
3. Export analytics: Use the monitoring system

## 🧪 Testing the System

### 1. Test Crisis Detection

```python
# Test various crisis levels
test_inputs = [
    "I want to kill myself",  # Critical
    "I feel hopeless",        # High  
    "I'm having a bad day",   # Moderate/None
]
```

### 2. Test Emergency Notifications

1. Set up test Twilio and email credentials
2. Use test phone numbers and emails
3. Verify notifications are sent correctly

### 3. Load Testing

```bash
# Install locust for load testing
pip install locust

# Create locustfile.py for testing
# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

## 📱 Mobile Integration

### Flutter App Integration

Update your Flutter app to use the new endpoints:

```dart
// Example Flutter integration
class MentalHealthAPI {
  static const String baseUrl = 'https://your-api-domain.com';
  
  static Future<Map<String, dynamic>> analyzeText({
    required String text,
    String? userId,
    String? sessionId,
    Map<String, String>? emergencyContacts,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/analyze_text'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'user_id': userId,
        'session_id': sessionId,
        'emergency_contacts': emergencyContacts,
      }),
    );
    
    return jsonDecode(response.body);
  }
}
```

## 🔍 Troubleshooting

### Common Issues

1. **ONNX Model Not Found**
   ```bash
   # Ensure you've exported the model
   python export_onnx.py
   ```

2. **Twilio Authentication Failed**
   - Verify your Account SID and Auth Token
   - Check that your Twilio phone number is verified

3. **Email Notifications Not Working**
   - Use app passwords for Gmail
   - Verify SMTP settings
   - Check firewall/security settings

4. **Database Connection Issues**
   - Ensure SQLite file permissions
   - Check database path in monitoring.py

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Production Checklist

- [ ] ONNX model exported and optimized
- [ ] Environment variables configured
- [ ] CORS settings restricted to your domain
- [ ] Rate limiting implemented
- [ ] Database configured (PostgreSQL for production)
- [ ] Log rotation and monitoring set up
- [ ] SSL/TLS certificates configured
- [ ] Emergency contact validation implemented
- [ ] Crisis escalation procedures documented
- [ ] Load testing completed
- [ ] Backup and recovery procedures in place

## 📞 Support and Resources

### Crisis Helplines by Region

- **US**: 988 Suicide & Crisis Lifeline
- **UK**: Samaritans - 116 123
- **International**: https://findahelpline.com

### Technical Support

For technical issues:
1. Check the logs in `mental_health_assistant.log`
2. Review API documentation at `/docs`
3. Test individual components using the provided test scripts

---

**⚠️ Important**: This system is designed to assist and complement professional mental health care, not replace it. Always ensure proper crisis escalation procedures are in place and that users have access to immediate professional help when needed.
