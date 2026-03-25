import React, { useEffect, useMemo, useRef, useState } from "react";

function StatusPill({ status }) {
  const cfg = (() => {
    if (status === "PASS") {
      return "inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 text-green-800 text-xs font-semibold border border-green-200";
    }
    if (status === "WARNING") {
      return "inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-50 text-yellow-800 text-xs font-semibold border border-yellow-200";
    }
    if (status === "FAIL") {
      return "inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-50 text-red-800 text-xs font-semibold border border-red-200";
    }
    return "inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-200";
  })();

  const label = status || "MISSING";
  const prefix =
    status === "PASS" ? "✔" : status === "WARNING" ? "!" : status === "FAIL" ? "✖" : "•";

  return (
    <span className={cfg}>
      <span aria-hidden>{prefix}</span> {label}
    </span>
  );
}

function worstStatus(statuses) {
  const has = (s) => statuses.includes(s);
  if (has("FAIL")) return "FAIL";
  if (has("WARNING")) return "WARNING";
  if (has("MISSING")) return "MISSING";
  return "PASS";
}

function formatExpected(expected) {
  if (Array.isArray(expected)) return expected.filter(Boolean).join(", ");
  if (expected == null) return "";
  return String(expected);
}

function statusBg(status) {
  if (status === "PASS") return "bg-green-50 border-green-200";
  if (status === "WARNING") return "bg-yellow-50 border-yellow-200";
  if (status === "FAIL") return "bg-red-50 border-red-200";
  return "bg-slate-50 border-slate-200";
}

function statusLeftBorder(status) {
  if (status === "PASS") return "border-l-green-500";
  if (status === "WARNING") return "border-l-yellow-500";
  if (status === "FAIL") return "border-l-red-500";
  return "border-l-slate-400";
}

function statusLeftBorderRow(status) {
  if (status === "PASS") return "border-l-green-400";
  if (status === "WARNING") return "border-l-yellow-400";
  if (status === "FAIL") return "border-l-red-400";
  return "border-l-slate-300";
}

function statusFieldText(status) {
  if (status === "PASS") return "text-green-900";
  if (status === "WARNING") return "text-yellow-900";
  if (status === "FAIL") return "text-red-900";
  return "text-slate-700";
}

