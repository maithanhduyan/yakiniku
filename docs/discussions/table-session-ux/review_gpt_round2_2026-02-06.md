# 🔭 GPT Visionary — Round 2 Review | 2026-02-06

## Phản hồi cho các Compromise Proposals

### 1. 4-phase lifecycle
**✅ Chấp nhận**

Sau khi xem xét lại codebase, tôi chấp nhận 4 phases: **WELCOME → ORDERING → BILL_REVIEW → CLEANING**.

**Lý do chấp nhận cho tầm nhìn dài hạn:**

- READY phase trong đề xuất Round 1 của tôi thực chất chỉ là WELCOME khi iPad idle — tách ra tạo thêm complexity mà không thêm giá trị. WELCOME **đã là** idle state.
- BILL_REVIEW lightweight (read-only order summary khi khách bấm "会計") hoàn toàn đủ cho MVP. Code hiện tại ở `renderHistory()` đã có order summary với tổng tiền — chỉ cần tái sử dụng UI này cho BILL_REVIEW.
- Nếu POS gửi `session_paid` → auto-transition to CLEANING giữ flow đơn giản. Backend đã có `TableSession` và `OrderEvent` — infrastructure sẵn sàng.
- **Mở rộng trong tương lai**: 4 phases không chặn việc thêm sub-states trong BILL_REVIEW (feedback, tipping) sau này. State machine dễ mở rộng bằng cách thêm sub-states hơn là thêm top-level phases.

**Điều kiện**: BILL_REVIEW phải có nút "追加注文" (thêm món) để quay lại ORDERING — vì yakiniku thường khách gọi thêm ngay cả sau khi xem bill. Đây là feature phổ biến ở chuỗi 牛角, 焼肉きんぐ.

---

### 2. Lightweight Event Logger thay vì Full EventStore
**✅ Chấp nhận**

Đây là thay đổi lập trường lớn nhất của tôi. Tôi chấp nhận **Lightweight Event Logger (~100-150 LOC)** thay vì full ClientEventStore.

**Lý do thay đổi lập trường:**

1. **Backend đã là source of truth cho event sourcing.** `OrderEvent` model đã có 23 EventTypes, composite indexes, correlation tracking. Duplicate hệ thống này trên client là vi phạm Single Responsibility.

2. **Concrete use case được yêu cầu — tôi không tìm được.** Câu hỏi synthesis là: "Cho use case cụ thể mà event replay trên client cần thiết mà state machine + localStorage không handle được." Tôi đã suy nghĩ kỹ:

   - *Crash giữa order flow?* → State machine đọc cart + `session_phase` + history từ localStorage là đủ.
   - *Audit trail?* → Backend `OrderEvent` table đã cover.
   - *Debugging offline issues?* → Lightweight event log (type + timestamp) đủ cho debugging mà không cần full replay.
   - *AI features tương lai?* → AI sẽ chạy trên server với full event history từ database, không phải trên iPad.

3. **LOC analysis trung thực** (xem bảng bên dưới) cho thấy full EventStore là overkill.

**Chấp nhận design cụ thể:**
- Mỗi action → ghi `{type, timestamp}` vào `session_log_{TABLE_ID}` trong localStorage
- Sync log lên backend qua offline queue (không phải real-time)
- State recovery = read phase + cart + history (state machine), **KHÔNG** event replay
- Clear log khi CLEANING → WELCOME transition

---

### 3. Long-press 3s, no PIN
**✅ Chấp nhận**

**Lý do:**

- Tôi đã overweight security cho MVP. Thực tế yakiniku restaurant: nhân viên xoay ca liên tục, share iPad, PIN = friction cho table turnover. 1 phút thêm per table × 30 bàn = 30 phút staff time lãng phí mỗi ngày.
- Long-press 3s đã đủ ngăn khách vô tình trigger. Trẻ em (concern chính) hiếm khi giữ nút 3 giây liên tục.
- PIN configurable per branch trong Phase 2 là hợp lý — chi nhánh cao cấp hơn có thể muốn PIN, izakaya-style thì không.

