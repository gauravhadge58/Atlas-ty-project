"""
Preservation Property Tests for Material/Finish Validation No Reference Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

CRITICAL: These tests MUST PASS on unfixed code - they capture baseline behavior to preserve.

This test suite uses property-based testing to verify that the fix does NOT change
existing functionality for:
- Material validation when reference data EXISTS
- Finish validation when reference data EXISTS
- Material validation when PDF has NO material data (empty strings)
- Finish validation when PDF has NO finish data (empty strings)
- Heat treatment validation logic (completely separate from material/finish)

GOAL: Ensure no regressions are introduced by the fix.

EXPECTED OUTCOME: Tests PASS on unfixed code (confirms baseline behavior to preserve).

The fix should ONLY affect the case where:
- PDF has material data OR finish data AND
- No reference data exists for that material

All other cases must remain unchanged.
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
# Property 2: Preservation - Reference Data Validation Logic Unchanged
# ============================================================================

# ============================================================================
# Test 2.1: Reference Exists, Material Matches
# ============================================================================

def test_preservation_reference_exists_material_matches():
    """
    Property 2: Preservation - Reference exists, material matches
    
    **Validates: Requirements 3.3**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    material data that MATCHES the reference, the system returns
    material_status = "PASS".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, material matches")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 with matching material name
    part_keys = {"PART-001"}
    part_details = {
        "PART-001": {
            "material_code": "EDM000136",
            "material_name": "EN8",  # Matches reference
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table with material
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Material Name: 'EN8'")
    print(f"  Reference materials: ['EN8']")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "PASS"
    # This must remain "PASS" after the fix
    assert material_status == "PASS", (
        f"REGRESSION: material_status is '{material_status}', expected 'PASS'\n"
        f"When reference exists and material matches,\n"
        f"the status must remain 'PASS'"
    )
    
    print("✓ Test passed - material_status is 'PASS' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.2: Reference Exists, Material Doesn't Match
# ============================================================================

def test_preservation_reference_exists_material_mismatch():
    """
    Property 2: Preservation - Reference exists, material doesn't match
    
    **Validates: Requirements 3.4**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    material data that DOES NOT MATCH the reference, the system returns
    material_status = "FAIL".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, material doesn't match")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 with non-matching material name
    part_keys = {"PART-002"}
    part_details = {
        "PART-002": {
            "material_code": "EDM000136",
            "material_name": "SS400",  # Does not match reference
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table with material
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Material Name: 'SS400'")
    print(f"  Reference materials: ['EN8']")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "FAIL"
    # This must remain "FAIL" after the fix
    assert material_status == "FAIL", (
        f"REGRESSION: material_status is '{material_status}', expected 'FAIL'\n"
        f"When reference exists and material doesn't match,\n"
        f"the status must remain 'FAIL'"
    )
    
    print("✓ Test passed - material_status is 'FAIL' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.3: Reference Exists, Finish Matches
# ============================================================================

def test_preservation_reference_exists_finish_matches():
    """
    Property 2: Preservation - Reference exists, finish matches
    
    **Validates: Requirements 3.5**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    finish data that MATCHES the reference, the system returns
    finish_status = "PASS".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, finish matches")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 with matching finish
    part_keys = {"PART-003"}
    part_details = {
        "PART-003": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",  # Matches reference (synonym)
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table with finish
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],  # CHEMICAL BLACK is a synonym
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Finish: 'CHEMICAL BLACK'")
    print(f"  Reference finish: ['BLACKODISING']")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  finish_status: {finish_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "PASS"
    # This must remain "PASS" after the fix
    assert finish_status == "PASS", (
        f"REGRESSION: finish_status is '{finish_status}', expected 'PASS'\n"
        f"When reference exists and finish matches,\n"
        f"the status must remain 'PASS'"
    )
    
    print("✓ Test passed - finish_status is 'PASS' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.4: Reference Exists, Finish Doesn't Match
# ============================================================================

def test_preservation_reference_exists_finish_mismatch():
    """
    Property 2: Preservation - Reference exists, finish doesn't match
    
    **Validates: Requirements 3.6**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    finish data that DOES NOT MATCH the reference, the system returns
    finish_status = "FAIL" or "WARNING".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, finish doesn't match")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 with non-matching finish
    part_keys = {"PART-004"}
    part_details = {
        "PART-004": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "ZINC PLATED",  # Does not match reference
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table with finish
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Finish: 'ZINC PLATED'")
    print(f"  Reference finish: ['BLACKODISING']")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  finish_status: {finish_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "FAIL" or "WARNING"
    # This must remain "FAIL" or "WARNING" after the fix
    assert finish_status in ["FAIL", "WARNING"], (
        f"REGRESSION: finish_status is '{finish_status}', expected 'FAIL' or 'WARNING'\n"
        f"When reference exists and finish doesn't match,\n"
        f"the status must remain 'FAIL' or 'WARNING'"
    )
    
    print(f"✓ Test passed - finish_status is '{finish_status}' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.5: PDF Has No Material Data (Empty Strings)
# ============================================================================

def test_preservation_pdf_no_material_data():
    """
    Property 2: Preservation - PDF has no material data
    
    **Validates: Requirements 3.1**
    
    UPDATED BEHAVIOR: When PDF has no material data (empty material_code AND 
    empty material_name), the system returns material_status = "PASS" because
    validation is not applicable (e.g., assembly parts).
    
    This is a business logic change from the original behavior.
    
    EXPECTED OUTCOME: This test PASSES with new logic (validation not applicable).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - PDF has no material data")
    print("="*80)
    print()
    
    # Setup: Part with no material data
    part_keys = {"PART-005"}
    part_details = {
        "PART-005": {
            "material_code": "",  # Empty
            "material_name": "",  # Empty
            "finish": "BLACKODISING",
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table (doesn't matter for this test)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material Code: '' (empty)")
    print(f"  Material Name: '' (empty)")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # OBSERVE: Expected behavior with new logic is "PASS"
    # When PDF has no material data, validation is not applicable
    assert material_status == "PASS", (
        f"REGRESSION: material_status is '{material_status}', expected 'PASS'\n"
        f"When PDF has no material data (empty strings),\n"
        f"the status should be 'PASS' (validation not applicable)"
    )
    
    print("✓ Test passed - material_status is 'PASS' as expected (validation not applicable)")
    print("="*80)


# ============================================================================
# Test 2.6: PDF Has No Finish Data (Empty String)
# ============================================================================

def test_preservation_pdf_no_finish_data():
    """
    Property 2: Preservation - PDF has no finish data
    
    **Validates: Requirements 3.2**
    
    UPDATED BEHAVIOR: When PDF has no finish data (empty finish string), the 
    system returns finish_status = "PASS" because validation is not applicable
    (e.g., assembly parts).
    
    This is a business logic change from the original behavior.
    
    EXPECTED OUTCOME: This test PASSES with new logic (validation not applicable).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - PDF has no finish data")
    print("="*80)
    print()
    
    # Setup: Part with no finish data
    part_keys = {"PART-006"}
    part_details = {
        "PART-006": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "",  # Empty
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table (doesn't matter for this test)
    reference_table = []
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Finish: '' (empty)")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    print(f"Output:")
    print(f"  finish_status: {finish_status}")
    print()
    
    # OBSERVE: Expected behavior with new logic is "PASS"
    # When PDF has no finish data, validation is not applicable
    assert finish_status == "PASS", (
        f"REGRESSION: finish_status is '{finish_status}', expected 'PASS'\n"
        f"When PDF has no finish data (empty string),\n"
        f"the status should be 'PASS' (validation not applicable)"
    )
    
    print("✓ Test passed - finish_status is 'PASS' as expected (validation not applicable)")
    print("="*80)


# ============================================================================
# Test 2.7: Heat Treatment Validation Logic Unchanged
# ============================================================================

def test_preservation_heat_treatment_validation():
    """
    Property 2: Preservation - Heat treatment validation logic unchanged
    
    **Validates: Requirements 3.7**
    
    OBSERVE behavior on UNFIXED code: Heat treatment validation logic operates
    independently of material/finish validation and must remain unchanged.
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Heat treatment validation logic unchanged")
    print("="*80)
    print()
    
    # Setup: Test various heat treatment validation scenarios
    part_keys = {"PART-H1", "PART-H2", "PART-H3"}
    part_details = {
        "PART-H1": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "HARDENED AND TEMPERED TO 60-70 kg/mm2",  # Matches
            "description": "Heat treatment matches"
        },
        "PART-H2": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "HARDENED AND TEMPERED TO 50-60 kg/mm2",  # Mismatch
            "description": "Heat treatment mismatch"
        },
        "PART-H3": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",  # Missing
            "description": "Heat treatment missing"
        }
    }
    
    # Reference table
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input: 3 parts with different heat treatment validation scenarios")
    print()
    
    # Check results
    assert len(results) == 3, "Expected 3 results"
    
    # Find each result
    results_by_part = {r["part_number"]: r for r in results}
    
    # PART-H1: Heat treatment matches
    h1 = results_by_part["PART-H1"]
    h1_status = h1["heat"]["status"]
    print(f"  PART-H1 (Heat treatment matches): heat_status = {h1_status}")
    assert h1_status == "PASS", f"REGRESSION: Expected 'PASS', got '{h1_status}'"
    
    # PART-H2: Heat treatment mismatch
    h2 = results_by_part["PART-H2"]
    h2_status = h2["heat"]["status"]
    print(f"  PART-H2 (Heat treatment mismatch): heat_status = {h2_status}")
    assert h2_status == "FAIL", f"REGRESSION: Expected 'FAIL', got '{h2_status}'"
    
    # PART-H3: Heat treatment missing
    h3 = results_by_part["PART-H3"]
    h3_status = h3["heat"]["status"]
    print(f"  PART-H3 (Heat treatment missing): heat_status = {h3_status}")
    assert h3_status == "MISSING", f"REGRESSION: Expected 'MISSING', got '{h3_status}'"
    
    print()
    print("✓ Test passed - heat treatment validation logic unchanged (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.8: Reference Exists, Material Missing from PDF
# ============================================================================

def test_preservation_reference_exists_material_missing():
    """
    Property 2: Preservation - Reference exists, material missing from PDF
    
    **Validates: Requirements 3.1**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    material code but NO material name, the system returns material_status = "MISSING".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, material missing from PDF")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 with no material name
    part_keys = {"PART-007"}
    part_details = {
        "PART-007": {
            "material_code": "EDM000136",
            "material_name": "",  # Missing
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Test part"
        }
    }
    
    # Reference table with material
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Material Name: '' (empty)")
    print(f"  Reference materials: ['EN8']")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    print(f"Output:")
    print(f"  material_status: {material_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "MISSING"
    # This must remain "MISSING" after the fix
    assert material_status == "MISSING", (
        f"REGRESSION: material_status is '{material_status}', expected 'MISSING'\n"
        f"When reference exists but PDF has no material name,\n"
        f"the status must remain 'MISSING'"
    )
    
    print("✓ Test passed - material_status is 'MISSING' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Property-Based Test: Reference Exists Cases
# ============================================================================

@given(
    material_name=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
        min_size=2,
        max_size=10
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_preservation_property_material_validation_with_reference(material_name: str):
    """
    Property 2: Preservation - Material validation with reference unchanged
    
    **Validates: Requirements 3.3, 3.4**
    
    Property-based test: For ANY material validation scenario where reference
    data exists, the logic must remain unchanged.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For any material validation with reference data, the function SHALL
    continue to validate materials correctly independent of the fix.
    """
    # Setup: Material with reference
    part_keys = {"PART-TEST"}
    part_details = {
        "PART-TEST": {
            "material_code": "EDM999999",
            "material_name": material_name.strip(),
            "finish": "TEST",
            "heat_treatment": "",
            "description": "Test"
        }
    }
    
    reference_table = [
        {
            "edm": "EDM999999",
            "materials": ["EXPECTED"],  # Different from input
            "finish": ["TEST"],
            "heat": "NA"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    material_status = result["material"]["status"]
    
    # Expected behavior: "FAIL" when material doesn't match reference
    assert material_status == "FAIL", (
        f"REGRESSION for material '{material_name}':\n"
        f"  material_status is '{material_status}', expected 'FAIL'\n"
        f"  Material validation logic must remain unchanged"
    )


@given(
    finish=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        min_size=2,
        max_size=30
    ).filter(lambda x: x.strip() != "" and x.strip().upper() != "TEST")
)
@settings(max_examples=50)
def test_preservation_property_finish_validation_with_reference(finish: str):
    """
    Property 2: Preservation - Finish validation with reference unchanged
    
    **Validates: Requirements 3.5, 3.6**
    
    Property-based test: For ANY finish validation scenario where reference
    data exists, the logic must remain unchanged.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For any finish validation with reference data, the function SHALL
    continue to validate finish correctly independent of the fix.
    """
    # Setup: Material with reference
    part_keys = {"PART-TEST"}
    part_details = {
        "PART-TEST": {
            "material_code": "EDM999999",
            "material_name": "TEST",
            "finish": finish.strip(),
            "heat_treatment": "",
            "description": "Test"
        }
    }
    
    reference_table = [
        {
            "edm": "EDM999999",
            "materials": ["TEST"],
            "finish": ["TEST"],  # Different from input
            "heat": "NA"
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    finish_status = result["finish"]["status"]
    
    # Expected behavior: "FAIL" or "WARNING" when finish doesn't match reference
    assert finish_status in ["FAIL", "WARNING"], (
        f"REGRESSION for finish '{finish}':\n"
        f"  finish_status is '{finish_status}', expected 'FAIL' or 'WARNING'\n"
        f"  Finish validation logic must remain unchanged"
    )


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PRESERVATION PROPERTY TESTS")
    print("# Material/Finish Validation No Reference Fix")
    print("# CRITICAL: These tests MUST PASS on unfixed code")
    print("# They capture baseline behavior that must be preserved after the fix")
    print("#"*80)
    
    # Run concrete examples first (these provide clear output)
    try:
        test_preservation_reference_exists_material_matches()
        print("\n✓ Test 2.1 PASSED (Reference exists, material matches)")
    except AssertionError as e:
        print(f"\n✗ Test 2.1 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_material_mismatch()
        print("\n✓ Test 2.2 PASSED (Reference exists, material mismatch)")
    except AssertionError as e:
        print(f"\n✗ Test 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_finish_matches()
        print("\n✓ Test 2.3 PASSED (Reference exists, finish matches)")
    except AssertionError as e:
        print(f"\n✗ Test 2.3 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_finish_mismatch()
        print("\n✓ Test 2.4 PASSED (Reference exists, finish mismatch)")
    except AssertionError as e:
        print(f"\n✗ Test 2.4 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_pdf_no_material_data()
        print("\n✓ Test 2.5 PASSED (PDF has no material data)")
    except AssertionError as e:
        print(f"\n✗ Test 2.5 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_pdf_no_finish_data()
        print("\n✓ Test 2.6 PASSED (PDF has no finish data)")
    except AssertionError as e:
        print(f"\n✗ Test 2.6 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_heat_treatment_validation()
        print("\n✓ Test 2.7 PASSED (Heat treatment validation logic)")
    except AssertionError as e:
        print(f"\n✗ Test 2.7 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_material_missing()
        print("\n✓ Test 2.8 PASSED (Reference exists, material missing from PDF)")
    except AssertionError as e:
        print(f"\n✗ Test 2.8 FAILED: {e}")
        sys.exit(1)
    
    # Run property-based tests
    print("\n" + "="*80)
    print("Running property-based tests (50 examples each)...")
    print("="*80)
    
    try:
        test_preservation_property_material_validation_with_reference()
        print("✓ Property 2.1 PASSED (Material validation with reference - 50 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.1 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_property_finish_validation_with_reference()
        print("✓ Property 2.2 PASSED (Finish validation with reference - 50 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.2 FAILED: {e}")
        sys.exit(1)
    
    print("\n" + "#"*80)
    print("# ALL PRESERVATION TESTS PASSED")
    print("# Baseline behavior documented and verified")
    print("# These tests will ensure no regressions after the fix")
    print("#"*80)
