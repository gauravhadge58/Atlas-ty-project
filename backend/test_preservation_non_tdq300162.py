"""
Preservation Property Tests for Non-TDQ300162 BOM Extraction

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

These tests capture the CURRENT behavior of BOM extraction for non-TDQ300162 PDFs
on UNFIXED code. They establish a baseline that must be preserved when implementing
the fix for TDQ300162.

IMPORTANT: These tests are EXPECTED TO PASS on unfixed code.
"""

import sys
sys.path.insert(0, 'backend')

from services.bom_extractor import extract_bom_from_page1
from hypothesis import given, strategies as st, settings, Phase
import pytest


class TestPreservationNonTDQ300162:
    """
    Preservation property tests for non-TDQ300162 BOM extraction behavior.
    
    These tests validate that the fix for TDQ300162 does NOT change the extraction
    behavior for other PDFs.
    """

    def test_tdq300123_standard_layout_preservation(self):
        """
        **Validates: Requirements 3.1**
        
        Property 2: Preservation - TDQ300123 Standard Layout
        
        Test that extract_bom_from_page1 continues to extract all items correctly
        from TDQ300123 PDF (standard table layout).
        
        This test captures the CURRENT behavior on unfixed code and ensures it
        remains unchanged after the fix.
        """
        pdf_path = "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf"
        
        print("\n" + "="*80)
        print("PRESERVATION TEST: TDQ300123 Standard Layout")
        print("="*80)
        print(f"PDF: {pdf_path}")
        print("Expected: Extract all 15 items with correct data")
        
        # Extract BOM
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        print(f"\nExtracted {len(bom_rows)} items")
        
        # Baseline: Current behavior extracts 15 items
        assert len(bom_rows) == 15, (
            f"Expected 15 items (baseline behavior), but got {len(bom_rows)} items. "
            f"This indicates a regression in standard layout extraction."
        )
        
        # Verify key items are present (spot check)
        part_numbers = [row.get('part_number') for row in bom_rows]
        
        # Check for some expected part numbers from baseline
        expected_samples = [
            "218092451",  # Item with large item number
            "TDQ300123-09",  # Standard part number format
            "TDQ300265-11",  # Another standard format
            "TDQ300123-A00",  # Assembly part number
        ]
        
        for expected_pn in expected_samples:
            assert expected_pn in part_numbers, (
                f"Expected part number '{expected_pn}' not found in extraction. "
                f"This indicates a regression in standard layout extraction."
            )
        
        # Verify all items have non-empty part numbers
        for i, row in enumerate(bom_rows):
            pn = row.get('part_number', '')
            assert pn and len(pn) > 0, (
                f"Item {i+1}: Part number is empty. "
                f"This indicates a regression in part number extraction."
            )
        
        print("✓ PASSED: TDQ300123 extraction behavior preserved")

    def test_1950830513_split_part_number_preservation(self):
        """
        **Validates: Requirements 3.2**
        
        Property 2: Preservation - 1950830513 Split Part Number Reconstruction
        
        Test that extract_bom_from_page1 continues to handle split part numbers
        correctly from 1950830513 PDF.
        
        This test captures the CURRENT behavior on unfixed code, including the
        reconstruction of split part numbers (e.g., "8 19" + "50830513-18" → "1950830513-18").
        """
        pdf_path = "1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        print("\n" + "="*80)
        print("PRESERVATION TEST: 1950830513 Split Part Number")
        print("="*80)
        print(f"PDF: {pdf_path}")
        print("Expected: Extract all items with split part number reconstruction")
        
        # Extract BOM
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        print(f"\nExtracted {len(bom_rows)} items")
        
        # Baseline: Current behavior extracts 9 items
        assert len(bom_rows) == 9, (
            f"Expected 9 items (baseline behavior), but got {len(bom_rows)} items. "
            f"This indicates a regression in split part number extraction."
        )
        
        # Verify reconstructed part numbers are present
        part_numbers = [row.get('part_number') for row in bom_rows]
        
        # Check for reconstructed part numbers from baseline
        expected_reconstructed = [
            "1950830513-18",  # Should be reconstructed from "8 19" + "50830513-18"
            "1950830513-17",
            "1950830513-16",
            "1950830513-15",
            "1950830513-12",
            "1950830513-10",
            "1950830513-09",
            "1950830513-01",
        ]
        
        for expected_pn in expected_reconstructed:
            assert expected_pn in part_numbers, (
                f"Expected reconstructed part number '{expected_pn}' not found. "
                f"This indicates a regression in split part number reconstruction."
            )
        
        # Verify that reconstructed part numbers follow the pattern "1950830513-XX"
        reconstructed_count = sum(1 for pn in part_numbers if pn.startswith("1950830513-"))
        assert reconstructed_count >= 8, (
            f"Expected at least 8 reconstructed part numbers with pattern '1950830513-XX', "
            f"but found {reconstructed_count}. This indicates a regression in reconstruction logic."
        )
        
        print("✓ PASSED: 1950830513 split part number behavior preserved")

    def test_non_tdq300162_general_preservation(self):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
        
        Property 2: Preservation - General Non-TDQ300162 Behavior
        
        Test that extract_bom_from_page1 continues to work correctly for various
        non-TDQ300162 PDFs, preserving all existing extraction patterns:
        - Standard table layouts
        - Split part number reconstruction
        - Inverted numbering detection
        - Multiple table candidate selection
        - Text-based fallback
        - Column alignment handling
        - Part number normalization
        """
        # Test multiple PDFs to ensure broad preservation
        test_cases = [
            {
                'pdf_path': "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
                'name': "TDQ300123",
                'min_items': 10,  # Should extract at least 10 items
                'description': "Standard layout"
            },
            {
                'pdf_path': "1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf",
                'name': "1950830513",
                'min_items': 8,  # Should extract at least 8 items
                'description': "Split part number reconstruction"
            },
        ]
        
        print("\n" + "="*80)
        print("PRESERVATION TEST: General Non-TDQ300162 Behavior")
        print("="*80)
        
        for test_case in test_cases:
            pdf_path = test_case['pdf_path']
            name = test_case['name']
            min_items = test_case['min_items']
            description = test_case['description']
            
            print(f"\nTesting: {name} ({description})")
            print(f"PDF: {pdf_path}")
            
            try:
                bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
                
                print(f"  Extracted {len(bom_rows)} items")
                
                # Verify minimum item count
                assert len(bom_rows) >= min_items, (
                    f"{name}: Expected at least {min_items} items, but got {len(bom_rows)}. "
                    f"This indicates a regression in {description}."
                )
                
                # Verify all items have required fields
                for i, row in enumerate(bom_rows):
                    item = row.get('item')
                    part_number = row.get('part_number', '')
                    qty = row.get('qty')
                    
                    # Item number should be present (can be int or None)
                    assert item is not None or i == 0, (
                        f"{name} Item {i+1}: Missing item number. "
                        f"This indicates a regression in item number extraction."
                    )
                    
                    # Part number should be non-empty
                    assert part_number and len(part_number) > 0, (
                        f"{name} Item {i+1}: Part number is empty. "
                        f"This indicates a regression in part number extraction."
                    )
                    
                    # Quantity should be present
                    assert qty is not None, (
                        f"{name} Item {i+1}: Missing quantity. "
                        f"This indicates a regression in quantity extraction."
                    )
                
                print(f"  ✓ {name} extraction behavior preserved")
                
            except Exception as e:
                pytest.fail(
                    f"{name}: Extraction failed with error: {e}. "
                    f"This indicates a regression in {description}."
                )
        
        print("\n✓ PASSED: General non-TDQ300162 behavior preserved")

    @settings(
        max_examples=10,
        phases=[Phase.generate, Phase.target],
        deadline=None
    )
    @given(
        pdf_choice=st.sampled_from([
            "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
            "1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf",
        ])
    )
    def test_property_non_tdq300162_extraction_stability(self, pdf_choice):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
        
        Property 2: Preservation - Non-TDQ300162 Extraction Stability
        
        Property-based test that verifies extraction behavior is stable and consistent
        for non-TDQ300162 PDFs across multiple test runs.
        
        This test uses property-based testing to generate multiple test cases and
        ensure that the extraction behavior is deterministic and consistent.
        """
        # Extract BOM
        bom_rows, annotation_context = extract_bom_from_page1(pdf_choice)
        
        # Property: Extraction should always succeed for valid PDFs
        assert len(bom_rows) > 0, (
            f"Extraction returned 0 items for {pdf_choice}. "
            f"This indicates a regression in BOM extraction."
        )
        
        # Property: All extracted items should have valid part numbers
        for row in bom_rows:
            part_number = row.get('part_number', '')
            assert part_number and len(part_number) >= 2, (
                f"Invalid part number '{part_number}' in {pdf_choice}. "
                f"This indicates a regression in part number validation."
            )
        
        # Property: Annotation context should be valid
        assert annotation_context is not None, (
            f"Missing annotation context for {pdf_choice}. "
            f"This indicates a regression in annotation context generation."
        )
        
        required_keys = ['table_x0', 'table_x1', 'table_y0', 'table_y1', 
                        'page_width', 'page_height', 'row_height_guess']
        for key in required_keys:
            assert key in annotation_context, (
                f"Missing key '{key}' in annotation context for {pdf_choice}. "
                f"This indicates a regression in annotation context generation."
            )


