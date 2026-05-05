#!/usr/bin/env python3
"""Debug script to understand why extraction is failing"""

import pdfplumber
import re
from services.common import normalize_part_number

pdf_path = 'TDK040023_Lift aid of IXL1500 stator OP10.pdf'

_PART_NUMBER_RE = re.compile(
    r"^(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for page_idx in range(1, min(3, len(pdf.pages))):
        print(f"\n{'='*80}")
        print(f"PAGE {page_idx}")
        print('='*80)
        
        page = pdf.pages[page_idx]
        text = page.extract_text() or ""
        
        if not text:
            print("  No text extracted")
            continue
        
        print(f"Text length: {len(text)} chars")
        
        # Show first 500 chars
        print("\nFirst 500 chars:")
        print(text[:500])
        
        # Search for PART NUMBER
        text_u = text.upper()
        if "PART NUMBER" in text_u:
            print("\n✓ 'PART NUMBER' found in text")
            
            # Try regex
            matches = list(_PART_NUMBER_RE.finditer(text_u))
            print(f"\nRegex matches: {len(matches)}")
            
            for i, m in enumerate(matches[:5]):
                pn_raw = m.group("part") or ""
                pn = normalize_part_number(pn_raw)
                print(f"  Match {i+1}: '{pn_raw}' -> normalized: '{pn}'")
                print(f"    Full match: '{m.group(0)}'")
        else:
            print("\n✗ 'PART NUMBER' NOT found in text")
        
        # Also check for numbered format
        if re.search(r'\d+\.\s*PART\s*NUMBER', text_u):
            print("\n✓ Numbered format 'X. PART NUMBER' found")
            
            # Extract those lines
            for line in text.splitlines():
                if re.search(r'\d+\.\s*PART\s*NUMBER', line, re.IGNORECASE):
                    print(f"  Line: '{line}'")
