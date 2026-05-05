import pdfplumber
import re
from services.common import normalize_part_number, normalize_text

# Regex patterns from drawing_extractor.py
_REGEX_PART_DESC = re.compile(
    r"PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80}?)\s*"
    r"DESCRIPTION\s*[:\-]?\s*(?P<desc>.+?)"
    r"(?=\s*PART\s*NUMBER\s*[:\-]?|\s*$)",
    flags=re.IGNORECASE | re.DOTALL,
)

_REGEX_PART_NOTES = re.compile(
    r"NOTES?\s*:\s*\d+\.\s*PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})",
    flags=re.IGNORECASE,
)

def analyze_pdf(pdf_path):
    print(f'\n{"="*80}')
    print(f'PDF: {pdf_path.split("/")[-1]}')
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        print(f'Total pages: {page_count}')
        
        # Track parts found on each page
        parts_by_page = {}
        
        for page_idx in range(1, page_count):  # Start from page 1 (skip BOM page 0)
            page = pdf.pages[page_idx]
            try:
                text = page.extract_text() or ""
            except Exception as e:
                print(f"Page {page_idx}: Text extraction failed: {e}")
                continue
            
            if not text:
                continue
            
            text_norm = normalize_text(text)
            
            if "PART NUMBER" not in text_norm:
                continue
            
            # Try primary pattern
            matches = list(_REGEX_PART_DESC.finditer(text_norm))
            if not matches:
                # Try fallback pattern
                matches = list(_REGEX_PART_NOTES.finditer(text_norm))
            
            if matches:
                parts_on_page = []
                for m in matches:
                    pn_raw = m.group("part") or ""
                    pn_raw_norm = normalize_text(pn_raw)
                    
                    # Clean up
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
                    
                    if pn and any(ch.isdigit() for ch in pn):
                        parts_on_page.append(pn)
                
                if parts_on_page:
                    parts_by_page[page_idx] = parts_on_page
                    print(f'\nPage {page_idx + 1} (index {page_idx}): Found {len(parts_on_page)} parts')
                    for part in parts_on_page:
                        print(f'  - {part}')
        
        print(f'\n{"="*80}')
        print(f'Summary: Found parts on {len(parts_by_page)} pages (excluding BOM page 0)')
        total_parts = sum(len(parts) for parts in parts_by_page.values())
        print(f'Total parts extracted from pages 1+: {total_parts}')
        print("="*80)

# Test all three PDFs
pdfs = [
    '../TDQ300162  1  FIXTURES FOR HYDRAULIC TOOLING  Released  VIN-WIP.pdf',
    '../TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf',
    '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'
]

for pdf_path in pdfs:
    try:
        analyze_pdf(pdf_path)
    except Exception as e:
        print(f'Error analyzing {pdf_path}: {e}')
