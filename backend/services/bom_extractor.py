import pdfplumber
from typing import Any, Dict, List, Tuple

from .common import normalize_part_number, normalize_text, parse_int, parse_qty


def _safe_cell_str(cell: Any) -> str:
    if cell is None:
        return ""
    return str(cell)


def _find_header_indexes(header_row: List[str]) -> Tuple[int, int, int, int]:
    """
    Try to locate BOM columns in a header row.
    Fallback to common layout:
    - item: 0
    - part_number: 1
    - description: 2
    - qty: last
    """
    normalized = [normalize_text(c) for c in header_row]
    item_col = 0
    part_col = 1
    desc_col = 2
    qty_col = len(header_row) - 1

    for i, h in enumerate(normalized):
        if not h:
            continue
        if "ITEM" in h:
            item_col = i
        if ("PART" in h and "NUMBER" in h) or h == "PARTNUMBER" or "PART#" in h:
            part_col = i
        if "DESCRIPTION" in h or h == "DESC":
            desc_col = i
        if "QTY" in h or h == "QUANTITY":
            qty_col = i
    return item_col, part_col, desc_col, qty_col


def _part_number_plausible(part_number: str) -> bool:
    pn = normalize_part_number(part_number)
    if not pn:
        return False
    if "COPYRIGHT" in pn or "CONFIDENTIAL" in pn:
        return False
    # Part numbers usually include digits.
    return any(ch.isdigit() for ch in pn) and len(pn) >= 2


def _table_score(extracted_rows: List[List[Any]]) -> int:
    """
    Score a table candidate by how much it looks like a BOM.
    """
    if not extracted_rows:
        return 0

    score = 0

    # Consider up to first 8 rows for header/body hints.
    for row in extracted_rows[:8]:
        joined = normalize_text(" ".join(_safe_cell_str(c) for c in row))
        if "ITEM" in joined:
            score += 2
        if ("PART" in joined and "NUMBER" in joined) or "PART#" in joined or "PARTNUMBER" in joined:
            score += 3
        if "DESCRIPTION" in joined:
            score += 3
        if "QTY" in joined or "QUANTITY" in joined:
            score += 2

    # Additional plausibility for part number-like cells.
    plausible_cells = 0
    for row in extracted_rows[:15]:
        for cell in row[:8]:
            pn = normalize_part_number(_safe_cell_str(cell))
            if _part_number_plausible(pn):
                plausible_cells += 1
    score += min(plausible_cells, 12)

    return score


def _parse_bom_from_text_lines(page_text: str) -> List[Dict[str, Any]]:
    """
    Fallback BOM parsing using a simple heuristic:
    item + part_number + description + qty (qty must be the last token).
    """
    lines = [ln.strip() for ln in (page_text or "").splitlines() if ln.strip()]
    bom_rows: List[Dict[str, Any]] = []

    for ln in lines:
        toks = ln.split()
        if len(toks) < 4:
            continue
        if not toks[0].isdigit():
            continue
        item = parse_int(toks[0])

        part_number_raw = toks[1]
        pn = normalize_part_number(part_number_raw)
        if not _part_number_plausible(pn):
            continue

        qty_raw = toks[-1]
        if not qty_raw.isdigit():
            continue
        qty = int(qty_raw)

        description = normalize_text(" ".join(toks[2:-1]))
        bom_rows.append(
            {
                "item": item if item is not None else len(bom_rows) + 1,
                "part_number": pn,
                "description": description,
                "qty": qty,
            }
        )

    # Deduplicate by (item, part_number).
    dedup: Dict[Tuple[Any, str], Dict[str, Any]] = {}
    for r in bom_rows:
        dedup[(r.get("item"), r.get("part_number"))] = r
    out = list(dedup.values())
    return out


