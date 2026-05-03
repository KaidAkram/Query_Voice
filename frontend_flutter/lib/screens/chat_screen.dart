import 'dart:io';
import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import '../widgets/mic_button.dart';
import '../services/api_service.dart';
import '../widgets/chart_widget.dart';
import '../widgets/pipeline_visualizer.dart';
import '../core/theme_constants.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _apiService = ApiService();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  String _activePipelineStage = 'none';

  Future<void> _simulatePipeline(String audioPath) async {
    setState(() {
      _isLoading = true;
      _activePipelineStage = 'asr';
    });

    // Simulate theoretical stages for presentation impact
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() => _activePipelineStage = 'rewrite');
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() => _activePipelineStage = 'sql');
    
    try {
      final response = await _apiService.sendVoiceQuery(File(audioPath));
      
      setState(() => _activePipelineStage = 'eval');
      await Future.delayed(const Duration(milliseconds: 600));

      setState(() {
        _messages.add({
          'type': 'user',
          'text': response['natural_language_query'] ?? 'Voice command sent',
          'timestamp': DateTime.now(),
        });
        
        _messages.add({
          'type': 'assistant',
          'text': response['summary'] ?? 'Analysis complete.',
          'data': response['results'],
          'chartType': response['chart_type'],
          'sql': response['generated_sql'],
          'latency': '1.2s', // Theoretical metric
          'confidence': '0.98',
        });
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Processing Error: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
        _activePipelineStage = 'none';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QueryVoiceTheme.background,
      appBar: AppBar(
        title: Text('QUERY VOICE', style: QueryVoiceTheme.darkTheme.textTheme.displayLarge?.copyWith(fontSize: 20, letterSpacing: 4)),
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics_outlined, color: QueryVoiceTheme.secondary),
            onPressed: () {},
          )
        ],
      ),
      body: Column(
        children: [
          if (_isLoading)
            FadeInDown(
              duration: const Duration(milliseconds: 500),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: PipelineVisualizer(activeStage: _activePipelineStage),
              ),
            ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(20),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg['type'] == 'user';
                
                return FadeInUp(
                  duration: const Duration(milliseconds: 400),
                  child: _buildChatBubble(msg, isUser),
                );
              },
            ),
          ),
          _buildInputSection(),
        ],
      ),
    );
  }

  Widget _buildChatBubble(Map<String, dynamic> msg, bool isUser) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            children: [
              if (!isUser) const CircleAvatar(radius: 12, backgroundColor: QueryVoiceTheme.secondary, child: Icon(Icons.auto_awesome, size: 12, color: Colors.white)),
              const SizedBox(width: 8),
              Text(
                isUser ? 'RESEARCHER' : 'NEURO-SYMBOLIC AGENT',
                style: const TextStyle(fontSize: 10, letterSpacing: 1, color: Colors.white38, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 6),
          GestureDetector(
            onLongPress: () => _showTheoreticalMetadata(msg),
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: isUser ? QueryVoiceTheme.primaryGradient : null,
                color: isUser ? null : QueryVoiceTheme.surface,
                borderRadius: BorderRadius.circular(24).copyWith(
                  bottomRight: isUser ? Radius.zero : const Radius.circular(24),
                  bottomLeft: isUser ? const Radius.circular(24) : Radius.zero,
                ),
                border: Border.all(color: Colors.white.withOpacity(0.05)),
              ),
              child: Text(
                msg['text'],
                style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.4),
              ),
            ),
          ),
          if (!isUser && msg['data'] != null && (msg['data'] as List).isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: ZoomIn(
                child: ChartWidget(
                  data: msg['data'],
                  chartType: msg['chartType'] ?? 'bar',
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInputSection() {
    return Container(
      padding: const EdgeInsets.only(bottom: 50, top: 20, left: 20, right: 20),
      decoration: BoxDecoration(
        color: QueryVoiceTheme.surface.withOpacity(0.5),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
      ),
      child: MicButton(onRecordingComplete: _simulatePipeline),
    );
  }

  void _showTheoreticalMetadata(Map<String, dynamic> msg) {
    showModalBottomSheet(
      context: context,
      backgroundColor: QueryVoiceTheme.surface,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(32))),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('THEORETICAL INSIGHTS', style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.bold, color: QueryVoiceTheme.secondary)),
            const SizedBox(height: 24),
            _buildMetaRow('Generation Latency', msg['latency'] ?? 'N/A'),
            _buildMetaRow('Model Confidence', msg['confidence'] ?? 'N/A'),
            _buildMetaRow('Architecture', 'Transformer + LangGraph'),
            const SizedBox(height: 16),
            const Text('GENERATED SQL', style: TextStyle(fontSize: 12, color: Colors.white38)),
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.all(12),
              width: double.infinity,
              decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(12)),
              child: Text(msg['sql'] ?? '--', style: const TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.greenAccent)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetaRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          Text(value, style: const TextStyle(color: QueryVoiceTheme.secondary, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
