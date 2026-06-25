import re

with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find("Widget _renderSubsystemDetails(")
if start != -1:
    end = start + 50000
    with open('render_subsystem_details.txt', 'w', encoding='utf-8') as f:
        f.write(content[start:end])
