import streamlit as st
import pandas as pd
import os, json

RAW_DIR = "ride_data/raw"

def safe_get_distance_miles(data):
    """Return distance in miles from any data format (Strava or FIT-style)."""
    try:
        # --- Strava API format (flat) ---
        if isinstance(data.get("distance"), (int, float)):
            return round(float(data["distance"]) / 1609.34, 2)
        # --- FIT parser style (nested dict with .data) ---
        elif isinstance(data.get("distance"), dict) and "data" in data["distance"]:
            dist_list = data["distance"]["data"]
            return round(dist_list[-1] / 1609.34, 2) if dist_list else 0.0
    except Exception:
        return 0.0
    return 0.0


def safe_get_name(data, file_name):
    """Return clean activity name or fallback."""
    return (
        data.get("name")
        or data.get("_meta", {}).get("name")
        or f"Unnamed Activity ({file_name.replace('.json', '')})"
    )


def list_rides():
    """List all valid ride files (sorted newest to oldest)."""
    rides = []
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR)
        return pd.DataFrame()

    for f in sorted(os.listdir(RAW_DIR), reverse=True):
        if not f.endswith(".json"):
            continue
        path = os.path.join(RAW_DIR, f)
        try:
            with open(path, "r") as file:
                data = json.load(file)
            name = safe_get_name(data, f)
            distance = safe_get_distance_miles(data)

            # Try to read power & HR if present (Strava or FIT)
            avg_power = None
            avg_hr = None

            if "average_watts" in data:
                avg_power = data["average_watts"]
            elif isinstance(data.get("watts"), dict) and "data" in data["watts"]:
                watts = data["watts"]["data"]
                avg_power = sum(watts) / len(watts) if watts else None

            if "average_heartrate" in data:
                avg_hr = data["average_heartrate"]
            elif isinstance(data.get("heartrate"), dict) and "data" in data["heartrate"]:
                hrs = data["heartrate"]["data"]
                avg_hr = sum(hrs) / len(hrs) if hrs else None

            rides.append({
                "Activity": name,
                "File": f,
                "Distance (mi)": distance,
                "Avg Power (W)": round(avg_power, 1) if avg_power else None,
                "Avg HR (bpm)": round(avg_hr, 1) if avg_hr else None
            })
        except Exception as e:
            st.warning(f"⚠️ Skipped {f}: {e}")
            continue

    return pd.DataFrame(rides)


def render():
    st.title("🚴 Ride History")

    rides = list_rides()
    if rides.empty:
        st.info("No rides found. Sync with Strava or upload FIT files first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Rides")

    for _, row in rides.iterrows():
        cols = st.columns([4, 0.6, 0.6])
        cols[0].markdown(
            f"**{row['Activity']}** — {row['Distance (mi)']:.2f} mi  |  "
            f"⚡ {row['Avg Power (W)'] or '—'} W  |  ❤️ {row['Avg HR (bpm)'] or '—'} bpm"
        )

        if cols[1].button("🔍", key=f"view_{row['File']}"):
            st.session_state["selected_ride"] = row["File"]
            st.session_state["active_tab"] = "📊 Ride Analysis"
            st.rerun()

        if cols[2].button("🗑️", key=f"delete_{row['File']}"):
            os.remove(os.path.join(RAW_DIR, row["File"]))
            st.success(f"Deleted {row['Activity']}")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
