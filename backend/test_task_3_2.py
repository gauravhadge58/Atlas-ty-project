"""Quick test for Task 3.2 heat treatment extraction"""
from services.drawing_extractor import extract_part_materials_from_pages

pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"
result = extract_part_materials_from_pages(pdf_path, 1)

print(f"Parts found: {len(result)}")
print()

for part_num, data in sorted(result.items())[:5]:
    heat = data.get("heat_treatment", "")
    material = data.get("material_name", "")
    finish = data.get("finish", "")
    print(f"{part_num}:")
    print(f"  Material: {material}")
    print(f"  Finish: {finish}")
    print(f"  Heat Treatment: {heat}")
    print()
