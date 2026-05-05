import React, { useEffect, useMemo, useRef, useState } from "react";

// ── Helpers ────────────────────────────────────────────────────────────────
function formatExpected(expected) {
  if (Array.isArray(expected)) return expected.filter(Boolean).join(", ");
  if (expected == null) return "";
  return String(expected);
}

function worstStatus(statuses) {
  if (statuses.includes("FAIL"))    return "FAIL";
  if (statuses.includes("WARNING")) return "WARNING";
  if (statuses.includes("MISSING")) return "MISSING";
  if (statuses.includes("PASS"))    return "PASS";
  return "N/A";
}

function statusChipClass(status) {
  const map = { PASS: "pass", FAIL: "fail", WARNING: "warning", MISSING: "missing", "N/A": "na" };
  return `status-chip status-chip--${map[status] || "missing"}`;
}

function StatusChip({ status }) {
  const labels = { PASS: "Pass", FAIL: "Fail", WARNING: "Warning", MISSING: "Missing", "N/A": "N/A" };
  return (
    <span className={statusChipClass(status)}>
      <span className="status-chip__dot" />
      {labels[status] || status}
    </span>
  );
}

function leftAccentColor(status) {
  if (status === "PASS")    return "var(--color-success)";
  if (status === "WARNING") return "var(--color-warning)";
  if (status === "FAIL")    return "var(--color-error)";
  return "var(--color-text-tertiary)";
}

// ── Icons ──────────────────────────────────────────────────────────────────
function IconChevronRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="9 18 15 12 9 6"/>
    </svg>
  );
}
function IconChevronDown() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  );
}
function IconLayers() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>
    </svg>
  );
}
function IconSearch() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  );
}

// ── Skeleton ───────────────────────────────────────────────────────────────
function SkeletonRows() {
  return (
    <>
      {[70, 85, 60].map((w, i) => (
        <tr key={i}>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 14, width: "80%" }} /></td>
          <td colSpan={3} style={{ padding: "12px" }}><div className="skeleton" style={{ height: 14, width: `${w}%` }} /></td>
          <td style={{ padding: "12px" }}><div className="skeleton" style={{ height: 20, width: 64 }} /></td>
        </tr>
      ))}
    </>
  );
}

