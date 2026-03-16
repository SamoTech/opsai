import asyncio
import json
import logging
from typing import Dict, Set

import redis as sync_redis
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Per-process in-memory registry — only holds connections for THIS process.
# Cross-process delivery is handled by Redis pub/sub.
_local_connections: Dict[str, Set[WebSocket]] = {}
_subscriber_tasks: Dict[str, asyncio.Task] = {}
_redis_async: aioredis.Redis = None

_REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379")
_CHANNEL_PREFIX = "opsai:project:"


async def _get_async_redis() -> aioredis.Redis:
    global _redis_async
    if _redis_async is None:
        _redis_async = aioredis.from_url(_REDIS_URL, decode_responses=True)
    return _redis_async


async def _redis_subscriber(project_id: str) -> None:
    """Background task: listens on a Redis channel and forwards messages
    to every WebSocket in _local_connections for this process."""
    redis = await _get_async_redis()
    pubsub = redis.pubsub()
    channel = f"{_CHANNEL_PREFIX}{project_id}"
    await pubsub.subscribe(channel)
    logger.info(f"Redis subscriber started for channel {channel}")
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            connections = _local_connections.get(project_id, set())
            dead: Set[WebSocket] = set()
            for ws in list(connections):
                try:
                    await ws.send_text(message["data"])
                except Exception:
                    dead.add(ws)
            connections -= dead
    except asyncio.CancelledError:
        await pubsub.unsubscribe(channel)
        logger.info(f"Redis subscriber cancelled for channel {channel}")
        raise


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str) -> None:
    await websocket.accept()

    if project_id not in _local_connections:
        _local_connections[project_id] = set()
    _local_connections[project_id].add(websocket)
    logger.info(f"WS connected: project={project_id} total={len(_local_connections[project_id])}")

    # Start one Redis subscriber per project per process
    if project_id not in _subscriber_tasks or _subscriber_tasks[project_id].done():
        task = asyncio.create_task(_redis_subscriber(project_id))
        _subscriber_tasks[project_id] = task

    try:
        while True:
            # Keep connection alive; client can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        _local_connections[project_id].discard(websocket)
        logger.info(f"WS disconnected: project={project_id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
        _local_connections[project_id].discard(websocket)
    finally:
        # Cancel subscriber if no more local connections for this project
        if not _local_connections.get(project_id):
            task = _subscriber_tasks.pop(project_id, None)
            if task and not task.done():
                task.cancel()


def broadcast_to_project(project_id: str, message: dict) -> None:
    """Publish a message to all processes via Redis pub/sub.

    Intentionally synchronous — safe to call from Celery workers.
    Uses a short-lived sync Redis connection (no persistent pool needed).
    """
    try:
        client = sync_redis.from_url(_REDIS_URL)
        channel = f"{_CHANNEL_PREFIX}{project_id}"
        client.publish(channel, json.dumps(message))
        client.close()
    except Exception as e:
        logger.warning(f"Redis broadcast failed for project {project_id}: {e}")
