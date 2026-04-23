from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    # When running from workspace root: `uvicorn backend.main:app`
    from backend.services.bom_extractor import extract_bom_from_page1
    from backend.services.drawing_extractor import extract_parts_from_pages, extract_part_materials_from_pages
    from backend.services.matcher import match_bom
    from backend.services.material_validator import validate_materials_for_upload
    from backend.services.material_db import (
        get_reference_table,
        save_reference_table,
        reset_to_default,
        parse_excel_to_rows,
    )
except ModuleNotFoundError:
    # When running from inside backend folder: `uvicorn main:app`
    from services.bom_extractor import extract_bom_from_page1
    from services.drawing_extractor import extract_parts_from_pages, extract_part_materials_from_pages
    from services.matcher import match_bom
    from services.material_validator import validate_materials_for_upload
    from services.material_db import (
        get_reference_table,
        save_reference_table,
        reset_to_default,
        parse_excel_to_rows,
    )


app = FastAPI(title="Drawing BOM Validator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "uploads"

OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    # Avoid gigantic uploads accidentally killing the service.
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=413, detail="PDF too large (max 50MB).")

    job_id = uuid.uuid4().hex
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    input_pdf_path = job_dir / "input.pdf"
    annotated_pdf_path = job_dir / "annotated.pdf"

    input_pdf_path.write_bytes(content)

    try:
        bom_rows, annotation_context = extract_bom_from_page1(str(input_pdf_path))
        extracted_part_keys = extract_parts_from_pages(str(input_pdf_path), start_page_index=1)
        bom_results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_part_keys)
        part_details = extract_part_materials_from_pages(str(input_pdf_path), start_page_index=1)
        material_validation = validate_materials_for_upload(part_keys=extracted_part_keys, part_details=part_details)

        # Annotation feature disabled:
        # Return the original PDF unchanged while keeping validation results.
        annotated_pdf_path.write_bytes(content)

        annotated_pdf_url = str(request.base_url).rstrip("/") + f"/outputs/{job_id}/annotated.pdf"

        bom_annotation_positions = []

        return JSONResponse(
            {
                "job_id": job_id,
                "annotated_pdf_url": annotated_pdf_url,
                "results": bom_results,
                "bom_annotation_positions": bom_annotation_positions,
                "material_results": material_validation.get("material_results", []),
            }
        )
    except Exception as e:
        # Clean up job dir best-effort (keeps debugging artifacts out of the way).
        try:
            if job_dir.exists():
                shutil.rmtree(job_dir)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {e}")


# ---------------------------------------------------------------------------
# Material Reference Table endpoints
# ---------------------------------------------------------------------------

@app.get("/material-reference")
def get_material_reference() -> JSONResponse:
    """Return the current active material reference table."""
    try:
        rows = get_reference_table()
        return JSONResponse({"rows": rows})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load reference table: {e}")


@app.post("/material-reference/upload-excel")
async def upload_material_excel(file: UploadFile = File(...)) -> JSONResponse:
    """
    Accept an .xlsx file, parse it using the company material sheet format,
    and return the parsed rows for the frontend to preview/edit before saving.
    """
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx).")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=413, detail="Excel file too large (max 10 MB).")

    try:
        rows = parse_excel_to_rows(content)
        return JSONResponse({"rows": rows})
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Excel file: {e}")


@app.post("/material-reference/save")
async def save_material_reference(request: Request) -> JSONResponse:
    """
    Persist an edited list of rows to the SQLite database.
    Body: { "rows": [ { edm, materials, finish, heat, base_material, use_notes }, ... ] }
    """
    body = await request.json()
    rows = body.get("rows")
    if not isinstance(rows, list) or not rows:
        raise HTTPException(status_code=400, detail="Body must contain a non-empty 'rows' list.")

    try:
        save_reference_table(rows)
        return JSONResponse({"saved": len(rows)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save reference table: {e}")


@app.post("/material-reference/reset")
def reset_material_reference() -> JSONResponse:
    """Reset the active table back to the bundled factory defaults (from JSON)."""
    try:
        reset_to_default()
        rows = get_reference_table()
        return JSONResponse({"reset": True, "rows": rows})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset reference table: {e}")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

