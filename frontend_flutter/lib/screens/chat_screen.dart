import 'package:flutter/material.dart';

/// ChatScreen — The primary conversational interface for QueryVoice.
///
/// Displays a chat-style UI where the user can:
/// - Tap a microphone button to record a voice query
/// - View transcribed text and SQL results
/// - See rendered charts from query responses
class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('QueryVoice'),
        centerTitle: true,
      ),
      body: const Center(
        child: Text('Chat interface — coming soon'),
      ),
      // TODO: Add MicButton FAB and message list
    );
  }
}
