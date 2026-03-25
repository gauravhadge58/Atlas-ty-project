import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 5 * 60 * 1000,
  });

  return res.data;
}

