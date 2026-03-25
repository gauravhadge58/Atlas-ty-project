import re
from typing import Optional


_re_whitespace = re.compile(r"\s+")


def normalize_text(value: Optional[str]) -> str:
    """
    Normalize extracted text for stable matching.
    - Uppercase
    - Collapse whitespace
    """
    if not value:
        return ""
    value = value.upper()
    value = _re_whitespace.sub(" ", value).strip()
    return value


def normalize_part_number(part_number: Optional[str]) -> str:
    """
    Normalize part numbers by removing whitespace.
    Keep other characters because part numbers can include hyphens/slashes/dots.
    """
    if not part_number:
        return ""
    part_number = normalize_text(part_number)
    part_number = re.sub(r"\s+", "", part_number)
    return part_number


def parse_int(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    value = normalize_text(value)
    # Keep digits only (handles cases like "1." or "QTY 2")
    digits = re.sub(r"[^\d]", "", value)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def parse_qty(value: Optional[str]) -> Optional[float]:
    """
    Parse quantity from strings like "2", "2 EA", "1.5", "QTY: 3".
    Returns float to be permissive; UI can display as int if it is integral.
    """
    if not value:
        return None
    value = normalize_text(value)
    # Extract first numeric token (int or decimal)
    m = re.search(r"(\d+(?:\.\d+)?)", value)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def is_standard_part(part_number: str) -> bool:
    """
    Standard hardware rule:
    - part_number is numeric
    - length == 9
    """
    pn = normalize_part_number(part_number)
    return bool(re.fullmatch(r"\d{9}", pn))

