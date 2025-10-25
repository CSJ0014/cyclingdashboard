// frontend/src/api.js
const API_BASE = "https://cyclingdashboard-7496mkxn3-csj0014s-projects.vercel.app/";

export async function listRides() {
  const res = await fetch(`${API_BASE}/rides/`);
  if (!res.ok) throw new Error("Failed to list rides");
  return res.json();
}

export async function getRide(fname) {
  const res = await fetch(`${API_BASE}/rides/${encodeURIComponent(fname)}`);
  if (!res.ok) throw new Error("Ride not found");
  return res.json();
}

export async function generateReport(fname) {
  const res = await fetch(`${API_BASE}/report/generate/${encodeURIComponent(fname)}`, {
    method: "POST",
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`PDF generation failed: ${txt}`);
  }
  const blob = await res.blob();
  return blob;
}
