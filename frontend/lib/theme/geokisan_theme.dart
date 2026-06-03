import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class GeoKisanTheme {
  // Explicit HSL-derived Color Token Definitions
  static const Color primaryGreen = Color(0xFF4A7C2F);   // geokisan-primary-green (Field Green)
  static const Color aiGold = Color(0xFFC8860A);         // geokisan-ai-gold (Harvest Gold)
  static const Color waterBlue = Color(0xFF1A6B8A);       // geokisan-water-blue (Canal Blue)
  static const Color alertClay = Color(0xFF8B4513);       // geokisan-alert-clay (Clay Earth)
  static const Color bgDark = Color(0xFF1C2410);          // geokisan-bg-dark (Deep Soil)
  static const Color surfaceCream = Color(0xFFFAF8F3);    // geokisan-surface-cream (Off-white Cream background)
  static const Color lightText = Color(0xFF2F3E1E);       // High-contrast readable forest text

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
        surface: Color(0xFF2C381E),
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
        color: const Color(0xFF2C381E),
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
      // Native RTL rendering utilizing the Noto Nastaliq Urdu family
      // Font scale minimum sits at 16sp
      double adjustedSize = fontSize < 16.0 ? 16.0 : fontSize;
      return TextStyle(
        fontFamily: 'Noto Nastaliq Urdu',
        fontSize: adjustedSize,
        fontWeight: fontWeight,
        color: color,
        height: 1.8, // Increased line height for legible Urdu script rendering
      );
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
}
