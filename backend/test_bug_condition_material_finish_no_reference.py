"""
Bug Condition Exploration Test for Material/Finish Validation No Reference Fix

**Validates: Requirements 1.1, 1.2**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.

This test suite uses property-based testing to verify that the validate_materials
function correctly handles material and finish validation when no reference data exists
for a material.

GOAL: Surface counterexamples that demonstrate the bug exists.

EXPECTED OUTCOME: Test FAILS on unfixed code (this is correct - it proves the bug exists).

The bug: When a PDF has material data OR finish data AND there is no reference data for
that material, the system incorrectly returns material_status = "MISSING" or 
finish_status = "MISSING" instead of "PASS" (not applicable).
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
# Property 1: Bug Condition - Material Data Without Reference Returns MISSING
# ============================================================================

def test_bug_condition_concrete_sts_material_with_name():
    """
    Property 1: Bug Condition - Material "STS" with material name
    
    **Validates: Requirements 1.1**
    
    Test the specific case from the bug report: Material "STS" (not in reference)
    with material name in PDF should return material_status = "PASS" but currently
    returns "MISSING".
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Material STS with material name")
    print("="*80)
    print()
    
    # Setup: Material "STS" is not in material_reference.json
    part_keys = {"PART-001"}
    part_details = {
        "PART-001": {
            "material_code": "STS",
            "material_name": "STAINLESS STEEL",
            "finish": "",
            "heat_treatment": "",
            "description": "Test part with STS material"
        }
    }
    
    # Empty reference table (simulates material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: STS (not in reference)")
    print(f"  Material Name: STAINLESS STEEL")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # Expected behavior: material_status should be "PASS" (not applicable)
    # Current buggy behavior: material_status is "MISSING"
    assert material_status == "PASS", (
        f"Bug confirmed: material_status is '{material_status}', expected 'PASS'\n"
        f"When no reference data exists and PDF has material data,\n"
        f"the status should be 'PASS' (not applicable), not 'MISSING'"
    )
    
    print("✓ Test passed - material_status is 'PASS' as expected")
    print("="*80)


def test_bug_condition_concrete_sts_finish():
    """
    Property 2: Bug Condition - Material "STS" with finish
    
    **Validates: Requirements 1.2**
    
    Test the specific case from the bug report: Material "STS" (not in reference)
    with finish in PDF should return finish_status = "PASS" but currently
    returns "MISSING".
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Material STS with finish")
    print("="*80)
    print()
    
    # Setup: Material "STS" is not in material_reference.json
    part_keys = {"PART-002"}
    part_details = {
        "PART-002": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "BLACKODISING",
            "heat_treatment": "",
            "description": "Test part with STS material and finish"
        }
    }
    
    # Empty reference table (simulates material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: STS (not in reference)")
    print(f"  Finish: BLACKODISING")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  finish_status: {finish_status}")
    print()
    
    # Expected behavior: finish_status should be "PASS" (not applicable)
    # Current buggy behavior: finish_status is "MISSING"
    assert finish_status == "PASS", (
        f"Bug confirmed: finish_status is '{finish_status}', expected 'PASS'\n"
        f"When no reference data exists and PDF has finish data,\n"
        f"the status should be 'PASS' (not applicable), not 'MISSING'"
    )
    
    print("✓ Test passed - finish_status is 'PASS' as expected")
    print("="*80)


def test_bug_condition_concrete_xyz_both():
    """
    Property 1 & 2: Bug Condition - Material "XYZ" with both material and finish
    
    **Validates: Requirements 1.1, 1.2**
    
    Test another material not in reference database with both material name and finish
    to confirm the bug affects both validations.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Material XYZ with material name and finish")
    print("="*80)
    print()
    
    # Setup: Material "XYZ" is not in material_reference.json
    part_keys = {"PART-003"}
    part_details = {
        "PART-003": {
            "material_code": "XYZ",
            "material_name": "STEEL",
            "finish": "ZINC PLATED",
            "heat_treatment": "",
            "description": "Test part with XYZ material"
        }
    }
    
    # Empty reference table (simulates material not in database)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: XYZ (not in reference)")
    print(f"  Material Name: STEEL")
    print(f"  Finish: ZINC PLATED")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print(f"  finish_status: {finish_status}")
    print()
    
    # Expected behavior: both should be "PASS" (not applicable)
    failures = []
    if material_status != "PASS":
        failures.append(f"material_status is '{material_status}', expected 'PASS'")
    if finish_status != "PASS":
        failures.append(f"finish_status is '{finish_status}', expected 'PASS'")
    
    if failures:
        print("BUG CONFIRMED:")
        for failure in failures:
            print(f"  - {failure}")
        print()
        assert False, (
            f"Bug confirmed: {len(failures)} status(es) incorrect.\n"
            f"When no reference data exists and PDF has material/finish data,\n"
            f"the status should be 'PASS' (not applicable), not 'MISSING'"
        )
    
    print("✓ Test passed - both statuses are 'PASS' as expected")
    print("="*80)


