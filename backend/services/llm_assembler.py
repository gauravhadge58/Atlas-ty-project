"""
llm_assembler.py
----------------
Determines which parts in a BOM physically mate with each other.

Strategy (in order of preference):
  1. llama3.1:8b  – text-only, uses BOM descriptions + extracted features.
                    Fast (~5-15 s), reliable JSON output, no image needed.
  2. llava        – vision model, sends page-1 image as context.
                    Slower (~60-90 s), used only if llama3.1 is not available.

Returns: { "PART-A": ["PART-B", "PART-C"], ... }
"""

from __future__ import annotations

import base64
import io
import json
import re
from typing import Any, Dict, List, Optional

import requests
import pdfplumber

OLLAMA_BASE   = "http://localhost:11434"
TEXT_MODEL    = "llama3.1:8b"   # fast text-only model
VISION_MODEL  = "llava"         # fallback vision model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _available_models() -> List[str]:
    """Return list of model names currently loaded in Ollama."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


def _call_ollama(
    prompt: str,
    model: str,
    images: Optional[List[str]] = None,
    timeout: int = None,
) -> str:
    # Increase context size for vision models
    num_ctx = 8192 if images else 4096
    
    payload = {
        "model":  model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_ctx": num_ctx},
    }
    if images:
        payload["images"] = images

    resp = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    try:
        data = resp.json()
        if isinstance(data, str):
            data = json.loads(data)
        if isinstance(data, dict):
            return data.get("response", "")
        return str(data)
    except Exception:
        return resp.text


def _parse_graph(raw: str, allowed_upper: set) -> Dict[str, List[str]]:
    """Extract, validate and deduplicate the graph JSON from a raw LLM response."""
    json_match = re.search(r"\{[\s\S]+\}", raw)
    if not json_match:
        return {}
    parsed = json.loads(json_match.group())

    graph_data = parsed.get("graph", [])
    graph: Dict[str, List[str]] = {}
    def _add_edge(p1: str, p2: str):
        if p1 not in allowed_upper:
            print(f"[llm_assembler] Dropping hallucinated part: {p1}")
            return
        if p2 not in allowed_upper:
            print(f"[llm_assembler] Dropping hallucinated part: {p2}")
            return
        if p2 not in graph.get(p1, []):
            graph.setdefault(p1, []).append(p2)
        if p1 not in graph.get(p2, []):
            graph.setdefault(p2, []).append(p1)

    if isinstance(graph_data, list):
        for item in graph_data:
            # Handle list of lists: [["A", "B"]]
            if isinstance(item, list) and len(item) == 2:
                p1, p2 = str(item[0]).upper().strip(), str(item[1]).upper().strip()
                _add_edge(p1, p2)
            # Handle list of dicts: [{"part_number": "A", "mates_with": ["B"]}]
            elif isinstance(item, dict):
                p1 = str(item.get("part_number", "")).upper().strip()
                for p2 in item.get("mates_with", []):
                    _add_edge(p1, str(p2).upper().strip())
            # Handle flat list (vision model sometimes returns this): ["A", "B"]
            # Treat consecutive pairs as edges: ["A", "B", "C", "D"] -> A-B, C-D
            elif isinstance(item, str):
                # Collect all strings first
                pass
        
        # Handle flat string list after collecting all items
        if graph_data and all(isinstance(item, str) for item in graph_data):
            print(f"[llm_assembler] Vision model returned flat list: {graph_data}")
            # Pair consecutive items: [A, B, C, D] -> (A,B), (C,D)
            for i in range(0, len(graph_data) - 1, 2):
                p1 = str(graph_data[i]).upper().strip()
                p2 = str(graph_data[i + 1]).upper().strip()
                _add_edge(p1, p2)
    elif isinstance(graph_data, dict):
        for k, vals in graph_data.items():
            k_up = k.upper().strip()
            if k_up not in allowed_upper:
                print(f"[llm_assembler] Dropping hallucinated key: {k_up}")
                continue
            for v in (vals or []):
                v_up = str(v).upper().strip()
                if v_up not in allowed_upper:
                    print(f"[llm_assembler] Dropping hallucinated value: {v_up}")
                    continue
                if v_up not in graph.get(k_up, []):
                    graph.setdefault(k_up, []).append(v_up)

    return graph


def _build_bom_text(bom_rows, profiles, part_numbers_list) -> str:
    """Build a rich, structured BOM description for the LLM prompt."""
    lines = []
    for r in bom_rows:
        pn = r.get("part_number")
        if not pn:
            continue
        desc = r.get("description", "N/A")
        qty  = r.get("qty", 1)

        features_str = ""
        if profiles and pn in profiles:
            p = profiles[pn]
            feats = []
            if getattr(p, "threads", None):
                feats.append("Threads: " + ", ".join(t.label() for t in p.threads))
            if getattr(p, "hole_patterns", None):
                feats.append("Holes: " + ", ".join(
                    f"{h.count}×Ø{h.diameter}" for h in p.hole_patterns))
            if getattr(p, "bore_shaft_fits", None):
                feats.append("Fits: " + ", ".join(
                    f"Ø{b.nominal}{b.fit_code}" for b in p.bore_shaft_fits))
            if feats:
                features_str = f"  [{'; '.join(feats)}]"

        lines.append(f"  - {pn} (qty {qty}): {desc}{features_str}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Text-only prompt (llama3.1)
# ---------------------------------------------------------------------------

_TEXT_PROMPT_TMPL = """\
You are a mechanical assembly expert. Analyse the BOM below and output which parts physically mate.

