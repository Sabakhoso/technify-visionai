"""
WebSocket connection manager and live broadcasting for dashboard events.
Supports real-time alerts, camera status, and detection updates.
"""

import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("technify_visionai.websockets")

ws_router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    def __init__(self):
        # Map channel names to sets of connected WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket client connected to channel '{channel}'")
        # Send initial status handshake
        await websocket.send_json({
            "type": "connection_established",
            "channel": channel,
            "status": "connected"
        })

    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info(f"WebSocket client disconnected from channel '{channel}'")

    async def broadcast(self, channel: str, message: dict):
        connections = self.active_connections.get(channel, set()).copy()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection, channel)

    async def broadcast_all(self, message: dict):
        for channel in list(self.active_connections.keys()):
            await self.broadcast(channel, message)


manager = ConnectionManager()


async def handle_websocket_loop(websocket: WebSocket, channel: str):
    await manager.connect(websocket, channel)
    try:
        while True:
            # Keep connection open, handle client heartbeats or messages
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
    except Exception as e:
        logger.debug(f"WebSocket loop terminated: {e}")
        manager.disconnect(websocket, channel)


@ws_router.websocket("/ws/{channel}")
async def websocket_channel_endpoint(websocket: WebSocket, channel: str):
    await handle_websocket_loop(websocket, channel)


@ws_router.websocket("/ws")
async def websocket_root_endpoint(websocket: WebSocket):
    await handle_websocket_loop(websocket, "general")


@ws_router.websocket("/{channel}")
async def websocket_direct_channel_endpoint(websocket: WebSocket, channel: str):
    await handle_websocket_loop(websocket, channel)

