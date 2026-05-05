"""Test N/A status for material validation"""
from services.bom_extractor import extract_bom_from_page1
from services.drawing_extractor import extract_parts_from_pages, extract_part_materials_from_pages
from services.material_validator import validate_materials_for_upload

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

# Extract BOM and parts
bom_rows, _ = extract_bom_from_page1(pdf_path)
extracted_part_keys = extract_parts_from_pages(pdf_path, start_page_index=1)
part_details = extract_part_materials_from_pages(pdf_path, start_page_index=1)

# Validate materials
validation_results = validate_materials_for_upload(extracted_part_keys, part_details)

print("Material Validation Results:")
print("="*80)

for result in validation_results['material_results']:
    pn = result['part_number']
    mat_status = result['material']['status']
    fin_status = result['finish']['status']
    heat_status = result['heat']['status']
    
    print(f"\nPart: {pn}")
    print(f"  Material: {mat_status} (actual: '{result['material']['actual']}')")
    print(f"  Finish: {fin_status} (actual: '{result['finish']['actual']}')")
    print(f"  Heat: {heat_status} (actual: '{result['heat']['actual']}')")

print("\n" + "="*80)
print("Status Summary:")
print("  N/A = Not Applicable (no data in PDF or no reference data)")
print("  PASS = Validation passed (matches reference)")
print("  FAIL = Validation failed (doesn't match reference)")
print("  MISSING = Required data is absent")
print("  WARNING = Similar but not exact match")
