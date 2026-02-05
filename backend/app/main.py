"""
FastAPI Application Entry Point
"""
import signal
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.services.notification_service import notification_manager


def setup_signal_handlers():
    """Setup signal handlers to gracefully shutdown SSE before uvicorn"""
    import sys
    import time

    def sync_shutdown_handler(signum, frame):
        """Synchronous signal handler that triggers async shutdown"""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        # Set the shutdown event synchronously - SSE generators will exit on next check
        notification_manager._shutdown_event.set()

        # Give SSE connections 2 seconds to close gracefully
        print("⏳ Waiting for SSE connections to close...")
        time.sleep(2)

        # Now raise KeyboardInterrupt to let uvicorn shutdown
        raise KeyboardInterrupt

    # Register signal handlers
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, sync_shutdown_handler)
    signal.signal(signal.SIGINT, sync_shutdown_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Setup signal handlers early
    setup_signal_handlers()

    # Startup: Initialize database
    await init_db()
    print("🍖 Database initialized")
    yield
    # Shutdown: Close SSE connections first
    print("👋 Shutting down...")
    await notification_manager.shutdown()
    print("✅ Graceful shutdown complete")


app = FastAPI(
    title="Yakiniku Jinan API",
    description="Restaurant booking and customer insights API",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files for dashboard
app.mount("/static", StaticFiles(directory="../dashboard/static"), name="static")

# Static files for menu images (backend serves images)
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# CORS - allow web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Yakiniku Jinan API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============ Legacy Routers (backward compatibility) ============
from app.routers import bookings, customers, branches, chat, dashboard, notifications, tables, menu, orders

app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(branches.router, prefix="/api/branches", tags=["branches"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(tables.router, prefix="/api/tables", tags=["tables"])
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(dashboard.router, prefix="/admin", tags=["dashboard"])

# ============ Domain Routers (new modular structure) ============
# Team: web
from app.domains.booking.router import router as booking_router
app.include_router(booking_router, prefix="/api/booking", tags=["booking-domain"])

# Team: table-order
from app.domains.order.router import router as order_router
app.include_router(order_router, prefix="/api/order", tags=["order-domain"])

# Team: kitchen
from app.domains.kitchen.router import router as kitchen_router
app.include_router(kitchen_router, prefix="/api/kitchen", tags=["kitchen-domain"])

# Team: pos
from app.domains.pos.router import router as pos_router
app.include_router(pos_router, prefix="/api/pos", tags=["pos-domain"])

# Team: checkin
from app.domains.checkin.router import router as checkin_router
app.include_router(checkin_router, prefix="/api/checkin", tags=["checkin-domain"])
