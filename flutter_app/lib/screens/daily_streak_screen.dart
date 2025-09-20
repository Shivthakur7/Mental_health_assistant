import 'package:flutter/material.dart';
import '../services/api_client.dart';

class DailyStreakScreen extends StatefulWidget {
  final MentalHealthApi api;

  const DailyStreakScreen({Key? key, required this.api}) : super(key: key);

  @override
  State<DailyStreakScreen> createState() => _DailyStreakScreenState();
}

class _DailyStreakScreenState extends State<DailyStreakScreen> {
  Map<String, dynamic>? _questions;
  Map<String, dynamic>? _streakInfo;
  List<Map<String, dynamic>> _answers = [];
  bool _isLoading = false;
  bool _isSubmitting = false;
  String? _error;
  int _currentQuestionIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadDailyQuestions();
    _loadStreakInfo();
  }

  Future<void> _loadDailyQuestions() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Call API to get daily questions
      final response = await widget.api.getDailyQuestions();
      setState(() {
        _questions = response;
        _answers = List.generate(
          (response['questions'] as List).length,
          (index) => {},
        );
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _loadStreakInfo() async {
    try {
      final streakInfo = await widget.api.getStreakInfo();
      setState(() {
        _streakInfo = streakInfo;
      });
    } catch (e) {
      // Handle error silently for streak info
    }
  }

  Future<void> _submitAnswers() async {
    if (_answers.any((answer) => answer.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please answer all questions before submitting'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final result = await widget.api.submitDailyCheckin(
        questionsData: _questions!,
        answers: _answers,
      );

      if (mounted) {
        // Show success dialog with results
        _showResultsDialog(result);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  void _showResultsDialog(Map<String, dynamic> result) {
    final wellnessScore = result['wellness_score'] as Map<String, dynamic>? ?? {};
    final streakInfo = result['streak_info'] as Map<String, dynamic>? ?? {};
    final insights = result['insights'] as Map<String, dynamic>? ?? {};
    final needsIntervention = result['needs_intervention'] as bool? ?? false;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              needsIntervention ? Icons.warning : Icons.celebration,
              color: needsIntervention ? Colors.red : Colors.green,
            ),
            const SizedBox(width: 8),
            const Text('Daily Check-in Complete!'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Wellness Score
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getScoreColor(wellnessScore['overall_score'] ?? 0).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Text(
                      'Wellness Score: ${((wellnessScore['overall_score'] ?? 0) as num).toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: _getScoreColor(wellnessScore['overall_score'] ?? 0),
                      ),
                    ),
                    Text(
                      _getWellnessMessage(wellnessScore['wellness_category'] ?? 'unknown'),
                      style: const TextStyle(fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Streak Info
              if (streakInfo.isNotEmpty) ...[
                Text(
                  '🔥 Current Streak: ${streakInfo['current_streak'] ?? 0} days',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                Text(
                  '🏆 Longest Streak: ${streakInfo['longest_streak'] ?? 0} days',
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 12),
              ],

              // Insights
              if (insights.isNotEmpty) ...[
                const Text(
                  'Insights:',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...((insights['recommendations'] as List?) ?? []).map(
                  (rec) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• '),
                        Expanded(child: Text(rec.toString())),
                      ],
                    ),
                  ),
                ),
              ],

              if (needsIntervention) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: const Column(
                    children: [
                      Text(
                        '⚠️ We\'re concerned about your wellbeing',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.red,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Consider reaching out to a mental health professional or trusted friend. You don\'t have to face this alone.',
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // Go back to main screen
            },
            child: const Text('Continue'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Daily Check-in'),
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Daily Check-in'),
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
              const SizedBox(height: 16),
              Text('Error: $_error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadDailyQuestions,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (_questions == null) return const SizedBox.shrink();

    final questions = _questions!['questions'] as List;
    final checkedInToday = _streakInfo?['checked_in_today'] as bool? ?? false;

    if (checkedInToday) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Daily Check-in'),
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.check_circle, size: 80, color: Colors.green.shade400),
              const SizedBox(height: 16),
              const Text(
                'Already checked in today!',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                '🔥 Current streak: ${_streakInfo?['current_streak'] ?? 0} days',
                style: const TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Back to Home'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Check-in'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Progress indicator
          LinearProgressIndicator(
            value: (_currentQuestionIndex + 1) / questions.length,
            backgroundColor: Colors.grey.shade300,
            valueColor: const AlwaysStoppedAnimation<Color>(Colors.teal),
          ),
          
          // Streak info header
          if (_streakInfo != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: Colors.teal.shade50,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.local_fire_department, color: Colors.orange),
                  const SizedBox(width: 8),
                  Text(
                    'Current Streak: ${_streakInfo!['current_streak'] ?? 0} days',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),

          // Question content
          Expanded(
            child: PageView.builder(
              itemCount: questions.length,
              onPageChanged: (index) {
                setState(() {
                  _currentQuestionIndex = index;
                });
              },
              itemBuilder: (context, index) {
                final question = questions[index] as Map<String, dynamic>;
                return _buildQuestionCard(question, index);
              },
            ),
          ),

          // Submit button
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitAnswers,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Complete Check-in',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuestionCard(Map<String, dynamic> question, int index) {
    final questionType = question['type'] as String;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Question ${index + 1} of ${_questions!['questions'].length}',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                question['question'] as String,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 24),
              
              if (questionType == 'scale')
                _buildScaleQuestion(question, index)
              else if (questionType == 'multiple_choice')
                _buildMultipleChoiceQuestion(question, index)
              else if (questionType == 'text')
                _buildTextQuestion(question, index),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScaleQuestion(Map<String, dynamic> question, int index) {
    final minValue = question['scale_min'] as int;
    final maxValue = question['scale_max'] as int;
    final labels = question['scale_labels'] as Map<String, dynamic>? ?? {};
    final currentValue = (_answers[index]['value'] as num?)?.toDouble() ?? minValue.toDouble();

    return Column(
      children: [
        Slider(
          value: currentValue,
          min: minValue.toDouble(),
          max: maxValue.toDouble(),
          divisions: maxValue - minValue,
          label: currentValue.round().toString(),
          onChanged: (value) {
            setState(() {
              _answers[index] = {
                'question_id': question['id'],
                'value': value.round(),
                'category': question['category'],
              };
            });
          },
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(labels[minValue.toString()] ?? minValue.toString()),
            Text('${currentValue.round()}'),
            Text(labels[maxValue.toString()] ?? maxValue.toString()),
          ],
        ),
      ],
    );
  }

  Widget _buildMultipleChoiceQuestion(Map<String, dynamic> question, int index) {
    final options = question['options'] as List;
    final selectedValue = (_answers[index]['value'] as num?)?.toInt();

    return Column(
      children: options.map((option) {
        final optionMap = option as Map<String, dynamic>;
        final value = optionMap['value'] as int;
        final text = optionMap['text'] as String;

        return RadioListTile<int>(
          title: Text(text),
          value: value,
          groupValue: selectedValue,
          onChanged: (newValue) {
            setState(() {
              _answers[index] = {
                'question_id': question['id'],
                'value': newValue,
                'category': question['category'],
              };
            });
          },
        );
      }).toList(),
    );
  }

  Widget _buildTextQuestion(Map<String, dynamic> question, int index) {
    final placeholder = question['placeholder'] as String? ?? '';

    return TextField(
      decoration: InputDecoration(
        hintText: placeholder,
        border: const OutlineInputBorder(),
      ),
      maxLines: 3,
      onChanged: (text) {
        setState(() {
          _answers[index] = {
            'question_id': question['id'],
            'value': text,
            'category': question['category'],
          };
        });
      },
    );
  }

  Color _getScoreColor(num score) {
    final scoreValue = score.toDouble();
    if (scoreValue >= 80) return Colors.green;
    if (scoreValue >= 65) return Colors.lightGreen;
    if (scoreValue >= 50) return Colors.orange;
    if (scoreValue >= 35) return Colors.deepOrange;
    return Colors.red;
  }

  String _getWellnessMessage(String category) {
    switch (category) {
      case 'excellent':
        return 'Excellent! You\'re doing great! 🌟';
      case 'good':
        return 'Good job! Keep up the positive momentum! 👍';
      case 'fair':
        return 'You\'re doing okay. Consider some self-care activities. 💙';
      case 'concerning':
        return 'We\'re here to support you. Consider reaching out for help. 🤗';
      case 'critical':
        return 'Please prioritize your wellbeing and seek professional support. ❤️';
      default:
        return 'Thank you for checking in! 😊';
    }
  }
}
