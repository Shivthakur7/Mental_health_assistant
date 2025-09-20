import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'services/api_client.dart';
import 'widgets/crisis_dialog.dart';
import 'widgets/activity_recommendations.dart';
import 'screens/settings_screen.dart';
import 'screens/analytics_screen.dart';
import 'screens/daily_streak_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _controller = TextEditingController();
  // If backend runs on laptop and you're using Android emulator, use 10.0.2.2:8000
  // For embedded Python on-device, use 127.0.0.1:8000
  final _api = MentalHealthApi(baseUrl: 'http://127.0.0.1:8000');
  final _imagePicker = ImagePicker();
  bool _checking = true;
  bool _backendOk = false;
  bool _loading = false;
  String _mood = '';
  String _tip = '';
  String? _error;
  
  // Multi-modal inputs
  File? _selectedImage;
  File? _recordedAudio;
  Map<String, dynamic>? _multimodalResult;
  
  // Activity recommendations
  Map<String, dynamic>? _recommendedActivities;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // Start session
    await _startSession();
    // Check backend health
    await _checkHealth();
  }

  Future<void> _startSession() async {
    try {
      final sessionId = await _api.startSession();
      if (sessionId != null) {
        // Save session for persistence
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('session_id', sessionId);
      }
    } catch (e) {
      print('Failed to start session: $e');
    }
  }

  Future<void> _checkHealth() async {
    setState(() {
      _checking = true;
      _error = null;
    });
    try {
      final ok = await _api.health();
      setState(() {
        _backendOk = ok;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _checking = false;
      });
    }
  }

  Future<void> _analyze() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    
    setState(() {
      _loading = true;
      _error = null;
      _mood = '';
      _tip = '';
      _multimodalResult = null;
      _recommendedActivities = null;
    });
    
    try {
      Map<String, dynamic> res;
      
      // Get emergency contacts from settings
      final prefs = await SharedPreferences.getInstance();
      final emergencyContactsEnabled = prefs.getBool('emergency_contacts_enabled') ?? false;
      Map<String, String>? emergencyContacts;
      
      if (emergencyContactsEnabled) {
        final phone = prefs.getString('emergency_phone');
        final email = prefs.getString('emergency_email');
        if (phone?.isNotEmpty == true || email?.isNotEmpty == true) {
          emergencyContacts = {};
          if (phone?.isNotEmpty == true) emergencyContacts['phone'] = phone!;
          if (email?.isNotEmpty == true) emergencyContacts['email'] = email!;
        }
      }

      // Use multimodal analysis if we have additional inputs
      if (_selectedImage != null || _recordedAudio != null) {
        res = await _api.analyzeMultimodal(
          text: text,
          imageFile: _selectedImage,
          audioFile: _recordedAudio,
          emergencyContacts: emergencyContacts,
          userName: prefs.getString('user_name') ?? 'User',
        );
        setState(() {
          _multimodalResult = res;
          final multimodalAnalysis = res['multimodal_analysis'] as Map<String, dynamic>?;
          if (multimodalAnalysis != null) {
            final score = (multimodalAnalysis['final_mood_score'] as num?)?.toDouble() ?? 0.0;
            final label = multimodalAnalysis['mood_label'] as String? ?? '';
            _mood = '$label (${score.toStringAsFixed(3)})';
          }
          _tip = res['cbt_tip'] as String? ?? '';
          _recommendedActivities = res['recommended_activities'] as Map<String, dynamic>?;
        });
      } else {
        // Text-only analysis with crisis detection
        res = await _api.analyzeText(
          text,
          emergencyContacts: emergencyContacts,
        );
        setState(() {
          final score = (res['mood_score'] as num?)?.toDouble() ?? 0.0;
          final label = res['mood_label'] as String? ?? '';
          _mood = '$label (${score.toStringAsFixed(2)})';
          _tip = res['cbt_tip'] as String? ?? '';
          _recommendedActivities = res['recommended_activities'] as Map<String, dynamic>?;
        });
      }
      
      // Check for crisis detection
      final crisisDetected = res['crisis_detected'] as bool? ?? false;
      if (crisisDetected) {
        _showCrisisDialog(res);
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  void _showCrisisDialog(Map<String, dynamic> analysisResult) {
    showDialog(
      context: context,
      barrierDismissible: false, // Prevent dismissing by tapping outside
      builder: (context) => CrisisDialog(analysisResult: analysisResult),
    );
  }

  Future<void> _pickImage() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        maxWidth: 800,
        maxHeight: 600,
        imageQuality: 80,
      );
      
      if (image != null) {
        setState(() {
          _selectedImage = File(image.path);
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Failed to capture image: $e';
      });
    }
  }

  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 800,
        maxHeight: 600,
        imageQuality: 80,
      );
      
      if (image != null) {
        setState(() {
          _selectedImage = File(image.path);
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Failed to pick image: $e';
      });
    }
  }

  Future<void> _pickAudioFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );

      if (result != null && result.files.single.path != null) {
        setState(() {
          _recordedAudio = File(result.files.single.path!);
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Failed to pick audio file: $e';
      });
    }
  }

  void _clearInputs() {
    setState(() {
      _selectedImage = null;
      _recordedAudio = null;
      _multimodalResult = null;
      _mood = '';
      _tip = '';
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mental Health AI'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => DailyStreakScreen(api: _api),
                ),
              );
            },
            icon: const Icon(Icons.local_fire_department),
            tooltip: 'Daily Streak',
          ),
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => AnalyticsScreen(api: _api),
                ),
              );
            },
            icon: const Icon(Icons.analytics),
            tooltip: 'Analytics',
          ),
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );
            },
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_checking) const LinearProgressIndicator(),
            if (!_checking && !_backendOk)
              Card(
                color: Colors.amber.shade100,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Backend not reachable'),
                      const SizedBox(height: 8),
                      const Text('Ensure FastAPI is running and URL is correct.'),
                      const SizedBox(height: 8),
                      ElevatedButton(
                        onPressed: _checkHealth,
                        child: const Text('Retry health check'),
                      ),
                    ],
                  ),
                ),
              ),
            
            // Text Input Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('📝 Text Input', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        labelText: 'How are you feeling today?',
                        border: OutlineInputBorder(),
                        hintText: 'Describe your emotions, thoughts, or experiences...',
                      ),
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Multi-modal Input Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('🎭 Multi-modal Input (Optional)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    
                    // Image Input
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _pickImage,
                            icon: const Icon(Icons.camera_alt),
                            label: const Text('Take Photo'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _pickImageFromGallery,
                            icon: const Icon(Icons.photo_library),
                            label: const Text('Gallery'),
                          ),
                        ),
                      ],
                    ),
                    
                    if (_selectedImage != null) ...[
                      const SizedBox(height: 8),
                      Container(
                        height: 100,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            _selectedImage!,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    ],
                    
                    const SizedBox(height: 12),
                    
                    // Audio Input
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _pickAudioFile,
                            icon: const Icon(Icons.audiotrack),
                            label: const Text('Select Audio File'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    if (_recordedAudio != null) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          border: Border.all(color: Colors.green),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.audiotrack, color: Colors.green),
                            SizedBox(width: 8),
                            Text('Audio file selected successfully'),
                          ],
                        ),
                      ),
                    ],
                    
                    if (_selectedImage != null || _recordedAudio != null) ...[
                      const SizedBox(height: 12),
                      TextButton.icon(
                        onPressed: _clearInputs,
                        icon: const Icon(Icons.clear),
                        label: const Text('Clear All Inputs'),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Analyze Button
            ElevatedButton.icon(
              onPressed: (!_backendOk || _loading) ? null : _analyze,
              icon: _loading 
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.psychology),
              label: Text(_loading ? 'Analyzing...' : 'Analyze Mood'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Error Display
            if (_error != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              ),
            
            // Results Display
            if (_mood.isNotEmpty) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '🎯 Analysis Result',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Mood: $_mood',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      Text('💡 Tip: $_tip'),
                      
                      // Multi-modal details
                      if (_multimodalResult != null) ...[
                        const SizedBox(height: 16),
                        const Divider(),
                        const Text(
                          '📊 Detailed Analysis',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        _buildMultimodalDetails(),
                      ],
                    ],
                  ),
                ),
              ),
              
              // Activity Recommendations
              ActivityRecommendationsWidget(activities: _recommendedActivities),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMultimodalDetails() {
    if (_multimodalResult == null) return const SizedBox.shrink();
    
    final multimodalAnalysis = _multimodalResult!['multimodal_analysis'] as Map<String, dynamic>?;
    final individualResults = _multimodalResult!['individual_results'] as Map<String, dynamic>?;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (multimodalAnalysis != null) ...[
          Text('Confidence: ${((multimodalAnalysis['final_confidence'] ?? multimodalAnalysis['overall_confidence'] ?? 0.0) * 100).toStringAsFixed(1)}%'),
          Text('Primary modality: ${multimodalAnalysis['primary_modality'] ?? 'text'}'),
          const SizedBox(height: 8),
        ],
        
        if (individualResults != null) ...[
          if (individualResults['text'] != null)
            _buildModalityResult('📝 Text', individualResults['text']),
          if (individualResults['voice'] != null)
            _buildModalityResult('🎤 Voice', individualResults['voice']),
          if (individualResults['face'] != null)
            _buildModalityResult('😊 Face', individualResults['face']),
        ],
        
        if (_multimodalResult!['recommendation'] != null) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '💬 ${_multimodalResult!['recommendation']}',
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildModalityResult(String title, Map<String, dynamic> data) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Text(
        '$title: ${data['emotion'] ?? data['score']?.toStringAsFixed(2) ?? 'N/A'} '
        '(${((data['confidence'] ?? 0) * 100).toStringAsFixed(1)}%)',
        style: const TextStyle(fontSize: 12),
      ),
    );
  }
}
