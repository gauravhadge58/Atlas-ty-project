"""
Observe baseline behavior for non-TDQ300162 PDFs on UNFIXED code.

This script captures the current extraction results to establish a baseline
that preservation tests should validate.
"""

import sys
sys.path.insert(0, 'backend')

from services.bom_extractor import extract_bom_from_page1
import json


def observe_pdf_extraction(pdf_path: str, pdf_name: str):
    """Observe and document current extraction behavior for a PDF."""
    print(f"\n{'='*80}")
    print(f"Observing: {pdf_name}")
    print(f"{'='*80}")
    print(f"PDF Path: {pdf_path}")
    
    try:
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        
        print(f"\nExtracted {len(bom_rows)} items:")
        print(f"{'Item':<6} {'Part Number':<20} {'Description':<40} {'QTY':<5}")
        print("-" * 80)
        
        for row in bom_rows:
            item = row.get('item', '?')
            part_number = row.get('part_number', '')
            description = row.get('description', '')
            qty = row.get('qty', '?')
            
            # Truncate long descriptions
            if len(description) > 37:
                description = description[:37] + "..."
            
            print(f"{item:<6} {part_number:<20} {description:<40} {qty:<5}")
        
        # Save baseline data for test generation
        baseline = {
            'pdf_name': pdf_name,
            'pdf_path': pdf_path,
            'item_count': len(bom_rows),
            'items': [
                {
                    'item': row.get('item'),
                    'part_number': row.get('part_number'),
                    'description': row.get('description'),
                    'qty': row.get('qty')
                }
                for row in bom_rows
            ]
        }
        
        return baseline
        
    except Exception as e:
        print(f"\n✗ FAILED to extract BOM: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# BASELINE BEHAVIOR OBSERVATION")
    print("# Capturing current extraction results for non-TDQ300162 PDFs")
    print("# This establishes the baseline that preservation tests will validate")
    print("#"*80)
    
    baselines = []
    
    # Test 1: TDQ300123 - Standard table layout
    baseline1 = observe_pdf_extraction(
        "TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf",
        "TDQ300123 (Standard Layout)"
    )
    if baseline1:
        baselines.append(baseline1)
    
    # Test 2: 1950830513 - Split part number reconstruction
    baseline2 = observe_pdf_extraction(
        "1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf",
        "1950830513 (Split Part Number)"
    )
    if baseline2:
        baselines.append(baseline2)
    
    # Save baselines to JSON for reference
    with open('backend/baseline_behavior.json', 'w') as f:
        json.dump(baselines, f, indent=2)
    
    print("\n" + "#"*80)
    print("# BASELINE OBSERVATION COMPLETE")
    print(f"# Captured {len(baselines)} baseline behaviors")
    print("# Saved to: backend/baseline_behavior.json")
    print("#"*80)
