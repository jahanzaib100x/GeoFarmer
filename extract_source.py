"""
Extract Dart source code from the compiled app.dill kernel file.
The kernel binary contains the original source text embedded within it.
We'll scan for recognizable Dart patterns and extract the main.dart source.
"""
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

dill_path = r'frontend\.dart_tool\flutter_build\78299de89d176b9560d8694aa0f24c70\app.dill'

with open(dill_path, 'rb') as f:
    data = f.read()

print(f"app.dill size: {len(data)} bytes")

# The Dart kernel format embeds source text. Let's find all occurrences of
# our main.dart content. The source is typically stored as UTF-8 text blocks.
# We'll look for the class definition patterns.

# Strategy: Find the large contiguous block of UTF-8 text that contains our source.
# Dart kernel stores sources as length-prefixed strings.

# Let's find all source URIs first
uri_pattern = b'package:geofarmer/main.dart'
uri_idx = data.find(uri_pattern)
print(f"Package URI found at: {uri_idx}")

# Find the file URI
file_pattern = b'file:///F:/.Hackathon/0.GeoFarmer/frontend/lib/main.dart'
file_idx = data.find(file_pattern)
print(f"File URI found at: {file_idx}")

# Now let's find the actual source content. In Dart kernel format,
# source text is stored after a source URI entry. Let's search for
# the beginning of the main.dart source - the import statements.
import_pattern = b"import 'package:flutter/material.dart'"
import_idx = data.find(import_pattern)
print(f"Import statement found at: {import_idx}")

if import_idx >= 0:
    # The source should be a contiguous block from here.
    # Let's find where it ends by looking for a non-UTF8 sequence or null bytes
    # after a reasonable stretch.
    
    # Extract a large chunk and find the end
    chunk_start = import_idx
    # Read up to 500KB from the import start
    chunk = data[chunk_start:chunk_start + 500000]
    
    # Find the end - look for the last valid Dart line
    # The source ends when we hit binary data (non-printable chars in sequence)
    end_markers = [
        b'\x00\x00\x00',  # null bytes
    ]
    
    # Decode as UTF-8, stopping when we can't
    try:
        text = chunk.decode('utf-8', errors='replace')
    except:
        text = chunk.decode('latin-1')
    
    # Find where actual Dart code ends - look for long runs of replacement chars
    # or binary garbage
    lines = text.split('\n')
    good_lines = []
    bad_count = 0
    for line in lines:
        # Check if line looks like valid Dart/text
        replacements = line.count('\ufffd')
        nulls = line.count('\x00')
        if replacements > 5 or nulls > 3:
            bad_count += 1
            if bad_count > 2:
                break
        else:
            bad_count = 0
            good_lines.append(line)
    
    source = '\n'.join(good_lines)
    
    # Clean up any trailing binary artifacts
    source = source.rstrip('\x00').rstrip()
    
    print(f"\nExtracted source: {len(source)} chars, {source.count(chr(10))} lines")
    
    # Check for key classes
    for pattern in ['FarmBoundaryDrawingScreen', 'BoundaryPainter', '_fetchGeeScan', 
                    'YoloBoundingBoxPainter', 'GoogleMap(', 'class GeoKisanSubsystemPage']:
        if pattern in source:
            print(f"  FOUND: {pattern}")
        else:
            print(f"  MISSING: {pattern}")
    
    # Write the extracted source
    with open('recovered_main_dart.txt', 'w', encoding='utf-8') as f:
        f.write(source)
    print(f"\nSaved to recovered_main_dart.txt")
else:
    print("Could not find import statement in app.dill")
    
    # Try alternative: search for class definitions
    class_pattern = b'class GeoKisanApp extends StatefulWidget'
    class_idx = data.find(class_pattern)
    print(f"GeoKisanApp class found at: {class_idx}")
    
    if class_idx >= 0:
        # Search backwards for import
        search_back = data[max(0, class_idx - 5000):class_idx]
        imp_in_back = search_back.rfind(b'import ')
        if imp_in_back >= 0:
            real_start = max(0, class_idx - 5000) + imp_in_back
            print(f"Found import at {real_start}")
