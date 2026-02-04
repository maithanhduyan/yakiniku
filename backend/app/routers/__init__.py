"""
API Routers
"""
from app.routers.bookings import router as bookings_router
from app.routers.customers import router as customers_router
from app.routers.branches import router as branches_router
from app.routers.chat import router as chat_router

__all__ = ["bookings_router", "customers_router", "branches_router", "chat_router"]
