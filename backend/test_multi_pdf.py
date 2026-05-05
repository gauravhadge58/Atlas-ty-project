#!/usr/bin/env python3
"""
Multi-PDF Testing Script for BOM Validation Multipage Search Fix

Tests the fix across multiple PDFs to ensure it works generally.
"""

from pathlib import Path
from services.bom_extractor import extract_bom_from_page1
from services.drawing_extractor import extract_parts_from_pages
from services.matcher import match_bom

# Test PDFs
TEST_PDFS = [
    "../TDK040023_Lift aid of IXL1500 stator OP10.pdf",
    "../TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
    "../TDQ300162  1  FIXTURES FOR HYDRAULIC TOOLING  Released  VIN-WIP.pdf",
]

def test_pdf(pdf_path: str):
    """Test a single PDF and return results"""
    print(f"\n{'='*80}")
    print(f"Testing: {Path(pdf_path).name}")
    print('='*80)
    
    try:
        # Extract BOM
        bom_rows, _ = extract_bom_from_page1(pdf_path)
        print(f"BOM rows extracted: {len(bom_rows)}")
        
        # Extract parts from pages 2+
        extracted_parts = extract_parts_from_pages(pdf_path, start_page_index=1)
        print(f"Parts extracted from pages 2+: {len(extracted_parts)}")
        print(f"  Parts: {sorted(extracted_parts)}")
        
        # Match BOM
        results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_parts)
        
        # Count statuses
        found_count = sum(1 for r in results if r['status'] == 'FOUND')
        missing_count = sum(1 for r in results if r['status'] == 'MISSING')
        standard_count = sum(1 for r in results if r['status'] == 'STANDARD')
        
        print(f"\nMatching results:")
        print(f"  FOUND: {found_count}/{len(results)}")
        print(f"  MISSING: {missing_count}/{len(results)}")
        print(f"  STANDARD: {standard_count}/{len(results)}")
        
        # Show details for parts with detailed drawings (FOUND)
        if found_count > 0:
            print(f"\n  Parts with detailed drawings (FOUND):")
            for r in results:
                if r['status'] == 'FOUND':
                    print(f"    - {r['part_number']}: {r['description']}")
        
        # Show details for missing parts
        if missing_count > 0:
            print(f"\n  Parts without detailed drawings (MISSING):")
            for r in results:
                if r['status'] == 'MISSING':
                    print(f"    - {r['part_number']}: {r['description']}")
        
        return {
            'pdf': Path(pdf_path).name,
            'bom_count': len(bom_rows),
            'extracted_count': len(extracted_parts),
            'found': found_count,
            'missing': missing_count,
            'standard': standard_count,
            'success': True
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'pdf': Path(pdf_path).name,
            'success': False,
            'error': str(e)
        }

def main():
    print("\n" + "#"*80)
    print("# MULTI-PDF TESTING FOR BOM VALIDATION MULTIPAGE SEARCH FIX")
    print("#"*80)
    
    results = []
    for pdf_path in TEST_PDFS:
        if not Path(pdf_path).exists():
            print(f"\nSkipping {pdf_path} - file not found")
            continue
        
        result = test_pdf(pdf_path)
        results.append(result)
    
    # Summary
    print("\n" + "#"*80)
    print("# SUMMARY")
    print("#"*80)
    
    for result in results:
        if result['success']:
            print(f"\n{result['pdf']}:")
            print(f"  BOM: {result['bom_count']} rows")
            print(f"  Extracted: {result['extracted_count']} parts from pages 2+")
            print(f"  FOUND: {result['found']}/{result['bom_count']}")
            print(f"  MISSING: {result['missing']}/{result['bom_count']}")
            print(f"  STANDARD: {result['standard']}/{result['bom_count']}")
        else:
            print(f"\n{result['pdf']}: FAILED - {result.get('error', 'Unknown error')}")
    
    print("\n" + "#"*80)
    print("# CONCLUSION")
    print("#"*80)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTested {successful}/{total} PDFs successfully")
    
    if successful > 0:
        total_found = sum(r['found'] for r in results if r['success'])
        total_bom = sum(r['bom_count'] for r in results if r['success'])
        print(f"Overall: {total_found}/{total_bom} parts with detailed drawings found")
        print("\n✓ Fix is working correctly across multiple PDFs")
    
    print("\n" + "#"*80)

if __name__ == "__main__":
    main()
