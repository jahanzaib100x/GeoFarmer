import re
import os

original_code = open(r'f:\.Hackathon\0.GeoFarmer\recovered_main_final.dart', encoding='utf-8').read()

# 1. Apply Auth Changes
auth_import = "import 'screens/auth_screen.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\n\nvoid main() async {"
original_code = original_code.replace('void main() async {', auth_import)

auth_app = '''class GeoKisanApp extends StatefulWidget {
  const GeoKisanApp({super.key});
  @override
  State<GeoKisanApp> createState() => _GeoKisanAppState();
}

class _GeoKisanAppState extends State<GeoKisanApp> {
  bool _isAuthenticated = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    setState(() {
      _isAuthenticated = token != null && token.isNotEmpty;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }
    return MaterialApp(
      title: 'Geo Kisaan',
      theme: GeoKisanTheme.lightTheme,
      darkTheme: GeoKisanTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: _isAuthenticated ? const GeoKisanHomePage() : GeoKisanAuthScreen(
        isUrdu: false, // Defaulting to English on first launch
        isDarkMode: false,
        onLoginSuccess: () {
          setState(() {
            _isAuthenticated = true;
          });
        },
      ),
    );
  }
}'''
original_code = re.sub(r'class GeoKisanApp extends StatelessWidget \{.*?Widget build\(BuildContext context\) \{.*?return MaterialApp\(.*?home: const GeoKisanHomePage\(\),.*?\);\s*\}\s*\}', auth_app, original_code, flags=re.DOTALL)

# 2. Modify GeoKisanHomePage for the 5-Tab Shell
new_home_page = '''class _GeoKisanHomePageState extends State<GeoKisanHomePage> {
  bool _isUrdu = false;
  bool _isDarkMode = false;
  int _currentTabIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _isUrdu = prefs.getBool('isUrdu') ?? false;
      _isDarkMode = prefs.getBool('isDarkMode') ?? false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentTabIndex,
        children: [
          GeoKisanSubsystemPage(moduleId: 'tab_farm', moduleTitle: widget.isUrdu ? "فارم" : "Farm", isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _isUrdu ? 'ur' : 'en', activeLand: LandNode(id: "1", nickname: "Main Farm", polygonCoords: [], createdAt: DateTime.now()), lands: [], backendUrl: "https://geofarmer-backend.onrender.com", farmerCNIC: "00000"),
          GeoKisanSubsystemPage(moduleId: 'tab_monitor', moduleTitle: widget.isUrdu ? "مانیٹر" : "Monitor", isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _isUrdu ? 'ur' : 'en', activeLand: LandNode(id: "1", nickname: "Main Farm", polygonCoords: [], createdAt: DateTime.now()), lands: [], backendUrl: "https://geofarmer-backend.onrender.com", farmerCNIC: "00000"),
          GeoKisanSubsystemPage(moduleId: 'tab_ai_hub', moduleTitle: widget.isUrdu ? "اے آئی ہب" : "AI Hub", isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _isUrdu ? 'ur' : 'en', activeLand: LandNode(id: "1", nickname: "Main Farm", polygonCoords: [], createdAt: DateTime.now()), lands: [], backendUrl: "https://geofarmer-backend.onrender.com", farmerCNIC: "00000"),
          GeoKisanSubsystemPage(moduleId: 'm3', moduleTitle: widget.isUrdu ? "نقشہ" : "Navigate", isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _isUrdu ? 'ur' : 'en', activeLand: LandNode(id: "1", nickname: "Main Farm", polygonCoords: [], createdAt: DateTime.now()), lands: [], backendUrl: "https://geofarmer-backend.onrender.com", farmerCNIC: "00000"),
          GeoKisanSubsystemPage(moduleId: 'tab_more', moduleTitle: widget.isUrdu ? "مزید" : "More", isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _isUrdu ? 'ur' : 'en', activeLand: LandNode(id: "1", nickname: "Main Farm", polygonCoords: [], createdAt: DateTime.now()), lands: [], backendUrl: "https://geofarmer-backend.onrender.com", farmerCNIC: "00000"),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTabIndex,
        onTap: (index) => setState(() => _currentTabIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: GeoKisanTheme.primaryGreen,
        unselectedItemColor: GeoKisanTheme.lightText.withOpacity(0.5),
        backgroundColor: _isDarkMode ? GeoKisanTheme.bgDarkCard : Colors.white,
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.agriculture), label: widget.isUrdu ? "فارم" : "Farm"),
          BottomNavigationBarItem(icon: Icon(Icons.water_drop), label: widget.isUrdu ? "مانیٹر" : "Monitor"),
          BottomNavigationBarItem(icon: Icon(Icons.smart_toy), label: widget.isUrdu ? "اے آئی ہب" : "AI Hub"),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: widget.isUrdu ? "نقشہ" : "Navigate"),
          BottomNavigationBarItem(icon: Icon(Icons.more_horiz), label: widget.isUrdu ? "مزید" : "More"),
        ],
      ),
    );
  }
}
// =========================================='''
original_code = re.sub(r'class _GeoKisanHomePageState extends State<GeoKisanHomePage> \{.*?// ==========================================', new_home_page, original_code, flags=re.DOTALL)

