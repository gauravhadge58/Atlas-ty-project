#!/usr/bin/env python3
import re
import pdfplumber

_PART_NUMBER_RE = re.compile(
    r"(?:^|(?<=\s))(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})(?=\s+\d+\.\s+[A-Z]|\s*$)",
    flags=re.IGNORECASE | re.MULTILINE,
)

pdf = pdfplumber.open('TDK040023_Lift aid of IXL1500 stator OP10.pdf')
text = pdf.pages[7].extract_text()

print("Page 7 text (lines 40-55):")
lines = text.splitlines()
for i in range(40, min(55, len(lines))):
    print(f"{i}: {lines[i]}")

print("\n\nTesting regex on page 7:")
text_u = text.upper()
matches = list(_PART_NUMBER_RE.finditer(text_u))
print(f"Found {len(matches)} matches")
for m in matches:
    print(f"  Match: '{m.group('part')}'")
    print(f"  Full: '{m.group(0)}'")
