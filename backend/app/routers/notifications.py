"""
Notification Router - SSE endpoint for real-time notifications
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
import asyncio

from app.services.notification_service import notification_manager

router = APIRouter()


async def event_generator(request: Request, branch_code: str):
    """Generate SSE events for connected clients"""
    queue = await notification_manager.connect(branch_code)

    try:
        # Send initial connection message
        yield "event: connected\ndata: {\"status\": \"connected\"}\n\n"

        while True:
            # Check if server is shutting down (checked frequently)
            if notification_manager.shutdown_event.is_set():
                yield "event: shutdown\ndata: {\"status\": \"server_shutdown\"}\n\n"
                break

            # Check if client disconnected
            try:
                if await request.is_disconnected():
                    break
            except asyncio.CancelledError:
                # Server shutting down - exit gracefully
                break

            try:
                # Wait for notification with SHORT timeout for responsive shutdown
                notification = await asyncio.wait_for(
                    queue.get(),
                    timeout=1.0  # Check shutdown every 1 second
                )
                # None means shutdown signal
                if notification is None:
                    yield "event: shutdown\ndata: {\"status\": \"server_shutdown\"}\n\n"
                    break
                yield notification.to_sse()
            except asyncio.TimeoutError:
                # Every 30 timeouts (~30 seconds), send keepalive
                pass
            except asyncio.CancelledError:
                # Server shutting down - exit gracefully
                break

    except asyncio.CancelledError:
        # Outer catch for any remaining CancelledError
        pass
    finally:
        try:
            await notification_manager.disconnect(branch_code, queue)
        except asyncio.CancelledError:
            # Ignore CancelledError during cleanup
            pass


@router.get("/stream")
async def notification_stream(
    request: Request,
    branch_code: str = Query(default="hirama"),
):
    """
    SSE endpoint for real-time notifications.

    Connect to this endpoint to receive notifications:
    - new_booking: New booking created
    - booking_cancelled: Booking cancelled
    - booking_confirmed: Booking confirmed
    - vip_arrived: VIP customer arrived

    Usage:
    ```javascript
    const eventSource = new EventSource('/api/notifications/stream?branch_code=JIAN');
    eventSource.onmessage = (event) => {
        const notification = JSON.parse(event.data);
        console.log(notification);
    };
    ```
    """
    return StreamingResponse(
        event_generator(request, branch_code),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/clients")
async def get_connected_clients(
    branch_code: str = Query(default=None),
):
    """Get number of connected notification clients"""
    return {
        "branch_code": branch_code,
        "connected_clients": notification_manager.get_client_count(branch_code),
    }
