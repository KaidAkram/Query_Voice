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

class _MicButtonState extends State<MicButton>
    with SingleTickerProviderStateMixin {
  bool _isRecording = false;
  late final AudioRecorder _audioRecorder;
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _animationController.stop();
        _animationController.reset();
      });
      if (path != null && widget.onRecordingComplete != null) {
        widget.onRecordingComplete!(path);
      }
    } else {
      if (await _audioRecorder.hasPermission()) {
        final Directory tempDir = await getTemporaryDirectory();
        final String filePath =
            '${tempDir.path}/query_voice_${DateTime.now().millisecondsSinceEpoch}.wav';

        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.wav),
          path: filePath,
        );
        setState(() {
          _isRecording = true;
          _animationController.repeat();
        });
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
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          height: _isRecording ? 80 : 0,
          child: _isRecording
              ? AnimatedBuilder(
                  animation: _animationController,
                  builder: (context, child) {
                    return CustomPaint(
                      size: const Size(double.infinity, 80),
                      painter: ModernWaveformPainter(
                        animationValue: _animationController.value,
                        color: QueryVoiceTheme.secondary,
                      ),
                    );
                  },
                )
              : const SizedBox.shrink(),
        ),
        const SizedBox(height: 20),
        GestureDetector(
          onTap: _toggleRecording,
          child: Stack(
            alignment: Alignment.center,
            children: [
              if (_isRecording) ...[
                _buildRipple(1.0),
                _buildRipple(1.5),
                _buildRipple(2.0),
              ],
              AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  final double pulse = _isRecording
                      ? (1.0 +
                          (math.sin(_animationController.value * 2 * math.pi) *
                              0.05))
                      : 1.0;
                  return Transform.scale(
                    scale: pulse,
                    child: Container(
                      height: _isRecording ? 95 : 80,
                      width: _isRecording ? 95 : 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: _isRecording
                            ? const LinearGradient(
                                colors: [Color(0xFFFF4D4D), Color(0xFFB30000)],
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                              )
                            : QueryVoiceTheme.primaryGradient,
                        border: Border.all(
                          color: Colors.white
                              .withOpacity(_isRecording ? 0.3 : 0.1),
                          width: 2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: (_isRecording
                                    ? Colors.redAccent
                                    : QueryVoiceTheme.primary)
                                .withOpacity(0.5),
                            blurRadius: _isRecording ? 40 : 20,
                            spreadRadius: _isRecording ? 12 : 2,
                          ),
                          if (_isRecording)
                            BoxShadow(
                              color: Colors.white.withOpacity(0.2),
                              blurRadius: 10,
                              spreadRadius: -2,
                              offset: const Offset(0, -4),
                            ),
                        ],
                      ),
                      child: TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0.0, end: _isRecording ? 1.0 : 0.0),
                        duration: const Duration(milliseconds: 300),
                        builder: (context, value, child) {
                          return Transform.rotate(
                            angle: value * math.pi / 4,
                            child: Icon(
                              _isRecording
                                  ? Icons.stop_rounded
                                  : Icons.mic_rounded,
                              size: 32 + (value * 10),
                              color: Colors.white,
                              shadows: [
                                Shadow(
                                  color: Colors.black26,
                                  blurRadius: 10,
                                  offset: const Offset(0, 4),
                                )
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        Text(
          _isRecording ? 'ANALYIZING VOICE...' : 'TAP TO COMMAND',
          style: TextStyle(
            color: _isRecording ? Colors.redAccent : Colors.white24,
            fontSize: 9,
            letterSpacing: 4,
            fontWeight: FontWeight.w900,
            shadows: [
              if (_isRecording)
                const Shadow(color: Colors.redAccent, blurRadius: 10)
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRipple(double delay) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 2000),
      builder: (context, value, child) {
        return Opacity(
          opacity: (1 - value) * 0.5,
          child: Transform.scale(
            scale: 1 + (value * delay),
            child: Container(
              height: 90,
              width: 90,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                    color: Colors.redAccent.withOpacity(0.5), width: 2),
              ),
            ),
          ),
        );
      },
      onEnd: () {
        // This is a simple way to repeat the ripple
      },
    );
  }
}

class ModernWaveformPainter extends CustomPainter {
  final double animationValue;
  final Color color;

  ModernWaveformPainter({required this.animationValue, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = color.withOpacity(0.5)
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    final double width = size.width;
    final double height = size.height;
    final int barCount = 40;
    final double spacing = width / barCount;

    for (int i = 0; i < barCount; i++) {
      // Create a sine wave effect based on position and animation value
      final double x = i * spacing;
      final double normalizedX = i / barCount;

      // Amplitude mask (tapers at ends)
      final double mask = math.sin(normalizedX * math.pi);

      // Dynamic height calculation
      final double wave1 = math
          .sin((normalizedX * 4 * math.pi) + (animationValue * 2 * math.pi));
      final double wave2 = math
          .sin((normalizedX * 2 * math.pi) - (animationValue * 4 * math.pi));

      final double barHeight =
          (40 * mask) + (wave1 * 10 * mask) + (wave2 * 15 * mask);

      final double yStart = (height - barHeight) / 2;

      canvas.drawLine(
        Offset(x, yStart),
        Offset(x, yStart + barHeight),
        paint,
      );
    }

    // Draw a second, thinner and brighter layer for depth
    paint.color = color;
    paint.strokeWidth = 1.5;
    for (int i = 0; i < barCount; i++) {
      final double x = i * spacing;
      final double normalizedX = i / barCount;
      final double mask = math.sin(normalizedX * math.pi);
      final double wave = math
          .sin((normalizedX * 8 * math.pi) + (animationValue * 6 * math.pi));
      final double barHeight = (20 * mask) + (wave * 15 * mask);
      final double yStart = (height - barHeight) / 2;

      canvas.drawLine(Offset(x, yStart), Offset(x, yStart + barHeight), paint);
    }
  }

  @override
  bool shouldRepaint(covariant ModernWaveformPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}
