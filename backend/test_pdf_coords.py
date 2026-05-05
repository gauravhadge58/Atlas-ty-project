import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r'G:\ATLAS\Drawing_self_check_edited_UI\TDQ300177  1  TIMING TOOL ARM  In Work  VIN-WIP  a00554675 (1).pdf'

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[2]
    words = page.extract_words()
    
    print('--- Page 2 Words ---')
    for w in words:
        if 'TDQ300177' in w['text'] or 'M12' in w['text'] or 'M8' in w['text']:
            print(f"{w['text']:<20} X:{w['x0']:>6.1f} Y:{w['top']:>6.1f}")
