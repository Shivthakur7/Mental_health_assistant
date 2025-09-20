import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class MentalHealthApi {
  final String baseUrl;
  String? _sessionId;
  
  MentalHealthApi({required this.baseUrl});

  // Session Management
  Future<String?> startSession({String? userId}) async {
    final uri = Uri.parse('$baseUrl/start_session');
    final res = await http.post(
      uri,
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId ?? 'flutter_user'}),
    );
    
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body) as Map<String, dynamic>;
      _sessionId = data['session_id'] as String?;
      return _sessionId;
    }
    return null;
  }

  String? get sessionId => _sessionId;

  Future<bool> health() async {
    final uri = Uri.parse('$baseUrl/health');
    final res = await http.get(uri);
    if (res.statusCode == 200) {
      try {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        return data['status'] == 'ok';
      } catch (_) {
        return false;
      }
    }
    return false;
  }

  // Enhanced text analysis with crisis detection
  Future<Map<String, dynamic>> analyzeText(
    String text, {
    String location = 'international',
    Map<String, String>? emergencyContacts,
  }) async {
    final uri = Uri.parse('$baseUrl/analyze_text');
    
    final body = {
      'text': text,
      'session_id': _sessionId,
      'user_id': 'flutter_user',
      'location': location,
      if (emergencyContacts != null) 'emergency_contacts': emergencyContacts,
    };
    
    final res = await http.post(
      uri,
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    
    if (res.statusCode != 200) {
      throw Exception('Server error: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // Enhanced multimodal analysis with crisis detection
  Future<Map<String, dynamic>> analyzeMultimodal({
    required String text,
    File? audioFile,
    File? imageFile,
    String location = 'international',
    Map<String, String>? emergencyContacts,
    String userName = 'User',
  }) async {
    final uri = Uri.parse('$baseUrl/analyze_multimodal');
    
    var request = http.MultipartRequest('POST', uri);
    
    // Add text and session fields
    request.fields['text'] = text;
    request.fields['session_id'] = _sessionId ?? '';
    request.fields['user_id'] = 'flutter_user';
    request.fields['location'] = location;
    request.fields['user_name'] = userName;
    
    if (emergencyContacts != null) {
      request.fields['emergency_contacts'] = jsonEncode(emergencyContacts);
    }
    
    // Add audio file if provided
    if (audioFile != null) {
      request.files.add(
        await http.MultipartFile.fromPath(
          'audio',
          audioFile.path,
          filename: 'audio.wav',
        ),
      );
    }
    
    // Add image file if provided
    if (imageFile != null) {
      request.files.add(
        await http.MultipartFile.fromPath(
          'image',
          imageFile.path,
          filename: 'image.jpg',
        ),
      );
    }
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    if (response.statusCode != 200) {
      throw Exception('Server error: ${response.statusCode} ${response.body}');
    }
    
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  // System status and analytics
  Future<Map<String, dynamic>> getSystemStatus() async {
    final uri = Uri.parse('$baseUrl/system_status');
    final res = await http.get(uri);
    
    if (res.statusCode != 200) {
      throw Exception('Failed to get system status: ${res.statusCode}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getAnalytics({int days = 7}) async {
    final uri = Uri.parse('$baseUrl/analytics?days=$days');
    final res = await http.get(uri);
    
    if (res.statusCode != 200) {
      throw Exception('Failed to get analytics: ${res.statusCode}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
