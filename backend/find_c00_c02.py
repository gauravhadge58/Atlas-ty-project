import fitz
import re

pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'
doc = fitz.open(pdf_path)

print("Searching for detailed part pages for C00 and C02...\n")

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    # Look for numbered notes format with PART NUMBER
    if re.search(r'1\.\s*PART NUMBER:\s*TDK040023-C0[02]', text):
        print(f'=== Page {page_num + 1} - Detailed page for C00 or C02 ===')
        lines = text.split('\n')
        for line in lines[:30]:
            print(line)
        print('\n')

doc.close()
