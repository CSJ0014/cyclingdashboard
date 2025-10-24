# backend/routes/report.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile

router = APIRouter()

# We'll import your existing PDF generator from backend.utils.pdf_generator
# Ensure you copied your utils/ into backend/utils/
try:
    from utils.pdf_generator import generate_ride_report
    from utils.ride_analysis_utils import strava_json_to_df, compute_ride_metrics, load_ride_json
except Exception as e:
    # If utils are not present or import fails, endpoints will raise at runtime
    generate_ride_report = None
    strava_json_to_df = None
    compute_ride_metrics = None
    load_ride_json = None

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ride_data", "raw")

def get_raw_dir():
    # same logic as rides.py
    repo_root = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(repo_root, "ride_data", "raw"),
        os.path.join(repo_root, "..", "ride_data", "raw"),
        os.path.join(repo_root, "backend", "ride_data", "raw"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


@router.post("/generate/{fname}")
def generate(fname: str):
    if generate_ride_report is None:
        raise HTTPException(status_code=500, detail="PDF generator not available on server")
    raw = get_raw_dir()
    path = os.path.join(raw, fname)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Ride JSON not found")

    # load data and compute metrics
    data = load_ride_json(path)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load ride data")

    df = strava_json_to_df(data)
    metrics = compute_ride_metrics(df)
    pdf_path = generate_ride_report(df, metrics, fname)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF generation failed")

    return FileResponse(path=pdf_path, filename=os.path.basename(pdf_path), media_type='application/pdf')
