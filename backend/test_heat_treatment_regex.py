"""Test the heat treatment regex pattern directly"""

import sys
from pathlib import Path
import re

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.drawing_extractor import _HEAT_TREATMENT_RE
from services.common import normalize_text

print("Testing _HEAT_TREATMENT_RE pattern")
print("="*80)

test_cases = [
    "5. HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2",
    "HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2",
    "5.HEAT TREATMENT:HARDENED",
    "5.  HEAT TREATMENT:  HARDENED",
    "heat treatment: tempered",
    "10. HEAT TREATMENT: CASE HARDENING TO 0.5-0.8MM DEPTH",
]

for test in test_cases:
    match = _HEAT_TREATMENT_RE.search(test)
    if match:
        value = normalize_text(match.group("val") or "")
        print(f"✓ '{test}'")
        print(f"  → '{value}'")
    else:
        print(f"✗ '{test}' (no match)")
    print()

print("="*80)
print("Testing with multi-line block text (simulating actual usage)")
print("="*80)

block_text = """NOTES:
1. PART NUMBER: TDK040023-A01
2. PART DESCRIPTION: SHAFT
3. MATERIAL: SS400
4. SURFACE FINISH: BLACK OXIDE
5. HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2
"""

print("Block text:")
print(block_text)
print()

match = _HEAT_TREATMENT_RE.search(block_text)
if match:
    value = normalize_text(match.group("val") or "")
    print(f"✓ Heat treatment found: '{value}'")
else:
    print("✗ No heat treatment match found")
