# ==============================================================
# 📄 PDF REPORT GENERATOR — Enhanced Athlete Progress Report
# Generates single-ride + multi-ride metrics summary (2 pages)
# ==============================================================

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
import os
from datetime import datetime, timedelta


# --------------------------------------------------------------
# 🧩 MAIN REPORT FUNCTION
# --------------------------------------------------------------

def generate_ride_report(df: pd.DataFrame, metrics: dict, ride_name: str):
    """Generate a PDF ride report and athlete progress summary."""

    # --- Paths ---
    os.makedirs("ride_reports", exist_ok=True)
    safe_name = ride_name.replace(".json", "").replace(" ", "_")
    pdf_path = os.path.join("ride_reports", f"{safe_name}_report.pdf")

    # --- Layout setup ---
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # --- Colors ---
    primary = colors.HexColor("#6200EE")
    secondary_bg = colors.HexColor("#EDE7F6")
    accent = colors.HexColor("#311B92")

    # ----------------------------------------------------------
    # 🚴 PAGE 1 — INDIVIDUAL RIDE SUMMARY
    # ----------------------------------------------------------
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        textColor=primary,
        fontSize=20,
        spaceAfter=12,
    )
    elements.append(Paragraph(f"🚴 Ride Report — {ride_name}", title_style))
    elements.append(Spacer(1, 12))

    # --- Metrics Table ---
    metric_data = [
        ["Metric", "Value"],
        ["Distance (mi)", f"{metrics.get('distance_mi', 0):.1f}"],
        ["Duration (min)", f"{metrics.get('duration_min', 0):.1f}"],
        ["Avg Speed (mph)", f"{metrics.get('avg_speed', 0):.1f}"],
        ["Avg Power (W)", f"{metrics.get('avg_power', 0):.0f}"],
        ["Normalized Power (W)", f"{metrics.get('np_power', 0):.0f}"],
        ["Intensity Factor", f"{metrics.get('intensity_factor', 0):.2f}"],
        ["Training Stress Score", f"{metrics.get('tss', 0):.0f}"],
        ["Avg Heart Rate", f"{metrics.get('avg_hr', 0):.0f} bpm"],
        ["Max Heart Rate", f"{metrics.get('max_hr', 0):.0f} bpm"],
    ]

    table = Table(metric_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), secondary_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), accent),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 16))

    # --- Power / HR / Speed Chart ---
    plot_cols = [c for c in ["watts", "heartrate", "speed_mph"] if c in df.columns]
    if plot_cols:
        plt.figure(figsize=(6.2, 3))
        for col in plot_cols:
            plt.plot(df["time_s"], df[col], label=col.capitalize())
        plt.xlabel("Time (s)")
        plt.ylabel("Value")
        plt.title("Ride Data")
        plt.legend()
        plt.tight_layout()

        chart_path = tempfile.mktemp(suffix=".png")
        plt.savefig(chart_path, dpi=150)
        plt.close()

        elements.append(Image(chart_path, width=6.5 * inch, height=3 * inch))
        elements.append(Spacer(1, 16))

    # --- HR Zones ---
    hr_zones = metrics.get("hr_zone_dist", {})
    if hr_zones:
        zone_data = [["Zone", "Time %"]] + [[z, f"{pct:.1f}%"] for z, pct in hr_zones.items()]
        zone_table = Table(zone_data, hAlign="LEFT")
        zone_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3E5F5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#4A148C")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        elements.append(Paragraph("Heart Rate Zone Distribution", styles["Heading3"]))
        elements.append(zone_table)

    # ----------------------------------------------------------
    # 📈 PAGE 2 — ATHLETE PROGRESS REPORT
    # ----------------------------------------------------------
    elements.append(PageBreak())
    elements.append(Paragraph("📊 Athlete Progress Summary", title_style))
    elements.append(Spacer(1, 12))

    # --- Load all previous ride summaries ---
    all_data = _load_all_rides_for_summary("ride_data/raw")
    if all_data.empty:
        elements.append(Paragraph("No additional rides found for summary.", styles["Normal"]))
        doc.build(elements)
        return pdf_path

    # --- Compute trends (weekly TSS, avg power, volume) ---
    weekly = (
        all_data.groupby(pd.Grouper(key="date", freq="W"))[
            ["distance_km", "avg_power", "tss"]
        ]
        .mean()
        .reset_index()
    )

    # --- Trend Charts ---
    if not weekly.empty:
        plt.figure(figsize=(6, 3))
        plt.plot(weekly["date"], weekly["distance_km"], label="Weekly Distance (km)")
        plt.plot(weekly["date"], weekly["tss"], label="Weekly TSS")
        plt.title("Training Volume & Stress Trends")
        plt.xlabel("Week")
        plt.legend()
        plt.tight_layout()
        chart2_path = tempfile.mktemp(suffix=".png")
        plt.savefig(chart2_path, dpi=150)
        plt.close()
        elements.append(Image(chart2_path, width=6.5 * inch, height=3 * inch))
        elements.append(Spacer(1, 16))

    # --- Summary Table ---
    avg_power = all_data["avg_power"].mean()
    avg_tss = all_data["tss"].mean()
    total_dist = all_data["distance_km"].sum()
    total_rides = len(all_data)

    summary_data = [
        ["Summary Metric", "Value"],
        ["Total Rides", total_rides],
        ["Total Distance (km)", f"{total_dist:.1f}"],
        ["Average Power (W)", f"{avg_power:.1f}"],
        ["Average TSS", f"{avg_tss:.1f}"],
    ]
    summary_table = Table(summary_data, hAlign="LEFT")
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), secondary_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), accent),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(summary_table)

    # ----------------------------------------------------------
    # 🧾 BUILD PDF
    # ----------------------------------------------------------
    doc.build(elements)
    return pdf_path


