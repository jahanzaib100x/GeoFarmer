import re

with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    content = f.read()

def extract_method(method_name):
    start_idx = content.find(f"Widget {method_name}")
    if start_idx == -1: return ""
    brace_count = 0
    end_idx = start_idx
    started = False
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brace_count += 1
            started = True
        elif content[i] == '}':
            brace_count -= 1
        if started and brace_count == 0:
            end_idx = i + 1
            break
    return content[start_idx:end_idx]

with open('farm_tab_methods.txt', 'w', encoding='utf-8') as f:
    f.write(extract_method('_buildMyFarmProfileTab') + '\n\n')
    f.write(extract_method('_buildLandRegistrationWizard') + '\n\n')
    f.write(extract_method('_buildActiveCropList') + '\n\n')
