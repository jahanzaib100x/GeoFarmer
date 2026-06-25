with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('snippet500.txt', 'w', encoding='utf-8') as f:
    for i, l in enumerate(lines[500:600]):
        f.write(f"{i+501}: {l}")
