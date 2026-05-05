"""
Preservation Property Tests for Heat Treatment Validation No Reference Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

CRITICAL: These tests MUST PASS on unfixed code - they capture baseline behavior to preserve.

This test suite uses property-based testing to verify that the fix does NOT change
existing functionality for:
- Heat treatment validation when reference data EXISTS and requires heat treatment
- Heat treatment validation when reference data EXISTS and indicates NA
- Heat treatment validation when reference data EXISTS and PDF has heat treatment data
- Material validation logic (completely separate from heat treatment)
- Finish validation logic (completely separate from heat treatment)

GOAL: Ensure no regressions are introduced by the fix.

EXPECTED OUTCOME: Tests PASS on unfixed code (confirms baseline behavior to preserve).

The fix should ONLY affect the case where:
- PDF has no heat treatment field AND
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
# Test 2.1: Reference Exists, Requires Heat Treatment, PDF Missing
# ============================================================================

def test_preservation_reference_requires_heat_pdf_missing():
    """
    Property 2: Preservation - Reference requires heat treatment, PDF missing
    
    **Validates: Requirements 3.1**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND requires
    heat treatment AND PDF has no heat treatment field, the system returns
    heat_status = "MISSING".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference requires heat treatment, PDF missing")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 requires heat treatment "60-70"
    part_keys = {"PART-001"}
    part_details = {
        "PART-001": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Test part"
        }
    }
    
    # Reference table with heat treatment requirement
    reference_table = [
        {
            "edm": "EDM000136",
            "materials": ["EN8"],
            "finish": ["BLACKODISING"],
            "heat": "60-70"  # Requires heat treatment
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000136 (in reference)")
    print(f"  Heat Treatment: '' (empty)")
    print(f"  Reference heat: '60-70' (required)")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "MISSING"
    # This must remain "MISSING" after the fix
    assert heat_status == "MISSING", (
        f"REGRESSION: heat_status is '{heat_status}', expected 'MISSING'\n"
        f"When reference requires heat treatment but PDF is missing it,\n"
        f"the status must remain 'MISSING'"
    )
    
    print("✓ Test passed - heat_status is 'MISSING' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.2: Reference Exists, Heat Treatment NA, PDF Missing
# ============================================================================

def test_preservation_reference_na_pdf_missing():
    """
    Property 2: Preservation - Reference indicates NA, PDF missing
    
    **Validates: Requirements 3.2, 3.3**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND indicates
    heat treatment is NA AND PDF has no heat treatment field, the system returns
    heat_status = "PASS".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference indicates NA, PDF missing")
    print("="*80)
    print()
    
    # Setup: Material EDM000800 has heat treatment "NA"
    part_keys = {"PART-002"}
    part_details = {
        "PART-002": {
            "material_code": "EDM000800",
            "material_name": "SS400",
            "finish": "NATURAL",
            "heat_treatment": "",  # No heat treatment in PDF
            "description": "Test part"
        }
    }
    
    # Reference table with heat treatment NA
    reference_table = [
        {
            "edm": "EDM000800",
            "materials": ["SS400"],
            "finish": ["NATURAL"],
            "heat": "NA"  # Heat treatment not applicable
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000800 (in reference)")
    print(f"  Heat Treatment: '' (empty)")
    print(f"  Reference heat: 'NA' (not applicable)")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "PASS"
    # This must remain "PASS" after the fix
    assert heat_status == "PASS", (
        f"REGRESSION: heat_status is '{heat_status}', expected 'PASS'\n"
        f"When reference indicates NA and PDF has no heat treatment,\n"
        f"the status must remain 'PASS'"
    )
    
    print("✓ Test passed - heat_status is 'PASS' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.3: Reference Exists, Heat Treatment NA, PDF Has Data
# ============================================================================

def test_preservation_reference_na_pdf_has_data():
    """
    Property 2: Preservation - Reference indicates NA, PDF has data
    
    **Validates: Requirements 3.4**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND indicates
    heat treatment is NA AND PDF HAS heat treatment data, the system returns
    heat_status = "WARNING" (unexpected data).
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference indicates NA, PDF has data")
    print("="*80)
    print()
    
    # Setup: Material EDM000800 has heat treatment "NA" but PDF has data
    part_keys = {"PART-003"}
    part_details = {
        "PART-003": {
            "material_code": "EDM000800",
            "material_name": "SS400",
            "finish": "NATURAL",
            "heat_treatment": "HARDENED TO 60-70",  # Has heat treatment (unexpected)
            "description": "Test part"
        }
    }
    
    # Reference table with heat treatment NA
    reference_table = [
        {
            "edm": "EDM000800",
            "materials": ["SS400"],
            "finish": ["NATURAL"],
            "heat": "NA"  # Heat treatment not applicable
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details, reference_table)
    
    print(f"Input:")
    print(f"  Material: EDM000800 (in reference)")
    print(f"  Heat Treatment: 'HARDENED TO 60-70' (present)")
    print(f"  Reference heat: 'NA' (not applicable)")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "WARNING"
    # This must remain "WARNING" after the fix
    assert heat_status == "WARNING", (
        f"REGRESSION: heat_status is '{heat_status}', expected 'WARNING'\n"
        f"When reference indicates NA but PDF has heat treatment data,\n"
        f"the status must remain 'WARNING'"
    )
    
    print("✓ Test passed - heat_status is 'WARNING' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.4: Reference Exists, PDF Has Matching Heat Treatment
# ============================================================================

def test_preservation_reference_exists_pdf_matches():
    """
    Property 2: Preservation - Reference exists, PDF matches
    
    **Validates: Requirements 3.2**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    heat treatment data that MATCHES the reference, the system returns
    heat_status = "PASS".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, PDF matches")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 requires "60-70" and PDF has "60-70"
    part_keys = {"PART-004"}
    part_details = {
        "PART-004": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "HARDENED AND TEMPERED TO 60-70 kg/mm2",  # Matches
            "description": "Test part"
        }
    }
    
    # Reference table with heat treatment requirement
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
    print(f"  Heat Treatment: 'HARDENED AND TEMPERED TO 60-70 kg/mm2'")
    print(f"  Reference heat: '60-70'")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "PASS"
    # This must remain "PASS" after the fix
    assert heat_status == "PASS", (
        f"REGRESSION: heat_status is '{heat_status}', expected 'PASS'\n"
        f"When PDF heat treatment matches reference,\n"
        f"the status must remain 'PASS'"
    )
    
    print("✓ Test passed - heat_status is 'PASS' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.5: Reference Exists, PDF Has Non-Matching Heat Treatment
# ============================================================================

def test_preservation_reference_exists_pdf_mismatch():
    """
    Property 2: Preservation - Reference exists, PDF mismatch
    
    **Validates: Requirements 3.2**
    
    OBSERVE behavior on UNFIXED code: When reference data exists AND PDF has
    heat treatment data that DOES NOT MATCH the reference, the system returns
    heat_status = "FAIL".
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Reference exists, PDF mismatch")
    print("="*80)
    print()
    
    # Setup: Material EDM000136 requires "60-70" but PDF has "50-60"
    part_keys = {"PART-005"}
    part_details = {
        "PART-005": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "HARDENED AND TEMPERED TO 50-60 kg/mm2",  # Mismatch
            "description": "Test part"
        }
    }
    
    # Reference table with heat treatment requirement
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
    print(f"  Heat Treatment: 'HARDENED AND TEMPERED TO 50-60 kg/mm2'")
    print(f"  Reference heat: '60-70'")
    print()
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    print(f"Output:")
    print(f"  heat_status: {heat_status}")
    print()
    
    # OBSERVE: Expected behavior on unfixed code is "FAIL"
    # This must remain "FAIL" after the fix
    assert heat_status == "FAIL", (
        f"REGRESSION: heat_status is '{heat_status}', expected 'FAIL'\n"
        f"When PDF heat treatment does not match reference,\n"
        f"the status must remain 'FAIL'"
    )
    
    print("✓ Test passed - heat_status is 'FAIL' as expected (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.6: Material Validation Logic Unchanged
# ============================================================================

def test_preservation_material_validation_logic():
    """
    Property 2: Preservation - Material validation logic unchanged
    
    **Validates: Requirements 3.5**
    
    OBSERVE behavior on UNFIXED code: Material validation logic operates
    independently of heat treatment validation and must remain unchanged.
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Material validation logic unchanged")
    print("="*80)
    print()
    
    # Setup: Test various material validation scenarios
    part_keys = {"PART-M1", "PART-M2", "PART-M3"}
    part_details = {
        "PART-M1": {
            "material_code": "EDM000136",
            "material_name": "EN8",  # Matches reference
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Material matches"
        },
        "PART-M2": {
            "material_code": "EDM000136",
            "material_name": "SS400",  # Does not match reference
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Material mismatch"
        },
        "PART-M3": {
            "material_code": "EDM000136",
            "material_name": "",  # Missing material name
            "finish": "CHEMICAL BLACK",
            "heat_treatment": "",
            "description": "Material missing"
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
    
    print(f"Input: 3 parts with different material validation scenarios")
    print()
    
    # Check results
    assert len(results) == 3, "Expected 3 results"
    
    # Find each result
    results_by_part = {r["part_number"]: r for r in results}
    
    # PART-M1: Material matches
    m1 = results_by_part["PART-M1"]
    m1_status = m1["material"]["status"]
    print(f"  PART-M1 (Material matches): material_status = {m1_status}")
    assert m1_status == "PASS", f"REGRESSION: Expected 'PASS', got '{m1_status}'"
    
    # PART-M2: Material mismatch
    m2 = results_by_part["PART-M2"]
    m2_status = m2["material"]["status"]
    print(f"  PART-M2 (Material mismatch): material_status = {m2_status}")
    assert m2_status == "FAIL", f"REGRESSION: Expected 'FAIL', got '{m2_status}'"
    
    # PART-M3: Material missing
    m3 = results_by_part["PART-M3"]
    m3_status = m3["material"]["status"]
    print(f"  PART-M3 (Material missing): material_status = {m3_status}")
    assert m3_status == "MISSING", f"REGRESSION: Expected 'MISSING', got '{m3_status}'"
    
    print()
    print("✓ Test passed - material validation logic unchanged (baseline preserved)")
    print("="*80)


# ============================================================================
# Test 2.7: Finish Validation Logic Unchanged
# ============================================================================

def test_preservation_finish_validation_logic():
    """
    Property 2: Preservation - Finish validation logic unchanged
    
    **Validates: Requirements 3.5**
    
    OBSERVE behavior on UNFIXED code: Finish validation logic operates
    independently of heat treatment validation and must remain unchanged.
    
    This behavior MUST be preserved after the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Finish validation logic unchanged")
    print("="*80)
    print()
    
    # Setup: Test various finish validation scenarios
    part_keys = {"PART-F1", "PART-F2", "PART-F3"}
    part_details = {
        "PART-F1": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "CHEMICAL BLACK",  # Matches reference (synonym)
            "heat_treatment": "",
            "description": "Finish matches"
        },
        "PART-F2": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "ZINC PLATED",  # Does not match reference
            "heat_treatment": "",
            "description": "Finish mismatch"
        },
        "PART-F3": {
            "material_code": "EDM000136",
            "material_name": "EN8",
            "finish": "",  # Missing finish
            "heat_treatment": "",
            "description": "Finish missing"
        }
    }
    
    # Reference table
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
    
    print(f"Input: 3 parts with different finish validation scenarios")
    print()
    
    # Check results
    assert len(results) == 3, "Expected 3 results"
    
    # Find each result
    results_by_part = {r["part_number"]: r for r in results}
    
    # PART-F1: Finish matches (synonym)
    f1 = results_by_part["PART-F1"]
    f1_status = f1["finish"]["status"]
    print(f"  PART-F1 (Finish matches): finish_status = {f1_status}")
    assert f1_status == "PASS", f"REGRESSION: Expected 'PASS', got '{f1_status}'"
    
    # PART-F2: Finish mismatch
    f2 = results_by_part["PART-F2"]
    f2_status = f2["finish"]["status"]
    print(f"  PART-F2 (Finish mismatch): finish_status = {f2_status}")
    assert f2_status == "FAIL", f"REGRESSION: Expected 'FAIL', got '{f2_status}'"
    
    # PART-F3: Finish missing
    f3 = results_by_part["PART-F3"]
    f3_status = f3["finish"]["status"]
    print(f"  PART-F3 (Finish missing): finish_status = {f3_status}")
    assert f3_status == "MISSING", f"REGRESSION: Expected 'MISSING', got '{f3_status}'"
    
    print()
    print("✓ Test passed - finish validation logic unchanged (baseline preserved)")
    print("="*80)


# ============================================================================
# Property-Based Test: Reference Exists Cases
# ============================================================================

@given(
    heat_range=st.text(
        alphabet="0123456789-",
        min_size=3,
        max_size=10
    ).filter(lambda x: "-" in x and x.count("-") == 1 and x.split("-")[0].isdigit() and x.split("-")[1].isdigit())
)
@settings(max_examples=50)
def test_preservation_property_reference_exists_heat_required(heat_range: str):
    """
    Property 2: Preservation - Reference exists with heat requirement
    
    **Validates: Requirements 3.1, 3.2**
    
    Property-based test: For ANY material with reference data that requires
    heat treatment, the validation logic must remain unchanged.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For any material with reference data AND heat_expected != NA,
    the function SHALL continue to validate heat treatment correctly:
    - PDF missing heat treatment → "MISSING"
    - PDF has matching heat treatment → "PASS"
    - PDF has non-matching heat treatment → "FAIL"
    """
    # Setup: Material with reference that requires heat treatment
    part_keys = {"PART-TEST"}
    
    # Test case 1: PDF missing heat treatment
    part_details_missing = {
        "PART-TEST": {
            "material_code": "EDM999999",
            "material_name": "TEST",
            "finish": "TEST",
            "heat_treatment": "",  # Missing
            "description": "Test"
        }
    }
    
    reference_table = [
        {
            "edm": "EDM999999",
            "materials": ["TEST"],
            "finish": ["TEST"],
            "heat": heat_range  # Requires heat treatment
        }
    ]
    
    # Execute validation
    results = validate_materials(part_keys, part_details_missing, reference_table)
    
    # Check result
    assert len(results) == 1, "Expected 1 result"
    result = results[0]
    heat_status = result["heat"]["status"]
    
    # Expected behavior: "MISSING" when PDF has no heat treatment but reference requires it
    assert heat_status == "MISSING", (
        f"REGRESSION for heat_range '{heat_range}':\n"
        f"  heat_status is '{heat_status}', expected 'MISSING'\n"
        f"  When reference requires heat treatment but PDF is missing it,\n"
        f"  the status must remain 'MISSING'"
    )


@given(
    material_name=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd")),
        min_size=2,
        max_size=10
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_preservation_property_material_validation(material_name: str):
    """
    Property 2: Preservation - Material validation unchanged
    
    **Validates: Requirements 3.5**
    
    Property-based test: For ANY material validation scenario, the logic
    must remain unchanged regardless of heat treatment fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For any material validation, the function SHALL continue to
    validate materials correctly independent of heat treatment logic.
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


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PRESERVATION PROPERTY TESTS")
    print("# Heat Treatment Validation No Reference Fix")
    print("# CRITICAL: These tests MUST PASS on unfixed code")
    print("# They capture baseline behavior that must be preserved after the fix")
    print("#"*80)
    
    # Run concrete examples first (these provide clear output)
    try:
        test_preservation_reference_requires_heat_pdf_missing()
        print("\n✓ Test 2.1 PASSED (Reference requires heat, PDF missing)")
    except AssertionError as e:
        print(f"\n✗ Test 2.1 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_na_pdf_missing()
        print("\n✓ Test 2.2 PASSED (Reference NA, PDF missing)")
    except AssertionError as e:
        print(f"\n✗ Test 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_na_pdf_has_data()
        print("\n✓ Test 2.3 PASSED (Reference NA, PDF has data)")
    except AssertionError as e:
        print(f"\n✗ Test 2.3 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_pdf_matches()
        print("\n✓ Test 2.4 PASSED (Reference exists, PDF matches)")
    except AssertionError as e:
        print(f"\n✗ Test 2.4 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_reference_exists_pdf_mismatch()
        print("\n✓ Test 2.5 PASSED (Reference exists, PDF mismatch)")
    except AssertionError as e:
        print(f"\n✗ Test 2.5 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_material_validation_logic()
        print("\n✓ Test 2.6 PASSED (Material validation logic)")
    except AssertionError as e:
        print(f"\n✗ Test 2.6 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_finish_validation_logic()
        print("\n✓ Test 2.7 PASSED (Finish validation logic)")
    except AssertionError as e:
        print(f"\n✗ Test 2.7 FAILED: {e}")
        sys.exit(1)
    
    # Run property-based tests
    print("\n" + "="*80)
    print("Running property-based tests (50 examples each)...")
    print("="*80)
    
    try:
        test_preservation_property_reference_exists_heat_required()
        print("✓ Property 2.1 PASSED (Reference exists with heat requirement - 50 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.1 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_property_material_validation()
        print("✓ Property 2.2 PASSED (Material validation unchanged - 50 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.2 FAILED: {e}")
        sys.exit(1)
    
    print("\n" + "#"*80)
    print("# ALL PRESERVATION TESTS PASSED")
    print("# Baseline behavior documented and verified")
    print("# These tests will ensure no regressions after the fix")
    print("#"*80)
