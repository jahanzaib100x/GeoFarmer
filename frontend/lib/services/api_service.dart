import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../main.dart';

class ApiService {
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

  static Future<String> callGeminiChat(List<Map<String, String>> history, {String? systemPrompt}) async {
    return _callChatHistory(history, systemPrompt);
  }

  static Future<String> _callChatHistory(List<Map<String, String>> history, String? systemPrompt) async {
    try {
      final url = "${globalBackendUrl}/api/ai/chat-history";
      final mappedHistory = history.map((msg) {
        final role = msg['role'] == 'user' ? 'user' : 'model';
        final content = msg['text'] ?? msg['content'] ?? '';
        return {
          "role": role,
          "content": content
        };
      }).toList();

      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "history": mappedHistory,
          "system_prompt": systemPrompt
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        return decoded["reply"] ?? "";
      } else {
        throw Exception("Server returned status ${response.statusCode}");
      }
    } catch (e) {
      print("Chat history call failed: $e");
      rethrow;
    }
  }

  static Future<String> askAI(String prompt) async {
    try {
      final url = "${globalBackendUrl}/api/ai/ask";
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"prompt": prompt}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        return decoded["reply"] ?? "";
      } else {
        throw Exception("Server returned status ${response.statusCode}");
      }
    } catch (e) {
      print("askAI failed: $e");
      return "Unable to process query. Please check your backend connection.";
    }
  }

  static Future<String> askAIWithImage(String prompt, String imageBase64) async {
    try {
      final url = Uri.parse("${globalBackendUrl}/api/ai/ask-image");
      final request = http.MultipartRequest("POST", url);
      request.fields["prompt"] = prompt;
      
      final bytes = base64Decode(imageBase64);
      request.files.add(http.MultipartFile.fromBytes(
        "image",
        bytes,
        filename: "upload.jpg",
      ));
      
      final response = await request.send().timeout(const Duration(seconds: 30));
      if (response.statusCode == 200) {
        final respStr = await response.stream.bytesToString();
        final decoded = jsonDecode(respStr);
        return decoded["reply"] ?? "";
      } else {
        throw Exception("Server returned status ${response.statusCode}");
      }
    } catch (e) {
      print("askAIWithImage failed: $e");
      rethrow;
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
