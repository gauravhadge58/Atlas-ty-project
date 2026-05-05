from services.bom_extractor import extract_bom_from_page1

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'
bom_rows, annotation_context = extract_bom_from_page1(pdf_path)

print(f"Total BOM rows extracted: {len(bom_rows)}\n")

for row in bom_rows:
    print(f"Item: {row.get('item', 'N/A')}")
    print(f"  Part Number: {row.get('part_number', 'N/A')}")
    print(f"  Description: {row.get('description', 'N/A')}")
    print(f"  Qty: {row.get('qty', 'N/A')}")
    print()
