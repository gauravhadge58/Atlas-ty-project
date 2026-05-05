#!/usr/bin/env python3
import re
import pdfplumber

_PART_NUMBER_RE = re.compile(
    r"(?:^|(?<=\s))(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80}?)(?=\s|$)",
    flags=re.IGNORECASE | re.MULTILINE,
)

pdf = pdfplumber.open('TDK040023_Lift aid of IXL1500 stator OP10.pdf')
text = pdf.pages[7].extract_text()
text_u = text.upper()

# Find line 45
lines = text_u.splitlines()
line45 = lines[45] if len(lines) > 45 else ""
print(f"Line 45: '{line45}'")
print(f"Line 45 repr: {repr(line45)}")

# Test regex on line 45 alone
matches_line = list(_PART_NUMBER_RE.finditer(line45))
print(f"\nMatches on line 45 alone: {len(matches_line)}")
for m in matches_line:
    print(f"  '{m.group('part')}'")

# Test regex on full text
matches_full = list(_PART_NUMBER_RE.finditer(text_u))
print(f"\nMatches on full page text: {len(matches_full)}")
for m in matches_full:
    print(f"  '{m.group('part')}' at position {m.start()}")

# Check if line 45 starts at the beginning of a line in the full text
line45_start = text_u.find(line45)
print(f"\nLine 45 position in full text: {line45_start}")
if line45_start > 0:
    print(f"Character before line 45: {repr(text_u[line45_start-1])}")
