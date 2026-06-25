import re

with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
for i, l in enumerate(lines):
    if 'Plot A' in l or 'Plot B' in l or 'Orchard East' in l:
        output.append(f"{i+1}: {l.strip()}")

with open('hardcoded_plots.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
