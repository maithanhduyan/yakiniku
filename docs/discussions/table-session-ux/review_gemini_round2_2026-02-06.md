# ⚡ Gemini Pragmatist — Round 2 Review | 2026-02-06

## Phản hồi cho các Compromise Proposals

### 1. 4-phase lifecycle (thêm BILL_REVIEW)
**Chấp nhận có điều kiện**

Tôi đã xem lại code hiện tại. Hàm `renderHistory()` trong app.js đã render order summary hoàn chỉnh — group by time, total items, total amount. BILL_REVIEW phase thực chất chỉ cần:

1. Khi khách bấm "会計" → set `session_phase = 'bill_review'`
2. Lock giao diện ordering, hiển thị full-screen order history (đã có sẵn!)
3. Thêm nút "追加注文" để quay lại ORDERING
4. Listen `session_paid` event từ WebSocket → auto-transition CLEANING

Ước tính: **~30-40 LOC** cho phase transition logic. UI tái sử dụng 100% `renderHistory()` hiện có. Không cần component mới.

**Điều kiện**: BILL_REVIEW KHÔNG thêm feedback form, KHÔNG thêm tipping UI, KHÔNG thêm bất kỳ feature nào ngoài read-only summary + "追加注文" button. Nếu ai đó muốn thêm feature vào phase này sau, đó là PR riêng.

### 2. Lightweight Event Logger
**Chấp nhận**

Đây KHÔNG phải event sourcing — đây là analytics log. Backend đã có `OrderEvent` model hoàn chỉnh với 23 EventTypes, indexes, correlation tracking. Client KHÔNG cần duplicate bất kỳ thứ gì trong đó.

Cái chúng ta thêm là:

```javascript
// ~35 LOC
const SessionLog = {
    _key: () => `session_log_${TABLE_ID}`,

    log(type, meta = {}) {
        try {
            const logs = JSON.parse(localStorage.getItem(this._key()) || '[]');
            logs.push({ type, ts: Date.now(), ...meta });
            localStorage.setItem(this._key(), JSON.stringify(logs));
        } catch (e) { /* ignore - analytics, not critical */ }
    },

    flush() {
        const logs = JSON.parse(localStorage.getItem(this._key()) || '[]');
        if (logs.length === 0) return;
        navigator.sendBeacon?.(`${CONFIG.API_URL}/tableorder/session-log/`,
            JSON.stringify({ table_id: TABLE_ID, session_id: SESSION_ID, logs }));
        localStorage.removeItem(this._key());
    },

    clear() { localStorage.removeItem(this._key()); }
};
```

Rồi rải `SessionLog.log('menu_item_viewed', { item_id })`, `SessionLog.log('order_submitted')`, v.v. vào ~15 chỗ trong app.js. Total: **~50 LOC** client-side.

Tại sao tôi accept: Dashboard app (`apps/dashboard/`) đã tồn tại. Data này feed trực tiếp vào dashboard analytics mà không cần phát triển gì thêm phía backend ngoài 1 endpoint nhận log. ROI rõ ràng: biết khách xem menu item nào nhưng không order → thông tin cho menu optimization.

**Lằn ranh đỏ**: Đây là fire-and-forget analytics. Nếu mất log → không sao. KHÔNG retry, KHÔNG block UI, KHÔNG ảnh hưởng ordering flow. Dùng `sendBeacon` hoặc offline queue, không phải dedicated sync engine.

### 3. Long-press 3s, no PIN
**Xác nhận**

Không thay đổi. Long-press 3s cho staff actions (CLEANING → WELCOME, session reset). PIN configurable per branch cho Phase 2 — đồng ý, nhưng Phase 2 nghĩa là KHÔNG code nó bây giờ. Không để lại placeholder, không để "TODO: add PIN check here". Clean code, ship now.

### 4. Grilling guide trong item modal
**Chấp nhận**

Modal hiện có: image, title, description, price, quantity selector, notes field. Thêm 1 tab "焼き方ガイド" chỉ là:

- 1 div ẩn/hiện khi bấm tab
- Content: static text + hình ảnh từ menu data (thêm `grilling_guide` field vào menu item schema)
- Không timer logic, không haptic, không flip alert

Ước tính: **~40 LOC** frontend + thêm 1 optional field vào menu item model. 1 ngày dev.

**Tại sao accept**: Đây là content, không phải feature. Không tăng maintenance burden. Giá trị cho khách: biết nướng bao lâu mà KHÔNG CÓ liability risk. Zero runtime complexity.

### 5. 2-tier sync
**Chấp nhận**

Đây gần như chính xác approach của tôi từ Round 1:

- **Tier 1 (Critical)**: Orders → `submitOrder()` hiện tại, đã hoạt động, đã tested. Không đổi.
- **Tier 2 (Best-effort)**: Session logs, analytics, call events → offline queue. Flush on reconnect hoặc mỗi 60s.

