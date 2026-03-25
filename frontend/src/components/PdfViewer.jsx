import React, { useEffect, useMemo, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";

// Use a locally bundled pdf.js worker to avoid CDN/network issues.
// This prevents react-pdf from falling back to a fake worker.
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "../../node_modules/react-pdf/node_modules/pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

export default function PdfViewer({ annotatedPdfUrl, loading, scrollTarget }) {
  const containerRef = useRef(null);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.1);
  const [pdfError, setPdfError] = useState("");

  const zoomLabel = useMemo(() => `${Math.round(scale * 100)}%`, [scale]);
  const documentOptions = useMemo(() => ({ useWorkerFetch: false }), []);

  useEffect(() => {
    if (!scrollTarget || !containerRef.current) return;
    // BOM annotations are on page 1.
    const targetPage = scrollTarget.page || 1;
    if (targetPage !== 1) return;

    // Ensure page 1 is rendered before we attempt to scroll.
    if (pageNumber !== 1) {
      setPageNumber(1);
      return;
    }

    const container = containerRef.current;
    const pageEl = container.querySelector('.react-pdf__Page[data-page-number="1"]');
    if (!pageEl) return;

    const containerRect = container.getBoundingClientRect();
    const pageRect = pageEl.getBoundingClientRect();
    const relativeTop = pageRect.top - containerRect.top;

    const y = typeof scrollTarget.y_pdf === "number" ? scrollTarget.y_pdf : 0;
    container.scrollTop = relativeTop + y * scale - 40;
  }, [scrollTarget, scale, annotatedPdfUrl, numPages, pageNumber]);

  useEffect(() => {
    setPdfError("");
    setPageNumber(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [annotatedPdfUrl]);

  return (
    <div className="flex flex-col min-h-0 h-full">
      <div className="px-4 py-3 border-b border-slate-200 bg-white/70 backdrop-blur flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-slate-900">PDF</div>
          <div className="text-xs text-slate-600">BOM validated against extracted text</div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="h-9 w-9 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-slate-700"
            onClick={() => setScale((s) => Math.max(0.6, s - 0.1))}
            disabled={!annotatedPdfUrl || loading}
          >
            -
          </button>
          <div className="text-sm text-slate-700 w-16 text-center font-medium">{zoomLabel}</div>
          <button
            type="button"
            className="h-9 w-9 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-slate-700"
            onClick={() => setScale((s) => Math.min(2.2, s + 0.1))}
            disabled={!annotatedPdfUrl || loading}
          >
            +
          </button>
        </div>
      </div>

      <div ref={containerRef} className="flex-1 overflow-auto bg-slate-50 relative">
        {!annotatedPdfUrl ? (
          <div className="h-full flex items-center justify-center p-6">
            <div className="w-full max-w-md text-center">
              <div className="text-sm font-semibold text-slate-900">No PDF loaded</div>
              <div className="mt-2 text-sm text-slate-600">
                Drag & drop a drawing PDF. The app will extract the BOM from page 1,
                detect part definitions on the remaining pages, and annotate the BOM.
              </div>
            </div>
          </div>
        ) : null}

        {annotatedPdfUrl ? (
          <Document
            key={annotatedPdfUrl}
            file={annotatedPdfUrl}
            onLoadSuccess={({ numPages }) => {
              setNumPages(numPages);
              setPageNumber(1);
            }}
            onLoadError={(err) => setPdfError(err?.message || String(err))}
            options={documentOptions}
            loading={
              <div className="p-6 text-sm text-slate-600 flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-full border-2 border-slate-300 border-t-slate-900 animate-spin" />
                Loading PDF...
              </div>
            }
            error={
              <div className="p-6 text-sm text-red-700">
                Failed to load PDF.
                {pdfError ? <div className="mt-2 text-xs text-red-800">{pdfError}</div> : null}
              </div>
            }
          >
            {numPages ? (
              <Page
                key={`page_${pageNumber}`}
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
            ) : null}
          </Document>
        ) : null}

        {loading ? (
          <div className="absolute inset-0 bg-slate-900/5 pointer-events-none" />
        ) : null}
      </div>

      {annotatedPdfUrl && numPages ? (
        <div className="px-4 py-3 border-t border-slate-200 bg-white/70 backdrop-blur flex items-center justify-between gap-3">
          <div className="text-xs text-slate-600">
            Page <span className="font-semibold text-slate-800">{pageNumber}</span> of{" "}
            <span className="font-semibold text-slate-800">{numPages}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="px-3 py-1 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-sm font-medium text-slate-700 disabled:opacity-50"
              onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
              disabled={loading || pageNumber <= 1}
            >
              Prev
            </button>

            <input
              type="number"
              min={1}
              max={numPages}
              value={pageNumber}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (Number.isNaN(v)) return;
                setPageNumber(Math.max(1, Math.min(numPages, v)));
              }}
              className="w-20 px-2 py-1 text-sm rounded-xl border border-slate-200 bg-white/80 text-slate-800"
              disabled={loading}
            />

            <button
              type="button"
              className="px-3 py-1 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-sm font-medium text-slate-700 disabled:opacity-50"
              onClick={() => setPageNumber((p) => Math.min(numPages, p + 1))}
              disabled={loading || pageNumber >= numPages}
            >
              Next
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

