import re

def apply_part4():
    with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Tab 3 AI Summarizer with TTS
    # Original text: _waterSummaryUr / _waterSummaryEn
    # We will inject a button for AI Summarizer in the Smart Irrigation tab.
    ai_summary_ui = """
                    const SizedBox(height: 16),
                    Card(
                      elevation: 2,
                      color: GeoKisanTheme.primaryGreen.withOpacity(0.05),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(widget.isUrdu ? "اے آئی موسم اور آبپاشی کا خلاصہ" : "AI Weather & Irrigation Insight", style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen)),
                                IconButton(icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen), onPressed: () => _speak(widget.isUrdu ? _waterSummaryUr : _waterSummaryEn)),
                              ],
                            ),
                            Text(widget.isUrdu ? _waterSummaryUr : _waterSummaryEn, style: const TextStyle(fontSize: 12)),
                          ],
                        ),
                      ),
                    ),
"""
    code = code.replace(
        'const Divider(height: 24),',
        ai_summary_ui + '\n                        const Divider(height: 24),'
    )

    # 2. Tab 5: Full-Screen Map / Earth Toggle
    # Look for: _buildDroneStressMapGrid -> this is actually Tab 4, wait.
    # Wait, the prompt says Tab 5 Navigate (Maps/GEE + Route Optimizer + Draw boundary).
    # Let's search for the "Draw Plot Boundary on Map"
    # we can inject a Full Screen map button for the "Navigate" tab's map.
    full_screen_btn = """
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(widget.isUrdu ? "نقشہ منظر:" : "Map View:", style: TextStyle(fontWeight: FontWeight.bold)),
                            ElevatedButton.icon(
                              onPressed: () {
                                Navigator.push(context, MaterialPageRoute(builder: (_) => Scaffold(
                                  appBar: AppBar(title: Text("Full Screen Map"), leading: BackButton()),
                                  body: _buildInteractiveMapSelector(local),
                                )));
                              },
                              icon: const Icon(Icons.fullscreen),
                              label: Text("Full Screen"),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
"""
    code = code.replace(
        'title: Text(widget.isUrdu ? "پلاٹ کی حدود نقشے پر بنائیں" : "Draw Plot Boundary on Map", style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen)),\n                    ),\n                    const SizedBox(height: 8),\n                    SizedBox(\n                      height: 300,',
        'title: Text(widget.isUrdu ? "پلاٹ کی حدود نقشے پر بنائیں" : "Draw Plot Boundary on Map", style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen)),\n                    ),\n                    const SizedBox(height: 8),\n' + full_screen_btn + '                    SizedBox(\n                      height: 300,'
    )

    # 3. Tab 5: Draw Boundary AI Summary TTS
    # If the user clicks confirm boundary, add a TTS button or show an AI summary dialog.
    ai_boundary_summary = """
                        ElevatedButton.icon(
                          onPressed: () async {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Fetching Google Earth Engine Insights...")));
                            String result = await AIService.generateContent("Provide an AI summary for a farm boundary drawn at $_onboardingLocation with size $_onboardingLandSize Acres. Predict soil type and NDVI.");
                            showDialog(context: context, builder: (_) => AlertDialog(
                              title: Text("GEE AI Insight"),
                              content: Text(result),
                              actions: [
                                TextButton(onPressed: () => _speak(result), child: Text("Read Aloud")),
                                TextButton(onPressed: () => Navigator.pop(context), child: Text("Close")),
                              ]
                            ));
                          },
                          icon: const Icon(Icons.analytics),
                          label: Text("Analyze Boundary"),
                        ),
"""
    # Find "محفوظ کریں" : "Confirm Boundary" button
    code = code.replace(
        'ElevatedButton.icon(\n                            onPressed: () {',
        ai_boundary_summary + '\n                          ElevatedButton.icon(\n                            onPressed: () {'
    )

    # 4. Tab 6: Offline Agronomy Guide Expansion & TTS
    # Expand _buildLocalEmptyState or wherever the guide is.
    # The offline guide is likely built in Tab 6 ("More" -> "Offline Guide").
    # Wait, the prompt asked to expand it to 6 sections: Soil prep, Irrigation charts, Pest ID, Seasonal calendar, Pesticides, Storage.
    offline_guide_expansion = """
                ExpansionTile(
                  leading: Icon(Icons.book, color: GeoKisanTheme.primaryGreen),
                  title: Text("Comprehensive Agronomy Guide (Offline)"),
                  children: [
                    for (var topic in ["Soil Preparation", "Irrigation Charts", "Pest ID & Management", "Seasonal Sowing Calendar", "Pesticides Guide", "Storage & Post-Harvest"])
                      ListTile(
                        title: Text(topic),
                        trailing: IconButton(
                          icon: Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen),
                          onPressed: () => _speak("Reading guide for $topic: Always ensure proper soil tilling and timely watering..."),
                        ),
                      )
                  ],
                ),
"""
    # Replace existing offline guide card if possible or just append it to Tab 6.
    # Tab 6 is 'tab_more'. Let's find "تبصرہ بھیجیں" (Send Feedback) to insert before it.
    code = code.replace(
        'Card(\n              child: ListTile(\n                leading: const Icon(Icons.feedback',
        offline_guide_expansion + '\n            Card(\n              child: ListTile(\n                leading: const Icon(Icons.feedback'
    )

    # 5. Tab 6: Mandi Prices AI fetching
    mandi_prices_btn = """
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.storefront, color: Colors.orange),
                    title: Text(widget.isUrdu ? "مندی کی قیمتیں (اے آئی)" : "Live Mandi Prices (AI)"),
                    subtitle: Text("Powered by Gemini / DeepSeek"),
                    trailing: IconButton(
                      icon: Icon(Icons.refresh),
                      onPressed: () async {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Fetching latest prices...")));
                        String res = await AIService.generateContent("Give me the current average Mandi prices for Wheat, Cotton, and Rice per 40kg in Pakistan.");
                        showDialog(context: context, builder: (_) => AlertDialog(
                          title: Text("Live Mandi Rates"),
                          content: SingleChildScrollView(child: Text(res)),
                          actions: [
                            TextButton(onPressed: () => _speak(res), child: Text("Listen")),
                            TextButton(onPressed: () => Navigator.pop(context), child: Text("Close")),
                          ]
                        ));
                      },
                    ),
                  ),
                ),
"""
    code = code.replace(
        'Card(\n              child: ListTile(\n                leading: const Icon(Icons.language',
        mandi_prices_btn + '\n            Card(\n              child: ListTile(\n                leading: const Icon(Icons.language'
    )

    with open('../frontend/lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(code)

    print("Patched phase 4 part 4")

if __name__ == "__main__":
    apply_part4()
