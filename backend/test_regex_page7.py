#!/usr/bin/env python3
import re

_MATERIAL_RE = re.compile(r"^(?:\d+\.\s*)?MATERIAL\s*:\s*(?P<val>.+?)(?:\s+\d+\.\s+[A-Z]|$)", flags=re.IGNORECASE | re.MULTILINE)
_FINISH_RE = re.compile(r"^(?:\d+\.\s*)?(SURFACE\s+)?FINISH\s*:\s*(?P<val>.+?)(?:\s+\d+\.\s+[A-Z]|$)", flags=re.IGNORECASE | re.MULTILINE)

# Test lines from page 7
test_lines = [
    "3. MATERIAL: SS400 2. PART DESCRIPTION: BRACKET PLATE",
    "4. SURFACE FINISH: BLACK OXIDE 3. MATERIAL: SS400",
]

for line in test_lines:
    print(f"\nLine: '{line}'")
    
    m_match = _MATERIAL_RE.search(line)
    if m_match:
        print(f"  MATERIAL match: '{m_match.group('val')}'")
    else:
        print("  MATERIAL: no match")
    
    f_match = _FINISH_RE.search(line)
    if f_match:
        print(f"  FINISH match: '{f_match.group('val')}'")
    else:
        print("  FINISH: no match")
