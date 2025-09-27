import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/api_client.dart';
import 'widgets/crisis_dialog.dart';
import 'widgets/activity_recommendations.dart';
import 'widgets/animated_widgets.dart';
import 'screens/settings_screen.dart';
import 'screens/analytics_screen.dart';
import 'screens/daily_streak_screen.dart';
import 'screens/welcome_screen.dart';
import 'screens/meditation_screen.dart';
import 'screens/mood_journal_screen.dart';
import 'screens/resources_screen.dart';
import 'config/api_config.dart';
import 'config/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MindCare AI',
      theme: AppTheme.lightTheme,
      home: const WelcomeScreen(),
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
  // API client configured from centralized config
  final _api = MentalHealthApi(baseUrl: ApiConfig.baseUrl);
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
      drawer: _buildNavigationDrawer(context),
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildAppBar(context),
              Expanded(
                child: _buildBody(context),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(30),
          bottomRight: Radius.circular(30),
        ),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryBlue.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Row(
        children: [
          Builder(
            builder: (context) => IconButton(
              onPressed: () => Scaffold.of(context).openDrawer(),
              icon: const Icon(Icons.menu, color: Colors.white, size: 28),
            ),
          ),
          Expanded(
            child: Column(
              children: [
                GradientText(
                  text: 'MindCare AI',
                  style: GoogleFonts.poppins(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                  gradient: const LinearGradient(
                    colors: [Colors.white, Colors.white70],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Your Mental Health Companion',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    color: Colors.white70,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.psychology,
              color: Colors.white,
              size: 24,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationDrawer(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      child: Column(
        children: [
          Container(
            decoration: const BoxDecoration(
              gradient: AppTheme.primaryGradient,
            ),
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(40),
                      ),
                      child: const Icon(
                        Icons.psychology,
                        color: Colors.white,
                        size: 40,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'MindCare AI',
                      style: GoogleFonts.poppins(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Mental Health Assistant',
                      style: GoogleFonts.poppins(
                        fontSize: 12,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                _buildDrawerItem(
                  context,
                  Icons.home,
                  'Home',
                  () => Navigator.pop(context),
                ),
                _buildDrawerItem(
                  context,
                  Icons.self_improvement,
                  'Meditation',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const MeditationScreen(),
                      ),
                    );
                  },
                ),
                _buildDrawerItem(
                  context,
                  Icons.book,
                  'Mood Journal',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const MoodJournalScreen(),
                      ),
                    );
                  },
                ),
                _buildDrawerItem(
                  context,
                  Icons.help_outline,
                  'Resources',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ResourcesScreen(),
                      ),
                    );
                  },
                ),
                const Divider(),
                _buildDrawerItem(
                  context,
                  Icons.local_fire_department,
                  'Daily Streak',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => DailyStreakScreen(api: _api),
                      ),
                    );
                  },
                ),
                _buildDrawerItem(
                  context,
                  Icons.analytics,
                  'Analytics',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => AnalyticsScreen(api: _api),
                      ),
                    );
                  },
                ),
                _buildDrawerItem(
                  context,
                  Icons.settings,
                  'Settings',
                  () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const SettingsScreen(),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(
    BuildContext context,
    IconData icon,
    String title,
    VoidCallback onTap,
  ) {
    return ListTile(
      leading: Icon(
        icon,
        color: AppTheme.primaryBlue,
        size: 24,
      ),
      title: Text(
        title,
        style: GoogleFonts.poppins(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: Colors.grey.shade800,
        ),
      ),
      onTap: onTap,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    );
  }

  Widget _buildBody(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: AnimationLimiter(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: AnimationConfiguration.toStaggeredList(
            duration: const Duration(milliseconds: 375),
            childAnimationBuilder: (widget) => SlideAnimation(
              verticalOffset: 50.0,
              child: FadeInAnimation(child: widget),
            ),
            children: [
              if (_checking) 
                Container(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: const LinearProgressIndicator(
                    backgroundColor: Colors.white,
                    valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryBlue),
                  ),
                ),
              if (!_checking && !_backendOk)
                FloatingCard(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.warning_amber_rounded,
                            color: Colors.orange.shade600,
                            size: 24,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Backend Connection',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.orange.shade700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Unable to connect to the backend service. Please ensure the FastAPI server is running.',
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 12),
                      AnimatedGradientButton(
                        text: 'Retry Connection',
                        icon: Icons.refresh,
                        onPressed: _checkHealth,
                        width: double.infinity,
                        height: 40,
                      ),
                    ],
                  ),
                ),
              
              // Quick Actions Section
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                child: Row(
                  children: [
                    Expanded(
                      child: _buildQuickActionCard(
                        context,
                        'Meditation',
                        Icons.self_improvement,
                        AppTheme.softGreen,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const MeditationScreen(),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildQuickActionCard(
                        context,
                        'Mood Journal',
                        Icons.book,
                        AppTheme.warmPink,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const MoodJournalScreen(),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            
              // Text Input Section
              FloatingCard(
                margin: const EdgeInsets.only(bottom: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            gradient: AppTheme.primaryGradient,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(
                            Icons.chat_bubble_outline,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Share Your Feelings',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryBlue,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: TextField(
                        controller: _controller,
                        decoration: InputDecoration(
                          labelText: 'How are you feeling today?',
                          hintText: 'Describe your emotions, thoughts, or experiences...',
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.all(16),
                          labelStyle: GoogleFonts.poppins(
                            color: Colors.grey.shade600,
                          ),
                          hintStyle: GoogleFonts.poppins(
                            color: Colors.grey.shade400,
                          ),
                        ),
                        style: GoogleFonts.poppins(),
                        maxLines: 4,
                      ),
                    ),
                  ],
                ),
              ),
            
              // Multi-modal Input Section
              FloatingCard(
                margin: const EdgeInsets.only(bottom: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [AppTheme.warmPink, AppTheme.calmTeal],
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(
                            Icons.photo_camera,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Multi-modal Input',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryBlue,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.lightBlue,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'Optional',
                            style: GoogleFonts.poppins(
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.primaryBlue,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    
                    // Image Input
                    Row(
                      children: [
                        Expanded(
                          child: Container(
                            height: 48,
                            decoration: BoxDecoration(
                              border: Border.all(color: AppTheme.primaryBlue.withOpacity(0.3)),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(12),
                                onTap: _pickImage,
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.camera_alt,
                                      color: AppTheme.primaryBlue,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Camera',
                                      style: GoogleFonts.poppins(
                                        color: AppTheme.primaryBlue,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Container(
                            height: 48,
                            decoration: BoxDecoration(
                              border: Border.all(color: AppTheme.primaryBlue.withOpacity(0.3)),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(12),
                                onTap: _pickImageFromGallery,
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.photo_library,
                                      color: AppTheme.primaryBlue,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Gallery',
                                      style: GoogleFonts.poppins(
                                        color: AppTheme.primaryBlue,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    if (_selectedImage != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        height: 120,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.file(
                            _selectedImage!,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    ],
                    
                    const SizedBox(height: 16),
                    
                    // Audio Input
                    Container(
                      width: double.infinity,
                      height: 48,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [AppTheme.softGreen, AppTheme.calmTeal],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(12),
                          onTap: _pickAudioFile,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.audiotrack,
                                color: Colors.white,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Select Audio File',
                                style: GoogleFonts.poppins(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    
                    if (_recordedAudio != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.softGreen.withOpacity(0.1),
                          border: Border.all(color: AppTheme.softGreen.withOpacity(0.3)),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.audiotrack,
                              color: AppTheme.softGreen,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Audio file selected successfully',
                              style: GoogleFonts.poppins(
                                color: AppTheme.softGreen,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    
                    if (_selectedImage != null || _recordedAudio != null) ...[
                      const SizedBox(height: 12),
                      TextButton.icon(
                        onPressed: _clearInputs,
                        icon: Icon(
                          Icons.clear,
                          color: Colors.grey.shade600,
                        ),
                        label: Text(
                          'Clear All Inputs',
                          style: GoogleFonts.poppins(
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            
              // Analyze Button
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                child: AnimatedGradientButton(
                  text: _loading ? 'Analyzing...' : 'Analyze My Mood',
                  icon: _loading ? null : Icons.psychology,
                  isLoading: _loading,
                  onPressed: (!_backendOk || _loading) ? null : _analyze,
                  width: double.infinity,
                  height: 56,
                ),
              ),
            
              // Error Display
              if (_error != null)
                FloatingCard(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.error_outline,
                            color: Colors.red.shade600,
                            size: 24,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Error',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.red.shade700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _error!,
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.red.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
            
              // Results Display
              if (_mood.isNotEmpty) ...[
                FloatingCard(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 50,
                            height: 50,
                            decoration: AppDecorations.moodCard,
                            child: const Icon(
                              Icons.psychology,
                              color: Colors.white,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Analysis Result',
                                  style: GoogleFonts.poppins(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.primaryBlue,
                                  ),
                                ),
                                Text(
                                  'Your mood analysis is ready',
                                  style: GoogleFonts.poppins(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          gradient: AppTheme.moodGradient,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Mood: $_mood',
                              style: GoogleFonts.poppins(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.white,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '💡 $_tip',
                              style: GoogleFonts.poppins(
                                fontSize: 14,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      // Multi-modal details
                      if (_multimodalResult != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '📊 Detailed Analysis',
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: AppTheme.primaryBlue,
                                ),
                              ),
                              const SizedBox(height: 12),
                              _buildMultimodalDetails(),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                
                // Activity Recommendations
                ActivityRecommendationsWidget(activities: _recommendedActivities),
              ],
            ],
          ),
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
          Text(
            'Confidence: ${((multimodalAnalysis['final_confidence'] ?? multimodalAnalysis['overall_confidence'] ?? 0.0) * 100).toStringAsFixed(1)}%',
            style: GoogleFonts.poppins(fontSize: 14, color: Colors.grey.shade700),
          ),
          Text(
            'Primary modality: ${multimodalAnalysis['primary_modality'] ?? 'text'}',
            style: GoogleFonts.poppins(fontSize: 14, color: Colors.grey.shade700),
          ),
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
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.lightBlue,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '💬 ${_multimodalResult!['recommendation']}',
              style: GoogleFonts.poppins(
                fontSize: 14,
                fontStyle: FontStyle.italic,
                color: AppTheme.primaryBlue,
              ),
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
        style: GoogleFonts.poppins(fontSize: 12),
      ),
    );
  }

  Widget _buildQuickActionCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 100,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              color.withOpacity(0.8),
              color,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.3),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: Colors.white,
                size: 32,
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: GoogleFonts.poppins(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
