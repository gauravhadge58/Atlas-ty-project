from services.drawing_extractor import extract_part_materials_from_pages
from services.material_validator import validate_materials
import json

# Extract data for TDK040023 PDF
pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'
part_details = extract_part_materials_from_pages(pdf_path)
part_keys = set(part_details.keys())

# Run validation
validation_results = validate_materials(part_keys, part_details)

print("All parts with their material/finish data and validation status:\n")
for r in sorted(validation_results, key=lambda x: x['part_number']):
    details = part_details.get(r['part_number'], {})
    mat_code = details.get('material_code', '')
    mat_name = details.get('material_name', '')
    finish = details.get('finish', '')
    
    print(f"{r['part_number']}:")
    print(f"  Extracted: mat_code='{mat_code}', mat_name='{mat_name}', finish='{finish}'")
    print(f"  Validation: Material={r['material']['status']}, Finish={r['finish']['status']}, Heat={r['heat']['status']}")
    print()
