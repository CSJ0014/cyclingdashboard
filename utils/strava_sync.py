import os
import requests
import json
import time
from datetime import datetime, timezone
import streamlit as st


# ==============================================================
# ⚙️  STRAVA CONFIGURATION
# ==============================================================

STRAVA_API_BASE = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"
RAW_DIR = "ride_data/raw"


# ==============================================================
# 🔑  TOKEN MANAGEMENT HELPERS
# ==============================================================

def get_tokens():
    """Fetch Strava API credentials and tokens from secrets or session."""
    return {
        "client_id": st.secrets.get("STRAVA_CLIENT_ID"),
        "client_secret": st.secrets.get("STRAVA_CLIENT_SECRET"),
        "access_token": st.session_state.get("STRAVA_ACCESS_TOKEN", st.secrets.get("STRAVA_ACCESS_TOKEN")),
        "refresh_token": st.session_state.get("STRAVA_REFRESH_TOKEN", st.secrets.get("STRAVA_REFRESH_TOKEN")),
        "expires_at": float(st.session_state.get("STRAVA_TOKEN_EXPIRES_AT", st.secrets.get("STRAVA_TOKEN_EXPIRES_AT", "0"))),
    }


def save_tokens(tokens):
    """Store refreshed tokens in session so future calls use them."""
    st.session_state["STRAVA_ACCESS_TOKEN"] = tokens["access_token"]
    st.session_state["STRAVA_REFRESH_TOKEN"] = tokens["refresh_token"]
    st.session_state["STRAVA_TOKEN_EXPIRES_AT"] = tokens["expires_at"]


def refresh_access_token(tokens):
    """Refresh Strava access token if expired or invalid."""
    if not tokens["refresh_token"]:
        raise ValueError("Missing Strava refresh token. Please reconnect.")

    payload = {
        "client_id": tokens["client_id"],
        "client_secret": tokens["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    }

    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to auto-refresh Strava token: {response.text}")

    new_tokens = response.json()
    save_tokens({
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens["refresh_token"],
        "expires_at": new_tokens["expires_at"],
    })
    return new_tokens["access_token"]


def ensure_valid_token():
    """Ensure we have a valid token or refresh it."""
    tokens = get_tokens()
    now = time.time()

    # Refresh if token expired
    if now >= tokens["expires_at"]:
        try:
            new_access_token = refresh_access_token(tokens)
            return new_access_token
        except ValueError as e:
            if "invalid" in str(e).lower():
                st.warning("⚠️ Your Strava authorization has expired. Please reconnect below.")
                st.session_state["STRAVA_AUTH_REQUIRED"] = True
                return None
            raise
    return tokens["access_token"]


# ==============================================================
# 🚴  RIDE FETCHING
# ==============================================================

def fetch_strava_rides(after_year=2025):
    """Fetch recent rides from Strava API."""
    os.makedirs(RAW_DIR, exist_ok=True)
    access_token = ensure_valid_token()
    if not access_token:
        return "⚠️ Reauthorization required."

    after_timestamp = int(datetime(after_year, 1, 1, tzinfo=timezone.utc).timestamp())
    headers = {"Authorization": f"Bearer {access_token}"}

    page, new_count = 1, 0
    while True:
        resp = requests.get(
            f"{STRAVA_API_BASE}/athlete/activities",
            params={"after": after_timestamp, "page": page, "per_page": 50},
            headers=headers,
        )
        if resp.status_code != 200:
            raise ValueError(f"Failed to fetch activities: {resp.text}")

        activities = resp.json()
        if not activities:
            break

        for act in activities:
            act_type = act.get("type", "")
            if act_type not in ["Ride", "VirtualRide", "GravelRide"]:
                continue
            file_path = os.path.join(RAW_DIR, f"activity_{act['id']}.json")
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    json.dump(act, f, indent=2)
                new_count += 1
        page += 1

    return f"✅ Synced {new_count} new rides (Ride, Virtual, Gravel)."


# ==============================================================
# 🔁  RECONNECT PROMPT
# ==============================================================

def reconnect_prompt():
    """Display reconnect button when Strava tokens are invalid."""
    with st.sidebar:
        st.warning("⚠️ Strava connection expired. Please reconnect your account.")
        reconnect_url = (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={st.secrets['STRAVA_CLIENT_ID']}"
            f"&response_type=code"
            f"&redirect_uri=https://YOUR-STREAMLIT-APP-URL"
            f"&approval_prompt=auto&scope=activity:read_all"
        )
        st.markdown(f"[🔗 Reconnect to Strava]({reconnect_url})")


# ==============================================================
# ✅  ENTRY POINT FOR AUTO SYNC
# ==============================================================

def auto_sync_if_ready():
    """Run auto-sync only if tokens are valid and no reauth needed."""
    if st.session_state.get("STRAVA_AUTH_REQUIRED"):
        reconnect_prompt()
        return "⚠️ Reauthorization required."
    try:
        msg = fetch_strava_rides(after_year=2025)
        return msg
    except Exception as e:
        if "invalid" in str(e).lower():
            st.session_state["STRAVA_AUTH_REQUIRED"] = True
            reconnect_prompt()
            return "⚠️ Token invalid; please reconnect."
        raise
