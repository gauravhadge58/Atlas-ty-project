import pdfplumber
import sys
import re
import math

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = r'G:\ATLAS\Drawing_self_check_edited_UI\TDQ300177  1  TIMING TOOL ARM  In Work  VIN-WIP  a00554675 (1).pdf'

_PART_BLOCK_RE = re.compile(
    r"(?:PART\s*NUMBER:\s*)?(?P<pn>[A-Za-z0-9]+(?:-\d+)?)"
)

def normalize_part_number(s: str) -> str:
    if not s:
        return ""
    # Usually part numbers are something like TDQ300177-01
    return s.upper().replace(" ", "")

def _extract_spatial_features(page):
    words = page.extract_words(x_tolerance=10, y_tolerance=5)
    
    # 1. Find Centroids (Part Numbers)
    centroids = {}
    for w in words:
        text = w['text']
        if "TDQ" in text:
            m = _PART_BLOCK_RE.search(text)
            if m:
                pn = normalize_part_number(m.group("pn"))
                if pn:
                    # use the center of the bounding box as centroid
                    cx = (w['x0'] + w['x1']) / 2
                    cy = (w['top'] + w['bottom']) / 2
                    centroids[pn] = (cx, cy)
    
    if not centroids:
        return []
        
    print(f"Centroids: {centroids}")

    # 2. Group all words into lines based on vertical overlap (or just use words if tolerance handles it)
    # Actually, page.extract_words(x_tolerance=10) groups text reasonably well if they are on the same line.
    
    # 3. Assign text to closest centroid
    blocks = {pn: [] for pn in centroids}
    
    for w in words:
        cx = (w['x0'] + w['x1']) / 2
        cy = (w['top'] + w['bottom']) / 2
        
        # Find closest centroid
        closest_pn = None
        min_dist = float('inf')
        for pn, (px, py) in centroids.items():
            dist = math.hypot(cx - px, cy - py)
            if dist < min_dist:
                min_dist = dist
                closest_pn = pn
                
        if closest_pn:
            blocks[closest_pn].append(w['text'])
            
    # Combine words into blocks
    result = []
    for pn, word_list in blocks.items():
        result.append((pn, " ".join(word_list)))
        
    return result

with pdfplumber.open(pdf_path) as pdf:
    print("--- Page 1 (Index 1) ---")
    blocks1 = _extract_spatial_features(pdf.pages[1])
    for pn, txt in blocks1:
        print(f"[{pn}] M12: {'M12' in txt}, M8: {'M8' in txt}")
        
    print("\n--- Page 2 (Index 2) ---")
    blocks2 = _extract_spatial_features(pdf.pages[2])
    for pn, txt in blocks2:
        print(f"[{pn}] M12: {'M12' in txt}, M8: {'M8' in txt}")
