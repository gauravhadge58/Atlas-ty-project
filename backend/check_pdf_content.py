import fitz

pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'
doc = fitz.open(pdf_path)

# Check all pages for C00 and C02
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    if 'C00' in text or 'LIFT BRACKET' in text:
        print(f'\n=== Page {page_num + 1} - Contains C00/LIFT BRACKET ===')
        lines = text.split('\n')
        # Find lines around C00
        for i, line in enumerate(lines):
            if 'C00' in line or 'LIFT BRACKET' in line:
                start = max(0, i - 3)
                end = min(len(lines), i + 15)
                print('\n'.join(lines[start:end]))
                print('---')
                break
    
    if 'C02' in text or 'SLEEVE' in text:
        print(f'\n=== Page {page_num + 1} - Contains C02/SLEEVE ===')
        lines = text.split('\n')
        # Find lines around C02
        for i, line in enumerate(lines):
            if 'C02' in line or ('SLEEVE' in line and 'TDK' in text):
                start = max(0, i - 3)
                end = min(len(lines), i + 15)
                print('\n'.join(lines[start:end]))
                print('---')
                break

doc.close()
