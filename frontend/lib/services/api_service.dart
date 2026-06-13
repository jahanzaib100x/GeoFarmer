import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants.dart';

class ApiService {
  static Future<String> getGeminiKey() async {
    final prefs = await SharedPreferences.getInstance();
    final storedKey = prefs.getString('gemini_api_key') ?? '';
    if (storedKey.isNotEmpty) return storedKey;
    return AppConstants.geminiApiKey;
  }

  static Future<String> getDeepseekKey() async {
    final prefs = await SharedPreferences.getInstance();
    final storedKey = prefs.getString('deepseek_api_key') ?? '';
    if (storedKey.isNotEmpty) return storedKey;
    return AppConstants.deepseekApiKey;
  }

  static Future<String> translateText(String text, String targetLanguage) async {
    final keySource = targetLanguage + text;
    final bytes = utf8.encode(keySource);
    final digest = md5.convert(bytes);
    final cacheKey = "trans_${digest.toString()}";

    try {
      final prefs = await SharedPreferences.getInstance();
      if (prefs.containsKey(cacheKey)) {
        final cachedValue = prefs.getString(cacheKey);
        if (cachedValue != null && cachedValue.isNotEmpty) {
          return cachedValue;
        }
      }

      final prompt = "Translate the following text to $targetLanguage. Only return the translation, no extra text: $text";
      final translation = await askAI(prompt);

      await prefs.setString(cacheKey, translation);
      return translation;
    } catch (e) {
      print("Translation failed: $e");
      return text;
    }
  }

  static Future<String> callGemini(String prompt, {String? imageBase64}) async {
    final key = await getGeminiKey();
    final url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$key';
    final Map<String, dynamic> body;
    if (imageBase64 == null) {
      body = {
        "contents": [
          {
            "parts": [
              {"text": prompt}
            ]
          }
        ]
      };
    } else {
      body = {
        "contents": [
          {
            "parts": [
              {
                "inlineData": {
                  "mimeType": "image/jpeg",
                  "data": imageBase64
                }
              },
              {"text": prompt}
            ]
          }
        ]
      };
    }

    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      try {
        final text = decoded['candidates'][0]['content']['parts'][0]['text'] as String;
        return text;
      } catch (e) {
        throw Exception("Failed to parse Gemini response: ${response.body}");
      }
    } else {
      throw Exception("Gemini failed with status ${response.statusCode}: ${response.body}");
    }
  }

  static Future<String> callDeepSeek(String prompt) async {
    final key = await getDeepseekKey();
    final url = 'https://api.deepseek.com/chat/completions';
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $key',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are an expert agricultural AI assistant for Pakistani farmers."},
          {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
      }),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      try {
        return decoded['choices'][0]['message']['content'] as String;
      } catch (e) {
        throw Exception("Failed to parse DeepSeek response: ${response.body}");
      }
    } else {
      throw Exception("DeepSeek failed with status ${response.statusCode}: ${response.body}");
    }
  }

  static Future<String> callGeminiChat(List<Map<String, String>> history, {String? systemPrompt}) async {
    final key = await getGeminiKey();
    final url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$key';
    final contents = history.map((msg) {
      final role = msg['role'] == 'user' ? 'user' : 'model';
      final text = msg['text'] ?? msg['content'] ?? '';
      return {
        "role": role,
        "parts": [
          {"text": text}
        ]
      };
    }).toList();

    final Map<String, dynamic> body = {"contents": contents};
    if (systemPrompt != null && systemPrompt.isNotEmpty) {
      body["systemInstruction"] = {
        "parts": [
          {"text": systemPrompt}
        ]
      };
    }

    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      try {
        return decoded['candidates'][0]['content']['parts'][0]['text'] as String;
      } catch (e) {
        throw Exception("Failed to parse Gemini response: ${response.body}");
      }
    } else {
      throw Exception("Gemini Chat failed with status ${response.statusCode}: ${response.body}");
    }
  }

  static Future<String> callDeepSeekChat(List<Map<String, String>> history, {String? systemPrompt}) async {
    final key = await getDeepseekKey();
    final url = 'https://api.deepseek.com/chat/completions';
    final messages = <Map<String, String>>[];
    if (systemPrompt != null && systemPrompt.isNotEmpty) {
      messages.add({"role": "system", "content": systemPrompt});
    } else {
      messages.add({"role": "system", "content": "You are an expert agricultural AI assistant for Pakistani farmers."});
    }
    for (var msg in history) {
      messages.add({
        "role": msg['role'] ?? 'user',
        "content": msg['text'] ?? msg['content'] ?? ''
      });
    }

    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $key',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": 1000
      }),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      try {
        return decoded['choices'][0]['message']['content'] as String;
      } catch (e) {
        throw Exception("Failed to parse DeepSeek response: ${response.body}");
      }
    } else {
      throw Exception("DeepSeek Chat failed with status ${response.statusCode}: ${response.body}");
    }
  }

  static Future<String> askAI(String prompt) async {
    try {
      return await callGemini(prompt);
    } catch (e) {
      print('Gemini failed: $e');
      try {
        return await callDeepSeek(prompt);
      } catch (de) {
        print('DeepSeek failed: $de');
        rethrow;
      }
    }
  }

  static Future<String> askAIWithImage(String prompt, String imageBase64) async {
    try {
      return await callGemini(prompt, imageBase64: imageBase64);
    } catch (e) {
      print('Gemini with image failed: $e');
      try {
        return await callDeepSeek(prompt);
      } catch (de) {
        print('DeepSeek fallback failed: $de');
        rethrow;
      }
    }
  }

  static String buildLanguageInstruction(String languageCode) {
    if (languageCode == 'en') {
      return "Respond in English.";
    } else {
      return "Respond entirely in Urdu language using Urdu script (Nastaliq).";
    }
  }
}
