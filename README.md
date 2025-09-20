# 🧠 Mental Health AI Assistant

A comprehensive mental health support application with AI-powered crisis detection, multi-modal analysis, and emergency notification systems.

## 📁 Project Structure

```
Mental_health_assistant/
├── 📱 flutter_app/              # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart           # Main Flutter app
│   │   └── services/           # API integration services
│   ├── android/                # Android platform files
│   ├── ios/                    # iOS platform files
│   └── pubspec.yaml           # Flutter dependencies
│
├── 🔧 backend/                  # Python AI backend
│   ├── api/                    # FastAPI endpoints
│   │   └── main.py            # Main API server
│   ├── models/                 # AI models and inference
│   │   ├── model.py           # Sentiment analysis (ONNX)
│   │   ├── voice_emotion.py   # Voice emotion detection
│   │   ├── face_emotion.py    # Facial emotion analysis
│   │   └── multimodal_fusion.py # Multi-modal AI fusion
│   ├── services/              # Business logic services
│   │   ├── crisis_detection.py    # Crisis detection engine
│   │   ├── emergency_notifications.py # SMS/Email alerts
│   │   └── monitoring.py      # Analytics and logging
│   ├── utils/                 # Utility functions
│   │   ├── cbt_tips.py       # CBT therapy tips
│   │   ├── export_onnx.py    # Model export utilities
│   │   └── quantize_onnx.py  # Model optimization
│   ├── onnx_model/           # Optimized AI models
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Environment configuration
│
└── 📚 docs/                    # Documentation
    ├── README_STAGE4.md       # Stage 4 implementation details
    ├── NEXT_STEPS.md         # Deployment and next steps
    └── DEPLOYMENT_GUIDE.md   # Complete deployment guide
```

## 🚀 Features

### 🧠 AI-Powered Analysis
- **Sentiment Analysis**: ONNX-optimized transformer models
- **Voice Emotion Detection**: Real-time audio emotion analysis
- **Facial Expression Analysis**: Computer vision emotion detection
- **Multi-modal Fusion**: Combined analysis for higher accuracy

### 🚨 Crisis Detection & Safety
- **Advanced Crisis Detection**: 40+ crisis keywords with severity levels
- **Multi-level Assessment**: Critical, High, Moderate, None
- **Emergency Notifications**: Automated SMS and email alerts
- **Crisis Resources**: Localized helplines and immediate support

### 📊 Production Features
- **Real-time Analytics**: Usage statistics and crisis metrics
- **Session Management**: User tracking and interaction logging
- **Performance Monitoring**: System health and response times
- **Database Integration**: SQLite with comprehensive logging

### 📱 Mobile Integration
- **Flutter Frontend**: Cross-platform mobile application
- **Multi-modal Input**: Text, voice, and image analysis
- **Real-time Processing**: Instant crisis detection and response
- **Offline Capabilities**: Local model inference support

## 🛠️ Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Flutter App Setup
```bash
cd flutter_app
flutter pub get
flutter run
```

### Environment Configuration
```bash
cd backend
cp .env.example .env
# Edit .env with your Twilio and email credentials
```

## 🔗 API Endpoints

- `POST /analyze_text` - Text sentiment analysis with crisis detection
- `POST /analyze_multimodal` - Multi-modal analysis (text, voice, image)
- `GET /system_status` - System health and configuration
- `GET /analytics` - Usage analytics and statistics
- `POST /start_session` - Initialize user session
- `GET /health` - Basic health check

## 🎯 Use Cases

### For Users
- **Daily Mood Tracking**: Monitor emotional wellbeing
- **Crisis Support**: Immediate help during mental health crises
- **CBT Guidance**: Cognitive Behavioral Therapy tips and exercises
- **Multi-modal Input**: Express feelings through text, voice, or images

### For Healthcare Providers
- **Patient Monitoring**: Track patient emotional states
- **Crisis Intervention**: Automated alerts for high-risk situations
- **Analytics Dashboard**: Usage patterns and intervention effectiveness
- **Integration Ready**: API for existing healthcare systems

### For Researchers
- **Data Collection**: Anonymized mental health interaction data
- **Model Training**: Continuous improvement of AI models
- **Intervention Studies**: A/B testing of different support strategies

## 🔒 Privacy & Security

- **Local Processing**: AI models run locally, no external API calls
- **Encrypted Communications**: Secure data transmission
- **Anonymized Analytics**: Privacy-preserving usage statistics
- **GDPR Compliant**: Data protection and user rights

## 🚀 Deployment Options

### Mobile App Deployment
- **Android**: Google Play Store ready
- **iOS**: App Store ready
- **Cross-platform**: Single codebase for both platforms

### Backend Deployment
- **Cloud Platforms**: Render, Railway, Google Cloud
- **Containerized**: Docker support for easy deployment
- **Scalable**: Horizontal scaling support

## 📈 Technical Highlights

### AI/ML Engineering
- **ONNX Optimization**: 3x faster inference than PyTorch
- **Quantization**: Reduced model size for mobile deployment
- **Multi-modal AI**: Advanced fusion algorithms
- **Real-time Processing**: Sub-second response times

### Software Engineering
- **Clean Architecture**: Modular, maintainable codebase
- **Comprehensive Testing**: Unit tests and integration tests
- **Production Logging**: Structured logging and monitoring
- **API Documentation**: Auto-generated OpenAPI specs

### Mobile Development
- **Flutter Framework**: Modern, reactive UI
- **State Management**: Efficient app state handling
- **Platform Integration**: Native iOS and Android features
- **Offline Support**: Local data storage and sync

## 🤝 Contributing

This project demonstrates enterprise-level software development practices:
- Clean code architecture
- Comprehensive documentation
- Production-ready deployment
- Real-world impact focus

## 📞 Crisis Resources

**Emergency**: If you or someone you know is in immediate danger, contact emergency services (911, 999, 112) immediately.

**Crisis Helplines**:
- US: 988 Suicide & Crisis Lifeline
- UK: Samaritans (116 123)
- International: https://findahelpline.com

---

**⚠️ Important**: This system supplements professional mental health care and should not replace emergency services or professional therapy.
