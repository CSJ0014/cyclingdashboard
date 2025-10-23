import os, json, time, requests, streamlit as st
from datetime import datetime, timezone

SETTINGS_FILE = "ride_data/settings.json"
RAW_DIR = "ride_data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

CLIENT_ID = st.secrets.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = st.secrets.get("STRAVA_REFRESH_TOKEN")

def _save_settings(s):
    os.makedirs("ride_data", exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def strava_refresh_if_needed():
    """Auto-refresh Strava token using the refresh token in secrets.toml"""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)

    # Return cached token if still valid
    if (
        "STRAVA_ACCESS_TOKEN" in settings
        and time.time() < settings.get("STRAVA_TOKEN_EXPIRES_AT", 0) - 300
    ):
        return settings["STRAVA_ACCESS_TOKEN"]

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": settings.get("STRAVA_REFRESH_TOKEN", REFRESH_TOKEN),
    }
    r = requests.post("https://www.strava.com/oauth/token", data=data)
    if r.status_code == 200:
        tok = r.json()
        settings.update({
            "STRAVA_ACCESS_TOKEN": tok["access_token"],
            "STRAVA_REFRESH_TOKEN": tok["refresh_token"],
            "STRAVA_TOKEN_EXPIRES_AT": tok["expires_at"],
        })
        _save_settings(settings)
        return tok["access_token"]
    else:
        st.warning(f"⚠️ Failed to auto-refresh Strava token: {r.text}")
        return None

def fetch_strava_rides(after_year=2025):
    """Automatically fetch and save new Strava activities."""
    access_token = strava_refresh_if_needed()
    if not access_token:
        return "⚠️ Strava token not available."

    after_timestamp = int(datetime(after_year, 1, 1, tzinfo=timezone.utc).timestamp())
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://www.strava.com/api/v3/athlete/activities"
    page, total_new = 1, 0

    while True:
        params = {"per_page": 50, "page": page, "after": after_timestamp}
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            st.error(f"Strava API error: {r.text}")
            break

        activities = r.json()
        if not activities:
            break

        for a in activities:
            # Only keep Ride, Gravel Ride, Virtual Ride
            if a["type"] not in ["Ride", "Gravel Ride", "VirtualRide"]:
                continue

            a_id = a["id"]
            save_path = os.path.join(RAW_DIR, f"activity_{a_id}.json")
            if os.path.exists(save_path):
                continue  # Skip existing

            # Fetch full activity stream
            stream_url = f"https://www.strava.com/api/v3/activities/{a_id}/streams"
            stream_params = {"keys": "time,distance,heartrate,watts,velocity_smooth,latlng", "key_by_type": "true"}
            stream_resp = requests.get(stream_url, headers=headers, params=stream_params)

            if stream_resp.status_code == 200:
                data = stream_resp.json()
                data["_meta"] = {
                    "name": a.get("name", f"Activity {a_id}"),
                    "type": a.get("type", ""),
                    "date": a.get("start_date_local", ""),
                }
                with open(save_path, "w") as f:
                    json.dump(data, f)
                total_new += 1
        page += 1

    return f"✅ Synced {total_new} new activities automatically."
