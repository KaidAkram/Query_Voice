import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class QueryVoiceTheme {
  // Cyber-Medical Color Palette
  static const Color primary = Color(0xFF6366F1); // Indigo
  static const Color secondary = Color(0xFF06B6D4); // Cyan
  static const Color accent = Color(0xFF8B5CF6); // Violet
  static const Color background = Color(0xFF0F172A); // Slate 900
  static const Color surface = Color(0xFF1E293B); // Slate 800
  static const Color glass = Color(0x1AFFFFFF); // Low opacity white
  
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static ThemeData darkTheme = ThemeData.dark().copyWith(
    scaffoldBackgroundColor: background,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      secondary: secondary,
      surface: surface,
    ),
    textTheme: GoogleFonts.outfitTextTheme(ThemeData.dark().textTheme).copyWith(
      displayLarge: GoogleFonts.outfit(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        color: Colors.white70,
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
    ),
  );
  
  static BoxDecoration glassDecoration = BoxDecoration(
    color: glass,
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: Colors.white12),
  );
}
