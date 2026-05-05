"""
Preservation Property Tests for BOM Validation Multipage Search Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

CRITICAL: These tests MUST PASS on unfixed code - they capture baseline behavior to preserve.

This test suite uses property-based testing to verify that the fix does NOT change
existing functionality for:
- BOM extraction from page 1 (index 0)
- Standard part detection (9-digit numeric part numbers)
- Matching logic (STANDARD/FOUND/MISSING classification)
- Part number normalization
- Text normalization

GOAL: Ensure no regressions are introduced by the fix.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from hypothesis import given, strategies as st, settings, assume
from services.bom_extractor import extract_bom_from_page1
from services.common import normalize_part_number, normalize_text, is_standard_part
from services.matcher import match_bom

# Test PDF file path
PDF_PATH = backend_dir.parent / "TDK040023_Lift aid of IXL1500 stator OP10.pdf"


# ============================================================================
# Property 2.1: BOM Extraction from Page 1 Preservation
# ============================================================================

def test_preservation_bom_extraction_from_page1():
    """
    Property 2: Preservation - BOM Extraction from Page 1
    
    **Validates: Requirements 3.1**
    
    Test that extract_bom_from_page1() continues to extract BOM rows correctly
    from page 1 (index 0) of the PDF, regardless of the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    This test observes and documents the current behavior:
    - BOM rows are extracted from page 1
    - Each row has item, part_number, description, qty fields
    - Part numbers are normalized correctly
    - Row positions (_row_y) are calculated
    """
    print("\n" + "="*80)
    print("TEST: Preservation - BOM Extraction from Page 1")
    print("="*80)
    print(f"PDF: {PDF_PATH}")
    print()
    
    # Verify PDF exists
    assert PDF_PATH.exists(), f"Test PDF not found: {PDF_PATH}"
    
    # Extract BOM from page 1
    print("Extracting BOM from page 1...")
    bom_rows, annotation_context = extract_bom_from_page1(str(PDF_PATH))
    
    print(f"BOM rows extracted: {len(bom_rows)}")
    print()
    
    # Verify basic structure
    assert len(bom_rows) > 0, "BOM extraction should return at least one row"
    
    # Verify each row has required fields
    for i, row in enumerate(bom_rows):
        assert "item" in row, f"Row {i} missing 'item' field"
        assert "part_number" in row, f"Row {i} missing 'part_number' field"
        assert "description" in row, f"Row {i} missing 'description' field"
        assert "qty" in row, f"Row {i} missing 'qty' field"
        assert "_row_y" in row, f"Row {i} missing '_row_y' field"
        
        # Verify part_number is normalized (uppercase, no spaces)
        pn = row["part_number"]
        assert pn == pn.upper(), f"Part number {pn} should be uppercase"
        assert " " not in pn, f"Part number {pn} should not contain spaces"
    
    # Verify annotation context has required fields
    assert "table_x0" in annotation_context
    assert "table_x1" in annotation_context
    assert "table_y0" in annotation_context
    assert "table_y1" in annotation_context
    assert "page_width" in annotation_context
    assert "page_height" in annotation_context
    assert "row_height_guess" in annotation_context
    
    print("BASELINE BEHAVIOR OBSERVED:")
    print(f"  BOM rows: {len(bom_rows)}")
    print(f"  Sample part numbers: {[row['part_number'] for row in bom_rows[:3]]}")
    print(f"  All rows have required fields: ✓")
    print(f"  Part numbers are normalized: ✓")
    print(f"  Annotation context is complete: ✓")
    print()
    print("✓ BOM extraction from page 1 works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.2: Standard Part Detection Preservation
# ============================================================================

@given(part_number=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=1, max_size=20))
@settings(max_examples=100)
def test_preservation_standard_part_detection_property(part_number: str):
    """
    Property 2: Preservation - Standard Part Detection
    
    **Validates: Requirements 3.2**
    
    Test that is_standard_part() continues to correctly identify 9-digit numeric
    part numbers as standard parts.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For all part numbers, is_standard_part() returns True if and only if
    the normalized part number is exactly 9 digits.
    """
    # Test the property
    result = is_standard_part(part_number)
    normalized = normalize_part_number(part_number)
    
    # Expected behavior: True if normalized is exactly 9 digits
    expected = bool(normalized and normalized.isdigit() and len(normalized) == 9)
    
    assert result == expected, (
        f"is_standard_part('{part_number}') returned {result}, expected {expected}. "
        f"Normalized: '{normalized}'"
    )


def test_preservation_standard_part_detection_examples():
    """
    Property 2: Preservation - Standard Part Detection (Examples)
    
    **Validates: Requirements 3.2**
    
    Test specific examples of standard part detection to document baseline behavior.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Standard Part Detection (Examples)")
    print("="*80)
    print()
    
    # Test cases: (input, expected_result)
    test_cases = [
        ("123456789", True),      # Exactly 9 digits
        ("12345678", False),      # 8 digits
        ("1234567890", False),    # 10 digits
        ("ABC123456", False),     # Contains letters
        ("123 456 789", True),    # 9 digits with spaces (normalized to 9 digits)
        ("", False),              # Empty string
        ("TDK040023-01", False),  # Part number with letters and hyphen
    ]
    
    print("BASELINE BEHAVIOR OBSERVED:")
    for input_val, expected in test_cases:
        result = is_standard_part(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} is_standard_part('{input_val}') = {result} (expected {expected})")
        assert result == expected, f"Unexpected result for '{input_val}'"
    
    print()
    print("✓ Standard part detection works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.3: Matching Logic Preservation
# ============================================================================

@given(
    bom_rows=st.lists(
        st.fixed_dictionaries({
            "item": st.integers(min_value=1, max_value=100),
            "part_number": st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Pd")), min_size=1, max_size=20),
            "description": st.text(min_size=0, max_size=50),
            "qty": st.integers(min_value=1, max_value=100),
        }),
        min_size=1,
        max_size=10,
    ),
    extracted_parts=st.sets(
        st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Pd")), min_size=1, max_size=20),
        min_size=0,
        max_size=10,
    ),
)
@settings(max_examples=100)
def test_preservation_matching_logic_property(bom_rows: List[Dict[str, Any]], extracted_parts: Set[str]):
    """
    Property 2: Preservation - Matching Logic
    
    **Validates: Requirements 3.3, 3.4**
    
    Test that match_bom() continues to correctly classify parts as STANDARD/FOUND/MISSING.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For all BOM rows and extracted part sets:
    - If part is 9-digit numeric, status is STANDARD
    - Else if part is in extracted_parts, status is FOUND
    - Else status is MISSING
    """
    # Normalize extracted parts (match_bom expects normalized keys)
    normalized_extracted = {normalize_part_number(p) for p in extracted_parts}
    
    # Run matching
    results = match_bom(bom_rows=bom_rows, extracted_part_keys=normalized_extracted)
    
    # Verify results match expected behavior
    assert len(results) == len(bom_rows), "Result count should match BOM row count"
    
    for i, (bom_row, result) in enumerate(zip(bom_rows, results)):
        pn = bom_row.get("part_number", "")
        normalized_pn = normalize_part_number(pn)
        status = result.get("status", "")
        
        # Expected behavior
        if is_standard_part(pn):
            expected_status = "STANDARD"
        elif normalized_pn in normalized_extracted:
            expected_status = "FOUND"
        else:
            expected_status = "MISSING"
        
        assert status == expected_status, (
            f"Row {i}: part '{pn}' (normalized: '{normalized_pn}') has status '{status}', "
            f"expected '{expected_status}'. "
            f"is_standard={is_standard_part(pn)}, "
            f"in_extracted={normalized_pn in normalized_extracted}"
        )


def test_preservation_matching_logic_examples():
    """
    Property 2: Preservation - Matching Logic (Examples)
    
    **Validates: Requirements 3.3, 3.4**
    
    Test specific examples of matching logic to document baseline behavior.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Matching Logic (Examples)")
    print("="*80)
    print()
    
    # Create test BOM rows
    bom_rows = [
        {"item": 1, "part_number": "123456789", "description": "Standard screw", "qty": 10},
        {"item": 2, "part_number": "TDK040023-01", "description": "Custom part", "qty": 1},
        {"item": 3, "part_number": "TDK040023-02", "description": "Another part", "qty": 2},
        {"item": 4, "part_number": "MISSING-PART", "description": "Not found", "qty": 1},
    ]
    
    # Create extracted parts set (only TDK040023-01 is found)
    extracted_parts = {"TDK040023-01"}
    
    # Run matching
    results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_parts)
    
    print("BASELINE BEHAVIOR OBSERVED:")
    for result in results:
        pn = result.get("part_number", "")
        status = result.get("status", "")
        print(f"  Part '{pn}': {status}")
    
    # Verify expected statuses
    assert results[0]["status"] == "STANDARD", "123456789 should be STANDARD"
    assert results[1]["status"] == "FOUND", "TDK040023-01 should be FOUND"
    assert results[2]["status"] == "MISSING", "TDK040023-02 should be MISSING"
    assert results[3]["status"] == "MISSING", "MISSING-PART should be MISSING"
    
    print()
    print("✓ Matching logic works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.4: Part Number Normalization Preservation
# ============================================================================

@given(part_number=st.text(min_size=0, max_size=50))
@settings(max_examples=100)
def test_preservation_part_number_normalization_property(part_number: str):
    """
    Property 2: Preservation - Part Number Normalization
    
    **Validates: Requirements 3.5**
    
    Test that normalize_part_number() continues to normalize part numbers correctly.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For all part numbers, normalize_part_number() returns:
    - Uppercase version
    - With all whitespace removed
    - Empty string if input is None or empty
    """
    result = normalize_part_number(part_number)
    
    # Expected behavior
    if not part_number:
        assert result == "", f"Empty input should return empty string, got '{result}'"
    else:
        # Should be uppercase
        assert result == result.upper(), f"Result should be uppercase: '{result}'"
        # Should have no whitespace
        assert " " not in result, f"Result should have no spaces: '{result}'"
        assert "\t" not in result, f"Result should have no tabs: '{result}'"
        assert "\n" not in result, f"Result should have no newlines: '{result}'"


def test_preservation_part_number_normalization_examples():
    """
    Property 2: Preservation - Part Number Normalization (Examples)
    
    **Validates: Requirements 3.5**
    
    Test specific examples of part number normalization to document baseline behavior.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Part Number Normalization (Examples)")
    print("="*80)
    print()
    
    # Test cases: (input, expected_output)
    test_cases = [
        ("TDK040023-01", "TDK040023-01"),
        ("tdk040023-01", "TDK040023-01"),
        ("TDK 040023 01", "TDK04002301"),
        ("  TDK040023-01  ", "TDK040023-01"),
        ("TDK\t040023\n01", "TDK04002301"),
        ("", ""),
        ("123 456 789", "123456789"),
    ]
    
    print("BASELINE BEHAVIOR OBSERVED:")
    for input_val, expected in test_cases:
        result = normalize_part_number(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_part_number('{repr(input_val)}') = '{result}' (expected '{expected}')")
        assert result == expected, f"Unexpected result for '{input_val}'"
    
    print()
    print("✓ Part number normalization works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.5: Text Normalization Preservation
# ============================================================================

@given(text=st.text(min_size=0, max_size=100))
@settings(max_examples=100)
def test_preservation_text_normalization_property(text: str):
    """
    Property 2: Preservation - Text Normalization
    
    **Validates: Requirements 3.6**
    
    Test that normalize_text() continues to normalize text correctly.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For all text, normalize_text() returns:
    - Uppercase version
    - With whitespace collapsed to single spaces
    - Trimmed of leading/trailing whitespace
    - Empty string if input is None or empty
    """
    result = normalize_text(text)
    
    # Expected behavior
    if not text:
        assert result == "", f"Empty input should return empty string, got '{result}'"
    else:
        # Should be uppercase
        assert result == result.upper(), f"Result should be uppercase: '{result}'"
        # Should not have leading/trailing whitespace
        assert result == result.strip(), f"Result should be trimmed: '{result}'"
        # Should not have multiple consecutive spaces
        assert "  " not in result, f"Result should not have multiple spaces: '{result}'"


def test_preservation_text_normalization_examples():
    """
    Property 2: Preservation - Text Normalization (Examples)
    
    **Validates: Requirements 3.6**
    
    Test specific examples of text normalization to document baseline behavior.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Text Normalization (Examples)")
    print("="*80)
    print()
    
    # Test cases: (input, expected_output)
    test_cases = [
        ("PART NUMBER", "PART NUMBER"),
        ("part number", "PART NUMBER"),
        ("  PART   NUMBER  ", "PART NUMBER"),
        ("PART\tNUMBER", "PART NUMBER"),
        ("PART\nNUMBER", "PART NUMBER"),
        ("", ""),
        ("  ", ""),
    ]
    
    print("BASELINE BEHAVIOR OBSERVED:")
    for input_val, expected in test_cases:
        result = normalize_text(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_text('{repr(input_val)}') = '{result}' (expected '{expected}')")
        assert result == expected, f"Unexpected result for '{input_val}'"
    
    print()
    print("✓ Text normalization works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PRESERVATION PROPERTY TESTS")
    print("# CRITICAL: These tests MUST PASS on unfixed code")
    print("# They capture baseline behavior that must be preserved after the fix")
    print("#"*80)
    
    # Run example-based tests (these provide clear output)
    try:
        test_preservation_bom_extraction_from_page1()
        print("\n✓ Test 2.1 PASSED (BOM Extraction)")
    except AssertionError as e:
        print(f"\n✗ Test 2.1 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_standard_part_detection_examples()
        print("\n✓ Test 2.2 PASSED (Standard Part Detection - Examples)")
    except AssertionError as e:
        print(f"\n✗ Test 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_matching_logic_examples()
        print("\n✓ Test 2.3 PASSED (Matching Logic - Examples)")
    except AssertionError as e:
        print(f"\n✗ Test 2.3 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_part_number_normalization_examples()
        print("\n✓ Test 2.4 PASSED (Part Number Normalization - Examples)")
    except AssertionError as e:
        print(f"\n✗ Test 2.4 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_text_normalization_examples()
        print("\n✓ Test 2.5 PASSED (Text Normalization - Examples)")
    except AssertionError as e:
        print(f"\n✗ Test 2.5 FAILED: {e}")
        sys.exit(1)
    
    # Run property-based tests (these generate many test cases)
    print("\n" + "="*80)
    print("Running property-based tests (100 examples each)...")
    print("="*80)
    
    try:
        test_preservation_standard_part_detection_property()
        print("✓ Property 2.2 PASSED (Standard Part Detection - 100 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_matching_logic_property()
        print("✓ Property 2.3 PASSED (Matching Logic - 100 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.3 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_part_number_normalization_property()
        print("✓ Property 2.4 PASSED (Part Number Normalization - 100 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.4 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_text_normalization_property()
        print("✓ Property 2.5 PASSED (Text Normalization - 100 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.5 FAILED: {e}")
        sys.exit(1)
    
    print("\n" + "#"*80)
    print("# ALL PRESERVATION TESTS PASSED")
    print("# Baseline behavior documented and verified")
    print("# These tests will ensure no regressions after the fix")
    print("#"*80)
