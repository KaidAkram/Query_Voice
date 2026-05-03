import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import '../core/theme_constants.dart';

class PipelineVisualizer extends StatelessWidget {
  final String activeStage; // 'asr', 'rewrite', 'sql', 'eval'

  const PipelineVisualizer({super.key, required this.activeStage});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          const Text(
            'AGENTIC REASONING PIPELINE',
            style: TextStyle(
              fontSize: 12,
              letterSpacing: 2,
              fontWeight: FontWeight.bold,
              color: QueryVoiceTheme.secondary,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildNode('asr', 'Whisper ASR', Icons.settings_voice),
              _buildConnector('asr'),
              _buildNode('rewrite', 'NLP Rewrite', Icons.psychology),
              _buildConnector('rewrite'),
              _buildNode('sql', 'SQL Synth', Icons.code),
              _buildConnector('sql'),
              _buildNode('eval', 'Reflexion', Icons.auto_fix_high),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNode(String stage, String label, IconData icon) {
    bool isActive = activeStage == stage;
    return Column(
      children: [
        Pulse(
          animate: isActive,
          infinite: true,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isActive ? QueryVoiceTheme.primary.withOpacity(0.3) : Colors.white.withOpacity(0.05),
              shape: BoxShape.circle,
              border: Border.all(
                color: isActive ? QueryVoiceTheme.secondary : Colors.white24,
                width: 2,
              ),
              boxShadow: isActive ? [
                BoxShadow(
                  color: QueryVoiceTheme.primary.withOpacity(0.5),
                  blurRadius: 10,
                  spreadRadius: 2,
                )
              ] : [],
            ),
            child: Icon(
              icon,
              color: isActive ? Colors.white : Colors.white38,
              size: 24,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: isActive ? Colors.white : Colors.white38,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }

  Widget _buildConnector(String stage) {
    // Determine if the connector should be "active" based on progress
    return Expanded(
      child: Container(
        height: 2,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              activeStage == stage ? QueryVoiceTheme.secondary : Colors.white12,
              activeStage == stage ? Colors.white12 : Colors.white12,
            ],
          ),
        ),
      ),
    );
  }
}