def extract_bom_from_page1(pdf_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Extract BOM rows from page 1 of the drawing PDF.

    Returns:
      - bom_rows: [{item, part_number, description, qty, _row_y}]
      - annotation_context: {table_x0, table_x1, table_y0, table_y1, page_width, page_height, row_height_guess}
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        page_height = float(page.height)
        page_width = float(page.width)

        tables = page.find_tables()
        if not tables:
            raise ValueError("No table found on page 1 (BOM).")

        # Pick the table candidate that best matches BOM header keywords.
        best_table = None
        best_score = -1
        best_extracted: List[List[Any]] = []
        for t in tables:
            try:
                candidate_extracted = t.extract() or []
            except Exception:
                candidate_extracted = []
            sc = _table_score(candidate_extracted)
            if sc > best_score:
                best_score = sc
                best_table = t
                best_extracted = candidate_extracted

        table = best_table if best_table is not None else tables[0]
        extracted = best_extracted or []

        table_bbox = getattr(table, "bbox", None) or (0, 0, page_width, page_height)
        table_top = float(table_bbox[1])
        table_bottom = float(table_bbox[3])
        table_left = float(table_bbox[0])
        table_right = float(table_bbox[2])

        # Attempt structured table parsing first.
        bom_rows: List[Dict[str, Any]] = []
        if extracted:
            header_idx = None
            for i, row in enumerate(extracted):
                joined = normalize_text(" ".join(_safe_cell_str(c) for c in row))
                if ("PART" in joined and "NUMBER" in joined and "DESCRIPTION" in joined) or (
                    "PART" in joined and "NUMBER" in joined and "QTY" in joined
                ):
                    header_idx = i
                    break
            header_idx = header_idx if header_idx is not None else 0

            header_row = [normalize_text(_safe_cell_str(c)) for c in extracted[header_idx]]
            max_cols = max(len(r) for r in extracted) if extracted else 0
            header_row = header_row + [""] * (max_cols - len(header_row))
            item_col, part_col, desc_col, qty_col = _find_header_indexes(header_row)

            data_rows = extracted[header_idx + 1 :]
            row_count = len(data_rows)
            row_height_guess = (table_bottom - table_top) / max(row_count, 1)

            # pdfplumber table row bboxes sometimes exist; use them if present.
            row_bboxes: List[Tuple[float, float]] = []
            for r in getattr(table, "rows", []):
                bbox = getattr(r, "bbox", None)
                if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                    row_bboxes.append((float(bbox[1]), float(bbox[3])))

            for i, row in enumerate(data_rows):
                row = list(row) + [""] * (max_cols - len(row))
                item_val = parse_int(row[item_col]) if item_col < len(row) else None
                part_number_raw = normalize_text(_safe_cell_str(row[part_col])) if part_col < len(row) else ""
                part_number = normalize_part_number(part_number_raw)
                description = normalize_text(_safe_cell_str(row[desc_col])) if desc_col < len(row) else ""
                qty = parse_qty(_safe_cell_str(row[qty_col])) if qty_col < len(row) else None

                if not part_number or not _part_number_plausible(part_number):
                    continue

                extracted_row_index = header_idx + 1 + i
                y_top = None
                y_bottom = None
                if extracted_row_index < len(row_bboxes) and row_bboxes:
                    y_top, y_bottom = row_bboxes[extracted_row_index]
                if y_top is None or y_bottom is None:
                    y_top = table_top + i * row_height_guess
                    y_bottom = y_top + row_height_guess

                bom_rows.append(
                    {
                        "item": item_val if item_val is not None else i + 1,
                        "part_number": part_number,
                        "description": description,
                        "qty": qty if qty is not None else 1,
                        "_row_y": (float(y_top) + float(y_bottom)) / 2.0,
                    }
                )

        plausible_count = sum(1 for r in bom_rows if _part_number_plausible(r.get("part_number", "")))
        # If the structured parse still looks like garbage (title block/copyright), fallback to text lines.
        if not bom_rows or plausible_count < 2:
            text = page.extract_text() or ""
            parsed_rows = _parse_bom_from_text_lines(text)
            if not parsed_rows:
                raise ValueError("Failed to extract BOM rows from page 1.")

            row_height_guess = (table_bottom - table_top) / max(len(parsed_rows), 1)
            bom_rows = []
            for i, r in enumerate(parsed_rows):
                y_top = table_top + i * row_height_guess
                y_bottom = y_top + row_height_guess
                r["_row_y"] = (float(y_top) + float(y_bottom)) / 2.0
                bom_rows.append(r)

        if not bom_rows:
            raise ValueError("No BOM rows found on page 1.")

        row_height_guess = (table_bottom - table_top) / max(len(bom_rows), 1)

        # Some drawings number BOM items bottom-to-top (item `1` at the bottom,
        # highest item at the top). Our `_row_y` computation is based on the
        # table's extracted row order (usually top-to-bottom), so we detect
        # whether the "top row" currently has the highest item number.
        # If not, flip all `_row_y` values within the table bbox.
        items_with_y = [(r.get("item"), r.get("_row_y")) for r in bom_rows if isinstance(r.get("item"), int)]
        if items_with_y:
            min_y_item, _ = min(items_with_y, key=lambda t: t[1] if t[1] is not None else float("inf"))
            max_y_item, _ = max(items_with_y, key=lambda t: t[1] if t[1] is not None else float("-inf"))
            if isinstance(min_y_item, int) and isinstance(max_y_item, int) and min_y_item < max_y_item:
                for r in bom_rows:
                    r["_row_y"] = (table_top + table_bottom) - float(r["_row_y"])

        annotation_context = {
            "table_x0": table_left,
            "table_x1": table_right,
            "table_y0": table_top,
            "table_y1": table_bottom,
            "page_width": page_width,
            "page_height": page_height,
            "row_height_guess": float(row_height_guess),
        }
        return bom_rows, annotation_context

