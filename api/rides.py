# api/rides.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rides")
def list_rides():
    """List available rides, with demo fallback for Vercel."""
    rides_dir = "ride_data/raw"

    if os.path.exists(rides_dir):
        rides = [
            f for f in os.listdir(rides_dir)
            if f.endswith((".fit", ".csv", ".json"))
        ]
    else:
        # ✅ fallback demo rides so frontend isn’t empty
        rides = [
            "demo_ride_001.json",
            "demo_ride_002.json",
            "demo_ride_003.json"
        ]

    return JSONResponse({"rides": rides})


@app.get("/api/rides/{filename}")
def get_ride(filename: str):
    """Return file data or demo JSON if not found."""
    path = os.path.join("ride_data/raw", filename)

    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            data = {"message": f"Loaded {filename} (not JSON readable)"}
        return JSONResponse(data)

    # Demo data fallback for cloud deployment
    return JSONResponse({
        "filename": filename,
        "status": "ok",
        "distance_miles": 24.8,
        "avg_power": 216,
        "duration_minutes": 63,
        "normalized_power": 229,
        "note": "Demo ride data for Vercel deployment."
    })
