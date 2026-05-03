import 'package:flutter/material.dart';

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

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.large(
      onPressed: () {
        // TODO: Implement audio recording toggle
        setState(() => _isRecording = !_isRecording);
      },
      backgroundColor: _isRecording ? Colors.redAccent : const Color(0xFF6C63FF),
      child: Icon(
        _isRecording ? Icons.stop : Icons.mic,
        size: 36,
      ),
    );
  }
}
