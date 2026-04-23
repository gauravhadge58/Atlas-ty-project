from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from rapidfuzz import fuzz

from .common import normalize_text

try:
    from .material_db import get_reference_table as _db_get_reference_table
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False


_FINISH_SYNONYMS: Dict[str, str] = {
    # PDF often spells it like this.
    "CHEMICAL BLACK": "BLACKODISING",
}

_EDM_RE = re.compile(r"\b(EDM\d+)\b", flags=re.IGNORECASE)
_HEAT_RANGE_RE = re.compile(
    r"(?P<a>\d{1,3})\s*(?:-|–|—|TO)\s*(?P<b>\d{1,3})",
    flags=re.IGNORECASE,
)

_HEAT_KEYWORDS_RE = re.compile(r"\b(?:HARDENED|TEMPERED|CASE HARDENING)\b", flags=re.IGNORECASE)


def _load_reference_table() -> List[Dict[str, Any]]:
    """Load from SQLite (preferred) or fall back to the bundled JSON."""
    if _DB_AVAILABLE:
        try:
            return _db_get_reference_table()
        except Exception:
            pass
    # Fallback: direct JSON read
    ref_path = Path(__file__).resolve().parent.parent / "data" / "material_reference.json"
    with ref_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_code(value: Optional[str]) -> str:
    if not value:
        return ""
    value = normalize_text(value)
    # Some PDFs can have stray spaces/punctuation.
    value = value.replace(" ", "")
    return value


def _edm_numeric_key(edm_code: str) -> str:
    """
    Normalize EDM codes that differ only by leading zero padding.
    Example:
      - EDM000800 -> EDM 800
      - EDM0000800 -> EDM 800
    """
    if not edm_code:
        return ""
    m = re.search(r"\bEDM(\d+)\b", edm_code.upper())
    if not m:
        return _normalize_code(edm_code)
    digits = m.group(1)
    return str(int(digits)) if digits else ""


def _extract_edm_code(material_line: str) -> str:
    """
    Extract the EDM code from a `MATERIAL:` line.
    Example: `EDM000136/ EN8 ...` -> `EDM000136`
    """
    if not material_line:
        return ""
    m = _EDM_RE.search(material_line)
    return m.group(1).upper() if m else ""


def _extract_numeric_heat_range(heat_text: str) -> str:
    """
    Extract `a-b` numeric ranges from text like:
      - "HARDENED AND TEMPERED TO 60-70 kg/mm2"
      - "CASE HARDENING TO 55-85 HRC"
    """
    if not heat_text:
        return ""
    m = _HEAT_RANGE_RE.search(heat_text.upper())
    if not m:
        return ""
    return f"{int(m.group('a'))}-{int(m.group('b'))}"


def _normalize_finish(actual_finish: str) -> str:
    v = normalize_text(actual_finish)
    if not v:
        return ""
    for k, mapped in _FINISH_SYNONYMS.items():
        if k in v:
            return mapped
    return v


def _similar_finish(expected: str, actual: str) -> bool:
    expected_n = normalize_text(expected)
    actual_n = normalize_text(actual)
    if not expected_n or not actual_n:
        return False
    if expected_n == actual_n:
        return False  # exact match handled elsewhere
    # Substring is treated as "close but not exact".
    if expected_n in actual_n or actual_n in expected_n:
        return True
    # Fuzzy ratio for minor OCR differences.
    return fuzz.ratio(expected_n, actual_n) >= 85


def _worst_status(statuses: List[str]) -> str:
    # Ordering: FAIL > WARNING > MISSING > PASS
    if "FAIL" in statuses:
        return "FAIL"
    if "WARNING" in statuses:
        return "WARNING"
    if "MISSING" in statuses:
        return "MISSING"
    return "PASS"


