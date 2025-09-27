import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'dart:convert';
import '../config/app_theme.dart';

class MoodJournalScreen extends StatefulWidget {
  const MoodJournalScreen({super.key});

  @override
  State<MoodJournalScreen> createState() => _MoodJournalScreenState();
}

class _MoodJournalScreenState extends State<MoodJournalScreen>
    with TickerProviderStateMixin {
  final TextEditingController _journalController = TextEditingController();
  List<MoodEntry> _moodEntries = [];
  String _selectedMood = '';
  late AnimationController _fabController;
  late Animation<double> _fabAnimation;

  final List<MoodOption> _moodOptions = [
    MoodOption('😊', 'Happy', Colors.yellow.shade600, 5),
    MoodOption('😌', 'Content', Colors.green.shade500, 4),
    MoodOption('😐', 'Neutral', Colors.grey.shade500, 3),
    MoodOption('😔', 'Sad', Colors.blue.shade500, 2),
    MoodOption('😰', 'Anxious', Colors.orange.shade600, 1),
  ];

  @override
  void initState() {
    super.initState();
    _loadMoodEntries();
    _fabController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fabAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fabController, curve: Curves.easeInOut),
    );
    _fabController.forward();
  }

  @override
  void dispose() {
    _journalController.dispose();
    _fabController.dispose();
    super.dispose();
  }

  Future<void> _loadMoodEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final entriesJson = prefs.getStringList('mood_entries') ?? [];
    setState(() {
      _moodEntries = entriesJson
          .map((json) => MoodEntry.fromJson(jsonDecode(json)))
          .toList();
      _moodEntries.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    });
  }

  Future<void> _saveMoodEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final entriesJson = _moodEntries
        .map((entry) => jsonEncode(entry.toJson()))
        .toList();
    await prefs.setStringList('mood_entries', entriesJson);
  }

  void _addMoodEntry() {
    if (_selectedMood.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Please select a mood first',
            style: GoogleFonts.poppins(),
          ),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    final moodOption = _moodOptions.firstWhere((m) => m.emoji == _selectedMood);
    final entry = MoodEntry(
      mood: _selectedMood,
      moodLabel: moodOption.label,
      moodScore: moodOption.score,
      note: _journalController.text.trim(),
      timestamp: DateTime.now(),
    );

    setState(() {
      _moodEntries.insert(0, entry);
      _selectedMood = '';
      _journalController.clear();
    });

    _saveMoodEntries();
    Navigator.of(context).pop();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Mood entry saved!',
          style: GoogleFonts.poppins(),
        ),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _showAddMoodDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Container(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Handle
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                
                Text(
                  'How are you feeling?',
                  style: GoogleFonts.poppins(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.primaryBlue,
                  ),
                ),
                const SizedBox(height: 20),
                
                // Mood Selection
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: _moodOptions.map((mood) {
                    bool isSelected = _selectedMood == mood.emoji;
                    return GestureDetector(
                      onTap: () {
                        setModalState(() {
                          _selectedMood = mood.emoji;
                        });
                      },
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? mood.color.withOpacity(0.2)
                              : Colors.grey.shade100,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: isSelected ? mood.color : Colors.transparent,
                            width: 2,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              mood.emoji,
                              style: const TextStyle(fontSize: 24),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              mood.label,
                              style: GoogleFonts.poppins(
                                fontWeight: isSelected
                                    ? FontWeight.w600
                                    : FontWeight.w500,
                                color: isSelected ? mood.color : Colors.black87,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),
                
                const SizedBox(height: 24),
                
                // Journal Note
                Text(
                  'Add a note (optional)',
                  style: GoogleFonts.poppins(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _journalController,
                  maxLines: 4,
                  decoration: InputDecoration(
                    hintText: 'What\'s on your mind?',
                    hintStyle: GoogleFonts.poppins(color: Colors.grey.shade500),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey.shade300),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppTheme.primaryBlue),
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Save Button
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _addMoodEntry,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryBlue,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      'Save Entry',
                      style: GoogleFonts.poppins(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
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
                      icon: Icon(
                        Icons.arrow_back,
                        color: AppTheme.primaryBlue,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        'Mood Journal',
                        style: GoogleFonts.poppins(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.primaryBlue,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(width: 48),
                  ],
                ),
              ),
              
              // Mood Entries List
              Expanded(
                child: _moodEntries.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              width: 100,
                              height: 100,
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(50),
                              ),
                              child: Icon(
                                Icons.mood,
                                size: 50,
                                color: Colors.grey.shade400,
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'No mood entries yet',
                              style: GoogleFonts.poppins(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                                color: Colors.grey.shade600,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Start tracking your mood to see patterns',
                              style: GoogleFonts.poppins(
                                color: Colors.grey.shade500,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      )
                    : AnimationLimiter(
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _moodEntries.length,
                          itemBuilder: (context, index) {
                            final entry = _moodEntries[index];
                            return AnimationConfiguration.staggeredList(
                              position: index,
                              duration: const Duration(milliseconds: 375),
                              child: SlideAnimation(
                                verticalOffset: 50.0,
                                child: FadeInAnimation(
                                  child: _buildMoodEntryCard(entry),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: ScaleTransition(
        scale: _fabAnimation,
        child: FloatingActionButton.extended(
          onPressed: _showAddMoodDialog,
          backgroundColor: AppTheme.primaryBlue,
          icon: const Icon(Icons.add, color: Colors.white),
          label: Text(
            'Add Entry',
            style: GoogleFonts.poppins(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMoodEntryCard(MoodEntry entry) {
    final moodOption = _moodOptions.firstWhere(
      (m) => m.emoji == entry.mood,
      orElse: () => _moodOptions[2], // Default to neutral
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: AppDecorations.softCard,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: moodOption.color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(25),
                ),
                child: Center(
                  child: Text(
                    entry.mood,
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      entry.moodLabel,
                      style: GoogleFonts.poppins(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: moodOption.color,
                      ),
                    ),
                    Text(
                      _formatDateTime(entry.timestamp),
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
          if (entry.note.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                entry.note,
                style: GoogleFonts.poppins(
                  fontSize: 14,
                  color: Colors.grey.shade700,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays == 0) {
      return 'Today ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      return 'Yesterday ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }
}

class MoodEntry {
  final String mood;
  final String moodLabel;
  final int moodScore;
  final String note;
  final DateTime timestamp;

  MoodEntry({
    required this.mood,
    required this.moodLabel,
    required this.moodScore,
    required this.note,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'mood': mood,
      'moodLabel': moodLabel,
      'moodScore': moodScore,
      'note': note,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory MoodEntry.fromJson(Map<String, dynamic> json) {
    return MoodEntry(
      mood: json['mood'],
      moodLabel: json['moodLabel'],
      moodScore: json['moodScore'],
      note: json['note'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}

class MoodOption {
  final String emoji;
  final String label;
  final Color color;
  final int score;

  MoodOption(this.emoji, this.label, this.color, this.score);
}
