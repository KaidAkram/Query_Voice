import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

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
    return FloatingActionButton.large(
      onPressed: _toggleRecording,
      backgroundColor: _isRecording ? Colors.redAccent : const Color(0xFF6C63FF),
      child: Icon(
        _isRecording ? Icons.stop : Icons.mic,
        size: 36,
      ),
    );
  }
}
