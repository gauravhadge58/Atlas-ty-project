import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getMaterialReference, uploadMaterialExcel, saveMaterialReference, resetMaterialReference } from "../api.js";

// ── Helpers ────────────────────────────────────────────────────────────────
function listStr(arr) { return Array.isArray(arr) ? arr.join(", ") : arr || ""; }
function toArray(val) {
  if (Array.isArray(val)) return val;
  if (typeof val === "string") return val.split(",").map((s) => s.trim()).filter(Boolean);
  return [];
}

// ── Icons ──────────────────────────────────────────────────────────────────
function IconArrowLeft() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
    </svg>
  );
}
function IconUpload() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  );
}
function IconEdit() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
    </svg>
  );
}
function IconRefresh() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/>
    </svg>
  );
}
function IconPlus() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  );
}
function IconSave() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
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
function IconSearch() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  );
}
function IconTable() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="9" x2="9" y2="21"/>
    </svg>
  );
}

// ── Editable row ───────────────────────────────────────────────────────────
function EditableRow({ row, index, onChange, onDelete }) {
  function inp(key, placeholder = "") {
    return (
      <input
        value={key === "materials" || key === "finish" ? listStr(row[key]) : row[key] ?? ""}
        onChange={(e) => {
          const val = e.target.value;
          if (key === "materials" || key === "finish") {
            onChange(index, key, val.split(",").map((s) => s.trim()).filter(Boolean));
          } else {
            onChange(index, key, val);
          }
        }}
        placeholder={placeholder}
        className="input-field input-sm"
        style={{ borderRadius: "var(--radius-sm)" }}
      />
    );
  }

  return (
    <tr>
      <td style={{ padding: "6px 12px", fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)", fontFamily: "monospace", textAlign: "center", width: 40 }}>{index + 1}</td>
      <td style={{ padding: "6px 8px" }}>{inp("base_material", "e.g. Low carbon Steel")}</td>
      <td style={{ padding: "6px 8px", width: 136 }}>{inp("edm", "e.g. EDM000136")}</td>
      <td style={{ padding: "6px 8px" }}>{inp("materials", "e.g. EN8, 80M40")}</td>
      <td style={{ padding: "6px 8px" }}>{inp("finish", "e.g. BLACKODISING")}</td>
      <td style={{ padding: "6px 8px", width: 160 }}>{inp("heat", "e.g. 60-70 or blank")}</td>
      <td style={{ padding: "6px 8px", textAlign: "center", width: 44 }}>
        <button
          type="button"
          onClick={() => onDelete(index)}
          className="btn btn-danger-ghost btn-sm"
          title="Delete row"
          style={{ width: 28, padding: 0 }}
        >
          <IconTrash />
        </button>
      </td>
    </tr>
  );
}

// ── Read-only row ──────────────────────────────────────────────────────────
function ReadOnlyRow({ row, index }) {
  const hasHeat = row.heat && row.heat.trim() !== "" && row.heat.toUpperCase() !== "NA";
  return (
    <tr>
      <td style={{ padding: "10px 12px", fontSize: "var(--text-xs)", color: "var(--color-text-tertiary)", fontFamily: "monospace", textAlign: "center", width: 40 }}>{index + 1}</td>
      <td style={{ padding: "10px 12px", fontSize: "var(--text-sm)", color: "var(--color-text-primary)" }}>{row.base_material || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}</td>
      <td style={{ padding: "10px 12px", fontFamily: "monospace", fontSize: "var(--text-xs)", fontWeight: 600, color: "var(--color-brand)", width: 136 }}>{row.edm}</td>
      <td style={{ padding: "10px 12px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
          {toArray(row.materials).map((m, i) => <span key={i} className="badge badge--blue">{m}</span>)}
        </div>
      </td>
      <td style={{ padding: "10px 12px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
          {toArray(row.finish).map((f, i) => <span key={i} className="badge badge--slate">{f}</span>)}
        </div>
      </td>
      <td style={{ padding: "10px 12px", width: 160 }}>
        {hasHeat ? <span className="badge badge--amber">{row.heat}</span> : <span style={{ color: "var(--color-text-tertiary)", fontSize: "var(--text-xs)" }}>NA</span>}
      </td>
    </tr>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────
export default function MaterialReferencePage() {
  const [rows, setRows]           = useState([]);
  const [editMode, setEditMode]   = useState(false);
  const [editRows, setEditRows]   = useState([]);
  const [loading, setLoading]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError]         = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const fileInputRef              = useRef(null);

  useEffect(() => { loadTable(); }, []);

  async function loadTable() {
    setLoading(true); setError("");
    try { const data = await getMaterialReference(); setRows(data.rows || []); }
    catch (e) { setError(e?.response?.data?.detail || "Failed to load reference table."); }
    finally { setLoading(false); }
  }

  function startEdit()  { setEditRows(rows.map((r) => ({ ...r }))); setEditMode(true); setSuccessMsg(""); setError(""); }
  function cancelEdit() { setEditMode(false); setEditRows([]); }

  function handleChange(index, key, value) {
    setEditRows((prev) => { const n = [...prev]; n[index] = { ...n[index], [key]: value }; return n; });
  }
  function handleDelete(index) { setEditRows((prev) => prev.filter((_, i) => i !== index)); }
  function handleAddRow() {
    setEditRows((prev) => [...prev, { edm: "", materials: [], finish: [], heat: "", base_material: "", use_notes: "" }]);
  }

  async function handleSave() {
    setSaving(true); setError(""); setSuccessMsg("");
    try {
      await saveMaterialReference(editRows);
      setRows(editRows); setEditMode(false);
      setSuccessMsg(`Saved ${editRows.length} rows — future validations will use this table.`);
    } catch (e) { setError(e?.response?.data?.detail || "Failed to save table."); }
    finally { setSaving(false); }
  }

  async function handleExcelUpload(e) {
    const file = e.target.files?.[0]; if (!file) return;
    setUploading(true); setError(""); setSuccessMsg("");
    try {
      const data = await uploadMaterialExcel(file);
      const parsed = data.rows || [];
      setEditRows(parsed); setEditMode(true);
      setSuccessMsg(`Parsed ${parsed.length} rows from "${file.name}". Review below and click Save & Apply.`);
    } catch (e) { setError(e?.response?.data?.detail || "Failed to parse Excel file."); }
    finally { setUploading(false); e.target.value = ""; }
  }

  async function handleReset() {
    if (!window.confirm("Reset to factory defaults? All custom changes will be lost.")) return;
    setLoading(true); setError(""); setSuccessMsg("");
    try {
      const data = await resetMaterialReference();
      setRows(data.rows || []); setEditMode(false);
      setSuccessMsg("Table reset to factory defaults.");
    } catch (e) { setError(e?.response?.data?.detail || "Failed to reset."); }
    finally { setLoading(false); }
  }

  const activeRows = editMode ? editRows : rows;
  const displayRows = activeRows.filter((r) => {
    const term = searchTerm.trim().toUpperCase();
    if (!term) return true;
    return (r.edm || "").toUpperCase().includes(term) ||
           (r.base_material || "").toUpperCase().includes(term) ||
           listStr(r.materials).toUpperCase().includes(term);
  });

  return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", background: "var(--color-bg)", overflow: "hidden" }}>

      {/* ── Page sub-header: title + actions ── */}
      <div style={{ background: "var(--color-surface)", borderBottom: "1px solid var(--color-border)", flexShrink: 0 }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 24px", height: 48, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <h1 style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--color-text-primary)", lineHeight: 1.25 }}>
              Material Reference Table
            </h1>
            <p style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>
              {editMode
                ? `Editing ${editRows.length} rows — click Save & Apply to activate`
                : `${rows.length} entries active · used for material validation`}
            </p>
          </div>

          {/* Action buttons */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {!editMode ? (
              <>
                <label className={`btn btn-primary btn-sm ${uploading ? "btn--loading" : ""}`} style={{ cursor: uploading ? "wait" : "pointer" }}>
                  <IconUpload />
                  {uploading ? "Parsing…" : "Upload Excel"}
                  <input ref={fileInputRef} type="file" accept=".xlsx,.xls" style={{ display: "none" }} onChange={handleExcelUpload} disabled={uploading} />
                </label>
                <button className="btn btn-secondary btn-sm" onClick={startEdit}>
                  <IconEdit />
                  Edit Table
                </button>
                <button className="btn btn-ghost btn-sm" onClick={handleReset} title="Reset to factory defaults">
                  <IconRefresh />
                  Reset
                </button>
              </>
            ) : (
              <>
                <button className="btn btn-success btn-sm" onClick={handleAddRow}>
                  <IconPlus />
                  Add Row
                </button>
                <button className="btn btn-ghost btn-sm" onClick={cancelEdit}>Cancel</button>
                <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
                  {saving ? (
                    <span style={{ display: "inline-block", width: 14, height: 14, borderRadius: "50%", border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "#fff", animation: "spin 0.7s linear infinite" }} />
                  ) : <IconSave />}
                  {saving ? "Saving…" : "Save & Apply"}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── Banners ── */}
      <div style={{ maxWidth: 1280, margin: "0 auto", width: "100%", padding: "0 24px" }}>
        {editMode && (
          <div className="alert alert--warning" style={{ marginTop: 12 }}>
            You are in <strong>edit mode</strong>. Changes are not applied until you click <strong>Save &amp; Apply</strong>.
          </div>
        )}
        {successMsg && <div className="alert alert--success" style={{ marginTop: 12 }}>{successMsg}</div>}
        {error      && <div className="alert alert--error"   style={{ marginTop: 12 }}>{error}</div>}
      </div>

      {/* ── Main content ── */}
      <main style={{ flex: 1, minHeight: 0, maxWidth: 1280, margin: "0 auto", width: "100%", padding: "16px 24px 24px", display: "flex", flexDirection: "column", gap: 12 }}>

        {/* Toolbar */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <label htmlFor="ref-search" style={{ position: "relative", maxWidth: 280, flex: 1 }}>
            <span style={{ position: "absolute", left: 9, top: "50%", transform: "translateY(-50%)", color: "var(--color-text-tertiary)", pointerEvents: "none" }}>
              <IconSearch />
            </span>
            <input
              id="ref-search"
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search EDM, material, base…"
              className="input-field"
              style={{ paddingLeft: 30 }}
            />
          </label>
          <span style={{ fontSize: "var(--text-xs)", color: "var(--color-text-secondary)" }}>
            {displayRows.length} {displayRows.length === 1 ? "row" : "rows"}{searchTerm ? " found" : ""}
          </span>
        </div>

        {/* Table card */}
        <div className="card" style={{ flex: 1, minHeight: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {loading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, padding: "64px 24px", color: "var(--color-text-secondary)", fontSize: "var(--text-sm)" }}>
              <span style={{ display: "inline-block", width: 18, height: 18, borderRadius: "50%", border: "2px solid var(--color-border)", borderTopColor: "var(--color-brand)", animation: "spin 0.7s linear infinite" }} />
              Loading reference table…
            </div>
          ) : (
            <div style={{ overflow: "auto", flex: 1, minHeight: 0 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: 40 }}>#</th>
                    <th>Base Material</th>
                    <th style={{ width: 136 }}>EDM Code</th>
                    <th>
                      Material Grades
                      {editMode && <span style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0, color: "var(--color-text-tertiary)", marginLeft: 4, fontSize: 11 }}>(comma-sep)</span>}
                    </th>
                    <th>
                      Surface Finish
                      {editMode && <span style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0, color: "var(--color-text-tertiary)", marginLeft: 4, fontSize: 11 }}>(comma-sep)</span>}
                    </th>
                    <th style={{ width: 160 }}>Heat Treatment</th>
                    {editMode && <th style={{ width: 44 }} />}
                  </tr>
                </thead>
                <tbody>
                  {displayRows.length === 0 ? (
                    <tr>
                      <td colSpan={editMode ? 7 : 6}>
                        <div className="empty-state">
                          <span className="empty-state__icon"><IconTable /></span>
                          <div className="empty-state__title">{searchTerm ? "No rows match your search" : "No rows yet"}</div>
                          <div className="empty-state__desc">
                            {searchTerm ? "Try a different search term." : "Upload an Excel file or click Edit Table to add rows manually."}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ) : editMode ? (
                    displayRows.map((row, i) => (
                      <EditableRow key={i} row={row} index={i} onChange={handleChange} onDelete={handleDelete} />
                    ))
                  ) : (
                    displayRows.map((row, i) => (
                      <ReadOnlyRow key={row.id ?? i} row={row} index={i} />
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
