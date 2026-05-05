import pdfplumber
from services.common import normalize_text, parse_int
from services.bom_extractor import _safe_cell_str, _part_number_plausible, _find_header_indexes

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    # Find header
    header_idx = 23
    header_row = [normalize_text(_safe_cell_str(c)) for c in extracted[header_idx]]
    max_cols = max(len(r) for r in extracted)
    header_row = header_row + [""] * (max_cols - len(header_row))
    item_col, part_col, desc_col, qty_col = _find_header_indexes(header_row)
    
    print(f"Columns: item={item_col}, part={part_col}")
    print()
    
    # Get data rows before header
    data_rows = extracted[:header_idx]
    
    # Check row 14 (item 8)
    row = data_rows[14]
    row = list(row) + [""] * (max_cols - len(row))
    
    item_cell = normalize_text(_safe_cell_str(row[item_col]))
    print(f"Row 14 - Item cell (col {item_col}): '{item_cell}'")
    
    if item_cell and ' ' in item_cell:
        item_val = parse_int(item_cell.split()[0])
    else:
        item_val = parse_int(item_cell)
    print(f"Item value: {item_val}")
    
    part_number_raw = normalize_text(_safe_cell_str(row[part_col]))
    print(f"Part number raw (col {part_col}): '{part_number_raw}'")
    
    if part_col > 0:
        prev_cell = normalize_text(_safe_cell_str(row[part_col - 1]))
        print(f"Previous cell (col {part_col-1}): '{prev_cell}'")
        
        if prev_cell and ' ' in prev_cell:
            parts = prev_cell.split()
            print(f"Previous cell parts: {parts}")
            
            if len(parts) == 2:
                potential_item = parse_int(parts[0])
                partial_digits = parts[1]
                print(f"Potential item: {potential_item}, Partial digits: '{partial_digits}'")
                print(f"Match: potential_item ({potential_item}) == item_val ({item_val})? {potential_item == item_val}")
                print(f"partial_digits.isdigit()? {partial_digits.isdigit()}")
                
                if potential_item == item_val and partial_digits.isdigit() and len(partial_digits) > 0:
                    reconstructed = partial_digits + part_number_raw
                    print(f"Reconstructed: '{reconstructed}'")
                    print(f"_part_number_plausible(reconstructed)? {_part_number_plausible(reconstructed)}")
                    print(f"_part_number_plausible(part_number_raw)? {_part_number_plausible(part_number_raw)}")
                    
                    if _part_number_plausible(reconstructed) and not _part_number_plausible(part_number_raw):
                        print("✓ Would use reconstructed part number")
                    else:
                        print("✗ Would NOT use reconstructed part number")
