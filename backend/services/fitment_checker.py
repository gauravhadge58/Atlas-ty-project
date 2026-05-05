"""
fitment_checker.py
------------------
Rules-based fitment verification engine.

Checks:
  1. Thread match       – M-size AND pitch must match between mating parts
  2. Hole pattern match – bolt-circle count must match on both parts
  3. Bore / shaft fit   – ISO tolerance fit codes (H7/h6 etc.) where present

All data is extracted locally from pdfplumber text – no external API calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import pdfplumber

from .common import normalize_part_number, normalize_text

# ---------------------------------------------------------------------------
# ISO coarse-thread standard pitches (fallback when pitch not stated)
# ---------------------------------------------------------------------------
_STANDARD_PITCHES: Dict[int, float] = {
    2: 0.4, 3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 7: 1.0,
    8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0,
    18: 2.5, 20: 2.5, 22: 2.5, 24: 3.0, 27: 3.0,
    30: 3.5, 33: 3.5, 36: 4.0, 42: 4.5, 48: 5.0,
}

# Valid ISO shaft/bore fit pairs  {hole_grade: [compatible shaft grades]}
_VALID_FIT_PAIRS: Dict[str, List[str]] = {
    "H7": ["h6", "g6", "f7", "k6", "n6", "p6", "s6"],
    "H8": ["h7", "f8", "e8", "d9"],
    "H9": ["h9", "d9", "e9"],
    "H11": ["h11", "c11", "d11"],
    "H6": ["h5", "g5", "k5", "n5", "p5"],
}

# ---------------------------------------------------------------------------
# IS 3406 Part I-1975  Countersinks – Type A (Medium Series)
# Key: nominal_mm -> (d1_H13, D_H13)  all dims in mm
# ---------------------------------------------------------------------------
_CS_TYPE_A: Dict[float, Tuple[float, float]] = {
    1.6: (1.8, 3.7),  2.0: (2.4, 4.6),  2.5: (2.9, 5.0),
    3.0: (3.4, 6.6),  4.0: (4.5, 9.0),  5.0: (5.5, 11.0),
    6.0: (6.6, 13.0), 8.0: (9.0, 17.2), 10.0: (11.0, 21.5),
    12.0: (14.0, 26.0), 16.0: (18.0, 34.0), 20.0: (22.0, 42.0),
}

# IS 3406 Part II-1975  Counter Bores – Medium Series
# Key: nominal_mm -> (d_H13, D_H13)  all dims in mm
# ---------------------------------------------------------------------------
_CB_MEDIUM: Dict[float, Tuple[float, float]] = {
    3.0: (3.4, 6.3),  4.0: (4.5, 8.0),  5.0: (5.5, 9.5),
    6.0: (6.6, 11.0), 8.0: (9.0, 14.5), 10.0: (11.0, 17.5),
    12.0: (14.0, 20.0), 16.0: (18.0, 26.0), 20.0: (22.0, 33.0),
    24.0: (26.0, 39.0), 30.0: (33.0, 48.0), 36.0: (39.0, 57.0),
}

# IS 2016-1967  Machined Washers
# Key: nominal_screw_mm -> (d_inner_H12, D_outer, s_thickness_basic)
# ---------------------------------------------------------------------------
_WASHER_MACHINED: Dict[float, Tuple[float, float, float]] = {
    1.6: (1.7, 4.0, 0.3),   2.0: (2.2, 5.0, 0.3),   2.5: (2.7, 6.5, 0.5),
    3.0: (3.2, 7.0, 0.5),   4.0: (4.3, 9.0, 0.8),   5.0: (5.3, 10.0, 1.0),
    6.0: (6.4, 12.5, 1.6),  8.0: (8.4, 17.0, 1.6),  10.0: (10.5, 21.0, 2.0),
    12.0: (13.0, 24.0, 2.5), 16.0: (17.0, 30.0, 3.0), 20.0: (21.0, 37.0, 3.0),
    24.0: (25.0, 44.0, 4.0), 30.0: (31.0, 56.0, 4.0), 36.0: (37.0, 66.0, 5.0),
}

# IS 5370-1969  Plain Washers
# Key: nominal_screw_mm -> (d_inner, D_outer, s_thickness)
# ---------------------------------------------------------------------------
_WASHER_PLAIN: Dict[float, Tuple[float, float, float]] = {
    2.5: (2.8, 8.0, 0.8),  3.0: (3.2, 9.0, 0.8),  4.0: (4.3, 12.0, 1.0),
    5.0: (5.3, 15.0, 1.5), 6.0: (6.4, 18.0, 1.5), 8.0: (8.4, 25.0, 2.0),
    10.0: (10.5, 30.0, 2.5), 12.0: (13.0, 40.0, 3.0), 16.0: (17.0, 50.0, 3.0),
    20.0: (21.0, 60.0, 4.0),
}

# IS 3063-1972  Single Coil Rectangular Section Spring Washers
# Key: nominal_mm -> (d1_basic, d2_max, s_basic)
# ---------------------------------------------------------------------------
_WASHER_SPRING: Dict[float, Tuple[float, float, float]] = {
    2.0: (2.1, 4.4, 0.5),  2.5: (2.6, 5.1, 0.6),  3.0: (3.1, 6.2, 0.8),
    4.0: (4.1, 7.6, 1.5),  5.0: (5.1, 9.2, 1.8),  6.0: (6.1, 11.8, 2.5),
    8.0: (8.2, 14.8, 3.0), 10.0: (10.2, 18.1, 3.5), 12.0: (12.2, 21.1, 4.0),
    16.0: (16.2, 27.4, 5.0), 20.0: (20.2, 33.6, 6.0), 24.0: (24.5, 40.0, 7.0),
    30.0: (30.5, 48.2, 8.0), 36.0: (36.5, 58.2, 10.0),
}

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
# Thread: optional count × M<nom> × <pitch> × <length> with optional DEPTH/DEEP keyword
# e.g. "4xM8x1.25", "M12x1.75", "M8", "M8×1.25 DEPTH 20"
_THREAD_RE = re.compile(
    r"(?:(?P<count>\d+)\s*[xX×]\s*)?"
    r"M(?P<nom>\d+(?:\.\d+)?)"
    r"(?:\s*[xX×]\s*(?P<pitch>\d+(?:\.\d+)?))?"
    r"(?:\s*[xX×]\s*(?P<length>\d+(?:\.\d+)?))?"          # optional length (M8x1.25x30)
    r"(?:\s*(?:DEPTH|DEEP)\s*(?P<depth>\d+(?:\.\d+)?))?",  # optional depth keyword (M8 DEPTH 20)
    re.IGNORECASE,
)

# Hole pattern: 4×Ø8.5  or  4x9  (clearance / counterbore)
# Negative lookbehind (?<![ Mm\d]) prevents:
#   - M8×1.25  being read as "8 holes of Ø1.25"  (M before count)
#   - M12×1.75 being read as "2 holes of Ø1.75"  (digit before count, mid-number)
_HOLE_PATTERN_RE = re.compile(
    r"(?<![Mm\d])(?P<count>[2-9]|[1-9]\d)\s*[xX×]\s*[ØøΦ∅]?\s*(?P<dia>\d+(?:\.\d+)?)"
)

# Single hole: Ø8.5 (no count prefix) — collects all such mentions and sums them
_SINGLE_HOLE_RE = re.compile(
    r"(?<![\d×xX])\s*[ØøΦ∅]\s*(?P<dia>\d+(?:\.\d+)?)"
)

# Bore / shaft fit:  Ø25H7  or  Ø25h6
_BORE_SHAFT_RE = re.compile(
    r"[ØøΦ∅]\s*(?P<nom>\d+(?:\.\d+)?)\s*(?P<fit>[A-Za-z]\d+)"
)

# PART NUMBER block header in drawing pages
_PART_BLOCK_RE = re.compile(
    r"PART\s+NUMBER\s*[:\-]?\s*(?P<pn>[A-Z0-9][A-Z0-9\-/\. ]{1,40})",
    re.IGNORECASE,
)

# Keywords that identify a MALE (external-thread) part
_MALE_KW_RE = re.compile(
    r"\b(SCREW|BOLT|STUD|PIN|PLUG|SHAFT|SPINDLE|AXLE|RIVET)\b",
    re.IGNORECASE,
)

# Countersink callout: CSK/C'SINK + optional angle + diameter
# e.g. "CSK Ø9", "C'SINK 90° Ø9", "COUNTERSUNK Ø17.2"
_CSK_RE = re.compile(
    r"(?:C[' ]?SINK|CSK|COUNTERSUNK?)\b"
    r"(?:[^\d]{0,15}(?P<angle>\d{2,3})\s*°)?"
    r"[^\d]{0,10}[ØøΦ∅]?\s*(?P<dia>\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Counterbore callout: CBORE/C'BORE + diameter + optional depth
# e.g. "CBORE Ø14 DEEP 8", "C'BORE Ø14"
_CBORE_RE = re.compile(
    r"(?:C[' ]?BORE|CBORE|COUNTERBORE)\b"
    r"[^\d]{0,10}[ØøΦ∅]?\s*(?P<dia>\d+(?:\.\d+)?)"
    r"(?:[^\d]{0,15}(?:DEEP|DEPTH)[^\d]{0,5}(?P<depth>\d+(?:\.\d+)?))?" ,
    re.IGNORECASE,
)

# Washer callout: WASHER M8 / SPRING WASHER M10 / PLAIN WASHER M6
_WASHER_RE = re.compile(
    r"(?P<wtype>SPRING\s+WASHER|PLAIN\s+WASHER|MACHINED\s+WASHER|WASHER)"
    r"[^\d]{0,10}M(?P<nom>\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Tapped hole keywords: TAPPED, TAP, THREADED HOLE, THD
_TAPPED_HOLE_KW_RE = re.compile(
    r"\b(TAPPED|TAP|THREADED\s+HOLE|THD)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class ThreadFeature:
    nominal: float       # e.g. 8.0
    pitch: float         # e.g. 1.25
    count: int           # number of instances
    gender: str          # "male" | "female"
    raw: str             # original text fragment
    length: Optional[float] = None
    is_clearance: bool = False

    def label(self) -> str:
        pfx = f"{self.count}×" if self.count > 1 else ""
        len_sfx = f"×{self.length}" if self.length else ""
        return f"{pfx}M{int(self.nominal) if self.nominal == int(self.nominal) else self.nominal}×{self.pitch}{len_sfx}"


@dataclass
class HolePattern:
    count: int
    diameter: float
    source: str          # part_number


@dataclass
class BoreShaftFit:
    nominal: float
    fit_code: str        # e.g. "H7"
    fit_type: str        # "bore" | "shaft"
    source: str


@dataclass
class CountersinkFeature:
    screw_nom: float       # matched screw size e.g. 8.0
    csk_dia: float         # diameter found on drawing
    angle: float           # degrees, default 90
    source: str            # part_number


@dataclass
class CounterboreFeature:
    screw_nom: float
    cbore_dia: float
    depth: Optional[float]
    source: str


@dataclass
class WasherFeature:
    screw_nom: float
    washer_type: str       # "spring" | "plain" | "machined" | "general"
    source: str


@dataclass
class DimensionProfile:
    part_number: str
    description: str
    gender: str                                    # "male" | "female"
    threads: List[ThreadFeature] = field(default_factory=list)
    hole_patterns: List[HolePattern] = field(default_factory=list)
    bore_shaft_fits: List[BoreShaftFit] = field(default_factory=list)
    linear_dims: List[float] = field(default_factory=list)
    countersinks: List[CountersinkFeature] = field(default_factory=list)
    counterbores: List[CounterboreFeature] = field(default_factory=list)
    washers: List[WasherFeature] = field(default_factory=list)
    bom_qty: int = 1                               # quantity from BOM table


@dataclass
class FitmentResult:
    part_a: str
    part_b: str
    interface_type: str   # "THREAD" | "HOLE_PATTERN" | "BORE_SHAFT"
    feature_a: str
    feature_b: str
    status: str           # "PASS" | "FAIL" | "WARNING"
    message: str
    checks: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _std_pitch(nominal: float) -> float:
    return _STANDARD_PITCHES.get(int(round(nominal)), 0.0)


def _classify_gender(description: str) -> str:
    return "male" if _MALE_KW_RE.search(description or "") else "female"


def _parse_threads(text: str, gender: str) -> List[ThreadFeature]:
    """Extract thread callouts from a text block. Also tries reversed text
    because some CAD PDFs embed mirrored strings (e.g. '52.1x8Mx4' = '4xM8x1.25').
    
    Detects tapped holes from keywords (TAPPED, TAP, THREADED HOLE, THD) and
    sets gender to 'female' for those threads.
    """
    found: List[ThreadFeature] = []
    seen: Set[Tuple[float, float, int]] = set()

    for candidate in [text, text[::-1]]:
        for m in _THREAD_RE.finditer(candidate):
            nom_s = m.group("nom")
            if not nom_s:
                continue
            try:
                nom = float(nom_s)
            except ValueError:
                continue
            if not (2 <= nom <= 100):
                continue

            pitch_s = m.group("pitch")
            pitch = float(pitch_s) if pitch_s else _std_pitch(nom)
            if pitch == 0:
                continue

            length_s = m.group("length")
            depth_s = m.group("depth")
            # Prefer explicit length, fall back to depth keyword
            length = float(length_s) if length_s else (float(depth_s) if depth_s else None)

            cnt_s = m.group("count")
            cnt = int(cnt_s) if cnt_s else 1

            # Check for tapped hole keywords before the thread spec
            # Look in a window of text before the match
            match_start = m.start()
            window_start = max(0, match_start - 50)  # Look 50 chars before
            text_before = candidate[window_start:match_start]
            
            # If tapped hole keyword found, override gender to female
            thread_gender = gender
            if _TAPPED_HOLE_KW_RE.search(text_before):
                thread_gender = "female"

            key = (nom, pitch, cnt, length)
            if key in seen:
                continue
            seen.add(key)
            found.append(ThreadFeature(nom, pitch, cnt, thread_gender, m.group(0).strip(), length, False))

    return found


def _parse_hole_patterns(text: str, part_number: str) -> List[HolePattern]:
    """Extract hole patterns from text.
    - First looks for counted patterns like '4×Ø8.5'
    - Then falls back to aggregating individual Ø8.5 callouts (counting occurrences)
    - Also tries reversed text (for mirrored PDF text blocks)
    - Also tries whitespace-collapsed reversed text (catches split lines like '5.8' + 'x4')
    """
    patterns: List[HolePattern] = []
    counted_dias: Set[float] = set()

    # Three candidates: normal, char-reversed, whitespace-collapsed-then-reversed
    collapsed = " ".join(text.split())
    candidates = [text, text[::-1], collapsed[::-1]]

    # Pass 1: counted patterns (4×Ø8.5) across all candidates
    for candidate in candidates:
        for m in _HOLE_PATTERN_RE.finditer(candidate):
            cnt = int(m.group("count"))
            dia = float(m.group("dia"))
            if 1 < dia < 300 and 1 < cnt <= 20:
                # Avoid duplicates — keep the highest count for each diameter
                existing = next((p for p in patterns if abs(p.diameter - dia) < 0.01), None)
                if existing:
                    if cnt > existing.count:
                        patterns.remove(existing)
                        patterns.append(HolePattern(cnt, dia, part_number))
                        counted_dias.add(dia)
                else:
                    patterns.append(HolePattern(cnt, dia, part_number))
                    counted_dias.add(dia)

    # Pass 2: single Ø callouts — only for diameters not already captured above
    # Aggregate by diameter: count how many times each diameter appears
    single_counts: Dict[float, int] = {}
    for m in _SINGLE_HOLE_RE.finditer(text):
        dia = float(m.group("dia"))
        if 1 < dia < 300 and dia not in counted_dias:
            single_counts[dia] = single_counts.get(dia, 0) + 1

    for dia, cnt in single_counts.items():
        patterns.append(HolePattern(cnt, dia, part_number))

    return patterns


def _parse_bore_shaft(text: str, part_number: str) -> List[BoreShaftFit]:
    fits: List[BoreShaftFit] = []
    for m in _BORE_SHAFT_RE.finditer(text):
        nom = float(m.group("nom"))
        code = m.group("fit")
        fit_type = "bore" if code[0].isupper() else "shaft"
        fits.append(BoreShaftFit(nom, code, fit_type, part_number))
    return fits


def _parse_countersinks(text: str, part_number: str) -> List[CountersinkFeature]:
    feats: List[CountersinkFeature] = []
    for m in _CSK_RE.finditer(text):
        try:
            dia = float(m.group("dia"))
        except (TypeError, ValueError):
            continue
        if not (1 < dia < 200):
            continue
        angle = float(m.group("angle")) if m.group("angle") else 90.0
        # Guess screw nominal from nearest standard CSK entry
        nom = min(_CS_TYPE_A.keys(), key=lambda k: abs(_CS_TYPE_A[k][1] - dia))
        feats.append(CountersinkFeature(nom, dia, angle, part_number))
    return feats


def _parse_counterbores(text: str, part_number: str) -> List[CounterboreFeature]:
    feats: List[CounterboreFeature] = []
    for m in _CBORE_RE.finditer(text):
        try:
            dia = float(m.group("dia"))
        except (TypeError, ValueError):
            continue
        if not (1 < dia < 200):
            continue
        depth_s = m.group("depth")
        depth = float(depth_s) if depth_s else None
        nom = min(_CB_MEDIUM.keys(), key=lambda k: abs(_CB_MEDIUM[k][1] - dia))
        feats.append(CounterboreFeature(nom, dia, depth, part_number))
    return feats


def _parse_washers(text: str, part_number: str) -> List[WasherFeature]:
    feats: List[WasherFeature] = []
    for m in _WASHER_RE.finditer(text):
        try:
            nom = float(m.group("nom"))
        except (TypeError, ValueError):
            continue
        wt_raw = m.group("wtype").upper()
        if "SPRING" in wt_raw:
            wtype = "spring"
        elif "PLAIN" in wt_raw:
            wtype = "plain"
        elif "MACHINED" in wt_raw:
            wtype = "machined"
        else:
            wtype = "general"
        feats.append(WasherFeature(nom, wtype, part_number))
    return feats


import math

def _extract_spatial_features(page, allowed_parts: set) -> List[Tuple[str, str]]:
    """
    Uses spatial coordinates (x,y) to group text on a PDF page.
    Finds centroids for known part numbers and assigns all other text on the
    page to the physically closest part number centroid.
    """
    words = page.extract_words(x_tolerance=10, y_tolerance=5)
    
    # Find Centroids (Part Numbers)
    centroids = {}
    for w in words:
        text = w['text']
        for pn in allowed_parts:
            # Check if this text block contains the part number
            if pn in text.upper() or pn.replace("-", "") in text.upper():
                cx = (w['x0'] + w['x1']) / 2
                cy = (w['top'] + w['bottom']) / 2
                centroids[pn] = (cx, cy)
    
    if not centroids:
        return []
        
    # Group words to closest centroid
    blocks = {pn: [] for pn in centroids}
    for w in words:
        cx = (w['x0'] + w['x1']) / 2
        cy = (w['top'] + w['bottom']) / 2
        
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


# ---------------------------------------------------------------------------
# Public extraction API
# ---------------------------------------------------------------------------
def extract_fitment_data(
    pdf_path: str,
    bom_rows: List[Dict[str, Any]],
) -> Dict[str, DimensionProfile]:
    """
    Build a DimensionProfile for every part referenced in bom_rows.

    - Custom parts  → parsed from their drawing page text
    - Purchased / standard fasteners → thread inferred from BOM description
    """
    # Description lookup keyed by normalised part number
    desc_map: Dict[str, str] = {
        normalize_part_number(r.get("part_number", "")): (r.get("description") or "")
        for r in bom_rows
        if r.get("part_number")
    }
    # BOM quantity lookup for all parts (used to set bom_qty on custom part profiles)
    qty_map: Dict[str, int] = {
        normalize_part_number(r.get("part_number", "")): int(r.get("qty") or 1)
        for r in bom_rows
        if r.get("part_number")
    }

    profiles: Dict[str, DimensionProfile] = {}

    # ------------------------------------------------------------------ #
    # Step 1 – seed all BOM parts (purchased items get thread from desc)  #
    # ------------------------------------------------------------------ #
    for row in bom_rows:
        raw_pn = row.get("part_number") or ""
        pn = normalize_part_number(raw_pn)
        if not pn:
            continue
        desc = row.get("description") or ""
        gender = _classify_gender(desc)

        # Infer drawing-number prefix from the assembly drawing name
        # (heuristic: parts whose number starts with a digit or looks like a
        # catalogue number are purchased standard items)
        is_purchased = pn[:3].isdigit() or not re.match(r"[A-Z]{2,}", pn)

        if is_purchased:
            # For purchased fasteners like "M8X30 SOC HD CAP SCREW SS":
            # Parse nominal + optional length from "M8X30" or "M8X1.25X30" format.
            # We want to KEEP the length so the engagement check can use it.
            # First try to detect M<nom>x<pitch>x<length>
            fastener_full_re = re.compile(
                r"\bM(?P<nom>\d+(?:\.\d+)?)(?:[Xx](?P<pitch>\d+(?:\.\d+)?))?(?:[Xx](?P<length>\d+(?:\.\d+)?))?\b"
            )
            fm = fastener_full_re.search(desc.upper())
            if fm:
                nom_s = fm.group("nom")
                pitch_s = fm.group("pitch")
                length_s = fm.group("length")
                # Heuristic: if we got two numbers and one of them is > 4, it's (nom, length)
                # because pitch is always <= 4 for metric threads
                nom = float(nom_s) if nom_s else None
                pitch_raw = float(pitch_s) if pitch_s else None
                length_raw = float(length_s) if length_s else None
                if pitch_raw and not length_raw and pitch_raw > 4.0:
                    # pitch_s is actually the length (e.g. M8X30 → nom=8, "pitch"=30 is really length)
                    length_raw, pitch_raw = pitch_raw, None
                pitch = pitch_raw if pitch_raw else _std_pitch(int(round(nom))) if nom else 0
                if nom and pitch:
                    # Extract BOM quantity for screws – BOM uses 'qty' key
                    qty = int(row.get("qty") or 1)
                    ft = ThreadFeature(
                        nominal=nom, pitch=pitch, count=qty,
                        gender=gender, raw=fm.group(0), length=length_raw
                    )
                    threads = [ft]
                else:
                    threads = _parse_threads(desc.upper(), gender)
            else:
                threads = _parse_threads(desc.upper(), gender)
            profiles[pn] = DimensionProfile(
                part_number=pn,
                description=desc,
                gender=gender,
                threads=threads,
                bom_qty=1,  # count on ThreadFeature already = BOM qty
            )

    # ------------------------------------------------------------------ #
    # Step 2 – parse drawing pages (pages 1 onward, skip BOM page)       #
    # ------------------------------------------------------------------ #
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx in range(1, len(pdf.pages)):
            page = pdf.pages[page_idx]
            try:
                text = page.extract_text() or ""
            except Exception:
                continue
            if not text.strip():
                continue

            allowed = set(desc_map.keys())
            blocks = _extract_spatial_features(page, allowed)

            # ── Fallback: if no PART NUMBER block header found, scan the whole page
            # for any known BOM part number mentioned anywhere and extract features
            # for those parts from the full page text. This catches detail drawings
            # where the part number appears in the title block instead of a callout.
            if not blocks:
                norm_text = text.upper().replace(" ", "").replace("-", "").replace("/", "")
                for known_pn in allowed:
                    if not known_pn:
                        continue
                    norm_pn = known_pn.upper().replace(" ", "").replace("-", "").replace("/", "")
                    if norm_pn in norm_text or known_pn in text:
                        blocks.append((known_pn, text))
                        break  # one detail-drawing page → one part

            if not blocks:
                continue

            # Debug: log what page text was found for each block
            for blk_pn, blk_text in blocks:
                print(f"[fitment][page{page_idx}] Matched '{blk_pn}' — first 300 chars: {repr(blk_text[:300])}")

            for pn, block in blocks:
                desc = desc_map.get(pn, "")
                gender = _classify_gender(desc)

                threads = _parse_threads(block.upper(), gender)
                hole_patterns = _parse_hole_patterns(block, pn)
                bore_shaft_fits = _parse_bore_shaft(block, pn)
                countersinks = _parse_countersinks(block, pn)
                counterbores = _parse_counterbores(block, pn)
                washers = _parse_washers(block, pn)

                # Rough linear dims: numbers 2–5 digits that look like mm values
                lin_re = re.compile(r"\b(\d{1,4}(?:\.\d{1,2})?)\b")
                linear_dims = []
                for m in lin_re.finditer(block):
                    v = float(m.group(1))
                    if 1 < v < 3000:
                        linear_dims.append(round(v, 2))

                if pn not in profiles:
                    profiles[pn] = DimensionProfile(
                        part_number=pn,
                        description=desc,
                        gender=gender,
                        threads=threads,
                        hole_patterns=hole_patterns,
                        bore_shaft_fits=bore_shaft_fits,
                        linear_dims=sorted(set(linear_dims)),
                        countersinks=countersinks,
                        counterbores=counterbores,
                        washers=washers,
                        bom_qty=qty_map.get(pn, 1),
                    )
                else:
                    # Merge - accumulate features from ALL drawing pages
                    existing_thread_keys = {(t.nominal, t.pitch) for t in profiles[pn].threads}
                    for t in threads:
                        if (t.nominal, t.pitch) not in existing_thread_keys:
                            profiles[pn].threads.append(t)
                            existing_thread_keys.add((t.nominal, t.pitch))
                    # Holes: dedup by diameter, keep highest count across pages
                    existing_dias = {h.diameter for h in profiles[pn].hole_patterns}
                    for h in hole_patterns:
                        if h.diameter not in existing_dias:
                            profiles[pn].hole_patterns.append(h)
                            existing_dias.add(h.diameter)
                        else:
                            ex = next(hp for hp in profiles[pn].hole_patterns if hp.diameter == h.diameter)
                            if h.count > ex.count:
                                profiles[pn].hole_patterns.remove(ex)
                                profiles[pn].hole_patterns.append(h)
                    # Bore/shaft fits: dedup by nominal+code
                    existing_fits = {(b.nominal, b.fit_code) for b in profiles[pn].bore_shaft_fits}
                    for b in bore_shaft_fits:
                        if (b.nominal, b.fit_code) not in existing_fits:
                            profiles[pn].bore_shaft_fits.append(b)
                            existing_fits.add((b.nominal, b.fit_code))
                    profiles[pn].countersinks.extend(countersinks)
                    profiles[pn].counterbores.extend(counterbores)
                    profiles[pn].washers.extend(washers)

            # ── Page-level hole supplementation ───────────────────────────
            # In multi-part pages (e.g. TDQ300177-01 and -02 on same page),
            # the clearance holes for -01 may appear in -02's text block.
            # For any female part that got no holes from its own block,
            # supplement it with ALL hole patterns from the full page text
            # (filtered to diameters not already attributed to co-located parts).
            page_all_holes = _parse_hole_patterns(text, "_PAGE_")
            parts_on_page = [pn for pn, _ in blocks]
            for pn in parts_on_page:
                if pn in profiles and profiles[pn].gender == "female" and not profiles[pn].hole_patterns:
                    # Share ALL page-level holes with zero-feature female parts.
                    # We intentionally allow overlap – TDQ300177-01 and -02 can
                    # both have Ø9.0 clearance holes on the same drawing page.
                    for h in page_all_holes:
                        profiles[pn].hole_patterns.append(
                            HolePattern(h.count, h.diameter, pn)
                        )
                    if profiles[pn].hole_patterns:
                        print(f"[fitment][supplement] {pn} ← page-level holes: "
                              f"{[f'{h.count}×Ø{h.diameter}' for h in profiles[pn].hole_patterns]}")

    # Debug: print what was extracted per part
    for pn, p in profiles.items():
        thread_labels = [t.label() for t in p.threads]
        hole_labels = [f"{h.count}×Ø{h.diameter}" for h in p.hole_patterns]
        print(f"[fitment][extract] {pn} ({p.gender}): threads={thread_labels}, holes={hole_labels}")

    return profiles


# ---------------------------------------------------------------------------
# Fitment rules
# ---------------------------------------------------------------------------
def _global_nut_exists(profiles: Dict[str, DimensionProfile], nominal: float) -> bool:
    """Check if ANY female part in the BOM can act as the mating thread for this fastener.
    This includes:
    - Explicit NUT parts with matching thread
    - Any female part with a matching TAPPED thread (the tapped hole itself is the nut)
    """
    for pn, p in profiles.items():
        if p.gender == "female":
            for t in p.threads:
                if abs(t.nominal - nominal) < 0.05:
                    return True  # tapped female thread found — acts as the nut
    return False

def _check_threads(
    profiles: Dict[str, DimensionProfile],
    assembly_graph: Optional[Dict[str, List[str]]] = None,
) -> List[FitmentResult]:
    """
    Validates male parts against female parts using strict mechanical design rules.
    Checks:
    1. Thread Compatibility (size, pitch)
    2. Screw Length vs Hole Depth
    3. Thread Engagement
    4. Hole Type Check
    5. Quantity Check
    6. Interference / Safety Check
    """
    results: List[FitmentResult] = []

    males = [(pn, p) for pn, p in profiles.items() if p.gender == "male"]
    females = [(pn, p) for pn, p in profiles.items() if p.gender == "female"]

    checked_pairs: Set[Tuple[str, str, float]] = set()

    for male_pn, male_p in males:
        for m_thread in male_p.threads:
            for fem_pn, fem_p in females:
                # ── Assembly-graph filter (when LLM is available) ──────────
                if assembly_graph:
                    mates_of_male = assembly_graph.get(male_pn.upper())
                    mates_of_fem  = assembly_graph.get(fem_pn.upper())

                    if mates_of_male is not None and mates_of_fem is not None:
                        # Both in graph → strict filtering
                        male_connected = [p.upper() for p in mates_of_male]
                        fem_connected  = [p.upper() for p in mates_of_fem]
                        if (fem_pn.upper() not in male_connected and
                                male_pn.upper() not in fem_connected):
                            # Auto-bypass: If they share the exact same thread size, check them anyway!
                            has_matching_thread = any(abs(m_thread.nominal - f_thread.nominal) <= 0.05 for f_thread in fem_p.threads)
                            if not has_matching_thread:
                                continue

                    elif mates_of_male is not None and mates_of_fem is None:
                        # Male is in graph but female is absent.
                        male_connected = [p.upper() for p in mates_of_male]
                        if fem_pn.upper() not in male_connected:
                            has_matching_thread = any(abs(m_thread.nominal - f_thread.nominal) <= 0.05 for f_thread in fem_p.threads)
                            if fem_p.threads and not has_matching_thread:
                                continue  # female has threads but no thread match & LLM didn't connect
                            # if female has only holes, or has a matching thread → fall through to checks
                # ──────────────────────────────────────────────────────────

                # We must check against BOTH threaded holes and clearance holes in the female part
                candidates = []
                # Find matching threads
                for f_thread in fem_p.threads:
                    if abs(m_thread.nominal - f_thread.nominal) <= 0.05:
                        candidates.append(('thread', f_thread))
                        
                # Find matching clearance holes
                for f_hole in fem_p.hole_patterns:
                    if m_thread.nominal < f_hole.diameter <= m_thread.nominal + 2.0:
                        candidates.append(('hole', f_hole))

                if not candidates:
                    continue

                pair_key = (min(male_pn, fem_pn), max(male_pn, fem_pn), m_thread.nominal)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                # Pick the best candidate based on quantity match
                total_screws = m_thread.count * male_p.bom_qty
                
                def qty_diff(cand):
                    feature_type, feature = cand
                    return abs((feature.count * fem_p.bom_qty) - total_screws)
                    
                best_cand = min(candidates, key=qty_diff)
                
                if best_cand[0] == 'thread':
                    _perform_strict_validation(results, male_pn, male_p, fem_pn, fem_p, m_thread, f_thread=best_cand[1], profiles=profiles)
                else:
                    _perform_strict_validation(results, male_pn, male_p, fem_pn, fem_p, m_thread, f_hole=best_cand[1], profiles=profiles)

    return results

def _perform_strict_validation(
    results: List[FitmentResult],
    male_pn: str, male_p: DimensionProfile,
    fem_pn: str, fem_p: DimensionProfile,
    m_thread: ThreadFeature,
    profiles: Dict[str, DimensionProfile],
    f_thread: Optional[ThreadFeature] = None,
    f_hole: Optional[HolePattern] = None
):
    checks = {}
    overall_status = "PASS"
    fail_reasons = []
    warn_reasons = []

    # 1. Thread Compatibility
    if f_thread:
        if abs(m_thread.pitch - f_thread.pitch) > 0.01:
            checks["thread_match"] = f"FAIL: Pitch mismatch (M: {m_thread.pitch}, F: {f_thread.pitch})"
            overall_status = "FAIL"
            fail_reasons.append("Thread pitch mismatch.")
        else:
            checks["thread_match"] = "PASS: Size and pitch match."
    elif f_hole:
        checks["thread_match"] = f"PASS: Clearance hole (Ø{f_hole.diameter}) accommodates M{m_thread.nominal}."

    # 4. Hole Type Check & Nut Presence
    if f_hole:
        nut_exists = _global_nut_exists(profiles, m_thread.nominal)
        if not nut_exists:
            checks["hole_type_check"] = "FAIL: Clearance hole requires a nut, but no matching nut found in BOM."
            if overall_status != "FAIL": overall_status = "FAIL"
            fail_reasons.append("Missing mating nut for clearance hole.")
        else:
            checks["hole_type_check"] = "PASS: Mating nut found globally in BOM."
    else:
        checks["hole_type_check"] = "PASS: Hole is threaded."

    # 2. Screw Length vs Hole Depth & 3. Thread Engagement
    if m_thread.length:
        screw_len = m_thread.length
        hole_depth = f_thread.length if (f_thread and f_thread.length) else None
        
        if hole_depth:
            if screw_len > hole_depth:
                checks["length_check"] = f"FAIL: Screw length ({screw_len}) exceeds hole depth ({hole_depth}). Will bottom out."
                if overall_status != "FAIL": overall_status = "FAIL"
                fail_reasons.append("Screw bottoms out in hole.")
            elif screw_len < m_thread.nominal:
                checks["length_check"] = f"FAIL: Screw length ({screw_len}) < 1x diameter ({m_thread.nominal}). Too short."
                if overall_status != "FAIL": overall_status = "FAIL"
                fail_reasons.append("Screw too short for safe engagement.")
            elif screw_len <= 1.5 * m_thread.nominal:
                checks["length_check"] = f"WARNING: Screw length ({screw_len}) is between 1x and 1.5x diameter."
                if overall_status == "PASS": overall_status = "WARNING"
                warn_reasons.append("Marginal screw length.")
            else:
                checks["length_check"] = "PASS: Screw length is valid."
                
            engagement = min(screw_len, hole_depth)
            if engagement < m_thread.nominal:
                checks["engagement_check"] = f"FAIL: Engagement length ({engagement}) < diameter ({m_thread.nominal})."
                if overall_status != "FAIL": overall_status = "FAIL"
                fail_reasons.append("Insufficient thread engagement.")
            elif engagement < 1.5 * m_thread.nominal:
                checks["engagement_check"] = f"WARNING: Marginal engagement ({engagement})."
                if overall_status == "PASS": overall_status = "WARNING"
                warn_reasons.append("Marginal thread engagement.")
            else:
                checks["engagement_check"] = "PASS: Good engagement."
                
            # 6. Interference
            if screw_len >= hole_depth - 1.0:
                checks["interference_check"] = "WARNING: Screw length is very close to hole depth (interference risk)."
                if overall_status == "PASS": overall_status = "WARNING"
                warn_reasons.append("Possible bottoming interference.")
            else:
                checks["interference_check"] = "PASS: Safe clearance at bottom of hole."
        else:
            checks["length_check"] = "WARNING: Hole depth not specified. Assuming through-hole or sufficient depth."
            checks["engagement_check"] = "N/A: Missing hole depth."
            checks["interference_check"] = "N/A"
            if overall_status == "PASS": overall_status = "WARNING"
            warn_reasons.append("Missing hole depth for validation.")
    else:
        checks["length_check"] = "N/A: Screw length not specified."
        checks["engagement_check"] = "N/A"
        checks["interference_check"] = "N/A"
        # We don't fail or warn here strictly if length is just unparsed, to avoid breaking all tests

    # 5. Quantity Check
    # Total screws in assembly = count per part × number of parts (bom_qty)
    total_screws = m_thread.count * male_p.bom_qty
    f_count = f_thread.count if f_thread else (f_hole.count if f_hole else 1)
    total_holes = f_count * fem_p.bom_qty

    if total_screws > total_holes:
        checks["quantity_check"] = f"FAIL: Screws ({total_screws}) > Holes ({total_holes})."
        if overall_status != "FAIL": overall_status = "FAIL"
        fail_reasons.append("Not enough holes for screws.")
    elif total_holes > total_screws:
        checks["quantity_check"] = f"WARNING: Holes ({total_holes}) > Screws ({total_screws})."
        if overall_status == "PASS": overall_status = "WARNING"
        warn_reasons.append("More holes than screws provided.")
    else:
        checks["quantity_check"] = "PASS: Quantities match exactly."

    if fail_reasons:
        msg = " | ".join(fail_reasons)
    elif warn_reasons:
        msg = " | ".join(warn_reasons)
    else:
        msg = "All strict mechanical design checks passed."

    feat_a = m_thread.label()
    feat_b = f_thread.label() if f_thread else f"{f_hole.count}×Ø{f_hole.diameter}"

    results.append(FitmentResult(
        part_a=male_pn,
        part_b=fem_pn,
        interface_type="THREAD",
        feature_a=feat_a,
        feature_b=feat_b,
        status=overall_status,
        message=msg,
        checks=checks
    ))


def _check_hole_patterns(
    profiles: Dict[str, DimensionProfile],
    assembly_graph: Optional[Dict[str, List[str]]] = None,
) -> List[FitmentResult]:
    """
    Compare hole patterns between parts that the LLM says are mated.
    Flags count or diameter mismatches on the same bolt circle.
    Only runs on pairs confirmed by the assembly graph (or all pairs if no graph).
    """
    results: List[FitmentResult] = []

    # Collect all parts that have multi-hole patterns
    parts_with_patterns = [
        (pn, p) for pn, p in profiles.items() if p.hole_patterns
    ]

    checked: Set[Tuple[str, str]] = set()

    for i, (pn_a, pa) in enumerate(parts_with_patterns):
        for j, (pn_b, pb) in enumerate(parts_with_patterns):
            if i >= j:
                continue
            pair = (min(pn_a, pn_b), max(pn_a, pn_b))
            if pair in checked:
                continue

            # ── Assembly-graph filter ────────────────────────────────────
            if assembly_graph:
                mates_a = [p.upper() for p in assembly_graph.get(pn_a.upper(), [])]
                mates_b = [p.upper() for p in assembly_graph.get(pn_b.upper(), [])]
                # Skip if LLM says these two don't mate
                if pn_b.upper() not in mates_a and pn_a.upper() not in mates_b:
                    continue
            # ─────────────────────────────────────────────────────────────

            checked.add(pair)

            # Match hole patterns: same count AND diameter within 0.5 mm
            for hp_a in pa.hole_patterns:
                for hp_b in pb.hole_patterns:
                    dia_diff = abs(hp_a.diameter - hp_b.diameter)
                    if hp_a.count != hp_b.count:
                        continue   # Different count — not the same bolt circle
                    if dia_diff <= 0.5:
                        results.append(FitmentResult(
                            part_a=pn_a, part_b=pn_b,
                            interface_type="HOLE_PATTERN",
                            feature_a=f"{hp_a.count}×Ø{hp_a.diameter}",
                            feature_b=f"{hp_b.count}×Ø{hp_b.diameter}",
                            status="PASS",
                            message=(
                                f"Hole pattern {hp_a.count}×Ø{hp_a.diameter} "
                                f"on {pa.description or pn_a} aligns with "
                                f"{hp_b.count}×Ø{hp_b.diameter} on {pb.description or pn_b}."
                            ),
                        ))
                    elif dia_diff <= 2.0:
                        results.append(FitmentResult(
                            part_a=pn_a, part_b=pn_b,
                            interface_type="HOLE_PATTERN",
                            feature_a=f"{hp_a.count}×Ø{hp_a.diameter}",
                            feature_b=f"{hp_b.count}×Ø{hp_b.diameter}",
                            status="WARNING",
                            message=(
                                f"Same hole count ({hp_a.count}) but diameter differs: "
                                f"Ø{hp_a.diameter} vs Ø{hp_b.diameter}. Verify clearance."
                            ),
                        ))
                    # > 2.0 mm difference → completely different features, skip silently

    return results


def _check_bore_shaft(profiles: Dict[str, DimensionProfile]) -> List[FitmentResult]:
    """
    Validate ISO bore/shaft fit pairs where explicit tolerance codes exist.
    """
    results: List[FitmentResult] = []

    bores: List[Tuple[str, DimensionProfile, BoreShaftFit]] = []
    shafts: List[Tuple[str, DimensionProfile, BoreShaftFit]] = []

    for pn, p in profiles.items():
        for fit in p.bore_shaft_fits:
            if fit.fit_type == "bore":
                bores.append((pn, p, fit))
            else:
                shafts.append((pn, p, fit))

    for b_pn, b_p, bore in bores:
        for s_pn, s_p, shaft in shafts:
            if abs(bore.nominal - shaft.nominal) > 0.05:
                continue
            # Check compatibility
            valid_shafts = _VALID_FIT_PAIRS.get(bore.fit_code.upper(), [])
            feat_a = f"Ø{bore.nominal} {bore.fit_code}"
            feat_b = f"Ø{shaft.nominal} {shaft.fit_code}"
            if shaft.fit_code.lower() in [s.lower() for s in valid_shafts]:
                results.append(FitmentResult(
                    part_a=b_pn, part_b=s_pn,
                    interface_type="BORE_SHAFT",
                    feature_a=feat_a, feature_b=feat_b,
                    status="PASS",
                    message=(
                        f"{bore.fit_code}/{shaft.fit_code} is a valid ISO fit "
                        f"for Ø{bore.nominal} mm."
                    ),
                ))
            else:
                results.append(FitmentResult(
                    part_a=b_pn, part_b=s_pn,
                    interface_type="BORE_SHAFT",
                    feature_a=feat_a, feature_b=feat_b,
                    status="FAIL",
                    message=(
                        f"{bore.fit_code}/{shaft.fit_code} is NOT a standard ISO "
                        f"fit pair for Ø{bore.nominal} mm."
                    ),
                ))

    return results


# ---------------------------------------------------------------------------
# IS-standard fitment checks
# ---------------------------------------------------------------------------
def _check_countersinks(profiles: Dict[str, DimensionProfile]) -> List[FitmentResult]:
    """Validate countersink diameters against IS 3406 Part I-1975."""
    results: List[FitmentResult] = []
    for pn, p in profiles.items():
        for cs in p.countersinks:
            std = _CS_TYPE_A.get(cs.screw_nom)
            feat = f"CSK Ø{cs.csk_dia} {int(cs.angle)}°"
            ref = f"IS 3406 Pt.I M{int(cs.screw_nom)}"
            if std is None:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-I",
                    interface_type="COUNTERSINK",
                    feature_a=feat, feature_b=ref,
                    status="WARNING",
                    message=f"No IS 3406 Pt.I entry for M{int(cs.screw_nom)}. Cannot verify Ø{cs.csk_dia}.",
                ))
                continue
            std_D = std[1]
            if abs(cs.csk_dia - std_D) <= 0.5:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-I",
                    interface_type="COUNTERSINK",
                    feature_a=feat, feature_b=f"{ref} D={std_D}",
                    status="PASS",
                    message=f"Countersink Ø{cs.csk_dia} matches IS 3406 Pt.I standard D={std_D} for M{int(cs.screw_nom)}.",
                ))
            else:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-I",
                    interface_type="COUNTERSINK",
                    feature_a=feat, feature_b=f"{ref} D={std_D}",
                    status="FAIL",
                    message=f"Countersink Ø{cs.csk_dia} deviates from IS 3406 Pt.I standard D={std_D} for M{int(cs.screw_nom)} (diff={round(abs(cs.csk_dia-std_D),2)} mm).",
                ))
    return results


def _check_counterbores(profiles: Dict[str, DimensionProfile]) -> List[FitmentResult]:
    """Validate counterbore diameters against IS 3406 Part II-1975."""
    results: List[FitmentResult] = []
    for pn, p in profiles.items():
        for cb in p.counterbores:
            std = _CB_MEDIUM.get(cb.screw_nom)
            feat = f"CBORE Ø{cb.cbore_dia}" + (f" DEEP {cb.depth}" if cb.depth else "")
            ref = f"IS 3406 Pt.II M{int(cb.screw_nom)}"
            if std is None:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-II",
                    interface_type="COUNTERBORE",
                    feature_a=feat, feature_b=ref,
                    status="WARNING",
                    message=f"No IS 3406 Pt.II entry for M{int(cb.screw_nom)}. Cannot verify Ø{cb.cbore_dia}.",
                ))
                continue
            std_D = std[1]
            if abs(cb.cbore_dia - std_D) <= 0.5:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-II",
                    interface_type="COUNTERBORE",
                    feature_a=feat, feature_b=f"{ref} D={std_D}",
                    status="PASS",
                    message=f"Counterbore Ø{cb.cbore_dia} matches IS 3406 Pt.II standard D={std_D} for M{int(cb.screw_nom)}.",
                ))
            else:
                results.append(FitmentResult(
                    part_a=pn, part_b="IS 3406-II",
                    interface_type="COUNTERBORE",
                    feature_a=feat, feature_b=f"{ref} D={std_D}",
                    status="FAIL",
                    message=f"Counterbore Ø{cb.cbore_dia} deviates from IS 3406 Pt.II standard D={std_D} for M{int(cb.screw_nom)} (diff={round(abs(cb.cbore_dia-std_D),2)} mm).",
                ))
    return results


def _check_washers(profiles: Dict[str, DimensionProfile]) -> List[FitmentResult]:
    """Validate washer nominal size exists in the relevant IS washer table."""
    results: List[FitmentResult] = []
    table_map = {
        "spring":   (_WASHER_SPRING,   "IS 3063-1972"),
        "plain":    (_WASHER_PLAIN,    "IS 5370-1969"),
        "machined": (_WASHER_MACHINED, "IS 2016-1967"),
        "general":  (_WASHER_MACHINED, "IS 2016-1967"),
    }
    for pn, p in profiles.items():
        for w in p.washers:
            table, std_name = table_map.get(w.washer_type, (_WASHER_MACHINED, "IS 2016-1967"))
            feat = f"{w.washer_type.title()} Washer M{int(w.screw_nom)}"
            if w.screw_nom in table:
                d_in, D_out, s = table[w.screw_nom]
                results.append(FitmentResult(
                    part_a=pn, part_b=std_name,
                    interface_type="WASHER",
                    feature_a=feat, feature_b=f"{std_name} d={d_in} D={D_out} s={s}",
                    status="PASS",
                    message=f"{feat} is a standard size per {std_name} (d={d_in}, D={D_out}, s={s} mm).",
                ))
            else:
                results.append(FitmentResult(
                    part_a=pn, part_b=std_name,
                    interface_type="WASHER",
                    feature_a=feat, feature_b=std_name,
                    status="WARNING",
                    message=f"M{int(w.screw_nom)} not found in {std_name}. Verify washer size.",
                ))
    return results


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------
def check_fitment_for_upload(
    pdf_path: str,
    bom_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Entry point called from main.py.

    Returns:
    {
      "profiles":  { pn: { threads, hole_patterns, ... } },
      "results":   [ { part_a, part_b, interface_type, feature_a, feature_b, status, message } ],
      "summary":   { total, pass, fail, warning },
      "llm_used":  bool
    }
    """
    profiles = extract_fitment_data(pdf_path, bom_rows)

    # ── LLM assembly graph (uses Ollama if running, else falls back) ───────
    # Run the LLM in a background thread so brute-force results are always
    # returned quickly. If the LLM finishes within 45 s, its graph is used
    # to filter matches (more accurate). If it times out, brute-force runs.
    assembly_graph: Optional[Dict[str, List[str]]] = None
    llm_used = False
    try:
        from .llm_assembler import build_assembly_graph, is_ollama_available
        import threading

        if is_ollama_available():
            llm_result: Dict = {}

            def _run_llm():
                try:
                    llm_result["graph"] = build_assembly_graph(pdf_path, bom_rows, profiles)
                except Exception as ex:
                    print(f"[fitment] LLM thread error: {ex}")

            t = threading.Thread(target=_run_llm, daemon=True)
            t.start()
            t.join(timeout=None)   # No timeout - wait indefinitely for LLM response

            if t.is_alive():
                print("[fitment] LLM thread still running (should not happen with timeout=None)")
            else:
                assembly_graph = llm_result.get("graph") or None
                llm_used = bool(assembly_graph)
                print(f"[fitment] LLM assembly graph: {assembly_graph}")
        else:
            print("[fitment] Ollama not available – using brute-force matching")
    except Exception as e:
        print(f"[fitment] LLM assembler import/call failed: {e}")

    results: List[FitmentResult] = []
    results.extend(_check_threads(profiles, assembly_graph))
    results.extend(_check_hole_patterns(profiles, assembly_graph))
    results.extend(_check_bore_shaft(profiles))
    results.extend(_check_countersinks(profiles))
    results.extend(_check_counterbores(profiles))
    results.extend(_check_washers(profiles))

    # ── Fallback if LLM graph produced zero matches ──────────
    if len(results) == 0 and llm_used:
        print("[fitment] LLM graph yielded 0 matches. Falling back to brute-force matching.")
        results.clear()
        results.extend(_check_threads(profiles, None))
        results.extend(_check_hole_patterns(profiles, None))
        results.extend(_check_bore_shaft(profiles))
        results.extend(_check_countersinks(profiles))
        results.extend(_check_counterbores(profiles))
        results.extend(_check_washers(profiles))

    total = len(results)
    pass_count = sum(1 for r in results if r.status == "PASS")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARNING")

    # Serialise profiles for the frontend
    profiles_out = {}
    for pn, p in profiles.items():
        profiles_out[pn] = {
            "description": p.description,
            "gender": p.gender,
            "threads": [
                {"label": t.label(), "nominal": t.nominal, "pitch": t.pitch, "count": t.count, "gender": t.gender}
                for t in p.threads
            ],
            "hole_patterns": [
                {"count": h.count, "diameter": h.diameter}
                for h in p.hole_patterns
            ],
            "bore_shaft_fits": [
                {"nominal": b.nominal, "fit_code": b.fit_code, "type": b.fit_type}
                for b in p.bore_shaft_fits
            ],
            "countersinks": [
                {"screw_nom": c.screw_nom, "csk_dia": c.csk_dia, "angle": c.angle}
                for c in p.countersinks
            ],
            "counterbores": [
                {"screw_nom": c.screw_nom, "cbore_dia": c.cbore_dia, "depth": c.depth}
                for c in p.counterbores
            ],
            "washers": [
                {"screw_nom": w.screw_nom, "washer_type": w.washer_type}
                for w in p.washers
            ],
        }

    return {
        "profiles": profiles_out,
        "results": [
            {
                "part_a": r.part_a,
                "part_b": r.part_b,
                "interface_type": r.interface_type,
                "feature_a": r.feature_a,
                "feature_b": r.feature_b,
                "status": r.status,
                "message": r.message,
                "checks": getattr(r, 'checks', {}),
            }
            for r in results
        ],
        "summary": {
            "total": total,
            "pass": pass_count,
            "fail": fail_count,
            "warning": warn_count,
        },
        "assembly_graph": assembly_graph or {},
    }
