"""
AI Table Optimization Service
Tá»‘i Æ°u hÃ³a viá»‡c xáº¿p bÃ n vÃ  quáº£n lÃ½ capacity nhÃ  hÃ ng
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload

from app.models.table import Table, TableAssignment, TableStatus
from app.models.booking import Booking, BookingStatus


class OptimizationStrategy(str, Enum):
    """Chiáº¿n lÆ°á»£c tá»‘i Æ°u hÃ³a"""
    MAXIMIZE_CAPACITY = "maximize_capacity"      # Tá»‘i Ä‘a sá»‘ khÃ¡ch
    MINIMIZE_WASTE = "minimize_waste"            # Giáº£m lÃ£ng phÃ­ gháº¿
    VIP_PRIORITY = "vip_priority"                # Æ¯u tiÃªn VIP
    QUICK_TURNOVER = "quick_turnover"            # Tá»‘i Ä‘a vÃ²ng quay bÃ n


@dataclass
class TableSlot:
    """ThÃ´ng tin 1 slot thá»i gian cá»§a bÃ n"""
    table_id: str
    table_number: str
    max_capacity: int
    time_slot: str
    is_available: bool
    booking_id: Optional[str] = None
    guests: int = 0


@dataclass
class TimeSlotSummary:
    """Tá»•ng há»£p tÃ¬nh tráº¡ng 1 khung giá»"""
    time_slot: str
    total_tables: int
    available_tables: int
    occupied_tables: int
    total_capacity: int
    used_capacity: int
    available_capacity: int
    utilization_rate: float  # 0-100%
    tables: List[TableSlot] = field(default_factory=list)


@dataclass
class TableSuggestion:
    """Äá» xuáº¥t bÃ n cho booking"""
    table_id: str
    table_number: str
    capacity: int
    score: float  # 0-100, Ä‘iá»ƒm phÃ¹ há»£p
    reason: str
    waste: int  # Sá»‘ gháº¿ thá»«a


@dataclass
class OptimizationInsight:
    """Insight tá»« AI vá» tÃ¬nh tráº¡ng nhÃ  hÃ ng"""
    type: str  # "warning", "suggestion", "opportunity"
    title: str
    message: str
    priority: int  # 1-5
    action: Optional[str] = None
    data: Optional[Dict] = None


class TableOptimizationService:
    """
    AI Service Ä‘á»ƒ tá»‘i Æ°u hÃ³a viá»‡c xáº¿p bÃ n

    Features:
    1. Äá» xuáº¥t bÃ n phÃ¹ há»£p cho sá»‘ khÃ¡ch
    2. Cáº£nh bÃ¡o khi sáº¯p full
    3. Gá»£i Ã½ thá»i gian thay tháº¿
    4. PhÃ¢n tÃ­ch utilization
    """

    # Thá»i gian trung bÃ¬nh 1 bá»¯a Äƒn (phÃºt)
    AVERAGE_DINING_TIME = 90

    # Thá»i gian buffer giá»¯a cÃ¡c booking (phÃºt)
    TURNOVER_BUFFER = 30

    # Slot duration (phÃºt)
    SLOT_DURATION = 30

    def __init__(self, db: AsyncSession, branch_code: str):
        self.db = db
        self.branch_code = branch_code

    # ==========================================
    # CORE: TÃ¬m bÃ n phÃ¹ há»£p
    # ==========================================

    async def find_best_tables(
        self,
        guests: int,
        booking_date: date,
        time_slot: str,
        strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_WASTE
    ) -> List[TableSuggestion]:
        """
        TÃ¬m bÃ n phÃ¹ há»£p nháº¥t cho sá»‘ khÃ¡ch

        Strategy:
        - MINIMIZE_WASTE: Chá»n bÃ n cÃ³ capacity gáº§n nháº¥t vá»›i sá»‘ khÃ¡ch
        - MAXIMIZE_CAPACITY: Æ¯u tiÃªn bÃ n lá»›n Ä‘á»ƒ cÃ³ chá»— náº¿u khÃ¡ch thÃªm
        - VIP_PRIORITY: Æ¯u tiÃªn bÃ n VIP/private
        """
        # Láº¥y táº¥t cáº£ bÃ n available cho slot nÃ y
        available_tables = await self._get_available_tables(booking_date, time_slot)

        if not available_tables:
            return []

        suggestions = []

        for table in available_tables:
            # Bá» qua bÃ n quÃ¡ nhá»
            if table.max_capacity < guests:
                continue

            # TÃ­nh Ä‘iá»ƒm dá»±a trÃªn strategy
            score, reason = self._calculate_table_score(
                table, guests, strategy
            )

            waste = table.max_capacity - guests

            suggestions.append(TableSuggestion(
                table_id=table.id,
                table_number=table.table_number,
                capacity=table.max_capacity,
                score=score,
                reason=reason,
                waste=waste
            ))

        # Sáº¯p xáº¿p theo score giáº£m dáº§n
        suggestions.sort(key=lambda x: x.score, reverse=True)

        return suggestions[:5]  # Top 5 Ä‘á» xuáº¥t

    def _calculate_table_score(
        self,
        table: Table,
        guests: int,
        strategy: OptimizationStrategy
    ) -> Tuple[float, str]:
        """TÃ­nh Ä‘iá»ƒm phÃ¹ há»£p cá»§a bÃ n"""
        base_score = 100.0
        reason_parts = []

        waste = table.max_capacity - guests

        if strategy == OptimizationStrategy.MINIMIZE_WASTE:
            # Giáº£m Ä‘iá»ƒm theo sá»‘ gháº¿ thá»«a
            waste_penalty = waste * 10
            base_score -= waste_penalty

            if waste == 0:
                reason_parts.append("å®Œç’§ã«ãƒžãƒƒãƒ")
            elif waste <= 2:
                reason_parts.append(f"ä½™ã‚Š{waste}å¸­")
            else:
                reason_parts.append(f"ä½™ã‚Š{waste}å¸­(å¤§ãã‚)")

        elif strategy == OptimizationStrategy.MAXIMIZE_CAPACITY:
            # Æ¯u tiÃªn bÃ n lá»›n hÆ¡n
            capacity_bonus = table.max_capacity * 5
            base_score += capacity_bonus
            reason_parts.append(f"æœ€å¤§{table.max_capacity}åã¾ã§å¯¾å¿œ")

        # Bonus cho cÃ¡c features
        if table.table_type == "private":
            base_score += 15
            reason_parts.append("å€‹å®¤")

        if table.has_window:
            base_score += 5
            reason_parts.append("çª“éš›")

        # Priority bonus
        base_score += table.priority * 2

        reason = "ã€".join(reason_parts) if reason_parts else "æ¨™æº–å¸­"

        return max(0, min(100, base_score)), reason

    async def _get_available_tables(
        self,
        booking_date: date,
        time_slot: str
    ) -> List[Table]:
        """Láº¥y danh sÃ¡ch bÃ n cÃ²n trá»‘ng cho slot"""
        # Láº¥y táº¥t cáº£ bÃ n cá»§a branch
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = tables_result.scalars().all()

        # Láº¥y cÃ¡c bÃ n Ä‘Ã£ Ä‘Æ°á»£c assign cho slot nÃ y
        booked_tables_query = select(TableAssignment.table_id).join(
            Booking
        ).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == booking_date,
                Booking.time == time_slot,
                Booking.status.in_(["pending", "confirmed"])
            )
        )
        booked_result = await self.db.execute(booked_tables_query)
        booked_table_ids = {r[0] for r in booked_result.fetchall()}

        # Lá»c ra bÃ n cÃ²n trá»‘ng
        available = [t for t in all_tables if t.id not in booked_table_ids]

        return available

    # ==========================================
    # AVAILABILITY CHECK
    # ==========================================

    async def check_availability(
        self,
        guests: int,
        booking_date: date,
        time_slot: str
    ) -> Dict[str, Any]:
        """
        Kiá»ƒm tra xem cÃ³ thá»ƒ Ä‘áº·t bÃ n khÃ´ng

        Returns:
            {
                "available": True/False,
                "tables": [TableSuggestion],
                "alternatives": [{"time": "18:30", "tables": [...]}],
                "message": "..."
            }
        """
        suggestions = await self.find_best_tables(guests, booking_date, time_slot)

        if suggestions:
            return {
                "available": True,
                "tables": suggestions,
                "alternatives": [],
                "message": f"{len(suggestions)}å¸­ã”æ¡ˆå†…å¯èƒ½ã§ã™"
            }

        # KhÃ´ng cÃ³ bÃ n -> tÃ¬m alternatives
        alternatives = await self._find_alternative_slots(guests, booking_date, time_slot)

        return {
            "available": False,
            "tables": [],
            "alternatives": alternatives,
            "message": "ç”³ã—è¨³ã”ã–ã„ã¾ã›ã‚“ã€ã”å¸Œæœ›ã®æ™‚é–“ã¯æº€å¸­ã§ã™ã€‚" +
                      (f"ä»£ã‚ã‚Šã«{len(alternatives)}ã¤ã®æ™‚é–“å¸¯ãŒã”ã–ã„ã¾ã™ã€‚" if alternatives else "")
        }

    async def _find_alternative_slots(
        self,
        guests: int,
        booking_date: date,
        requested_slot: str,
        range_hours: int = 2
    ) -> List[Dict]:
        """TÃ¬m cÃ¡c slot thay tháº¿ trong vÃ²ng Â±range_hours"""
        alternatives = []

        # Parse requested time
        req_hour, req_min = map(int, requested_slot.split(":"))
        req_minutes = req_hour * 60 + req_min

        # Generate slots to check
        all_slots = [
            f"{h:02d}:{m:02d}"
            for h in range(17, 23)
            for m in [0, 30]
            if not (h == 22 and m == 30)
        ]

        for slot in all_slots:
            if slot == requested_slot:
                continue

            # Check if within range
            slot_hour, slot_min = map(int, slot.split(":"))
            slot_minutes = slot_hour * 60 + slot_min

            if abs(slot_minutes - req_minutes) > range_hours * 60:
                continue

            # Check availability
            tables = await self.find_best_tables(guests, booking_date, slot)

            if tables:
                alternatives.append({
                    "time": slot,
                    "tables": tables[:2],  # Top 2
                    "diff_minutes": slot_minutes - req_minutes
                })

        # Sort by closest to requested time
        alternatives.sort(key=lambda x: abs(x["diff_minutes"]))

        return alternatives[:5]  # Top 5 alternatives

    # ==========================================
    # ANALYTICS & INSIGHTS
    # ==========================================

    async def get_time_slot_summary(
        self,
        target_date: date
    ) -> List[TimeSlotSummary]:
        """Tá»•ng há»£p tÃ¬nh tráº¡ng táº¥t cáº£ cÃ¡c slot trong ngÃ y"""
        # Láº¥y táº¥t cáº£ bÃ n
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = list(tables_result.scalars().all())

        total_capacity = sum(t.max_capacity for t in all_tables)

        # Láº¥y táº¥t cáº£ booking trong ngÃ y
        bookings_query = select(Booking).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == target_date,
                Booking.status.in_(["pending", "confirmed"])
            )
        )
        bookings_result = await self.db.execute(bookings_query)
        bookings = list(bookings_result.scalars().all())

        # Group bookings by time
        bookings_by_time: Dict[str, List[Booking]] = {}
        for b in bookings:
            if b.time not in bookings_by_time:
                bookings_by_time[b.time] = []
            bookings_by_time[b.time].append(b)

        # Generate all slots
        all_slots = [
            f"{h:02d}:{m:02d}"
            for h in range(17, 23)
            for m in [0, 30]
            if not (h == 22 and m == 30)
        ]

        summaries = []

        for slot in all_slots:
            slot_bookings = bookings_by_time.get(slot, [])
            used_capacity = sum(b.guests for b in slot_bookings)
            available_capacity = total_capacity - used_capacity

            occupied = len(slot_bookings)
            available = len(all_tables) - occupied

            utilization = (used_capacity / total_capacity * 100) if total_capacity > 0 else 0

            summaries.append(TimeSlotSummary(
                time_slot=slot,
                total_tables=len(all_tables),
                available_tables=available,
                occupied_tables=occupied,
                total_capacity=total_capacity,
                used_capacity=used_capacity,
                available_capacity=available_capacity,
                utilization_rate=round(utilization, 1),
                tables=[]  # Populate if needed
            ))

        return summaries

    async def generate_insights(
        self,
        target_date: date
    ) -> List[OptimizationInsight]:
        """
        Táº¡o insights vÃ  suggestions cho staff

        Examples:
        - "20:00 sáº¯p full (7/8 bÃ n), cÃ¢n nháº¯c tá»« chá»‘i booking má»›i"
        - "18:00 cÃ²n nhiá»u bÃ n 6 gháº¿, khÃ¡ch 2 ngÆ°á»i nÃªn chuyá»ƒn sang 4 gháº¿"
        - "HÃ´m nay cÃ³ 3 VIP, Ä‘Ã£ reserve phÃ²ng riÃªng"
        """
        insights = []

        # Get slot summaries
        summaries = await self.get_time_slot_summary(target_date)

        for summary in summaries:
            # Warning: Sáº¯p full
            if summary.utilization_rate >= 80:
                insights.append(OptimizationInsight(
                    type="warning",
                    title=f"âš ï¸ {summary.time_slot} æ··é›‘æ³¨æ„",
                    message=f"åˆ©ç”¨çŽ‡{summary.utilization_rate}% - æ®‹ã‚Š{summary.available_tables}å¸­",
                    priority=4 if summary.utilization_rate >= 90 else 3,
                    action="æ–°è¦äºˆç´„ã‚’æŽ§ãˆã‚‹ã‹ã€ä»£æ›¿æ™‚é–“ã‚’ã”æ¡ˆå†…ãã ã•ã„",
                    data={
                        "time_slot": summary.time_slot,
                        "utilization": summary.utilization_rate,
                        "available": summary.available_tables
                    }
                ))

            # Opportunity: Slot trá»‘ng
            elif summary.utilization_rate < 30 and summary.time_slot >= "18:00":
                insights.append(OptimizationInsight(
                    type="opportunity",
                    title=f"ðŸ“ˆ {summary.time_slot} ç©ºãå¤šã‚",
                    message=f"åˆ©ç”¨çŽ‡{summary.utilization_rate}% - {summary.available_tables}å¸­ç©ºã",
                    priority=2,
                    action="ãƒ—ãƒ­ãƒ¢ãƒ¼ã‚·ãƒ§ãƒ³ã‚„äºˆç´„è»¢æ›ã®æ©Ÿä¼š",
                    data={
                        "time_slot": summary.time_slot,
                        "available": summary.available_tables
                    }
                ))

        # Check for table waste (big table for small group)
        waste_insights = await self._check_capacity_waste(target_date)
        insights.extend(waste_insights)

        # Sort by priority
        insights.sort(key=lambda x: x.priority, reverse=True)

        return insights

    async def _check_capacity_waste(
        self,
        target_date: date
    ) -> List[OptimizationInsight]:
        """Kiá»ƒm tra lÃ£ng phÃ­ capacity"""
        insights = []

        # Láº¥y bookings vá»›i table assignment
        query = select(Booking, TableAssignment, Table).join(
            TableAssignment, Booking.id == TableAssignment.booking_id
        ).join(
            Table, TableAssignment.table_id == Table.id
        ).where(
            and_(
                Booking.branch_code == self.branch_code,
                Booking.date == target_date,
                Booking.status.in_(["pending", "confirmed"])
            )
        )

        result = await self.db.execute(query)
        rows = result.fetchall()

        waste_cases = []

        for booking, assignment, table in rows:
            waste = table.max_capacity - booking.guests
            if waste >= 3:  # 3+ gháº¿ thá»«a
                waste_cases.append({
                    "booking": booking,
                    "table": table,
                    "waste": waste
                })

        if waste_cases:
            total_waste = sum(c["waste"] for c in waste_cases)
            insights.append(OptimizationInsight(
                type="suggestion",
                title=f"ðŸ’¡ å¸­åŠ¹çŽ‡ã®æ”¹å–„å¯èƒ½",
                message=f"{len(waste_cases)}ä»¶ã®äºˆç´„ã§åˆè¨ˆ{total_waste}å¸­ã®ä½™è£•ã‚ã‚Š",
                priority=2,
                action="å°ã•ã„å¸­ã¸ã®å¤‰æ›´ã‚’æ¤œè¨Ž",
                data={
                    "waste_cases": [
                        {
                            "time": c["booking"].time,
                            "guests": c["booking"].guests,
                            "table": c["table"].table_number,
                            "capacity": c["table"].max_capacity
                        }
                        for c in waste_cases
                    ]
                }
            ))

        return insights

    # ==========================================
    # TABLE ASSIGNMENT
    # ==========================================

    async def auto_assign_table(
        self,
        booking_id: str,
        guests: int,
        booking_date: date,
        time_slot: str
    ) -> Optional[TableAssignment]:
        """Tá»± Ä‘á»™ng assign bÃ n cho booking"""
        suggestions = await self.find_best_tables(guests, booking_date, time_slot)

        if not suggestions:
            return None

        best_table = suggestions[0]

        # Create assignment
        assignment = TableAssignment(
            booking_id=booking_id,
            table_id=best_table.table_id,
            notes=f"Auto-assigned: {best_table.reason}"
        )

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)

        return assignment

    async def reassign_table(
        self,
        booking_id: str,
        new_table_id: str,
        reason: str = ""
    ) -> Optional[TableAssignment]:
        """Äá»•i bÃ n cho booking"""
        # Delete old assignment
        old_query = select(TableAssignment).where(
            TableAssignment.booking_id == booking_id
        )
        old_result = await self.db.execute(old_query)
        old_assignment = old_result.scalar_one_or_none()

        if old_assignment:
            await self.db.delete(old_assignment)

        # Create new assignment
        new_assignment = TableAssignment(
            booking_id=booking_id,
            table_id=new_table_id,
            notes=f"Reassigned: {reason}"
        )

        self.db.add(new_assignment)
        await self.db.commit()
        await self.db.refresh(new_assignment)

        return new_assignment

    # ==========================================
    # GANTT CHART DATA
    # ==========================================

    async def get_gantt_data(
        self,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Get data for Gantt chart visualization

        Returns:
        - tables: List of tables with their bookings
        - time_slots: List of time slots (17:00-22:00)
        - bookings_map: Dict mapping table_id -> list of booking blocks
        """
        # Get all tables
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        ).order_by(Table.zone, Table.table_number)
        tables_result = await self.db.execute(tables_query)
        tables = tables_result.scalars().all()

        # Get all bookings for the date
        bookings_query = (
            select(Booking)
            .options(selectinload(Booking.table_assignments))
            .where(
                and_(
                    Booking.branch_code == self.branch_code,
                    Booking.date == target_date,
                    Booking.status.not_in([BookingStatus.CANCELLED, BookingStatus.NO_SHOW])
                )
            )
            .order_by(Booking.time)
        )
        bookings_result = await self.db.execute(bookings_query)
        bookings = bookings_result.scalars().all()

        # Time slots from 17:00 to 22:30 (30 min intervals)
        time_slots = []
        start_hour = 17
        end_hour = 23
        for hour in range(start_hour, end_hour):
            time_slots.append(f"{hour:02d}:00")
            if hour < end_hour - 1 or (hour == end_hour - 1 and hour == 22):
                time_slots.append(f"{hour:02d}:30")

        # Build bookings map by table
        bookings_by_table: Dict[str, List[Dict]] = {str(t.id): [] for t in tables}

        # Create time_slot to index map for quick lookup
        slot_index_map = {slot: idx for idx, slot in enumerate(time_slots)}

        # Also track unassigned bookings
        unassigned_bookings = []

        for booking in bookings:
            time_str = booking.time[:5] if len(booking.time) >= 5 else booking.time
            slot_index = slot_index_map.get(time_str, -1)

            booking_block = {
                "id": str(booking.id),
                "time": booking.time,
                "time_str": time_str,
                "slot_index": slot_index,  # Pre-calculated slot index
                "guests": booking.guests,
                "customer_name": booking.guest_name or "ã‚²ã‚¹ãƒˆ",
                "status": booking.status,
                "duration_slots": 3,  # 90 min = 3 slots of 30 min
                "notes": booking.note or "",
            }

            # Find table assignment
            if booking.table_assignments:
                for assignment in booking.table_assignments:
                    table_id = str(assignment.table_id)
                    if table_id in bookings_by_table:
                        bookings_by_table[table_id].append(booking_block)
            else:
                unassigned_bookings.append(booking_block)

        # Convert tables to response format
        tables_data = []
        for table in tables:
            table_bookings = bookings_by_table.get(str(table.id), [])
            tables_data.append({
                "id": str(table.id),
                "table_number": table.table_number,
                "name": table.name or "",
                "max_capacity": table.max_capacity,
                "table_type": table.table_type,
                "zone": table.zone or "",
                "bookings": table_bookings,
            })

        return {
            "tables": tables_data,
            "time_slots": time_slots,
            "unassigned_bookings": unassigned_bookings,
            "slot_duration": self.SLOT_DURATION,
        }


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def get_optimization_service(
    db: AsyncSession,
    branch_code: str
) -> TableOptimizationService:
    """Factory function to get optimization service"""
    return TableOptimizationService(db, branch_code)

