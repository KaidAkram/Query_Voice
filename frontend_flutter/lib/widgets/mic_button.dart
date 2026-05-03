import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'dart:math' as math;
import '../core/theme_constants.dart';

/// MicButton — An animated floating action button for voice recording.
///
/// Handles:
/// - Press-and-hold to record audio
/// - Visual feedback (pulsing animation) during recording
/// - Triggers callback with recorded audio file path
class MicButton extends StatefulWidget {
  final Function(String audioPath)? onRecordingComplete;

  const MicButton({super.key, this.onRecordingComplete});

  @override
  State<MicButton> createState() => _MicButtonState();
}

class _MicButtonState extends State<MicButton> {
  bool _isRecording = false;
  late final AudioRecorder _audioRecorder;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      // Stop recording
      final path = await _audioRecorder.stop();
      setState(() => _isRecording = false);
      if (path != null && widget.onRecordingComplete != null) {
        widget.onRecordingComplete!(path);
      }
    } else {
      // Start recording
      if (await _audioRecorder.hasPermission()) {
        final Directory tempDir = await getTemporaryDirectory();
        final String filePath = '${tempDir.path}/query_voice_${DateTime.now().millisecondsSinceEpoch}.wav';
        
        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.wav),
          path: filePath,
        );
        setState(() => _isRecording = true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Microphone permission denied.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (_isRecording)
          SizedBox(
            height: 60,
            width: double.infinity,
            child: CustomPaint(
              painter: WaveformPainter(
                color: QueryVoiceTheme.secondary,
              ),
            ),
          ),
        const SizedBox(height: 20),
        GestureDetector(
          onTap: _toggleRecording,
          child: Container(
            height: 90,
            width: 90,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: _isRecording 
                ? const LinearGradient(colors: [Colors.redAccent, Colors.red])
                : QueryVoiceTheme.primaryGradient,
              boxShadow: [
                BoxShadow(
                  color: (_isRecording ? Colors.redAccent : QueryVoiceTheme.primary).withOpacity(0.4),
                  blurRadius: 20,
                  spreadRadius: 5,
                )
              ],
            ),
            child: Icon(
              _isRecording ? Icons.stop_rounded : Icons.mic_rounded,
              size: 40,
              color: Colors.white,
            ),
          ),
        ),
      ],
    );
  }
}

class WaveformPainter extends CustomPainter {
  final Color color;
  final math.Random random = math.Random();

  WaveformPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    const int barCount = 30;
    final double spacing = size.width / barCount;

    for (int i = 0; i < barCount; i++) {
      final double barHeight = random.nextDouble() * size.height;
      final double x = i * spacing;
      final double y = (size.height - barHeight) / 2;
      
      canvas.drawLine(
        Offset(x, y),
        Offset(x, y + barHeight),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

