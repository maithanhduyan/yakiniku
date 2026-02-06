# 🎼 Synthesis — Round 1 | 2026-02-06

## Chủ đề: Table Session UX & Event Sourcing cho `table-order` app

---

## 📊 Bảng đồng thuận

| # | Điểm thảo luận | GPT (Visionary) | Gemini (Pragmatist) | Đồng thuận? |
|---|----------------|-----------------|---------------------|-------------|
| 1 | Số phases trong session lifecycle | 6 phases (READY→WELCOME→ORDERING→PAYMENT→CLEANING→READY) nhưng ORDERING merge với DINING | 3 phases (WELCOME→ORDERING→CLEANING) | ❌ |
| 2 | ORDERING & DINING merge hay tách | Merge — yakiniku khách gọi liên tục khi ăn | Merge — không cần DINING phase riêng | ✅ |
| 3 | PAYMENT phase trên iPad | Có — hiển thị bill summary, feedback form, "add more" button | Không — thanh toán xảy ra ở POS, iPad chỉ nhận event rồi chuyển CLEANING | ❌ |
| 4 | Client-side event sourcing | Full `ClientEventStore` class với `append()`, `replay()`, `_applyEvent()` reducer, sync engine, batch sync | KHÔNG — backend đã có. Client chỉ cần offline event queue (~50 LOC) | ❌ |
| 5 | localStorage key schema | Phức tạp: device config, active session, events per session, sync queue, sessions index | Đơn giản: flat keys scoped by TABLE_ID, clear on session end | ❌ |
| 6 | Sync strategy | Hybrid: critical events sync ngay, informational batch 30s, analytics at session end | Fire-and-forget + offline queue flush on reconnect | ❌ |
| 7 | Conflict resolution | CRDT-like pattern, client wins + server reconciles | Last-Write-Wins, không cần CRDT (1 iPad = 1 writer) | ❌ |
| 8 | Retention policy | 48h synced, 7 days unsynced, 50 session limit, 4MB max | Last 50 sessions, clear session data on CLEANING→WELCOME | ✅ |
| 9 | Staff protection mechanism | Long-press 5s + 4-digit PIN | Long-press 3s, KHÔNG PIN | ❌ |
| 10 | Welcome screen | Có — branding, language selector, touch to start | Có — branding, touch to start | ✅ |
| 11 | Cleaning screen | Locked, session summary, staff-only unlock | Locked, session summary, long-press to complete | ✅ |
| 12 | Grilling timer | Có — flip alerts, haptic feedback, per-meat-type | KHÔNG — liability risk, khách không nhìn iPad khi nướng | ❌ |
| 13 | Course-based category ordering | Có — recommendation engine dựa trên session time | Có — đơn giản dựa trên thời gian session (5 phút logic) | ✅ |
| 14 | Reorder prompt | Implicit trong recommendation strip | Có — sau 15 phút im lặng, 1 lần duy nhất | ✅ |
| 15 | Static pairing suggestions | Có — trong recommendation strip | Có — hardcoded rules, hiển thị ở modal | ✅ |
| 16 | 食べ放題 mode | Có — hide prices, countdown, anti-waste | Phase 2 — cần backend pricing logic | ✅ (cùng agree Phase 2) |
| 17 | Edge case: khách bỏ về | 30min timeout auto-detect | Staff long-press manual trigger | ❌ |
| 18 | Edge case: crash recovery | Event replay từ localStorage | Đọc `session_phase` từ localStorage, resume | ❌ |
| 19 | Privacy/PII | No PII on iPad, APPI compliant discussion | No PII on iPad — anonymous by design | ✅ |
| 20 | Analytics destination | iPad shows stats + central data lake | Dashboard app (đã có), không phải iPad | ✅ (dashboard) |

---

## ✅ Các điểm đã đồng thuận (10/20)

1. **ORDERING & DINING merge**: Cả hai đồng ý yakiniku không cần tách — khách gọi liên tục khi ăn
2. **Welcome screen**: Cần có, branding + touch to start
3. **Cleaning screen**: Locked, hiển thị session summary, staff-only unlock
4. **Retention ~50 sessions**: Giữ limited history trên device
5. **Course-based category**: Gợi ý category dựa trên thời gian session
6. **Reorder prompt**: Nhắc khách gọi thêm sau khoảng im lặng
7. **Static pairing**: Hardcoded rules, không cần AI
8. **食べ放題 = Phase 2**: Cần backend support, chưa làm ngay
9. **No PII on iPad**: Anonymous by design
10. **Analytics ở dashboard**: Không phải trên iPad

---

## ❌ Các điểm bất đồng (10/20)