export default function MaterialTable({
  materialResults,
  loading,
  error,
  backendMaterialFieldMissing,
}) {
  const [filterMode, setFilterMode] = useState("ALL"); // ALL | FAIL | WARNING | MISSING
  const [expandedParts, setExpandedParts] = useState(() => new Set());
  const [searchTerm, setSearchTerm] = useState("");
  const userAdjustedExpandedRef = useRef(false);

  const parts = materialResults || [];

  const fieldRowsByPart = useMemo(() => {
    return parts.map((part) => {
      const rows = [
        {
          field: "Material",
          expected: formatExpected(part?.material?.expected),
          actual: part?.material?.actual || "",
          status: part?.material?.status || "MISSING",
          key: "material",
        },
        {
          field: "Finish",
          expected: formatExpected(part?.finish?.expected),
          actual: part?.finish?.actual || "",
          status: part?.finish?.status || "MISSING",
          key: "finish",
        },
        {
          field: "Heat",
          expected: part?.heat?.expected || "NA",
          actual: part?.heat?.actual_range || part?.heat?.actual || "",
          status: part?.heat?.status || "MISSING",
          key: "heat",
        },
      ];

      const overall = worstStatus(rows.map((r) => r.status));
      return { part, rows, overall };
    });
  }, [parts]);

  const statusCounts = useMemo(() => {
    // Count by field (Material/Finish/Heat), not by part.
    const counts = { PASS: 0, WARNING: 0, FAIL: 0, MISSING: 0 };
    for (const pr of fieldRowsByPart) {
      for (const r of pr.rows) {
        const s = r.status || "MISSING";
        if (s in counts) counts[s] += 1;
      }
    }
    return counts;
  }, [fieldRowsByPart]);

  const visibleParts = useMemo(() => {
    const term = searchTerm.trim().toUpperCase();
    return fieldRowsByPart
      .filter(({ part }) => {
        if (!term) return true;
        const pn = (part?.part_number || "").toUpperCase();
        return pn.includes(term);
      })
      .filter(({ rows }) => {
        if (filterMode === "ALL") return true;
        return rows.some((r) => r.status === filterMode);
      })
      .map(({ part }) => part);
  }, [fieldRowsByPart, filterMode, searchTerm]);

  const visiblePartNumbers = useMemo(() => {
    return new Set((visibleParts || []).map((p) => p?.part_number).filter(Boolean));
  }, [visibleParts]);

  useEffect(() => {
    // When a new PDF loads, expand everything by default unless
    // the user already interacted with the expand/collapse controls.
    if (!parts.length) return;
    if (!userAdjustedExpandedRef.current) {
      setExpandedParts(() => new Set(parts.map((p) => p?.part_number).filter(Boolean)));
    }
  }, [parts]);

  const togglePart = (partNumber) => {
    userAdjustedExpandedRef.current = true;
    setExpandedParts((prev) => {
      const next = new Set(prev);
      if (next.has(partNumber)) next.delete(partNumber);
      else next.add(partNumber);
      return next;
    });
  };

  const expandAll = () => {
    userAdjustedExpandedRef.current = true;
    setExpandedParts(() => new Set(parts.map((p) => p?.part_number).filter(Boolean)));
  };

  const collapseAll = () => {
    userAdjustedExpandedRef.current = true;
    setExpandedParts(new Set());
  };

  return (
    <div className="flex flex-col min-h-0 h-full">
      <div className="px-4 pt-4 pb-3 flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">Material Validation</div>
          <div className="text-xs text-slate-600">
            {parts?.length ? `${parts.length} parts extracted` : "Upload a PDF to begin"}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-50 text-green-800 border border-green-200 text-xs">
              ✔ PASS ({statusCounts.PASS})
            </span>
            <span className="inline-flex items-center px-2 py-1 rounded-full bg-yellow-50 text-yellow-800 border border-yellow-200 text-xs">
              ! WARNING ({statusCounts.WARNING})
            </span>
            <span className="inline-flex items-center px-2 py-1 rounded-full bg-red-50 text-red-800 border border-red-200 text-xs">
              ✖ FAIL ({statusCounts.FAIL})
            </span>
            <span className="inline-flex items-center px-2 py-1 rounded-full bg-slate-50 text-slate-700 border border-slate-200 text-xs">
              • MISSING ({statusCounts.MISSING})
            </span>
          </div>

          <div className="inline-flex items-center rounded-xl border border-slate-200 bg-white/70 backdrop-blur p-1">
            <button
              type="button"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterMode === "ALL"
                  ? "bg-slate-900 text-white"
                  : "bg-transparent text-slate-700 hover:bg-slate-50"
              }`}
              onClick={() => setFilterMode("ALL")}
            >
              All
            </button>
            <button
              type="button"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterMode === "FAIL"
                  ? "bg-red-600 text-white"
                  : "bg-transparent text-slate-700 hover:bg-slate-50"
              }`}
              onClick={() => setFilterMode("FAIL")}
            >
              Fail
            </button>
            <button
              type="button"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterMode === "WARNING"
                  ? "bg-yellow-400 text-slate-900"
                  : "bg-transparent text-slate-700 hover:bg-slate-50"
              }`}
              onClick={() => setFilterMode("WARNING")}
            >
              Warning
            </button>
            <button
              type="button"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterMode === "MISSING"
                  ? "bg-slate-700 text-white"
                  : "bg-transparent text-slate-700 hover:bg-slate-50"
              }`}
              onClick={() => setFilterMode("MISSING")}
            >
              Missing
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="px-4 pb-3 text-sm text-slate-700 flex items-center gap-2">
          <span className="inline-block h-3 w-3 rounded-full border-2 border-slate-300 border-t-slate-900 animate-spin" />
          Processing PDF...
        </div>
      ) : null}

      {error ? (
        <div className="px-4 pb-3">
          <div className="text-sm text-red-800 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
            {error}
          </div>
        </div>
      ) : null}

      <div className="px-4 pb-3 flex flex-wrap items-center gap-2">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search part number..."
          className="flex-1 min-w-[220px] px-3 py-2 rounded-xl border border-slate-200 bg-white/80 text-slate-800 text-sm"
        />
        <button
          type="button"
          className="px-3 py-2 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-sm font-medium text-slate-700 disabled:opacity-50"
          onClick={expandAll}
          disabled={!parts.length}
        >
          Expand all
        </button>
        <button
          type="button"
          className="px-3 py-2 rounded-xl border border-slate-200 bg-white/80 hover:bg-white transition-colors text-sm font-medium text-slate-700 disabled:opacity-50"
          onClick={collapseAll}
          disabled={!expandedParts.size}
        >
          Collapse all
        </button>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto overflow-x-auto px-1 pb-2 max-h-[calc(100vh-280px)]">
        {visibleParts?.length ? (
          <table className="min-w-full table-fixed text-sm">
            <thead className="sticky top-0 bg-white/80 backdrop-blur z-10 border-b">
              <tr className="text-left">
                <th className="px-3 py-2 font-semibold text-slate-700 w-44">Part Number</th>
                <th className="px-3 py-2 font-semibold text-slate-700 w-36">Field</th>
                <th className="px-3 py-2 font-semibold text-slate-700">Expected</th>
                <th className="px-3 py-2 font-semibold text-slate-700">Actual</th>
                <th className="px-3 py-2 font-semibold text-slate-700 w-44">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {fieldRowsByPart
                .filter(({ part }) => visiblePartNumbers.has(part?.part_number))
                .map(({ part, rows, overall }) => {
                  const partNumber = part?.part_number;
                  const isExpanded = expandedParts.has(partNumber);
                  const visibleRows =
                    filterMode === "ALL" ? rows : rows.filter((r) => r.status === filterMode);
                  const parentTextClass = isExpanded ? "text-white" : "text-slate-900";
                  const descriptionTextClass = isExpanded ? "text-white/80" : "text-slate-600";

                  return (
                    <React.Fragment key={partNumber}>
                      <tr
                        className={`cursor-pointer transition-colors ${
                          isExpanded
                            ? `bg-slate-700 text-white border-l-4 ${statusLeftBorder(overall)}`
                            : "bg-white hover:bg-slate-50"
                        }`}
                        onClick={() => togglePart(partNumber)}
                      >
                        <td className={`px-3 py-2 font-mono break-all ${parentTextClass}`}>
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                              <span aria-hidden className="text-slate-500">
                                {isExpanded ? "▾" : "▸"}
                              </span>
                              {partNumber}
                            </div>
                            {part?.description ? (
                              <div className={`text-xs font-medium leading-tight ${descriptionTextClass}`}>
                                {part.description}
                              </div>
                            ) : null}
                          </div>
                        </td>
                        <td className="px-3 py-2 text-slate-700">
                          {visibleRows.length ? `${visibleRows.length} item(s)` : "No matches"}
                        </td>
                        <td className="px-3 py-2 text-slate-500">—</td>
                        <td className="px-3 py-2 text-slate-500">—</td>
                        <td className="px-3 py-2">
                          <StatusPill status={overall} />
                        </td>
                      </tr>

                      {isExpanded
                        ? visibleRows.map((r) => (
                            <tr
                              key={`${partNumber}_${r.key}`}
                            className={`bg-white border-l-4 ${statusLeftBorderRow(r.status)}`}
                            >
                              <td className="px-3 py-2 font-mono text-slate-900 break-all">
                                {partNumber}
                              </td>
                            <td className={`px-3 py-2 ${statusFieldText(r.status)} font-medium`}>{r.field}</td>
                              <td className="px-3 py-2 text-slate-700 break-words">
                                {r.expected || "—"}
                              </td>
                              <td className="px-3 py-2 text-slate-900 break-words">
                                {r.actual || "—"}
                              </td>
                              <td className="px-3 py-2">
                                <StatusPill status={r.status} />
                              </td>
                            </tr>
                          ))
                        : null}
                    </React.Fragment>
                  );
                })}
            </tbody>
          </table>
        ) : (
          <div className="p-6 text-sm text-slate-600 bg-white/60 rounded-2xl border border-dashed border-slate-200 m-3">
            {backendMaterialFieldMissing ? (
              <div>
                Backend did not return `material_results`.
                <div className="mt-2 text-xs text-slate-500">
                  This usually means the backend is running an older version or the frontend is pointing at the
                  wrong port. Restart the backend and confirm the API response includes <code>material_results</code>.
                </div>
              </div>
            ) : (
              "No material validation results to display."
            )}
          </div>
        )}
      </div>
    </div>
  );
}

