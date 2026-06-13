import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AIService {
  static const String geminiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';
  static const String deepseekUrl = 'https://api.deepseek.com/chat/completions';

  static Future<String> getGeminiKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('gemini_api_key') ?? '';
  }

  static Future<String> getDeepseekKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('deepseek_api_key') ?? '';
  }

  static Future<String> generateContent(String prompt, {String systemPrompt = ''}) async {
    try {
      final geminiKey = await getGeminiKey();
      final response = await http.post(
        Uri.parse('$geminiUrl?key=$geminiKey'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "contents": [{
            "parts": [{"text": "${systemPrompt.isNotEmpty ? '$systemPrompt\n\n' : ''}$prompt"}]
          }]
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['candidates'][0]['content']['parts'][0]['text'] ?? '';
      }
    } catch (e) {
      print("Gemini API failed: $e");
    }

    // Fallback to DeepSeek
    try {
      final deepseekKey = await getDeepseekKey();
      final response = await http.post(
        Uri.parse(deepseekUrl),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $deepseekKey'
        },
        body: jsonEncode({
          "model": "deepseek-chat",
          "messages": [
            if (systemPrompt.isNotEmpty) {"role": "system", "content": systemPrompt},
            {"role": "user", "content": prompt}
          ],
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['choices'][0]['message']['content'] ?? '';
      }
    } catch (e) {
      print("DeepSeek API failed: $e");
    }

    return "AI generation failed. Please check your internet connection or API keys.";
  }
}
