import 'package:flutter/material.dart';

class ActivityRecommendationsWidget extends StatelessWidget {
  final Map<String, dynamic>? activities;

  const ActivityRecommendationsWidget({
    Key? key,
    this.activities,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (activities == null || activities!['activities'] == null) {
      return const SizedBox.shrink();
    }

    final activityList = List<Map<String, dynamic>>.from(activities!['activities']);
    final explanation = activities!['explanation'] as String? ?? '';
    final moodCategory = activities!['mood_category'] as String? ?? '';

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  _getCategoryIcon(moodCategory),
                  color: _getCategoryColor(moodCategory),
                  size: 24,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Recommended Activities',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _getCategoryColor(moodCategory),
                    ),
                  ),
                ),
              ],
            ),
            
            if (explanation.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                explanation,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
            
            const SizedBox(height: 16),
            
            // Activities List
            ...activityList.map((activity) => _buildActivityTile(activity)).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityTile(Map<String, dynamic> activity) {
    final title = activity['title'] as String? ?? '';
    final description = activity['description'] as String? ?? '';
    final duration = activity['duration'] as String? ?? '';
    final icon = activity['icon'] as String? ?? '💡';
    final type = activity['type'] as String? ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title with icon
          Row(
            children: [
              Text(
                icon,
                style: const TextStyle(fontSize: 20),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (duration.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    duration,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue.shade700,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
            ],
          ),
          
          if (description.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              description,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade700,
                height: 1.3,
              ),
            ),
          ],
          
          if (type.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                type.toUpperCase(),
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'crisis':
        return Icons.emergency;
      case 'moderate_negative':
        return Icons.healing;
      case 'neutral':
        return Icons.self_improvement;
      case 'positive':
        return Icons.celebration;
      default:
        return Icons.lightbulb;
    }
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'crisis':
        return Colors.red.shade700;
      case 'moderate_negative':
        return Colors.orange.shade700;
      case 'neutral':
        return Colors.blue.shade700;
      case 'positive':
        return Colors.green.shade700;
      default:
        return Colors.grey.shade700;
    }
  }
}

class DailyActivityWidget extends StatefulWidget {
  final VoidCallback? onRefresh;

  const DailyActivityWidget({
    Key? key,
    this.onRefresh,
  }) : super(key: key);

  @override
  State<DailyActivityWidget> createState() => _DailyActivityWidgetState();
}

class _DailyActivityWidgetState extends State<DailyActivityWidget> {
  Map<String, dynamic>? _dailyActivity;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadDailyActivity();
  }

  Future<void> _loadDailyActivity() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // You can implement API call here to get daily activity
      // For now, showing a placeholder
      await Future.delayed(const Duration(milliseconds: 500));
      
      setState(() {
        _dailyActivity = {
          "daily_activity": {
            "title": "Take 5 Deep Breaths",
            "description": "Breathe in slowly for 4 counts, hold for 4, then breathe out for 6 counts. This helps activate your parasympathetic nervous system.",
            "duration": "2-3 minutes",
            "type": "breathing",
            "icon": "🫁"
          },
          "message": "💡 Daily Wellness Suggestion"
        };
      });
    } catch (e) {
      // Handle error
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    if (_dailyActivity == null) {
      return const SizedBox.shrink();
    }

    final activity = _dailyActivity!['daily_activity'] as Map<String, dynamic>;
    final message = _dailyActivity!['message'] as String? ?? 'Daily Activity';

    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.wb_sunny, color: Colors.green.shade700),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    message,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.green.shade700,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () {
                    _loadDailyActivity();
                    widget.onRefresh?.call();
                  },
                  icon: Icon(Icons.refresh, color: Colors.green.shade700),
                  tooltip: 'Get new suggestion',
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        activity['icon'] as String? ?? '💡',
                        style: const TextStyle(fontSize: 20),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          activity['title'] as String? ?? '',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    activity['description'] as String? ?? '',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                      height: 1.3,
                    ),
                  ),
                  if (activity['duration'] != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Duration: ${activity['duration']}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.green.shade600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
