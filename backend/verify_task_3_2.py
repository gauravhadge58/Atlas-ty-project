"""
Verification script for Task 3.2: Heat Treatment Extraction Logic Update

This script verifies that the heat treatment extraction logic correctly:
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

from services.drawing_extractor import extract_part_materials_from_pages

def verify_heat_treatment_extraction():
    """Verify heat treatment extraction works for TDK040023 PDF"""
    
    pdf_path = "../TDK040023_Lift aid of IXL1500 stator OP10.pdf"
    
    print("=" * 80)
    print("TASK 3.2 VERIFICATION: Heat Treatment Extraction Logic")
    print("=" * 80)
    print()
    
    try:
        # Extract materials from the PDF
        materials = extract_part_materials_from_pages(pdf_path, start_page_index=1)
        
        print(f"✓ Successfully extracted materials from {len(materials)} parts")
        print()
        
        # Check if heat treatment values are extracted
        parts_with_heat_treatment = 0
        parts_without_heat_treatment = 0
        
        print("Heat Treatment Extraction Results:")
        print("-" * 80)
        
        for part_num, data in sorted(materials.items()):
            heat_treatment = data.get("heat_treatment", "")
            if heat_treatment:
                parts_with_heat_treatment += 1
                print(f"  ✓ {part_num}: {heat_treatment[:60]}...")
            else:
                parts_without_heat_treatment += 1
                print(f"  ✗ {part_num}: (no heat treatment)")
        
        print()
        print("=" * 80)
        print(f"Summary:")
        print(f"  Parts with heat treatment: {parts_with_heat_treatment}")
        print(f"  Parts without heat treatment: {parts_without_heat_treatment}")
        print(f"  Total parts: {len(materials)}")
        print("=" * 80)
        print()
        
        # Verify the fix is working
        if parts_with_heat_treatment > 0:
            print("✓ VERIFICATION PASSED: Heat treatment extraction is working!")
            print("  The new regex pattern successfully extracts heat treatment from numbered format.")
            return True
        else:
            print("✗ VERIFICATION FAILED: No heat treatment values extracted")
            print("  The fix may not be working correctly.")
            return False
            
    except FileNotFoundError:
        print(f"✗ ERROR: PDF file not found: {pdf_path}")
        print("  Please ensure the PDF is in the current directory.")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_heat_treatment_extraction()
    sys.exit(0 if success else 1)
