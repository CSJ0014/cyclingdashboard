import os, json, time, requests, streamlit as st
from datetime import datetime, timezone

SETTINGS_FILE = "ride_data/settings.json"
RAW_DIR = "ride_data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

CLIENT_ID = st.secrets.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = st.secrets.get("STRAVA_CLIENT_SECRET")

def _load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_settings(s):
    os.makedirs("ride_data", exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def strava_refresh_if_needed():
    """Return a valid Strava access token, refreshing if needed."""
    s = _load_settings()
    if "STRAVA_ACCESS_TOKEN" not in s:
        return None
    if time.time() < s.get("STRAVA_TOKEN_EXPIRES_AT", 0) - 300:
        return s["STRAVA_ACCESS_TOKEN"]

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": s["STRAVA_REFRESH_TOKEN"],
    }
    r = requests.post("https://www.strava.com/oauth/token", data=data)
    if r.status_code == 200:
        tok = r.json()
        s.update({
            "STRAVA_ACCESS_TOKEN": tok["access_token"],
            "STRAVA_REFRESH_TOKEN": tok["refresh_token"],
            "STRAVA_TOKEN_EXPIRES_AT": tok["expires_at"],
        })
        _save_settings(s)
        return s["STRAVA_ACCESS_TOKEN"]
    return None

def fetch_strava_rides(after_year=2025):
    """Download new rides (Ride, Gravel, Virtual) since given year."""
    token = strava_refresh_if_needed()
    if not token:
        return "⚠️ Strava not connected."

    after_timestamp = int(datetime(after_year, 1, 1, tzinfo=timezone.utc).timestamp())
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://www.strava.com/api/v3/athlete/activities?after={after_timestamp}&per_page=100"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return f"⚠️ Failed to fetch rides: {r.text}"

    activities = r.json()
    new_count = 0
    for a in activities:
        if a["type"].lower() not in ["ride", "gravel_ride", "virtualride"]:
            continue
        act_id = a["id"]
        out_path = os.path.join(RAW_DIR, f"activity_{act_id}.json")
        if os.path.exists(out_path):
            continue
        a["_meta"] = {
            "id": act_id,
            "name": a.get("name", f"Ride {act_id}"),
            "distance_m": a.get("distance", 0),
            "moving_time_s": a.get("moving_time", 0),
            "average_watts": a.get("average_watts", 0),
            "average_heartrate": a.get("average_heartrate", 0),
            "start_date": a.get("start_date", ""),
            "type": a.get("type", "Ride"),
        }
        with open(out_path, "w") as f:
            json.dump(a, f, indent=2)
        new_count += 1
    return f"✅ Synced {new_count} new rides from Strava."

def connect_strava(code):
    """Complete OAuth handshake and store tokens using secrets for credentials."""
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    r = requests.post("https://www.strava.com/oauth/token", data=data)
    if r.status_code != 200:
        return f"❌ Authorization failed: {r.text}"

    tok = r.json()
    s = _load_settings()
    s.update({
        "STRAVA_ACCESS_TOKEN": tok["access_token"],
        "STRAVA_REFRESH_TOKEN": tok["refresh_token"],
        "STRAVA_TOKEN_EXPIRES_AT": tok["expires_at"],
    })
    _save_settings(s)
    return "✅ Connected to Strava successfully."
