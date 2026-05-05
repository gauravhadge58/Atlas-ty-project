import React, { useMemo, useState } from "react";

// ── Icons ─────────────────────────────────────────────────────────────────
function IconLink() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
      <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
    </svg>
  );
}
function IconThread() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="10"/>
      <path d="M8 12h8M12 8v8"/>
    </svg>
  );
}
function IconHole() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="4"/>
    </svg>
  );
}
function IconFit() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="3" y="8" width="18" height="8" rx="2"/>
    </svg>
  );
}
function IconCSK() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M4 6h16M8 6l-4 12h16L16 6"/>
    </svg>
  );
}
function IconCBore() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="6" y="4" width="12" height="6" rx="1"/>
      <rect x="9" y="10" width="6" height="10" rx="1"/>
    </svg>
  );
}
function IconWasher() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="9"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

// ── Status badge ──────────────────────────────────────────────────────────
function StatusBadge({ status }) {
  const cfg = {
    PASS:    { bg: "var(--color-success-bg, #d1fae5)", color: "var(--color-success)", label: "✓ PASS" },
    FAIL:    { bg: "var(--color-error-bg, #fee2e2)",   color: "var(--color-error)",   label: "✕ FAIL" },
    WARNING: { bg: "var(--color-warn-bg, #fef9c3)",    color: "#b45309",              label: "⚠ WARN" },
  };
  const s = cfg[status] || cfg.WARNING;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: "2px 8px", borderRadius: 4,
      fontSize: 11, fontWeight: 700, letterSpacing: "0.04em",
      background: s.bg, color: s.color,
    }}>
      {s.label}
    </span>
  );
}

// ── Interface type badge ──────────────────────────────────────────────────
function TypeBadge({ type }) {
  const cfg = {
    THREAD:       { icon: <IconThread />, label: "Thread",       color: "var(--color-brand, #6366f1)" },
    HOLE_PATTERN: { icon: <IconHole />,   label: "Hole Pattern", color: "#0891b2" },
    BORE_SHAFT:   { icon: <IconFit />,    label: "Bore/Shaft",   color: "#7c3aed" },
    COUNTERSINK:  { icon: <IconCSK />,    label: "Countersink",  color: "#b45309" },
    COUNTERBORE:  { icon: <IconCBore />,  label: "Counterbore",  color: "#0f766e" },
    WASHER:       { icon: <IconWasher />, label: "Washer",       color: "#be185d" },
  };
  const t = cfg[type] || { icon: <IconLink />, label: type, color: "#64748b" };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      color: t.color, fontSize: 11, fontWeight: 600,
    }}>
      {t.icon}{t.label}
    </span>
  );
}

