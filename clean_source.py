"""
Clean up the recovered main.dart source:
1. Trim to just our app code (before Flutter framework sources)
2. Collapse double-spaced lines from kernel encoding
3. Write clean output
"""
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('recovered_main_dart.txt', encoding='utf-8') as f:
    lines = f.readlines()

# Find where our source ends - look for the BSD license / flutter framework boundary
end_line = len(lines)
for i in range(len(lines)):
    line = lines[i].strip()
    # The framework source starts with a BSD license comment after binary junk
    if i > 10000 and ('Use of this source code is governed by a BSD-style license' in line):
        # Go back to find the last valid line of our code
        end_line = i - 2  # skip the binary junk line before it
        break

print(f"Our source ends at line {end_line}")

# Extract just our source
our_lines = lines[:end_line]

# The kernel stores sources with double line spacing (empty line between each line).
# Collapse consecutive blank lines to single blank lines.
cleaned = []
prev_blank = False
for line in our_lines:
    stripped = line.rstrip()
    is_blank = (stripped == '' or stripped == '\r')
    
    if is_blank:
        if not prev_blank:
            cleaned.append('')
        prev_blank = True
    else:
        # Remove any binary artifacts (control chars except \t)
        clean_line = ''.join(c for c in stripped if c == '\t' or (ord(c) >= 32) or c == '\n')
        cleaned.append(clean_line)
        prev_blank = False

source = '\n'.join(cleaned) + '\n'

print(f"Cleaned source: {len(source)} chars, {source.count(chr(10))} lines")

# Verify key classes
for pattern in ['FarmBoundaryDrawingScreen', 'BoundaryPainter', '_fetchGeeScan', 
                'YoloBoundingBoxPainter', 'GoogleMap(', 'class GeoKisanSubsystemPage',
                'class GeoKisanApp', 'class GeoKisanHomePage', 'class BackEndHttpResponse',
                'class _RawHtmlResponse', 'class BounceInkWell', 'onBoundarySaved']:
    if pattern in source:
        print(f"  FOUND: {pattern}")
    else:
        print(f"  MISSING: {pattern}")

# Check brace balance
opens = source.count('{')
closes = source.count('}')
print(f"\nBrace balance: {{ = {opens}, }} = {closes}, diff = {opens - closes}")

# Check parenthesis balance
opens_p = source.count('(')
closes_p = source.count(')')
print(f"Paren balance: ( = {opens_p}, ) = {closes_p}, diff = {opens_p - closes_p}")

with open('recovered_main_clean.dart', 'w', encoding='utf-8') as f:
    f.write(source)
print(f"\nSaved cleaned source to recovered_main_clean.dart")