Rules:
- A SCREW/BOLT mates ONLY with the structural parts that RECEIVE it (plates, bodies, bases, arms with tapped holes or clearance holes).
- A SCREW must NOT mate with another screw/fastener.
- A purchased standard fastener (part number starting with digits, e.g. 218231413) mates with custom parts that are RECEIVERS (plates, arms, bodies), not with tips, pins, or other fasteners.
- A THUMB SCREW or CLAMP SCREW mates with BOTH the part it clamps (the moving component) AND the structural part it threads into (like a plate or base).
- Only include DIRECT physical contacts. Do not list parts that are merely adjacent.

BOM:
{bom_text}

Allowed part numbers (ONLY use these, do not invent others): [{allowed}]

Return ONLY this JSON, no extra text:
{{
  "graph": [
    ["PART_A", "PART_B"]
  ]
}}

JSON:"""



_VISION_PROMPT_TMPL = """\
You are a mechanical assembly expert reviewing an engineering drawing.
The images show the assembly with numbered balloons and part details.

Bill of Materials (balloon to part):
{bom_text}

Identify which parts physically mate with each other. 
IMPORTANT: Only use these exact part numbers: [{allowed}].

Return ONLY valid JSON in this EXACT format (array of pairs):
{{
  "graph": [
    ["PART_A", "PART_B"],
    ["PART_C", "PART_D"]
  ]
}}

