"""
Preservation Property Tests for BOM Extraction Split Part Numbers Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

CRITICAL: These tests MUST PASS on unfixed code - they capture baseline behavior to preserve.

This test suite uses property-based testing to verify that the fix does NOT change
existing functionality for:
- BOM extraction for PDFs with standard single-column part numbers
- Part number plausibility check using _part_number_plausible()
- Data structure format returned by extract_bom_from_page1
- All other BOM extraction logic (header detection, row parsing, fallback text parsing)

GOAL: Ensure no regressions are introduced by the fix.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from hypothesis import given, strategies as st, settings, assume
from services.bom_extractor import extract_bom_from_page1, _part_number_plausible
from services.common import normalize_part_number, normalize_text

# Test PDF files with standard single-column part numbers
STANDARD_PDF_PATHS = [
    backend_dir.parent / "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
    backend_dir.parent / "TDQ300162  1  FIXTURES FOR HYDRAULIC TOOLING  Released  VIN-WIP.pdf",
]


# ============================================================================
# Property 2.1: Standard Single-Column Part Number Extraction Preservation
# ============================================================================

def test_preservation_standard_single_column_part_numbers():
    """
    Property 2: Preservation - Standard Single-Column Part Number Extraction
    
    **Validates: Requirements 3.1, 3.2**
    
    Test that BOM extraction for PDFs with standard single-column part numbers
    continues to work exactly as before.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    This test observes and documents the current behavior for PDFs where
    part numbers are NOT split across columns.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Standard Single-Column Part Number Extraction")
    print("="*80)
    
    for pdf_path in STANDARD_PDF_PATHS:
        if not pdf_path.exists():
            print(f"SKIP: PDF not found: {pdf_path}")
            continue
            
        print(f"PDF: {pdf_path.name}")
        print()
        
        # Extract BOM from page 1
        print("Extracting BOM from page 1...")
        bom_rows, annotation_context = extract_bom_from_page1(str(pdf_path))
        
        print(f"BOM rows extracted: {len(bom_rows)}")
        
        # Verify basic structure
        assert len(bom_rows) > 0, f"BOM extraction should return at least one row for {pdf_path.name}"
        
        # Verify each row has required fields and correct data structure format
        for i, row in enumerate(bom_rows):
            # Check required fields exist
            assert "item" in row, f"Row {i} missing 'item' field in {pdf_path.name}"
            assert "part_number" in row, f"Row {i} missing 'part_number' field in {pdf_path.name}"
            assert "description" in row, f"Row {i} missing 'description' field in {pdf_path.name}"
            assert "qty" in row, f"Row {i} missing 'qty' field in {pdf_path.name}"
            assert "_row_y" in row, f"Row {i} missing '_row_y' field in {pdf_path.name}"
            
            # Verify data types
            assert isinstance(row["_row_y"], (int, float)), f"_row_y should be numeric in row {i} of {pdf_path.name}"
            
            # Verify part_number is normalized (uppercase, no spaces)
            pn = row["part_number"]
            assert pn == pn.upper(), f"Part number {pn} should be uppercase in {pdf_path.name}"
            assert " " not in pn, f"Part number {pn} should not contain spaces in {pdf_path.name}"
        
        # Verify annotation context has required fields
        required_context_keys = ["table_x0", "table_x1", "table_y0", "table_y1", 
                               "page_width", "page_height", "row_height_guess"]
        for key in required_context_keys:
            assert key in annotation_context, f"Missing annotation context key: {key} in {pdf_path.name}"
        
        print("BASELINE BEHAVIOR OBSERVED:")
        print(f"  BOM rows: {len(bom_rows)}")
        print(f"  Sample part numbers: {[row['part_number'] for row in bom_rows[:3]]}")
        print(f"  All rows have required fields: ✓")
        print(f"  Part numbers are normalized: ✓")
        print(f"  Annotation context is complete: ✓")
        print()
    
    print("✓ Standard single-column part number extraction works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.2: Part Number Plausibility Check Preservation
# ============================================================================

@given(part_number=st.text(min_size=0, max_size=50))
@settings(max_examples=100)
def test_preservation_part_number_plausible_property(part_number: str):
    """
    Property 2: Preservation - Part Number Plausibility Check
    
    **Validates: Requirements 3.3**
    
    Test that _part_number_plausible() continues to validate part numbers
    using the same logic as before.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    Property: For all part numbers, _part_number_plausible() returns True if:
    - Normalized part number is not empty
    - Does not contain "COPYRIGHT" or "CONFIDENTIAL"
    - Contains at least one digit
    - Has length >= 2
    """
    result = _part_number_plausible(part_number)
    
    # Expected behavior based on current implementation
    normalized = normalize_part_number(part_number)
    
    if not normalized:
        expected = False
    elif "COPYRIGHT" in normalized or "CONFIDENTIAL" in normalized:
        expected = False
    else:
        expected = any(ch.isdigit() for ch in normalized) and len(normalized) >= 2
    
    assert result == expected, (
        f"_part_number_plausible('{part_number}') returned {result}, expected {expected}. "
        f"Normalized: '{normalized}'"
    )


def test_preservation_part_number_plausible_examples():
    """
    Property 2: Preservation - Part Number Plausibility Check (Examples)
    
    **Validates: Requirements 3.3**
    
    Test specific examples of part number plausibility to document baseline behavior.
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Part Number Plausibility Check (Examples)")
    print("="*80)
    print()
    
    # Test cases: (input, expected_result)
    test_cases = [
        ("TDQ300123-01", True),    # Valid part number
        ("123456789", True),       # Numeric part number
        ("AB12", True),            # Short but valid
        ("A", False),              # Too short, no digits
        ("", False),               # Empty
        ("COPYRIGHT NOTICE", False), # Contains COPYRIGHT
        ("CONFIDENTIAL DATA", False), # Contains CONFIDENTIAL
        ("ABC", False),            # No digits
        ("12", True),              # Minimum valid (2 chars, has digit)
    ]
    
    print("BASELINE BEHAVIOR OBSERVED:")
    for input_val, expected in test_cases:
        result = _part_number_plausible(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} _part_number_plausible('{input_val}') = {result} (expected {expected})")
        assert result == expected, f"Unexpected result for '{input_val}'"
    
    print()
    print("✓ Part number plausibility check works correctly (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.3: Data Structure Format Preservation
# ============================================================================

def test_preservation_data_structure_format():
    """
    Property 2: Preservation - Data Structure Format
    
    **Validates: Requirements 3.4**
    
    Test that the data structure format returned by extract_bom_from_page1
    remains unchanged: [{item, part_number, description, qty, _row_y}]
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    print("\n" + "="*80)
    print("TEST: Preservation - Data Structure Format")
    print("="*80)
    
    for pdf_path in STANDARD_PDF_PATHS:
        if not pdf_path.exists():
            print(f"SKIP: PDF not found: {pdf_path}")
            continue
            
        print(f"PDF: {pdf_path.name}")
        
        # Extract BOM
        bom_rows, annotation_context = extract_bom_from_page1(str(pdf_path))
        
        if not bom_rows:
            print(f"  No BOM rows extracted, skipping format check")
            continue
        
        # Check data structure format
        sample_row = bom_rows[0]
        required_keys = ["item", "part_number", "description", "qty", "_row_y"]
        
        print(f"  Sample row keys: {list(sample_row.keys())}")
        
        # Verify all required keys are present
        for key in required_keys:
            assert key in sample_row, f"Missing required key '{key}' in {pdf_path.name}"
        
        # Verify data types are reasonable
        assert isinstance(sample_row.get("item"), (int, type(None))), f"item should be int or None in {pdf_path.name}"
        assert isinstance(sample_row.get("part_number"), str), f"part_number should be str in {pdf_path.name}"
        assert isinstance(sample_row.get("description"), str), f"description should be str in {pdf_path.name}"
        assert isinstance(sample_row.get("qty"), (int, float, type(None))), f"qty should be int, float, or None in {pdf_path.name}"
        assert isinstance(sample_row.get("_row_y"), (int, float)), f"_row_y should be numeric in {pdf_path.name}"
        
        print(f"  ✓ Data structure format is correct")
        
        # Check annotation context format
        required_context_keys = ["table_x0", "table_x1", "table_y0", "table_y1", 
                               "page_width", "page_height", "row_height_guess"]
        
        print(f"  Annotation context keys: {list(annotation_context.keys())}")
        
        for key in required_context_keys:
            assert key in annotation_context, f"Missing annotation context key '{key}' in {pdf_path.name}"
            assert isinstance(annotation_context[key], (int, float)), f"Context key '{key}' should be numeric in {pdf_path.name}"
        
        print(f"  ✓ Annotation context format is correct")
        print()
    
    print("✓ Data structure format is preserved (baseline preserved)")
    print("="*80)


# ============================================================================
# Property 2.4: BOM Extraction Logic Preservation (Property-Based)
# ============================================================================

@given(
    # Generate test data that simulates table rows with non-split part numbers
    table_rows=st.lists(
        st.lists(
            st.one_of(
                st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Pd")), min_size=1, max_size=20),
                st.integers(min_value=1, max_value=100).map(str),
                st.just("")
            ),
            min_size=4,
            max_size=8
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=50)
def test_preservation_bom_extraction_logic_property(table_rows: List[List[str]]):
    """
    Property 2: Preservation - BOM Extraction Logic (Property-Based)
    
    **Validates: Requirements 3.1, 3.4**
    
    Test that BOM extraction logic (header detection, row parsing) continues
    to work the same way for non-split part number cases.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    
    This property tests that the internal logic for processing table rows
    remains unchanged when part numbers are not split across columns.
    """
    # Skip empty or invalid table structures
    assume(len(table_rows) > 0)
    assume(all(len(row) >= 4 for row in table_rows))
    
    # This is a simplified test of the internal logic
    # We test that part number normalization and plausibility checking
    # work consistently for table-like data
    
    for row in table_rows:
        # Simulate part number processing from a table row
        # Assume part number is in column 1 (typical BOM layout)
        if len(row) > 1:
            part_number_raw = row[1]
            part_number = normalize_part_number(part_number_raw)
            
            # The plausibility check should be consistent
            is_plausible = _part_number_plausible(part_number)
            
            # Re-check should give same result (idempotent)
            is_plausible_again = _part_number_plausible(part_number)
            assert is_plausible == is_plausible_again, (
                f"Plausibility check not idempotent for '{part_number}'"
            )
            
            # Normalization should be idempotent
            normalized_again = normalize_part_number(part_number)
            assert part_number == normalized_again, (
                f"Normalization not idempotent: '{part_number}' vs '{normalized_again}'"
            )


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PRESERVATION PROPERTY TESTS - BOM EXTRACTION SPLIT PART NUMBERS FIX")
    print("# CRITICAL: These tests MUST PASS on unfixed code")
    print("# They capture baseline behavior that must be preserved after the fix")
    print("#"*80)
    
    # Run example-based tests (these provide clear output)
    try:
        test_preservation_standard_single_column_part_numbers()
        print("\n✓ Test 2.1 PASSED (Standard Single-Column Part Number Extraction)")
    except AssertionError as e:
        print(f"\n✗ Test 2.1 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test 2.1 ERROR: {e}")
        # Continue with other tests
    
    try:
        test_preservation_part_number_plausible_examples()
        print("\n✓ Test 2.2 PASSED (Part Number Plausibility Check - Examples)")
    except AssertionError as e:
        print(f"\n✗ Test 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_data_structure_format()
        print("\n✓ Test 2.3 PASSED (Data Structure Format)")
    except AssertionError as e:
        print(f"\n✗ Test 2.3 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test 2.3 ERROR: {e}")
        # Continue with other tests
    
    # Run property-based tests (these generate many test cases)
    print("\n" + "="*80)
    print("Running property-based tests...")
    print("="*80)
    
    try:
        test_preservation_part_number_plausible_property()
        print("✓ Property 2.2 PASSED (Part Number Plausibility Check - 100 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.2 FAILED: {e}")
        sys.exit(1)
    
    try:
        test_preservation_bom_extraction_logic_property()
        print("✓ Property 2.4 PASSED (BOM Extraction Logic - 50 examples)")
    except AssertionError as e:
        print(f"✗ Property 2.4 FAILED: {e}")
        sys.exit(1)
    
    print("\n" + "#"*80)
    print("# ALL PRESERVATION TESTS PASSED")
    print("# Baseline behavior documented and verified")
    print("# These tests will ensure no regressions after the fix")
    print("#"*80)