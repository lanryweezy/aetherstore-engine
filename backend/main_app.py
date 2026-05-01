# main_app.py
# Main FastAPI application for Aetherstore Engine

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import os
from api import api_router
from database import init_db, get_db_health
from config import settings
from security_middleware import limiter, rate_limit_handler, SecurityMiddleware
from slowapi.errors import RateLimitExceeded
from monitoring_service import monitoring_service, monitoring_middleware
from email_service import email_service
import logging
import asyncio
import json
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="The ultimate 3D fashion platform API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS.split(",") if settings.CORS_METHODS != "*" else ["*"],
    allow_headers=settings.CORS_HEADERS.split(",") if settings.CORS_HEADERS != "*" else ["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add monitoring middleware
from starlette.middleware.base import BaseHTTPMiddleware

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await monitoring_middleware(request, call_next)

app.add_middleware(MonitoringMiddleware)

# WebSocket manager for social shopping
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Maps room_id -> user_id -> WebSocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Redis client for Pub/Sub
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Background tasks to listen to Redis channels
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}

    async def _redis_listener(self, room_id: str):
        """Background task that listens to Redis for messages sent to this room by other server nodes."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(room_id)
        logger.info(f"Subscribed to Redis channel for room: {room_id}")

        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    target_user_id = data.get("internal_target_user_id")
                    exclude_user_id = data.get("internal_exclude_user_id")

                    # Clean internal routing fields before sending to clients
                    payload = {k: v for k, v in data.items() if not k.startswith("internal_")}

                    if target_user_id:
                        # Direct personal message routing
                        if room_id in self.active_connections and target_user_id in self.active_connections[room_id]:
                            await self.active_connections[room_id][target_user_id].send_json(payload)
                    else:
                        # Broadcast routing
                        if room_id in self.active_connections:
                            for uid, connection in self.active_connections[room_id].items():
                                if uid != exclude_user_id:
                                    try:
                                        await connection.send_json(payload)
                                    except Exception as e:
                                        logger.error(f"Error sending message to {uid} in {room_id}: {e}")
        except asyncio.CancelledError:
            await pubsub.unsubscribe(room_id)
            logger.info(f"Unsubscribed from Redis channel for room: {room_id}")

    async def connect(self, room_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            # Start a Redis listener for this room if one doesn't exist on this node
            if room_id not in self.pubsub_tasks:
                self.pubsub_tasks[room_id] = asyncio.create_task(self._redis_listener(room_id))

        self.active_connections[room_id][user_id] = websocket
        # Increment a Redis counter for global occupancy
        await self.redis.hincrby("room_occupancy", room_id, 1)

    async def disconnect(self, room_id: str, user_id: str):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            # Decrement global occupancy
            await self.redis.hincrby("room_occupancy", room_id, -1)

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                # Stop Redis listener for this room to save resources
                if room_id in self.pubsub_tasks:
                    self.pubsub_tasks[room_id].cancel()
                    del self.pubsub_tasks[room_id]

    async def broadcast(self, room_id: str, message: dict, exclude_user_id: str = None):
        """Publish a broadcast message to Redis, so all server nodes receive it."""
        message["internal_exclude_user_id"] = exclude_user_id
        await self.redis.publish(room_id, json.dumps(message))

    async def send_personal_message(self, room_id: str, target_user_id: str, message: dict):
        """Publish a direct message to Redis, so the node holding the target user can send it."""
        message["internal_target_user_id"] = target_user_id
        await self.redis.publish(room_id, json.dumps(message))

    async def get_occupancy(self, room_id: str) -> int:
        """Fetch the global occupancy count across all server nodes."""
        val = await self.redis.hget("room_occupancy", room_id)
        return int(val) if val else 0

manager = ConnectionManager()

@app.websocket("/ws/social/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await manager.connect(room_id, user_id, websocket)
    try:
        # Broadcast user joined + occupancy update
        await manager.broadcast(room_id, {
            "type": "presence",
            "user_id": user_id,
            "status": "joined",
            "occupancy": await manager.get_occupancy(room_id),
            "timestamp": datetime.now().isoformat()
        }, exclude_user_id=user_id)

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                await manager.broadcast(room_id, {
                    "type": "chat",
                    "user_id": user_id,
                    "message": data.get("message"),
                    "timestamp": datetime.now().isoformat()
                })
            elif msg_type == "transform":
                # Real-time position/rotation sync for avatars
                await manager.broadcast(room_id, {
                    "type": "transform",
                    "user_id": user_id,
                    "position": data.get("position"),
                    "rotation": data.get("rotation"),
                    "animation_state": data.get("animation_state"),
                    "timestamp": datetime.now().isoformat()
                }, exclude_user_id=user_id)
            elif msg_type in ["webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"]:
                # WebRTC Signaling - Send directly to the target peer
                target_user = data.get("target_user_id")
                if target_user:
                    await manager.send_personal_message(room_id, target_user, {
                        "type": msg_type,
                        "user_id": user_id, # The sender
                        "payload": data.get("payload")
                    })

    except WebSocketDisconnect:
        await manager.disconnect(room_id, user_id)
        await manager.broadcast(room_id, {
            "type": "presence",
            "user_id": user_id,
            "status": "left",
            "occupancy": await manager.get_occupancy(room_id),
            "timestamp": datetime.now().isoformat()
        })

# Mount static files for frontend
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Include API routers
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Aetherstore Engine...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Don't raise exception to allow app to start for development
    
    # Initialize monitoring (Sentry)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        monitoring_service.initialize_sentry(sentry_dsn, settings.ENVIRONMENT)
        logger.info("Sentry monitoring initialized")
    
    logger.info("Aetherstore Engine started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup application on shutdown"""
    logger.info("Shutting down Aetherstore Engine...")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Root endpoint with welcome page"""
    return """
    <html>
        <head>
            <title>Aetherstore Engine</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                h1 { font-size: 3em; margin-bottom: 20px; }
                p { font-size: 1.2em; margin-bottom: 30px; }
                .links { display: flex; justify-content: center; gap: 20px; }
                a { color: #fff; text-decoration: none; padding: 10px 20px; border: 2px solid #fff; border-radius: 5px; transition: all 0.3s; }
                a:hover { background: rgba(255,255,255,0.2); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 Aetherstore Engine</h1>
                <p>The ultimate 3D fashion platform API</p>
                <div class="links">
                    <a href="/docs">📘 API Documentation</a>
                    <a href="/redoc">📖 ReDoc Documentation</a>
                    <a href="/static">🛍️ Frontend</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
@app.get("/api/health") # Backwards compatibility
async def health_check():
    """Health check endpoint"""
    db_healthy = get_db_health()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now(),
        "database": "healthy" if db_healthy else "unhealthy",
        "version": settings.APP_VERSION
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": datetime.now()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics"""
    return monitoring_service.get_metrics()

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics = monitoring_service.get_prometheus_metrics()
    if metrics:
        from fastapi.responses import Response
        return Response(content=metrics, media_type="text/plain")
    else:
        return {"message": "Prometheus not available"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {"error": "Resource not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(exc)}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    uvicorn.run(
        "main_app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )