import React from "react";
import { ThemeProvider, CssBaseline, Container } from "@mui/material";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import theme from "./theme";
import Dashboard from "./pages/Dashboard";
import RideAnalysis from "./pages/RideAnalysis";

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ride/:fname" element={<RideAnalysis />} />
          </Routes>
        </Container>
      </BrowserRouter>
    </ThemeProvider>
  );
}
