import React from "react";

function StatusPill({ status }) {
  if (status === "FOUND") {
    return (
      <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 text-green-800 text-xs font-semibold border border-green-200">
        <span aria-hidden>✔</span> FOUND
      </span>
    );
  }
  if (status === "STANDARD") {
    return (
      <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-800 text-xs font-semibold border border-blue-200">
        <span aria-hidden>⚙</span> STANDARD
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-50 text-red-800 text-xs font-semibold border border-red-200">
      <span aria-hidden>✖</span> MISSING
    </span>
  );
}

export default function ResultsTable({
  results,
  allResults,
  loading,
  error,
  selectedItem,
  onRowClick,
  annotatedPdfUrl,
}) {
  return (
    <div className="flex flex-col min-h-0">
      <div className="px-4 pt-4 pb-3 flex items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">Validation Results</div>
          <div className="text-xs text-slate-600">
            {allResults?.length ? `${allResults.length} BOM items` : "Upload a PDF to begin"}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {annotatedPdfUrl ? (
            <a
              href={annotatedPdfUrl}
              download
              className="px-3 py-2 rounded-xl text-sm font-medium bg-slate-900 text-white hover:bg-slate-800 transition-colors"
            >
              Download PDF
            </a>
          ) : null}
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

      <div className="flex-1 min-h-0 overflow-auto px-1">
        {results?.length ? (
          <table className="min-w-full table-fixed text-sm">
            <thead className="sticky top-0 bg-white/80 backdrop-blur z-10 border-b">
              <tr className="text-left">
                <th className="px-3 py-2 font-semibold text-slate-700 w-14">Item</th>
                <th className="px-3 py-2 font-semibold text-slate-700 w-36">Part Number</th>
                <th className="px-3 py-2 font-semibold text-slate-700">Description</th>
                <th className="px-3 py-2 font-semibold text-slate-700 w-40">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.map((r) => {
                const isSelected = selectedItem === r.item;
                return (
                  <tr
                    key={`${r.item}_${r.part_number}`}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-yellow-50"
                        : "bg-white hover:bg-slate-50"
                    }`}
                    onClick={() => onRowClick?.(r.item)}
                  >
                    <td className="px-3 py-2 text-slate-900">{r.item}</td>
                    <td className="px-3 py-2 font-mono text-slate-900 break-all">
                      {r.part_number}
                    </td>
                    <td className="px-3 py-2 text-slate-700">
                      <span className="block break-words">{r.description}</span>
                    </td>
                    <td className="px-3 py-2">
                      <StatusPill status={r.status} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="p-6 text-sm text-slate-600 bg-white/60 rounded-2xl border border-dashed border-slate-200 m-3">
            No results to display.
          </div>
        )}
      </div>
    </div>
  );
}

