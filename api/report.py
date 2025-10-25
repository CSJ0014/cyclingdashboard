# api/report.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from vercel_python_runtime import Vercel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/report/generate/{filename}")
def generate_report(filename: str):
    """Placeholder: generate a simple PDF or dummy file."""
    path = os.path.join("ride_data/raw", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Ride not found")

    output_path = f"/tmp/{filename}_report.txt"
    with open(output_path, "w") as f:
        f.write(f"Report for {filename}\nGenerated successfully on Vercel.")

    return FileResponse(output_path, media_type="text/plain", filename="report.txt")

handler = Vercel(app)
