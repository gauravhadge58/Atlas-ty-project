#!/usr/bin/env python3
"""Quick verification script to check if the fix is working"""

from services.bom_extractor import extract_bom_from_page1
from services.drawing_extractor import extract_parts_from_pages
from services.matcher import match_bom

pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'

# Extract BOM
bom_rows, _ = extract_bom_from_page1(pdf_path)
print(f'BOM rows: {len(bom_rows)}')
for row in bom_rows:
    print(f"  {row['item']}: {row['part_number']} - {row['description']}")

# Extract parts from pages 2-10
extracted_parts = extract_parts_from_pages(pdf_path, start_page_index=1)
print(f'\nExtracted parts from pages 2-10: {sorted(extracted_parts)}')

# Match BOM
results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_parts)
print(f'\nMatching results:')
found_count = 0
missing_count = 0
for result in results:
    pn = result['part_number']
    status = result['status']
    print(f'  {pn}: {status}')
    if status == 'FOUND':
        found_count += 1
    elif status == 'MISSING':
        missing_count += 1

print(f'\nSummary: {found_count} FOUND, {missing_count} MISSING out of {len(results)} total')
