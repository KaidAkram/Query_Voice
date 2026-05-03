import 'dart:io';
import 'package:flutter/material.dart';
import '../widgets/mic_button.dart';
import '../services/api_service.dart';
import '../widgets/chart_widget.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _apiService = ApiService();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;

  void _handleVoiceQuery(String audioPath) async {
    setState(() => _isLoading = true);
    
    try {
      final response = await _apiService.sendVoiceQuery(File(audioPath));
      
      setState(() {
        _messages.add({
          'type': 'user',
          'text': response['natural_language_query'] ?? 'Voice command sent',
        });
        
        _messages.add({
          'type': 'assistant',
          'text': response['summary'] ?? 'Here are your results:',
          'data': response['results'],
          'chartType': response['chart_type'],
          'sql': response['generated_sql'],
        });
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('QueryVoice', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg['type'] == 'user';
                
                return Column(
                  crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isUser ? const Color(0xFF6C63FF) : const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(16).copyWith(
                          bottomRight: isUser ? Radius.zero : const Radius.circular(16),
                          bottomLeft: isUser ? const Radius.circular(16) : Radius.zero,
                        ),
                      ),
                      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                      child: Text(
                        msg['text'],
                        style: const TextStyle(color: Colors.white, fontSize: 16),
                      ),
                    ),
                    if (!isUser && msg['data'] != null && (msg['data'] as List).isNotEmpty)
                      ChartWidget(
                        data: msg['data'],
                        chartType: msg['chartType'] ?? 'bar',
                      ),
                  ],
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(color: Color(0xFF6C63FF)),
            ),
          Padding(
            padding: const EdgeInsets.only(bottom: 40, top: 20),
            child: MicButton(onRecordingComplete: _handleVoiceQuery),
          ),
        ],
      ),
    );
  }
}
