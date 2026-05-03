import 'package:flutter/material.dart';
// import 'package:query_voice/screens/chat_screen.dart';

void main() {
  runApp(const QueryVoiceApp());
}

class QueryVoiceApp extends StatelessWidget {
  const QueryVoiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QueryVoice',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF6C63FF),
        useMaterial3: true,
        brightness: Brightness.dark,
      ),
      home: const Scaffold(
        body: Center(
          child: Text(
            'QueryVoice — Voice-Driven BI',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
      ),
      // home: const ChatScreen(),
    );
  }
}
