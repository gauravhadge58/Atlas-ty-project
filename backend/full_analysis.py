from services.drawing_extractor import extract_parts_from_pages, extract_part_materials_from_pages
from services.bom_extractor import extract_bom_from_page1
from services.matcher import match_bom

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"

print("="*80)
print("FULL ANALYSIS OF BOM VALIDATION")
print("="*80)

# 1. Extract BOM from page 1
print("\n1. BOM from Page 1:")
bom_rows, _ = extract_bom_from_page1(pdf_path)
print(f"   Total BOM items: {len(bom_rows)}")
for row in bom_rows:
    print(f"   - {row['part_number']}: {row['description']}")

# 2. Extract parts from pages 2-10
print("\n2. Parts extracted from pages 2-10 (index 1-9):")
extracted_parts = extract_parts_from_pages(pdf_path, start_page_index=1)
print(f"   Total parts extracted: {len(extracted_parts)}")
for part in sorted(extracted_parts):
    print(f"   - {part}")

# 3. Match BOM
print("\n3. BOM Matching Results:")
bom_results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_parts)
for result in bom_results:
    part = result['part_number']
    status = result['status']
    desc = result['description']
    print(f"   - {part:20} {status:10} {desc}")

# 4. Analysis
print("\n4. Analysis:")
print("   Parts in BOM but NOT extracted:")
bom_parts = {row['part_number'] for row in bom_rows}
missing_from_extraction = bom_parts - extracted_parts
for part in sorted(missing_from_extraction):
    # Find the BOM row for this part
    bom_row = next((r for r in bom_rows if r['part_number'] == part), None)
    if bom_row:
        print(f"   - {part}: {bom_row['description']}")

print("\n   Parts extracted but NOT in BOM:")
extra_in_extraction = extracted_parts - bom_parts
for part in sorted(extra_in_extraction):
    print(f"   - {part}")

print("\n" + "="*80)
