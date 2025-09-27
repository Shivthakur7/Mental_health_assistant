import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:async';
import '../config/app_theme.dart';

class MeditationScreen extends StatefulWidget {
  const MeditationScreen({super.key});

  @override
  State<MeditationScreen> createState() => _MeditationScreenState();
}

class _MeditationScreenState extends State<MeditationScreen>
    with TickerProviderStateMixin {
  late AnimationController _breathingController;
  late AnimationController _rippleController;
  late Animation<double> _breathingAnimation;
  late Animation<double> _rippleAnimation;
  
  Timer? _sessionTimer;
  Timer? _breathingTimer;
  
  int _sessionDuration = 300; // 5 minutes default
  int _remainingTime = 300;
  bool _isActive = false;
  bool _isPaused = false;
  
  String _currentPhase = 'Breathe In';
  int _breathCount = 0;
  
  final List<int> _durations = [180, 300, 600, 900]; // 3, 5, 10, 15 minutes
  final List<String> _durationLabels = ['3 min', '5 min', '10 min', '15 min'];

  @override
  void initState() {
    super.initState();
    _breathingController = AnimationController(
      duration: const Duration(seconds: 8), // 4 seconds in, 4 seconds out
      vsync: this,
    );
    
    _rippleController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _breathingAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _breathingController,
      curve: Curves.easeInOut,
    ));
    
    _rippleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _rippleController,
      curve: Curves.easeOut,
    ));

    _breathingController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() {
          _currentPhase = 'Breathe Out';
          _breathCount++;
        });
        _breathingController.reverse();
      } else if (status == AnimationStatus.dismissed) {
        setState(() {
          _currentPhase = 'Breathe In';
        });
        _breathingController.forward();
      }
    });
  }

  @override
  void dispose() {
    _breathingController.dispose();
    _rippleController.dispose();
    _sessionTimer?.cancel();
    _breathingTimer?.cancel();
    super.dispose();
  }

  void _startSession() {
    setState(() {
      _isActive = true;
      _isPaused = false;
      _remainingTime = _sessionDuration;
      _breathCount = 0;
    });
    
    _breathingController.forward();
    _rippleController.repeat();
    
    _sessionTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        if (_remainingTime > 0) {
          _remainingTime--;
        } else {
          _stopSession();
        }
      });
    });
  }

  void _pauseSession() {
    setState(() {
      _isPaused = !_isPaused;
    });
    
    if (_isPaused) {
      _breathingController.stop();
      _rippleController.stop();
      _sessionTimer?.cancel();
    } else {
      _breathingController.forward();
      _rippleController.repeat();
      _sessionTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          if (_remainingTime > 0) {
            _remainingTime--;
          } else {
            _stopSession();
          }
        });
      });
    }
  }

  void _stopSession() {
    setState(() {
      _isActive = false;
      _isPaused = false;
      _remainingTime = _sessionDuration;
      _currentPhase = 'Breathe In';
    });
    
    _breathingController.reset();
    _rippleController.reset();
    _sessionTimer?.cancel();
    _breathingTimer?.cancel();
    
    // Show completion dialog
    _showCompletionDialog();
  }

  void _showCompletionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(
          '🎉 Session Complete!',
          style: GoogleFonts.poppins(fontWeight: FontWeight.bold),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Great job! You completed a ${_sessionDuration ~/ 60}-minute meditation session.',
              style: GoogleFonts.poppins(),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Breaths taken: $_breathCount',
              style: GoogleFonts.poppins(
                fontWeight: FontWeight.w600,
                color: AppTheme.primaryBlue,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Continue',
              style: GoogleFonts.poppins(color: AppTheme.primaryBlue),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(int seconds) {
    int minutes = seconds ~/ 60;
    int remainingSeconds = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF667eea),
              Color(0xFF764ba2),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // App Bar
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                    ),
                    Expanded(
                      child: Text(
                        'Mindful Breathing',
                        style: GoogleFonts.poppins(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(width: 48), // Balance the back button
                  ],
                ),
              ),
              
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      // Timer Display
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          _formatTime(_remainingTime),
                          style: GoogleFonts.poppins(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Breathing Circle
                      Expanded(
                        child: Center(
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              // Ripple Effect
                              AnimatedBuilder(
                                animation: _rippleAnimation,
                                builder: (context, child) {
                                  return Container(
                                    width: 300 * _rippleAnimation.value,
                                    height: 300 * _rippleAnimation.value,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: Colors.white.withOpacity(
                                          0.3 * (1 - _rippleAnimation.value),
                                        ),
                                        width: 2,
                                      ),
                                    ),
                                  );
                                },
                              ),
                              
                              // Main Breathing Circle
                              AnimatedBuilder(
                                animation: _breathingAnimation,
                                builder: (context, child) {
                                  return Container(
                                    width: 200 * _breathingAnimation.value,
                                    height: 200 * _breathingAnimation.value,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      gradient: RadialGradient(
                                        colors: [
                                          Colors.white.withOpacity(0.3),
                                          Colors.white.withOpacity(0.1),
                                        ],
                                      ),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.white.withOpacity(0.2),
                                          blurRadius: 20,
                                          spreadRadius: 5,
                                        ),
                                      ],
                                    ),
                                    child: Center(
                                      child: Text(
                                        _currentPhase,
                                        style: GoogleFonts.poppins(
                                          fontSize: 18,
                                          fontWeight: FontWeight.w600,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      // Breath Counter
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.air,
                              color: Colors.white,
                              size: 24,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Breaths: $_breathCount',
                              style: GoogleFonts.poppins(
                                fontSize: 16,
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Duration Selection (when not active)
                      if (!_isActive) ...[
                        Text(
                          'Choose Duration',
                          style: GoogleFonts.poppins(
                            fontSize: 16,
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: List.generate(_durations.length, (index) {
                            bool isSelected = _sessionDuration == _durations[index];
                            return GestureDetector(
                              onTap: () {
                                setState(() {
                                  _sessionDuration = _durations[index];
                                  _remainingTime = _sessionDuration;
                                });
                              },
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 8,
                                ),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? Colors.white
                                      : Colors.white.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  _durationLabels[index],
                                  style: GoogleFonts.poppins(
                                    color: isSelected
                                        ? const Color(0xFF667eea)
                                        : Colors.white,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            );
                          }),
                        ),
                        const SizedBox(height: 32),
                      ],
                      
                      // Control Buttons
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          if (_isActive) ...[
                            // Pause/Resume Button
                            FloatingActionButton(
                              onPressed: _pauseSession,
                              backgroundColor: Colors.white,
                              child: Icon(
                                _isPaused ? Icons.play_arrow : Icons.pause,
                                color: const Color(0xFF667eea),
                                size: 32,
                              ),
                            ),
                            
                            // Stop Button
                            FloatingActionButton(
                              onPressed: _stopSession,
                              backgroundColor: Colors.red.withOpacity(0.8),
                              child: const Icon(
                                Icons.stop,
                                color: Colors.white,
                                size: 32,
                              ),
                            ),
                          ] else ...[
                            // Start Button
                            FloatingActionButton.extended(
                              onPressed: _startSession,
                              backgroundColor: Colors.white,
                              icon: const Icon(
                                Icons.play_arrow,
                                color: Color(0xFF667eea),
                              ),
                              label: Text(
                                'Start Session',
                                style: GoogleFonts.poppins(
                                  color: const Color(0xFF667eea),
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
