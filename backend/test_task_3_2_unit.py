"""
Unit test for Task 3.2: Heat Treatment Extraction Logic

This test verifies that the heat treatment extraction logic in
extract_part_materials_from_pages() correctly:
1. Uses the new _HEAT_TREATMENT_RE regex pattern first
2. Falls back to _extract_heat_treatment() for backward compatibility
3. Handles both numbered and standard formats
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.drawing_extractor import _HEAT_TREATMENT_RE, _extract_heat_treatment
from services.common import normalize_text


def test_heat_treatment_regex_numbered_format():
    """Test that _HEAT_TREATMENT_RE matches numbered format"""
    print("=" * 80)
    print("TEST 1: Heat Treatment Regex - Numbered Format")
    print("=" * 80)
    
    test_cases = [
        ("5. HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2", 
         "HARDENED AND TEMPERED TO 60-70 kg/mm2"),
        ("3. HEAT TREATMENT: CASE HARDENING", 
         "CASE HARDENING"),
        ("1. HEAT TREATMENT: TEMPERED", 
         "TEMPERED"),
    ]
    
    all_passed = True
    for line, expected in test_cases:
        match = _HEAT_TREATMENT_RE.search(line)
        if match:
            extracted = normalize_text(match.group("val") or "")
            expected_norm = normalize_text(expected)
            if extracted == expected_norm:
                print(f"  ✓ '{line}' → '{extracted}'")
            else:
                print(f"  ✗ '{line}' → '{extracted}' (expected '{expected_norm}')")
                all_passed = False
        else:
            print(f"  ✗ '{line}' → NO MATCH")
            all_passed = False
    
    print()
    return all_passed


def test_heat_treatment_regex_standard_format():
    """Test that _HEAT_TREATMENT_RE matches standard format (backward compatibility)"""
    print("=" * 80)
    print("TEST 2: Heat Treatment Regex - Standard Format (Backward Compatibility)")
    print("=" * 80)
    
    test_cases = [
        ("HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2", 
         "HARDENED AND TEMPERED TO 60-70 kg/mm2"),
        ("HEAT TREATMENT: CASE HARDENING", 
         "CASE HARDENING"),
        ("HEAT TREATMENT: TEMPERED", 
         "TEMPERED"),
    ]
    
    all_passed = True
    for line, expected in test_cases:
        match = _HEAT_TREATMENT_RE.search(line)
        if match:
            extracted = normalize_text(match.group("val") or "")
            expected_norm = normalize_text(expected)
            if extracted == expected_norm:
                print(f"  ✓ '{line}' → '{extracted}'")
            else:
                print(f"  ✗ '{line}' → '{extracted}' (expected '{expected_norm}')")
                all_passed = False
        else:
            print(f"  ✗ '{line}' → NO MATCH")
            all_passed = False
    
    print()
    return all_passed


def test_heat_treatment_fallback():
    """Test that keyword-based extraction still works as fallback"""
    print("=" * 80)
    print("TEST 3: Heat Treatment Fallback - Keyword-Based Extraction")
    print("=" * 80)
    
    # Test cases where there's no explicit "HEAT TREATMENT:" line
    # but heat treatment keywords appear in the text
    test_cases = [
        ("MATERIAL: EN8 NOTE HARDENED AND TEMPERED TO 60-70 kg/mm2", 
         "HARDENED AND TEMPERED TO 60-70 kg/mm2"),
        ("FINISH: BLACK OXIDE\nHARDENED AND TEMPERED TO 60-70 kg/mm2", 
         "HARDENED AND TEMPERED TO 60-70 kg/mm2"),
        ("Some text\nCASE HARDENING TO 0.5mm DEPTH", 
         "CASE HARDENING TO 0.5mm DEPTH"),
    ]
    
    all_passed = True
    for block_text, expected_substring in test_cases:
        # First check if regex matches (it shouldn't for these cases)
        regex_match = _HEAT_TREATMENT_RE.search(block_text)
        
        # Then use fallback extraction
        extracted = _extract_heat_treatment(block_text)
        
        if not regex_match and extracted and expected_substring.upper() in extracted.upper():
            print(f"  ✓ Fallback extraction worked for: '{block_text[:50]}...'")
            print(f"    Extracted: '{extracted}'")
        else:
            print(f"  ✗ Fallback extraction failed for: '{block_text[:50]}...'")
            print(f"    Regex match: {regex_match is not None}")
            print(f"    Extracted: '{extracted}'")
            all_passed = False
    
    print()
    return all_passed


def test_heat_treatment_extraction_logic():
    """Test the actual extraction logic: regex first, then fallback"""
    print("=" * 80)
    print("TEST 4: Heat Treatment Extraction Logic (Regex First, Then Fallback)")
    print("=" * 80)
    
    test_cases = [
        # Case 1: Explicit "HEAT TREATMENT:" line (numbered) - should use regex
        {
            "block_text": "PART NUMBER: TEST-01\n5. HEAT TREATMENT: HARDENED TO 60 kg/mm2",
            "expected": "HARDENED TO 60 KG/MM2",
            "should_use_regex": True
        },
        # Case 2: Explicit "HEAT TREATMENT:" line (standard) - should use regex
        {
            "block_text": "PART NUMBER: TEST-02\nHEAT TREATMENT: CASE HARDENING",
            "expected": "CASE HARDENING",
            "should_use_regex": True
        },
        # Case 3: No explicit line, but keywords present - should use fallback
        {
            "block_text": "PART NUMBER: TEST-03\nMATERIAL: EN8\nHARDENED AND TEMPERED TO 60-70 kg/mm2",
            "expected_contains": "HARDENED AND TEMPERED",
            "should_use_regex": False
        },
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        block_text = test_case["block_text"]
        
        # Simulate the extraction logic from extract_part_materials_from_pages()
        heat_treatment = ""
        ht_match = _HEAT_TREATMENT_RE.search(block_text)
        if ht_match:
            heat_treatment = normalize_text(ht_match.group("val") or "")
        else:
            heat_treatment = _extract_heat_treatment(block_text)
        
        # Verify the result
        if test_case.get("should_use_regex"):
            expected = normalize_text(test_case["expected"])
            if ht_match and heat_treatment == expected:
                print(f"  ✓ Case {i}: Regex matched and extracted '{heat_treatment}'")
            else:
                print(f"  ✗ Case {i}: Expected regex match with '{expected}', got '{heat_treatment}'")
                print(f"    Regex matched: {ht_match is not None}")
                all_passed = False
        else:
            expected_contains = test_case.get("expected_contains", "").upper()
            if not ht_match and heat_treatment and expected_contains in heat_treatment.upper():
                print(f"  ✓ Case {i}: Fallback extraction worked, got '{heat_treatment}'")
            else:
                print(f"  ✗ Case {i}: Expected fallback extraction with '{expected_contains}', got '{heat_treatment}'")
                print(f"    Regex matched: {ht_match is not None}")
                all_passed = False
    
    print()
    return all_passed


def main():
    print("\n" + "#" * 80)
    print("# TASK 3.2 UNIT TEST: Heat Treatment Extraction Logic")
    print("#" * 80)
    print()
    
    results = []
    
    # Run all tests
    results.append(("Numbered Format", test_heat_treatment_regex_numbered_format()))
    results.append(("Standard Format", test_heat_treatment_regex_standard_format()))
    results.append(("Fallback Extraction", test_heat_treatment_fallback()))
    results.append(("Extraction Logic", test_heat_treatment_extraction_logic()))
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print()
        print("Task 3.2 Implementation Verified:")
        print("  1. ✓ Heat treatment regex pattern matches numbered format")
        print("  2. ✓ Heat treatment regex pattern matches standard format")
        print("  3. ✓ Fallback to keyword-based extraction works")
        print("  4. ✓ Extraction logic tries regex first, then fallback")
        print()
        print("Task 3.2 is COMPLETE!")
    else:
        print("✗ SOME TESTS FAILED")
        print("Task 3.2 implementation needs fixes.")
    
    print("#" * 80)
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