# 3. Merge the Switch cases in _renderSubsystemDetails
def get_case_body(code, case_name):
    pattern = r'case \'' + case_name + r'\':\s*(.*?)(?=case \'\w+\':|default:)'
    match = re.search(pattern, code, flags=re.DOTALL)
    if match:
        body = match.group(1).strip()
        if body.startswith('return '): body = body[7:]
        if body.endswith(';'): body = body[:-1]
        return body
    return 'Container()'

farm_body = f"""
      case 'tab_farm':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            {get_case_body(original_code, 'm2')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm28')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm15')}
          ],
        );
"""

monitor_body = f"""
      case 'tab_monitor':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            {get_case_body(original_code, 'm9')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm8')}
          ],
        );
"""

ai_hub_body = f"""
      case 'tab_ai_hub':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            {get_case_body(original_code, 'm5')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm4')}
          ],
        );
"""

more_body = f"""
      case 'tab_more':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            {get_case_body(original_code, 'm1')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm18')},
            const Divider(height: 32),
            {get_case_body(original_code, 'm27')}
          ],
        );
"""

original_code = re.sub(r'switch \(\s*widget\.moduleId\s*\)\s*\{', 'switch (widget.moduleId) {\n' + farm_body + monitor_body + ai_hub_body + more_body, original_code)

# 4. Remove all usages of dead variables 
def delete_regex(code, pattern):
    return re.sub(pattern, '', code, flags=re.DOTALL)

# We know the specific variables that were causing issues:
# _negotiationTipsUr, _negotiationTipsEn, _negotiationFeedbackUr, _negotiationFeedbackEn, _negotiationScore, _negotiationTargetPrice
# They are set inside _submitNegotiationBargain and _processTranscriptionSimulation
# And used inside case 'm7'
# If we simply delete the entire `case 'm7':` and the related functions, it's safer.
cases_to_remove = ['m7', 'm11', 'm14', 'm16', 'm19', 'm21', 'm24', 'm25', 'm26']
for case in cases_to_remove:
    pattern = r'case \'' + case + r'\':\s*.*?(?=case \'\w+\':|default:|\n\s*\})'
    original_code = re.sub(pattern, '', original_code, flags=re.DOTALL)

# Delete functions that match specific keywords
def remove_function_containing(code, keyword):
    matches = list(re.finditer(r'(Widget|Future<void>|void)\s+(_\w+)\s*\([^)]*\)\s*(async\s*)?\{', code))
    for m in reversed(matches):
        start = m.start()
        brace_start = code.find('{', start)
        if brace_start == -1: continue
        open_braces = 1
        idx = brace_start + 1
        while idx < len(code) and open_braces > 0:
            if code[idx] == '{': open_braces += 1
            elif code[idx] == '}': open_braces -= 1
            idx += 1
        func_body = code[start:idx]
        if keyword in func_body:
            code = code[:start] + code[idx:]
    return code

keywords = [
    '_submitNegotiationBargain',
    '_processTranscriptionSimulation',
    '_droneHotspots',
    '_scannedArea',
    '_complaintController',
    '_mandiAiRouteResult'
]

for kw in keywords:
    original_code = remove_function_containing(original_code, kw)

# Remove lingering disposes
original_code = original_code.replace('    _negotiationTextController.dispose();\n', '')
original_code = original_code.replace('    _complaintController.dispose();\n', '')

with open(r'f:\.Hackathon\0.GeoFarmer\frontend\lib\main.dart', 'w', encoding='utf-8') as f:
    f.write(original_code)
print('Applied refactor cleanly to main.dart!')
