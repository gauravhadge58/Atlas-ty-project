from services.bom_extractor import extract_bom_from_page1

bom_rows, _ = extract_bom_from_page1("../TDK040023_Lift aid of IXL1500 stator OP10.pdf")

print("BOM from Page 1:")
print(f"{'Part Number':<20} {'Description':<40} {'Qty':<5}")
print("="*70)
for row in bom_rows:
    part = row.get('part_number', 'N/A')
    desc = row.get('description', 'N/A')
    qty = row.get('qty', 'N/A')
    print(f"{part:<20} {desc:<40} {qty:<5}")
