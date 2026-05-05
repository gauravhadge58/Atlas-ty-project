"""
Capture baseline extraction results for regression testing.

Runs fitment extraction on all PDFs in the project root and saves
the dimensional profiles to a JSON file for comparison after changes.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.bom_extractor import extract_bom_from_page1
from services.fitment_checker import extract_fitment_data


def serialize_profile(profile) -> Dict[str, Any]:
    """Convert DimensionProfile to JSON-serializable dict."""
    return {
        "part_number": profile.part_number,
        "description": profile.description,
        "gender": profile.gender,
        "bom_qty": profile.bom_qty,
        "threads": [
            {
                "nominal": t.nominal,
                "pitch": t.pitch,
                "count": t.count,
                "gender": t.gender,
                "length": t.length,
                "is_clearance": t.is_clearance,
                "raw": t.raw,
            }
            for t in profile.threads
        ],
        "hole_patterns": [
            {
                "count": h.count,
                "diameter": h.diameter,
                "source": h.source,
            }
            for h in profile.hole_patterns
        ],
        "bore_shaft_fits": [
            {
                "nominal": b.nominal,
                "fit_code": b.fit_code,
                "fit_type": b.fit_type,
                "source": b.source,
            }
            for b in profile.bore_shaft_fits
        ],
        "countersinks": [
            {
                "screw_nom": c.screw_nom,
                "csk_dia": c.csk_dia,
                "angle": c.angle,
                "source": c.source,
            }
            for c in profile.countersinks
        ],
        "counterbores": [
            {
                "screw_nom": c.screw_nom,
                "cbore_dia": c.cbore_dia,
                "depth": c.depth,
                "source": c.source,
            }
            for c in profile.counterbores
        ],
        "washers": [
            {
                "screw_nom": w.screw_nom,
                "washer_type": w.washer_type,
                "source": w.source,
            }
            for w in profile.washers
        ],
        "linear_dims": profile.linear_dims,
    }


def main():
    """Capture baseline extraction results from all project PDFs."""
    # Find all PDFs in project root
    project_root = Path(__file__).parent.parent
    pdf_files = list(project_root.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files in project root")
    
    baseline = {}
    
    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        
        try:
            # Extract BOM
            bom_rows, _ = extract_bom_from_page1(str(pdf_path))
            print(f"  BOM: {len(bom_rows)} items")
            
            # Extract fitment data
            profiles = extract_fitment_data(str(pdf_path), bom_rows)
            print(f"  Profiles: {len(profiles)} parts")
            
            # Serialize profiles
            serialized_profiles = {
                pn: serialize_profile(profile)
                for pn, profile in profiles.items()
            }
            
            baseline[pdf_path.name] = {
                "bom_count": len(bom_rows),
                "profile_count": len(profiles),
                "profiles": serialized_profiles,
            }
            
        except Exception as e:
            print(f"  ERROR: {e}")
            baseline[pdf_path.name] = {
                "error": str(e)
            }
    
    # Save baseline to fixtures
    output_path = Path(__file__).parent / "tests" / "fixtures" / "baseline_profiles.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(baseline, f, indent=2)
    
    print(f"\n✓ Baseline saved to: {output_path}")
    print(f"  Total PDFs processed: {len(baseline)}")
    print(f"  Successful: {sum(1 for v in baseline.values() if 'error' not in v)}")
    print(f"  Failed: {sum(1 for v in baseline.values() if 'error' in v)}")


if __name__ == "__main__":
    main()
