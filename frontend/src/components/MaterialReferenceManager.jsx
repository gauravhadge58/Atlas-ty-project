import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  getMaterialReference,
  uploadMaterialExcel,
  saveMaterialReference,
  resetMaterialReference,
} from "../api.js";

// ─── tiny helpers ────────────────────────────────────────────────────────────

function listStr(arr) {
  if (Array.isArray(arr)) return arr.join(", ");
  return arr || "";
}

function toArray(val) {
  if (Array.isArray(val)) return val;
  if (typeof val === "string") return val.split(",").map((s) => s.trim()).filter(Boolean);
  return [];
}

function Badge({ label, color }) {
  const palette = {
    green:  "bg-emerald-50 text-emerald-700 border-emerald-200",
    amber:  "bg-amber-50 text-amber-700 border-amber-200",
    blue:   "bg-blue-50 text-blue-700 border-blue-200",
    slate:  "bg-slate-100 text-slate-600 border-slate-200",
  };
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${palette[color] || palette.slate}`}>
      {label}
    </span>
  );
}

// ─── editable row component ───────────────────────────────────────────────────

function EditableRow({ row, index, onChange, onDelete }) {
  function field(key) {
    return (
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
        className="w-full px-2 py-1 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition"
        placeholder={key === "heat" ? "e.g. 60-70 or blank" : ""}
      />
    );
  }

  return (
    <tr className="group hover:bg-indigo-50/40 transition-colors">
      <td className="px-3 py-2 text-xs text-slate-400 font-mono text-center">{index + 1}</td>
      <td className="px-3 py-2">{field("base_material")}</td>
      <td className="px-3 py-2">{field("edm")}</td>
      <td className="px-3 py-2">
        <input
          value={listStr(row.materials)}
          onChange={(e) =>
            onChange(index, "materials", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))
          }
          className="w-full px-2 py-1 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition"
          placeholder="e.g. EN8, 80M40"
        />
      </td>
      <td className="px-3 py-2">
        <input
          value={listStr(row.finish)}
          onChange={(e) =>
            onChange(index, "finish", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))
          }
          className="w-full px-2 py-1 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 transition"
          placeholder="e.g. BLACKODISING"
        />
      </td>
      <td className="px-3 py-2">{field("heat")}</td>
      <td className="px-3 py-2 text-center">
        <button
          type="button"
          onClick={() => onDelete(index)}
          className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-600 text-lg leading-none"
          title="Delete row"
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
    <tr className="hover:bg-slate-50/80 transition-colors">
      <td className="px-3 py-2 text-xs text-slate-400 text-center font-mono">{index + 1}</td>
      <td className="px-3 py-2 text-sm text-slate-700">{row.base_material || "—"}</td>
      <td className="px-3 py-2 font-mono text-xs text-indigo-700 font-semibold">{row.edm}</td>
      <td className="px-3 py-2">
        <div className="flex flex-wrap gap-1">
          {toArray(row.materials).map((m, i) => (
            <Badge key={i} label={m} color="blue" />
          ))}
        </div>
      </td>
      <td className="px-3 py-2">
        <div className="flex flex-wrap gap-1">
          {toArray(row.finish).map((f, i) => (
            <Badge key={i} label={f} color="slate" />
          ))}
        </div>
      </td>
      <td className="px-3 py-2 text-xs text-slate-600">
        {hasHeat ? <Badge label={row.heat} color="amber" /> : <span className="text-slate-400">NA</span>}
      </td>
    </tr>
  );
}

// ─── main component ───────────────────────────────────────────────────────────

export default function MaterialReferenceManager({ onClose }) {
  const [rows, setRows]               = useState([]);
  const [editMode, setEditMode]       = useState(false);
  const [editRows, setEditRows]       = useState([]);
  const [loading, setLoading]         = useState(false);
  const [saving, setSaving]           = useState(false);
  const [uploading, setUploading]     = useState(false);
  const [error, setError]             = useState("");
  const [successMsg, setSuccessMsg]   = useState("");
  const [searchTerm, setSearchTerm]   = useState("");
  const fileInputRef                  = useRef(null);

  // ── load current table on mount ────────────────────────────────────────────
  useEffect(() => {
    loadTable();
  }, []);

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

  // ── enter edit mode ────────────────────────────────────────────────────────
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

  // ── cell change ────────────────────────────────────────────────────────────
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

  // ── save ───────────────────────────────────────────────────────────────────
  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccessMsg("");
    try {
      await saveMaterialReference(editRows);
      setRows(editRows);
      setEditMode(false);
      setSuccessMsg(`✔ Saved ${editRows.length} rows. Future validations will use this table.`);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to save table.");
    } finally {
      setSaving(false);
    }
  }

  // ── upload excel ───────────────────────────────────────────────────────────
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
      setSuccessMsg(`✔ Parsed ${parsed.length} rows from "${file.name}". Review and click Save.`);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to parse Excel file.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  // ── reset ──────────────────────────────────────────────────────────────────
  async function handleReset() {
    if (
      !window.confirm(
        "Reset the material reference table to factory defaults?\nAll custom edits will be lost."
      )
    )
      return;
    setLoading(true);
    setError("");
    setSuccessMsg("");
    try {
      const data = await resetMaterialReference();
      setRows(data.rows || []);
      setEditMode(false);
      setSuccessMsg("✔ Table reset to factory defaults.");
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to reset table.");
    } finally {
      setLoading(false);
    }
  }

  // ── search filter ──────────────────────────────────────────────────────────
  const displayRows = (editMode ? editRows : rows).filter((r) => {
    const term = searchTerm.trim().toUpperCase();
    if (!term) return true;
    return (
      (r.edm || "").toUpperCase().includes(term) ||
      (r.base_material || "").toUpperCase().includes(term) ||
      listStr(r.materials).toUpperCase().includes(term)
    );
  });

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.55)", backdropFilter: "blur(4px)" }}
    >
      <div
        className="relative bg-white rounded-2xl shadow-2xl w-full flex flex-col overflow-hidden"
        style={{ maxWidth: 1050, maxHeight: "92vh" }}
      >
        {/* ── header ── */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-indigo-600 to-indigo-500">
          <div>
            <div className="text-white font-bold text-lg tracking-tight">Material Reference Table</div>
            <div className="text-indigo-200 text-xs mt-0.5">
              {editMode
                ? `Editing ${editRows.length} rows — save to apply for validation`
                : `${rows.length} entries active`}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-indigo-200 hover:text-white transition text-2xl leading-none px-2"
            title="Close"
          >
            ×
          </button>
        </div>

        {/* ── toolbar ── */}
        <div className="flex flex-wrap items-center gap-2 px-6 py-3 border-b border-slate-100 bg-slate-50/60">
          {/* search */}
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search EDM / material…"
            className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-400 w-52"
          />

          <div className="flex-1" />

          {!editMode ? (
            <>
              {/* Upload Excel */}
              <label
                className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-sm font-semibold cursor-pointer transition
                  ${uploading
                    ? "bg-indigo-200 text-indigo-400 cursor-wait"
                    : "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm"}`}
                title="Upload an .xlsx material sheet"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4-4m0 0l4 4m-4-4v12" />
                </svg>
                {uploading ? "Parsing…" : "Upload Excel"}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  className="hidden"
                  onChange={handleExcelUpload}
                  disabled={uploading}
                />
              </label>

              {/* Edit button */}
              <button
                onClick={startEdit}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-sm font-semibold bg-slate-800 text-white hover:bg-slate-900 shadow-sm transition"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Table
              </button>

              {/* Reset */}
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-sm font-semibold border border-slate-200 text-slate-600 bg-white hover:bg-slate-50 transition"
                title="Reset to factory defaults"
              >
                ↺ Reset to Default
              </button>
            </>
          ) : (
            <>
              {/* Add row */}
              <button
                onClick={handleAddRow}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-sm font-semibold bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm transition"
              >
                + Add Row
              </button>

              {/* Cancel */}
              <button
                onClick={cancelEdit}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-sm font-semibold border border-slate-200 text-slate-600 bg-white hover:bg-slate-50 transition"
              >
                Cancel
              </button>

              {/* Save */}
              <button
                onClick={handleSave}
                disabled={saving}
                className="inline-flex items-center gap-1.5 px-5 py-1.5 rounded-xl text-sm font-bold bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition disabled:opacity-60 disabled:cursor-wait"
              >
                {saving ? (
                  <>
                    <span className="inline-block h-3 w-3 rounded-full border-2 border-indigo-300 border-t-white animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>💾 Save & Apply</>
                )}
              </button>
            </>
          )}
        </div>

        {/* ── status messages ── */}
        {successMsg && (
          <div className="mx-6 mt-3 px-4 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium">
            {successMsg}
          </div>
        )}
        {error && (
          <div className="mx-6 mt-3 px-4 py-2 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm">
            {error}
          </div>
        )}

        {/* ── table ── */}
        <div className="flex-1 min-h-0 overflow-auto px-2 pb-4">
          {loading ? (
            <div className="flex items-center justify-center gap-3 py-20 text-slate-500 text-sm">
              <span className="inline-block h-5 w-5 rounded-full border-2 border-slate-300 border-t-indigo-600 animate-spin" />
              Loading reference table…
            </div>
          ) : (
            <table className="min-w-full table-auto text-sm mt-3">
              <thead className="sticky top-0 bg-white/90 backdrop-blur z-10">
                <tr className="border-b-2 border-slate-100">
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-400 w-10">#</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-600 w-48">Base Material</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-600 w-36">EDM Code</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-600">
                    Material Grades
                    {editMode && <span className="ml-1 text-slate-400 font-normal">(comma-sep)</span>}
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-600">
                    Surface Finish
                    {editMode && <span className="ml-1 text-slate-400 font-normal">(comma-sep)</span>}
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-600 w-36">Heat Treatment</th>
                  {editMode && <th className="px-3 py-2 w-8" />}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {displayRows.length === 0 ? (
                  <tr>
                    <td
                      colSpan={editMode ? 7 : 6}
                      className="px-4 py-12 text-center text-slate-400 text-sm"
                    >
                      {searchTerm ? "No rows match your search." : "No rows in the table yet."}
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
          )}
        </div>

        {/* ── footer hint ── */}
        {editMode && !loading && (
          <div className="px-6 py-2 border-t border-slate-100 bg-amber-50/60 text-xs text-amber-700">
            ⚠ Changes are <strong>not applied</strong> until you click <strong>Save &amp; Apply</strong>. After saving, all new PDF validations will use this table.
          </div>
        )}
      </div>
    </div>
  );
}