// ── Main component ─────────────────────────────────────────────────────────
export default function MaterialTable({ materialResults, loading, error, backendMaterialFieldMissing }) {
  const [filterMode, setFilterMode]     = useState("ALL");
  const [expandedParts, setExpandedParts] = useState(() => new Set());
  const [searchTerm, setSearchTerm]     = useState("");
  const userAdjustedExpandedRef         = useRef(false);

  const parts = materialResults || [];

  const fieldRowsByPart = useMemo(() =>
    parts.map((part) => {
      const rows = [
        { field: "Material", expected: formatExpected(part?.material?.expected), actual: part?.material?.actual || "",      status: part?.material?.status || "MISSING", key: "material" },
        { field: "Finish",   expected: formatExpected(part?.finish?.expected),   actual: part?.finish?.actual || "",        status: part?.finish?.status   || "MISSING", key: "finish"   },
        { field: "Heat",     expected: part?.heat?.expected || "NA",             actual: part?.heat?.actual_range || part?.heat?.actual || "", status: part?.heat?.status || "MISSING", key: "heat" },
      ];
      return { part, rows, overall: worstStatus(rows.map((r) => r.status)) };
    }), [parts]);

  const statusCounts = useMemo(() => {
    const c = { PASS: 0, WARNING: 0, FAIL: 0, MISSING: 0, "N/A": 0 };
    for (const pr of fieldRowsByPart) for (const r of pr.rows) { const s = r.status || "MISSING"; if (s in c) c[s]++; }
    return c;
  }, [fieldRowsByPart]);

  const visibleParts = useMemo(() => {
    const term = searchTerm.trim().toUpperCase();
    return fieldRowsByPart
      .filter(({ part }) => !term || (part?.part_number || "").toUpperCase().includes(term))
      .filter(({ rows }) => filterMode === "ALL" || rows.some((r) => r.status === filterMode))
      .map(({ part }) => part);
  }, [fieldRowsByPart, filterMode, searchTerm]);

  const visiblePartNumbers = useMemo(() => new Set((visibleParts || []).map((p) => p?.part_number).filter(Boolean)), [visibleParts]);

  useEffect(() => {
    if (!parts.length || userAdjustedExpandedRef.current) return;
    setExpandedParts(new Set(parts.map((p) => p?.part_number).filter(Boolean)));
  }, [parts]);

  const togglePart = (pn) => {
    userAdjustedExpandedRef.current = true;
    setExpandedParts((prev) => { const n = new Set(prev); n.has(pn) ? n.delete(pn) : n.add(pn); return n; });
  };
  const expandAll   = () => { userAdjustedExpandedRef.current = true; setExpandedParts(new Set(parts.map((p) => p?.part_number).filter(Boolean))); };
  const collapseAll = () => { userAdjustedExpandedRef.current = true; setExpandedParts(new Set()); };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>

      {/* Section header */}
      <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--color-border)", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: "var(--text-sm)", color: "var(--color-text-primary)" }}>Material Validation</div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>
            {parts?.length ? `${parts.length} parts extracted` : "Upload a PDF to begin"}
          </div>
        </div>
        {/* Status summary pills */}
        {parts.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span className="status-chip status-chip--pass"   style={{ fontSize: 11 }}><span className="status-chip__dot"/>Pass {statusCounts.PASS}</span>
            <span className="status-chip status-chip--warning" style={{ fontSize: 11 }}><span className="status-chip__dot"/>Warn {statusCounts.WARNING}</span>
            <span className="status-chip status-chip--fail"   style={{ fontSize: 11 }}><span className="status-chip__dot"/>Fail {statusCounts.FAIL}</span>
          </div>
        )}
      </div>

      {/* Toolbar */}
      <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--color-border)", display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        {/* Search */}
        <label htmlFor="mat-search" style={{ position: "relative", flex: 1, minWidth: 160 }}>
          <span style={{ position: "absolute", left: 9, top: "50%", transform: "translateY(-50%)", color: "var(--color-text-tertiary)", pointerEvents: "none" }}>
            <IconSearch />
          </span>
          <input
            id="mat-search"
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search part number"
            className="input-field input-sm"
            style={{ paddingLeft: 30 }}
          />
        </label>

        {/* Filter segment */}
        <div className="segment">
          {["ALL","FAIL","WARNING","MISSING","N/A"].map((mode) => {
            const activeClass = mode === "ALL" ? "seg-btn--active" : mode === "FAIL" ? "seg-btn--active-err" : mode === "WARNING" ? "seg-btn--active-warn" : "seg-btn--active";
            return (
              <button key={mode} className={`seg-btn ${filterMode === mode ? activeClass : ""}`} onClick={() => setFilterMode(mode)}>
                {mode === "ALL" ? "All" : mode === "N/A" ? "N/A" : mode.charAt(0) + mode.slice(1).toLowerCase()}
              </button>
            );
          })}
        </div>

        {/* Expand/collapse */}
        <button className="btn btn-ghost btn-sm" onClick={expandAll}   disabled={!parts.length}>Expand all</button>
        <button className="btn btn-ghost btn-sm" onClick={collapseAll} disabled={!expandedParts.size}>Collapse all</button>
      </div>

      {/* Error */}
      {error && <div style={{ padding: "8px 16px" }}><div className="alert alert--error">{error}</div></div>}

      {/* Table */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", overflowX: "auto" }}>
        {loading ? (
          <table className="data-table"><thead><tr><th style={{width:160}}>Part Number</th><th style={{width:90}}>Field</th><th>Expected</th><th>Actual</th><th style={{width:100}}>Status</th></tr></thead><tbody><SkeletonRows /></tbody></table>
        ) : visibleParts?.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 160 }}>Part Number</th>
                <th style={{ width: 90 }}>Field</th>
                <th>Expected</th>
                <th>Actual</th>
                <th style={{ width: 100 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {fieldRowsByPart
                .filter(({ part }) => visiblePartNumbers.has(part?.part_number))
                .map(({ part, rows, overall }) => {
                  const pn = part?.part_number;
                  const isExpanded = expandedParts.has(pn);
                  const visibleRows = filterMode === "ALL" ? rows : rows.filter((r) => r.status === filterMode);

                  return (
                    <React.Fragment key={pn}>
                      {/* Parent row */}
                      <tr
                        style={{
                          cursor: "pointer",
                          background: isExpanded ? "var(--color-surface-2)" : "var(--color-surface)",
                          borderLeft: `3px solid ${leftAccentColor(overall)}`,
                        }}
                        onClick={() => togglePart(pn)}
                      >
                        <td style={{ paddingLeft: 9 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <span style={{ color: "var(--color-text-tertiary)", flexShrink: 0 }}>
                              {isExpanded ? <IconChevronDown /> : <IconChevronRight />}
                            </span>
                            <div>
                              <div style={{ fontFamily: "monospace", fontSize: "var(--text-xs)", fontWeight: 600, color: "var(--color-text-primary)", wordBreak: "break-all" }}>{pn}</div>
                              {part?.description && (
                                <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 1, lineHeight: 1.3 }}>{part.description}</div>
                              )}
                              {part?.edm_code && (
                                <div style={{ fontSize: 11, color: "var(--color-brand)", marginTop: 2, fontFamily: "monospace", fontWeight: 600 }}>
                                  EDM: {part.edm_code}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td style={{ color: "var(--color-text-secondary)", fontSize: "var(--text-xs)" }}>
                          {visibleRows.length ? `${visibleRows.length} field${visibleRows.length > 1 ? "s" : ""}` : "No matches"}
                        </td>
                        <td style={{ color: "var(--color-text-tertiary)" }}>—</td>
                        <td style={{ color: "var(--color-text-tertiary)" }}>—</td>
                        <td><StatusChip status={overall} /></td>
                      </tr>

                      {/* Child rows */}
                      {isExpanded && visibleRows.map((r) => (
                        <tr key={`${pn}_${r.key}`} style={{ borderLeft: `3px solid ${leftAccentColor(r.status)}` }}>
                          <td style={{ paddingLeft: 9, fontFamily: "monospace", fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)", wordBreak: "break-all" }}>{pn}</td>
                          <td style={{ fontSize: "var(--text-xs)", fontWeight: 500, color: "var(--color-text-primary)" }}>{r.field}</td>
                          <td style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)", wordBreak: "break-word" }}>{r.expected || "—"}</td>
                          <td style={{ fontSize: "var(--text-xs)", color: "var(--color-text-primary)", wordBreak: "break-word" }}>{r.actual || "—"}</td>
                          <td><StatusChip status={r.status} /></td>
                        </tr>
                      ))}
                    </React.Fragment>
                  );
                })}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <span className="empty-state__icon"><IconLayers /></span>
            <div className="empty-state__title">
              {backendMaterialFieldMissing ? "Backend response missing material_results" : "No material results"}
            </div>
            <div className="empty-state__desc">
              {backendMaterialFieldMissing
                ? "Restart the backend and confirm the API response includes material_results."
                : parts.length ? "No parts match the current filter or search." : "Upload a drawing PDF to validate material specifications."}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
