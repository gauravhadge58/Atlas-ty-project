import pdfplumber
from services.common import normalize_text
from services.bom_extractor import _safe_cell_str

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    print(f"Total rows: {len(extracted)}\n")
    
    # Look for rows with "19" and "50830513" pattern
    for i, row in enumerate(extracted):
        row_text = " | ".join([_safe_cell_str(cell) for cell in row if cell])
        if "50830513" in row_text or ("19" in row_text and "REST BLOCK" in row_text):
            print(f"Row {i}: {row}")
            print()
