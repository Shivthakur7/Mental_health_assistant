import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class MentalHealthApi {
  final String baseUrl;
  const MentalHealthApi({required this.baseUrl});

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

  Future<Map<String, dynamic>> analyzeText(String text) async {
    final uri = Uri.parse('$baseUrl/analyze_text');
    final res = await http.post(
      uri,
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );
    if (res.statusCode != 200) {
      throw Exception('Server error: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> analyzeMultimodal({
    required String text,
    File? audioFile,
    File? imageFile,
  }) async {
    final uri = Uri.parse('$baseUrl/analyze_multimodal');
    
    var request = http.MultipartRequest('POST', uri);
    
    // Add text field
    request.fields['text'] = text;
    
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
}
