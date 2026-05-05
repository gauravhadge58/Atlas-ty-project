import pdfplumber
import re

pdfs = [
    'TDQ300162  1  FIXTURES FOR HYDRAULIC TOOLING  Released  VIN-WIP.pdf',
    'TDQ300123  1  GV80 IE4 MOTOR LIFTING FIXTURE.pdf',
    '1950830513  C  EXCHANGE MODULE WOODEN BOX.pdf'
]

for pdf_path in pdfs:
    print(f'\n{"="*80}')
    print(f'PDF: {pdf_path}')
    print("="*80)
    try:
        with pdfplumber.open(f'../{pdf_path}') as pdf:
            for page_idx in range(min(4, len(pdf.pages))):
                page = pdf.pages[page_idx]
                text = page.extract_text() or ''
                
                # Look for PART NUMBER patterns
                if 'PART NUMBER' in text.upper():
                    print(f'\nPage {page_idx + 1} (index {page_idx}):')
                    
                    # Extract lines with PART NUMBER
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if 'PART NUMBER' in line.upper():
                            print(f'  Line {i}: {line[:150]}')
                            # Show next 2 lines for context
                            if i+1 < len(lines):
                                print(f'  Line {i+1}: {lines[i+1][:150]}')
                            if i+2 < len(lines):
                                print(f'  Line {i+2}: {lines[i+2][:150]}')
                            print()
    except Exception as e:
        print(f'Error: {e}')
