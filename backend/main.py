import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from observability_middleware import ObservabilityMiddleware
from api import api_router
from api.physics import router as physics_router
from config import settings

from websocket_manager import manager as ws_manager
from ai_processing import ai_processor

# Define Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize system infrastructure on startup"""
    logging.info(f"Starting {settings.APP_NAME}...")
    for directory in [settings.UPLOAD_DIR, settings.DATA_DIR, settings.TEMP_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Start Real-time Telemetry & Task Watchdog
    telemetry_task = asyncio.create_task(ws_manager.stream_system_health(ai_processor))
    watchdog_task = asyncio.create_task(ws_manager.watch_ai_tasks())
    
    logging.info("Infrastructure & Distributed Watchdog initialized.")
    yield
    # Cleanup
    telemetry_task.cancel()
    watchdog_task.cancel()
    logging.info("Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Aetherstore Engine API",
    description="The ultimate 3D fashion platform API - Refactored for Universal Intelligence",
    version="2.0.0",
    lifespan=lifespan
)

@app.websocket("/ws/nerve-center")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "guest"):
    """
    Real-time Nerve Center WebSocket Endpoint.
    Handles telemetry stream and player presence.
    """
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Wait for client spatial updates
            data = await websocket.receive_json()
            if data.get("type") == "PRESENCE_SYNC":
                await ws_manager.handle_presence_update(user_id, data.get("state", {}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WS Runtime Error: {e}")
        ws_manager.disconnect(websocket, user_id)

# Register Observability Middleware (Early for full coverage)
app.add_middleware(ObservabilityMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend (Robust Path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "..", "frontend")

if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logging.warning(f"Static directory not found: {static_dir}. Serving placeholder mode.")

# Include Modular Routers
app.include_router(api_router)
app.include_router(physics_router)

# Root Endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Aetherstore Engine v2.0</title>
            <style>
                body { background: #020617; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
                h1 { background: linear-gradient(to right, #60a5fa, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 900; }
                a { color: #38bdf8; text-decoration: none; border: 1px solid #1e293b; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s; }
                a:hover { background: #1e293b; border-color: #38bdf8; }
            </style>
        </head>
        <body>
            <h1>Aetherstore Engine 2.0</h1>
            <p>Unified 25-Pillar Meta Research Stack Active</p>
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <a href="/docs">API Docs</a>
                <a href="/static/super_intelligence_demo.html">Super-AI Center</a>
                <a href="/static">Launch Platform</a>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
