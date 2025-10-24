# ============================================================
# 🚴 CYCLING COACHING DASHBOARD — FASTAPI BACKEND
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json

from utils.pdf_generator import generate_ride_report

# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(title="Cycling Coaching Dashboard API", version="1.0")

# Allow CORS for your frontend (adjust the URL when deployed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace "*" with your Vite frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "ride_data/raw"

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "🚴 Cycling Dashboard backend is running!"}

# ============================================================
# LIST RIDES
# ============================================================

@app.get("/api/rides")
def list_rides():
    """List all synced ride files."""
    try:
        if not os.path.exists(DATA_DIR):
            raise HTTPException(status_code=404, detail="Ride data folder not found.")

        rides = []
        for file in os.listdir(DATA_DIR):
            if not file.endswith(".json"):
                continue
            path = os.path.join(DATA_DIR, file)
            try:
                with open(path, "r") as f:
                    act = json.load(f)
                    rides.append({
                        "id": act.get("id"),
                        "name": act.get("name", "Unnamed Ride"),
                        "distance_mi": round(act.get("distance", 0) / 1609.34, 2),
                        "moving_time": act.get("moving_time", 0),
                        "date": act.get("start_date", "Unknown"),
                        "type": act.get("type", "Ride"),
                    })
            except Exception as e:
                print(f"⚠️ Error loading {file}: {e}")
                continue

        rides = sorted(rides, key=lambda x: x["date"], reverse=True)
        return {"count": len(rides), "rides": rides}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# GENERATE PDF REPORT
# ============================================================

@app.get("/api/report/{ride_id}")
def generate_report(ride_id: str):
    """Generate and return PDF report for a specific ride."""
    file_path = os.path.join(DATA_DIR, f"activity_{ride_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Ride file not found.")

    try:
        with open(file_path, "r") as f:
            act = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read activity file.")

    try:
        from utils.metrics import calculate_basic_metrics
        import pandas as pd

        # Convert minimal JSON to DataFrame stub
        df = pd.DataFrame([{
            "distance_mi": act.get("distance", 0) / 1609.34,
            "moving_time": act.get("moving_time", 0),
            "average_speed_mph": (act.get("average_speed", 0) * 2.23694),
            "average_watts": act.get("average_watts", 0),
            "max_watts": act.get("max_watts", 0),
        }])

        metrics = calculate_basic_metrics(df)
        pdf_path = generate_ride_report(df, metrics, f"activity_{ride_id}.json")

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

# ============================================================
# 404 HANDLER
# ============================================================

@app.exception_handler(404)
def not_found_handler(_, exc):
    return JSONResponse(status_code=404, content={"error": str(exc.detail)})

@app.exception_handler(500)
def server_error_handler(_, exc):
    return JSONResponse(status_code=500, content={"error": str(exc.detail)})
