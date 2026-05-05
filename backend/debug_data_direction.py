import pdfplumber
from services.common import normalize_text
from services.bom_extractor import _safe_cell_str, _find_header_indexes

pdf_path = '../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    
    table = tables[0]
    extracted = table.extract()
    
    # Find header
    header_idx = None
    for i, row in enumerate(extracted):
        joined = normalize_text(" ".join(_safe_cell_str(c) for c in row))
        has_part_or_item = "PART" in joined or ("PA" in joined and "RT" in joined) or "ITEM" in joined
        has_number = "NUMBER" in joined
        has_description = "DESCRIPTION" in joined or "DESC" in joined
        has_qty = "QTY" in joined or "QUANTITY" in joined
        
        if (has_part_or_item and has_number and has_description) or (
            has_part_or_item and has_number and has_qty
        ):
            header_idx = i
            break
    
    header_idx = header_idx if header_idx is not None else 0
    print(f"Header index: {header_idx}")
    
    header_row = [normalize_text(_safe_cell_str(c)) for c in extracted[header_idx]]
    max_cols = max(len(r) for r in extracted) if extracted else 0
    header_row = header_row + [""] * (max_cols - len(header_row))
    item_col, part_col, desc_col, qty_col = _find_header_indexes(header_row)
    
    print(f"Column indexes: item={item_col}, part={part_col}, desc={desc_col}, qty={qty_col}")
    
    data_rows_after = extracted[header_idx + 1 :]
    data_rows_before = extracted[:header_idx] if header_idx > 0 else []
    
    print(f"\nRows after header: {len(data_rows_after)}")
    print(f"Rows before header: {len(data_rows_before)}")
    
    def count_plausible_rows(rows):
        count = 0
        for row in rows:
            if len(row) > part_col:
                pn_raw = normalize_text(_safe_cell_str(row[part_col]))
                if pn_raw and len(pn_raw) > 3:
                    count += 1
                    print(f"  Found plausible: '{pn_raw}'")
        return count
    
    print(f"\nChecking rows after header (first 15):")
    plausible_after = count_plausible_rows(data_rows_after[:15])
    print(f"Plausible after: {plausible_after}")
    
    print(f"\nChecking rows before header (last 15):")
    plausible_before = count_plausible_rows(data_rows_before[-15:])
    print(f"Plausible before: {plausible_before}")
    
    if plausible_before > plausible_after and plausible_before > 0:
        print(f"\nUsing rows BEFORE header")
    else:
        print(f"\nUsing rows AFTER header")
