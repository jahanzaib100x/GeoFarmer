import re

file_path = r'f:\.Hackathon\0.GeoFarmer\frontend\lib\main.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_cases = """
      case 'tab_farm':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildFarmerProfile(),
            const Divider(height: 32),
            _buildCropRegistration(),
            const Divider(height: 32),
            _buildSmartCropCalendar(),
          ],
        );
      case 'tab_monitor':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildLiveSensorDashboard(),
            const Divider(height: 32),
            _buildIrrigationReminders(),
          ],
        );
      case 'tab_ai_hub':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildCropDoctorHub(),
            const Divider(height: 32),
            _buildAiChatbot(),
          ],
        );
      case 'tab_more':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildMandiPrices(),
            const Divider(height: 32),
            _buildSeasonalFinancialLedger(),
            const Divider(height: 32),
            _buildOfflineSurvivalGuide(),
            const Divider(height: 32),
            // Moved settings
            ListTile(title: Text(widget.isUrdu ? "ترتیبات" : "Settings"), leading: const Icon(Icons.settings)),
          ],
        );
"""

# Insert new cases after switch(widget.moduleId) {
content = re.sub(r'(switch\s*\(\s*widget\.moduleId\s*\)\s*\{)', r'\1\n' + new_cases, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated GeoKisanSubsystemPageState switch cases")
