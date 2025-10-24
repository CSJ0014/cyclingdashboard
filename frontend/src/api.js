const API_BASE = "https://cyclingdashboard-backend.onrender.com/api";

export async function listRides() {
  const res = await fetch(`${API_BASE}/api/rides/`);
  if (!res.ok) throw new Error("Failed to list rides");
  return res.json();
}

export async function getRide(fname) {
  const res = await fetch(`${API_BASE}/api/rides/${encodeURIComponent(fname)}`);
  if (!res.ok) throw new Error("Ride not found");
  return res.json();
}

export async function generateReport(fname) {
  const res = await fetch(`${API_BASE}/api/report/generate/${encodeURIComponent(fname)}`, {
    method: "POST",
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`PDF generation failed: ${txt}`);
  }
  const blob = await res.blob();
  return blob;
}

import axios from "axios";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});