def validate_materials(
    part_keys: Set[str],
    part_details: Dict[str, Dict[str, str]],
    reference_table: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Validate material/finish/heat for each part key.

    `part_details` comes from the drawing extractor and is keyed by normalized `part_number`.
    """
    reference_table = reference_table if reference_table is not None else _load_reference_table()

    ref_by_edm_numeric: Dict[str, Dict[str, Any]] = {}
    for row in reference_table:
        edm = _normalize_code(row.get("edm"))
        if edm:
            ref_by_edm_numeric[_edm_numeric_key(edm)] = row

    out: List[Dict[str, Any]] = []

    for part_number in sorted(part_keys):
        d = part_details.get(part_number, {}) or {}
        actual_material_code = _normalize_code(d.get("material_code") or "")
        actual_material_numeric_key = _edm_numeric_key(actual_material_code)
        actual_material_name = normalize_text(d.get("material_name") or "")
        actual_finish_raw = d.get("finish") or ""
        actual_finish = _normalize_finish(actual_finish_raw)
        actual_heat_treatment = normalize_text(d.get("heat_treatment") or "")
        actual_heat_range = _extract_numeric_heat_range(actual_heat_treatment)
        actual_description = normalize_text(d.get("description") or "")

        ref = ref_by_edm_numeric.get(actual_material_numeric_key)
        if not ref:
            material_expected: List[str] = []
            finish_expected: List[str] = []
            heat_expected: Optional[str] = None
        else:
            material_expected = [normalize_text(m) for m in (ref.get("materials") or []) if m]
            finish_expected = [normalize_text(f) for f in (ref.get("finish") or []) if f]
            heat_expected = ref.get("heat")  # may be None

        if not actual_material_name and not actual_material_code:
            material_status = "MISSING"
        elif not ref:
            material_status = "MISSING"
        elif not actual_material_name:
            material_status = "MISSING"
        else:
            material_status = "PASS" if actual_material_name in material_expected else "FAIL"

        if not actual_finish_raw:
            finish_status = "MISSING"
        elif not ref:
            finish_status = "MISSING"
        else:
            if any(actual_finish == exp for exp in finish_expected):
                finish_status = "PASS"
            else:
                # Optional soft matches: exact-by-normalization only is PASS,
                # everything else similar-ish becomes WARNING.
                finish_status = "FAIL"
                for exp in finish_expected:
                    if _similar_finish(exp, actual_finish):
                        finish_status = "WARNING"
                        break

        heat_expected_norm = normalize_text(heat_expected) if heat_expected else ""
        if not actual_heat_treatment or not actual_heat_range:
            if not ref:
                heat_status = "MISSING"
            elif heat_expected is None or heat_expected_norm in {"", "NA"}:
                # Reference indicates no numeric heat validation required.
                heat_status = "PASS"
            else:
                heat_status = "MISSING"
        else:
            if not ref:
                heat_status = "MISSING"
            elif heat_expected is None or heat_expected_norm in {"", "NA"}:
                heat_status = "WARNING"
            else:
                heat_status = "PASS" if actual_heat_range == heat_expected_norm else "FAIL"

        # For display: if we have a heat treatment sentence, keep it, but also attach the extracted range.
        heat_expected_display = heat_expected_norm if heat_expected_norm else "NA"

        # Avoid showing huge/empty strings in the UI.
        actual_material_display = actual_material_name
        actual_finish_display = normalize_text(actual_finish_raw)
        actual_heat_display = actual_heat_treatment

        out.append(
            {
                "part_number": part_number,
                "description": actual_description,
                "material": {
                    "expected": material_expected,
                    "actual": actual_material_display,
                    "status": material_status,
                },
                "finish": {
                    "expected": finish_expected,
                    "actual": actual_finish_display,
                    "status": finish_status,
                },
                "heat": {
                    "expected": heat_expected_display,
                    "actual": actual_heat_display,
                    "actual_range": actual_heat_range,
                    "status": heat_status,
                },
            }
        )

    return out


def validate_materials_for_upload(part_keys: Set[str], part_details: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Convenience wrapper that keeps backend response shape stable.
    """
    return {"material_results": validate_materials(part_keys=part_keys, part_details=part_details)}

