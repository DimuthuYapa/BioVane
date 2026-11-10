"""
BioVane Launcher
Starts the BioVane FastAPI backend and serves both the API and the compiled React command-center UI.
"""
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("=" * 65)
    print("Starting BioVane: Micro-Climate & Shift Fatigue Anomaly Grid")
    print("=" * 65)
    print("Dashboard URL:   http://127.0.0.1:8000")
    print("API Swagger:     http://127.0.0.1:8000/docs")
    print("Privacy Guard:   k >= 5, Laplace Differential Privacy active")
    print("Micro-Climate:   Live Open-Meteo Telemetry + GCC Presets")
    print("=" * 65)

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
