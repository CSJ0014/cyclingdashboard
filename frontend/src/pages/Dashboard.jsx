import React, { useEffect, useState } from "react";
import { Typography, Stack, CircularProgress } from "@mui/material";
import { listRides, generateReport } from "../api";
import RideCard from "../components/RideCard";

export default function Dashboard() {
  const [rides, setRides] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRides()
      .then((data) => setRides(data))
      .catch((err) => {
        console.error(err);
        setRides([]);
      })
      .finally(() => setLoading(false));
  }, []);

  function handleAnalyze(path) {
    window.location.href = `/ride/${encodeURIComponent(path)}`;
  }

  async function handleDownload(path) {
    try {
      const blob = await generateReport(path);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${path.replace(".json", "")}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h4" fontWeight={700}>Cycling Coaching Dashboard</Typography>
      <Typography color="text.secondary">Recent rides</Typography>
      {loading && <CircularProgress />}
      {!loading && rides && rides.length === 0 && <Typography>No rides found</Typography>}
      <Stack spacing={2}>
        {rides && rides.map((r) => (
          <RideCard key={r.path || r.id} ride={r} onAnalyze={handleAnalyze} onDownload={handleDownload} />
        ))}
      </Stack>
    </Stack>
  );
}
