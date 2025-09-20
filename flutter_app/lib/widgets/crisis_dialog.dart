import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class CrisisDialog extends StatelessWidget {
  final Map<String, dynamic> analysisResult;

  const CrisisDialog({
    Key? key,
    required this.analysisResult,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final crisisLevel = analysisResult['crisis_level'] as String? ?? 'unknown';
    final message = analysisResult['message'] as String? ?? 
        'We\'re concerned about you. Help is available.';
    final immediateSteps = List<String>.from(
      analysisResult['immediate_steps'] ?? []
    );
    final helplines = analysisResult['helplines'] as Map<String, dynamic>?;

    return AlertDialog(
      title: Row(
        children: [
          Icon(
            Icons.warning,
            color: _getCrisisColor(crisisLevel),
            size: 28,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _getCrisisTitle(crisisLevel),
              style: TextStyle(
                color: _getCrisisColor(crisisLevel),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Crisis message
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _getCrisisColor(crisisLevel).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _getCrisisColor(crisisLevel).withOpacity(0.3),
                ),
              ),
              child: Text(
                message,
                style: const TextStyle(fontSize: 16),
              ),
            ),
            
            if (immediateSteps.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Immediate Steps:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              ...immediateSteps.map(
                (step) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ', style: TextStyle(fontSize: 16)),
                      Expanded(child: Text(step)),
                    ],
                  ),
                ),
              ),
            ],
            
            if (helplines != null) ...[
              const SizedBox(height: 16),
              const Text(
                'Crisis Resources:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              _buildHelplineInfo(helplines),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('I understand'),
        ),
        if (crisisLevel == 'critical') ...[
          ElevatedButton(
            onPressed: () => _callEmergency(),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Call 911'),
          ),
        ],
        ElevatedButton(
          onPressed: () => _openHelpline(helplines),
          style: ElevatedButton.styleFrom(
            backgroundColor: _getCrisisColor(crisisLevel),
            foregroundColor: Colors.white,
          ),
          child: const Text('Get Help Now'),
        ),
      ],
    );
  }

  Widget _buildHelplineInfo(Map<String, dynamic> helplines) {
    final primary = helplines['primary'] as Map<String, dynamic>?;
    
    if (primary == null) return const SizedBox.shrink();
    
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
          Text(
            primary['name'] as String? ?? 'Crisis Helpline',
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          if (primary['phone'] != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.phone, size: 16, color: Colors.blue),
                const SizedBox(width: 4),
                Text(
                  primary['phone'] as String,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
          if (primary['description'] != null) ...[
            const SizedBox(height: 4),
            Text(
              primary['description'] as String,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getCrisisColor(String level) {
    switch (level) {
      case 'critical':
        return Colors.red.shade700;
      case 'high':
        return Colors.orange.shade700;
      case 'moderate':
        return Colors.yellow.shade700;
      default:
        return Colors.blue.shade700;
    }
  }

  String _getCrisisTitle(String level) {
    switch (level) {
      case 'critical':
        return 'Critical Crisis Alert';
      case 'high':
        return 'High Priority Support';
      case 'moderate':
        return 'Mental Health Support';
      default:
        return 'Support Available';
    }
  }

  void _callEmergency() async {
    final uri = Uri.parse('tel:911');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  void _openHelpline(Map<String, dynamic>? helplines) async {
    if (helplines == null) return;
    
    final primary = helplines['primary'] as Map<String, dynamic>?;
    if (primary == null) return;
    
    // Try to call the phone number first
    final phone = primary['phone'] as String?;
    if (phone != null) {
      final uri = Uri.parse('tel:$phone');
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
        return;
      }
    }
    
    // Fallback to website
    final url = primary['url'] as String?;
    if (url != null) {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
    }
  }
}
