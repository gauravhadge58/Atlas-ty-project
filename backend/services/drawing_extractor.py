import pdfplumber
import re
from typing import Dict, List, Set

from .common import normalize_part_number, normalize_text


_REGEX_PART_DESC = re.compile(
    r"PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80}?)\s*"
    r"DESCRIPTION\s*[:\-]?\s*(?P<desc>.+?)"
    r"(?=\s*PART\s*NUMBER\s*[:\-]?|\s*$)",
    flags=re.IGNORECASE | re.DOTALL,
)

_DESC_TRIM_SPLIT = re.compile(
    r"\b(?:MATERIAL|FINISH|NOTE|HARDENED|TEMPERED|SECTION|DRAWING|SIZE|SHEET|SCALE)\b",
    flags=re.IGNORECASE,
)


def extract_parts_from_pages(pdf_path: str, start_page_index: int = 1) -> Set[str]:
    """
    Extract all PART NUMBER / DESCRIPTION occurrences from pages >= start_page_index.

    Returns:
      A set of normalized part number keys.
    """
    with pdfplumber.open(pdf_path) as pdf:
        part_keys: Set[str] = set()
        page_count = len(pdf.pages)

        for page_idx in range(start_page_index, page_count):
            page = pdf.pages[page_idx]
            try:
                text = page.extract_text() or ""
            except Exception:
                # Some PDFs can throw internal pdfminer exceptions during layout;
                # skip problematic pages rather than failing the whole run.
                continue
            if not text:
                continue
            text_norm = normalize_text(text)

            if "PART NUMBER" not in text_norm:
                continue

            for m in _REGEX_PART_DESC.finditer(text_norm):
                pn_raw = m.group("part") or ""
                pn_raw_norm = normalize_text(pn_raw)
                # OCR sometimes appends labels into the same capture (e.g. "...-01 NOTE ...").
                # Trim common label words from the end.
                pn_raw_norm = re.split(
                    r"\b(?:NOTE|MATERIAL|FINISH|HARDENED|TEMPERED|DESCRIPTION)\b",
                    pn_raw_norm,
                    maxsplit=1,
                )[0].strip()
                pn = normalize_part_number(pn_raw_norm)
                if pn and any(ch.isdigit() for ch in pn):
                    part_keys.add(pn)

    return part_keys

