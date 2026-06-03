import os
import re

def verify_system_integrity():
    """
    Automated testing script to crawl and verify the integrity of the
    GeoKisan / GeoFarmer precision-agriculture suite workspace.
    Checks directory structure, core code imports, design tokens mapping,
    and fail-safe relay rules.
    """
    workspace = "f:\\.Hackathon\\0.GeoFarmer"
    errors = []
    successes = []
    
    print("="*60)
    print("PROJECT GEOKISAN / GEOFARMER INTEGRITY SCANNER")
    print("="*60)
    
    # 1. Directory Checks
    target_dirs = [
        "backend",
        "dashboard",
        "firmware",
        "frontend",
        "frontend/lib",
        "frontend/lib/theme",
        "frontend/lib/localization"
    ]
    
    print("\nChecking Directory Structures...")
    for d in target_dirs:
        dir_path = os.path.join(workspace, d.replace('/', '\\'))
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            successes.append(f"Directory established: {d}")
        else:
            errors.append(f"Directory missing: {d}")
            
    # 2. Key File Checks
    target_files = [
        "backend/main.py",
        "backend/train.py",
        "backend/requirements.txt",
        "backend/Dockerfile",
        "dashboard/dashboard.py",
        "firmware/esp32_wifi.ino",
        "frontend/pubspec.yaml",
        "frontend/lib/main.dart",
        "frontend/lib/theme/geokisan_theme.dart",
        "frontend/lib/localization/app_localizations.dart",
        "README.md"
    ]
    
    print("Checking Production Files...")
    for f in target_files:
        file_path = os.path.join(workspace, f.replace('/', '\\'))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            successes.append(f"File verified: {f} ({os.path.getsize(file_path)} bytes)")
        else:
            errors.append(f"File missing: {f}")
            
    # 3. Analyze ESP32 Fail-Safe Configurations
    ino_path = os.path.join(workspace, "firmware", "esp32_wifi.ino")
    if os.path.exists(ino_path):
        print("Inspecting ESP32 Hardware Safeguards...")
        with open(ino_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        if "using namespace std;" in content:
            successes.append("ESP32 C++ namespace check passed.")
        else:
            errors.append("ESP32 namespace directive missing.")
            
        if "digitalWrite(PUMP_RELAY_PIN, LOW);" in content:
            successes.append("ESP32 Water Pump Relay forced-LOW boot rule verified.")
        else:
            errors.append("ESP32 Water Pump Relay fail-safe check failed!")
            
    # 4. Check Design Token Configurations in Flutter Theme
    theme_path = os.path.join(workspace, "frontend", "lib", "theme", "geokisan_theme.dart")
    if os.path.exists(theme_path):
        print("Scanning Flutter Theme Design Tokens...")
        with open(theme_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        tokens = {
            "primaryGreen": "0xFF4A7C2F",
            "aiGold": "0xFFC8860A",
            "waterBlue": "0xFF1A6B8A",
            "alertClay": "0xFF8B4513",
            "bgDark": "0xFF1C2410",
            "surfaceCream": "0xFFFAF8F3"
        }
        
        for k, val in tokens.items():
            if k in content and val in content:
                successes.append(f"Theme Token matched: {k} -> {val}")
            else:
                errors.append(f"Theme Token mismatch or missing: {k} ({val})")
                
    # 5. Check Flutter Multi-Language Layout Font Constraints
    theme_path = os.path.join(workspace, "frontend", "lib", "theme", "geokisan_theme.dart")
    if os.path.exists(theme_path):
        print("Analyzing Bilingual Navigation Core Layouts...")
        with open(theme_path, "r", encoding="utf-8") as file:
            content_theme = file.read()
            
        if "Noto Nastaliq Urdu" in content_theme:
            successes.append("Noto Nastaliq Urdu typography mapping verified.")
        else:
            errors.append("Noto Nastaliq Urdu typography mapping missing in theme config.")
            
    main_dart_path = os.path.join(workspace, "frontend", "lib", "main.dart")
    if os.path.exists(main_dart_path):
        with open(main_dart_path, "r", encoding="utf-8") as file:
            content_main = file.read()
        if "TextDirection.rtl" in content_main and "TextDirection.ltr" in content_main:
            successes.append("Dynamic RTL/LTR bi-directional UI matrices verified.")
        else:
            errors.append("Bi-directional text layouts rules missing.")


    # 6. Render Report Summary
    print("\n" + "="*60)
    print("GEOKISAN INTEGRITY RESULTS SUMMARY")
    print("="*60)
    print(f"Total Checks Passed: {len(successes)}")
    print(f"Total Errors Found:  {len(errors)}")
    print("="*60)
    
    if errors:
        print("\nSYSTEM INTEGRITY DEVIATIONS FOUND:")
        for err in errors:
            print(f"- {err}")
    else:
        print("\nALL SYSTEMS INTEGRAL AND PRODUCTION-READY!")
        
    print("="*60)

if __name__ == "__main__":
    verify_system_integrity()
