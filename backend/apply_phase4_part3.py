import re

def apply_part3():
    with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Inject TTS and STT instance variables
    tts_vars = """
  final stt.SpeechToText _speechToText = stt.SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  
  Future<void> _speak(String text) async {
    await _flutterTts.setLanguage(widget.isUrdu ? "ur-PK" : "en-US");
    await _flutterTts.speak(text);
  }
"""
    if "_speak" not in code:
        code = code.replace(
            "final ScrollController _dashboardScrollController = ScrollController();",
            "final ScrollController _dashboardScrollController = ScrollController();\n" + tts_vars
        )

    # 2. Add TTS buttons to Yield Generator
    # Search for Yield Estimation button
    yield_button = """
                      _buildActionSubmitButton(label: widget.isUrdu ? "پیداوار کا اندازہ لگائیں" : "Evaluate Yield Analytics", onPressed: () async {
                        if (_selectedCrop == "None") return;
                        setState(() { _isEvaluatingYield = true; });
                        try {
                          String prompt = "Provide a crop yield estimate, summary of factors, and practical agronomic advice for $_selectedCrop grown in Multan, Pakistan. Keep it concise, 3 sentences max.";
                          String result = await AIService.generateContent(prompt, systemPrompt: "You are an expert agronomist.");
                          setState(() {
                            _yieldEstimateEn = result;
                            _yieldEstimateUr = result; // Assuming bilingual output
                          });
                          await _speak(result);
                        } catch (e) {
                          print("Yield API error: $e");
                        }
                        setState(() { _isEvaluatingYield = false; });
                      }),
                      const SizedBox(height: 12),
                      if (_yieldEstimateEn.isNotEmpty)
                        Row(
                          children: [
                            Expanded(child: Text(_yieldEstimateEn)),
                            IconButton(icon: Icon(Icons.volume_up, color: Colors.green), onPressed: () => _speak(_yieldEstimateEn)),
                          ]
                        ),
"""
    
    # We will replace the original evaluate button logic with this.
    # The original is:
    # _buildActionSubmitButton(label: widget.isUrdu ? "پیداوار کا اندازہ لگائیں" : "Evaluate Yield Analytics", onPressed: () {
    code = re.sub(
        r'_buildActionSubmitButton\(label: widget\.isUrdu \? "پیداوار کا اندازہ لگائیں" : "Evaluate Yield Analytics", onPressed: \(\) \{[\s\S]*?\}\),',
        yield_button,
        code
    )

    # 3. Add TTS to AI Hub Crop Doctor
    # Look for "if (_diagClass.isNotEmpty)" where the diagnosis results are displayed.
    # We will inject a TTS button next to the severity.
    tts_doctor = """
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.orange.withOpacity(0.1),
                                border: Border.all(color: Colors.orange),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(_diagSeverity, style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 11)),
                            ),
                            IconButton(
                              icon: const Icon(Icons.volume_up, color: Colors.orange),
                              onPressed: () => _speak(widget.isUrdu ? _diagRemedyUr : _diagRemedyEn),
                            )
"""
    code = code.replace(
        """Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.orange.withOpacity(0.1),
                                border: Border.all(color: Colors.orange),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(_diagSeverity, style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 11)),
                            ),""",
        tts_doctor
    )

    # 4. Global Language Selector in AppBar
    # We need to find AppBar( in _GeoKisanSubsystemPageState or main app layout.
    # Actually, the main app shell uses Scaffold( appBar: AppBar( ...
    lang_appbar = """
        actions: [
          PopupMenuButton<String>(
            icon: Icon(Icons.language, color: Colors.white),
            onSelected: (String result) {
              // Update language logic here, maybe widget.onToggleLanguage()
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(value: 'en', child: Text('English')),
              const PopupMenuItem<String>(value: 'ur', child: Text('اردو (Urdu)')),
              const PopupMenuItem<String>(value: 'pa', child: Text('پنجابی (Punjabi)')),
              const PopupMenuItem<String>(value: 'sd', child: Text('سنڌي (Sindhi)')),
              const PopupMenuItem<String>(value: 'ps', child: Text('پښتو (Pashto)')),
              const PopupMenuItem<String>(value: 'ba', child: Text('بلوچی (Balochi)')),
            ],
          ),
          IconButton(
"""
    # Replace `actions: [\n          IconButton(`
    code = code.replace(
        "actions: [\n          IconButton(",
        lang_appbar
    )

    with open('../frontend/lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(code)

    print("Patched phase 4 part 3")

if __name__ == "__main__":
    apply_part3()