// ── Summary cards ─────────────────────────────────────────────────────────
function SummaryCards({ summary }) {
  if (!summary || summary.total === 0) return null;
  const passRate = summary.total > 0 ? Math.round((summary.pass / summary.total) * 100) : 0;

  const cards = [
    { label: "Total Checks", value: summary.total,   color: "var(--color-text-primary)" },
    { label: "Pass",         value: summary.pass,    color: "var(--color-success)" },
    { label: "Fail",         value: summary.fail,    color: "var(--color-error)" },
    { label: "Warning",      value: summary.warning, color: "#b45309" },
  ];

  return (
    <div style={{ padding: "12px 16px 0", display: "flex", gap: 10, flexWrap: "wrap" }}>
      {cards.map(c => (
        <div key={c.label} style={{
          flex: "1 1 80px", minWidth: 80,
          background: "var(--color-surface-raised, var(--color-surface))",
          border: "1px solid var(--color-border)",
          borderRadius: 8, padding: "8px 12px",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 2,
        }}>
          <span style={{ fontSize: 20, fontWeight: 700, color: c.color, lineHeight: 1 }}>{c.value}</span>
          <span style={{ fontSize: 10, color: "var(--color-text-tertiary)", letterSpacing: "0.05em", textTransform: "uppercase" }}>{c.label}</span>
        </div>
      ))}
      {/* Pass-rate bar */}
      <div style={{
        flex: "2 1 160px", minWidth: 140,
        background: "var(--color-surface-raised, var(--color-surface))",
        border: "1px solid var(--color-border)",
        borderRadius: 8, padding: "8px 14px",
        display: "flex", flexDirection: "column", gap: 6,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 10, color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Pass Rate</span>
          <span style={{ fontSize: 14, fontWeight: 700, color: passRate === 100 ? "var(--color-success)" : passRate >= 70 ? "#b45309" : "var(--color-error)" }}>
            {passRate}%
          </span>
        </div>
        <div style={{ height: 6, borderRadius: 3, background: "var(--color-border)", overflow: "hidden" }}>
          <div style={{
            height: "100%", borderRadius: 3,
            width: `${passRate}%`,
            background: passRate === 100 ? "var(--color-success)" : passRate >= 70 ? "#f59e0b" : "var(--color-error)",
            transition: "width 0.5s ease",
          }} />
        </div>
      </div>
    </div>
  );
}

// ── Empty / loading state ─────────────────────────────────────────────────
function EmptyState({ loading, error, jobId, onRunFitmentCheck }) {
  if (loading) return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 40 }}>
      <div style={{ textAlign: "center", color: "var(--color-text-tertiary)" }}>
        <div className="spinner" style={{ margin: "0 auto 12px" }} aria-label="Loading" />
        <div style={{ fontSize: 13 }}>Analysing fitment interfaces…</div>
      </div>
    </div>
  );
  if (error) return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 40, color: "var(--color-error)", fontSize: 13 }}>
      {error}
    </div>
  );
  
  // Show "Run Fitment Check" button if we have a jobId but no results
  if (jobId && onRunFitmentCheck) {
    return (
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 40, gap: 16 }}>
        <IconLink />
        <div style={{ fontSize: 13, color: "var(--color-text-tertiary)", textAlign: "center", marginBottom: 8 }}>
          Fitment validation is ready to run.<br />
          <span style={{ fontSize: 11 }}>Checks thread matches, hole patterns, and bore/shaft fits.</span>
        </div>
        <button
          onClick={onRunFitmentCheck}
          className="btn btn-primary"
          style={{
            padding: "10px 24px",
            fontSize: 14,
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <IconLink />
          Run Fitment Check
        </button>
        <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginTop: 4 }}>
          ⚠ This may take a few minutes
        </div>
      </div>
    );
  }
  
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 40, gap: 10 }}>
      <IconLink />
      <div style={{ fontSize: 13, color: "var(--color-text-tertiary)", textAlign: "center" }}>
        Upload a drawing PDF to run fitment verification.<br />
        <span style={{ fontSize: 11 }}>Checks thread matches, hole patterns, and bore/shaft fits.</span>
      </div>
    </div>
  );
}

