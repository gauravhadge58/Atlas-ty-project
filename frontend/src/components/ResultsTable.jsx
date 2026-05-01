import React from "react";

function IconDownload() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
      <polyline points="7 10 12 15 17 10"/>
      <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  );
}

function IconFileSearch() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
  );
}

function StatusChip({ status }) {
  const map = {
    FOUND:    { cls: "status-chip status-chip--found",    label: "Found"    },
    STANDARD: { cls: "status-chip status-chip--standard", label: "Standard" },
    MISSING:  { cls: "status-chip status-chip--missing",  label: "Missing"  },
  };
  const cfg = map[status] || { cls: "status-chip", label: status };
  return (
    <span className={cfg.cls}>
      <span className="status-chip__dot" />
      {cfg.label}
    </span>
  );
}

function SkeletonRows() {
  return (
    <>
      {[80, 60, 90].map((w, i) => (
        <tr key={i}>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 14, width: 24 }} /></td>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 14, width: `${w}%` }} /></td>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 14, width: "70%" }} /></td>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 20, width: 70 }} /></td>
        </tr>
      ))}
    </>
  );
}

export default function ResultsTable({ results, allResults, loading, error, selectedItem, onRowClick, annotatedPdfUrl }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>

      {/* Section header */}
      <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, borderBottom: "1px solid var(--color-border)" }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: "var(--text-sm)", color: "var(--color-text-primary)" }}>Validation Results</div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>
            {allResults?.length ? `${allResults.length} BOM items` : "Upload a PDF to begin"}
          </div>
        </div>
        {annotatedPdfUrl && (
          <a href={annotatedPdfUrl} download className="btn btn-primary btn-sm" style={{ textDecoration: "none" }}>
            <IconDownload />
            Download PDF
          </a>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div style={{ padding: "8px 16px" }}>
          <div className="alert alert--error">{error}</div>
        </div>
      )}

      {/* Table area */}
      <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
        {loading || results?.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 48 }}>Item</th>
                <th style={{ width: 140 }}>Part Number</th>
                <th>Description</th>
                <th style={{ width: 100 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows />
              ) : (
                results.map((r) => {
                  const isSelected = selectedItem === r.item;
                  return (
                    <tr
                      key={`${r.item}_${r.part_number}`}
                      className={isSelected ? "row--selected" : ""}
                      style={{ cursor: "pointer" }}
                      onClick={() => onRowClick?.(r.item)}
                    >
                      <td style={{ color: "var(--color-text-primary)", fontWeight: 500 }}>{r.item}</td>
                      <td style={{ fontFamily: "monospace", fontSize: "var(--text-xs)", color: "var(--color-text-primary)", wordBreak: "break-all" }}>{r.part_number}</td>
                      <td style={{ color: "var(--color-text-secondary)" }}>{r.description}</td>
                      <td><StatusChip status={r.status} /></td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        ) : (
          /* Empty state */
          <div className="empty-state">
            <span className="empty-state__icon"><IconFileSearch /></span>
            <div className="empty-state__title">No results yet</div>
            <div className="empty-state__desc">
              {allResults?.length
                ? "No items match the current filter."
                : "Upload a drawing PDF above to validate the BOM."}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
