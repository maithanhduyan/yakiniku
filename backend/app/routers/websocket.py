"""
WebSocket Router for Real-time Dashboard Communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections per branch"""

    def __init__(self):
        # branch_code -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> subscribed channels
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, branch_code: str):
        """Accept and register a new connection"""
        await websocket.accept()

        if branch_code not in self.active_connections:
            self.active_connections[branch_code] = set()

        self.active_connections[branch_code].add(websocket)
        self.subscriptions[websocket] = set()

        print(f"📡 WebSocket connected: branch={branch_code}, total={len(self.active_connections[branch_code])}")

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "data": {
                "branch": branch_code,
                "timestamp": datetime.now().isoformat()
            }
        })

    def disconnect(self, websocket: WebSocket, branch_code: str):
        """Remove a connection"""
        if branch_code in self.active_connections:
            self.active_connections[branch_code].discard(websocket)

        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

        print(f"📡 WebSocket disconnected: branch={branch_code}")

    def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe to a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)
            print(f"📡 Subscribed to channel: {channel}")

    def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe from a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Failed to send personal message: {e}")

    async def broadcast_to_branch(self, branch_code: str, message: dict, channel: str = None):
        """Broadcast message to all connections in a branch"""
        if branch_code not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[branch_code]:
            # If channel specified, only send to subscribed connections
            if channel and websocket in self.subscriptions:
                if channel not in self.subscriptions[websocket]:
                    continue

            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected
        for ws in disconnected:
            self.disconnect(ws, branch_code)

    async def broadcast_all(self, message: dict, channel: str = None):
        """Broadcast to all branches"""
        for branch_code in list(self.active_connections.keys()):
            await self.broadcast_to_branch(branch_code, message, channel)

    def get_connection_count(self, branch_code: str = None) -> int:
        """Get number of active connections"""
        if branch_code:
            return len(self.active_connections.get(branch_code, set()))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


@router.websocket("/dashboard")
async def dashboard_websocket(
    websocket: WebSocket,
    branch: str = Query(default="jinan")
):
    """WebSocket endpoint for dashboard real-time updates"""
    await manager.connect(websocket, branch)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "subscribe":
                    channel = message.get("channel")
                    if channel:
                        manager.subscribe(websocket, channel)
                        await manager.send_personal(websocket, {
                            "type": "subscribed",
                            "channel": channel
                        })

                elif msg_type == "unsubscribe":
                    channel = message.get("channel")
                    if channel:
                        manager.unsubscribe(websocket, channel)
                        await manager.send_personal(websocket, {
                            "type": "unsubscribed",
                            "channel": channel
                        })

                elif msg_type == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})

                else:
                    # Handle other message types
                    print(f"📨 Received: {msg_type}")

            except json.JSONDecodeError:
                print(f"❌ Invalid JSON received")

    except WebSocketDisconnect:
        manager.disconnect(websocket, branch)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, branch)


# Helper functions to broadcast events from other parts of the app

async def broadcast_booking_created(branch_code: str, booking: dict):
    """Broadcast new booking event"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "booking:created",
        "data": booking,
        "channel": "bookings"
    }, channel="bookings")


async def broadcast_booking_updated(branch_code: str, booking: dict):
    """Broadcast booking update event"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "booking:updated",
        "data": booking,
        "channel": "bookings"
    }, channel="bookings")


async def broadcast_table_status(branch_code: str, table: dict):
    """Broadcast table status change"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "table:status",
        "data": table,
        "channel": "tables"
    }, channel="tables")


async def broadcast_notification(branch_code: str, title: str, message: str):
    """Broadcast notification"""
    await manager.broadcast_to_branch(branch_code, {
        "type": "notification",
        "data": {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    })
