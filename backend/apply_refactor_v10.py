import re
import codecs

# 1. Read original golden code
original_code = codecs.open(r'f:\.Hackathon\0.GeoFarmer\recovered_main_final.dart', 'r', 'utf-8').read()

# 2. Add Auth Imports
auth_import = "import 'screens/auth_screen.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\n\nvoid main() async {"
original_code = original_code.replace('void main() async {', auth_import)

# 3. Inject Auth state into _GeoKisanAppState
auth_state_vars = '''  bool _isAuthenticated = false;
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
'''
original_code = original_code.replace('  bool _isUrdu = false;', auth_state_vars + '\n  bool _isUrdu = false;')

# 4. Modify GeoKisanApp build method
material_app_search = r'return MaterialApp\(\s*title: .*?\s*(theme:.*?home:\s*)(GeoKisanHomePage\([^)]*\)),'
def app_replace(m):
    return 'if (_isLoading) return const MaterialApp(home: Scaffold(body: Center(child: CircularProgressIndicator())));\n    return MaterialApp(\n      title: _isUrdu ? \'Geo Kisaan\' : \'GeoFarmer\',\n      ' + m.group(1) + '_isAuthenticated ? ' + m.group(2) + ' : GeoKisanAuthScreen(isUrdu: _isUrdu, isDarkMode: _isDarkMode, activeLanguage: _activeLanguage, onToggleLanguage: _toggleLanguage, onSetLanguage: _setLanguage, onToggleTheme: _toggleTheme, onLoginSuccess: () { setState(() { _isAuthenticated = true; }); }),'

original_code = re.sub(material_app_search, app_replace, original_code, flags=re.DOTALL)

# 5. Inject _currentTabIndex into _GeoKisanHomePageState
original_code = original_code.replace('class _GeoKisanHomePageState extends State<GeoKisanHomePage> {', 'class _GeoKisanHomePageState extends State<GeoKisanHomePage> {\n  int _currentTabIndex = 0;')

# 6. Replace Widget build inside _GeoKisanHomePageState with 5-Tab Scaffold
build_start = original_code.find('Widget build(BuildContext context) {', original_code.find('class _GeoKisanHomePageState'))
end_of_home_page = original_code.find('class GeoKisanSubsystemPage extends StatefulWidget', build_start)

def make_tab(module_id, title_ur, title_en):
    return f'''GeoKisanSubsystemPage(
          moduleId: '{module_id}',
          moduleTitle: widget.isUrdu ? "{title_ur}" : "{title_en}",
          isUrdu: widget.isUrdu,
          isDarkMode: widget.isDarkMode,
          activeLanguage: widget.activeLanguage,
          activeLand: _activeLand,
          lands: _lands,
          backendUrl: _backendUrl,
          farmerCNIC: _farmerCNIC,
          farmerDOB: _farmerDOB,
          landCrops: _landCrops,
          landChats: _landChats,
          landLedgers: _landLedgers,
          landTelemetrySoil: _landTelemetrySoil,
          isOffline: _isOffline,
          onUpdateProfile: (cnic, dob) {{
            setState(() {{
              _farmerCNIC = cnic;
              _farmerDOB = dob;
            }});
          }},
          onUpdateLands: (newLands) {{
            setState(() {{
              _lands = newLands;
              if (newLands.isNotEmpty) {{
                if (!_lands.any((l) => l.id == _activeLand.id)) {{
                  _activeLand = newLands.first;
                }}
              }}
            }});
          }},
        )'''

tabs_children = f'''
      body: IndexedStack(
        index: _currentTabIndex,
        children: [
          {make_tab('tab_farm', 'فارم', 'Farm')},
          {make_tab('tab_monitor', 'مانیٹر', 'Monitor')},
          {make_tab('tab_ai_hub', 'اے آئی ہب', 'AI Hub')},
          {make_tab('m3', 'نقشہ', 'Navigate')},
          {make_tab('tab_more', 'مزید', 'More')},
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTabIndex,
        onTap: (index) => setState(() => _currentTabIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: GeoKisanTheme.primaryGreen,
        unselectedItemColor: GeoKisanTheme.lightText.withOpacity(0.5),
        backgroundColor: widget.isDarkMode ? const Color(0xFF1E1E1E) : Colors.white,
        items: [
          BottomNavigationBarItem(icon: const Icon(Icons.agriculture), label: widget.isUrdu ? "فارم" : "Farm"),
          BottomNavigationBarItem(icon: const Icon(Icons.water_drop), label: widget.isUrdu ? "مانیٹر" : "Monitor"),
          BottomNavigationBarItem(icon: const Icon(Icons.smart_toy), label: widget.isUrdu ? "اے آئی ہب" : "AI Hub"),
          BottomNavigationBarItem(icon: const Icon(Icons.map), label: widget.isUrdu ? "نقشہ" : "Navigate"),
          BottomNavigationBarItem(icon: const Icon(Icons.more_horiz), label: widget.isUrdu ? "مزید" : "More"),
        ],
      ),
'''

