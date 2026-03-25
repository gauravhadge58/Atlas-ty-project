import pdfplumber
import re
from typing import Dict, List, Set, Tuple

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


_PART_NUMBER_RE = re.compile(
    r"^PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
_MATERIAL_RE = re.compile(r"^MATERIAL\s*:\s*(?P<val>.+)$", flags=re.IGNORECASE | re.MULTILINE)
_FINISH_RE = re.compile(r"^FINISH\s*:\s*(?P<val>.+)$", flags=re.IGNORECASE | re.MULTILINE)
_DESCRIPTION_RE = re.compile(
    r"^DESCRIPTION\s*[:\-]?\s*(?P<val>.+)$",
    flags=re.IGNORECASE | re.MULTILINE,
)

_HEAT_KEYS = ("HARDENED", "TEMPERED", "CASE HARDENING")
_HEAT_KEYWORD_RE = re.compile(r"\b(?:HARDENED|TEMPERED|CASE HARDENING)\b", flags=re.IGNORECASE)


def _extract_material_code_and_name(material_line: str) -> Tuple[str, str]:
    """
    Parse `MATERIAL:` content, expected shape:
      `EDM000136/ En8 NOTE HARDENED AND TEMPERED TO ...`

    Returns (edm_code, material_name)
    """
    if not material_line:
        return "", ""
    material_norm = normalize_text(material_line)
    # Extract the EDM code first.
    m = re.search(r"\b(EDM\d+)\b", material_norm, flags=re.IGNORECASE)
    if not m:
        return "", material_norm

    edm_code = m.group(1).upper()
    remainder = material_norm[m.end() :].lstrip(" /:-")
    # Some PDFs append "NOTE HARDENED ...", strip trailing keywords.
    remainder = re.split(r"\b(?:NOTE|HARDENED|TEMPERED|CASE HARDENING)\b", remainder, maxsplit=1)[0].strip()
    remainder = remainder.strip(" /:-")
    return edm_code, remainder


def _extract_finish_value(finish_line: str) -> str:
    """
    Extract finish value from e.g.:
      `FINISH: CHEMICAL BLACK HARDENED AND TEMPERED TO 60-70 ...`
    """
    if not finish_line:
        return ""
    finish_norm = normalize_text(finish_line)
    finish_only = re.split(r"\b(?:HARDENED|TEMPERED|CASE HARDENING)\b", finish_norm, maxsplit=1)[0].strip()
    return finish_only


def _extract_heat_treatment(block_text: str) -> str:
    """
    Extract full heat-treatment lines from within the part block.
    """
    if not block_text:
        return ""

    lines = []
    for ln in (block_text or "").splitlines():
        ln_u = ln.upper()
        if any(k in ln_u for k in _HEAT_KEYS):
            m = _HEAT_KEYWORD_RE.search(ln_u)
            if m:
                lines.append(ln[m.start() :].strip())
            else:
                lines.append(ln_u.strip())

    # Deduplicate while preserving order.
    seen: Set[str] = set()
    deduped: List[str] = []
    for l in lines:
        n = normalize_text(l)
        if n and n not in seen:
            seen.add(n)
            deduped.append(normalize_text(l))
    return "; ".join(deduped)


def extract_part_materials_from_pages(
    pdf_path: str,
    start_page_index: int = 1,
) -> Dict[str, Dict[str, str]]:
    """
    Extract MATERIAL/FINISH/HEAT fields for each detected `PART NUMBER` block.

    Returns:
      dict keyed by normalized `part_number`:
        {
          "<PART>": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "HARDENED AND TEMPERED TO 60-70 ..."
          },
          ...
        }
    """
    with pdfplumber.open(pdf_path) as pdf:
        out: Dict[str, Dict[str, str]] = {}

        page_count = len(pdf.pages)
        for page_idx in range(start_page_index, page_count):
            page = pdf.pages[page_idx]
            try:
                text = page.extract_text() or ""
            except Exception:
                continue
            if not text:
                continue

            # Find all part number spans in this page.
            text_u = text.upper()
            matches = list(_PART_NUMBER_RE.finditer(text_u))
            if not matches:
                continue

            for i, m in enumerate(matches):
                pn_raw = m.group("part") or ""
                pn = normalize_part_number(pn_raw)
                if not pn:
                    continue

                block_start = m.start()
                block_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                block_text = text[block_start:block_end]

                # MATERIAL / FINISH lines are usually line-based within the block.
                material_line = ""
                mm = _MATERIAL_RE.search(block_text)
                if mm:
                    material_line = mm.group("val") or ""
                finish_line = ""
                fm = _FINISH_RE.search(block_text)
                if fm:
                    finish_line = fm.group("val") or ""

                description_val = ""
                dm = _DESCRIPTION_RE.search(block_text)
                if dm:
                    description_val = dm.group("val") or ""

                # Parse fields.
                material_code, material_name = _extract_material_code_and_name(material_line)
                finish = _extract_finish_value(finish_line)
                heat_treatment = _extract_heat_treatment(block_text)

                if pn not in out:
                    out[pn] = {
                        "material_code": material_code,
                        "material_name": material_name,
                        "finish": finish,
                        "heat_treatment": heat_treatment,
                        "description": normalize_text(description_val),
                    }
                else:
                    # Merge best-effort (don't clobber previously extracted non-empty values).
                    if material_code and not out[pn].get("material_code"):
                        out[pn]["material_code"] = material_code
                    if material_name and not out[pn].get("material_name"):
                        out[pn]["material_name"] = material_name
                    if finish and not out[pn].get("finish"):
                        out[pn]["finish"] = finish
                    if heat_treatment and not out[pn].get("heat_treatment"):
                        out[pn]["heat_treatment"] = heat_treatment
                    if description_val and not out[pn].get("description"):
                        out[pn]["description"] = normalize_text(description_val)

        return out


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


