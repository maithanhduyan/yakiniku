# 🤝 Final Consensus | Table Session UX & Event Sourcing | 2026-02-06

## Tổng quan
- **Chủ đề**: Session lifecycle, event sourcing strategy, và yakiniku customer UX cho `table-order` app
- **Số vòng thảo luận**: 2
- **Ngày bắt đầu → Đồng thuận**: 2026-02-06 → 2026-02-06
- **Participants**: GPT (Visionary), Gemini (Pragmatist)
- **Tỷ lệ đồng thuận cuối**: 20/20 = 100%

---

## Kết luận đồng thuận

### 1. Session Lifecycle: 4-Phase State Machine

**Quyết định**: `WELCOME → ORDERING → BILL_REVIEW → CLEANING`

**Lý do**:
- WELCOME là idle state — không cần READY phase riêng (GPT concession)
- BILL_REVIEW lightweight — tái sử dụng `renderHistory()` UI đã có, chỉ thêm ~30-40 LOC (Gemini concession thêm 1 phase)
- PAYMENT xảy ra ở POS — iPad chỉ hiển thị read-only summary khi khách bấm "会計"
- ORDERING merge DINING — yakiniku khách gọi liên tục khi ăn, không cần tách

**State transitions**:
```
WELCOME ──[touch "始める"]──→ ORDERING
ORDERING ──[bấm "会計"]──→ BILL_REVIEW
BILL_REVIEW ──[bấm "追加注文"]──→ ORDERING (backward)
BILL_REVIEW ──[POS "session_paid" event]──→ CLEANING
CLEANING ──[staff long-press 3s]──→ WELCOME
```

**Hành động tiếp theo**:
- [ ] Thêm `sessionPhase` vào `state` object trong `app.js`
- [ ] Tạo `transitionTo(phase)` function với validation
- [ ] Tạo Welcome screen HTML/CSS (branding + "始める" button)
- [ ] Tạo Cleaning screen HTML/CSS (session summary + long-press unlock)
- [ ] BILL_REVIEW = full-screen order history (reuse `renderHistory()`)
- [ ] Refactor `SESSION_ID` generation: chỉ khi WELCOME → ORDERING

---

### 2. Event Strategy: Lightweight Event Logger, KHÔNG Full Event Sourcing

**Quyết định**: Client-side dùng `SessionLog` analytics logger (~50-120 LOC). KHÔNG duplicate backend event sourcing.

**Lý do**:
- Backend `OrderEvent` model đã có 23 EventTypes, composite indexes, correlation tracking — đây là source of truth duy nhất
- Không tìm được concrete use case nào mà client-side event replay cần thiết mà state machine + localStorage không xử lý được (GPT admission)
- Full `ClientEventStore` = 460 LOC vs Lightweight Logger = 120 LOC, cùng functional outcome (GPT analysis)
- Fire-and-forget analytics — mất log = OK, KHÔNG block UI

**Implementation**:
```javascript
const SessionLog = {
    _key: () => `session_log_${TABLE_ID}`,
    log(type, meta = {}) {
        try {
            const logs = JSON.parse(localStorage.getItem(this._key()) || '[]');
            logs.push({ type, ts: Date.now(), ...meta });
            localStorage.setItem(this._key(), JSON.stringify(logs));
        } catch (e) { /* analytics, not critical */ }
    },
    flush() {
        const logs = JSON.parse(localStorage.getItem(this._key()) || '[]');
        if (!logs.length) return;
        navigator.sendBeacon?.(`${CONFIG.API_URL}/tableorder/session-log/`,
            JSON.stringify({ table_id: TABLE_ID, session_id: SESSION_ID, logs }));
        localStorage.removeItem(this._key());
    },
    clear() { localStorage.removeItem(this._key()); }
};
```

**Hành động tiếp theo**:
- [ ] Thêm `SessionLog` object vào `app.js`
- [ ] Rải `SessionLog.log()` calls vào ~15 chỗ (menu view, add cart, submit, phase transitions)
- [ ] Thêm flush scheduling: `setInterval` 60s + `online` event listener
- [ ] Backend: thêm endpoint `POST /api/tableorder/session-log/` (~30 LOC)

---

### 3. localStorage Schema: Flat Keys Scoped by TABLE_ID

**Quyết định**: 8-10 flat keys, clear on session end

| Key | Content | Lifetime |
|-----|---------|----------|
| `table_id` | Current table ID | Permanent |
| `preferred_lang` | `ja` / `en` | Permanent |
| `session_phase` | `welcome`/`ordering`/`bill_review`/`cleaning` | Per session |
| `session_id` | UUID | Per session |
| `table_order_cart` | Cart items JSON | Per session |
| `yakiniku_history_{TABLE_ID}` | Order history JSON | Per session |
| `session_log_{TABLE_ID}` | Analytics event log | Per session, flush on transition |
| `offline_queue` | Pending API calls | Until flushed |

