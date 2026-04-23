import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 5 * 60 * 1000,
  });

  return res.data;
}

// ── Material Reference Table ─────────────────────────────────────────────────

export async function getMaterialReference() {
  const res = await axios.get(`${API_BASE_URL}/material-reference`);
  return res.data; // { rows: [...] }
}

export async function uploadMaterialExcel(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_BASE_URL}/material-reference/upload-excel`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data; // { rows: [...] }
}

export async function saveMaterialReference(rows) {
  const res = await axios.post(`${API_BASE_URL}/material-reference/save`, { rows });
  return res.data; // { saved: N }
}

export async function resetMaterialReference() {
  const res = await axios.post(`${API_BASE_URL}/material-reference/reset`);
  return res.data; // { reset: true, rows: [...] }
}
