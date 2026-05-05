from __future__ import annotations

import asyncio
import shutil
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

try:
    # When running from workspace root: `uvicorn backend.main:app`
    from backend.services.bom_extractor import extract_bom_from_page1
    from backend.services.drawing_extractor import extract_parts_from_pages, extract_part_materials_from_pages
    from backend.services.matcher import match_bom
    from backend.services.material_validator import validate_materials_for_upload
    from backend.services.fitment_checker import check_fitment_for_upload
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
    from services.fitment_checker import check_fitment_for_upload
    from services.material_db import (
        get_reference_table,
        save_reference_table,
        reset_to_default,
        parse_excel_to_rows,
    )


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "uploads"

OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)


async def cleanup_old_outputs():
    """Periodically cleans up output folders older than 24 hours."""
    while True:
        try:
            now = time.time()
            max_age = 24 * 60 * 60  # 24 hours in seconds
            
            if OUTPUTS_DIR.exists():
                for job_dir in OUTPUTS_DIR.iterdir():
                    if job_dir.is_dir():
                        # Check folder modification time
                        if now - job_dir.stat().st_mtime > max_age:
                            try:
                                shutil.rmtree(job_dir)
                                print(f"Cleaned up old job dir: {job_dir.name}")
                            except Exception as e:
                                print(f"Failed to clean up {job_dir.name}: {e}")
        except Exception as e:
            print(f"Cleanup task error: {e}")
            
        # Wait for 1 hour before checking again
        await asyncio.sleep(60 * 60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start cleanup task
    task = asyncio.create_task(cleanup_old_outputs())
    yield
    # Shutdown: Cancel cleanup task
    task.cancel()

app = FastAPI(title="Drawing BOM Validator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
        print(f"[UPLOAD] Starting processing for job {job_id}")
        print(f"[UPLOAD] Step 1/5: Extracting BOM from page 1...")
        bom_rows, annotation_context = extract_bom_from_page1(str(input_pdf_path))
        print(f"[UPLOAD] Step 1/5: ✓ BOM extracted - {len(bom_rows)} items found")
        
        print(f"[UPLOAD] Step 2/5: Extracting part details from pages 2+...")
        extracted_part_keys = extract_parts_from_pages(str(input_pdf_path), start_page_index=1)
        print(f"[UPLOAD] Step 2/5: ✓ Part details extracted - {len(extracted_part_keys)} parts found")
        
        print(f"[UPLOAD] Step 3/5: Matching BOM items with extracted parts...")
        bom_results = match_bom(bom_rows=bom_rows, extracted_part_keys=extracted_part_keys)
        print(f"[UPLOAD] Step 3/5: ✓ BOM matching complete")
        
        print(f"[UPLOAD] Step 4/5: Extracting material specifications...")
        part_details = extract_part_materials_from_pages(str(input_pdf_path), start_page_index=1)
        print(f"[UPLOAD] Step 4/5: ✓ Material specs extracted")
        
        print(f"[UPLOAD] Step 5/5: Validating materials against reference table...")
        material_validation = validate_materials_for_upload(part_keys=extracted_part_keys, part_details=part_details)
        print(f"[UPLOAD] Step 5/5: ✓ Material validation complete")

        # Fitment verification - SKIPPED on initial upload for faster response
        # User can trigger it separately via /fitment/{job_id} endpoint
        print(f"[UPLOAD] Fitment check skipped (on-demand only)")
        fitment_data = {"profiles": {}, "results": [], "summary": {"total": 0, "pass": 0, "fail": 0, "warning": 0}, "assembly_graph": {}}

        # Annotation feature disabled:
        # Return the original PDF unchanged while keeping validation results.
        print(f"[UPLOAD] Creating response PDF...")
        annotated_pdf_path.write_bytes(content)

        annotated_pdf_url = str(request.base_url).rstrip("/") + f"/outputs/{job_id}/annotated.pdf"

        bom_annotation_positions = []

        print(f"[UPLOAD] ✓ Processing complete for job {job_id}")
        return JSONResponse(
            {
                "job_id": job_id,
                "annotated_pdf_url": annotated_pdf_url,
                "results": bom_results,
                "bom_annotation_positions": bom_annotation_positions,
                "material_results": material_validation.get("material_results", []),
                "fitment_results": fitment_data.get("results", []),
                "fitment_summary": fitment_data.get("summary", {}),
                "fitment_profiles": fitment_data.get("profiles", {}),
                "assembly_graph": fitment_data.get("assembly_graph", {}),
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


@app.post("/fitment/{job_id}")
async def run_fitment_check(job_id: str) -> JSONResponse:
    """
    Run fitment validation for a previously uploaded PDF.
    This is a separate endpoint to avoid slowing down the initial upload.
    """
    job_dir = OUTPUTS_DIR / job_id
    input_pdf_path = job_dir / "input.pdf"
    
    if not job_dir.exists() or not input_pdf_path.exists():
        raise HTTPException(status_code=404, detail="Job not found or PDF has been cleaned up.")
    
    try:
        print(f"[FITMENT] Starting fitment check for job {job_id}")
        
        # Re-extract BOM for fitment check
        print(f"[FITMENT] Step 1/2: Re-extracting BOM...")
        bom_rows, _ = extract_bom_from_page1(str(input_pdf_path))
        print(f"[FITMENT] Step 1/2: ✓ BOM extracted - {len(bom_rows)} items")
        
        # Run fitment verification
        print(f"[FITMENT] Step 2/2: Running fitment analysis (this may take 1-2 minutes)...")
        fitment_data = check_fitment_for_upload(
            pdf_path=str(input_pdf_path),
            bom_rows=bom_rows,
        )
        print(f"[FITMENT] Step 2/2: ✓ Fitment analysis complete")
        
        print(f"[FITMENT] ✓ Fitment check complete for job {job_id}")
        return JSONResponse({
            "job_id": job_id,
            "fitment_results": fitment_data.get("results", []),
            "fitment_summary": fitment_data.get("summary", {}),
            "fitment_profiles": fitment_data.get("profiles", {}),
            "assembly_graph": fitment_data.get("assembly_graph", {}),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fitment check failed: {e}")


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
# Serve built frontend static files (For Production / Docker)
# ---------------------------------------------------------------------------
frontend_dist = BASE_DIR.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Serve assets folder
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
    # Serve logo and other root public files
    @app.get("/logo.png")
    def serve_logo():
        logo_file = frontend_dist / "logo.png"
        if logo_file.exists():
            return FileResponse(logo_file)
        raise HTTPException(status_code=404, detail="Not found")

    # Serve index.html for all other routes to support React Router SPA
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        # Ignore API calls that fell through
        if catchall.startswith("api/") or catchall.startswith("outputs/"):
            raise HTTPException(status_code=404, detail="Not found")
            
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

