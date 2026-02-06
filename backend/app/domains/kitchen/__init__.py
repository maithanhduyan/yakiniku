"""
Kitchen Domain - Kitchen Display System (KDS)
Team: kitchen
"""
from app.domains.kitchen.router import router
from app.domains.kitchen.event_router import router as event_router

__all__ = ["router", "event_router"]
