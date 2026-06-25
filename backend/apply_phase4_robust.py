import re

def apply_phase4_patch():
    with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        code = f.read()

    print("Original size:", len(code))

    # 1. Imports
    if "import 'package:flutter_local_notifications/flutter_local_notifications.dart';" not in code:
        code = code.replace(
            "import 'package:flutter/material.dart';",
            "import 'package:flutter/material.dart';\nimport 'package:flutter_local_notifications/flutter_local_notifications.dart';\nimport 'package:speech_to_text/speech_to_text.dart' as stt;\nimport 'package:flutter_tts/flutter_tts.dart';\nimport 'services/ai_service.dart';"
        )

    # 2. Add Location Address to LandNode
    if "String address;" not in code and "class LandNode" in code:
        # Just simple replacement if possible
        code = re.sub(
            r'(class LandNode \{[\s\S]*?)(String description;)',
            r'\1\2\n  String address;',
            code
        )
        code = re.sub(
            r'(LandNode\(\{[\s\S]*?)(required this.description,)',
            r'\1\2 this.address = "",',
            code
        )

    # 3. Dynamic Lands
    code = re.sub(
        r'List<LandNode> _lands = \[\s*LandNode\(id: "L1"[^\]]+\];',
        'List<LandNode> _lands = [];',
        code
    )
    code = code.replace(
        '_activeLand = _lands[0];',
        'if (_lands.isNotEmpty) {\n      _activeLand = _lands[0];\n    } else {\n      _activeLand = LandNode(id: "L0", nickname: "Unassigned", size: 0, unit: "Acres", latitude: 0, longitude: 0, description: "No plots");\n    }'
    )

    # 4. Location Address input in _buildLandRegistrationWizard
    addr_field = """        TextField(
          decoration: InputDecoration(labelText: widget.isUrdu ? "مقام / پتہ (Location / Address)" : "Location / Address"),
          onChanged: (val) => _newLandAddress = val,
        ),
        const SizedBox(height: 8),
"""
    # Assuming _newLandName exists
    if "_newLandAddress" not in code:
        code = code.replace(
            'String _newLandName = "";',
            'String _newLandName = "";\n  String _newLandAddress = "";'
        )
    
    code = code.replace(
        'TextField(\n          decoration: const InputDecoration(labelText: "Land Nickname (e.g. Plot C)"),\n          onChanged: (val) => _newLandName = val,\n        ),',
        'TextField(\n          decoration: const InputDecoration(labelText: "Land Nickname (e.g. Plot C)"),\n          onChanged: (val) => _newLandName = val,\n        ),\n        const SizedBox(height: 8),\n' + addr_field
    )

    # 5. Crop Selector dynamic list
    code = code.replace(
        'items: ["Wheat", "Cotton", "Rice", "Mango", "Sugarcane", "Maize"].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),',
        'items: _localCrops.isNotEmpty ? _localCrops.map((c) => DropdownMenuItem(value: c.name, child: Text(c.name))).toList() : ["Add Crop First"].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),'
    )

    # 6. AI Hub 21 options
    expanded_crops = '["Auto Detect", "Wheat", "Rice", "Cotton", "Sugarcane", "Mango", "Maize", "Potato", "Tomato", "Onion", "Citrus", "Guava", "Apple", "Banana", "Grapes", "Date Palm", "Chili", "Peas", "Chickpea", "Mustard", "Sunflower"]'
    code = code.replace(
        'items: ["Wheat (Sona-21)", "Cotton (BT-902)", "Rice (Basmati)", "Mango (Chaunsa)", "Sugarcane (Sartaj)"].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),',
        f'items: {expanded_crops}.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),'
    )

    with open('../frontend/lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(code)

    print("Patched basic phase 4 parts.")
    print("New size:", len(code))

if __name__ == "__main__":
    apply_phase4_patch()
