import React, { useEffect, useMemo, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import Upload from "./Upload.jsx";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "../../node_modules/react-pdf/node_modules/pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

function IconZoomIn() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
    </svg>
  );
}
function IconZoomOut() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/>
    </svg>
  );
}
function IconChevronLeft() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="15 18 9 12 15 6"/>
    </svg>
  );
}
function IconChevronRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="9 18 15 12 9 6"/>
    </svg>
  );
}
function IconFileText() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
    </svg>
  );
}
function IconTrash() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
    </svg>
  );
}

export default function PdfViewer({ annotatedPdfUrl, loading, scrollTarget, onUpload, currentFileName, onReset }) {
  const containerRef = useRef(null);
  const [numPages, setNumPages]   = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale]         = useState(1.0);
  const [pdfError, setPdfError]   = useState("");

  const zoomLabel      = useMemo(() => `${Math.round(scale * 100)}%`, [scale]);
  const documentOptions = useMemo(() => ({ useWorkerFetch: false }), []);

  const userOverrideRef      = useRef(false);
  const pageOriginalWidthRef = useRef(null);

  const setScaleClamped = (next) => {
    const clamped = Math.max(0.6, Math.min(2.2, next));
    setScale((prev) => (Math.abs(prev - clamped) < 0.02 ? prev : clamped));
  };

  const refitToContainerWidth = () => {
    if (!containerRef.current || userOverrideRef.current || !pageOriginalWidthRef.current) return;
    const w = containerRef.current.clientWidth;
    if (!w || w <= 0) return;
    setScaleClamped(w / pageOriginalWidthRef.current);
  };

  useEffect(() => {
    if (!scrollTarget || !containerRef.current) return;
    if ((scrollTarget.page || 1) !== 1) return;
    if (pageNumber !== 1) { setPageNumber(1); return; }
    const container = containerRef.current;
    const pageEl = container.querySelector('.react-pdf__Page[data-page-number="1"]');
    if (!pageEl) return;
    const relTop = pageEl.getBoundingClientRect().top - container.getBoundingClientRect().top;
    const y = typeof scrollTarget.y_pdf === "number" ? scrollTarget.y_pdf : 0;
    container.scrollTop = relTop + y * scale - 40;
  }, [scrollTarget, scale, annotatedPdfUrl, numPages, pageNumber]);

  useEffect(() => {
    setPdfError(""); setPageNumber(1);
    userOverrideRef.current = false; setScale(1.0); pageOriginalWidthRef.current = null;
  }, [annotatedPdfUrl]);

  useEffect(() => {
    if (!annotatedPdfUrl || !containerRef.current) return;
    refitToContainerWidth();
    let ro = null;
    if (typeof ResizeObserver !== "undefined") {
      ro = new ResizeObserver(() => refitToContainerWidth());
      ro.observe(containerRef.current);
    } else {
      window.addEventListener("resize", refitToContainerWidth);
      return () => window.removeEventListener("resize", refitToContainerWidth);
    }
    return () => { if (ro) ro.disconnect(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [annotatedPdfUrl]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>

      {/* ── Top toolbar ── */}
      <div style={{
        padding: "8px 12px",
        borderBottom: "1px solid var(--color-border)",
        background: "var(--color-surface)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 8,
        flexShrink: 0,
      }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: "var(--text-sm)", color: "var(--color-text-primary)" }}>PDF Preview</div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>Drawing self-check — BOM & material validation</div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {annotatedPdfUrl && !loading && (
            <>
              <button
                className="btn btn-ghost btn-sm"
                style={{ color: "var(--color-error)" }}
                onClick={onReset}
              >
                <IconTrash />
                Clear PDF
              </button>
              <div style={{ width: 1, height: 16, background: "var(--color-border)", margin: "0 4px" }} />
            </>
          )}
          <button
            id="zoom-out"
            className="btn btn-ghost btn-sm"
            style={{ width: 28, padding: 0 }}
            onClick={() => { userOverrideRef.current = true; setScale((s) => Math.max(0.6, s - 0.1)); }}
            disabled={!annotatedPdfUrl || loading}
            title="Zoom out"
          >
            <IconZoomOut />
          </button>
          <div style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-text-secondary)", width: 40, textAlign: "center" }}>{zoomLabel}</div>
          <button
            id="zoom-in"
            className="btn btn-ghost btn-sm"
            style={{ width: 28, padding: 0 }}
            onClick={() => { userOverrideRef.current = true; setScale((s) => Math.min(2.2, s + 0.1)); }}
            disabled={!annotatedPdfUrl || loading}
            title="Zoom in"
          >
            <IconZoomIn />
          </button>
        </div>
      </div>

      {/* ── PDF canvas ── */}
      <div
        ref={containerRef}
        style={{
          flex: 1,
          overflow: "auto",
          background: "var(--color-surface-2)",
          position: "relative",
        }}
      >
        {!annotatedPdfUrl && (
          <div className="empty-state" style={{ height: "100%", justifyContent: "center" }}>
            <div style={{ maxWidth: 400, width: "100%" }}>
              <Upload onUpload={onUpload} loading={loading} currentFileName={currentFileName} />
            </div>
          </div>
        )}

        {annotatedPdfUrl && (
          <Document
            key={annotatedPdfUrl}
            file={annotatedPdfUrl}
            onLoadSuccess={({ numPages }) => { setNumPages(numPages); setPageNumber(1); }}
            onLoadError={(err) => setPdfError(err?.message || String(err))}
            options={documentOptions}
            loading={
              <div style={{ display: "flex", alignItems: "center", gap: 8, padding: 24, fontSize: "var(--text-sm)", color: "var(--color-text-secondary)" }}>
                <span style={{ display: "inline-block", width: 14, height: 14, borderRadius: "50%", border: "2px solid var(--color-border)", borderTopColor: "var(--color-brand)", animation: "spin 0.7s linear infinite" }} />
                Loading PDF…
              </div>
            }
            error={
              <div style={{ padding: 24, fontSize: "var(--text-sm)", color: "var(--color-error)" }}>
                Failed to render PDF.
                {pdfError && <div style={{ marginTop: 6, fontSize: "var(--text-xs)" }}>{pdfError}</div>}
              </div>
            }
          >
            {numPages && (
              <Page
                key={`page_${pageNumber}_${annotatedPdfUrl}`}
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                onLoadSuccess={(page) => {
                  if (page?.originalWidth) { pageOriginalWidthRef.current = page.originalWidth; refitToContainerWidth(); }
                }}
              />
            )}
          </Document>
        )}

        {/* Loading overlay */}
        {loading && (
          <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.04)", pointerEvents: "none" }} />
        )}
      </div>

      {/* ── Bottom pagination ── */}
      {annotatedPdfUrl && numPages && (
        <div style={{
          padding: "8px 12px",
          borderTop: "1px solid var(--color-border)",
          background: "var(--color-surface)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
          flexShrink: 0,
        }}>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>
            Page <strong style={{ color: "var(--color-text-primary)" }}>{pageNumber}</strong> of <strong style={{ color: "var(--color-text-primary)" }}>{numPages}</strong>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <button
              id="page-prev"
              className="btn btn-secondary btn-sm"
              style={{ width: 28, padding: 0 }}
              onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
              disabled={loading || pageNumber <= 1}
            >
              <IconChevronLeft />
            </button>

            <input
              type="number"
              min={1}
              max={numPages}
              value={pageNumber}
              onChange={(e) => { const v = parseInt(e.target.value, 10); if (!Number.isNaN(v)) setPageNumber(Math.max(1, Math.min(numPages, v))); }}
              className="input-field input-sm"
              style={{ width: 52, textAlign: "center", padding: "0 4px" }}
              disabled={loading}
              aria-label="Page number"
            />

            <button
              id="page-next"
              className="btn btn-secondary btn-sm"
              style={{ width: 28, padding: 0 }}
              onClick={() => setPageNumber((p) => Math.min(numPages, p + 1))}
              disabled={loading || pageNumber >= numPages}
            >
              <IconChevronRight />
            </button>
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
