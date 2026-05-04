import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

logger = logging.getLogger("aetherstore.websocket")
class ConnectionManager:
    """
    Manages persistent WebSocket connections for real-time telemetry,
    multisensory synchronization, social presence, and task notifications.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.player_states: Dict[str, Dict[str, Any]] = {}
        self.tracked_tasks: Dict[str, str] = {} # task_id -> user_id

    async def watch_ai_tasks(self):
        """
        Background task that monitors Celery workers and notifies users 
        instantly when their cinematic reels or 3D models are ready.
        """
        from worker import celery_app
        while True:
            if self.tracked_tasks:
                for task_id, user_id in list(self.tracked_tasks.items()):
                    res = celery_app.AsyncResult(task_id)
                    if res.ready():
                        await self.broadcast({
                            "type": "TASK_COMPLETED",
                            "user_id": user_id,
                            "task_id": task_id,
                            "status": res.status,
                            "result": res.result
                        })
                        del self.tracked_tasks[task_id]
            await asyncio.sleep(1) # Watchdog interval

    def track_task(self, task_id: str, user_id: str):
        """Registers a background task for real-time monitoring."""
        self.tracked_tasks[task_id] = user_id
        logger.info(f"Watchdog: Now tracking AI Task {task_id} for user {user_id}")

    async def connect(self, websocket: WebSocket, user_id: str):
...

        self.active_connections.append(websocket)
        self.player_states[user_id] = {
            "pos": [0, 0, 0],
            "rot": [0, 0, 0, 1],
            "active_product": None
        }
        logger.info(f"Presence: User {user_id} connected. Active: {len(self.active_connections)}")

        # Notify others of new arrival
        await self.broadcast({
            "type": "USER_JOINED",
            "user_id": user_id
        })

    def disconnect(self, websocket: WebSocket, user_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.player_states:
            del self.player_states[user_id]
        logger.info(f"Presence: User {user_id} left. Active: {len(self.active_connections)}")

    async def handle_presence_update(self, user_id: str, data: Dict[str, Any]):
        """Updates a user's spatial state and broadcasts to peers."""
        if user_id in self.player_states:
            self.player_states[user_id].update(data)
            await self.broadcast({
                "type": "PRESENCE_UPDATE",
                "user_id": user_id,
                "state": self.player_states[user_id]
            })

    async def broadcast(self, message: Dict[str, Any]):
...

        """Sends a message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")

    async def stream_system_health(self, ai_service: Any):
        """
        Background task to stream real-time pillar health and latency stats.
        """
        while True:
            if self.active_connections:
                try:
                    telemetry = ai_service.get_system_telemetry()
                    await self.broadcast({
                        "type": "SYSTEM_TELEMETRY",
                        "data": telemetry,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                except Exception as e:
                    logger.error(f"Telemetry stream error: {e}")
            await asyncio.sleep(2) # Stream every 2 seconds

    async def send_multisensory_trigger(self, trigger_type: str, payload: Dict[str, Any]):
        """
        Triggers real-time events like haptic probes or audio rustles.
        """
        await self.broadcast({
            "type": "MULTISENSORY_TRIGGER",
            "trigger": trigger_type,
            "payload": payload
        })

manager = ConnectionManager()