new_scaffold = f'''Widget build(BuildContext context) {{
    final local = AppLocalization(widget.isUrdu, activeLanguage: widget.activeLanguage);
    return Directionality(
      textDirection: widget.isUrdu ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Row(
            children: [
              const Icon(Icons.agriculture, color: Colors.white, size: 28),
              const SizedBox(width: 8),
              Text(
                local.translate('appName'),
                style: GeoKisanTheme.getHeaderStyle(isUrdu: widget.isUrdu, fontSize: 22, color: Colors.white),
              ),
            ],
          ),
          actions: [
            IconButton(
              onPressed: widget.onToggleTheme,
              icon: Icon(widget.isDarkMode ? Icons.wb_sunny : Icons.nightlight_round),
              tooltip: "Theme",
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.language, color: Colors.white),
              onSelected: widget.onToggleLanguage != null ? (val) {{ if (val == 'en' && widget.isUrdu) widget.onToggleLanguage!(); if (val == 'ur' && !widget.isUrdu) widget.onToggleLanguage!(); }} : null,
              itemBuilder: (context) => [
                const PopupMenuItem(value: 'en', child: Text("English")),
                const PopupMenuItem(value: 'ur', child: Text("اردو")),
              ],
            ),
          ],
        ),
        {tabs_children}
      ),
    );
  }}
}}

'''

original_code = original_code[:build_start] + new_scaffold + original_code[end_of_home_page:]

# 8. Extract old case bodies before replacing them
def get_case_body(code, case_name):
    pattern = r'case \'' + case_name + r'\':\s*(.*?)(?=\n\s*case \'\w+\':|\n\s*default:)'
    match = re.search(pattern, code, flags=re.DOTALL)
    if match:
        body = match.group(1).strip()
        if 'return' not in body:
            return 'return Container();'
        return body
    return 'return Container();'

farm_body = f"""
      case 'tab_farm':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm2')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm28')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm15')}
            }})
          ],
        );
"""

monitor_body = f"""
      case 'tab_monitor':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm9')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm8')}
            }})
          ],
        );
"""

ai_hub_body = f"""
      case 'tab_ai_hub':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm5')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm4')}
            }})
          ],
        );
"""

more_body = f"""
      case 'tab_more':
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm1')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm18')}
            }}),
            const Divider(height: 32),
            Builder(builder: (context) {{
              {get_case_body(original_code, 'm27')}
            }})
          ],
        );
"""

# 9. Now completely replace the switch block inside _renderSubsystemDetails
switch_start = original_code.find('switch (widget.moduleId) {')
switch_end = original_code.find('      default:', switch_start)
switch_end = original_code.find('    }', switch_end) + 5 # include the }

new_switch = f'''switch (widget.moduleId) {{
{farm_body}
{monitor_body}
{ai_hub_body}
{more_body}
      default:
        return const SizedBox.shrink();
    }}'''

original_code = original_code[:switch_start] + new_switch + original_code[switch_end:]

# 10. Update AuthScreen to accept onLoginSuccess!
auth_screen_code = codecs.open(r'f:\.Hackathon\0.GeoFarmer\frontend\lib\screens\auth_screen.dart', 'r', 'utf-8').read()
auth_screen_code = auth_screen_code.replace(
    'final VoidCallback onToggleTheme;',
    'final VoidCallback onToggleTheme;\n  final VoidCallback onLoginSuccess;'
)
auth_screen_code = auth_screen_code.replace(
    'required this.onToggleTheme,\n  })',
    'required this.onToggleTheme,\n    required this.onLoginSuccess,\n  })'
)
# Modify the pushReplacement to use onLoginSuccess instead
push_repl = r'''Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => GeoKisanHomePage(
          isUrdu: widget.isUrdu,
          isDarkMode: widget.isDarkMode,
          activeLanguage: widget.activeLanguage,
          onToggleLanguage: widget.onToggleLanguage,
          onSetLanguage: widget.onSetLanguage,
          onToggleTheme: widget.onToggleTheme,
        ),
      ),
    );'''
auth_screen_code = auth_screen_code.replace(push_repl, 'widget.onLoginSuccess();')

with codecs.open(r'f:\.Hackathon\0.GeoFarmer\frontend\lib\screens\auth_screen.dart', 'w', 'utf-8') as f:
    f.write(auth_screen_code)

with codecs.open(r'f:\.Hackathon\0.GeoFarmer\frontend\lib\main.dart', 'w', 'utf-8') as f:
    f.write(original_code)

print('Applied V10 refactor cleanly to main.dart and auth_screen.dart!')
