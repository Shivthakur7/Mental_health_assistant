import 'package:flutter/material.dart';
import '../services/api_client.dart';

class AnalyticsScreen extends StatefulWidget {
  final MentalHealthApi api;

  const AnalyticsScreen({Key? key, required this.api}) : super(key: key);

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  Map<String, dynamic>? _systemStatus;
  Map<String, dynamic>? _analytics;
  bool _isLoading = false;
  String? _error;
  int _selectedDays = 7;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final systemStatus = await widget.api.getSystemStatus();
      // Get user-specific analytics instead of global analytics
      final analytics = await widget.api.getUserAnalytics(days: _selectedDays);

      setState(() {
        _systemStatus = systemStatus;
        _analytics = analytics;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('System Analytics'),
        actions: [
          IconButton(
            onPressed: _loadData,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorWidget()
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildSystemStatusCard(),
                      const SizedBox(height: 16),
                      _buildAnalyticsCard(),
                      const SizedBox(height: 16),
                      _buildSessionInfoCard(),
                    ],
                  ),
                ),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red.shade300,
          ),
          const SizedBox(height: 16),
          Text(
            'Failed to load analytics',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            _error ?? 'Unknown error',
            style: TextStyle(color: Colors.grey.shade600),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildSystemStatusCard() {
    if (_systemStatus == null) return const SizedBox.shrink();

    final status = _systemStatus!['status'] as String? ?? 'unknown';
    final emergencyNotifications = _systemStatus!['emergency_notifications'] as Map<String, dynamic>? ?? {};
    final todayStats = _systemStatus!['today_stats'] as Map<String, dynamic>? ?? {};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.health_and_safety,
                  color: _getStatusColor(status),
                ),
                const SizedBox(width: 8),
                const Text(
                  'System Status',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildStatusRow(
              'Backend Status',
              status.toUpperCase(),
              _getStatusColor(status),
            ),
            _buildStatusRow(
              'SMS Notifications',
              emergencyNotifications['sms'] == true ? 'ENABLED' : 'DISABLED',
              emergencyNotifications['sms'] == true ? Colors.green : Colors.orange,
            ),
            _buildStatusRow(
              'Email Notifications',
              emergencyNotifications['email'] == true ? 'ENABLED' : 'DISABLED',
              emergencyNotifications['email'] == true ? Colors.green : Colors.orange,
            ),
            const Divider(),
            const Text(
              'Today\'s Activity',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Interactions',
                    '${(todayStats['interactions'] as num?)?.toInt() ?? 0}',
                    Icons.chat,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    'Crisis Events',
                    '${(todayStats['crisis_events'] as num?)?.toInt() ?? 0}',
                    Icons.warning,
                    Colors.red,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    'Users',
                    '${(todayStats['unique_users'] as num?)?.toInt() ?? 0}',
                    Icons.people,
                    Colors.green,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsCard() {
    if (_analytics == null) return const SizedBox.shrink();

    // Handle user-specific analytics structure
    final personalStats = _analytics!['personal_stats'] as Map<String, dynamic>? ?? {};
    final insights = _analytics!['insights'] as Map<String, dynamic>? ?? {};
    
    final totalInteractions = (personalStats['total_interactions'] as num?)?.toInt() ?? 0;
    final totalCrisisEvents = (personalStats['crisis_events'] as num?)?.toInt() ?? 0;
    final crisisRate = (personalStats['crisis_rate'] as num?)?.toDouble() ?? 0.0;
    final avgMoodScore = (personalStats['average_mood_score'] as num?)?.toDouble() ?? 0.0;
    final sessionCount = (personalStats['session_count'] as num?)?.toInt() ?? 0;
    final moodImprovement = (personalStats['mood_improvement'] as num?)?.toDouble() ?? 0.0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.analytics, color: Colors.purple),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Your Personal Analytics (Last $_selectedDays days)',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                DropdownButton<int>(
                  value: _selectedDays,
                  items: const [
                    DropdownMenuItem(value: 1, child: Text('1 day')),
                    DropdownMenuItem(value: 7, child: Text('7 days')),
                    DropdownMenuItem(value: 30, child: Text('30 days')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _selectedDays = value;
                      });
                      _loadData();
                    }
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Your Interactions',
                    '$totalInteractions',
                    Icons.chat_bubble_outline,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Crisis Events',
                    '$totalCrisisEvents',
                    Icons.warning_amber,
                    Colors.red,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Crisis Rate',
                    '${crisisRate.toStringAsFixed(1)}%',
                    Icons.trending_up,
                    crisisRate > 10 ? Colors.red : Colors.orange,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Avg Mood',
                    avgMoodScore.toStringAsFixed(2),
                    avgMoodScore >= 0 ? Icons.sentiment_satisfied : Icons.sentiment_dissatisfied,
                    avgMoodScore >= 0 ? Colors.green : Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Sessions',
                    '$sessionCount',
                    Icons.access_time,
                    Colors.purple,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildAnalyticsCard2(
                    'Mood Trend',
                    moodImprovement > 0.1 ? '📈 Improving' : moodImprovement < -0.1 ? '📉 Declining' : '➡️ Stable',
                    moodImprovement > 0.1 ? Icons.trending_up : moodImprovement < -0.1 ? Icons.trending_down : Icons.trending_flat,
                    moodImprovement > 0.1 ? Colors.green : moodImprovement < -0.1 ? Colors.red : Colors.orange,
                  ),
                ),
              ],
            ),
            
            // Add insights section
            if (insights.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                '💡 Personal Insights',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildInsightsSection(insights),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSessionInfoCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info_outline, color: Colors.teal),
                const SizedBox(width: 8),
                const Text(
                  'Session Information',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('Session ID', widget.api.sessionId?.substring(0, 8) ?? 'None'),
            _buildInfoRow('Backend URL', widget.api.baseUrl),
            _buildInfoRow('Last Updated', DateTime.now().toString().substring(0, 19)),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withOpacity(0.3)),
            ),
            child: Text(
              value,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w500,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 10,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsCard2(String title, String value, IconData icon, Color color) {
    return Flexible(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    value,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(
                fontSize: 11,
                color: color.withOpacity(0.8),
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 2,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsSection(Map<String, dynamic> insights) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildInsightRow('Mood Trending', insights['mood_trending'] ?? 'unknown'),
          _buildInsightRow('Activity Level', insights['activity_level'] ?? 'unknown'),
          _buildInsightRow('Crisis Frequency', insights['crisis_frequency'] ?? 'unknown'),
        ],
      ),
    );
  }

  Widget _buildInsightRow(String label, String value) {
    Color color = Colors.grey;
    IconData icon = Icons.info;
    
    switch (value.toLowerCase()) {
      case 'improving':
        color = Colors.green;
        icon = Icons.trending_up;
        break;
      case 'declining':
        color = Colors.red;
        icon = Icons.trending_down;
        break;
      case 'stable':
        color = Colors.blue;
        icon = Icons.trending_flat;
        break;
      case 'high':
        color = Colors.green;
        icon = Icons.arrow_upward;
        break;
      case 'moderate':
        color = Colors.orange;
        icon = Icons.remove;
        break;
      case 'low':
        color = Colors.red;
        icon = Icons.arrow_downward;
        break;
      case 'concerning':
        color = Colors.red;
        icon = Icons.warning;
        break;
      case 'none':
        color = Colors.green;
        icon = Icons.check_circle;
        break;
    }
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Text(
            value.toUpperCase(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return Colors.green;
      case 'degraded':
        return Colors.orange;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