**Hành động tiếp theo**:
- [ ] Thêm `session_phase` read/write vào `transitionTo()`
- [ ] Clear session keys khi CLEANING → WELCOME
- [ ] Retain permanent keys (`table_id`, `preferred_lang`)

---

### 4. Sync Strategy: 2-Tier

**Quyết định**:
- **Tier 1 (Critical, immediate)**: Orders → `submitOrder()` hiện tại, đã hoạt động
- **Tier 2 (Best-effort, async)**: Session logs, analytics → offline queue + flush on reconnect hoặc mỗi 60s

**Lý do**: 3-tier (batch 30s cho "informational") = marginal benefit vs complexity cost. 2-tier đủ cho single-iPad scenario.

**Hành động tiếp theo**:
- [ ] Thêm `client_order_id` (UUID) vào `submitOrder()` cho idempotency
- [ ] Backend: check `client_order_id` exists → return existing order (dedup)

---

### 5. Staff Protection: Long-Press 3s, No PIN

**Quyết định**: Long-press 3s cho staff actions. PIN configurable per branch trong Phase 2.

**Lý do**:
- PIN = friction cho table turnover, staff quên PIN
- Long-press 3s đủ ngăn accidental trigger (khách, trẻ em)
- 1 phút thêm/table × 30 bàn = 30 phút lãng phí/ngày nếu dùng PIN

**Hành động tiếp theo**:
- [ ] Implement long-press handler trên Cleaning screen "リセット" button
- [ ] Visual feedback: progress bar 0→100% trong 3 giây
- [ ] Haptic feedback trên iPad (nếu supported)

---

### 6. Crash Recovery: State Machine + Atomic Save

**Quyết định**:
- On app start: read `session_phase` + `cart` + `history` từ localStorage → resume
- Fix bug hiện tại: save history BEFORE clearing cart (atomic-ish)
- Fallback: `GET /api/tableorder/orders?session_id={id}` nếu history trống nhưng phase = ordering
- If corrupted: default WELCOME

**Lý do**: Event replay trên client không cần thiết — state machine + localStorage đủ cho mọi crash scenario. Reorder 2 dòng code fix bug hiện tại.

**Recovery flow**:
```
On app start:
  1. Read session_phase from localStorage
  2. Read cart from localStorage
  3. Read history from localStorage
  4. If phase = ORDERING AND cart exists → resume ordering
  5. If phase = ORDERING AND cart empty AND history empty →
     GET /api/tableorder/orders?session_id={id} to recover
  6. If corrupted or missing → WELCOME (clean slate)
```

**Hành động tiếp theo**:
- [ ] Reorder `submitOrder()`: `saveHistoryToStorage()` TRƯỚC `saveCartToStorage()`
- [ ] Thêm recovery logic vào `initApp()`

---

### 7. Yakiniku UX Features

**Quyết định**:

| Feature | Scope | Priority | Dev Days |
|---------|-------|----------|----------|
| 焼き方ガイド (Grilling guide) | Static tab trong item modal, data từ menu schema | Phase 1 | 1 |
| Course-based category hints | Gợi ý category dựa trên session time (5-min logic) | Phase 1 | 0.5 |
| Reorder prompt | Sau 15 phút im lặng, 1 lần duy nhất | Phase 1 | 0.5 |
| Static pairing suggestions | Hardcoded rules, hiển thị trong item modal | Phase 1 | 1 |
| 30-min inactivity warning | iPad-only notification, staff dismiss | Phase 1 | 0.25 |
| 食べ放題 mode | Hide prices, countdown, anti-waste | Phase 2 | TBD |
| PIN per branch | Configurable staff PIN | Phase 2 | TBD |
| Cross-device notification | Walkout warning → POS/Dashboard | Phase 2 | TBD |

**Grilling guide schema** (thêm vào menu item model):
- `grilling_guide_text`: String (hướng dẫn nướng)
- `grilling_guide_image`: String (URL hình minh họa)
- `recommended_doneness`: Enum (rare/medium/well-done)

---

### 8. Walkout Detection: Passive Warning

**Quyết định**: 30-minute inactivity → iPad notification (persistent). KHÔNG auto-close session. Staff quyết định.

**Lý do**: Khách có thể đi toilet, đang nướng không tương tác iPad. Auto-close = dangerous. Notification = helpful reminder.

**Future (Phase 2)**: Sau 60 phút, emit `SESSION_ABANDONED` event cho analytics.

---

## Lộ trình thực hiện

