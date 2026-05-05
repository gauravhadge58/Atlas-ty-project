#!/usr/bin/env python3
import re

_PART_NUMBER_RE = re.compile(
    r"(?:^|(?<=\s))(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80}?)(?=\s|$)",
    flags=re.IGNORECASE | re.MULTILINE,
)

line = "1. PART NUMBER: TDK040023-C02 NOTES:"
print(f"Testing line: '{line}'")
print(f"Line upper: '{line.upper()}'")

matches = list(_PART_NUMBER_RE.finditer(line.upper()))
print(f"\nFound {len(matches)} matches")
for m in matches:
    print(f"  Match: '{m.group('part')}'")
    print(f"  Full: '{m.group(0)}'")
    print(f"  Start: {m.start()}, End: {m.end()}")
