import re

file_path = r'f:\.Hackathon\0.GeoFarmer\frontend\lib\main.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _GeoKisanHomePageState with new Bottom Navigation Shell
new_home_page = """
class _GeoKisanHomePageState extends State<GeoKisanHomePage> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          GeoKisanSubsystemPage(
            moduleId: "tab_farm",
            title: widget.isUrdu ? "فارم" : "Farm",
            isUrdu: widget.isUrdu,
            isDarkMode: widget.isDarkMode,
            activeLanguage: widget.activeLanguage,
          ),
          GeoKisanSubsystemPage(
            moduleId: "tab_monitor",
            title: widget.isUrdu ? "مانیٹر" : "Monitor",
            isUrdu: widget.isUrdu,
            isDarkMode: widget.isDarkMode,
            activeLanguage: widget.activeLanguage,
          ),
          GeoKisanSubsystemPage(
            moduleId: "tab_ai_hub",
            title: widget.isUrdu ? "اے آئی ہب" : "AI Hub",
            isUrdu: widget.isUrdu,
            isDarkMode: widget.isDarkMode,
            activeLanguage: widget.activeLanguage,
          ),
          GeoKisanSubsystemPage(
            moduleId: "m3",
            title: widget.isUrdu ? "نقشہ" : "Navigate",
            isUrdu: widget.isUrdu,
            isDarkMode: widget.isDarkMode,
            activeLanguage: widget.activeLanguage,
          ),
          GeoKisanSubsystemPage(
            moduleId: "tab_more",
            title: widget.isUrdu ? "مزید" : "More",
            isUrdu: widget.isUrdu,
            isDarkMode: widget.isDarkMode,
            activeLanguage: widget.activeLanguage,
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: GeoKisanTheme.primaryGreen,
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
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
"""

# Regex to match the old _GeoKisanHomePageState entirely
content = re.sub(r'class _GeoKisanHomePageState extends State<GeoKisanHomePage> \{.*?Widget _buildSliderCarousel\(\) \{.*?\}\s*\}', new_home_page, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated GeoKisanHomePageState")
