import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getRide, generateReport } from "../api";
import { Typography, Button, Stack, CircularProgress, Paper } from "@mui/material";

export default function RideAnalysis() {
  const { fname } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRide(fname)
      .then((d) => setData(d))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [fname]);

  async function downloadPdf() {
    try {
      const blob = await generateReport(fname);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fname.replace(".json", "")}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(e.message);
    }
  }

  if (loading) return <CircularProgress />;
  if (!data) return <Typography>Ride not found</Typography>;

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>{data.name || "Ride Analysis"}</Typography>
      <Typography color="text.secondary">{data.start_date_local || data.start_date || ""}</Typography>
      <Button variant="contained" onClick={downloadPdf}>Generate & Download PDF</Button>

      <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>Raw JSON</Typography>
        <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(data, null, 2)}</pre>
      </Paper>
    </Stack>
  );
}