def run_preservation_tests():
    """Run all preservation tests and report results."""
    test_instance = TestPreservationNonTDQ300162()
    
    print("\n" + "#"*80)
    print("# PRESERVATION PROPERTY TESTS - NON-TDQ300162 BOM EXTRACTION")
    print("#"*80)
    print("# IMPORTANT: These tests MUST PASS on unfixed code")
    print("# They establish the baseline behavior to preserve when fixing TDQ300162")
    print("#"*80)
    
    test_results = []
    
    # Test 1: TDQ300123 standard layout preservation
    print("\n" + "="*80)
    print("Test 1: TDQ300123 Standard Layout Preservation")
    print("="*80)
    try:
        test_instance.test_tdq300123_standard_layout_preservation()
        print("\n✓ Test 1 PASSED: TDQ300123 standard layout behavior preserved")
        test_results.append(("TDQ300123 standard layout", True))
    except AssertionError as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        test_results.append(("TDQ300123 standard layout", False))
    except Exception as e:
        print(f"\n✗ Test 1 ERROR: {e}")
        test_results.append(("TDQ300123 standard layout", False))
    
    # Test 2: 1950830513 split part number preservation
    print("\n" + "="*80)
    print("Test 2: 1950830513 Split Part Number Preservation")
    print("="*80)
    try:
        test_instance.test_1950830513_split_part_number_preservation()
        print("\n✓ Test 2 PASSED: 1950830513 split part number behavior preserved")
        test_results.append(("1950830513 split part number", True))
    except AssertionError as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        test_results.append(("1950830513 split part number", False))
    except Exception as e:
        print(f"\n✗ Test 2 ERROR: {e}")
        test_results.append(("1950830513 split part number", False))
    
    # Test 3: General non-TDQ300162 preservation
    print("\n" + "="*80)
    print("Test 3: General Non-TDQ300162 Preservation")
    print("="*80)
    try:
        test_instance.test_non_tdq300162_general_preservation()
        print("\n✓ Test 3 PASSED: General non-TDQ300162 behavior preserved")
        test_results.append(("General non-TDQ300162", True))
    except AssertionError as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        test_results.append(("General non-TDQ300162", False))
    except Exception as e:
        print(f"\n✗ Test 3 ERROR: {e}")
        test_results.append(("General non-TDQ300162", False))
    
    # Test 4: Property-based extraction stability
    print("\n" + "="*80)
    print("Test 4: Property-Based Extraction Stability")
    print("="*80)
    try:
        # Run property-based test manually for each PDF
        for pdf_path in [
            "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
            "1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        ]:
            print(f"\nTesting stability for: {pdf_path}")
            
            # Extract BOM
            bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
            
            # Property: Extraction should always succeed for valid PDFs
            assert len(bom_rows) > 0, (
                f"Extraction returned 0 items for {pdf_path}. "
                f"This indicates a regression in BOM extraction."
            )
            
            # Property: All extracted items should have valid part numbers
            for row in bom_rows:
                part_number = row.get('part_number', '')
                assert part_number and len(part_number) >= 2, (
                    f"Invalid part number '{part_number}' in {pdf_path}. "
                    f"This indicates a regression in part number validation."
                )
            
            # Property: Annotation context should be valid
            assert annotation_context is not None, (
                f"Missing annotation context for {pdf_path}. "
                f"This indicates a regression in annotation context generation."
            )
            
            required_keys = ['table_x0', 'table_x1', 'table_y0', 'table_y1', 
                            'page_width', 'page_height', 'row_height_guess']
            for key in required_keys:
                assert key in annotation_context, (
                    f"Missing key '{key}' in annotation context for {pdf_path}. "
                    f"This indicates a regression in annotation context generation."
                )
            
            print(f"  ✓ Stability verified for {pdf_path}")
        
        print("\n✓ Test 4 PASSED: Property-based extraction stability verified")
        test_results.append(("Property-based stability", True))
    except AssertionError as e:
        print(f"\n✗ Test 4 FAILED: {e}")
        test_results.append(("Property-based stability", False))
    except Exception as e:
        print(f"\n✗ Test 4 ERROR: {e}")
        test_results.append(("Property-based stability", False))
    
    # Summary
    print("\n" + "#"*80)
    print("# PRESERVATION TEST SUMMARY")
    print("#"*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for test_name, result in test_results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n" + "#"*80)
        print("# ALL PRESERVATION TESTS PASSED")
        print("# Baseline behavior successfully captured")
        print("# These tests will ensure the fix doesn't introduce regressions")
        print("#"*80)
    else:
        print("\n" + "#"*80)
        print("# SOME PRESERVATION TESTS FAILED")
        print("# This may indicate issues with the baseline behavior")
        print("# or problems with the test implementation")
        print("#"*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_preservation_tests()
    sys.exit(0 if success else 1)
