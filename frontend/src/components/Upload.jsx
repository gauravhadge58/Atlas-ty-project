import React, { useCallback, useMemo, useRef, useState } from "react";

export default function Upload({ onUpload, loading, currentFileName }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const hint = useMemo(() => {
    if (loading) return "Processing...";
    return "Drag & drop a PDF here, or click to select.";
  }, [loading]);

  const onPickFile = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const onFileSelected = useCallback(
    (e) => {
      const file = e.target.files?.[0];
      if (file && file.type === "application/pdf") onUpload(file);
    },
    [onUpload],
  );

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={onFileSelected}
        disabled={loading}
      />

      <div
        className={`border-2 border-dashed rounded-2xl p-4 text-center cursor-pointer transition-colors ${
          loading
            ? "opacity-70 cursor-not-allowed"
            : dragActive
              ? "border-indigo-400 bg-indigo-50"
              : "border-slate-200 bg-white/70 hover:bg-white"
        }`}
        onClick={onPickFile}
        onDragOver={(e) => {
          e.preventDefault();
          if (!loading) setDragActive(true);
        }}
        onDragEnter={(e) => {
          e.preventDefault();
          if (!loading) setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          if (loading) return;
          setDragActive(false);
          const file = e.dataTransfer.files?.[0];
          if (file && file.type === "application/pdf") onUpload(file);
        }}
      >
        <div className="flex items-center justify-center gap-3">
          <div
            className={`h-10 w-10 rounded-xl flex items-center justify-center border ${
              dragActive ? "border-indigo-300 bg-indigo-100" : "border-slate-200 bg-slate-50"
            }`}
            aria-hidden
          >
            <span className="text-xs font-bold text-slate-700">PDF</span>
          </div>
          <div className="text-sm text-slate-700">{hint}</div>
        </div>

        {currentFileName ? (
          <div className="mt-3 text-xs text-slate-600 break-all">
            Loaded: {currentFileName}
          </div>
        ) : null}
      </div>
    </div>
  );
}

