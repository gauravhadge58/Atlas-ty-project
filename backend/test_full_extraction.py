"""Test full extraction pipeline with TDK040023 PDF"""
from services.drawing_extractor import extract_part_materials_from_pages
import pdfplumber

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"

# First, check how many pages the PDF has
with pdfplumber.open(pdf_path) as pdf:
    print(f"PDF has {len(pdf.pages)} pages")
    print()

# Try different start page indices
for start_page in [0, 1, 2]:
    print(f"Trying start_page_index={start_page}:")
    result = extract_part_materials_from_pages(pdf_path, start_page)
    print(f"  Parts found: {len(result)}")
    if result:
        print(f"  Part numbers: {list(result.keys())[:3]}")
    print()

# Use the correct start page
result = extract_part_materials_from_pages(pdf_path, 0)
if result:
    print(f"Full extraction with start_page_index=0:")
    print(f"Total parts: {len(result)}")
    print()
    
    for part_num, data in sorted(result.items())[:3]:
        print(f"{part_num}:")
        print(f"  Material: {data.get('material_name', '')}")
        print(f"  Finish: {data.get('finish', '')}")
        print(f"  Heat Treatment: {data.get('heat_treatment', '')[:60]}...")
        print()
