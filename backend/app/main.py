"""
NeoNatal Watch AI - FastAPI Backend
Optimized for low-spec hardware (8GB RAM, 4-core CPU, integrated GPU)
"""

import os
import sys

# --- LOW-SPEC HARDWARE OPTIMIZATIONS ---
# Must be set BEFORE any TensorFlow import
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"        # Suppress C++ TF noise
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"        # Disable oneDNN (AMD stability)
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true" # Don't pre-allocate GPU RAM
os.environ["OMP_NUM_THREADS"] = "4"              # Match Ryzen 3's 4 cores

# Allow backend to import ml modules by adding project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.api.router import api_router
from backend.app.services.inference_service import inference_service
from backend.app.db.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("FastAPI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Code here runs before the server starts accepting requests.
    We use this to load our heavy machine learning models into memory exactly once.
    """
    logger.info("Starting up FastAPI Server...")
    
    # Create Database Tables
    logger.info("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    
    # Load AI Models
    inference_service.load_models()
    yield
    logger.info("Shutting down FastAPI Server...")

# Initialize FastAPI App
app = FastAPI(
    title="NeoNatal Watch AI API",
    description="Real-Time NICU Infant Vital Monitoring and Deterioration Prediction",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS so the frontend can communicate with this API
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()] if cors_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix="/api/v1")

# Mount the frontend static files
from fastapi.staticfiles import StaticFiles
app.mount("/dashboard", StaticFiles(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend")), html=True), name="dashboard")

# Phase 15: Real-time alert WebSocket endpoint
from fastapi import WebSocket
from backend.app.api.endpoints.alerts_ws import alerts_websocket_endpoint

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alerts_websocket_endpoint(websocket)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "models_loaded": inference_service.is_ready,
        "message": "NeoNatal Watch AI Backend is running."
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)

