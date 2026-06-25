import re

with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    lines = f.readlines()

methods = []
for i, line in enumerate(lines):
    if re.match(r'^\s*Widget _build.*\(', line) or 'Widget _build' in line:
        methods.append(f"{i+1}: {line.strip()}")

with open('methods_dump.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(methods))

print(f"Found {len(methods)} build methods.")
