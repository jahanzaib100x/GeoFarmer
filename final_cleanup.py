"""
Final cleanup: Trim to line 15091, remove the extra blank lines from kernel double-spacing.
The kernel stores each source line followed by a blank line - we need to remove those
extra blank lines to get back to the original formatting.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('recovered_main_clean.dart', encoding='utf-8') as f:
    lines = f.readlines()

# Trim to valid code only (line 15091 = index 15090)
valid_lines = lines[:15092]

# The kernel double-spaces: every other line is blank.
# We need to remove the extra blank lines but keep intentional blank lines
# from the original source.
# Strategy: The kernel inserts ONE blank line after EVERY source line.
# So if the original had 2 consecutive blank lines, the kernel would show 3-4.
# Simply take every other line (the odd-indexed ones are the padding).
# Actually, let's be smarter - remove only the alternating blank lines.

# A simpler approach: since the original was ~8750 lines and this is ~15091,
# the ratio is ~1.72x which matches "every line doubled with blank after".
# Let's just strip alternating blanks.

result = []
i = 0
while i < len(valid_lines):
    line = valid_lines[i]
    result.append(line.rstrip() + '\n')
    # If next line is blank, skip it (kernel padding)
    if i + 1 < len(valid_lines) and valid_lines[i + 1].strip() == '':
        i += 2  # skip the blank padding line
    else:
        i += 1

# Write it
source = ''.join(result)
line_count = source.count('\n')

print(f"Final source: {len(source)} chars, {line_count} lines")

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

with open('recovered_main_final.dart', 'w', encoding='utf-8') as f:
    f.write(source)
print(f"\nSaved to recovered_main_final.dart")
