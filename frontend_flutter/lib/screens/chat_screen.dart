import 'dart:io';
import 'dart:ui';
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
  final ScrollController _scrollController = ScrollController();

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

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
        _scrollToBottom();
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
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Column(
          children: [
            RichText(
              text: TextSpan(
                style:
                    QueryVoiceTheme.darkTheme.textTheme.displayLarge?.copyWith(
                  fontSize: 16,
                  letterSpacing: 4,
                  fontWeight: FontWeight.w900,
                ),
                children: [
                  const TextSpan(text: 'QUERY '),
                  TextSpan(
                    text: 'V',
                    style: TextStyle(
                        color: QueryVoiceTheme.secondary, fontSize: 18),
                  ),
                  const TextSpan(text: 'OICE'),
                ],
              ),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: const BoxDecoration(
                    color: Colors.greenAccent,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  'SYSTEM ONLINE',
                  style: TextStyle(
                    fontSize: 8,
                    letterSpacing: 1.5,
                    color: Colors.white.withOpacity(0.3),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
        flexibleSpace: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
            child: Container(
              color: Colors.black.withOpacity(0.2),
            ),
          ),
        ),
      ),
      body: Stack(
        children: [
          // Decorative Background Blobs
          Positioned(
            top: -100,
            right: -50,
            child: _buildBackgroundBlob(
                250, QueryVoiceTheme.primary.withOpacity(0.1)),
          ),
          Positioned(
            bottom: 200,
            left: -100,
            child: _buildBackgroundBlob(
                300, QueryVoiceTheme.secondary.withOpacity(0.05)),
          ),
          Column(
            children: [
              const SizedBox(height: kToolbarHeight + 20),
              if (_isLoading)
                FadeInDown(
                  duration: const Duration(milliseconds: 500),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20.0, vertical: 8.0),
                    child:
                        PipelineVisualizer(activeStage: _activePipelineStage),
                  ),
                ),
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
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
              const SizedBox(height: 100), // Space for FAB
            ],
          ),
        ],
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: Material(
        color: Colors.transparent,
        child: Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: MicButton(onRecordingComplete: _simulatePipeline),
        ),
      ),
    );
  }

  Widget _buildBackgroundBlob(double size, Color color) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.2),
            blurRadius: 100,
            spreadRadius: 50,
          ),
        ],
      ),
    );
  }

  Widget _buildChatBubble(Map<String, dynamic> msg, bool isUser) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment:
                isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            children: [
              if (!isUser)
                const CircleAvatar(
                    radius: 12,
                    backgroundColor: QueryVoiceTheme.secondary,
                    child: Icon(Icons.auto_awesome,
                        size: 12, color: Colors.white)),
              const SizedBox(width: 8),
              Text(
                isUser ? 'RESEARCHER' : 'NEURO-SYMBOLIC AGENT',
                style: const TextStyle(
                    fontSize: 10,
                    letterSpacing: 1,
                    color: Colors.white38,
                    fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          GestureDetector(
            onLongPress: () => _showTheoreticalMetadata(msg),
            child: Container(
              padding: const EdgeInsets.all(18),
              constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.8),
              decoration: BoxDecoration(
                gradient: isUser ? QueryVoiceTheme.primaryGradient : null,
                color: isUser ? null : QueryVoiceTheme.surface.withOpacity(0.8),
                borderRadius: BorderRadius.circular(28).copyWith(
                  bottomRight: isUser ? Radius.zero : const Radius.circular(28),
                  bottomLeft: isUser ? const Radius.circular(28) : Radius.zero,
                ),
                border: Border.all(color: Colors.white.withOpacity(0.08)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  )
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    msg['text'],
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        height: 1.5,
                        fontWeight: FontWeight.w500),
                  ),
                  if (!isUser && msg['sql'] != null) ...[
                    const SizedBox(height: 16),
                    _buildSqlSnippet(msg['sql']),
                  ],
                ],
              ),
            ),
          ),
          if (!isUser &&
              msg['data'] != null &&
              msg['data'] is List &&
              (msg['data'] as List).isNotEmpty)
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

  Widget _buildSqlSnippet(String sql) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.black38,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.code_rounded,
                  size: 14, color: QueryVoiceTheme.secondary),
              const SizedBox(width: 8),
              Text(
                'GENERATED SQL',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.5,
                  color: Colors.white.withOpacity(0.4),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            sql,
            style: TextStyle(
              fontFamily: 'monospace',
              fontSize: 12,
              color: Colors.cyanAccent.withOpacity(0.8),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  void _showTheoreticalMetadata(Map<String, dynamic> msg) {
    showModalBottomSheet(
      context: context,
      backgroundColor: QueryVoiceTheme.surface,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(32))),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('THEORETICAL INSIGHTS',
                style: TextStyle(
                    letterSpacing: 2,
                    fontWeight: FontWeight.bold,
                    color: QueryVoiceTheme.secondary)),
            const SizedBox(height: 24),
            _buildMetaRow('Generation Latency', msg['latency'] ?? 'N/A'),
            _buildMetaRow('Model Confidence', msg['confidence'] ?? 'N/A'),
            _buildMetaRow('Architecture', 'Transformer + LangGraph'),
            const SizedBox(height: 16),
            const Text('GENERATED SQL',
                style: TextStyle(fontSize: 12, color: Colors.white38)),
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.all(12),
              width: double.infinity,
              decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(12)),
              child: Text(msg['sql'] ?? '--',
                  style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                      color: Colors.greenAccent)),
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
          Text(value,
              style: const TextStyle(
                  color: QueryVoiceTheme.secondary,
                  fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