Flush logic:
```javascript
setInterval(() => { if (navigator.onLine) SessionLog.flush(); }, 60000);
window.addEventListener('online', () => SessionLog.flush());
```
**~5 LOC** cho flush scheduling.

### 6. LWW + dedup
**Xác nhận**

Không thay đổi. 1 iPad per table = 1 writer. `client_order_id` (UUID generated client-side trước khi submit) cho dedup khi retry — backend check `client_order_id` exists → return existing order thay vì tạo mới. ~10 LOC client + ~5 LOC backend.

### 7. Walkout timeout warning
**Chấp nhận có điều kiện**

Tôi đã suy nghĩ lại. Position ban đầu của tôi là "staff manual only", nhưng:

- **Thực tế**: quán đông, 1-2 staff phục vụ 15+ bàn. Quên kiểm tra 1 bàn đã im 30 phút là hoàn toàn có thể xảy ra.
- **Cost**: Một `setTimeout` + check last interaction timestamp. **~15 LOC**.

```javascript
let inactivityTimer;
function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        if (state.sessionPhase === 'ordering') {
            showNotification('🔔 30分間操作がありません', 'warning', 0);
            SessionLog.log('inactivity_warning');
        }
    }, 30 * 60 * 1000);
}
document.addEventListener('touchstart', resetInactivityTimer, { passive: true });
```

**Điều kiện**:
1. Notification CHỈ hiển thị trên iPad đó — KHÔNG gửi notification lên kitchen/POS.
2. KHÔNG auto-close session. Notification persistent cho đến khi staff dismiss.
3. Timer reset khi có bất kỳ touch event nào.

### 8. Crash recovery — atomic save
**Chấp nhận**

Orchestra đúng. Đây là bug thực sự trong code hiện tại:

```javascript
// Current order (BUGGY):
state.cart = [];           // cart cleared from state
saveCartToStorage();       // cart cleared from localStorage
// ... UI updates ...
state.orderHistory.push(...historyItems);  // later
saveHistoryToStorage();                     // history saved
```

Nếu crash giữa clear cart và save history: **cart mất, history chưa lưu**.

**Fix đơn giản — reorder operations:**

```javascript
// Fixed order (ATOMIC-ISH):
const historyItems = orderData.items.map(item => ({ /* ... */ }));
state.orderHistory.push(...historyItems);
saveHistoryToStorage();    // ← SAVE HISTORY FIRST

state.cart = [];
saveCartToStorage();       // ← THEN clear cart
```

Đây KHÔNG cần event replay. Đây là bug fix cơ bản, reorder 2 dòng code.

## LOC Estimates

| Component | Estimated LOC | Dev Days |
|-----------|--------------|----------|
| Session phase state machine (4 phases) | ~60 | 0.5 |
| BILL_REVIEW UI (reuse renderHistory) | ~40 | 0.5 |
| Lightweight event logger (SessionLog) | ~35 | 0.25 |
| Event log call sites (rải vào app.js) | ~15 | 0.25 |
| Flush scheduling | ~5 | 0 |
| Grilling guide tab in modal | ~40 | 1 |
| Walkout inactivity warning | ~15 | 0.25 |
| Crash recovery fix (reorder lines) | ~5 (net change) | 0.1 |
| client_order_id dedup | ~15 | 0.25 |
| Long-press staff unlock | ~30 | 0.5 |
| **Total** | **~260** | **3.6 days** |

So sánh:
- GPT Round 1 approach (full EventStore + 6 phases + CRDT): **800-1200 LOC, 8-12 dev days**
- Gemini Round 1 pure minimal: **~120 LOC, 2 dev days**
- **Compromise hiện tại: ~260 LOC, 3.6 dev days** — chấp nhận được.

## Remaining Concerns

1. **Backend endpoint cho session log**: Cần 1 endpoint `POST /api/tableorder/session-log/` để nhận analytics log. ~30 LOC backend.

2. **BILL_REVIEW → CLEANING transition**: Cần backend gửi `session_paid` event qua WebSocket. Cần verify WebSocket routing.

3. **Grilling guide content**: Ai tạo content? Dev cost 1 ngày, nhưng content cost có thể 2-3 ngày cho 30+ items. Phase 1 chỉ thêm field, nội dung populate dần.

4. **Testing**: 3.6 dev days chưa tính testing. Thêm 1-2 ngày manual testing. Total realistic: **~5-6 dev days**.

## Đánh giá tổng thể

**Accepted: 7/8 proposals** (1 confirmed, 2 accepted có điều kiện, 4 accepted hoàn toàn)
**Rejected: 0/8**
**Confirmed unchanged: 2/8** (#3 Long-press, #6 LWW)

Thứ tôi KHÔNG accept: bất cứ gì có chữ "replay", "CRDT", "reducer", hoặc "event store" ở phía client. Backend có `OrderEvent` model hoàn chỉnh — đó là single source of truth. Client là thin layer. Period.

**Tổng: ~260 LOC, ~5-6 dev days (including testing). Ship được trong 1 sprint.**
