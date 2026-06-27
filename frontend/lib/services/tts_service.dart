import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

class TtsService {
  static final TtsService _instance = TtsService._internal();
  factory TtsService() => _instance;
  TtsService._internal();

  static final FlutterTts _tts = FlutterTts();
  static bool _isSpeaking = false;
  static String? _currentUtterance;
  static final List<VoidCallback> _listeners = [];

  static void addListener(VoidCallback cb) {
    _listeners.add(cb);
  }

  static void removeListener(VoidCallback cb) {
    _listeners.remove(cb);
  }

  static bool _initializing = false;
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized || _initializing) return;
    _initializing = true;
    try {
      if (defaultTargetPlatform == TargetPlatform.android) {
        try {
          await _tts.setEngine("com.google.android.tts");
        } catch (e) {
          print("TtsService failed to set Google TTS engine: $e");
        }
      }
      await _tts.setLanguage('en-US');
      await _tts.setSpeechRate(0.5);
      _tts.setCompletionHandler(() {
        _isSpeaking = false;
        _notifyListeners();
      });
      _tts.setStartHandler(() {
        _isSpeaking = true;
        _notifyListeners();
      });
      _tts.setErrorHandler((_) {
        _isSpeaking = false;
        _notifyListeners();
      });
      _initialized = true;
    } catch (e) {
      print("TtsService init failed: $e");
    } finally {
      _initializing = false;
    }
  }

  static void _notifyListeners() {
    for (final cb in List.of(_listeners)) {
      try {
        cb();
      } catch (e) {
        print("Error notifying TtsService listener: $e");
      }
    }
  }

  static Future<void> speak(String text, String languageCode) async {
    try {
      await _tts.stop();
      if (languageCode == 'en') {
        await _tts.setLanguage('en-US');
      } else {
        await _tts.setLanguage('ur-PK');
      }
      _isSpeaking = true;
      _currentUtterance = text;
      _notifyListeners();
      await _tts.speak(text);
    } catch (e) {
      print("TtsService speak failed: $e");
      _isSpeaking = false;
      _notifyListeners();
    }
  }

  static Future<void> stop() async {
    try {
      await _tts.stop();
      _isSpeaking = false;
      _currentUtterance = null;
      _notifyListeners();
    } catch (e) {
      print("TtsService stop failed: $e");
    }
  }

  static bool get isSpeaking => _isSpeaking;
  static String? get currentUtterance => _currentUtterance;
}
