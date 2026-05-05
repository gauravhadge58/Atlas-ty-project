#!/usr/bin/env python3
import pdfplumber
import re

pdf = pdfplumber.open('TDK040023_Lift aid of IXL1500 stator OP10.pdf')
text = pdf.pages[7].extract_text()
lines = text.splitlines()

print('Lines containing PART NUMBER or MATERIAL or FINISH:')
for i, line in enumerate(lines):
    if re.search(r'(PART\s*NUMBER|MATERIAL|FINISH)', line, re.IGNORECASE):
        print(f'Line {i}: {line}')
