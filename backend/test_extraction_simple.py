#!/usr/bin/env python3
from services.drawing_extractor import extract_part_materials_from_pages

materials = extract_part_materials_from_pages('TDK040023_Lift aid of IXL1500 stator OP10.pdf', start_page_index=1)
print(f'Parts extracted: {len(materials)}')
print('Parts:')
for pn in sorted(materials.keys()):
    fields = materials[pn]
    print(f'  {pn}:')
    print(f'    Material: {fields.get("material_name", "Missing")}')
    print(f'    Finish: {fields.get("finish", "Missing")}')
    print(f'    Heat: {fields.get("heat_treatment", "Missing")[:50] if fields.get("heat_treatment") else "Missing"}')