// ── Profiles panel (expandable) ───────────────────────────────────────────
function ProfilesPanel({ profiles }) {
  const [open, setOpen] = useState(false);
  if (!profiles || Object.keys(profiles).length === 0) return null;

  return (
    <div style={{ borderTop: "1px solid var(--color-border)", padding: "0 16px 12px" }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--color-text-secondary)", fontSize: 11, fontWeight: 600,
          padding: "8px 0", display: "flex", alignItems: "center", gap: 6,
          letterSpacing: "0.03em", textTransform: "uppercase",
        }}
      >
        <span style={{ display: "inline-block", transform: open ? "rotate(90deg)" : "none", transition: "transform 0.2s" }}>▶</span>
        Extracted Dimension Profiles ({Object.keys(profiles).length} parts)
      </button>

      {open && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 4 }}>
          {Object.entries(profiles).map(([pn, p]) => (
            <div key={pn} style={{
              background: "var(--color-surface-raised, var(--color-bg))",
              border: "1px solid var(--color-border)", borderRadius: 6, padding: "8px 12px",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--color-text-primary)", fontFamily: "monospace" }}>{pn}</span>
                <span style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>{p.description}</span>
                <span style={{
                  marginLeft: "auto", fontSize: 10, fontWeight: 600,
                  padding: "1px 6px", borderRadius: 3,
                  background: p.gender === "male" ? "#dbeafe" : "#fce7f3",
                  color: p.gender === "male" ? "#1d4ed8" : "#be185d",
                }}>
                  {p.gender === "male" ? "♂ Male" : "♀ Female"}
                </span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {(p.threads || []).map((t, i) => (
                  <span key={i} style={{
                    fontSize: 10, padding: "2px 6px", borderRadius: 3,
                    background: "var(--color-surface)", border: "1px solid var(--color-border)",
                    color: "var(--color-brand, #6366f1)", fontWeight: 600, fontFamily: "monospace",
                  }}>
                    {t.label}
                  </span>
                ))}
                {(p.bore_shaft_fits || []).map((b, i) => (
                  <span key={`b${i}`} style={{
                    fontSize: 10, padding: "2px 6px", borderRadius: 3,
                    background: "var(--color-surface)", border: "1px solid var(--color-border)",
                    color: "#7c3aed", fontWeight: 600, fontFamily: "monospace",
                  }}>
                    Ø{b.nominal} {b.fit_code}
                  </span>
                ))}
                {p.threads?.length === 0 && p.bore_shaft_fits?.length === 0 && (
                  <span style={{ fontSize: 10, color: "var(--color-text-tertiary)" }}>No thread/fit data extracted</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────
export default function FitmentTable({ fitmentResults, fitmentSummary, fitmentProfiles, loading, error, jobId, onRunFitmentCheck }) {
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [filterType, setFilterType]     = useState("ALL");
  const [expandedRow, setExpandedRow]   = useState(null);

  const hasResults = fitmentResults && fitmentResults.length > 0;

  const filtered = useMemo(() => {
    if (!fitmentResults) return [];
    return fitmentResults.filter(r => {
      const statusOk = filterStatus === "ALL" || r.status === filterStatus;
      const typeOk   = filterType   === "ALL" || r.interface_type === filterType;
      return statusOk && typeOk;
    });
  }, [fitmentResults, filterStatus, filterType]);

  const hasProfiles = fitmentProfiles && Object.keys(fitmentProfiles).length > 0;

  // Show empty / loading state
  if (loading || error || (!hasResults && !hasProfiles)) {
    return <EmptyState loading={loading} error={error} jobId={jobId} onRunFitmentCheck={onRunFitmentCheck} />;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      {/* Summary cards */}
      <SummaryCards summary={fitmentSummary} />

      {/* Filter bar */}
      <div style={{
        padding: "10px 16px", display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap",
        borderBottom: "1px solid var(--color-border)", flexShrink: 0,
      }}>
        <span style={{ fontSize: 11, color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: 4 }}>Filter:</span>

        {["ALL", "PASS", "FAIL", "WARNING"].map(s => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            style={{
              fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 4, cursor: "pointer", border: "1px solid",
              borderColor: filterStatus === s ? "var(--color-brand, #6366f1)" : "var(--color-border)",
              background: filterStatus === s ? "var(--color-brand, #6366f1)" : "transparent",
              color: filterStatus === s ? "#fff" : "var(--color-text-secondary)",
              transition: "all 0.15s",
            }}
          >
            {s}
          </button>
        ))}

        <div style={{ width: 1, height: 16, background: "var(--color-border)", margin: "0 4px" }} />

        {["ALL", "THREAD", "HOLE_PATTERN", "BORE_SHAFT", "COUNTERSINK", "COUNTERBORE", "WASHER"].map(t => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            style={{
              fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 4, cursor: "pointer", border: "1px solid",
              borderColor: filterType === t ? "#0891b2" : "var(--color-border)",
              background: filterType === t ? "#0891b2" : "transparent",
              color: filterType === t ? "#fff" : "var(--color-text-secondary)",
              transition: "all 0.15s",
            }}
          >
            {t === "HOLE_PATTERN" ? "Holes" : t === "BORE_SHAFT" ? "Bore/Shaft"
              : t === "COUNTERSINK" ? "CSK" : t === "COUNTERBORE" ? "CBORE"
              : t === "WASHER" ? "Washer" : t}
          </button>
        ))}

        <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--color-text-tertiary)" }}>
          {filtered.length} of {fitmentResults.length}
        </span>
      </div>

      {/* Table */}
      <div style={{ flex: 1, overflow: "auto", minHeight: 0 }}>
        <table style={{
          width: "100%", borderCollapse: "collapse",
          fontSize: 12,
        }}>
          <thead>
            <tr style={{ background: "var(--color-surface-raised, var(--color-surface))" }}>
              <th style={{
                width: 28, padding: "8px 4px 8px 12px",
                borderBottom: "1px solid var(--color-border)",
                position: "sticky", top: 0,
                background: "var(--color-surface-raised, var(--color-surface))",
              }} />
              {["Part A", "Part B", "Type", "Feature A", "Feature B", "Status"].map(h => (
                <th key={h} style={{
                  textAlign: "left", padding: "8px 12px",
                  fontSize: 10, fontWeight: 700, letterSpacing: "0.06em",
                  textTransform: "uppercase", color: "var(--color-text-tertiary)",
                  borderBottom: "1px solid var(--color-border)",
                  position: "sticky", top: 0,
                  background: "var(--color-surface-raised, var(--color-surface))",
                  whiteSpace: "nowrap",
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: 32, color: "var(--color-text-tertiary)", fontSize: 12 }}>
                  No results match the current filters.
                </td>
              </tr>
            ) : filtered.map((r, i) => (
              <React.Fragment key={i}>
                <tr
                  title={r.message}
                  onClick={() => setExpandedRow(expandedRow === i ? null : i)}
                  style={{
                    borderBottom: "1px solid var(--color-border)",
                    background: expandedRow === i 
                      ? "var(--color-surface-raised, rgba(99,102,241,0.08))"
                      : r.status === "FAIL"
                      ? "rgba(239,68,68,0.04)"
                      : r.status === "WARNING"
                      ? "rgba(234,179,8,0.04)"
                      : "transparent",
                    transition: "background 0.12s",
                    cursor: "pointer",
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = expandedRow === i ? "var(--color-surface-raised, rgba(99,102,241,0.08))" : "var(--color-surface-raised, rgba(99,102,241,0.04))"}
                  onMouseLeave={e => e.currentTarget.style.background = expandedRow === i 
                    ? "var(--color-surface-raised, rgba(99,102,241,0.08))"
                    : r.status === "FAIL"
                    ? "rgba(239,68,68,0.04)"
                    : r.status === "WARNING"
                    ? "rgba(234,179,8,0.04)"
                    : "transparent"}
                >
                  {/* Chevron expand indicator */}
                  <td style={{ padding: "7px 4px 7px 12px", width: 28, color: "var(--color-text-tertiary)", transition: "transform 0.2s" }}>
                    <span style={{
                      display: "inline-block",
                      fontSize: 9,
                      transform: expandedRow === i ? "rotate(90deg)" : "rotate(0deg)",
                      transition: "transform 0.2s ease",
                      opacity: 0.6,
                    }}>▶</span>
                  </td>
                  <td style={{ padding: "7px 12px", fontFamily: "monospace", fontSize: 11, fontWeight: 600, color: "var(--color-text-primary)", whiteSpace: "nowrap" }}>
                    {r.part_a}
                  </td>
                  <td style={{ padding: "7px 12px", fontFamily: "monospace", fontSize: 11, fontWeight: 600, color: "var(--color-text-primary)", whiteSpace: "nowrap" }}>
                    {r.part_b}
                  </td>
                  <td style={{ padding: "7px 12px", whiteSpace: "nowrap" }}>
                    <TypeBadge type={r.interface_type} />
                  </td>
                  <td style={{ padding: "7px 12px", fontFamily: "monospace", fontSize: 11, color: "var(--color-text-secondary)", whiteSpace: "nowrap" }}>
                    {r.feature_a}
                  </td>
                  <td style={{ padding: "7px 12px", fontFamily: "monospace", fontSize: 11, color: "var(--color-text-secondary)", whiteSpace: "nowrap" }}>
                    {r.feature_b}
                  </td>
                  <td style={{ padding: "7px 12px", whiteSpace: "nowrap" }}>
                    <StatusBadge status={r.status} />
                  </td>
                </tr>
                {expandedRow === i && (
                  <tr style={{ background: "var(--color-surface-raised, rgba(0,0,0,0.015))", borderBottom: "1px solid var(--color-border)" }}>
                    <td colSpan={8} style={{ padding: "14px 20px" }}>
                      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>

                        {/* Root cause banner */}
                        {r.checks && Object.entries(r.checks).some(([,v]) => v.startsWith("FAIL") || v.startsWith("WARNING")) && (
                          <div style={{
                            background: r.status === "FAIL" ? "rgba(239,68,68,0.08)" : "rgba(234,179,8,0.08)",
                            border: `1px solid ${r.status === "FAIL" ? "rgba(239,68,68,0.3)" : "rgba(234,179,8,0.3)"}`,
                            borderRadius: 6, padding: "10px 14px",
                          }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: r.status === "FAIL" ? "var(--color-error)" : "#b45309", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                              {r.status === "FAIL" ? "❌ Root Cause" : "⚠ Warnings"}
                            </div>
                            {Object.entries(r.checks)
                              .filter(([,v]) => v.startsWith("FAIL") || v.startsWith("WARNING"))
                              .map(([k, v]) => (
                                <div key={k} style={{ fontSize: 12, color: v.startsWith("FAIL") ? "var(--color-error)" : "#92400e", marginBottom: 3, lineHeight: 1.4 }}>
                                  <strong style={{ textTransform: "capitalize" }}>{k.replace(/_/g, " ")}:</strong> {v.replace(/^(FAIL|WARNING): /, "")}
                                </div>
                              ))}
                          </div>
                        )}

                        {/* All checks grid */}
                        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em", borderBottom: "1px solid var(--color-border)", paddingBottom: 4 }}>
                          All Validation Checks
                        </div>
                        {r.checks && Object.keys(r.checks).length > 0 ? (
                          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 7 }}>
                            {Object.entries(r.checks)
                              .sort(([,a],[,b]) => {
                                const rank = v => v.startsWith("FAIL") ? 0 : v.startsWith("WARNING") ? 1 : 2;
                                return rank(a) - rank(b);
                              })
                              .map(([checkKey, checkVal]) => {
                                const isFail = checkVal.startsWith("FAIL");
                                const isWarn = checkVal.startsWith("WARNING");
                                const isPass = checkVal.startsWith("PASS");
                                const color = isFail ? "var(--color-error)" : isWarn ? "#b45309" : isPass ? "var(--color-success)" : "var(--color-text-tertiary)";
                                const icon = isFail ? "❌" : isWarn ? "⚠" : isPass ? "✓" : "—";
                                const title = checkKey.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                                return (
                                  <div key={checkKey} style={{
                                    background: "var(--color-bg)",
                                    border: "1px solid var(--color-border)",
                                    borderLeft: `3px solid ${color}`,
                                    padding: "7px 10px", borderRadius: 4, fontSize: 11,
                                  }}>
                                    <div style={{ fontWeight: 700, color: "var(--color-text-secondary)", marginBottom: 2, display: "flex", alignItems: "center", gap: 4 }}>
                                      <span>{icon}</span> {title}
                                    </div>
                                    <div style={{ color: isFail ? "var(--color-error)" : isWarn ? "#92400e" : "var(--color-text-primary)", lineHeight: 1.4 }}>
                                      {checkVal.replace(/^(FAIL|WARNING|PASS): /, "")}
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        ) : (
                          <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", fontStyle: "italic" }}>
                            No granular checks available.
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Message area – shows on row hover via tooltip title above; 
          also show an expandable last-fail message */}
      {fitmentSummary?.fail > 0 && (
        <div style={{
          padding: "8px 16px",
          background: "rgba(239,68,68,0.06)",
          borderTop: "1px solid rgba(239,68,68,0.15)",
          fontSize: 11, color: "var(--color-error)",
        }}>
          ⚠ {fitmentSummary.fail} fitment issue{fitmentSummary.fail > 1 ? "s" : ""} found — hover a row for details.
        </div>
      )}

      {/* Profiles panel */}
      <ProfilesPanel profiles={fitmentProfiles} />
    </div>
  );
}
