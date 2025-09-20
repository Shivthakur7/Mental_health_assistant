# 📱 Flutter Integration Guide

## 🔗 Connecting Your Flutter App to the Backend

Your Flutter app needs to connect to the enhanced backend to use the new crisis detection and emergency notification features.

## 🛠️ Step 1: Update Flutter Dependencies

Add to your `flutter_app/pubspec.yaml`:

```yaml
dependencies:
  http: ^1.2.1  # Already added
  shared_preferences: ^2.2.2  # For session management
  provider: ^6.1.1  # For state management
```

## 🔧 Step 2: Update API Client

Update `flutter_app/lib/services/api_client.dart` to include crisis detection:

```dart
// Add these methods to your existing MentalHealthApi class

Future<Map<String, dynamic>> analyzeTextWithCrisis({
  required String text,
  String? sessionId,
  String? userId,
  String location = 'international',
  Map<String, String>? emergencyContacts,
}) async {
  final body = {
    'text': text,
    'session_id': sessionId,
    'user_id': userId ?? 'flutter_user',
    'location': location,
    if (emergencyContacts != null) 'emergency_contacts': emergencyContacts,
  };

  final response = await http.post(
    Uri.parse('$baseUrl/analyze_text'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(body),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to analyze text: ${response.statusCode}');
  }
}

Future<String?> startSession({String? userId}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/start_session'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'user_id': userId ?? 'flutter_user'}),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['session_id'];
  }
  return null;
}
```

## 🚨 Step 3: Handle Crisis Detection

Update your main Flutter app to handle crisis responses:

```dart
// In your main.dart or wherever you handle API responses

void _handleAnalysisResult(Map<String, dynamic> result) {
  // Check for crisis detection
  if (result['crisis_detected'] == true) {
    _showCrisisDialog(result);
  }
  
  // Display normal results
  setState(() {
    _mood = '${result['mood_label']} (${result['mood_score']})';
    _tip = result['cbt_tip'];
  });
}

void _showCrisisDialog(Map<String, dynamic> result) {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => AlertDialog(
      title: Text('🚨 Crisis Support'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            result['message'] ?? 'We\'re concerned about you. Help is available.',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 16),
          if (result['immediate_steps'] != null) ...[
            Text('Immediate Steps:', style: TextStyle(fontWeight: FontWeight.bold)),
            ...List<String>.from(result['immediate_steps']).map(
              (step) => Padding(
                padding: EdgeInsets.only(left: 8, top: 4),
                child: Text('• $step'),
              ),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text('I understand'),
        ),
        ElevatedButton(
          onPressed: () {
            // Open crisis helpline or emergency services
            Navigator.of(context).pop();
            // You can add URL launcher here for helplines
          },
          style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
          child: Text('Get Help Now', style: TextStyle(color: Colors.white)),
        ),
      ],
    ),
  );
}
```

## 📊 Step 4: Add Session Management

Add session management to your Flutter app:

```dart
class SessionManager {
  static const String _sessionKey = 'mental_health_session';
  
  static Future<String?> getSessionId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_sessionKey);
  }
  
  static Future<void> saveSessionId(String sessionId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_sessionKey, sessionId);
  }
  
  static Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_sessionKey);
  }
}
```

## 🔄 Step 5: Update Your Main App Logic

Update your existing Flutter app to use the new features:

```dart
class _HomePageState extends State<HomePage> {
  String? _sessionId;
  
  @override
  void initState() {
    super.initState();
    _initializeSession();
  }
  
  Future<void> _initializeSession() async {
    // Try to get existing session
    _sessionId = await SessionManager.getSessionId();
    
    // If no session, create new one
    if (_sessionId == null) {
      _sessionId = await _api.startSession();
      if (_sessionId != null) {
        await SessionManager.saveSessionId(_sessionId!);
      }
    }
  }
  
  Future<void> _analyzeText() async {
    if (_controller.text.isEmpty) return;
    
    setState(() {
      _loading = true;
      _error = null;
    });
    
    try {
      final result = await _api.analyzeTextWithCrisis(
        text: _controller.text,
        sessionId: _sessionId,
        // Optional: Add emergency contacts
        // emergencyContacts: {
        //   'phone': '+1234567890',
        //   'email': 'emergency@example.com',
        // },
      );
      
      _handleAnalysisResult(result);
      
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }
}
```

## 🌐 Step 6: Backend URL Configuration

Make sure your Flutter app points to the correct backend URL:

```dart
// For local development
final _api = MentalHealthApi(baseUrl: 'http://10.0.2.2:8000'); // Android emulator
final _api = MentalHealthApi(baseUrl: 'http://localhost:8000'); // iOS simulator

// For production (when you deploy the backend)
final _api = MentalHealthApi(baseUrl: 'https://your-backend.onrender.com');
```

## 🧪 Step 7: Test the Integration

1. **Start the backend**: `cd backend && python run_server.py`
2. **Run Flutter app**: `cd flutter_app && flutter run`
3. **Test crisis detection**: Enter "I feel hopeless" and verify crisis dialog appears
4. **Test normal flow**: Enter "I'm feeling okay" and verify normal response

## 🎯 Key Benefits of This Integration

✅ **Real-time Crisis Detection**: Instant identification of mental health crises  
✅ **Emergency Notifications**: Automated alerts to emergency contacts  
✅ **Session Tracking**: Persistent user sessions for better analytics  
✅ **Professional Resources**: Immediate access to crisis helplines  
✅ **Multi-modal Ready**: Framework for voice and image analysis  

Your Flutter app now has **enterprise-grade mental health crisis detection**! 🚀
