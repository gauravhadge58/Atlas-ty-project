import pdfplumber
import sys

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "TDK040023_Lift aid of IXL1500 stator OP10.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    # Check pages 2-5 (indices 1-4)
    for i in range(1, min(6, len(pdf.pages))):
        print(f"{'='*80}")
        print(f"PAGE {i+1} (index {i})")
        print(f"{'='*80}")
        text = pdf.pages[i].extract_text() or ""
        
        # Show full text to see the actual format
        print(text)
        print(f"\n{'='*80}\n")
