"""
Event Service - Event Sourcing Operations
Handles event logging, querying, and replay
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.domains.tableorder.events import (
    OrderEvent, EventType, EventSource,
    EventCreate, EventResponse, EventListResponse, EventQuery
)


class EventService:
    """Service for event sourcing operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ Event Creation ============

    async def log_event(
        self,
        event_type: EventType,
        branch_code: str,
        event_source: EventSource = EventSource.TABLE_ORDER,
        table_id: Optional[str] = None,
        session_id: Optional[str] = None,
        order_id: Optional[str] = None,
        order_item_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        data: dict = None,
        correlation_id: Optional[str] = None,
        sequence_number: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> OrderEvent:
        """Log a new event to the event store"""
        event = OrderEvent(
            event_type=event_type.value,
            event_source=event_source.value,
            branch_code=branch_code,
            table_id=table_id,
            session_id=session_id,
            order_id=order_id,
            order_item_id=order_item_id,
            actor_type=actor_type,
            actor_id=actor_id,
            data=data or {},
            correlation_id=correlation_id or str(uuid.uuid4()),
            sequence_number=sequence_number or 1,
            error_code=error_code,
            error_message=error_message,
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def log_order_created(
        self,
        order_id: str,
        branch_code: str,
        table_id: str,
        session_id: str,
        items: List[dict],
        source: EventSource = EventSource.TABLE_ORDER
    ) -> str:
        """Log order created event with correlation ID"""
        correlation_id = str(uuid.uuid4())

        await self.log_event(
            event_type=EventType.ORDER_CREATED,
            event_source=source,
            branch_code=branch_code,
            table_id=table_id,
            session_id=session_id,
            order_id=order_id,
            data={
                "items": items,
                "item_count": len(items),
                "total_quantity": sum(i.get("quantity", 1) for i in items)
            },
            correlation_id=correlation_id,
            sequence_number=1
        )

        return correlation_id

    async def log_gateway_sent(
        self,
        order_id: str,
        branch_code: str,
        destination: str,  # "kitchen", "pos", etc.
        correlation_id: str,
        message_data: dict
    ) -> OrderEvent:
        """Log when order is sent to kitchen/POS via WebSocket"""
        # Get next sequence number for this correlation
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_SENT,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={
                "destination": destination,
                "message": message_data
            },
            correlation_id=correlation_id,
            sequence_number=seq
        )

    async def log_gateway_received(
        self,
        order_id: str,
        branch_code: str,
        source: str,  # "kitchen", "pos"
        correlation_id: str
    ) -> OrderEvent:
        """Log acknowledgment from kitchen/POS"""
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_RECEIVED,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={"source": source, "acknowledged_at": datetime.utcnow().isoformat()},
            correlation_id=correlation_id,
            sequence_number=seq
        )

    async def log_gateway_failed(
        self,
        order_id: str,
        branch_code: str,
        destination: str,
        correlation_id: str,
        error_code: str,
        error_message: str
    ) -> OrderEvent:
        """Log failed delivery attempt"""
        seq = await self._get_next_sequence(correlation_id)

        return await self.log_event(
            event_type=EventType.GATEWAY_FAILED,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            data={"destination": destination},
            correlation_id=correlation_id,
            sequence_number=seq,
            error_code=error_code,
            error_message=error_message
        )

    async def log_error(
        self,
        event_type: EventType,
        branch_code: str,
        error_code: str,
        error_message: str,
        context: dict = None,
        order_id: Optional[str] = None,
        session_id: Optional[str] = None,
        table_id: Optional[str] = None
    ) -> OrderEvent:
        """Log an error event"""
        return await self.log_event(
            event_type=event_type,
            event_source=EventSource.SYSTEM,
            branch_code=branch_code,
            order_id=order_id,
            session_id=session_id,
            table_id=table_id,
            data=context or {},
            error_code=error_code,
            error_message=error_message
        )

    # ============ Event Querying ============

    async def get_events(self, query: EventQuery) -> EventListResponse:
        """Query events with filters and pagination"""
        stmt = select(OrderEvent)

        # Apply filters
        conditions = []
        if query.branch_code:
            conditions.append(OrderEvent.branch_code == query.branch_code)
        if query.table_id:
            conditions.append(OrderEvent.table_id == query.table_id)
        if query.session_id:
            conditions.append(OrderEvent.session_id == query.session_id)
        if query.order_id:
            conditions.append(OrderEvent.order_id == query.order_id)
        if query.event_type:
            conditions.append(OrderEvent.event_type == query.event_type)
        if query.event_source:
            conditions.append(OrderEvent.event_source == query.event_source)
        if query.correlation_id:
            conditions.append(OrderEvent.correlation_id == query.correlation_id)
        if query.start_time:
            conditions.append(OrderEvent.timestamp >= query.start_time)
        if query.end_time:
            conditions.append(OrderEvent.timestamp <= query.end_time)
        if query.has_error is True:
            conditions.append(OrderEvent.error_code.isnot(None))
        elif query.has_error is False:
            conditions.append(OrderEvent.error_code.is_(None))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(OrderEvent.timestamp.desc())
        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return EventListResponse(
            events=[EventResponse.model_validate(e) for e in events],
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    async def get_order_timeline(self, order_id: str) -> List[EventResponse]:
        """Get complete timeline of events for an order"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.order_id == order_id)
            .order_by(OrderEvent.timestamp.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_session_timeline(self, session_id: str) -> List[EventResponse]:
        """Get complete timeline of events for a session"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.session_id == session_id)
            .order_by(OrderEvent.timestamp.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_correlation_chain(self, correlation_id: str) -> List[EventResponse]:
        """Get all events in a correlation chain (for tracking delivery)"""
        stmt = (
            select(OrderEvent)
            .where(OrderEvent.correlation_id == correlation_id)
            .order_by(OrderEvent.sequence_number.asc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    # ============ Analytics & Diagnostics ============

    async def get_undelivered_orders(
        self,
        branch_code: str,
        since_minutes: int = 5
    ) -> List[dict]:
        """
        Find orders that were created but not acknowledged by kitchen.
        Use this to detect gateway issues.
        """
        since = datetime.utcnow() - timedelta(minutes=since_minutes)

        # Get all ORDER_CREATED events
        created_stmt = (
            select(OrderEvent)
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.event_type == EventType.ORDER_CREATED.value,
                    OrderEvent.timestamp >= since
                )
            )
        )
        result = await self.db.execute(created_stmt)
        created_events = result.scalars().all()

        undelivered = []
        for event in created_events:
            # Check if there's a corresponding GATEWAY_RECEIVED
            ack_stmt = (
                select(func.count())
                .select_from(OrderEvent)
                .where(
                    and_(
                        OrderEvent.correlation_id == event.correlation_id,
                        OrderEvent.event_type == EventType.GATEWAY_RECEIVED.value
                    )
                )
            )
            ack_count = (await self.db.execute(ack_stmt)).scalar() or 0

            if ack_count == 0:
                undelivered.append({
                    "order_id": event.order_id,
                    "correlation_id": event.correlation_id,
                    "created_at": event.timestamp.isoformat(),
                    "table_id": event.table_id,
                    "session_id": event.session_id,
                    "data": event.data,
                    "minutes_ago": (datetime.utcnow() - event.timestamp.replace(tzinfo=None)).seconds // 60
                })

        return undelivered

    async def get_failed_deliveries(
        self,
        branch_code: str,
        hours: int = 24
    ) -> List[EventResponse]:
        """Get all failed gateway deliveries in the last N hours"""
        since = datetime.utcnow() - timedelta(hours=hours)

        stmt = (
            select(OrderEvent)
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.event_type == EventType.GATEWAY_FAILED.value,
                    OrderEvent.timestamp >= since
                )
            )
            .order_by(OrderEvent.timestamp.desc())
        )

        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [EventResponse.model_validate(e) for e in events]

    async def get_error_summary(
        self,
        branch_code: str,
        hours: int = 24
    ) -> dict:
        """Get summary of errors in the last N hours"""
        since = datetime.utcnow() - timedelta(hours=hours)

        # Count by error type
        stmt = (
            select(
                OrderEvent.event_type,
                OrderEvent.error_code,
                func.count().label("count")
            )
            .where(
                and_(
                    OrderEvent.branch_code == branch_code,
                    OrderEvent.error_code.isnot(None),
                    OrderEvent.timestamp >= since
                )
            )
            .group_by(OrderEvent.event_type, OrderEvent.error_code)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        summary = {
            "total_errors": sum(r.count for r in rows),
            "by_type": {},
            "by_code": {}
        }

        for row in rows:
            # By event type
            if row.event_type not in summary["by_type"]:
                summary["by_type"][row.event_type] = 0
            summary["by_type"][row.event_type] += row.count

            # By error code
            if row.error_code not in summary["by_code"]:
                summary["by_code"][row.error_code] = 0
            summary["by_code"][row.error_code] += row.count

        return summary

    # ============ Helpers ============

    async def _get_next_sequence(self, correlation_id: str) -> int:
        """Get next sequence number for a correlation chain"""
        stmt = (
            select(func.max(OrderEvent.sequence_number))
            .where(OrderEvent.correlation_id == correlation_id)
        )
        result = await self.db.execute(stmt)
        max_seq = result.scalar() or 0
        return max_seq + 1


# ============ Convenience Functions ============

async def log_event(
    db: AsyncSession,
    event_type: EventType,
    branch_code: str,
    **kwargs
) -> OrderEvent:
    """Convenience function to log an event"""
    service = EventService(db)
    return await service.log_event(event_type, branch_code, **kwargs)
