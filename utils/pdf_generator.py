# ==============================================================
# 📄 PDF REPORT GENERATOR — for Cycling Dashboard
# Generates a ride summary PDF using ReportLab
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
)
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
import os


# --------------------------------------------------------------
# 🧩 MAIN REPORT FUNCTION
# --------------------------------------------------------------

def generate_ride_report(df: pd.DataFrame, metrics: dict, ride_name: str) -> str:
    """Generate a PDF ride report and return the file path."""

    # Create temporary folder
    os.makedirs("ride_reports", exist_ok=True)
    safe_name = ride_name.replace(".json", "").replace(" ", "_")
    pdf_path = os.path.join("ride_reports", f"{safe_name}_report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Title & layout
    elements = []
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#6200EE"),  # MD3 purple
        fontSize=20,
        spaceAfter=12,
    )
    elements.append(Paragraph(f"🚴 Ride Report — {ride_name}", title_style))
    elements.append(Spacer(1, 12))

    # ----------------------------------------------------------
    # 📊 METRICS TABLE
    # ----------------------------------------------------------
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE7F6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#311B92")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 18))

    # ----------------------------------------------------------
    # 📈 CHART — Power / HR / Speed
    # ----------------------------------------------------------
    plot_cols = [c for c in ["watts", "heartrate", "speed_mph"] if c in df.columns]

    if plot_cols:
        plt.figure(figsize=(6, 3))
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
        elements.append(Spacer(1, 12))

    # ----------------------------------------------------------
    # ❤️ HEART RATE ZONES (if available)
    # ----------------------------------------------------------
    hr_zones = metrics.get("hr_zone_dist", {})
    if hr_zones:
        zone_data = [["Zone", "Time %"]]
        for z, pct in hr_zones.items():
            zone_data.append([z, f"{pct:.1f}%"])

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
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Heart Rate Zone Distribution", styles["Heading3"]))
        elements.append(zone_table)

    # ----------------------------------------------------------
    # 🧾 BUILD PDF
    # ----------------------------------------------------------
    doc.build(elements)
    return pdf_path
