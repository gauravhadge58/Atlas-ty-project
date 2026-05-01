import React, { useCallback, useMemo, useRef, useState } from "react";

function IconUpload() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  );
}

function IconFile() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
    </svg>
  );
}

export default function Upload({ onUpload, loading, currentFileName }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const onPickFile = useCallback(() => {
    if (!loading) inputRef.current?.click();
  }, [loading]);

  const onFileSelected = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") onUpload(file);
  }, [onUpload]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    if (loading) return;
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === "application/pdf") onUpload(file);
  }, [loading, onUpload]);

  const zoneClass = [
    "drop-zone",
    dragActive ? "drop-zone--active" : "",
    loading    ? "drop-zone--loading" : "",
  ].filter(Boolean).join(" ");

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        id="pdf-file-input"
        accept="application/pdf"
        style={{ display: "none" }}
        onChange={onFileSelected}
        disabled={loading}
      />

      <div
        id="pdf-drop-zone"
        className={zoneClass}
        onClick={onPickFile}
        onDragOver={(e) => { e.preventDefault(); if (!loading) setDragActive(true); }}
        onDragEnter={(e) => { e.preventDefault(); if (!loading) setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={loading ? -1 : 0}
        aria-label="Upload PDF file"
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onPickFile(); }}
        style={{ marginBottom: 0 }}
      >
        {loading ? (
          /* skeleton shimmer while processing */
          <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "4px 0" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, color: "var(--color-text-secondary)", fontSize: "var(--text-xs)" }}>
              <span style={{
                display: "inline-block", width: 16, height: 16, borderRadius: "50%",
                border: "2px solid var(--color-border)", borderTopColor: "var(--color-brand)",
                animation: "spin 0.7s linear infinite",
              }} />
              Processing PDF…
            </div>
            <div className="skeleton" style={{ height: 6, width: "60%", margin: "0 auto" }} />
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12 }}>
            <span style={{ color: dragActive ? "var(--color-brand)" : "var(--color-text-tertiary)" }}>
              <IconUpload />
            </span>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--color-text-primary)" }}>
                {dragActive ? "Drop PDF here" : "Drag & drop a PDF, or click to select"}
              </div>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)", marginTop: 2 }}>
                Engineering drawing PDF only
              </div>
            </div>
          </div>
        )}
      </div>

      {currentFileName && !loading && (
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 8, fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>
          <IconFile />
          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {currentFileName}
          </span>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
