"""
Booking Models - Re-export from legacy models with extensions
"""
# Re-export from legacy models
from app.models.booking import Booking, BookingStatus

# Add new fields to existing model using mixin approach
# For now, we'll add qr_token and check-in fields via migration later

__all__ = ["Booking", "BookingStatus"]