# --------------------------------------------------------------
# 🗂️ HELPER — Load All Rides for Summary
# --------------------------------------------------------------

def _load_all_rides_for_summary(raw_dir: str) -> pd.DataFrame:
    """Aggregate key stats from all saved ride JSONs, using FTP from Streamlit session if available."""
    import json
    import pandas as pd
    import os
    import streamlit as st

    # --- Get FTP from settings tab (fallback 250W) ---
    ftp = st.session_state.get("ftp", 250.0)

    if not os.path.exists(raw_dir):
        return pd.DataFrame(columns=["date", "distance_km", "avg_power", "tss"])

    records = []
    for fname in os.listdir(raw_dir):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(raw_dir, fname), "r") as f:
                data = json.load(f)

            # ---- Parse Date ----
            date_val = data.get("start_date_local") or data.get("start_date")
            if not date_val:
                continue
            date = pd.to_datetime(date_val, errors="coerce")
            if pd.isna(date):
                continue

            # ---- Distance ----
            dist = data.get("distance", 0)
            if isinstance(dist, dict):
                dist = dist.get("data", [0])[-1] if "data" in dist else 0

            # ---- Duration ----
            moving_time = float(data.get("moving_time", 0))
            hours = moving_time / 3600 if moving_time else 0

            # ---- Power Metrics ----
            avg_power = data.get("average_watts", 0) or 0
            np_power = data.get("np_power", avg_power)
            intensity_factor = data.get("intensity_factor")

            # ---- Compute / Estimate TSS ----
            tss = data.get("tss", None)
            if not tss or tss == 0:
                if not intensity_factor and np_power and ftp:
                    intensity_factor = np_power / ftp
                if hours > 0 and intensity_factor:
                    tss = (hours * (intensity_factor ** 2) * 100)
                elif hours > 0 and avg_power and ftp:
                    tss = (hours * ((avg_power / ftp) ** 2) * 100)
                else:
                    tss = 0

            records.append({
                "date": date,
                "distance_km": dist / 1000 if dist else 0,
                "avg_power": avg_power,
                "tss": tss,
            })

        except Exception:
            continue

    # ---- Always Return a Valid DF ----
    if not records:
        return pd.DataFrame(columns=["date", "distance_km", "avg_power", "tss"])

    df = pd.DataFrame(records)
    if "date" not in df.columns:
        df["date"] = pd.NaT

    df = df.dropna(subset=["date"], how="all")
    df = df.sort_values("date").reset_index(drop=True)
    return df
