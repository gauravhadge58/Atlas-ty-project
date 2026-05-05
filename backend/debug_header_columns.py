import pdfplumber
from services.common import normalize_text
from services.bom_extractor import _safe_cell_str

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    header_row = extracted[23]
    
    print("Header row (row 23):")
    for i, cell in enumerate(header_row):
        if cell:
            print(f"  Column {i}: '{cell}'")
