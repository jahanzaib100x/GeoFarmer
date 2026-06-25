/*
Description: "Enable automatic audio feedback narration in Negotiation Coach when voice mode is active."
StartLine: 5770
EndLine: 5788
TargetFile: "f:\\.Hackathon\\0.GeoFarmer\\frontend\\lib\\main.dart"
*/

// ==================== TARGET CONTENT ====================
"        setState(() {\n          _negotiationScore = data[\"score\"] ?? 70;\n          _negotiationFeedbackEn = data[\"feedback_en\"] ?? \"\";\n          _negotiationFeedbackUr = data[\"feedback_ur\"] ?? \"\";\n          _negotiationTipsEn = data[\"tips_en\"] ?? \"\";\n          _negotiationTipsUr = data[\"tips_ur\"] ?? \"\";\n          _negotiationTargetPrice = data[\"target_mandi_price\"] ?? \"\";\n          _isSTTTranscribing = false;\n        });"

// ==================== REPLACEMENT CONTENT ====================
"          setState(() {\n            _negotiationScore = data[\"score\"] ?? 70;\n            _negotiationFeedbackEn = data[\"feedback_en\"] ?? \"\";\n            _negotiationFeedbackUr = data[\"feedback_ur\"] ?? \"\";\n            _negotiationTipsEn = data[\"tips_en\"] ?? \"\";\n            _negotiationTipsUr = data[\"tips_ur\"] ?? \"\";\n            _negotiationTargetPrice = data[\"target_mandi_price\"] ?? \"\";\n            _isSTTTranscribing = false;\n          });\n          if (_isNegotiationVoiceMode) {\n            final textToSpeak = widget.isUrdu ? _negotiationFeedbackUr : _negotiationFeedbackEn;\n            _voiceService.speak(textToSpeak, widget.isUrdu ? 'ur' : 'en');\n          }"

