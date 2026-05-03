import 'dart:io';
// import 'package:dio/dio.dart';

/// ApiService — Handles all HTTP communication with the FastAPI backend.
///
/// Endpoints:
/// - POST /api/v1/query/voice  — Upload audio file for ASR + Text-to-SQL
/// - POST /api/v1/query/text   — Submit text query for Text-to-SQL
/// - GET  /api/v1/health       — Health check
class ApiService {
  // TODO: Move to environment config
  static const String baseUrl = 'http://localhost:8000/api/v1';

  /// Sends a recorded audio file to the backend for processing.
  Future<Map<String, dynamic>> sendVoiceQuery(File audioFile) async {
    // TODO: Implement multipart upload via Dio
    throw UnimplementedError('sendVoiceQuery not yet implemented');
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
