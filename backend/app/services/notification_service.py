"""
Notification Service - Real-time notifications using SSE
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class NotificationType(str, Enum):
    NEW_BOOKING = "new_booking"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_CONFIRMED = "booking_confirmed"
    VIP_ARRIVED = "vip_arrived"
    CHAT_MESSAGE = "chat_message"


@dataclass
class Notification:
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_sse(self) -> str:
        """Format as SSE event"""
        payload = {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "data": self.data or {},
            "timestamp": self.timestamp,
        }
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


class NotificationManager:
    """
    Manages SSE connections and broadcasts notifications to connected clients.
    Each branch can have multiple connected staff members.
    """

    def __init__(self):
        # branch_code -> set of asyncio.Queue for each connected client
        self._clients: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()

    @property
    def shutdown_event(self) -> asyncio.Event:
        """Get the shutdown event for SSE connections to check"""
        return self._shutdown_event

    async def shutdown(self):
        """Signal all SSE connections to close gracefully"""
        print("ðŸ“¡ Shutting down SSE connections...")
        self._shutdown_event.set()

        # Send shutdown signal to all queues
        async with self._lock:
            for branch_code, clients in self._clients.items():
                for queue in clients:
                    try:
                        # Put None to signal shutdown
                        await queue.put(None)
                    except Exception:
                        pass
            # Clear all clients
            self._clients.clear()

        print("ðŸ“¡ All SSE connections closed")

    async def connect(self, branch_code: str) -> asyncio.Queue:
        """Register a new SSE client connection"""
        queue = asyncio.Queue()

        async with self._lock:
            if branch_code not in self._clients:
                self._clients[branch_code] = set()
            self._clients[branch_code].add(queue)

        print(f"ðŸ“¡ SSE client connected for branch: {branch_code} (total: {len(self._clients[branch_code])})")
        return queue

    async def disconnect(self, branch_code: str, queue: asyncio.Queue):
        """Remove a client connection"""
        async with self._lock:
            if branch_code in self._clients:
                self._clients[branch_code].discard(queue)
                if not self._clients[branch_code]:
                    del self._clients[branch_code]

        print(f"ðŸ“¡ SSE client disconnected from branch: {branch_code}")

    async def broadcast(self, branch_code: str, notification: Notification):
        """Send notification to all connected clients for a branch"""
        async with self._lock:
            clients = self._clients.get(branch_code, set()).copy()

        if not clients:
            print(f"ðŸ“¡ No clients connected for branch: {branch_code}")
            return

        print(f"ðŸ“¡ Broadcasting to {len(clients)} clients: {notification.title}")

        for queue in clients:
            try:
                await queue.put(notification)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

    async def broadcast_all(self, notification: Notification):
        """Broadcast to all connected clients across all branches"""
        async with self._lock:
            all_clients = []
            for clients in self._clients.values():
                all_clients.extend(clients)

        for queue in all_clients:
            try:
                await queue.put(notification)
            except Exception as e:
                print(f"Error broadcasting: {e}")

    def get_client_count(self, branch_code: str = None) -> int:
        """Get number of connected clients"""
        if branch_code:
            return len(self._clients.get(branch_code, set()))
        return sum(len(clients) for clients in self._clients.values())


# Singleton instance
notification_manager = NotificationManager()


# ============================================
# HELPER FUNCTIONS
# ============================================

async def notify_new_booking(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    guests: int,
    booking_id: str = None,
    table_number: str = None,
):
    """Send notification for new booking"""
    message = f"{guest_name}æ§˜ {guests}åæ§˜ - {booking_date} {booking_time}"
    if table_number:
        message += f" ({table_number})"

    notification = Notification(
        type=NotificationType.NEW_BOOKING,
        title="ðŸ”” æ–°è¦äºˆç´„",
        message=message,
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
            "guests": guests,
            "table_number": table_number,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_booking_cancelled(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    booking_id: str = None,
):
    """Send notification for cancelled booking"""
    notification = Notification(
        type=NotificationType.BOOKING_CANCELLED,
        title="âŒ äºˆç´„ã‚­ãƒ£ãƒ³ã‚»ãƒ«",
        message=f"{guest_name}æ§˜ - {booking_date} {booking_time}",
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_booking_confirmed(
    branch_code: str,
    guest_name: str,
    booking_date: str,
    booking_time: str,
    booking_id: str = None,
):
    """Send notification for confirmed booking"""
    notification = Notification(
        type=NotificationType.BOOKING_CONFIRMED,
        title="âœ… äºˆç´„ç¢ºèªå®Œäº†",
        message=f"{guest_name}æ§˜ - {booking_date} {booking_time}",
        data={
            "booking_id": booking_id,
            "guest_name": guest_name,
            "date": booking_date,
            "time": booking_time,
        }
    )
    await notification_manager.broadcast(branch_code, notification)


async def notify_vip_arrived(
    branch_code: str,
    customer_name: str,
    preferences: List[str] = None,
):
    """Send notification when VIP customer arrives"""
    notification = Notification(
        type=NotificationType.VIP_ARRIVED,
        title="â­ VIPæ¥åº—",
        message=f"{customer_name}æ§˜ãŒã”æ¥åº—ã§ã™",
        data={
            "customer_name": customer_name,
            "preferences": preferences or [],
        }
    )
    await notification_manager.broadcast(branch_code, notification)

