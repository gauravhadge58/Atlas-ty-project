import pdfplumber
import re

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for i in range(1, min(10, len(pdf.pages))):
        print(f"=== PAGE {i+1} (index {i}) ===")
        text = pdf.pages[i].extract_text() or ""
        
        has_part_number = "PART NUMBER" in text.upper()
        has_tdk = "TDK040023" in text
        
        # Find all TDK part numbers
        pn_matches = re.findall(r'TDK040023-[A-Z0-9]+', text, re.IGNORECASE)
        
        print(f"  Has 'PART NUMBER': {has_part_number}")
        print(f"  Has 'TDK040023': {has_tdk}")
        print(f"  Found part numbers: {pn_matches}")
        
        # Show snippet around PART NUMBER if it exists
        if has_part_number:
            idx = text.upper().find("PART NUMBER")
            snippet = text[max(0, idx-50):min(len(text), idx+200)]
            print(f"  Snippet: ...{snippet}...")
        
        print()