Each pair represents two parts that physically touch/mate.
JSON:"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_assembly_graph(
    pdf_path: str,
    bom_rows: List[Dict[str, Any]],
    profiles: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[str]]:
    """
    Ask the LLM which parts in the BOM mate with each other.
    Tries llama3.1:8b first (text-only, fast), then llava (vision, slower).
    """
    if not bom_rows:
        return {}

    part_numbers_list = [
        str(r.get("part_number", "")).upper()
        for r in bom_rows if r.get("part_number")
    ]
    # Restrict to parts we actually extracted features for.
    # BOM items without drawing pages (e.g. TDQ300177-07 with no profile)
    # would otherwise pass the hallucination filter and corrupt the graph.
    if profiles:
        known = set(pn.upper() for pn in profiles.keys())
        part_numbers_list = [pn for pn in part_numbers_list if pn in known]

    allowed_upper = set(part_numbers_list)
    allowed_str   = ", ".join(f'"{pn}"' for pn in part_numbers_list)
    bom_text      = _build_bom_text(bom_rows, profiles, part_numbers_list)

    available = _available_models()
    print(f"[llm_assembler] Available Ollama models: {available}")

    # ── Strategy 1: text-only with llama3.1:8b ──────────────────────────────
    # Exclude vision models explicitly — they are slow and designed for images.
    # Preference order: llama3.1 > phi > mistral (any non-vision model)
    def _is_text_model(name: str) -> bool:
        n = name.lower()
        if "vision" in n or "llava" in n:
            return False
        return ("llama3.1" in n or "phi" in n or "mistral" in n or "llama3" in n)

    text_graph = {}
    text_model = next((m for m in available if _is_text_model(m)), None)
    if text_model:
        prompt = _TEXT_PROMPT_TMPL.format(
            bom_text=bom_text, allowed=allowed_str
        )
        try:
            print(f"[llm_assembler] Using text model: {text_model}")
            raw = _call_ollama(prompt, model=text_model, timeout=None)
            text_graph = _parse_graph(raw, allowed_upper)
            print(f"[llm_assembler] Text-model graph: {text_graph}")
        except Exception as e:
            print(f"[llm_assembler] Text model failed: {e}")

    # ── Strategy 2: vision with llama3.2-vision or llava ─────────────────────
    # Prefer llama3.2-vision over llava (better for technical drawings)
    vision_model = None
    for m in available:
        if "llama3.2-vision" in m.lower():
            vision_model = m
            break
    if not vision_model:
        vision_model = next((m for m in available if "vision" in m or "llava" in m), None)
    
    if not vision_model:
        print("[llm_assembler] No suitable vision model available. Returning text graph.")
        return text_graph

    # Build images for all drawing pages (skip page 0 BOM)
    # Limit to first 5 pages to avoid context size issues
    img_strs: List[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            max_pages = min(6, len(pdf.pages))  # First 5 drawing pages (skip BOM page 0)
            for page_idx in range(1, max_pages):
                page = pdf.pages[page_idx]
                buf = io.BytesIO()
                page.to_image(resolution=72).original.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                img_strs.append(b64)
                print(f"[llm_assembler] Vision: added page {page_idx} ({len(b64)//1024} KB)")
    except Exception as e:
        print(f"[llm_assembler] Image extraction failed: {e}")

    prompt = _VISION_PROMPT_TMPL.format(
        bom_text=bom_text, allowed=allowed_str
    )
    
    vision_graph = {}
    try:
        print(f"[llm_assembler] Using vision model: {vision_model}")
        raw = _call_ollama(
            prompt, model=vision_model,
            images=img_strs or None,
            timeout=None,
        )
        print(f"[llm_assembler] RAW VISION OUTPUT:\n{raw}\n---END RAW---")
        vision_graph = _parse_graph(raw, allowed_upper)
        print(f"[llm_assembler] Vision-model graph: {vision_graph}")
    except Exception as e:
        print(f"[llm_assembler] Vision model {vision_model} failed: {e}")
        
        # Try fallback to llava if llama3.2-vision failed
        if "llama3.2-vision" in vision_model.lower():
            fallback_model = next((m for m in available if "llava" in m.lower()), None)
            if fallback_model:
                try:
                    print(f"[llm_assembler] Trying fallback vision model: {fallback_model}")
                    raw = _call_ollama(
                        prompt, model=fallback_model,
                        images=img_strs or None,
                        timeout=None,
                    )
                    print(f"[llm_assembler] FALLBACK RAW OUTPUT:\n{raw}\n---END RAW---")
                    vision_graph = _parse_graph(raw, allowed_upper)
                    print(f"[llm_assembler] Fallback vision-model graph: {vision_graph}")
                except Exception as e2:
                    print(f"[llm_assembler] Fallback vision model also failed: {e2}")

    # Merge graphs
    merged = text_graph.copy()
    for k, v in vision_graph.items():
        if k not in merged:
            merged[k] = v
        else:
            merged[k] = list(set(merged[k] + v))
            
    print(f"[llm_assembler] Merged graph: {merged}")
    return merged


def is_ollama_available() -> bool:
    """Quick health check — returns True if Ollama is reachable."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False
