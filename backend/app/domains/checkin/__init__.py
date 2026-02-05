"""
Check-in Domain - Customer Reception & Seating
Team: checkin
"""
from app.domains.checkin.router import router
from app.domains.checkin.models import WaitingList, CheckInLog

__all__ = ["router", "WaitingList", "CheckInLog"]
