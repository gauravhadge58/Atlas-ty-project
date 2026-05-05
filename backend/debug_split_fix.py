#!/usr/bin/env python3

import sys
from pathlib import Path
from services.bom_extractor import extract_bom_from_page1
import pdfplumber
from services.common import normalize_text, parse_int

def debug_table_structure():
    """Debug the table structure to understand the split part number issue"""
    pdf_path = "../1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf"
    
    print("="*80)
    print("DEBUGGING TABLE STRUCTURE FOR SPLIT PART NUMBER FIX")
    print("="*80)
    
    # First, let's see what the current extraction produces
    print("\n1. CURRENT EXTRACTION RESULTS:")
    print("-" * 40)
    try:
        bom_rows, annotation_context = extract_bom_from_page1(pdf_path)
        print(f"Total rows extracted: {len(bom_rows)}")
        for i, row in enumerate(bom_rows):
            print(f"  Row {i+1}: Item={row.get('item')}, Part={row.get('part_number')}, Desc={row.get('description')[:50]}...")
    except Exception as e:
        print(f"Error in extraction: {e}")
        return
    
    # Now let's examine the raw table structure
    print("\n2. RAW TABLE STRUCTURE:")
    print("-" * 40)
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.find_tables()
        
        if not tables:
            print("No tables found!")
            return
            
        print(f"Found {len(tables)} tables")
        
        # Look at the first table (assuming it's the BOM)
        table = tables[0]
        try:
            extracted = table.extract()
            if not extracted:
                print("Table extraction returned empty")
                return
                
            print(f"Table has {len(extracted)} rows")
            
            # Find the header
            header_idx = None
            for i, row in enumerate(extracted):
                joined = normalize_text(" ".join(str(c) if c else "" for c in row))
                if ("PART" in joined and "NUMBER" in joined):
                    header_idx = i
                    print(f"Found header at row {i}: {row}")
                    break
            
            if header_idx is None:
                print("No header found, using row 0")
                header_idx = 0
            
            # Show BOM-relevant rows
            print(f"\nBOM-relevant rows:")
            for i, row in enumerate(extracted):
                # Look for rows with item numbers and part numbers
                if len(row) > 18 and row[18] and row[19]:
                    item_part = str(row[18]).strip()
                    part_num = str(row[19]).strip()
                    desc = str(row[22]).strip() if len(row) > 22 and row[22] else ""
                    qty = str(row[26]).strip() if len(row) > 26 and row[26] else ""
                    
                    if item_part and part_num and any(c.isdigit() for c in item_part):
                        print(f"  Row {i}: Col18='{item_part}', Col19='{part_num}', Col22='{desc}', Col26='{qty}'")
                        
                        # Parse the split pattern
                        if ' ' in item_part:
                            parts = item_part.split()
                            if len(parts) == 2:
                                item_num = parse_int(parts[0])
                                partial_digits = parts[1]
                                reconstructed = partial_digits + part_num
                                print(f"    -> Item: {item_num}, Partial: '{partial_digits}', Reconstructed: '{reconstructed}'")
                        
        except Exception as e:
            print(f"Error extracting table: {e}")
                        
        except Exception as e:
            print(f"Error extracting table: {e}")

if __name__ == "__main__":
    debug_table_structure()