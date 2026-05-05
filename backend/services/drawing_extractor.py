import pdfplumber
import re
import logging
from typing import Dict, List, Set, Tuple

from .common import normalize_part_number, normalize_text

# Configure logging
logger = logging.getLogger(__name__)
# Set to WARNING level for production - only log warnings and errors
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


_REGEX_PART_DESC = re.compile(
    r"PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80}?)\s*"
    r"DESCRIPTION\s*[:\-]?\s*(?P<desc>.+?)"
    r"(?=\s*PART\s*NUMBER\s*[:\-]?|\s*$)",
    flags=re.IGNORECASE | re.DOTALL,
)

# Fallback pattern for notes-based format: "NOTES: 1. PART NUMBER: TDK040023-C02"
_REGEX_PART_NOTES = re.compile(
    r"NOTES?\s*:\s*\d+\.\s*PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})",
    flags=re.IGNORECASE,
)

_DESC_TRIM_SPLIT = re.compile(
    r"\b(?:MATERIAL|FINISH|NOTE|HARDENED|TEMPERED|SECTION|DRAWING|SIZE|SHEET|SCALE|PART)\b",
    flags=re.IGNORECASE,
)


_PART_NUMBER_RE = re.compile(
    r"(?:^|(?<=\s))(?:\d+\.\s*)?PART\s*NUMBER\s*[:\-]?\s*(?P<part>[A-Z0-9][A-Z0-9\-/\. ]{0,80})(?=\s|$)",
    flags=re.IGNORECASE | re.MULTILINE,
)
_MATERIAL_RE = re.compile(r"^(?:\d+\.\s*)?MATERIAL\s*:\s*(?P<val>.+?)(?:\s+\d+\.\s+[A-Z]|$)", flags=re.IGNORECASE | re.MULTILINE)
_FINISH_RE = re.compile(r"^(?:\d+\.\s*)?(SURFACE\s+)?FINISH\s*:\s*(?P<val>.+?)(?:\s+\d+\.\s+[A-Z]|$)", flags=re.IGNORECASE | re.MULTILINE)
_HEAT_TREATMENT_RE = re.compile(r"^(?:\d+\.\s*)?HEAT\s+TREATMENT\s*:\s*(?P<val>.+?)(?:\s+\d+\.\s+[A-Z]|$)", flags=re.IGNORECASE | re.MULTILINE)
_DESCRIPTION_RE = re.compile(
    r"^(?:\d+\.\s*)?(?:PART\s+)?DESCRIPTION\s*[:\-]?\s*(?P<val>.+)$",
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
            except Exception as e:
                logger.error(f"Page {page_idx}: Material extraction - text extraction failed: {e}")
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
                
                # Apply same cleanup logic as extract_parts_from_pages()
                pn_raw_norm = normalize_text(pn_raw)
                
                # Trim common label words from the end
                pn_raw_norm_trimmed = re.split(
                    r"\b(?:NOTE|MATERIAL|FINISH|HARDENED|TEMPERED|DESCRIPTION|PART)\b",
                    pn_raw_norm,
                    maxsplit=1,
                )[0].strip()
                
                # Remove trailing numbered list patterns like "2."
                pn_raw_norm_trimmed = re.sub(r'\s+\d+\.$', '', pn_raw_norm_trimmed).strip()
                
                # Extract just the part number pattern: PREFIX-SUFFIX
                part_match = re.match(r'^([A-Z]+\d+[-/][A-Z0-9]+)', pn_raw_norm_trimmed)
                if part_match:
                    pn_raw_norm_trimmed = part_match.group(1)
                
                pn = normalize_part_number(pn_raw_norm_trimmed)
                
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
                
                # Try regex match first for heat treatment (handles numbered format)
                heat_treatment = ""
                ht_match = _HEAT_TREATMENT_RE.search(block_text)
                if ht_match:
                    heat_treatment = normalize_text(ht_match.group("val") or "")
                else:
                    # Fall back to keyword-based extraction for backward compatibility
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
            except Exception as e:
                logger.error(f"Page {page_idx}: Text extraction failed: {e}")
                # Some PDFs can throw internal pdfminer exceptions during layout;
                # skip problematic pages rather than failing the whole run.
                continue
            
            if not text:
                continue
            
            text_norm = normalize_text(text)

            if "PART NUMBER" not in text_norm:
                continue

            matches = list(_REGEX_PART_DESC.finditer(text_norm))
            if not matches:
                # Try fallback pattern for notes-based format
                matches = list(_REGEX_PART_NOTES.finditer(text_norm))
            
            if not matches:
                # Log when PART NUMBER keyword exists but both regex patterns fail to match
                logger.warning(f"Page {page_idx}: 'PART NUMBER' found but no regex pattern matched")
                continue

            for match_idx, m in enumerate(matches):
                pn_raw = m.group("part") or ""
                
                pn_raw_norm = normalize_text(pn_raw)
                
                # OCR sometimes appends labels into the same capture (e.g. "...-01 NOTE ...").
                # Trim common label words from the end, including "PART" which appears in numbered lists.
                pn_raw_norm_trimmed = re.split(
                    r"\b(?:NOTE|MATERIAL|FINISH|HARDENED|TEMPERED|DESCRIPTION|PART)\b",
                    pn_raw_norm,
                    maxsplit=1,
                )[0].strip()
                
                # Additional cleanup: remove trailing numbered list patterns like "2." or "1."
                # This handles cases like "TDK040023-01 2." -> "TDK040023-01"
                pn_raw_norm_trimmed = re.sub(r'\s+\d+\.$', '', pn_raw_norm_trimmed).strip()
                
                # Extract just the part number pattern: typically "PREFIX-SUFFIX" where SUFFIX is alphanumeric
                # This handles cases like "TDK040023-A00 2-M12 TAP D.P25" -> "TDK040023-A00"
                # Part numbers typically follow pattern: LETTERS+DIGITS-ALPHANUMERIC (e.g., TDK040023-A00, TDK040023-01)
                part_match = re.match(r'^([A-Z]+\d+[-/][A-Z0-9]+)', pn_raw_norm_trimmed)
                if part_match:
                    pn_raw_norm_trimmed = part_match.group(1)
                
                pn = normalize_part_number(pn_raw_norm_trimmed)
                
                if pn and any(ch.isdigit() for ch in pn):
                    part_keys.add(pn)

        return part_keys
