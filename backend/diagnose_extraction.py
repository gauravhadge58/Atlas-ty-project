"""Simple diagnostic to see what's being extracted"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.drawing_extractor import extract_part_materials_from_pages
import pdfplumber

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"

print("Checking PDF pages...")
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    # Check a few pages for text
    for i in range(min(3, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text() or ""
        print(f"\nPage {i} text length: {len(text)}")
        if "PART NUMBER" in text.upper():
            print(f"  ✓ Contains 'PART NUMBER'")
            # Show first occurrence
            idx = text.upper().find("PART NUMBER")
            print(f"  Context: {text[max(0, idx-20):idx+80]}")

print("\n" + "="*80)
print("Extracting materials...")
materials = extract_part_materials_from_pages(pdf_path, start_page_index=0)
print(f"Extracted {len(materials)} parts")
for pn, data in sorted(materials.items()):
    print(f"\n{pn}:")
    for k, v in data.items():
        print(f"  {k}: {v[:60] if v else '(empty)'}...")

print("\n" + "="*80)
print("Trying with start_page_index=1...")
materials = extract_part_materials_from_pages(pdf_path, start_page_index=1)
print(f"Extracted {len(materials)} parts")
for pn, data in sorted(materials.items()):
    print(f"\n{pn}:")
    for k, v in data.items():
        print(f"  {k}: {v[:60] if v else '(empty)'}...")
