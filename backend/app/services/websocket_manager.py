"""Global WebSocket connection manager and event broadcasting utilities.

Provides a single ConnectionManager instance reused across routers and services
to push real-time updates (sessions, clips, memories, system events).
"""

from typing import Any, Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                # Drop dead connection silently
                self.disconnect(connection)


# Global singleton
manager = ConnectionManager()


async def broadcast_event(event_type: str, payload: Dict[str, Any]):
    """Broadcast a structured event to all clients.

    Args:
        event_type: High-level event category (e.g., 'clip.created').
        payload: Serializable dict payload.
    """
    await manager.broadcast({"type": event_type, "payload": payload})
