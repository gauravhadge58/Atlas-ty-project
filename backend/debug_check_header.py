import pdfplumber
from services.common import normalize_text
from services.bom_extractor import _safe_cell_str

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    # Check row 23 which should be the header
    print("Row 23 (expected header):")
    print(extracted[23])
    print()
    
    joined = normalize_text(" ".join(_safe_cell_str(c) for c in extracted[23]))
    print(f"Normalized joined text: '{joined}'")
    print()
    
    print(f"'PART' in joined: {'PART' in joined}")
    print(f"'NUMBER' in joined: {'NUMBER' in joined}")
    print(f"'DESCRIPTION' in joined: {'DESCRIPTION' in joined}")
    print(f"'QTY' in joined: {'QTY' in joined}")