def test_bug_condition_no_material_name():
    """
    Edge Case: Material "STS" with no material name
    
    **Validates: Requirements 3.1**
    
    Test edge case: material code present but no material name.
    This should remain "MISSING" even after the fix (different from the bug case).
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code.
    """
    print("\n" + "="*80)
    print("TEST: Edge Case - Material STS with no material name")
    print("="*80)
    print()
    
    # Setup: Material "STS" with no material name
    part_keys = {"PART-004"}
    part_details = {
        "PART-004": {
            "material_code": "STS",
            "material_name": "",  # Empty material name
            "finish": "",
            "heat_treatment": "",
            "description": "Test part with STS material code only"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: STS (not in reference)")
    print(f"  Material Name: '' (empty)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # Expected behavior: material_status should be "MISSING" (PDF truly missing data)
    # This is different from the bug case - empty material name is truly missing
    assert material_status == "MISSING", (
        f"Edge case: material_status is '{material_status}', expected 'MISSING'\n"
        f"When material name is empty, material_status should remain 'MISSING'"
    )
    
    print("✓ Test passed - material_status is 'MISSING' as expected (edge case)")
    print("="*80)


def test_bug_condition_no_finish():
    """
    Edge Case: Material "STS" with no finish
    
    **Validates: Requirements 3.2**
    
    Test edge case: material present but no finish.
    With new business logic, this should be "PASS" (validation not applicable).
    
    EXPECTED OUTCOME: This test should PASS with new logic.
    """
    print("\n" + "="*80)
    print("TEST: Edge Case - Material STS with no finish")
    print("="*80)
    print()
    
    # Setup: Material "STS" with no finish
    part_keys = {"PART-005"}
    part_details = {
        "PART-005": {
            "material_code": "STS",
            "material_name": "STS",
            "finish": "",  # Empty finish
            "heat_treatment": "",
            "description": "Test part with STS material, no finish"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: STS (not in reference)")
    print(f"  Finish: '' (empty)")
    print(f"  Reference Data: None")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  finish_status: {finish_status}")
    print()
    
    # Expected behavior: finish_status should be "PASS" (validation not applicable)
    assert finish_status == "PASS", (
        f"Edge case: finish_status is '{finish_status}', expected 'PASS'\n"
        f"When finish is empty, finish_status should be 'PASS' (not applicable)"
    )
    
    print("✓ Test passed - finish_status is 'PASS' as expected (edge case)")
    print("="*80)


@given(
    material_code=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
        min_size=2,
        max_size=10
    ).filter(lambda x: x.strip() != "" and not x.startswith("EDM")),
    material_name=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        min_size=2,
        max_size=30
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_bug_condition_property_material_no_reference(material_code: str, material_name: str):
    """
    Property 1: Bug Condition - No Reference Data Returns PASS for Material
    
    **Validates: Requirements 1.1**
    
    Property-based test: For ANY material not in reference database with material
    name in PDF, the material_status should be "PASS" (not applicable).
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any material_code not in reference AND actual_material_name != "",
    the function SHALL return material_status = "PASS".
    """
    # Setup
    part_keys = {"PART-TEST"}
    part_details = {
        "PART-TEST": {
            "material_code": material_code.strip(),
            "material_name": material_name.strip(),
            "finish": "",
            "heat_treatment": "",
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
    material_status = result["material"]["status"]
    
    # Expected behavior: material_status should be "PASS" (not applicable)
    assert material_status == "PASS", (
        f"Bug confirmed for material '{material_code}' with name '{material_name}':\n"
        f"  material_status is '{material_status}', expected 'PASS'\n"
        f"  When no reference data exists and PDF has material data,\n"
        f"  the status should be 'PASS' (not applicable), not 'MISSING'"
    )


@given(
    material_code=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
        min_size=2,
        max_size=10
    ).filter(lambda x: x.strip() != "" and not x.startswith("EDM")),
    finish=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        min_size=2,
        max_size=30
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_bug_condition_property_finish_no_reference(material_code: str, finish: str):
    """
    Property 2: Bug Condition - No Reference Data Returns PASS for Finish
    
    **Validates: Requirements 1.2**
    
    Property-based test: For ANY material not in reference database with finish
    in PDF, the finish_status should be "PASS" (not applicable).
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any material_code not in reference AND actual_finish_raw != "",
    the function SHALL return finish_status = "PASS".
    """
    # Setup
    part_keys = {"PART-TEST"}
    part_details = {
        "PART-TEST": {
            "material_code": material_code.strip(),
            "material_name": material_code.strip(),
            "finish": finish.strip(),
            "heat_treatment": "",
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
    finish_status = result["finish"]["status"]
    
    # Expected behavior: finish_status should be "PASS" (not applicable)
    assert finish_status == "PASS", (
        f"Bug confirmed for material '{material_code}' with finish '{finish}':\n"
        f"  finish_status is '{finish_status}', expected 'PASS'\n"
        f"  When no reference data exists and PDF has finish data,\n"
        f"  the status should be 'PASS' (not applicable), not 'MISSING'"
    )


def test_bug_condition_multiple_materials():
    """
    Property 1 & 2: Bug Condition - Multiple materials not in reference
    
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
            "material_name": "STAINLESS STEEL",
            "finish": "",
            "heat_treatment": "",
            "description": "Part A"
        },
        "PART-B": {
            "material_code": "XYZ",
            "material_name": "XYZ",
            "finish": "BLACKODISING",
            "heat_treatment": "",
            "description": "Part B"
        },
        "PART-C": {
            "material_code": "ABC",
            "material_name": "STEEL",
            "finish": "ZINC PLATED",
            "heat_treatment": "",
            "description": "Part C"
        }
    }
    
    # Empty reference table
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input: 3 parts with materials not in reference")
    print()
    
    # Check results
    assert len(results) == 3, "Expected 3 results"
    
    failures = []
    for result in results:
        part_num = result["part_number"]
        material_status = result["material"]["status"]
        finish_status = result["finish"]["status"]
        material = result["material"]["actual"]
        finish = result["finish"]["actual"]
        
        print(f"  {part_num} (Material: {material}, Finish: {finish}):")
        print(f"    material_status = {material_status}, finish_status = {finish_status}")
        
        if material and material_status != "PASS":
            failures.append(f"{part_num}: material_status is '{material_status}', expected 'PASS'")
        if finish and finish_status != "PASS":
            failures.append(f"{part_num}: finish_status is '{finish_status}', expected 'PASS'")
    
    print()
    
    if failures:
        print("BUG CONFIRMED - Counterexamples found:")
        for failure in failures:
            print(f"  - {failure}")
        print()
        print("ROOT CAUSE: When no reference data exists and PDF has material/finish data,")
        print("the system incorrectly returns 'MISSING' instead of 'PASS'")
        print("="*80)
        
        assert False, (
            f"Bug confirmed: {len(failures)} status(es) incorrect.\n"
            f"Expected 'PASS' (not applicable) but got 'MISSING'"
        )
    else:
        print("✓ All parts have correct statuses as expected")
        print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION TEST")
    print("# Material/Finish Validation No Reference Fix")
    print("# CRITICAL: This test MUST FAIL on unfixed code")
    print("# Failure confirms the bug exists and helps understand root cause")
    print("#"*80)
    
    # Run concrete examples first (these provide clear output)
    try:
        test_bug_condition_concrete_sts_material_with_name()
        print("\n✓ Test 1.1 PASSED (Material STS with name)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.1 FAILED (Material STS with name)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_concrete_sts_finish()
        print("\n✓ Test 1.2 PASSED (Material STS with finish)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.2 FAILED (Material STS with finish)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_concrete_xyz_both()
        print("\n✓ Test 1.3 PASSED (Material XYZ with both)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.3 FAILED (Material XYZ with both)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_multiple_materials()
        print("\n✓ Test 1.4 PASSED (Multiple Materials)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.4 FAILED (Multiple Materials)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    # Run edge cases (these should pass on both unfixed and fixed code)
    print("\n" + "="*80)
    print("Running edge case tests (should pass on unfixed code)...")
    print("="*80)
    
    try:
        test_bug_condition_no_material_name()
        print("\n✓ Edge Case 1 PASSED (No material name)")
    except AssertionError as e:
        print(f"\n✗ Edge Case 1 FAILED (No material name)")
        print(f"  UNEXPECTED - this should pass on unfixed code")
        print(f"  Error: {e}")
    
    try:
        test_bug_condition_no_finish()
        print("\n✓ Edge Case 2 PASSED (No finish)")
    except AssertionError as e:
        print(f"\n✗ Edge Case 2 FAILED (No finish)")
        print(f"  UNEXPECTED - this should pass on unfixed code")
        print(f"  Error: {e}")
    
    # Run property-based tests
    print("\n" + "="*80)
    print("Running property-based tests (50 examples each)...")
    print("="*80)
    
    try:
        test_bug_condition_property_material_no_reference()
        print("\n✓ Property Test 1 PASSED (Material validation, 50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Property Test 1 FAILED (Material validation, 50 examples)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:300]}")
    
    try:
        test_bug_condition_property_finish_no_reference()
        print("\n✓ Property Test 2 PASSED (Finish validation, 50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Property Test 2 FAILED (Finish validation, 50 examples)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:300]}")
    
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION COMPLETE")
    print("# Test failures above confirm the bug exists")
    print("# Counterexamples documented for root cause analysis")
    print("#"*80)
