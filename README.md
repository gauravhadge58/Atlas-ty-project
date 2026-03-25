# ATLAS Drawing BOM & Material Validator

Upload a drawing PDF to validate:

- **BOM (page 1)**: classifies BOM rows as `FOUND`, `STANDARD`, or `MISSING`
- **Materials (pages 2..N)**: extracts per-part **Material (EDM code + name)**, **Surface Finish**, and **Heat Treatment**, then validates against a reference table

## Features

### BOM validation
- Extracts BOM table rows from **page 1**
- Detects part definitions on **pages 2..N**
- Returns BOM validation results in `results`

### Material validation
- For each detected part number, extracts:
  - `material_code` and `material_name` from lines like `MATERIAL: EDM000136/ En8`
  - `finish` from `FINISH: CHEMICAL BLACK`
  - `heat_treatment` from lines containing `HARDENED`, `TEMPERED`, or `CASE HARDENING`
- Normalizes extracted values (uppercase, whitespace cleanup)
- Applies synonym mapping (example: `CHEMICAL BLACK -> BLACKODISING`)
- Extracts numeric heat ranges (example: `60-70`)
- Returns material validation results in `material_results`

Reference table:
- `backend/data/material_reference.json`

## Backend (FastAPI)

### Install
From the repo root:

```bash
cd backend
python -m pip install -r requirements.txt
```

### Run
Default port:

```bash
cd backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

API endpoints:
- `GET /health`
- `POST /upload` (multipart form-data, field name: `file`)

### Response (POST /upload)

```json
{
  "job_id": "....",
  "annotated_pdf_url": "http://.../outputs/..../annotated.pdf",
  "results": [ /* BOM rows */ ],
  "material_results": [
    {
      "part_number": "TDQ300177-01",
      "description": "BASE PLATE",
      "material": { "expected": ["EN8", "SM45C"], "actual": "EN8", "status": "PASS" },
      "finish": { "expected": ["BLACKODISING"], "actual": "CHEMICAL BLACK", "status": "WARNING" },
      "heat": { "expected": "60-70", "actual": "....", "actual_range": "60-70", "status": "PASS" }
    }
  ]
}
```

## Frontend (Vite + React)

### Install
```bash
cd frontend
npm install
```

### Run (dev)
```bash
cd frontend
npm run dev
```

Frontend API base URL:
- `frontend/src/api.js` uses `VITE_API_BASE_URL` or defaults to `http://localhost:8001`

If you run the backend on a different port, set:
```bash
# Windows (PowerShell)
$env:VITE_API_BASE_URL="http://localhost:8000"
```

## Notes
- Material validation extraction relies on text patterns found in the PDF (e.g. `MATERIAL:`, `FINISH:`, `HARDENED/TEMPERED`).
- If the Material tab shows no results, ensure the backend is restarted after changes (or restart the backend instance your frontend is calling).

