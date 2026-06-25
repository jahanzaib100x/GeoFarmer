import re

def main():
    with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1.1 Remove Hardcoded Land Blocks
    content = re.sub(
        r'List<LandNode> _lands = \[\s*LandNode\(id: "L1"[^\]]*\];',
        r'List<LandNode> _lands = [];\n  bool _isLandsLoaded = false;',
        content
    )

    # Replace _activeLand = _lands[0] in initState
    content = content.replace(
        '_activeLand = _lands[0];',
        '_activeLand = LandNode(id: "default", nickname: "Default Plot", size: 1.0, unit: "Acres", latitude: 0.0, longitude: 0.0, description: "Temp");'
    )

    # We need to add 'location' field to LandNode. Let's find LandNode class.
    # It probably doesn't have a 'location' string right now.
    
    with open('main_modified_temp.dart', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Patched part 1 into main_modified_temp.dart")

if __name__ == "__main__":
    main()
