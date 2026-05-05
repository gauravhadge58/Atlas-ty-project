import pdfplumber
from services.common import normalize_text, parse_int
from services.bom_extractor import _safe_cell_str, _part_number_plausible

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    # Find header
    header_idx = 23  # From debug output, we know the header is at row 23
    
    # Get data rows
    data_rows = extracted[header_idx + 1:]
    
    print(f"Analyzing {len(data_rows)} data rows after header...\n")
    
    # Assume part_col = 19, item_col = 18 based on header "EM PA RT NUMBER"
    part_col = 19
    item_col = 18
    
    for i, row in enumerate(data_rows[:10]):  # Check first 10 rows
        if len(row) <= part_col:
            continue
            
        item_val = parse_int(row[item_col]) if item_col < len(row) else None
        part_number_raw = normalize_text(_safe_cell_str(row[part_col])) if part_col < len(row) else ""
        prev_cell = normalize_text(_safe_cell_str(row[part_col - 1])) if part_col > 0 else ""
        
        print(f"Row {i}:")
        print(f"  prev_cell (col {part_col-1}): '{prev_cell}'")
        print(f"  part_number_raw (col {part_col}): '{part_number_raw}'")
        print(f"  item_val: {item_val}")
        
        if prev_cell and ' ' in prev_cell:
            parts = prev_cell.split()
            print(f"  prev_cell parts: {parts}")
            if len(parts) == 2:
                potential_item = parse_int(parts[0])
                partial_digits = parts[1]
                print(f"  potential_item: {potential_item}, partial_digits: '{partial_digits}'")
                print(f"  Match check: potential_item == item_val? {potential_item == item_val}")
                print(f"  partial_digits.isdigit()? {partial_digits.isdigit()}")
                
                if potential_item == item_val and partial_digits.isdigit():
                    reconstructed = partial_digits + part_number_raw
                    print(f"  Reconstructed: '{reconstructed}'")
                    print(f"  _part_number_plausible(reconstructed)? {_part_number_plausible(reconstructed)}")
                    print(f"  _part_number_plausible(part_number_raw)? {_part_number_plausible(part_number_raw)}")
        print()
