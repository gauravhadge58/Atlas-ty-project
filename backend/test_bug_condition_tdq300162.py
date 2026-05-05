"""
Bug Condition Exploration Test for TDQ300162 Incomplete BOM Extraction

This test demonstrates the bug condition where the TDQ300162 PDF fails to extract
all 9 BOM items correctly. The test MUST FAIL on unfixed code - failure confirms
the bug exists.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

**CRITICAL**: This test is EXPECTED TO FAIL on unfixed code.
- Current behavior: Extracts only 2 items with incorrect data
- Expected behavior: Extracts all 9 items with correct data

**Bug Condition**: Header detection fails OR data direction determination fails
for TDQ300162 PDF, resulting in incomplete/malformed BOM extraction.
"""

from services.bom_extractor import extract_bom_from_page1


class TestBugConditionTDQ300162:
    """
    Bug condition exploration tests for TDQ300162 incomplete BOM extraction.
    These tests are EXPECTED TO FAIL on unfixed code.
    
    OPTIMIZED: Reduced to single comprehensive test for faster execution.
    """

    def test_tdq300162_property_complete_extraction(self):
        """
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
        
        Property 1: Bug Condition - TDQ300162 Complete BOM Extraction
        
        Property-based test that encodes the expected behavior:
        For TDQ300162 PDF, extract_bom_from_page1 SHALL extract all 9 items with
        correct item numbers, part numbers, descriptions, and quantities.
        
        This is a scoped property test focused on the concrete failing case.
        
        **CRITICAL**: This test MUST FAIL on unfixed code.
        **NOTE**: This test encodes the expected behavior - it will validate the fix
        when it passes after implementation.
        """
        pdf_path = "../TDQ300162  1  FIXTURES FOR HYDRAULIC TOOLING  Released  VIN-WIP.pdf"
        
        print("\n" + "="*80)
        print("PROPERTY TEST: TDQ300162 Complete BOM Extraction")
        print("="*80)
        print(f"PDF: {pdf_path}")
        print("\nThis test encodes the EXPECTED BEHAVIOR (will fail on unfixed code)")
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Expected complete BOM data
        expected_bom = [
            {"item": 1, "part_number": "TDQ300162-01", "description": "PRESS TOOL DISC", "qty": 1},
            {"item": 2, "part_number": "TDQ300162-02", "description": "PRESS CYLINDER HOLDER PIN", "qty": 1},
            {"item": 3, "part_number": "TDQ300162-03", "description": "HOLLOW SHAFT", "qty": 1},
            {"item": 4, "part_number": "TDQ300162-04", "description": "ADAPTOR DISC", "qty": 1},
            {"item": 5, "part_number": "TDQ300162-05", "description": "LOCK NUT", "qty": 1},
            {"item": 6, "part_number": "TDQ300162-06", "description": "P77 HYDRAULIC HAND PUMP ENERPAC", "qty": 1},
            {"item": 7, "part_number": "TDQ300162-07", "description": "RCH121 SINGLE ACTING HOLLOW CYL ENERPAC", "qty": 1},
            {"item": 8, "part_number": "218191375", "description": "BOLT HX HD M6X60 SS", "qty": 2},
            {"item": 9, "part_number": "218231374", "description": "SCR CAP HD M6X35 SS", "qty": 1},
        ]
        
        print(f"\n--- DIAGNOSTIC OUTPUT ---")
        print(f"Extracted {len(bom_rows)} items (Expected: 9)")
        print(f"\nExtracted BOM rows:")
        for row in bom_rows:
            print(f"  Item {row.get('item')}: {row.get('part_number')} - {row.get('description')} (QTY: {row.get('qty')})")
        
        # Property: Correct number of items extracted
        assert len(bom_rows) == 9, f"Property violation: Expected 9 items, got {len(bom_rows)} (Bug Condition: incomplete extraction)"
        
        # Build lookup for extracted items
        extracted_items = {row.get('item'): row for row in bom_rows}
        
        # Property: All expected items exist with correct data
        for expected in expected_bom:
            item_num = expected["item"]
            expected_pn = expected["part_number"]
            expected_desc = expected["description"]
            expected_qty = expected["qty"]
            
            # Property: Item exists
            assert item_num in extracted_items, f"Property violation: Item {item_num} not found (Bug Condition: missing item)"
            
            actual = extracted_items[item_num]
            
            # Property: Part number is correct
            actual_pn = actual.get('part_number')
            assert actual_pn == expected_pn, f"Property violation: Item {item_num} part number - Expected '{expected_pn}', got '{actual_pn}' (Bug Condition: malformed part number)"
            
            # Property: Description is correct (allow partial match for flexibility)
            actual_desc = actual.get('description', '')
            assert actual_desc, f"Property violation: Item {item_num} description is empty (Bug Condition: empty description)"
            assert expected_desc in actual_desc or actual_desc in expected_desc, f"Property violation: Item {item_num} description - Expected '{expected_desc}', got '{actual_desc}' (Bug Condition: incorrect description)"
            
            # Property: Quantity is correct
            actual_qty = actual.get('qty')
            assert actual_qty == expected_qty, f"Property violation: Item {item_num} quantity - Expected {expected_qty}, got {actual_qty} (Bug Condition: incorrect quantity)"
        
        print(f"\n✓ All properties satisfied (Expected behavior achieved)")


def run_diagnostic_analysis():
    """
    Diagnostic helper to understand the root cause of the bug.
    
    This function extracts detailed information about header detection and
    data direction determination to help diagnose why the extraction fails.
    
    NOTE: Removed for faster test execution. Can be re-enabled if needed.
    """
    pass


if __name__ == "__main__":
    # Run diagnostic analysis first to understand the bug
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION - TDQ300162 INCOMPLETE BOM EXTRACTION")
    print("#"*80)
    print("# CRITICAL: This test MUST FAIL on unfixed code")
    print("# Failure confirms the bug exists and provides counterexamples")
    print("#"*80)
    
    # Run the single comprehensive test
    test_instance = TestBugConditionTDQ300162()
    
    print("\n" + "="*80)
    print("Running bug condition exploration test (optimized)...")
    print("="*80)
    
    # Single comprehensive test
    try:
        test_instance.test_tdq300162_property_complete_extraction()
        print("\n✓ Test PASSED: Property-based complete extraction (UNEXPECTED - bug may be fixed)")
        print("\n⚠ WARNING: Test passed - bug may already be fixed or test may be incorrect")
    except AssertionError as e:
        print(f"\n✗ Test FAILED: Property-based complete extraction (EXPECTED - bug confirmed)")
        print(f"   Counterexample: {e}")
        print("\n✓ Bug condition confirmed - test failed as expected on unfixed code")
        print("  Counterexamples documented above demonstrate the bug exists")
