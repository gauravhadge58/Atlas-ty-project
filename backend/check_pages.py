#!/usr/bin/env python3
import pdfplumber
import re

pdf = pdfplumber.open('TDK040023_Lift aid of IXL1500 stator OP10.pdf')
print(f'Total pages: {len(pdf.pages)}')

pattern = re.compile(r'(?:\d+\.\s*)?PART\s*NUMBER', re.IGNORECASE)
for i in range(len(pdf.pages)):
    text = pdf.pages[i].extract_text() or ''
    matches = pattern.findall(text)
    if matches:
        print(f'Page {i}: {len(matches)} PART NUMBER occurrences')
        # Extract actual part numbers
        pn_pattern = re.compile(r'(?:\d+\.\s*)?PART\s*NUMBER\s*:\s*([A-Z0-9\-/]+)', re.IGNORECASE)
        pns = pn_pattern.findall(text)
        for pn in pns:
            print(f'  - {pn}')
