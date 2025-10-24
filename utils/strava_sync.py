import streamlit as st
import requests
import os
import json
from datetime import datetime, timezone

STRAVA_API_URL = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"
RAW_DIR = "ride_data/raw"

# ============================================================
# 🔑 TOKEN MANAGEMENT
# ============================================================

def load_tokens():
    """Load tokens from Streamlit secrets."""
    required_keys = [
        "STRAVA_CLIENT_ID",
        "STRAVA_CLIENT_SECRET",
        "STRAVA_ACCESS_TOKEN",
        "STRAVA_REFRESH_TOKEN",
        "STRAVA_TOKEN_EXPIRES_AT",
    ]
    for key in required_keys:
        if key not in st.secrets:
            raise ValueError(f"Missing key in Streamlit secrets: {key}")

    return dict(
        client_id=st.secrets["STRAVA_CLIENT_ID"],
        client_secret=st.secrets["STRAVA_CLIENT_SECRET"],
        access_token=st.secrets["STRAVA_ACCESS_TOKEN"],
        refresh_token=st.secrets["STRAVA_REFRESH_TOKEN"],
        expires_at=int(st.secrets["STRAVA_TOKEN_EXPIRES_AT"]),
    )


def refresh_token_if_needed(tokens):
    """Refresh Strava access token if expired."""
    if datetime.now(timezone.utc).timestamp() < tokens["expires_at"]:
        return tokens  # still valid

    payload = {
        "client_id": tokens["client_id"],
        "client_secret": tokens["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    }

    r = requests.post(TOKEN_URL, data=payload)
    if r.status_code != 200:
        st.error(f"⚠️ Failed to auto-refresh Strava token: {r.text}")
        st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return tokens

    new_tokens = r.json()
    st.session_state["STRAVA_AUTH_REQUIRED"] = False
    st.session_state["STRAVA_ACCESS_TOKEN"] = new_tokens["access_token"]
    st.session_state["STRAVA_REFRESH_TOKEN"] = new_tokens["refresh_token"]
    st.session_state["STRAVA_TOKEN_EXPIRES_AT"] = new_tokens["expires_at"]
    return tokens


# ============================================================
# 🔁 FETCH ACTIVITIES
# ============================================================

from datetime import datetime, timezone
import os, json, requests, streamlit as st

def fetch_strava_rides(after_year: int = 2025):
    """Fetch only rides from Jan 1 of the specified year onward (Ride, VirtualRide, GravelRide)."""
    try:
        tokens = load_tokens()
    except Exception as e:
        st.error(f"⚠️ Missing or invalid Strava tokens: {e}")
        st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return "Missing Strava credentials."

    tokens = refresh_token_if_needed(tokens)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Only fetch rides starting from Jan 1 of the specified year
    after_timestamp = int(datetime(after_year, 1, 1, tzinfo=timezone.utc).timestamp())

    page = 1
    total_new = 0
    total_seen = 0
    os.makedirs(RAW_DIR, exist_ok=True)

    while True:
        params = {"after": after_timestamp, "per_page": 100, "page": page}
        r = requests.get(f"{STRAVA_API_URL}/athlete/activities", headers=headers, params=params)

        if r.status_code == 401:
            st.session_state["STRAVA_AUTH_REQUIRED"] = True
            return "⚠️ Authorization failed or missing permissions. Please reconnect Strava."
        elif r.status_code != 200:
            st.error(f"⚠️ Failed to fetch activities (page {page}): {r.text}")
            break

        activities = r.json()
        if not activities:
            break  # No more pages left

        for act in activities:
            total_seen += 1
            if act.get("type") not in ["Ride", "VirtualRide", "GravelRide"]:
                continue
            activity_id = act["id"]
            file_path = os.path.join(RAW_DIR, f"activity_{activity_id}.json")
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    json.dump(act, f, indent=2)
                total_new += 1

        page += 1

    return f"✅ Synced {total_new} new rides from {after_year} onward ({total_seen} total found)."


def auto_sync_if_ready():
    """Run automatic Strava sync for 2025 onward."""
    try:
        msg = fetch_strava_rides(after_year=2025)
        if "Missing Strava" in msg or "Authorization" in msg:
            st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return msg
    except Exception as e:
        st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return f"⚠️ Auto-sync failed: {e}"


# ============================================================
# 🧠 AUTO SYNC
# ============================================================

def auto_sync_if_ready():
    """Run automatic sync if tokens and permissions are valid."""
    try:
        msg = fetch_strava_rides(after_year=2025)
        if "Missing Strava" in msg or "Authorization" in msg:
            st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return msg
    except Exception as e:
        st.session_state["STRAVA_AUTH_REQUIRED"] = True
        return f"⚠️ Auto-sync failed: {e}"


# ============================================================
# 🔗 RECONNECT PROMPT
# ============================================================

def reconnect_prompt():
    """Show reconnect link if missing permissions or expired token."""
    st.markdown("---")
    st.warning("⚠️ Strava authorization is missing required permissions.")
    st.markdown("""
        Please reauthorize your Strava connection to grant **activity:read_all** access.  
        Click the link below to reconnect:
    """)
    client_id = st.secrets.get("STRAVA_CLIENT_ID", "")
    if not client_id:
        st.error("⚠️ Missing STRAVA_CLIENT_ID in secrets.")
        return

    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri=http://localhost/exchange_token"
        f"&response_type=code"
        f"&scope=read,activity:read_all"
    )
    st.markdown(f"👉 [Click here to reconnect your Strava account]({auth_url})", unsafe_allow_html=True)
    st.markdown("_Once you reconnect, copy your code into Colab to refresh your tokens._")
