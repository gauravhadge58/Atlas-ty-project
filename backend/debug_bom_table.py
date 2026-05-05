import pdfplumber

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    print(f"Found {len(tables)} tables on page 1\n")
    
    for idx, table in enumerate(tables):
        print(f"=== TABLE {idx + 1} ===")
        extracted = table.extract()
        print(f"Rows: {len(extracted)}")
        print()
        
        for i, row in enumerate(extracted):
            print(f"Row {i}: {row}")
        print()
