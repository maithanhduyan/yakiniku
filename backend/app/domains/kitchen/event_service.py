"""
Kitchen Event Service - Event Sourcing Operations for Kitchen Domain
Handles logging kitchen staff actions and querying history
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.domains.kitchen.events import (
    KitchenEvent, KitchenEventType, KitchenEventSource,
    KitchenEventCreate, KitchenEventResponse, KitchenHistoryResponse
)


class KitchenEventService:
    """Service for kitchen event sourcing"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ Event Creation ============

    async def log_event(
        self,
        event_type: KitchenEventType,
        branch_code: str,
        event_source: KitchenEventSource = KitchenEventSource.KITCHEN_DISPLAY,
        table_id: Optional[str] = None,
        table_number: Optional[str] = None,
        session_id: Optional[str] = None,
        order_id: Optional[str] = None,
        order_item_id: Optional[str] = None,
        item_name: Optional[str] = None,
        item_quantity: Optional[int] = None,
        station: Optional[str] = None,
        actor_type: Optional[str] = "staff",
        actor_id: Optional[str] = None,
        data: dict = None,
        wait_time_seconds: Optional[int] = None,
    ) -> KitchenEvent:
        """Log a new kitchen event"""
        event = KitchenEvent(
            event_type=event_type.value,
            event_source=event_source.value,
            branch_code=branch_code,
            table_id=table_id,
            table_number=table_number,
            session_id=session_id,
            order_id=order_id,
            order_item_id=order_item_id,
            item_name=item_name,
            item_quantity=item_quantity,
            station=station,
            actor_type=actor_type,
            actor_id=actor_id,
            data=data or {},
            wait_time_seconds=wait_time_seconds,
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def log_item_served(
        self,
        branch_code: str,
        order_id: str,
        order_item_id: str,
        item_name: str,
        item_quantity: int,
        table_number: str,
        station: str,
        wait_time_seconds: int = 0,
        table_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> KitchenEvent:
        """Log item served/completed by kitchen staff"""
        return await self.log_event(
            event_type=KitchenEventType.ITEM_SERVED,
            branch_code=branch_code,
            order_id=order_id,
            order_item_id=order_item_id,
            item_name=item_name,
            item_quantity=item_quantity,
            table_number=table_number,
            station=station,
            table_id=table_id,
            session_id=session_id,
            wait_time_seconds=wait_time_seconds,
            data={"action": "served"},
        )

    async def log_item_cancelled(
        self,
        branch_code: str,
        order_id: str,
        order_item_id: str,
        item_name: str,
        item_quantity: int,
        table_number: str,
        station: str,
        reason: str = "",
        source: KitchenEventSource = KitchenEventSource.KITCHEN_DISPLAY,
        wait_time_seconds: int = 0,
        table_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> KitchenEvent:
        """Log item cancelled"""
        return await self.log_event(
            event_type=KitchenEventType.ITEM_CANCELLED,
            event_source=source,
            branch_code=branch_code,
            order_id=order_id,
            order_item_id=order_item_id,
            item_name=item_name,
            item_quantity=item_quantity,
            table_number=table_number,
            station=station,
            table_id=table_id,
            session_id=session_id,
            wait_time_seconds=wait_time_seconds,
            data={"action": "cancelled", "reason": reason},
        )

    async def log_from_create(self, event_data: KitchenEventCreate) -> KitchenEvent:
        """Log event from frontend-submitted data"""
        return await self.log_event(
            event_type=event_data.event_type,
            event_source=event_data.event_source,
            branch_code=event_data.branch_code,
            table_id=event_data.table_id,
            table_number=event_data.table_number,
            session_id=event_data.session_id,
            order_id=event_data.order_id,
            order_item_id=event_data.order_item_id,
            item_name=event_data.item_name,
            item_quantity=event_data.item_quantity,
            station=event_data.station,
            actor_type=event_data.actor_type,
            actor_id=event_data.actor_id,
            data=event_data.data,
            wait_time_seconds=event_data.wait_time_seconds,
        )

    # ============ Event Querying ============

    async def get_history(
        self,
        branch_code: str,
        station: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        since_hours: int = 24,
    ) -> KitchenHistoryResponse:
        """Get kitchen event history with optional filters"""
        since = datetime.utcnow() - timedelta(hours=since_hours)

        # Base query
        stmt = select(KitchenEvent).where(
            and_(
                KitchenEvent.branch_code == branch_code,
                KitchenEvent.timestamp >= since,
            )
        )

        # Apply filters
        if station and station != "all":
            stmt = stmt.where(KitchenEvent.station == station)

        if event_type:
            stmt = stmt.where(KitchenEvent.event_type == event_type)
        else:
            # By default, show served and cancelled events (the main history items)
            stmt = stmt.where(
                KitchenEvent.event_type.in_([
                    KitchenEventType.ITEM_SERVED.value,
                    KitchenEventType.ITEM_CANCELLED.value,
                ])
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # Get events (newest first)
        stmt = stmt.order_by(desc(KitchenEvent.timestamp)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        # Build summary
        summary = await self._build_summary(branch_code, since, station)

        return KitchenHistoryResponse(
            events=[KitchenEventResponse.model_validate(e) for e in events],
            total=total,
            summary=summary,
        )

    async def _build_summary(
        self,
        branch_code: str,
        since: datetime,
        station: Optional[str] = None,
    ) -> dict:
        """Build summary stats for history"""
        base_cond = and_(
            KitchenEvent.branch_code == branch_code,
            KitchenEvent.timestamp >= since,
        )
        if station and station != "all":
            base_cond = and_(base_cond, KitchenEvent.station == station)

        # Count served
        served_stmt = select(func.count()).where(
            and_(base_cond, KitchenEvent.event_type == KitchenEventType.ITEM_SERVED.value)
        )
        served_result = await self.db.execute(served_stmt)
        served = served_result.scalar() or 0

        # Count cancelled
        cancelled_stmt = select(func.count()).where(
            and_(base_cond, KitchenEvent.event_type == KitchenEventType.ITEM_CANCELLED.value)
        )
        cancelled_result = await self.db.execute(cancelled_stmt)
        cancelled = cancelled_result.scalar() or 0

        # Average wait time for served items
        avg_stmt = select(func.avg(KitchenEvent.wait_time_seconds)).where(
            and_(
                base_cond,
                KitchenEvent.event_type == KitchenEventType.ITEM_SERVED.value,
                KitchenEvent.wait_time_seconds.isnot(None),
            )
        )
        avg_result = await self.db.execute(avg_stmt)
        avg_wait = avg_result.scalar()

        return {
            "served_count": served,
            "cancelled_count": cancelled,
            "avg_wait_seconds": round(avg_wait) if avg_wait else 0,
        }
