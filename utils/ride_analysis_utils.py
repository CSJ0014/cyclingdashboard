import json
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

# ===============================================================
# 📄 LOAD & CONVERT
# ===============================================================

def load_ride_json(file_path: str):
    """Load a single ride JSON from Strava (summary + streams)."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"⚠️ Failed to load ride file {file_path}: {e}")
        return None


def strava_json_to_df(data: dict) -> pd.DataFrame:
    """Convert Strava stream data into a clean time-indexed DataFrame."""
    # Ensure stream data exists
    if "time" not in data or "data" not in data["time"]:
        raise ValueError("Missing time stream in Strava data")

    df = pd.DataFrame()
    df["time_s"] = np.array(data["time"]["data"])

    # Optional data streams
    for key in ["distance", "velocity_smooth", "watts", "heartrate", "altitude"]:
        if key in data and isinstance(data[key], dict) and "data" in data[key]:
            df[key] = np.array(data[key]["data"])

    # Derived metrics
    if "distance" in df.columns:
        df["distance_mi"] = df["distance"] / 1609.34
    if "velocity_smooth" in df.columns:
        df["speed_mph"] = df["velocity_smooth"] * 2.23694

    return df


# ===============================================================
# 🧮 METRICS ENGINE
# ===============================================================

def compute_ride_metrics(df: pd.DataFrame, ftp: float = 250, hr_max: int = 190) -> dict:
    """Compute key cycling performance metrics."""
    metrics = {}

    # Distance
    if "distance_mi" in df.columns:
        metrics["distance_mi"] = float(df["distance_mi"].iloc[-1])

    # Duration
    duration_s = float(df["time_s"].iloc[-1])
    metrics["duration_min"] = duration_s / 60

    # Power metrics
    if "watts" in df.columns:
        metrics["avg_power"] = float(np.nanmean(df["watts"]))
        metrics["max_power"] = float(np.nanmax(df["watts"]))
        metrics["np_power"] = _normalized_power(df["watts"])
        metrics["intensity_factor"] = metrics["np_power"] / ftp
        metrics["tss"] = (metrics["duration_min"] / 60) * (metrics["intensity_factor"]**2) * 100

    # HR metrics
    if "heartrate" in df.columns:
        metrics["avg_hr"] = float(np.nanmean(df["heartrate"]))
        metrics["max_hr"] = float(np.nanmax(df["heartrate"]))
        metrics["hr_zone_dist"] = _hr_zones(df["heartrate"], hr_max)

    # Speed
    if "speed_mph" in df.columns:
        metrics["avg_speed"] = float(np.nanmean(df["speed_mph"]))
        metrics["max_speed"] = float(np.nanmax(df["speed_mph"]))

    return metrics


# ===============================================================
# 🧩 HELPER FUNCTIONS
# ===============================================================

def _normalized_power(power_series: np.ndarray) -> float:
    """Calculate Normalized Power per Coggan method."""
    if len(power_series) < 30:
        return np.nan
    rolling_avg = pd.Series(power_series).rolling(window=30, min_periods=1).mean()
    fourth_power = rolling_avg ** 4
    np_power = (np.nanmean(fourth_power)) ** 0.25
    return float(np_power)


def _hr_zones(hr_series: np.ndarray, hr_max: int) -> dict:
    """Compute time spent in 5 heart rate zones."""
    if len(hr_series) == 0:
        return {}
    zones = {
        "Z1 (<68%)": (0, 0.68 * hr_max),
        "Z2 (69–83%)": (0.69 * hr_max, 0.83 * hr_max),
        "Z3 (84–94%)": (0.84 * hr_max, 0.94 * hr_max),
        "Z4 (95–105%)": (0.95 * hr_max, 1.05 * hr_max),
        "Z5 (>106%)": (1.06 * hr_max, 300),
    }
    zone_dist = {}
    total = len(hr_series)
    for z, (low, high) in zones.items():
        pct = np.sum((hr_series >= low) & (hr_series < high)) / total * 100
        zone_dist[z] = round(pct, 1)
    return zone_dist
