import React, { useMemo, useState, useEffect } from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import PdfViewer from "./components/PdfViewer.jsx";
import ResultsTable from "./components/ResultsTable.jsx";
import MaterialTable from "./components/MaterialTable.jsx";
import MaterialReferencePage from "./components/MaterialReferencePage.jsx";
import { uploadPdf } from "./api.js";

// ── Theme hook ─────────────────────────────────────────────────────────────
function useTheme() {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem("atlas-theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("atlas-theme", theme);
  }, [theme]);
  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));
  return { theme, toggleTheme };
}

// ── Icons ──────────────────────────────────────────────────────────────────
function IconSun() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}
function IconMoon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
    </svg>
  );
}
function IconLogo() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
  );
}
function IconHome() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  );
}
function IconClipboard() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
    </svg>
  );
}

function StatusDot({ color }) {
  return <span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", background: color, flexShrink: 0 }} />;
}

// ── Shared top nav (used on all routes via Layout) ─────────────────────────
function AppNav() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header style={{
      background: "var(--color-surface)",
      borderBottom: "1px solid var(--color-border)",
      height: 64,
      display: "flex",
      alignItems: "center",
      padding: "0 24px",
      gap: 0,
      flexShrink: 0,
      position: "relative",
      zIndex: 20,
    }}>

      {/* ── Brand (left) ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 28 }}>
        <img
          src="/logo.png"
          alt="DrawingSelfCheck logo"
          style={{ width: 36, height: 36, objectFit: "contain", flexShrink: 0 }}
        />
        <div>
          <div style={{ fontWeight: 600, fontSize: "var(--text-base)", color: "var(--color-text-primary)", lineHeight: 1.15, letterSpacing: "-0.02em" }}>
            DrawingSelfCheck
          </div>
          <div style={{ fontSize: 10, color: "var(--color-text-tertiary)", lineHeight: 1.2, letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 500, marginTop: 1 }}>
            Atlas Copco
          </div>
        </div>
      </div>

      {/* ── Nav links (centre-left) ── */}
      <nav style={{ display: "flex", alignItems: "center", gap: 2, flex: 1 }} aria-label="Main navigation">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-link${isActive ? " nav-link--active" : ""}`}
        >
          <IconHome />
          Validator
        </NavLink>

        <NavLink
          to="/reference-table"
          className={({ isActive }) => `nav-link${isActive ? " nav-link--active" : ""}`}
        >
          <IconClipboard />
          Reference Table
        </NavLink>
      </nav>

      {/* ── Utilities (right) ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        {/* Divider before utility actions */}
        <div style={{ width: 1, height: 20, background: "var(--color-border)", marginRight: 4 }} />

        <button
          id="theme-toggle"
          className="btn btn-ghost btn-sm"
          onClick={toggleTheme}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          style={{ width: 32, padding: 0 }}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          {theme === "dark" ? <IconSun /> : <IconMoon />}
        </button>
      </div>
    </header>
  );
}

// ── Validator page ─────────────────────────────────────────────────────────
function ValidatorPage({
  loading, setLoading,
  error, setError,
  annotatedPdfUrl, setAnnotatedPdfUrl,
  results, setResults,
  materialResults, setMaterialResults,
  backendMaterialFieldMissing, setBackendMaterialFieldMissing,
  bomAnnotationPositions, setBomAnnotationPositions,
  uploadedFileName, setUploadedFileName
}) {
  const [missingOnly, setMissingOnly]   = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [activeTab, setActiveTab]       = useState("BOM");

  const yByItem = useMemo(() => {
    const map = new Map();
    for (const p of bomAnnotationPositions || []) map.set(p.item, p.y_pdf);
    return map;
  }, [bomAnnotationPositions]);

  const scrollTarget = useMemo(() => {
    if (selectedItem == null) return null;
    const y_pdf = yByItem.get(selectedItem);
    if (typeof y_pdf !== "number") return null;
    return { page: 1, y_pdf };
  }, [selectedItem, yByItem]);

  async function handleUpload(file) {
    setError(""); setLoading(true);
    setResults([]); setMaterialResults([]);
    setBackendMaterialFieldMissing(false);
    setBomAnnotationPositions([]); setSelectedItem(null);
    setAnnotatedPdfUrl(""); setUploadedFileName(file?.name || "");
    try {
      const data = await uploadPdf(file);
      setAnnotatedPdfUrl(data.annotated_pdf_url);
      setResults(data.results || []);
      setBomAnnotationPositions(data.bom_annotation_positions || []);
      const hasField = Object.prototype.hasOwnProperty.call(data, "material_results");
      setBackendMaterialFieldMissing(!hasField);
      setMaterialResults(Array.isArray(data.material_results) ? data.material_results : []);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setError("");
    setResults([]);
    setMaterialResults([]);
    setBackendMaterialFieldMissing(false);
    setBomAnnotationPositions([]);
    setSelectedItem(null);
    setAnnotatedPdfUrl("");
    setUploadedFileName("");
  }

  const filteredResults = useMemo(() => {
    if (!missingOnly) return results;
    return (results || []).filter((r) => r.status === "MISSING");
  }, [results, missingOnly]);

  const counts = useMemo(() => {
    const c = { FOUND: 0, STANDARD: 0, MISSING: 0 };
    for (const r of results || []) { if (r?.status in c) c[r.status] += 1; }
    return c;
  }, [results]);

  return (
    <div style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, padding: 16 }}>

      {/* PDF viewer panel */}
      <section className="card" style={{ minHeight: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        <PdfViewer 
          annotatedPdfUrl={annotatedPdfUrl} 
          loading={loading} 
          scrollTarget={scrollTarget} 
          onUpload={handleUpload}
          currentFileName={uploadedFileName}
          onReset={handleReset}
        />
      </section>

      {/* Results panel */}
      <section className="card" style={{ minHeight: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {/* Tabs + legend row */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 16px",
          borderBottom: "1px solid var(--color-border)",
          gap: 8,
        }}>
          <div className="tab-bar" style={{ borderBottom: "none", flex: 1 }}>
            <button
              id="tab-bom"
              className={`tab-btn ${activeTab === "BOM" ? "tab-btn--active" : ""}`}
              onClick={() => { setActiveTab("BOM"); setSelectedItem(null); }}
            >
              BOM Validation
            </button>
            <button
              id="tab-material"
              className={`tab-btn ${activeTab === "MATERIAL" ? "tab-btn--active" : ""}`}
              onClick={() => { setActiveTab("MATERIAL"); setSelectedItem(null); }}
            >
              Material Validation
            </button>
          </div>

          {/* Legend + filter — only on BOM tab when results exist */}
          {activeTab === "BOM" && results.length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 11, color: "var(--color-text-secondary)" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}><StatusDot color="var(--color-success)" />FOUND {counts.FOUND}</span>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}><StatusDot color="var(--color-info)" />STD {counts.STANDARD}</span>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}><StatusDot color="var(--color-error)" />MISS {counts.MISSING}</span>
              </div>
              <div style={{ width: 1, height: 16, background: "var(--color-border)" }} />
              <label style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "var(--color-text-secondary)", cursor: "pointer", userSelect: "none", whiteSpace: "nowrap" }}>
                <input
                  id="missing-only-toggle"
                  type="checkbox"
                  checked={missingOnly}
                  onChange={(e) => setMissingOnly(e.target.checked)}
                  style={{ accentColor: "var(--color-brand)", width: 13, height: 13 }}
                />
                Missing only
              </label>
            </div>
          )}
        </div>

        {/* Tab content */}
        <div style={{ flex: 1, minHeight: 0 }}>
          {activeTab === "BOM" ? (
            <ResultsTable
              results={filteredResults}
              allResults={results}
              loading={loading}
              error={error}
              selectedItem={selectedItem}
              onRowClick={(item) => setSelectedItem(item)}
              annotatedPdfUrl={annotatedPdfUrl}
            />
          ) : (
            <MaterialTable
              materialResults={materialResults}
              loading={loading}
              error={error}
              backendMaterialFieldMissing={backendMaterialFieldMissing}
            />
          )}
        </div>
      </section>
    </div>
  );
}

// ── Root with shared layout ────────────────────────────────────────────────
export default function App() {
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [annotatedPdfUrl, setAnnotatedPdfUrl]                   = useState("");
  const [results, setResults]                                   = useState([]);
  const [materialResults, setMaterialResults]                   = useState([]);
  const [backendMaterialFieldMissing, setBackendMaterialFieldMissing] = useState(false);
  const [bomAnnotationPositions, setBomAnnotationPositions]     = useState([]);
  const [uploadedFileName, setUploadedFileName]                 = useState("");

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--color-bg)" }}>
      <AppNav />
      <Routes>
        <Route path="/" element={
          <ValidatorPage 
            loading={loading} setLoading={setLoading}
            error={error} setError={setError}
            annotatedPdfUrl={annotatedPdfUrl} setAnnotatedPdfUrl={setAnnotatedPdfUrl}
            results={results} setResults={setResults}
            materialResults={materialResults} setMaterialResults={setMaterialResults}
            backendMaterialFieldMissing={backendMaterialFieldMissing} setBackendMaterialFieldMissing={setBackendMaterialFieldMissing}
            bomAnnotationPositions={bomAnnotationPositions} setBomAnnotationPositions={setBomAnnotationPositions}
            uploadedFileName={uploadedFileName} setUploadedFileName={setUploadedFileName}
          />
        } />
        <Route path="/reference-table" element={<MaterialReferencePage />} />
      </Routes>
    </div>
  );
}
