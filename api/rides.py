# api/rides.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from vercel_python_runtime import Vercel
import os
import json

app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rides")
def list_rides():
    """List all available rides from ride_data/raw"""
    rides_dir = "ride_data/raw"
    if not os.path.exists(rides_dir):
        return JSONResponse({"rides": []})
    rides = [f for f in os.listdir(rides_dir) if f.endswith((".fit", ".csv", ".json"))]
    return JSONResponse({"rides": rides})

@app.get("/api/rides/{filename}")
def get_ride(filename: str):
    """Return the contents of a specific ride (simplified for demo)"""
    path = os.path.join("ride_data/raw", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Ride not found")

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        data = {"message": f"Loaded {filename} (not JSON readable)"}
    return JSONResponse(data)

# Vercel handler
handler = Vercel(app)
