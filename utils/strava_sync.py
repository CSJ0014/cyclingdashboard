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
    """
    Download ALL detailed Strava rides (Ride, Gravel, VirtualRide) since given year.
    Uses pagination to fetch all pages of results.
    """
    token = strava_refresh_if_needed()
    if not token:
        return "⚠️ Strava not connected."

    after_timestamp = int(datetime(after_year, 1, 1, tzinfo=timezone.utc).timestamp())
    headers = {"Authorization": f"Bearer {token}"}

    page = 1
    total_new = 0
    while True:
        url = f"https://www.strava.com/api/v3/athlete/activities?after={after_timestamp}&per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return f"⚠️ Failed on page {page}: {r.text}"

        activities = r.json()
        if not activities:
            break  # ✅ no more pages

        for a in activities:
            type_lower = a["type"].lower()
            if type_lower not in ["ride", "gravel_ride", "virtualride"]:
                continue

            act_id = a["id"]
            out_path = os.path.join(RAW_DIR, f"activity_{act_id}.json")
            if os.path.exists(out_path):
                continue  # already downloaded

            # --- fetch detailed stream data ---
            stream_url = f"https://www.strava.com/api/v3/activities/{act_id}/streams"
            params = {"keys": "time,distance,watts,heartrate,velocity_smooth", "key_by_type": "true"}
            s = requests.get(stream_url, headers=headers, params=params)
            data = {}
            if s.status_code == 200:
                data = s.json()
            else:
                print(f"⚠️ Stream fetch failed for {act_id}: {s.text}")

            # --- merge summary + streams ---
            ride = {
                "_meta": {
                    "id": act_id,
                    "name": a.get("name", f"Ride {act_id}"),
                    "distance_m": a.get("distance", 0),
                    "moving_time_s": a.get("moving_time", 0),
                    "average_watts": a.get("average_watts", 0),
                    "average_heartrate": a.get("average_heartrate", 0),
                    "start_date": a.get("start_date", ""),
                    "type": a.get("type", "Ride"),
                }
            }
            ride.update(data)

            with open(out_path, "w") as f:
                json.dump(ride, f, indent=2)
            total_new += 1

        page += 1
        time.sleep(0.5)  # small pause to respect Strava API rate limits

    return f"✅ Synced {total_new} new rides (Ride, Gravel, Virtual) from Strava."

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
