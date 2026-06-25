import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class GeoKisanTheme {
  // Explicit HSL-derived Color Token Definitions
  static const Color primaryGreen = Color(0xFF2D5A27);   // geokisan-primary-green (Deep forest green)
  static const Color aiGold = Color(0xFFE8A020);         // geokisan-ai-gold (Warm wheat gold)
  static const Color waterBlue = Color(0xFF1A6B8A);       // geokisan-water-blue (Canal Blue)
  static const Color alertClay = Color(0xFFD64045);       // geokisan-alert-red (Alert red)
  static const Color warningAmber = Color(0xFFF4A261);     // geokisan-warning-amber (Warning amber)
  static const Color bgDark = Color(0xFF12160F);          // geokisan-bg-dark (Warm dark off-black)
  static const Color bgDarkSurface = Color(0xFF1B3318);   // geokisan-bg-dark-surface (Dark forest green)
  static const Color surfaceCream = Color(0xFFF5F2EC);    // geokisan-surface-cream (Off-white background)
  static const Color lightText = Color(0xFF233B1E);       // High-contrast readable forest text

  // Configure Light Theme (Optimized for outdoor field use, reducing eye strain)
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: surfaceCream,
      primaryColor: primaryGreen,
      colorScheme: const ColorScheme.light(
        primary: primaryGreen,
        secondary: waterBlue,
        tertiary: aiGold,
        error: alertClay,
        background: surfaceCream,
        surface: Colors.white,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onBackground: lightText,
        onSurface: lightText,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
        elevation: 2,
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: lightText),
        titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: lightText),
        bodyLarge: TextStyle(fontSize: 16, color: lightText),
        bodyMedium: TextStyle(fontSize: 14, color: lightText),
      ),
    );
  }

  // Configure Dark Theme (Sleek dark soil context)
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: bgDark,
      primaryColor: primaryGreen,
      colorScheme: const ColorScheme.dark(
        primary: primaryGreen,
        secondary: waterBlue,
        tertiary: aiGold,
        error: alertClay,
        background: bgDark,
        surface: bgDarkSurface,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onBackground: surfaceCream,
        onSurface: surfaceCream,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: bgDark,
        foregroundColor: surfaceCream,
        elevation: 2,
      ),
      cardTheme: CardThemeData(
        color: bgDarkSurface,
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: surfaceCream),
        titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: surfaceCream),
        bodyLarge: TextStyle(fontSize: 16, color: surfaceCream),
        bodyMedium: TextStyle(fontSize: 14, color: surfaceCream),
      ),
    );
  }

  // Retreives specific localized font configs dynamically based on translation state
  static TextStyle getTextStyle({
    required bool isUrdu,
    required double fontSize,
    FontWeight fontWeight = FontWeight.normal,
    required Color color,
  }) {
    if (isUrdu) {
      double adjustedSize = fontSize < 16.0 ? 16.0 : fontSize;
      return getUrduStyle(fontSize: adjustedSize, color: color).copyWith(fontWeight: fontWeight);
    } else {
      // LTR English theme layout copy using DM Sans
      return GoogleFonts.dmSans(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
      );
    }
  }

  static TextStyle getHeaderStyle({
    required bool isUrdu,
    required double fontSize,
    FontWeight fontWeight = FontWeight.bold,
    required Color color,
  }) {
    if (isUrdu) {
      return getTextStyle(isUrdu: true, fontSize: fontSize, fontWeight: fontWeight, color: color);
    } else {
      // LTR English headers using Playfair Display
      return GoogleFonts.playfairDisplay(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
      );
    }
  }

  static TextStyle getUrduStyle({double? fontSize, Color? color}) {
    return GoogleFonts.notoNastaliqUrdu(
      fontSize: fontSize ?? 16.0,
      color: color,
      height: 1.5,
    );
  }
}
