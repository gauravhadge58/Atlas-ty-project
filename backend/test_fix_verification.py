"""
Quick verification test to check the fix is working correctly
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.material_validator import validate_materials


def test_empty_material_full_validation():
    """Test that empty material code is handled correctly across all validations"""
    print("\n" + "="*80)
    print("TEST: Empty material code - full validation output")
    print("="*80)
    
    part_keys = {"PART-EMPTY"}
    part_details = {
        "PART-EMPTY": {
            "material_code": "",
            "material_name": "",
            "finish": "",
            "heat_treatment": "",
            "description": "Part with empty material"
        }
    }
    
    reference_table = []
    results = validate_materials(part_keys, part_details, reference_table)
    
    result = results[0]
    print(f"\nMaterial Status: {result['material']['status']}")
    print(f"Finish Status: {result['finish']['status']}")
    print(f"Heat Treatment Status: {result['heat']['status']}")
    print()
    
    # Material should be MISSING (no material specified)
    # Finish should be MISSING (no finish specified)
    # Heat treatment should be PASS (not applicable - no reference to validate against)
    print("Expected:")
    print("  Material: MISSING (no material specified)")
    print("  Finish: MISSING (no finish specified)")
    print("  Heat: PASS (not applicable - no reference data)")
    print()
    
    assert result['material']['status'] == "MISSING", "Material should be MISSING"
    assert result['finish']['status'] == "MISSING", "Finish should be MISSING"
    assert result['heat']['status'] == "PASS", "Heat should be PASS (not applicable)"
    
    print("✓ All validations correct!")
    print("="*80)


def test_sts_material_no_heat():
    """Test the main bug case: STS material with no heat treatment"""
    print("\n" + "="*80)
    print("TEST: STS material with no heat treatment (main bug case)")
    print("="*80)
    
    part_keys = {"PART-STS"}
    part_details = {
        "PART-STS": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "",
            "heat_treatment": "",
            "description": "Part with STS material"
        }
    }
    
    reference_table = []
    results = validate_materials(part_keys, part_details, reference_table)
    
    result = results[0]
    print(f"\nMaterial Status: {result['material']['status']}")
    print(f"Finish Status: {result['finish']['status']}")
    print(f"Heat Treatment Status: {result['heat']['status']}")
    print()
    
    # Material should be MISSING (not in reference)
    # Finish should be MISSING (not in reference)
    # Heat treatment should be PASS (not applicable - no reference to validate against)
    print("Expected:")
    print("  Material: MISSING (not in reference)")
    print("  Finish: MISSING (not in reference)")
    print("  Heat: PASS (not applicable - no reference data) ← BUG FIX")
    print()
    
    assert result['material']['status'] == "MISSING", "Material should be MISSING"
    assert result['finish']['status'] == "MISSING", "Finish should be MISSING"
    assert result['heat']['status'] == "PASS", "Heat should be PASS (not applicable)"
    
    print("✓ Bug is fixed! Heat treatment correctly returns PASS")
    print("="*80)


def test_edm_material_with_reference():
    """Test preservation: material with reference data should work as before"""
    print("\n" + "="*80)
    print("TEST: EDM material with reference data (preservation check)")
    print("="*80)
    
    part_keys = {"PART-EDM"}
    part_details = {
        "PART-EDM": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "BLACKODISING",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Part with EDM material"
        }
    }
    
    # Reference data that requires heat treatment
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"  # Requires heat treatment
        }
    ]
    
    results = validate_materials(part_keys, part_details, reference_table)
    
    result = results[0]
    print(f"\nMaterial Status: {result['material']['status']}")
    print(f"Finish Status: {result['finish']['status']}")
    print(f"Heat Treatment Status: {result['heat']['status']}")
    print()
    
    # Material should be PASS (matches reference)
    # Finish should be PASS (matches reference)
    # Heat treatment should be MISSING (required by reference but not in PDF)
    print("Expected:")
    print("  Material: PASS (matches reference)")
    print("  Finish: PASS (matches reference)")
    print("  Heat: MISSING (required by reference but not in PDF) ← PRESERVED")
    print()
    
    assert result['material']['status'] == "PASS", "Material should be PASS"
    assert result['finish']['status'] == "PASS", "Finish should be PASS"
    assert result['heat']['status'] == "MISSING", "Heat should be MISSING (required but absent)"
    
    print("✓ Preservation verified! Existing logic unchanged")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# FIX VERIFICATION TEST")
    print("# Verifying the heat treatment validation fix")
    print("#"*80)
    
    test_sts_material_no_heat()
    test_empty_material_full_validation()
    test_edm_material_with_reference()
    
    print("\n" + "#"*80)
    print("# ALL TESTS PASSED")
    print("# Fix is working correctly!")
    print("#"*80)
