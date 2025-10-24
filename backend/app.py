# backend/app.py

import sys, os

# add repo root to Python path so we can import utils
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import rides, report

app = FastAPI(title="Cycling Dashboard API")

# allow CORS from frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rides.router, prefix="/api/rides", tags=["rides"])
app.include_router(report.router, prefix="/api/report", tags=["report"])
