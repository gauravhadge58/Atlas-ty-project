#!/usr/bin/env python3
import pdfplumber
import re
from services.common import normalize_part_number, normalize_text

pdf_path = 'TDK040023_Lift aid of IXL1500 stator OP10.pdf'

_PART_NUMBER_RE = re.compile(
    r"^(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

with pdfplumber.open(pdf_path) as pdf:
    page_count = len(pdf.pages)
    print(f"Total pages: {page_count}")
    
    all_parts = {}
    
    for page_idx in range(1, page_count):
        page = pdf.pages[page_idx]
        text = page.extract_text() or ""
        
        if not text:
            continue
        
        text_u = text.upper()
        matches = list(_PART_NUMBER_RE.finditer(text_u))
        
        if matches:
            print(f"\nPage {page_idx}: {len(matches)} matches")
            for m in matches:
                pn_raw = m.group("part") or ""
                
                # Apply cleanup logic
                pn_raw_norm = normalize_text(pn_raw)
                pn_raw_norm_trimmed = re.split(
                    r"\b(?:NOTE|MATERIAL|FINISH|HARDENED|TEMPERED|DESCRIPTION|PART)\b",
                    pn_raw_norm,
                    maxsplit=1,
                )[0].strip()
                pn_raw_norm_trimmed = re.sub(r'\s+\d+\.$', '', pn_raw_norm_trimmed).strip()
                part_match = re.match(r'^([A-Z]+\d+[-/][A-Z0-9]+)', pn_raw_norm_trimmed)
                if part_match:
                    pn_raw_norm_trimmed = part_match.group(1)
                
                pn = normalize_part_number(pn_raw_norm_trimmed)
                
                print(f"  Raw: '{pn_raw}' -> Cleaned: '{pn_raw_norm_trimmed}' -> Normalized: '{pn}'")
                
                if pn:
                    all_parts[pn] = page_idx

print(f"\n\nTotal unique parts: {len(all_parts)}")
print("Parts:")
for pn in sorted(all_parts.keys()):
    print(f"  {pn} (page {all_parts[pn]})")
