import React, { useMemo, useState } from "react";
import Upload from "./components/Upload.jsx";
import PdfViewer from "./components/PdfViewer.jsx";
import ResultsTable from "./components/ResultsTable.jsx";
import { uploadPdf } from "./api.js";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [annotatedPdfUrl, setAnnotatedPdfUrl] = useState("");
  const [results, setResults] = useState([]);
  const [bomAnnotationPositions, setBomAnnotationPositions] = useState([]);
  const [uploadedFileName, setUploadedFileName] = useState("");

  const [missingOnly, setMissingOnly] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const yByItem = useMemo(() => {
    const map = new Map();
    for (const p of bomAnnotationPositions || []) {
      map.set(p.item, p.y_pdf);
    }
    return map;
  }, [bomAnnotationPositions]);

  const scrollTarget = useMemo(() => {
    if (selectedItem == null) return null;
    const y_pdf = yByItem.get(selectedItem);
    if (typeof y_pdf !== "number") return null;
    return { page: 1, y_pdf };
  }, [selectedItem, yByItem]);

  async function handleUpload(file) {
    setError("");
    setLoading(true);
    setResults([]);
    setBomAnnotationPositions([]);
    setSelectedItem(null);
    setAnnotatedPdfUrl("");
    setUploadedFileName(file?.name || "");
    try {
      const data = await uploadPdf(file);
      setAnnotatedPdfUrl(data.annotated_pdf_url);
      setResults(data.results || []);
      setBomAnnotationPositions(data.bom_annotation_positions || []);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || "Upload failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const filteredResults = useMemo(() => {
    if (!missingOnly) return results;
    return (results || []).filter((r) => r.status === "MISSING");
  }, [results, missingOnly]);

  const counts = useMemo(() => {
    const c = { FOUND: 0, STANDARD: 0, MISSING: 0 };
    for (const r of results || []) {
      if (r?.status in c) c[r.status] += 1;
    }
    return c;
  }, [results]);

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-50 via-indigo-50/60 to-white">
      <header className="px-6 py-4">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="text-lg font-semibold text-slate-900">Drawing BOM Validator</div>
            <div className="text-sm text-slate-600">
              Upload a drawing PDF to validate its BOM and mark the BOM rows on page 1.
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 justify-end">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-600">Legend</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-50 text-green-800 border border-green-200 text-xs">
                ✔ FOUND ({counts.FOUND})
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200 text-xs">
                ⚙ STANDARD ({counts.STANDARD})
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full bg-red-50 text-red-800 border border-red-200 text-xs">
                ✖ MISSING ({counts.MISSING})
              </span>
            </div>

            <label className="flex items-center gap-2 text-sm text-slate-700 bg-white/70 backdrop-blur px-3 py-2 rounded-xl border border-slate-200">
              <input
                type="checkbox"
                checked={missingOnly}
                onChange={(e) => setMissingOnly(e.target.checked)}
              />
              Show only missing
            </label>
          </div>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 px-4 pb-4 min-h-0">
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white/70 backdrop-blur shadow-sm min-h-0 flex flex-col">
          <PdfViewer
            annotatedPdfUrl={annotatedPdfUrl}
            loading={loading}
            scrollTarget={scrollTarget}
          />
        </section>
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white/70 backdrop-blur shadow-sm min-h-0 flex flex-col">
          <div className="px-4 pt-4">
            <Upload
              onUpload={handleUpload}
              loading={loading}
              currentFileName={uploadedFileName}
            />
          </div>

          <div className="flex-1 min-h-0 pb-4">
            <ResultsTable
              results={filteredResults}
              allResults={results}
              loading={loading}
              error={error}
              selectedItem={selectedItem}
              onRowClick={(item) => setSelectedItem(item)}
              annotatedPdfUrl={annotatedPdfUrl}
            />
          </div>
        </section>
      </main>
    </div>
  );
}

