"""
AI Table Optimization Service
Tối ưu hóa việc xếp bàn và quản lý capacity nhà hàng
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
    """Chiến lược tối ưu hóa"""
    MAXIMIZE_CAPACITY = "maximize_capacity"      # Tối đa số khách
    MINIMIZE_WASTE = "minimize_waste"            # Giảm lãng phí ghế
    VIP_PRIORITY = "vip_priority"                # Ưu tiên VIP
    QUICK_TURNOVER = "quick_turnover"            # Tối đa vòng quay bàn


@dataclass
class TableSlot:
    """Thông tin 1 slot thời gian của bàn"""
    table_id: str
    table_number: str
    max_capacity: int
    time_slot: str
    is_available: bool
    booking_id: Optional[str] = None
    guests: int = 0


@dataclass
class TimeSlotSummary:
    """Tổng hợp tình trạng 1 khung giờ"""
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
    """Đề xuất bàn cho booking"""
    table_id: str
    table_number: str
    capacity: int
    score: float  # 0-100, điểm phù hợp
    reason: str
    waste: int  # Số ghế thừa


@dataclass
class OptimizationInsight:
    """Insight từ AI về tình trạng nhà hàng"""
    type: str  # "warning", "suggestion", "opportunity"
    title: str
    message: str
    priority: int  # 1-5
    action: Optional[str] = None
    data: Optional[Dict] = None


class TableOptimizationService:
    """
    AI Service để tối ưu hóa việc xếp bàn

    Features:
    1. Đề xuất bàn phù hợp cho số khách
    2. Cảnh báo khi sắp full
    3. Gợi ý thời gian thay thế
    4. Phân tích utilization
    """

    # Thời gian trung bình 1 bữa ăn (phút)
    AVERAGE_DINING_TIME = 90

    # Thời gian buffer giữa các booking (phút)
    TURNOVER_BUFFER = 30

    # Slot duration (phút)
    SLOT_DURATION = 30

    def __init__(self, db: AsyncSession, branch_code: str):
        self.db = db
        self.branch_code = branch_code

    # ==========================================
    # CORE: Tìm bàn phù hợp
    # ==========================================

    async def find_best_tables(
        self,
        guests: int,
        booking_date: date,
        time_slot: str,
        strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_WASTE
    ) -> List[TableSuggestion]:
        """
        Tìm bàn phù hợp nhất cho số khách

        Strategy:
        - MINIMIZE_WASTE: Chọn bàn có capacity gần nhất với số khách
        - MAXIMIZE_CAPACITY: Ưu tiên bàn lớn để có chỗ nếu khách thêm
        - VIP_PRIORITY: Ưu tiên bàn VIP/private
        """
        # Lấy tất cả bàn available cho slot này
        available_tables = await self._get_available_tables(booking_date, time_slot)

        if not available_tables:
            return []

        suggestions = []

        for table in available_tables:
            # Bỏ qua bàn quá nhỏ
            if table.max_capacity < guests:
                continue

            # Tính điểm dựa trên strategy
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

        # Sắp xếp theo score giảm dần
        suggestions.sort(key=lambda x: x.score, reverse=True)

        return suggestions[:5]  # Top 5 đề xuất

    def _calculate_table_score(
        self,
        table: Table,
        guests: int,
        strategy: OptimizationStrategy
    ) -> Tuple[float, str]:
        """Tính điểm phù hợp của bàn"""
        base_score = 100.0
        reason_parts = []

        waste = table.max_capacity - guests

        if strategy == OptimizationStrategy.MINIMIZE_WASTE:
            # Giảm điểm theo số ghế thừa
            waste_penalty = waste * 10
            base_score -= waste_penalty

            if waste == 0:
                reason_parts.append("完璧にマッチ")
            elif waste <= 2:
                reason_parts.append(f"余り{waste}席")
            else:
                reason_parts.append(f"余り{waste}席(大きめ)")

        elif strategy == OptimizationStrategy.MAXIMIZE_CAPACITY:
            # Ưu tiên bàn lớn hơn
            capacity_bonus = table.max_capacity * 5
            base_score += capacity_bonus
            reason_parts.append(f"最大{table.max_capacity}名まで対応")

        # Bonus cho các features
        if table.table_type == "private":
            base_score += 15
            reason_parts.append("個室")

        if table.has_window:
            base_score += 5
            reason_parts.append("窓際")

        # Priority bonus
        base_score += table.priority * 2

        reason = "・".join(reason_parts) if reason_parts else "標準席"

        return max(0, min(100, base_score)), reason

    async def _get_available_tables(
        self,
        booking_date: date,
        time_slot: str
    ) -> List[Table]:
        """Lấy danh sách bàn còn trống cho slot"""
        # Lấy tất cả bàn của branch
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = tables_result.scalars().all()

        # Lấy các bàn đã được assign cho slot này
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

        # Lọc ra bàn còn trống
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
        Kiểm tra xem có thể đặt bàn không

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
                "message": f"{len(suggestions)}席ご案内可能です"
            }

        # Không có bàn -> tìm alternatives
        alternatives = await self._find_alternative_slots(guests, booking_date, time_slot)

        return {
            "available": False,
            "tables": [],
            "alternatives": alternatives,
            "message": "申し訳ございません、ご希望の時間は満席です。" +
                      (f"代わりに{len(alternatives)}つの時間帯がございます。" if alternatives else "")
        }

    async def _find_alternative_slots(
        self,
        guests: int,
        booking_date: date,
        requested_slot: str,
        range_hours: int = 2
    ) -> List[Dict]:
        """Tìm các slot thay thế trong vòng ±range_hours"""
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
        """Tổng hợp tình trạng tất cả các slot trong ngày"""
        # Lấy tất cả bàn
        tables_query = select(Table).where(
            and_(
                Table.branch_code == self.branch_code,
                Table.is_active == True
            )
        )
        tables_result = await self.db.execute(tables_query)
        all_tables = list(tables_result.scalars().all())

        total_capacity = sum(t.max_capacity for t in all_tables)

        # Lấy tất cả booking trong ngày
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
        Tạo insights và suggestions cho staff

        Examples:
        - "20:00 sắp full (7/8 bàn), cân nhắc từ chối booking mới"
        - "18:00 còn nhiều bàn 6 ghế, khách 2 người nên chuyển sang 4 ghế"
        - "Hôm nay có 3 VIP, đã reserve phòng riêng"
        """
        insights = []

        # Get slot summaries
        summaries = await self.get_time_slot_summary(target_date)

        for summary in summaries:
            # Warning: Sắp full
            if summary.utilization_rate >= 80:
                insights.append(OptimizationInsight(
                    type="warning",
                    title=f"⚠️ {summary.time_slot} 混雑注意",
                    message=f"利用率{summary.utilization_rate}% - 残り{summary.available_tables}席",
                    priority=4 if summary.utilization_rate >= 90 else 3,
                    action="新規予約を控えるか、代替時間をご案内ください",
                    data={
                        "time_slot": summary.time_slot,
                        "utilization": summary.utilization_rate,
                        "available": summary.available_tables
                    }
                ))

            # Opportunity: Slot trống
            elif summary.utilization_rate < 30 and summary.time_slot >= "18:00":
                insights.append(OptimizationInsight(
                    type="opportunity",
                    title=f"📈 {summary.time_slot} 空き多め",
                    message=f"利用率{summary.utilization_rate}% - {summary.available_tables}席空き",
                    priority=2,
                    action="プロモーションや予約転換の機会",
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
        """Kiểm tra lãng phí capacity"""
        insights = []

        # Lấy bookings với table assignment
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
            if waste >= 3:  # 3+ ghế thừa
                waste_cases.append({
                    "booking": booking,
                    "table": table,
                    "waste": waste
                })

        if waste_cases:
            total_waste = sum(c["waste"] for c in waste_cases)
            insights.append(OptimizationInsight(
                type="suggestion",
                title=f"💡 席効率の改善可能",
                message=f"{len(waste_cases)}件の予約で合計{total_waste}席の余裕あり",
                priority=2,
                action="小さい席への変更を検討",
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
        """Tự động assign bàn cho booking"""
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
        """Đổi bàn cho booking"""
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
                "customer_name": booking.guest_name or "ゲスト",
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
