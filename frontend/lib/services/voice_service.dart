import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class VoiceService {
  static final VoiceService _instance = VoiceService._internal();
  factory VoiceService() => _instance;
  VoiceService._internal();

  final FlutterTts _tts = FlutterTts();
  final stt.SpeechToText _stt = stt.SpeechToText();

  bool _isSpeaking = false;
  bool _isListening = false;
  bool _sttInitialized = false;
  bool _ttsInitialized = false;
  bool _isTtsInitializing = false;
  bool _isSttInitializing = false;

  bool get isSpeaking => _isSpeaking;
  bool get isListening => _isListening;

  // ──────────────── TTS ────────────────

  Future<void> initTts() async {
    if (_ttsInitialized || _isTtsInitializing) return;
    _isTtsInitializing = true;
    try {
      if (defaultTargetPlatform == TargetPlatform.android) {
        try {
          await _tts.setEngine("com.google.android.tts");
        } catch (e) {
          print("[VoiceService] Failed to set Google TTS engine: $e");
        }
      }
      await _tts.setVolume(1.0);
      await _tts.setSpeechRate(0.5);
      await _tts.setPitch(1.0);

      _tts.setStartHandler(() => _isSpeaking = true);
      _tts.setCompletionHandler(() => _isSpeaking = false);
      _tts.setErrorHandler((_) => _isSpeaking = false);
      _ttsInitialized = true;
    } catch (e) {
      print("[VoiceService] TTS initialization failed: $e");
    } finally {
      _isTtsInitializing = false;
    }
  }

  Future<void> speak(String text, String languageCode) async {
    if (text.isEmpty) return;
    try {
      await stop();
      String ttsLang = _mapToTtsLanguage(languageCode);
      await _tts.setLanguage(ttsLang);
      await _tts.speak(text);
      _isSpeaking = true;
    } catch (e) {
      print("[VoiceService] TTS speak failed: $e");
      _isSpeaking = false;
    }
  }

  Future<void> stop() async {
    try {
      await _tts.stop();
      _isSpeaking = false;
    } catch (e) {
      print("[VoiceService] TTS stop failed: $e");
    }
  }

  String _mapToTtsLanguage(String code) {
    const map = {
      'en': 'en-US',
      'ur': 'ur-PK',
      'pa': 'pa-PK',
      'ps': 'ps-AF',
      'sd': 'sd-PK',
      'bal': 'ur-PK',
      'sk': 'sk-PK',
    };
    return map[code] ?? 'en-US';
  }

  // ──────────────── STT ────────────────

  Function(String errorMsg)? _currentErrorCallback;

  Future<bool> initStt() async {
    if (_sttInitialized) return true;
    if (_isSttInitializing) return false;
    _isSttInitializing = true;
    try {
      _sttInitialized = await _stt.initialize(
        onStatus: (status) {
          if (status == 'done' || status == 'notListening') {
            _isListening = false;
          }
        },
        onError: (error) {
          print("[VoiceService] STT Error: $error");
          _isListening = false;
          if (_currentErrorCallback != null) {
            _currentErrorCallback!(error.errorMsg);
          }
        },
      );
    } catch (e) {
      print("[VoiceService] STT initialization failed: $e");
      _sttInitialized = false;
    } finally {
      _isSttInitializing = false;
    }
    return _sttInitialized;
  }

  Future<void> startListening({
    required String languageCode,
    required Function(String text, bool isFinal) onResult,
    required Function(String errorMsg) onError,
    Function(double soundLevel)? onSoundLevel,
  }) async {
    _currentErrorCallback = onError;
    try {
      if (!_sttInitialized) {
        final ok = await initStt();
        if (!ok) {
          onError("STT initialization failed");
          return;
        }
      }

      String locale = _mapToSttLocale(languageCode);
      try {
        final systemLocales = await _stt.locales();
        final hasLocale = systemLocales.any((l) => l.localeId == locale || l.localeId.split('_')[0] == languageCode);
        if (!hasLocale && systemLocales.isNotEmpty) {
          print("[VoiceService] Locale $locale not available. Finding match for $languageCode...");
          final matched = systemLocales.firstWhere(
            (l) => l.localeId.split('_')[0] == languageCode,
            orElse: () => systemLocales.first,
          );
          locale = matched.localeId;
          print("[VoiceService] Found fallback locale: $locale");
        }
      } catch (le) {
        print("[VoiceService] Locales query failed: $le. Using default mapping: $locale");
      }

      if (languageCode == 'ur') {
        try {
          final systemLocales = await _stt.locales();
          final hasUrdu = systemLocales.any((l) => l.localeId.split('_')[0] == 'ur');
          if (!hasUrdu && systemLocales.isNotEmpty) {
            locale = systemLocales.first.localeId;
            print("[VoiceService] Device does not support Urdu STT. Falling back to default: $locale");
          }
        } catch (_) {}
      }

      _isListening = true;

      await _stt.listen(
        onResult: (result) {
          onResult(result.recognizedWords, result.finalResult);
        },
        localeId: locale,
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 4),
        partialResults: true,
        onSoundLevelChange: onSoundLevel,
      );
    } catch (e) {
      print("[VoiceService] STT listen failed: $e");
      _isListening = false;
      onError(e.toString());
    }
  }

  Future<void> stopListening() async {
    try {
      await _stt.stop();
      _isListening = false;
    } catch (e) {
      print("[VoiceService] STT stop failed: $e");
    }
  }

  bool get sttAvailable => _sttInitialized;

  String _mapToSttLocale(String code) {
    const map = {
      'en': 'en_US',
      'ur': 'ur_PK',
      'pa': 'pa_PK',
      'ps': 'ps_PK',
      'sd': 'sd_PK',
      'bal': 'bal_PK',
      'sk': 'sk_PK',
    };
    return map[code] ?? 'en_US';
  }
}
