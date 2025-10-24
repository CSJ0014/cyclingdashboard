import React from "react";
import { Card, CardContent, Typography, Stack, Button } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import SearchIcon from "@mui/icons-material/Search";

export default function RideCard({ ride, onAnalyze, onDownload }) {
  const displayDate = ride.date ? new Date(ride.date).toLocaleString() : "Unknown date";
  return (
    <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <div>
            <Typography variant="h6">{ride.name || "Untitled Ride"}</Typography>
            <Typography variant="body2" color="text.secondary">{displayDate}</Typography>
          </div>
          <Stack direction="row" spacing={1}>
            <Button variant="outlined" startIcon={<SearchIcon />} onClick={() => onAnalyze(ride.path)}>Analyze</Button>
            <Button variant="contained" startIcon={<DownloadIcon />} onClick={() => onDownload(ride.path)}>PDF</Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
