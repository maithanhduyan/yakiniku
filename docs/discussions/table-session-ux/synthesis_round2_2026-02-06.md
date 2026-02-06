# 🎼 Synthesis — Round 2 | 2026-02-06

## Chủ đề: Table Session UX & Event Sourcing cho `table-order` app

---

## 📊 Bảng đồng thuận

| # | Điểm thảo luận | GPT (Visionary) | Gemini (Pragmatist) | Đồng thuận? |
|---|----------------|-----------------|---------------------|-------------|
| 1 | 4-phase lifecycle | ✅ Accept — WELCOME→ORDERING→BILL_REVIEW→CLEANING | ✅ Accept có điều kiện — BILL_REVIEW chỉ read-only | ✅ |
| 2 | ORDERING & DINING merge | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 3 | BILL_REVIEW content scope | Có nút "追加注文" quay lại ORDERING | Chỉ read-only + "追加注文", KHÔNG feedback/tipping | ✅ |
| 4 | Client-side Event Sourcing → Lightweight Logger | ✅ Accept — ~120 LOC, analytics-only | ✅ Accept — ~50 LOC SessionLog, fire-and-forget | ✅ |
| 5 | localStorage schema | Flat keys + `session_log_{TABLE_ID}` | Flat keys + SessionLog key | ✅ |
| 6 | Sync strategy — 2-tier | ✅ Orders immediate, rest via queue/60s | ✅ Tier 1 = submitOrder(), Tier 2 = queue/sendBeacon | ✅ |
| 7 | Conflict resolution — LWW + dedup | ✅ Accept, single-writer | ✅ Confirmed, client_order_id | ✅ |
| 8 | Retention ~50 sessions | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 9 | Staff protection — long-press 3s, no PIN | ✅ Accept | ✅ Confirmed | ✅ |
| 10 | Welcome screen | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 11 | Cleaning screen — staff-only unlock | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 12 | Grilling guide thay vì real-time timer | ✅ Accept — data trong menu schema | ✅ Accept — static content, 1 day dev | ✅ |
| 13 | Course-based category ordering | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 14 | Reorder prompt | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 15 | Static pairing suggestions | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 16 | 食べ放題 = Phase 2 | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 17 | Walkout — 30min timeout warning | ✅ Accept — notification only, no auto-close | ✅ Accept — iPad-only notification, ~15 LOC | ✅ |
| 18 | Crash recovery — state machine + atomic save | ✅ Accept — read phase+cart+history, fallback API | ✅ Accept — reorder save operations (history before cart) | ✅ |
| 19 | Privacy — No PII on iPad | ✅ (Round 1) | ✅ (Round 1) | ✅ |
| 20 | Analytics ở dashboard | ✅ (Round 1) | ✅ (Round 1) | ✅ |

---

## ✅ Các điểm đã đồng thuận (20/20)

1. **4-phase lifecycle**: WELCOME → ORDERING → BILL_REVIEW → CLEANING
2. **ORDERING merge DINING**: Yakiniku khách gọi liên tục khi ăn
3. **BILL_REVIEW scope**: Read-only order summary + nút "追加注文", KHÔNG feedback/tipping
4. **Lightweight Event Logger**: Analytics log (~50-120 LOC), KHÔNG phải event sourcing. `SessionLog` object, fire-and-forget
5. **localStorage flat keys**: Scoped by TABLE_ID + 1 session_log key
6. **2-tier sync**: Orders qua `submitOrder()` (existing), tất cả khác qua offline queue + flush 60s/reconnect
7. **LWW + `client_order_id` dedup**: Single-writer, không cần CRDT
8. **Retention ~50 sessions**: Clear session data on CLEANING → WELCOME
9. **Long-press 3s, no PIN**: PIN configurable per branch Phase 2
10. **Welcome screen**: Branding + touch to start
11. **Cleaning screen**: Locked, session summary, long-press staff unlock
12. **Grilling guide**: Static "焼き方ガイド" tab trong item modal, data trong menu schema
13. **Course-based categories**: Gợi ý dựa trên session time
14. **Reorder prompt**: Sau 15 phút im lặng
15. **Static pairing**: Hardcoded rules, hiển thị ở modal
16. **食べ放題 = Phase 2**: Cần backend pricing logic
17. **30-min walkout warning**: iPad notification only, KHÔNG auto-close, staff quyết định
18. **Crash recovery**: State machine (read phase+cart+history), save history BEFORE clearing cart, fallback API call
19. **No PII on iPad**: Anonymous by design
20. **Analytics → Dashboard app**: Không trên iPad

---

## 📈 Tỷ lệ đồng thuận: 20/20 = 100% ✅🎉

---

## 🎯 Đồng thuận đạt 100% — Chuyển sang Final Consensus

Cả hai agent đã đồng thuận hoàn toàn trên tất cả 20 điểm. Round 2 đã giải quyết toàn bộ 10 bất đồng từ Round 1 thông qua compromise proposals của Orchestra.

### Điểm nổi bật Round 2:
- **GPT thay đổi lớn nhất**: Từ bỏ full ClientEventStore (460 LOC) → chấp nhận Lightweight Logger (120 LOC). Lý do: backend đã là source of truth, không tìm được concrete use case cho client-side event replay.
- **Gemini thay đổi lớn nhất**: Chấp nhận BILL_REVIEW phase (từ 3→4 phases) và walkout warning. Lý do: BILL_REVIEW tái sử dụng UI đã có (~30 LOC), walkout warning chỉ ~15 LOC với operational value thực tế.
- **Cả hai đều converge** trên LOC estimate: ~260 LOC tổng, ~5-6 dev days (bao gồm testing).

### Minor Details cần ghi nhận (không ảnh hưởng đồng thuận):
1. **GPT yêu cầu** grilling guide data trong menu schema (3 fields) — Gemini đồng ý "thêm field vào model"
2. **GPT yêu cầu** `CALL_BILL_CANCELLED` EventType mới — cần thêm vào backend enum
3. **Gemini yêu cầu** session_paid WebSocket routing verification
4. **Gemini yêu cầu** backend endpoint `POST /api/tableorder/session-log/` (~30 LOC)
5. **Cả hai đồng ý** session_id chỉ generate khi WELCOME→ORDERING (không phải on page load)
