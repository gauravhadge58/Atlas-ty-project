from services.drawing_extractor import extract_part_materials_from_pages
from services.material_validator import validate_materials

# Extract data for TDK040023 PDF
pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'
part_details = extract_part_materials_from_pages(pdf_path)
part_keys = set(part_details.keys())

# Check parts C00 and C02
for part_num in ['TDK040023-C00', 'TDK040023-C02']:
    if part_num in part_details:
        details = part_details[part_num]
        print(f'\n{part_num}:')
        print(f'  material_code: "{details.get("material_code", "")}"')
        print(f'  material_name: "{details.get("material_name", "")}"')
        print(f'  finish: "{details.get("finish", "")}"')
        print(f'  heat_treatment: "{details.get("heat_treatment", "")}"')

# Run validation
validation_results = validate_materials(part_keys, part_details)
print('\n\nValidation Results:')
for r in validation_results:
    if r['part_number'] in ['TDK040023-C00', 'TDK040023-C02']:
        print(f'\n{r["part_number"]}:')
        print(f'  Material: {r["material"]["status"]} (actual: "{r["material"]["actual"]}")')
        print(f'  Finish: {r["finish"]["status"]} (actual: "{r["finish"]["actual"]}")')
        print(f'  Heat: {r["heat"]["status"]}')