### Bất đồng #1: Số phases — 6 vs 3
- **GPT nói**: 6 phases (READY, WELCOME, ORDERING, PAYMENT, CLEANING, completed) cho phép tracking chi tiết journey. PAYMENT phase cho phép feedback, "add more", bill preview.
- **Gemini nói**: 3 phases đủ (WELCOME, ORDERING, CLEANING). READY không cần vì WELCOME đã là idle state. PAYMENT xảy ra ở POS — iPad không cần biết chi tiết.
- **Khoảng cách**: Tranh luận chính ở PAYMENT phase trên iPad. GPT muốn hiển thị bill, Gemini cho rằng POS xử lý.
- **Gợi ý compromise**: **4 phases** — WELCOME → ORDERING → BILL_REVIEW → CLEANING. BILL_REVIEW là optional/lightweight: chỉ hiển thị order summary khi khách bấm "会計" (CALL_BILL), không cần feedback form phức tạp. Nếu POS gửi `session_paid`, skip thẳng qua CLEANING.

### Bất đồng #2: Client-side Event Sourcing — Full EventStore vs Simple Queue
- **GPT nói**: Full `ClientEventStore` class (300+ LOC) với `append()`, `replay()`, `_applyEvent()` reducer — cho phép rebuild state từ events, hỗ trợ crash recovery hoàn chỉnh, là nền tảng cho AI features sau này.
- **Gemini nói**: KHÔNG duplicate event sourcing — backend đã có. Client chỉ cần offline queue (~50 LOC) với `queueEvent()` + `flushQueue()`.
- **Khoảng cách**: Rất lớn. GPT muốn client là event-sourced system. Gemini muốn client là thin layer.
- **Gợi ý compromise**: **Lightweight Event Logger** — không full CQRS/replay, nhưng hơn queue đơn thuần. Mỗi action ghi 1 event vào session log (cho analytics), đồng thời queue sync lên backend. Không cần `replay()` — dùng state machine đơn giản để recovery. ~100-150 LOC.

### Bất đồng #3: localStorage Schema — Complex vs Flat
- **GPT nói**: 6 key types (device_config, active_session, events_per_session, cart_per_session, sync_queue, sessions_index) với ~17KB/session.
- **Gemini nói**: 7 flat keys total (table_id, preferred_lang, session_phase, session_id, cart, history, offline_queue) với ~50KB max.
- **Khoảng cách**: GPT lưu events per session (có thể lớn), Gemini chỉ lưu cart+history (compact).
- **Gợi ý compromise**: Dùng Gemini's flat approach nhưng thêm 1 key: `session_log_{TABLE_ID}` cho lightweight event log (chỉ type + timestamp, không full payload). Total ~8-10 keys.

### Bất đồng #4: Sync Strategy — Hybrid Priority vs Fire-and-Forget
- **GPT nói**: 3 tiers sync (critical=immediate, info=batch 30s, analytics=session end). Exponential backoff.
- **Gemini nói**: Orders sync qua existing `submitOrder()`. Events fire-and-forget. Offline queue flush on reconnect.
- **Khoảng cách**: GPT phức tạp hơn nhưng reliable hơn. Gemini đơn giản hơn nhưng có thể mất events.
- **Gợi ý compromise**: **2 tiers**: Orders sync ngay (existing flow, đã hoạt động). Tất cả events khác → offline queue, flush on reconnect hoặc mỗi 60s nếu online. Không cần 3 tiers.

### Bất đồng #5: Conflict Resolution — CRDT vs LWW
- **GPT nói**: CRDT-like, client wins + server reconciles, complex dedup.
- **Gemini nói**: Last-Write-Wins, 1 iPad = 1 writer = không có conflict.
- **Khoảng cách**: Nhỏ — cả hai đều nhận ra 1 iPad/bàn. GPT over-plan cho future multi-device.
- **Gợi ý compromise**: **Gemini's approach** — LWW + `client_order_id` cho dedup. CRDT không cần cho single-writer scenario.

### Bất đồng #6: Staff Protection — PIN vs No PIN
- **GPT nói**: Long-press 5s + 4-digit branch PIN cho CLEANING unlock.
- **Gemini nói**: Long-press 3s đủ, PIN = chậm + staff quên.
- **Khoảng cách**: Nhỏ — chỉ khác PIN.
- **Gợi ý compromise**: **Long-press 3s** cho staff actions thông thường (CLEANING→WELCOME). **PIN optional** — configurable per branch. Default: no PIN.

