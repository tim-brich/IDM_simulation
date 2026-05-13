import 'package:flutter/material.dart';

class AppTheme {
  static const Color emerald = Color(0xFF0D9488);
  static const Color graphite = Color(0xFF1F2937);
  static const Color gold = Color(0xFFF59E0B);
  static const Color backgroundDark = Color(0xFF111827);

  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: emerald,
      secondary: gold,
      surface: graphite,
      background: backgroundDark,
    ),
    scaffoldBackgroundColor: backgroundDark,
    cardTheme: CardThemeData(
      color: graphite,
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),
  );
}
