import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.metrics import build_tss_dataframe, get_all_ride_files


# ---------- Helper Functions ----------

def classify_tsb(tsb):
    """Return freshness zone color and label for TSB (Training Stress Balance)."""
    if tsb > 10:
        return "Fresh", "#2ecc71"

# --- Weekly Summary ---
st.subheader("📅 Weekly Training Load Summary")

# Ensure numeric formatting and safe defaults
weekly = weekly.round({"tss": 1, "CTL": 1, "ATL": 1, "TSB": 1})

# ---- Filter Controls ----
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    selected_phase = st.selectbox(
        "🧩 Filter by Phase",
        options=["All"] + sorted(df["Phase"].unique()),
        index=0,
    )
with col2:
    selected_zone = st.selectbox(
        "💡 Filter by Freshness Zone",
        options=["All"] + sorted(weekly["Zone"].unique()),
        index=0,
    )
with col3:
    sort_by = st.selectbox("↕️ Sort by", ["Date", "TSS", "CTL", "ATL", "TSB"], index=0)

# Apply filters
filtered = weekly.copy()
if selected_phase != "All":
    filtered = filtered[filtered["week"].isin(df[df["Phase"] == selected_phase]["week"])]
if selected_zone != "All":
    filtered = filtered[filtered["Zone"] == selected_zone]

# Sort
sort_key = sort_by.lower() if sort_by != "Date" else "week"
filtered = filtered.sort_values(sort_key, ascending=False)

# ---- Summary Chips ----
st.markdown("#### 🧱 Training Phase Breakdown")
phase_counts = df["Phase"].value_counts().to_dict()
chip_line = "  ".join(
    [f"✅ **{k}:** {v} days" for k, v in phase_counts.items() if k not in ["Unclassified", "Insufficient Data"]]
)
st.markdown(chip_line or "_No classified phases yet._")

# ---- Highlight Row Function ----
def highlight_rows(row):
    color = row["Color"]
    return [f"background-color: {color}"] * len(row)

styled_table = (
    filtered.tail(15)
    .style.format({"tss": "{:.0f}", "CTL": "{:.1f}", "ATL": "{:.1f}", "TSB": "{:.1f}"})
    .apply(highlight_rows, axis=1)
)

st.dataframe(styled_table, use_container_width=True)
