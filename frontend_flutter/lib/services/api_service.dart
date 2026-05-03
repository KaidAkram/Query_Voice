import 'dart:io';
import 'package:dio/dio.dart';

/// ApiService — Handles all HTTP communication with the FastAPI backend.
///
/// Endpoints:
/// - POST /api/v1/query/voice  — Upload audio file for ASR + Text-to-SQL
/// - POST /api/v1/query/text   — Submit text query for Text-to-SQL
/// - GET  /api/v1/health       — Health check
class ApiService {
  // TODO: Move to environment config
  static const String baseUrl = 'http://localhost:8000/api/v1';

  Future<Map<String, dynamic>> sendVoiceQuery(File audioFile) async {
    try {
      final dio = Dio();
      
      String fileName = audioFile.path.split('/').last;
      FormData formData = FormData.fromMap({
        "audio": await MultipartFile.fromFile(audioFile.path, filename: fileName),
      });

      print("--- [API_SERVICE] Sending audio file to backend... ---");
      Response response = await dio.post(
        '$baseUrl/query/voice',
        data: formData,
      );
      
      return response.data;
    } catch (e) {
      print("--- [API_SERVICE] Error in sendVoiceQuery: $e ---");
      throw Exception('Failed to send voice query: $e');
    }
  }

  /// Sends a text-based natural language query to the backend.
  Future<Map<String, dynamic>> sendTextQuery(String query) async {
    // TODO: Implement POST request
    throw UnimplementedError('sendTextQuery not yet implemented');
  }

  /// Checks backend health status.
  Future<bool> healthCheck() async {
    // TODO: Implement GET /health
    throw UnimplementedError('healthCheck not yet implemented');
  }
}
