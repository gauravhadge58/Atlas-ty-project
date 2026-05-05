"""
Bug Condition Exploration Test for Heat Treatment Validation No Reference Fix

**Validates: Requirements 1.1, 1.2**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.

This test suite uses property-based testing to verify that the validate_materials
function correctly handles heat treatment validation when no reference data exists
for a material.

GOAL: Surface counterexamples that demonstrate the bug exists.

EXPECTED OUTCOME: Test FAILS on unfixed code (this is correct - it proves the bug exists).

The bug: When a PDF has no heat treatment field AND there is no reference data for
that material, the system incorrectly returns heat_status = "MISSING" instead of
heat_status = "PASS" (not applicable).
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Set

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from hypothesis import given, strategies as st, settings, assume
from services.material_validator import validate_materials


# ============================================================================
# Property 1: Bug Condition - No Reference Data Returns MISSING Instead of PASS
# ============================================================================

def test_bug_condition_concrete_sts_material():
    """
    Property 1: Bug Condition - Material "STS" with no heat treatment
    
    **Validates: Requirements 1.1, 1.2**
    
    Test the specific case from the bug report: Material "STS" (not in reference)
    with no heat treatment in PDF should return heat_status = "PASS" but currently
    returns "MISSING".
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Material STS with no heat treatment")
    print("="*80)
    print()
    
    # Setup: Material "STS" is not in material_reference.json
    part_keys = {"PART-001"}
    part_details = {
        "PART-001": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Test part with STS material"
        }
    }
    
    # Empty reference table (simulates material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: STS (not in reference)")
    print(f"  Heat Treatment: '' (empty)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # Expected behavior: heat_status should be "PASS" (not applicable)
    # Current buggy behavior: heat_status is "MISSING"
    assert heat_status == "PASS", (
        f"Bug confirmed: heat_status is '{heat_status}', expected 'PASS'\n"
        f"When no reference data exists and PDF has no heat treatment,\n"
        f"the status should be 'PASS' (not applicable), not 'MISSING'"
    )
    
    print("✓ Test passed - heat_status is 'PASS' as expected")
    print("="*80)


def test_bug_condition_concrete_xyz_material():
    """
    Property 1: Bug Condition - Material "XYZ" with no heat treatment
    
    **Validates: Requirements 1.1, 1.2**
    
    Test another material not in reference database to confirm the bug is not
    specific to "STS".
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Material XYZ with no heat treatment")
    print("="*80)
    print()
    
    # Setup: Material "XYZ" is not in material_reference.json
    part_keys = {"PART-002"}
    part_details = {
        "PART-002": {
            "material_code": "XYZ",
            "material_name": "XYZ",
            "finish": "",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Test part with XYZ material"
        }
    }
    
    # Empty reference table (simulates material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: XYZ (not in reference)")
    print(f"  Heat Treatment: '' (empty)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # Expected behavior: heat_status should be "PASS" (not applicable)
    assert heat_status == "PASS", (
        f"Bug confirmed: heat_status is '{heat_status}', expected 'PASS'\n"
        f"When no reference data exists and PDF has no heat treatment,\n"
        f"the status should be 'PASS' (not applicable), not 'MISSING'"
    )
    
    print("✓ Test passed - heat_status is 'PASS' as expected")
    print("="*80)


def test_bug_condition_empty_material_code():
    """
    Property 1: Bug Condition - Empty material code with no heat treatment
    
    **Validates: Requirements 1.1, 1.2**
    
    Test edge case: empty material code with no heat treatment.
    This should remain "MISSING" even after the fix (different from the bug case).
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code.
    """
    print("\n" + "="*80)
    print("TEST: Edge Case - Empty material code with no heat treatment")
    print("="*80)
    print()
    
    # Setup: Empty material code
    part_keys = {"PART-003"}
    part_details = {
        "PART-003": {
            "material_code": "",
            "material_name": "",
            "finish": "",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Test part with empty material"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: '' (empty)")
    print(f"  Heat Treatment: '' (empty)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # Expected behavior: heat_status should be "MISSING" (material itself is missing)
    # This is different from the bug case - empty material is truly missing
    assert heat_status == "MISSING", (
        f"Edge case: heat_status is '{heat_status}', expected 'MISSING'\n"
        f"When material code is empty, heat_status should remain 'MISSING'"
    )
    
    print("✓ Test passed - heat_status is 'MISSING' as expected (edge case)")
    print("="*80)


def test_bug_condition_material_with_heat_treatment():
    """
    Property 1: Bug Condition - Material not in reference WITH heat treatment
    
    **Validates: Requirements 1.1, 1.2**
    
    Test that when a material not in reference HAS heat treatment in PDF,
    the status should remain "MISSING" (can't validate without reference).
    This should be unchanged by the fix.
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code.
    """
    print("\n" + "="*80)
    print("TEST: Edge Case - Material STS WITH heat treatment")
    print("="*80)
    print()
    
    # Setup: Material "STS" with heat treatment in PDF
    part_keys = {"PART-004"}
    part_details = {
        "PART-004": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "",
            "heat_treatment": "HARDENED TO 60-70",  # Has heat treatment
            "description": "Test part with STS material and heat treatment"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: STS (not in reference)")
    print(f"  Heat Treatment: 'HARDENED TO 60-70' (present)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # Expected behavior: heat_status should be "MISSING" (can't validate without reference)
    assert heat_status == "MISSING", (
        f"Edge case: heat_status is '{heat_status}', expected 'MISSING'\n"
        f"When PDF has heat treatment but no reference exists, status should be 'MISSING'"
    )
    
    print("✓ Test passed - heat_status is 'MISSING' as expected (edge case)")
    print("="*80)


@given(
    material_code=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
        min_size=2,
        max_size=10
    ).filter(lambda x: x.strip() != "" and not x.startswith("EDM"))
)
@settings(max_examples=50)
def test_bug_condition_property_no_reference_no_heat(material_code: str):
    """
    Property 1: Bug Condition - No Reference Data Returns PASS
    
    **Validates: Requirements 1.1, 1.2**
    
    Property-based test: For ANY material not in reference database with no heat
    treatment in PDF, the heat_status should be "PASS" (not applicable).
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any material_code not in reference AND actual_heat_treatment == ""
    AND actual_heat_range == "", the function SHALL return heat_status = "PASS".
    """
    # Setup
    part_keys = {"PART-TEST"}
    part_details = {
        "PART-TEST": {
            "material_code": material_code.strip(),
            "material_name": material_code.strip(),
            "finish": "",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": f"Test part with {material_code}"
        }
    }
    
    # Empty reference table (material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    # Expected behavior: heat_status should be "PASS" (not applicable)
    assert heat_status == "PASS", (
        f"Bug confirmed for material '{material_code}':\n"
        f"  heat_status is '{heat_status}', expected 'PASS'\n"
        f"  When no reference data exists and PDF has no heat treatment,\n"
        f"  the status should be 'PASS' (not applicable), not 'MISSING'"
    )


def test_bug_condition_multiple_materials():
    """
    Property 1: Bug Condition - Multiple materials not in reference
    
    **Validates: Requirements 1.1, 1.2**
    
    Test that the bug affects multiple materials in a single validation call.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Multiple materials not in reference")
    print("="*80)
    print()
    
    # Setup: Multiple materials not in reference
    part_keys = {"PART-A", "PART-B", "PART-C"}
    part_details = {
        "PART-A": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "",
            "heat_treatment": "",
            "description": "Part A"
        },
        "PART-B": {
            "material_code": "XYZ",
            "material_name": "XYZ",
            "finish": "",
            "heat_treatment": "",
            "description": "Part B"
        },
        "PART-C": {
            "material_code": "ABC",
            "material_name": "ABC",
            "finish": "",
            "heat_treatment": "",
            "description": "Part C"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input: 3 parts with materials not in reference, no heat treatment")
    print()
    
    # Check results
    assert len(results) == 3, "Expected 3 results"
    
    failures = []
    for result in results:
        part_num = result["part_number"]
        heat_status = result["heat"]["status"]
        material = result["material"]["actual"]
        
        print(f"  {part_num} (Material: {material}): heat_status = {heat_status}")
        
        if heat_status != "PASS":
            failures.append(f"{part_num}: heat_status is '{heat_status}', expected 'PASS'")
    
    print()
    
    if failures:
        print("BUG CONFIRMED - Counterexamples found:")
        for failure in failures:
            print(f"  - {failure}")
        print()
        print("ROOT CAUSE: When no reference data exists and PDF has no heat treatment,")
        print("the system incorrectly returns 'MISSING' instead of 'PASS'")
        print("="*80)
        
        assert False, (
            f"Bug confirmed: {len(failures)} part(s) have incorrect heat_status.\n"
            f"Expected 'PASS' (not applicable) but got 'MISSING'"
        )
    else:
        print("✓ All parts have heat_status = 'PASS' as expected")
        print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION TEST")
    print("# Heat Treatment Validation No Reference Fix")
    print("# CRITICAL: This test MUST FAIL on unfixed code")
    print("# Failure confirms the bug exists and helps understand root cause")
    print("#"*80)
    
    # Run concrete examples first (these provide clear output)
    try:
        test_bug_condition_concrete_sts_material()
        print("\n✓ Test 1.1 PASSED (Material STS)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.1 FAILED (Material STS)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_concrete_xyz_material()
        print("\n✓ Test 1.2 PASSED (Material XYZ)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.2 FAILED (Material XYZ)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_multiple_materials()
        print("\n✓ Test 1.3 PASSED (Multiple Materials)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.3 FAILED (Multiple Materials)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    # Run edge cases (these should pass on both unfixed and fixed code)
    print("\n" + "="*80)
    print("Running edge case tests (should pass on unfixed code)...")
    print("="*80)
    
    try:
        test_bug_condition_empty_material_code()
        print("\n✓ Edge Case 1 PASSED (Empty material code)")
    except AssertionError as e:
        print(f"\n✗ Edge Case 1 FAILED (Empty material code)")
        print(f"  UNEXPECTED - this should pass on unfixed code")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_material_with_heat_treatment()
        print("\n✓ Edge Case 2 PASSED (Material with heat treatment)")
    except AssertionError as e:
        print(f"\n✗ Edge Case 2 FAILED (Material with heat treatment)")
        print(f"  UNEXPECTED - this should pass on unfixed code")
        print(f"  Error: {e}")
    
    # Run property-based test
    print("\n" + "="*80)
    print("Running property-based test (50 examples)...")
    print("="*80)
    
    try:
        test_bug_condition_property_no_reference_no_heat()
        print("\n✓ Property Test PASSED (50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Property Test FAILED (50 examples)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:300]}")
    
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION COMPLETE")
    print("# Test failures above confirm the bug exists")
    print("# Counterexamples documented for root cause analysis")
    print("#"*80)
