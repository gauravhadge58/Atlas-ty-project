"""
Bug Condition Exploration Test for Split Part Number Extraction

This test demonstrates the bug condition where split part numbers are not extracted correctly.
The test MUST FAIL on unfixed code - failure confirms the bug exists.

**Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3**
"""

from services.bom_extractor import extract_bom_from_page1


class TestBugConditionExploration:
    """
    Bug condition exploration tests that demonstrate the split part number extraction bug.
    These tests are EXPECTED TO FAIL on unfixed code.
    """

    def test_split_part_number_extraction_all_items(self):
        """
        **Validates: Requirements 1.2, 2.2**
        
        Test that extract_bom_from_page1 extracts all 8 items from the problematic PDF.
        This test MUST FAIL on unfixed code - only 3 out of 8 items are currently extracted.
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Should extract at least 8 items (may extract more due to table structure)
        assert len(bom_rows) >= 8, f"Expected at least 8 items, but got {len(bom_rows)} items"
        
        # Verify we have items 1-8
        extracted_items = {row.get('item') for row in bom_rows}
        expected_items = {1, 2, 3, 4, 5, 6, 7, 8}
        missing_items = expected_items - extracted_items
        
        assert missing_items == set(), f"Missing items: {sorted(missing_items)}"

    def test_split_part_number_item_2_extraction(self):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Test that item 2 with split part number "1950830513-09" is extracted correctly.
        Split pattern: "2 19" + "50830513-09" should reconstruct to "1950830513-09"
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Find item 2
        item_2 = next((row for row in bom_rows if row.get('item') == 2), None)
        
        assert item_2 is not None, "Item 2 not found in extracted BOM"
        assert item_2.get('part_number') == "1950830513-09", f"Expected part number '1950830513-09', got '{item_2.get('part_number')}'"
        assert "BASE SHEET EPE FOAM" in item_2.get('description', ''), f"Expected description to contain 'BASE SHEET EPE FOAM', got '{item_2.get('description')}'"

    def test_split_part_number_item_4_extraction(self):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Test that item 4 with split part number "1950830513-12" is extracted correctly.
        Split pattern: "4 19" + "50830513-12" should reconstruct to "1950830513-12"
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Find item 4
        item_4 = next((row for row in bom_rows if row.get('item') == 4), None)
        
        assert item_4 is not None, "Item 4 not found in extracted BOM"
        assert item_4.get('part_number') == "1950830513-12", f"Expected part number '1950830513-12', got '{item_4.get('part_number')}'"
        assert "TOP COVER" in item_4.get('description', ''), f"Expected description to contain 'TOP COVER', got '{item_4.get('description')}'"

    def test_split_part_number_item_6_extraction(self):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Test that item 6 with split part number "1950830513-16" is extracted correctly.
        Split pattern: "6 19" + "50830513-16" should reconstruct to "1950830513-16"
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Find item 6
        item_6 = next((row for row in bom_rows if row.get('item') == 6), None)
        
        assert item_6 is not None, "Item 6 not found in extracted BOM"
        assert item_6.get('part_number') == "1950830513-16", f"Expected part number '1950830513-16', got '{item_6.get('part_number')}'"
        assert "REST BLOCK DP450/DP750/MB4200" in item_6.get('description', ''), f"Expected description to contain 'REST BLOCK DP450/DP750/MB4200', got '{item_6.get('description')}'"

    def test_split_part_number_item_7_extraction(self):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Test that item 7 with split part number "1950830513-17" is extracted correctly.
        Split pattern: "7 19" + "50830513-17" should reconstruct to "1950830513-17"
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Find item 7
        item_7 = next((row for row in bom_rows if row.get('item') == 7), None)
        
        assert item_7 is not None, "Item 7 not found in extracted BOM"
        assert item_7.get('part_number') == "1950830513-17", f"Expected part number '1950830513-17', got '{item_7.get('part_number')}'"
        assert "REST BLOCK DP160&250/MB2600" in item_7.get('description', ''), f"Expected description to contain 'REST BLOCK DP160&250/MB2600', got '{item_7.get('description')}'"

    def test_split_part_number_item_8_extraction(self):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Test that item 8 with split part number "1950830513-18" is extracted correctly.
        Split pattern: "8 19" + "50830513-18" should reconstruct to "1950830513-18"
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Find item 8
        item_8 = next((row for row in bom_rows if row.get('item') == 8), None)
        
        assert item_8 is not None, "Item 8 not found in extracted BOM"
        assert item_8.get('part_number') == "1950830513-18", f"Expected part number '1950830513-18', got '{item_8.get('part_number')}'"
        assert "REST BLOCK DP160&250" in item_8.get('description', ''), f"Expected description to contain 'REST BLOCK DP160&250', got '{item_8.get('description')}'"

    def test_property_split_part_number_reconstruction(self):
        """
        **Validates: Requirements 1.1, 1.3, 2.1, 2.3**
        
        Property-based test that demonstrates the bug condition:
        When part numbers are split across columns, the system should detect and reconstruct them.
        
        This is a scoped property test focused on the concrete failing case to ensure reproducibility.
        """
        pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        # Property: All expected items should be extracted
        expected_items = [
            {"item": 2, "part_number": "1950830513-09", "description_contains": "BASE SHEET EPE FOAM"},
            {"item": 4, "part_number": "1950830513-12", "description_contains": "TOP COVER"},
            {"item": 6, "part_number": "1950830513-16", "description_contains": "REST BLOCK DP450/DP750/MB4200"},
            {"item": 7, "part_number": "1950830513-17", "description_contains": "REST BLOCK DP160&250/MB2600"},
            {"item": 8, "part_number": "1950830513-18", "description_contains": "REST BLOCK DP160&250"},
        ]
        
        extracted_items = {row.get('item'): row for row in bom_rows}
        
        for expected in expected_items:
            item_num = expected["item"]
            expected_part_num = expected["part_number"]
            expected_desc = expected["description_contains"]
            
            # Property: Item should exist in extracted BOM
            assert item_num in extracted_items, f"Item {item_num} not found in extracted BOM (bug condition detected)"
            
            extracted_item = extracted_items[item_num]
            
            # Property: Part number should be correctly reconstructed
            actual_part_num = extracted_item.get('part_number')
            assert actual_part_num == expected_part_num, f"Item {item_num}: Expected part number '{expected_part_num}', got '{actual_part_num}' (split reconstruction failed)"
            
            # Property: Description should be preserved
            actual_desc = extracted_item.get('description', '')
            assert expected_desc in actual_desc, f"Item {item_num}: Expected description to contain '{expected_desc}', got '{actual_desc}'"


if __name__ == "__main__":
    # Run the tests to demonstrate the bug condition
    test_instance = TestBugConditionExploration()
    
    print("Running bug condition exploration tests...")
    print("These tests are EXPECTED TO FAIL on unfixed code to confirm the bug exists.\n")
    
    try:
        test_instance.test_split_part_number_extraction_all_items()
        print("✓ All items extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ All items extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_2_extraction()
        print("✓ Item 2 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 2 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_4_extraction()
        print("✓ Item 4 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 4 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_6_extraction()
        print("✓ Item 6 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 6 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_7_extraction()
        print("✓ Item 7 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 7 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_8_extraction()
        print("✓ Item 8 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 8 extraction test FAILED (expected): {e}")


if __name__ == "__main__":
    # Run the tests to demonstrate the bug condition
    test_instance = TestBugConditionExploration()
    
    print("Running bug condition exploration tests...")
    print("These tests are EXPECTED TO FAIL on unfixed code to confirm the bug exists.\n")
    
    try:
        test_instance.test_split_part_number_extraction_all_items()
        print("✓ All items extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ All items extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_2_extraction()
        print("✓ Item 2 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 2 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_4_extraction()
        print("✓ Item 4 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 4 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_6_extraction()
        print("✓ Item 6 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 6 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_7_extraction()
        print("✓ Item 7 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 7 extraction test FAILED (expected): {e}")
    
    try:
        test_instance.test_split_part_number_item_8_extraction()
        print("✓ Item 8 extraction test PASSED (unexpected)")
    except AssertionError as e:
        print(f"✗ Item 8 extraction test FAILED (expected): {e}")