"""
Bug Condition Exploration Test for Material Validation Numbered Notes Fix

**Validates: Requirements 2.1, 2.2, 2.3**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.

This test suite uses property-based testing to verify that the regex patterns
in drawing_extractor.py correctly match and extract material, finish, and heat
treatment information from numbered notes format lines.

GOAL: Surface counterexamples that demonstrate the bug exists.

EXPECTED OUTCOME: Test FAILS on unfixed code (this is correct - it proves the bug exists).
"""

import sys
from pathlib import Path
import re

# Add backend to path for imports
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from hypothesis import given, strategies as st, settings, assume
from services.drawing_extractor import _MATERIAL_RE, _FINISH_RE, _HEAT_KEYWORD_RE
from services.common import normalize_text


# ============================================================================
# Property 1: Bug Condition - Numbered Notes Format Extraction
# ============================================================================

@given(
    number=st.integers(min_value=1, max_value=99),
    material_value=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Zs")),
        min_size=2,
        max_size=30
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_bug_condition_numbered_material_extraction_property(number: int, material_value: str):
    """
    Property 1: Bug Condition - Numbered Material Format Extraction
    
    **Validates: Requirements 2.1**
    
    Test that _MATERIAL_RE pattern matches numbered format lines like "3. MATERIAL: SS400".
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any numbered material line (e.g., "3. MATERIAL: SS400"),
    the regex pattern SHALL match and extract the material value correctly.
    """
    # Generate test line with numbered prefix
    test_line = f"{number}. MATERIAL: {material_value.strip()}"
    
    # Try to match with current regex
    match = _MATERIAL_RE.search(test_line)
    
    # Expected behavior: Should match and extract the value
    assert match is not None, (
        f"_MATERIAL_RE failed to match numbered format line: '{test_line}'\n"
        f"This confirms the bug: regex does not handle numbered prefixes"
    )
    
    extracted_value = match.group("val").strip() if match else ""
    expected_value = material_value.strip()
    
    assert extracted_value == expected_value, (
        f"_MATERIAL_RE extracted '{extracted_value}', expected '{expected_value}' "
        f"from line: '{test_line}'"
    )


@given(
    number=st.integers(min_value=1, max_value=99),
    finish_value=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Zs")),
        min_size=2,
        max_size=30
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_bug_condition_numbered_surface_finish_extraction_property(number: int, finish_value: str):
    """
    Property 1: Bug Condition - Numbered Surface Finish Format Extraction
    
    **Validates: Requirements 2.2**
    
    Test that _FINISH_RE pattern matches numbered "SURFACE FINISH:" format lines.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any numbered surface finish line (e.g., "4. SURFACE FINISH: BLACK OXIDE"),
    the regex pattern SHALL match and extract the finish value correctly.
    """
    # Generate test line with numbered prefix and "SURFACE FINISH:"
    test_line = f"{number}. SURFACE FINISH: {finish_value.strip()}"
    
    # Try to match with current regex
    match = _FINISH_RE.search(test_line)
    
    # Expected behavior: Should match and extract the value
    assert match is not None, (
        f"_FINISH_RE failed to match numbered 'SURFACE FINISH:' line: '{test_line}'\n"
        f"This confirms the bug: regex does not handle 'SURFACE FINISH:' variant"
    )
    
    extracted_value = match.group("val").strip() if match else ""
    expected_value = finish_value.strip()
    
    assert extracted_value == expected_value, (
        f"_FINISH_RE extracted '{extracted_value}', expected '{expected_value}' "
        f"from line: '{test_line}'"
    )


@given(
    number=st.integers(min_value=1, max_value=99),
    heat_value=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Nd", "Zs")),
        min_size=10,
        max_size=50
    ).filter(lambda x: x.strip() != "")
)
@settings(max_examples=50)
def test_bug_condition_numbered_heat_treatment_extraction_property(number: int, heat_value: str):
    """
    Property 1: Bug Condition - Numbered Heat Treatment Format Extraction
    
    **Validates: Requirements 2.3**
    
    Test that heat treatment extraction handles numbered format lines.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    
    Property: For any numbered heat treatment line (e.g., "5. HEAT TREATMENT: HARDENED"),
    the system SHALL extract the heat treatment value correctly.
    
    NOTE: Currently there is no _HEAT_TREATMENT_RE pattern, so this test checks
    if the keyword-based extraction works for numbered format (it may not).
    """
    # Generate test line with numbered prefix
    test_line = f"{number}. HEAT TREATMENT: {heat_value.strip()}"
    
    # Check if there's a dedicated heat treatment regex pattern
    # (There isn't one in the current code, which is part of the bug)
    try:
        from services.drawing_extractor import _HEAT_TREATMENT_RE
        match = _HEAT_TREATMENT_RE.search(test_line)
        
        assert match is not None, (
            f"_HEAT_TREATMENT_RE failed to match numbered format line: '{test_line}'\n"
            f"This confirms the bug: regex does not handle numbered prefixes"
        )
        
        extracted_value = match.group("val").strip() if match else ""
        expected_value = heat_value.strip()
        
        assert extracted_value == expected_value, (
            f"_HEAT_TREATMENT_RE extracted '{extracted_value}', expected '{expected_value}' "
            f"from line: '{test_line}'"
        )
    except ImportError:
        # No dedicated heat treatment regex exists - this is part of the bug
        # For now, we'll document this as a known issue
        assert False, (
            f"No _HEAT_TREATMENT_RE pattern exists in drawing_extractor.py\n"
            f"This confirms part of the bug: heat treatment extraction lacks dedicated regex"
        )


def test_bug_condition_concrete_examples():
    """
    Property 1: Bug Condition - Concrete Examples from TDK040023 PDF
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    Test specific examples from the TDK040023 PDF that demonstrate the bug.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists).
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Concrete Examples")
    print("="*80)
    print()
    
    # Test cases from TDK040023 PDF
    test_cases = [
        # (line, regex_pattern, expected_value, field_name)
        ("3. MATERIAL: SS400", _MATERIAL_RE, "SS400", "MATERIAL"),
        ("3. MATERIAL: STS", _MATERIAL_RE, "STS", "MATERIAL"),
        ("4. SURFACE FINISH: BLACK OXIDE", _FINISH_RE, "BLACK OXIDE", "SURFACE FINISH"),
        ("4. SURFACE FINISH: NATURAL", _FINISH_RE, "NATURAL", "SURFACE FINISH"),
        ("5. HEAT TREATMENT: HARDENED AND TEMPERED TO 60-70 kg/mm2", None, "HARDENED AND TEMPERED TO 60-70 kg/mm2", "HEAT TREATMENT"),
    ]
    
    print("BUG CONDITION TESTING:")
    failures = []
    
    for line, pattern, expected_value, field_name in test_cases:
        if pattern is None:
            # Heat treatment - check if dedicated regex exists
            try:
                from services.drawing_extractor import _HEAT_TREATMENT_RE
                match = _HEAT_TREATMENT_RE.search(line)
            except ImportError:
                print(f"  ✗ {field_name}: No dedicated regex pattern exists")
                failures.append(f"{field_name}: No _HEAT_TREATMENT_RE pattern")
                continue
        else:
            match = pattern.search(line)
        
        if match:
            extracted = match.group("val").strip()
            if extracted == expected_value:
                print(f"  ✓ {field_name}: '{line}' → '{extracted}'")
            else:
                print(f"  ✗ {field_name}: '{line}' → '{extracted}' (expected '{expected_value}')")
                failures.append(f"{field_name}: Extracted '{extracted}', expected '{expected_value}'")
        else:
            print(f"  ✗ {field_name}: '{line}' → NO MATCH")
            failures.append(f"{field_name}: Pattern failed to match '{line}'")
    
    print()
    
    if failures:
        print("BUG CONFIRMED - Counterexamples found:")
        for failure in failures:
            print(f"  - {failure}")
        print()
        print("ROOT CAUSE ANALYSIS:")
        print("  1. _MATERIAL_RE does not include optional numbered prefix (?:\\d+\\.\\s*)?")
        print("  2. _FINISH_RE does not handle 'SURFACE FINISH:' variant")
        print("  3. No dedicated _HEAT_TREATMENT_RE pattern exists")
        print("="*80)
        
        # Fail the test to confirm bug exists
        assert False, (
            f"Bug confirmed: {len(failures)} test case(s) failed. "
            f"Regex patterns do not handle numbered notes format."
        )
    else:
        print("✓ All test cases passed (bug may already be fixed)")
        print("="*80)


def test_bug_condition_case_variations():
    """
    Property 1: Bug Condition - Case Variations
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    Test that case variations work correctly (they should, due to re.IGNORECASE).
    
    EXPECTED OUTCOME: This test FAILS on unfixed code due to numbered prefix,
    not due to case sensitivity.
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Case Variations")
    print("="*80)
    print()
    
    test_cases = [
        ("3. MATERIAL: SS400", _MATERIAL_RE, "SS400"),
        ("3. material: ss400", _MATERIAL_RE, "ss400"),
        ("3. Material: Ss400", _MATERIAL_RE, "Ss400"),
        ("4. SURFACE FINISH: BLACK OXIDE", _FINISH_RE, "BLACK OXIDE"),
        ("4. surface finish: black oxide", _FINISH_RE, "black oxide"),
        ("4. Surface Finish: Black Oxide", _FINISH_RE, "Black Oxide"),
    ]
    
    print("CASE VARIATION TESTING:")
    failures = []
    
    for line, pattern, expected_value in test_cases:
        match = pattern.search(line)
        
        if match:
            extracted = match.group("val").strip()
            if extracted == expected_value:
                print(f"  ✓ '{line}' → '{extracted}'")
            else:
                print(f"  ✗ '{line}' → '{extracted}' (expected '{expected_value}')")
                failures.append(f"Extracted '{extracted}', expected '{expected_value}' from '{line}'")
        else:
            print(f"  ✗ '{line}' → NO MATCH")
            failures.append(f"Pattern failed to match '{line}'")
    
    print()
    
    if failures:
        print(f"BUG CONFIRMED - {len(failures)} case variation(s) failed")
        print("="*80)
        assert False, f"Bug confirmed: Case variations failed due to numbered prefix"
    else:
        print("✓ All case variations passed")
        print("="*80)


def test_bug_condition_whitespace_variations():
    """
    Property 1: Bug Condition - Whitespace Variations
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    Test that whitespace variations are handled correctly.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code due to numbered prefix.
    """
    print("\n" + "="*80)
    print("TEST: Bug Condition - Whitespace Variations")
    print("="*80)
    print()
    
    test_cases = [
        ("3. MATERIAL: SS400", _MATERIAL_RE, "SS400"),
        ("3.  MATERIAL:  SS400", _MATERIAL_RE, "SS400"),  # Extra spaces
        ("3.MATERIAL:SS400", _MATERIAL_RE, "SS400"),      # No spaces
        ("4. SURFACE FINISH: BLACK OXIDE", _FINISH_RE, "BLACK OXIDE"),
        ("4.  SURFACE  FINISH:  BLACK OXIDE", _FINISH_RE, "BLACK OXIDE"),  # Extra spaces
    ]
    
    print("WHITESPACE VARIATION TESTING:")
    failures = []
    
    for line, pattern, expected_value in test_cases:
        match = pattern.search(line)
        
        if match:
            extracted = match.group("val").strip()
            if extracted == expected_value:
                print(f"  ✓ '{line}' → '{extracted}'")
            else:
                print(f"  ✗ '{line}' → '{extracted}' (expected '{expected_value}')")
                failures.append(f"Extracted '{extracted}', expected '{expected_value}' from '{line}'")
        else:
            print(f"  ✗ '{line}' → NO MATCH")
            failures.append(f"Pattern failed to match '{line}'")
    
    print()
    
    if failures:
        print(f"BUG CONFIRMED - {len(failures)} whitespace variation(s) failed")
        print("="*80)
        assert False, f"Bug confirmed: Whitespace variations failed due to numbered prefix"
    else:
        print("✓ All whitespace variations passed")
        print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION TEST")
    print("# CRITICAL: This test MUST FAIL on unfixed code")
    print("# Failure confirms the bug exists and helps understand root cause")
    print("#"*80)
    
    # Run concrete examples first (these provide clear output)
    try:
        test_bug_condition_concrete_examples()
        print("\n✓ Test 1.1 PASSED (Concrete Examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.1 FAILED (Concrete Examples)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    # Run case variations
    try:
        test_bug_condition_case_variations()
        print("\n✓ Test 1.2 PASSED (Case Variations)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.2 FAILED (Case Variations)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    # Run whitespace variations
    try:
        test_bug_condition_whitespace_variations()
        print("\n✓ Test 1.3 PASSED (Whitespace Variations)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print(f"\n✗ Test 1.3 FAILED (Whitespace Variations)")
        print(f"  This is EXPECTED - it confirms the bug exists")
        print(f"  Error: {e}")
    
    # Run property-based tests
    print("\n" + "="*80)
    print("Running property-based tests (50 examples each)...")
    print("="*80)
    
    try:
        test_bug_condition_numbered_material_extraction_property()
        print("✓ Property 1.1 PASSED (Numbered Material - 50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print("✗ Property 1.1 FAILED (Numbered Material - 50 examples)")
        print("  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:200]}")
    
    try:
        test_bug_condition_numbered_surface_finish_extraction_property()
        print("✓ Property 1.2 PASSED (Numbered Surface Finish - 50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print("✗ Property 1.2 FAILED (Numbered Surface Finish - 50 examples)")
        print("  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:200]}")
    
    try:
        test_bug_condition_numbered_heat_treatment_extraction_property()
        print("✓ Property 1.3 PASSED (Numbered Heat Treatment - 50 examples)")
        print("  WARNING: Bug may already be fixed!")
    except AssertionError as e:
        print("✗ Property 1.3 FAILED (Numbered Heat Treatment - 50 examples)")
        print("  This is EXPECTED - it confirms the bug exists")
        print(f"  First failure: {str(e)[:200]}")
    
    print("\n" + "#"*80)
    print("# BUG CONDITION EXPLORATION COMPLETE")
    print("# Test failures above confirm the bug exists")
    print("# Counterexamples documented for root cause analysis")
    print("#"*80)
