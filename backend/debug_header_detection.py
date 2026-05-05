import pdfplumber
from services.common import normalize_text
from services.bom_extractor import _safe_cell_str, _find_header_indexes

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    # Find header using same logic as bom_extractor
    header_idx = None
    for i, row in enumerate(extracted):
        joined = normalize_text(" ".join(_safe_cell_str(c) for c in row))
        if ("PART" in joined and "NUMBER" in joined and "DESCRIPTION" in joined) or (
            "PART" in joined and "NUMBER" in joined and "QTY" in joined
        ):
            print(f"Found header at row {i}: {joined[:100]}")
            header_idx = i
            break
    
    print(f"\nHeader index: {header_idx}")
    print(f"Data rows would be: {header_idx + 1} to {len(extracted)}")
    print(f"\nBut actual BOM data is in rows 14-22 (BEFORE the header!)")
    print("\nThis is a bottom-to-top BOM where items are listed above the header.")
