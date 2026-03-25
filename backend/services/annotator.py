from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF


def _find_fontfile() -> str | None:
    # Common font locations on Windows; DejaVu often ships with Cursor/Python.
    candidates = [
        r"C:\Windows\Fonts\DejaVuSans.ttf",
        r"C:\Windows\Fonts\dejavusans.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Try local font (if user added it)
    local = Path(__file__).resolve().parent.parent / "fonts" / "DejaVuSans.ttf"
    if local.exists():
        return str(local)
    return None


def annotate_pdf(
    input_pdf_path: str,
    output_pdf_path: str,
    bom_rows: List[Dict[str, Any]],
    bom_results: List[Dict[str, Any]],
    annotation_context: Dict[str, float],
) -> None:
    """
    Annotate page 1 BOM table with:
      - Green ✔ for FOUND
      - Blue ⚙ for STANDARD
      - Red ✖ for MISSING

    Uses best-effort Y positions from bom_rows' internal _row_y values.
    """
    fontfile = _find_fontfile()

    doc = fitz.open(input_pdf_path)
    page = doc[0]

    table_x0 = float(annotation_context["table_x0"])
    table_x1 = float(annotation_context["table_x1"])

    # Put the symbol near the left side of the BOM table.
    # pdfplumber bbox ordering is not guaranteed, so normalize first.
    table_left = min(table_x0, table_x1)
    table_right = max(table_x0, table_x1)

    # Keep a small padding inside the table border.
    # This should place the marker slightly left of the `ITEM` numbers.
    x = table_left + 2

    # Symbol + colors
    status_to_symbol = {
        "FOUND": ("✔", (0.0, 0.7, 0.0)),
        "STANDARD": ("⚙", (0.1, 0.4, 1.0)),
        "MISSING": ("✖", (0.95, 0.0, 0.0)),
    }

    # Marker size: tuned so the symbols are clearly visible in the browser PDF viewer.
    fontsize = 24
    for i, (row, res) in enumerate(zip(bom_rows, bom_results)):
        status = res.get("status", "MISSING")
        symbol, color = status_to_symbol.get(status, status_to_symbol["MISSING"])
        y = float(row.get("_row_y", annotation_context["table_y0"]))
        # PyMuPDF uses baseline; shift upward so the glyph is centered around `row_y`.
        y_baseline = y - (fontsize * 0.28)
        if fontfile:
            page.insert_text(
                (x, y_baseline),
                symbol,
                fontsize=fontsize,
                fontfile=fontfile,
                color=color,
            )
        else:
            page.insert_text((x, y_baseline), symbol, fontsize=fontsize, color=color)

    os.makedirs(Path(output_pdf_path).parent, exist_ok=True)
    doc.save(output_pdf_path)
    doc.close()