| Giai đoạn | Timeline | Hành động | Ưu tiên |
|-----------|----------|-----------|---------|
| **Sprint 1** | 3-4 ngày | Session state machine (4 phases), Welcome/Cleaning screens, crash recovery fix, long-press handler | P0 |
| **Sprint 2** | 2-3 ngày | SessionLog analytics, BILL_REVIEW UI, walkout warning, client_order_id dedup | P0 |
| **Sprint 3** | 2-3 ngày | Grilling guide, course hints, reorder prompt, static pairing | P1 |
| **Phase 2** | 1-3 tháng | 食べ放題 mode, configurable PIN, cross-device notifications | P2 |
| **Phase 3** | 6-12 tháng | AI recommendation engine (server-side), dynamic pairing from analytics data | P3 |

**Tổng Phase 1**: ~260 LOC frontend + ~30 LOC backend, **5-6 dev days** (bao gồm testing)

### Files cần thay đổi (Phase 1):

| File | Thay đổi |
|------|----------|
| `apps/table-order/js/app.js` | Session state machine, SessionLog, crash recovery, long-press, walkout timer |
| `apps/table-order/js/config.js` | SESSION_PHASES constant, INACTIVITY_TIMEOUT |
| `apps/table-order/index.html` | Welcome screen, Cleaning screen HTML |
| `apps/table-order/css/style.css` | Welcome/Cleaning screen styles, long-press animation |
| `apps/table-order/js/i18n/ja.js` | Translations cho Welcome, Cleaning, BILL_REVIEW |
| `apps/table-order/js/i18n/en.js` | English translations |
| `backend/app/domains/tableorder/router.py` | Session log endpoint |
| `backend/app/domains/tableorder/events.py` | `CALL_BILL_CANCELLED` EventType |
| `backend/app/models/item.py` | Grilling guide fields (Sprint 3) |

---

## Trade-offs đã chấp nhận

1. **Không có client-side event sourcing**: Mất khả năng replay trên client, nhưng backend đã cover. ROI âm (460 LOC vs 120 LOC cho cùng outcome). Cả hai đồng ý.

2. **Không có real-time grilling timer**: Mất differentiation feature, nhưng avoid liability risk (食品衛生法). Thay bằng static grilling guide — useful content, zero risk.

3. **Không có PIN cho MVP**: Security trade-off, nhưng long-press 3s đủ cho use case. PIN = configurable Phase 2.

4. **Walkout không auto-close**: Có thể bàn stay "occupied" lâu hơn cần thiết, nhưng avoid false-positive (khách đi toilet, đang nướng). Staff notification = good enough.

5. **BILL_REVIEW không có feedback**: Mất customer insight, nhưng keep scope nhỏ. Feedback = separate PR future.

6. **Analytics fire-and-forget**: Có thể mất data, nhưng analytics ≠ critical path. sendBeacon = best-effort, acceptable loss rate.

---

## Appendix: Lịch sử thảo luận

| Round | GPT Review | Gemini Review | Synthesis | Đồng thuận |
|-------|-----------|---------------|-----------|------------|
| 1 | [review_gpt_round1](01_visionary_review_2026-02-06.md) | [review_gemini_round1](01_gemini_review_2026-02-06.md) | [synthesis_round1](synthesis_round1_2026-02-06.md) | 10/20 = 50% |
| 2 | [review_gpt_round2](review_gpt_round2_2026-02-06.md) | [review_gemini_round2](review_gemini_round2_2026-02-06.md) | [synthesis_round2](synthesis_round2_2026-02-06.md) | 20/20 = 100% |

---

## Appendix: Kiến trúc quyết định

```
┌─────────────────────────────────────────────────────────┐
│                    iPad (Client)                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐ │
│  │ WELCOME  │→ │ ORDERING │→ │BILL_REVIEW│→ │CLEANING│ │
│  │          │  │          │  │           │  │        │ │
│  │ Branding │  │ Menu     │  │ History   │  │Summary │ │
│  │ 始める   │  │ Cart     │  │ 追加注文  │  │ Staff  │ │
│  │          │  │ History  │  │           │  │ 3s LP  │ │
│  └──────────┘  └──────────┘  └───────────┘  └────────┘ │
│       ↑                            │              │      │
│       └────────────────────────────┘              │      │
│                                    ←──────────────┘      │
│                                                          │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │   SessionLog    │  │  Offline Queue   │               │
│  │ (analytics,     │  │ (orders, events) │               │
│  │  fire-forget)   │  │ sync on reconnect│               │
│  └────────┬────────┘  └────────┬─────────┘               │
│           │                    │                          │
└───────────┼────────────────────┼──────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ OrderEvent   │  │ TableSession │  │ SessionLog    │  │
│  │ (23 types,   │  │ (lifecycle)  │  │ (analytics)   │  │
│  │  source of   │  │              │  │               │  │
│  │  truth)      │  │              │  │               │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```
