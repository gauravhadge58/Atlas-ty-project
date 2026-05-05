#!/usr/bin/env python3
import pdfplumber
import re

pdf = pdfplumber.open('TDK040023_Lift aid of IXL1500 stator OP10.pdf')

# Parts that show missing values
missing_parts = ['A00', 'B00', 'B02', 'C00', 'C02']

for part_suffix in missing_parts:
    part_num = f'TDK040023-{part_suffix}'
    print(f"\n{'='*80}")
    print(f"Searching for {part_num}")
    print('='*80)
    
    for page_idx in range(len(pdf.pages)):
        text = pdf.pages[page_idx].extract_text() or ''
        
        if part_num in text:
            print(f"\nFound on page {page_idx}")
            
            # Extract the section around this part number
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if part_num in line:
                    print(f"\nContext (lines {max(0, i-2)} to {min(len(lines), i+10)}):")
                    for j in range(max(0, i-2), min(len(lines), i+10)):
                        marker = ">>>" if j == i else "   "
                        print(f"{marker} {j}: {lines[j]}")
                    break
            break
