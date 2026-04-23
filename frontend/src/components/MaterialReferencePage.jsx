import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  getMaterialReference,
  uploadMaterialExcel,
  saveMaterialReference,
  resetMaterialReference,
} from "../api.js";

// ─── helpers ─────────────────────────────────────────────────────────────────

function listStr(arr) {
  if (Array.isArray(arr)) return arr.join(", ");
  return arr || "";
}

function toArray(val) {
  if (Array.isArray(val)) return val;
  if (typeof val === "string") return val.split(",").map((s) => s.trim()).filter(Boolean);
  return [];
}

// ─── badges ──────────────────────────────────────────────────────────────────

function Badge({ label, color }) {
  const palette = {
    green: "bg-emerald-50 text-emerald-700 border-emerald-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
    blue:  "bg-blue-50 text-blue-700 border-blue-200",
    slate: "bg-slate-100 text-slate-600 border-slate-200",
  };
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${palette[color] || palette.slate}`}>
      {label}
    </span>
  );
}

// ─── editable row ─────────────────────────────────────────────────────────────

function EditableRow({ row, index, onChange, onDelete }) {
  const inp = (key, placeholder = "") => (
    <input
      value={
        key === "materials" || key === "finish"
          ? listStr(row[key])
          : row[key] ?? ""
      }
      onChange={(e) => {
        const val = e.target.value;
        if (key === "materials" || key === "finish") {
          onChange(index, key, val.split(",").map((s) => s.trim()).filter(Boolean));
        } else {
          onChange(index, key, val);
        }
      }}
      placeholder={placeholder}
      className="w-full px-2 py-1.5 text-sm rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition"
    />
  );

  return (
    <tr className="group hover:bg-indigo-50/40 transition-colors border-b border-slate-100">
      <td className="px-4 py-2.5 text-xs text-slate-400 font-mono text-center w-10">{index + 1}</td>
      <td className="px-3 py-2">{inp("base_material", "e.g. Low carbon Steel")}</td>
      <td className="px-3 py-2 w-36">{inp("edm", "e.g. EDM000136")}</td>
      <td className="px-3 py-2">{inp("materials", "e.g. EN8, 80M40, SM45C")}</td>
      <td className="px-3 py-2">{inp("finish", "e.g. BLACKODISING")}</td>
      <td className="px-3 py-2 w-44">{inp("heat", "e.g. 60-70 or blank")}</td>
      <td className="px-3 py-2 text-center w-10">
        <button
          type="button"
          onClick={() => onDelete(index)}
          title="Delete row"
          className="w-7 h-7 rounded-full flex items-center justify-center text-red-400 hover:text-white hover:bg-red-500 text-lg leading-none transition-colors"
        >
          ×
        </button>
      </td>
    </tr>
  );
}

// ─── read-only row ────────────────────────────────────────────────────────────

function ReadOnlyRow({ row, index }) {
  const hasHeat = row.heat && row.heat.trim() !== "" && row.heat.toUpperCase() !== "NA";
  return (
    <tr className="hover:bg-slate-50 transition-colors border-b border-slate-100">
      <td className="px-4 py-3 text-xs text-slate-400 text-center font-mono w-10">{index + 1}</td>
      <td className="px-3 py-3 text-sm text-slate-700">{row.base_material || <span className="text-slate-300">—</span>}</td>
      <td className="px-3 py-3 font-mono text-sm text-indigo-700 font-semibold w-36">{row.edm}</td>
      <td className="px-3 py-3">
        <div className="flex flex-wrap gap-1">
          {toArray(row.materials).map((m, i) => <Badge key={i} label={m} color="blue" />)}
        </div>
      </td>
      <td className="px-3 py-3">
        <div className="flex flex-wrap gap-1">
          {toArray(row.finish).map((f, i) => <Badge key={i} label={f} color="slate" />)}
        </div>
      </td>
      <td className="px-3 py-3 w-44">
        {hasHeat
          ? <Badge label={row.heat} color="amber" />
          : <span className="text-slate-400 text-sm">NA</span>}
      </td>
    </tr>
  );
}

// ─── page ─────────────────────────────────────────────────────────────────────

export default function MaterialReferencePage() {
  const [rows, setRows]             = useState([]);
  const [editMode, setEditMode]     = useState(false);
  const [editRows, setEditRows]     = useState([]);
  const [loading, setLoading]       = useState(false);
  const [saving, setSaving]         = useState(false);
  const [uploading, setUploading]   = useState(false);
  const [error, setError]           = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const fileInputRef                = useRef(null);

  useEffect(() => { loadTable(); }, []);

  async function loadTable() {
    setLoading(true);
    setError("");
    try {
      const data = await getMaterialReference();
      setRows(data.rows || []);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to load reference table.");
    } finally {
      setLoading(false);
    }
  }

  function startEdit() {
    setEditRows(rows.map((r) => ({ ...r })));
    setEditMode(true);
    setSuccessMsg("");
    setError("");
  }

  function cancelEdit() {
    setEditMode(false);
    setEditRows([]);
  }

  function handleChange(index, key, value) {
    setEditRows((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [key]: value };
      return next;
    });
  }

  function handleDelete(index) {
    setEditRows((prev) => prev.filter((_, i) => i !== index));
  }

  function handleAddRow() {
    setEditRows((prev) => [
      ...prev,
      { edm: "", materials: [], finish: [], heat: "", base_material: "", use_notes: "" },
    ]);
  }

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccessMsg("");
    try {
      await saveMaterialReference(editRows);
      setRows(editRows);
      setEditMode(false);
      setSuccessMsg(`✔ Saved ${editRows.length} rows — future validations will use this table.`);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to save table.");
    } finally {
      setSaving(false);
    }
  }

  async function handleExcelUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    setSuccessMsg("");
    try {
      const data = await uploadMaterialExcel(file);
      const parsed = data.rows || [];
      setEditRows(parsed);
      setEditMode(true);
      setSuccessMsg(`✔ Parsed ${parsed.length} rows from "${file.name}". Review below and click Save & Apply.`);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to parse Excel file.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleReset() {
    if (!window.confirm("Reset to factory defaults? All custom changes will be lost.")) return;
    setLoading(true);
    setError("");
    setSuccessMsg("");
    try {
      const data = await resetMaterialReference();
      setRows(data.rows || []);
      setEditMode(false);
      setSuccessMsg("✔ Table reset to factory defaults.");
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to reset.");
    } finally {
      setLoading(false);
    }
  }

  const activeRows = editMode ? editRows : rows;
  const displayRows = activeRows.filter((r) => {
    const term = searchTerm.trim().toUpperCase();
    if (!term) return true;
    return (
      (r.edm || "").toUpperCase().includes(term) ||
      (r.base_material || "").toUpperCase().includes(term) ||
      listStr(r.materials).toUpperCase().includes(term)
    );
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/40 to-white flex flex-col">

      {/* ── top nav bar ── */}
      <header className="bg-white border-b border-slate-200 shadow-sm flex-shrink-0">
        <div className="max-w-screen-xl mx-auto px-6 py-4 flex items-center gap-4">
          {/* back button */}
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Validator
          </Link>

          <div className="h-5 w-px bg-slate-200" />

          <div className="flex-1">
            <h1 className="text-lg font-bold text-slate-900 leading-tight">Material Reference Table</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {editMode
                ? `Editing ${editRows.length} rows — click Save & Apply to use in validation`
                : `${rows.length} entries active · used for material validation`}
            </p>
          </div>

          {/* action buttons */}
          <div className="flex items-center gap-2">
            {!editMode ? (
              <>
                <label
                  className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold cursor-pointer transition shadow-sm
                    ${uploading ? "bg-indigo-300 text-white cursor-wait" : "bg-indigo-600 text-white hover:bg-indigo-700"}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4-4m0 0l4 4m-4-4v12" />
                  </svg>
                  {uploading ? "Parsing…" : "Upload Excel"}
                  <input ref={fileInputRef} type="file" accept=".xlsx,.xls" className="hidden" onChange={handleExcelUpload} disabled={uploading} />
                </label>

                <button
                  onClick={startEdit}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold bg-slate-800 text-white hover:bg-slate-900 shadow-sm transition"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Table
                </button>

                <button
                  onClick={handleReset}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold border border-slate-200 text-slate-600 bg-white hover:bg-slate-50 transition"
                >
                  ↺ Reset to Default
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleAddRow}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm transition"
                >
                  + Add Row
                </button>
                <button
                  onClick={cancelEdit}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold border border-slate-200 text-slate-600 bg-white hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-bold bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition disabled:opacity-60"
                >
                  {saving ? (
                    <>
                      <span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-indigo-300 border-t-white animate-spin" />
                      Saving…
                    </>
                  ) : "💾 Save & Apply"}
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ── status bar ── */}
      {(successMsg || error) && (
        <div className="max-w-screen-xl mx-auto w-full px-6 pt-4">
          {successMsg && (
            <div className="px-4 py-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium">
              {successMsg}
            </div>
          )}
          {error && (
            <div className="px-4 py-2.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm">
              {error}
            </div>
          )}
        </div>
      )}

      {/* ── edit mode warning ── */}
      {editMode && (
        <div className="max-w-screen-xl mx-auto w-full px-6 pt-3">
          <div className="px-4 py-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm">
            ⚠ You are in <strong>edit mode</strong>. Changes are not applied until you click <strong>Save &amp; Apply</strong>.
          </div>
        </div>
      )}

      {/* ── search + table ── */}
      <main className="flex-1 max-w-screen-xl mx-auto w-full px-6 py-5 flex flex-col gap-4">
        {/* toolbar */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-xs">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 111 11a6 6 0 0116 0z" />
            </svg>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search EDM, material, base…"
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <span className="text-sm text-slate-500 ml-1">
            {displayRows.length} {displayRows.length === 1 ? "row" : "rows"}
            {searchTerm ? " found" : ""}
          </span>
        </div>

        {/* table card */}
        <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          {loading ? (
            <div className="flex items-center justify-center gap-3 py-24 text-slate-500 text-sm">
              <span className="inline-block h-5 w-5 rounded-full border-2 border-slate-200 border-t-indigo-600 animate-spin" />
              Loading reference table…
            </div>
          ) : (
            <div className="overflow-auto flex-1">
              <table className="min-w-full table-auto text-sm">
                <thead className="sticky top-0 z-10 bg-slate-50 border-b-2 border-slate-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide w-10">#</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">Base Material</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide w-36">EDM Code</th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
                      Material Grades
                      {editMode && <span className="ml-1 normal-case font-normal text-slate-400">(comma-sep)</span>}
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
                      Surface Finish
                      {editMode && <span className="ml-1 normal-case font-normal text-slate-400">(comma-sep)</span>}
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide w-44">Heat Treatment</th>
                    {editMode && <th className="px-3 py-3 w-10" />}
                  </tr>
                </thead>
                <tbody>
                  {displayRows.length === 0 ? (
                    <tr>
                      <td
                        colSpan={editMode ? 7 : 6}
                        className="px-6 py-16 text-center text-slate-400 text-sm"
                      >
                        {searchTerm
                          ? "No rows match your search."
                          : "No rows found. Upload an Excel file or click Edit Table to add rows."}
                      </td>
                    </tr>
                  ) : editMode ? (
                    displayRows.map((row, i) => (
                      <EditableRow
                        key={i}
                        row={row}
                        index={i}
                        onChange={handleChange}
                        onDelete={handleDelete}
                      />
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
    </div>
  );
}
