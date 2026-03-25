from typing import Any, Dict, List, Set

from .common import is_standard_part


def match_bom(
    bom_rows: List[Dict[str, Any]],
    extracted_part_keys: Set[str],
) -> List[Dict[str, Any]]:
    """
    Classify each BOM row into:
      - STANDARD
      - FOUND
      - MISSING
    """
    results: List[Dict[str, Any]] = []

    for row in bom_rows:
        pn = row.get("part_number", "")
        if is_standard_part(pn):
            status = "STANDARD"
        elif pn in extracted_part_keys:
            status = "FOUND"
        else:
            status = "MISSING"

        results.append(
            {
                "item": row.get("item"),
                "part_number": pn,
                "description": row.get("description", ""),
                "status": status,
            }
        )

    return results

