from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory connection registry {project_id: [WebSocket]}
_connections: Dict[str, List[WebSocket]] = {}


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str):
    await websocket.accept()
    if project_id not in _connections:
        _connections[project_id] = []
    _connections[project_id].append(websocket)
    logger.info(f"WS connected: project={project_id} total={len(_connections[project_id])}")

    try:
        while True:
            # Keep alive ping every 30s
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        _connections[project_id].remove(websocket)
        logger.info(f"WS disconnected: project={project_id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
        if websocket in _connections.get(project_id, []):
            _connections[project_id].remove(websocket)


async def broadcast_to_project(project_id: str, message: dict):
    """Broadcast a message to all WebSocket clients subscribed to a project."""
    connections = _connections.get(str(project_id), [])
    dead = []
    for ws in connections:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.remove(ws)
