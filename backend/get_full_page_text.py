import fitz

pdf_path = '../TDK040023_Lift aid of IXL1500 stator OP10.pdf'
doc = fitz.open(pdf_path)

# Check pages 7 and 8 (indices 6 and 7)
for page_idx in [6, 7]:
    print(f'\n{"="*80}')
    print(f'PAGE {page_idx + 1} FULL TEXT')
    print("="*80)
    page = doc[page_idx]
    text = page.get_text()
    print(text)
    print("\n")

doc.close()
