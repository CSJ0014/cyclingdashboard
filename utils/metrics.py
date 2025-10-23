import os, json, pandas as pd, numpy as np
from datetime import datetime

RAW_DIR = "ride_data/raw"

def build_tss_dataframe(rides, ftp=222):
    """
    Build a dataframe of rides with TSS, CTL, ATL, and TSB metrics.
    Handles both FIT and Strava JSON formats.
    """
    rows = []
    for file in rides:
        path = os.path.join(RAW_DIR, file)
        try:
            with open(path) as f:
                data = json.load(f)
            meta = data.get("_meta", {})
            date = meta.get("start_date") or meta.get("start_date_local") or None
            if date:
                try:
                    date = datetime.fromisoformat(date.replace("Z", "+00:00")).date()
                except Exception:
                    continue
            else:
                continue

            # compute basic metrics
            avg_watts = meta.get("average_watts") or np.nan
            moving_time = meta.get("moving_time_s") or meta.get("moving_time") or 0
            tss = np.nan
            if avg_watts and ftp and moving_time:
                tss = (moving_time * avg_watts * (avg_watts / ftp)) / (ftp * 3600) * 100

            rows.append({
                "date": date,
                "name": meta.get("name", os.path.basename(file)),
                "tss": round(tss, 1) if not np.isnan(tss) else np.nan,
                "distance_m": meta.get("distance_m", 0),
                "type": meta.get("type", "Ride"),
            })
        except Exception as e:
            print(f"⚠️ Error processing {file}: {e}")

    if not rows:
        return pd.DataFrame(columns=["date", "name", "tss", "distance_m", "type"])

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    # calculate rolling metrics
    df["CTL"] = df["tss"].rolling(window=42, min_periods=1).mean()
    df["ATL"] = df["tss"].rolling(window=7, min_periods=1).mean()
    df["TSB"] = df["CTL"] - df["ATL"]

    return df

def get_all_ride_files():
    """Helper to list all ride JSON files"""
    if not os.path.exists(RAW_DIR):
        return []
    return [f for f in os.listdir(RAW_DIR) if f.endswith(".json")]