**Không còn điều kiện** — clean accept.

---

### 4. Grilling guide thay vì real-time timer
**✅ Chấp nhận có điều kiện**

**Chấp nhận grilling guide trong item modal** — "焼き方ガイド" tab với hình ảnh + text.

**Lý do chấp nhận:**
- Gemini's liability concern là valid: nếu khách theo timer mà vẫn ăn thịt chưa chín kỹ → legal risk thực sự ở Nhật (食品衛生法).
- Grilling guide = nội dung tĩnh, zero liability, hữu ích cho khách nước ngoài (du khách không biết nướng yakiniku).
- 1 ngày dev, tái sử dụng item modal đã có.

**Điều kiện**: Data cho grilling guide nên được lưu trong menu item schema (thêm trường `grilling_guide` vào item model) chứ không phải hardcode. Cho phép quản lý qua dashboard sau này. Cụ thể thêm vào item model:
- `grilling_guide_text`: String (hướng dẫn)
- `grilling_guide_image`: String (URL hình)
- `recommended_doneness`: Enum (rare/medium/well-done)

Đây không phải over-engineering — đây là data modeling cơ bản để content manageable.

---

### 5. 2-tier sync
**✅ Chấp nhận**

**Lý do:**
- Code hiện tại cho thấy `submitOrder()` đã là fire-and-forget với error handling. Đây tự nhiên là tier 1 (critical, immediate).
- Tất cả events khác (session log, analytics, call staff) → offline queue. Flush on reconnect hoặc mỗi 60s.
- 3-tier ban đầu tôi đề xuất thêm batch 30s cho "informational events" — nhưng thực tế sự khác biệt giữa flush-on-reconnect và batch-30s là marginal.
- Complexity budget nên dành cho features quan trọng hơn (BILL_REVIEW flow, grilling guide).

**Không còn điều kiện** — clean accept.

---

### 6. LWW + dedup thay vì CRDT
**✅ Chấp nhận**

**Lý do:**
- Đây là điểm tôi sai rõ nhất. 1 iPad = 1 table = **single writer**. CRDT giải quyết multi-writer conflict — problem không tồn tại.
- Ngay cả tương lai multi-device (khách scan QR từ phone cá nhân), mỗi device vẫn ghi vào order riêng → vẫn single-writer per order.
- `client_order_id` cho dedup (idempotency key) là pattern chuẩn, đủ cho mọi scenario.

**Không còn điều kiện** — clean accept.

---

### 7. Walkout timeout warning
**✅ Chấp nhận**

**Lý do:**
- Auto-close session khi không có human confirmation là nguy hiểm: khách có thể đi toilet 20 phút, hoặc đang nướng mà không tương tác với iPad.
- 30-minute inactivity → notification trên iPad là đủ. Staff quyết định có close hay không.

**Thêm 1 gợi ý tương lai** (không phải MVP): Nếu notification đã gửi + thêm 30 phút nữa không tương tác (tổng 60 phút), emit `SESSION_ABANDONED` event cho analytics — nhưng vẫn **không auto-close**.

---

### 8. Crash recovery via state machine
**✅ Chấp nhận**

**Concrete failure scenario analysis:**

1. **Cart add** → `saveCartToStorage()` gọi ngay → localStorage updated synchronously
2. **Submit order** → cart cleared TRƯỚC khi history saved (current bug)

**Potential gap**: crash GIỮA clear cart và save history → cart đã xóa, history chưa lưu. Nhưng:
- Order đã POST thành công lên backend → backend có data
- Khi iPad restart, client có thể fetch order history từ backend API
- Đây KHÔNG cần event replay — chỉ cần 1 API call

