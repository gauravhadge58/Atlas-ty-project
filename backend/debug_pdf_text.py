"""Debug PDF text extraction to see what format the part numbers are in"""
import pdfplumber
import re

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"

_PART_NUMBER_RE = re.compile(
    r"^PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

with pdfplumber.open(pdf_path) as pdf:
    print(f"PDF has {len(pdf.pages)} pages\n")
    
    # Check pages 2-5 for part number patterns
    for page_idx in range(2, min(6, len(pdf.pages))):
        page = pdf.pages[page_idx]
        text = page.extract_text() or ""
        
        print(f"=== PAGE {page_idx} ===")
        
        # Look for lines containing "PART NUMBER"
        lines_with_part = [line for line in text.split('\n') if 'PART NUMBER' in line.upper()]
        
        if lines_with_part:
            print(f"Found {len(lines_with_part)} lines with 'PART NUMBER':")
            for line in lines_with_part[:5]:
                print(f"  '{line}'")
                # Try to match with regex
                match = _PART_NUMBER_RE.search(line)
                if match:
                    print(f"    ✓ MATCHED: {match.group('part')}")
                else:
                    print(f"    ✗ NO MATCH")
        else:
            print("No 'PART NUMBER' found on this page")
        
        print()
        
        # Show first 500 chars of text to understand format
        if page_idx == 2:
            print("First 500 chars of page 2:")
            print(text[:500])
            print()