### Bất đồng #7: Grilling Timer
- **GPT nói**: Có — flip alerts, haptic, per-meat-type. Differentiation feature.
- **Gemini nói**: KHÔNG — liability risk, nobody looks at iPad while grilling, alternative: cooking notes in item description.
- **Khoảng cách**: Lớn — khác biệt triết lý.
- **Gợi ý compromise**: **Phase 2, simplified** — không phải real-time timer. Thay vào đó: thêm "焼き方ガイド" (grilling guide) tab trong item modal với hình ảnh + text hướng dẫn. Zero liability, useful content, 1 ngày dev.

### Bất đồng #8: Walkout Detection
- **GPT nói**: 30min timeout auto-detect, emit SESSION_ENDED with reason "walkout".
- **Gemini nói**: Staff manual trigger via long-press. Walkout là rare, manual OK.
- **Khoảng cách**: Nhỏ — có timeout hay không.
- **Gợi ý compromise**: **Optional timeout warning** — sau 30 phút không tương tác, hiển thị notification cho staff (không auto-close session). Staff quyết định.

### Bất đồng #9: Crash Recovery
- **GPT nói**: Full event replay từ localStorage events để rebuild state.
- **Gemini nói**: Đọc `session_phase` + có data → resume. Default WELCOME nếu nothing.
- **Khoảng cách**: GPT phức tạp hơn nhưng robust hơn. Gemini simple but may lose cart if phase = ordering.
- **Gợi ý compromise**: **Gemini's approach enhanced** — đọc session_phase + cart + history từ localStorage. Nếu phase = ordering VÀ có cart → resume. Nếu corrupted → WELCOME. Không cần replay.

### Bất đồng #10: PAYMENT Phase trên iPad
- **GPT nói**: Có PAYMENT phase riêng — bill summary, feedback form, "add more" button.
- **Gemini nói**: Không cần — POS xử lý, iPad nhận event → CLEANING.
- **Khoảng cách**: GPT muốn iPad tham gia payment flow, Gemini muốn iPad chỉ là ordering device.
- **Gợi ý compromise**: **Lightweight BILL_REVIEW** — Khi khách bấm "会計", iPad hiển thị order summary (read-only, tái sử dụng order history UI) + "追加注文" button. KHÔNG có feedback form. Khi POS send `session_paid` → auto-transition to CLEANING.

---

## 📈 Tỷ lệ đồng thuận: 10/20 = 50%

---

## 🎯 Hướng dẫn cho Round 2

### Câu hỏi cụ thể cho GPT:
1. Bạn có chấp nhận **4 phases** (WELCOME → ORDERING → BILL_REVIEW → CLEANING) thay vì 6? BILL_REVIEW là lightweight, không có feedback form.
2. Bạn có đồng ý **không làm full client-side event sourcing** mà thay bằng lightweight event logger (~150 LOC) + state machine? Backend đã có full event store.
3. PIN cho staff protection có thực sự cần cho MVP không? Hay long-press 3s đủ?
4. Grilling timer: bạn có chấp nhận **"grilling guide" trong item modal** (hình ảnh + text) thay vì real-time timer?

### Câu hỏi cụ thể cho Gemini:
1. Bạn có chấp nhận thêm **BILL_REVIEW phase** (lightweight, read-only order summary) khi khách bấm "会計"? Nó tái sử dụng order history UI đã có.
2. Bạn có đồng ý thêm **lightweight event logger** (ghi type + timestamp per action) vào session log cho analytics? Không phải full event sourcing, chỉ ~50 LOC thêm.
3. 30-minute inactivity **warning** (chỉ notification, không auto-close) — acceptable?
4. localStorage schema: bạn có chấp nhận thêm 1 key `session_log_{TABLE_ID}` cho event log nhẹ?

### Đề xuất compromise cần cả hai phản hồi:
1. **4-phase lifecycle**: WELCOME → ORDERING → BILL_REVIEW (optional) → CLEANING
2. **Lightweight Event Logger**: ~100-150 LOC, ghi type+timestamp, sync via offline queue. KHÔNG phải full event sourcing.
3. **2-tier sync**: Orders = existing `submitOrder()`. Everything else = offline queue + flush.
4. **Long-press 3s, no PIN** (configurable per branch cho Phase 2)
5. **Grilling guide** trong item modal thay vì real-time timer

### Data/evidence cần bổ sung:
- Cả hai: ước tính **cụ thể số LOC** cho approach của mình (GPT's full EventStore vs Gemini's simple queue vs compromise lightweight logger)
- GPT: evidence rằng **event replay** trên client thực sự cần thiết — use case cụ thể mà state machine + localStorage không handle được?
- Gemini: nếu crash xảy ra giữa `submitOrder()` (cart cleared) nhưng trước `saveHistoryToStorage()` — Gemini's approach mất data. Cách xử lý?
