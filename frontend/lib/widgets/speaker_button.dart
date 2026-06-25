import 'package:flutter/material.dart';
import '../services/tts_service.dart';

class SpeakerButton extends StatefulWidget {
  final String text;
  final String languageCode;

  const SpeakerButton({
    Key? key,
    required this.text,
    required this.languageCode,
  }) : super(key: key);

  @override
  State<SpeakerButton> createState() => _SpeakerButtonState();
}

class _SpeakerButtonState extends State<SpeakerButton> {
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();
    _isPlaying = TtsService.isSpeaking && TtsService.currentUtterance == widget.text;
    TtsService.addListener(_onTtsChanged);
  }

  @override
  void dispose() {
    TtsService.removeListener(_onTtsChanged);
    super.dispose();
  }

  void _onTtsChanged() {
    if (!mounted) return;
    setState(() {
      _isPlaying = TtsService.isSpeaking && TtsService.currentUtterance == widget.text;
    });
  }

  Future<void> _toggleSpeech() async {
    if (_isPlaying) {
      await TtsService.stop();
    } else {
      await TtsService.speak(widget.text, widget.languageCode);
    }
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(
        _isPlaying ? Icons.stop : Icons.volume_up,
        color: _isPlaying ? Colors.red : const Color(0xFF4A7C2F),
      ),
      onPressed: _toggleSpeech,
      tooltip: _isPlaying ? 'Stop' : 'Listen',
    );
  }
}
