# backend/routes/rides.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from typing import List

router = APIRouter()

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ride_data", "raw")
# If you moved your ride_data/raw under backend, adjust path accordingly.
# Alternatively, set RAW_DIR to the absolute path of repo/ride_data/raw

def get_raw_dir():
    # try common locations
    repo_root = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(repo_root, "ride_data", "raw"),
        os.path.join(repo_root, "..", "ride_data", "raw"),
        os.path.join(repo_root, "backend", "ride_data", "raw"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # fallback to first candidate
    return candidates[0]

@router.get("/", response_class=JSONResponse)
def list_rides():
    raw = get_raw_dir()
    if not os.path.exists(raw):
        return []
    rides = []
    for fname in sorted(os.listdir(raw), reverse=True):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(raw, fname)
        try:
            with open(path, "r") as f:
                data = json.load(f)
            rides.append({
                "id": data.get("id", fname.replace("activity_", "").replace(".json", "")),
                "name": data.get("name", "Untitled"),
                "date": data.get("start_date_local") or data.get("start_date"),
                "distance_m": data.get("distance", None),
                "moving_time": data.get("moving_time", None),
                "path": fname
            })
        except Exception:
            continue
    return rides

@router.get("/{fname}")
def get_ride(fname: str):
    raw = get_raw_dir()
    path = os.path.join(raw, fname)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Ride not found")
    with open(path, "r") as f:
        data = json.load(f)
    return data