**Design cụ thể tôi chấp nhận:**
```
On app start:
  1. Read session_phase from localStorage
  2. Read cart from localStorage
  3. Read history from localStorage
  4. If phase = ORDERING AND cart exists → resume ordering
  5. If phase = ORDERING AND cart empty AND history empty →
     try GET /api/tableorder/orders?session_id={id} to recover history
  6. If corrupted or missing → default WELCOME (clean slate)
```

---

## LOC Estimates

| Approach | Estimated LOC | Complexity | Dev Time |
|----------|--------------|------------|----------|
| Full ClientEventStore (Round 1 đề xuất) | ~460 LOC | High — EventStore class, reducer, replay engine, sync tiers, CRDT dedup, retention GC | 5-7 ngày |
| Lightweight Event Logger (compromise) | ~120 LOC | Low — logEvent(), syncQueue(), flushOnReconnect(), clearOnTransition() | 1-2 ngày |

**Breakdown cho Full ClientEventStore (nếu tôi làm):**
- `EventStore` class với `append()`, `getBySession()`, `replay()`: ~80 LOC
- `_applyEvent()` reducer (state rebuilder): ~60 LOC
- 3-tier sync engine (priority queue, batch timer, session-end flush): ~100 LOC
- CRDT-like conflict resolution: ~50 LOC
- Retention policy (48h cleanup, 50 session limit, 4MB guard): ~40 LOC
- localStorage schema manager (6 key types, migration): ~30 LOC
- Test coverage cho event replay edge cases: ~100 LOC
- **Total: ~460 LOC production + ~100 LOC tests**

**Breakdown cho Lightweight Event Logger:**
- `logEvent(type, meta)`: ~15 LOC
- `getSessionLog()`: ~10 LOC
- `syncEventLog()` + offline queue integration: ~50 LOC
- `clearSessionLog()`: ~10 LOC
- State machine recovery (read phase + cart + history): ~40 LOC
- **Total: ~120 LOC thêm**

**Verdict**: 460 LOC vs 120 LOC, cho cùng functional outcome trong context single-iPad. ROI của full EventStore là âm.

---

## Remaining Concerns

### 1. BILL_REVIEW → ORDERING backward transition
Cần định nghĩa rõ: khi khách ở BILL_REVIEW bấm "追加注文", state transition back to ORDERING phải:
- Giữ nguyên order history
- Emit event `CALL_BILL_CANCELLED` lên backend (để POS biết khách chưa muốn thanh toán nữa)
- Backend cần EventType mới: `CALL_BILL_CANCELLED`

### 2. Session start timing
Với 4-phase lifecycle:
- WELCOME screen → session chưa bắt đầu (iPad idle)
- Touch "始める" → session starts → emit `SESSION_STARTED` → transition to ORDERING
- Cần refactor SESSION_ID generation để chỉ gọi khi transition WELCOME → ORDERING

### 3. Offline queue format standardization
```javascript
// Proposed queue item format
{
  id: "evt_xxx",           // client-generated UUID
  type: "session.started", // Match backend EventType enum
  timestamp: "ISO-8601",
  session_id: "sess_xxx",
  table_id: "table-1",
  data: {}                 // Optional payload
}
```

---

## Đánh giá tổng thể

**Kết quả: 8/8 proposals CHẤP NHẬN** (6 clean accept, 2 accept có điều kiện nhỏ).

Tôi thay đổi lập trường đáng kể so với Round 1. Lý do:

1. **Codebase evidence thuyết phục.** Backend event sourcing đã mature. Duplicate lên client là waste.
2. **Single-writer reality.** 1 iPad = 1 bàn = mọi CRDT/complex sync argument sụp đổ.
3. **LOC analysis trung thực** cho thấy full EventStore có ROI âm — 460 LOC vs 120 LOC cho cùng outcome.
4. **Pragmatism ≠ short-term thinking.** Lightweight foundation + iterate > over-engineer from day 1.

**Tầm nhìn dài hạn không thay đổi** — chỉ thay đổi *cách đạt được*.

**Dự kiến tỷ lệ đồng thuận sau Round 2: 18-20/20**
