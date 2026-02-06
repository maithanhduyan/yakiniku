# 🔧 Gemini (Pragmatist) — Round 1 Review | 2026-02-06

## Tổng quan quan điểm

Sau khi đọc kỹ codebase hiện tại, tôi thấy **chúng ta đã có 70% infrastructure cần thiết** — `TableSession` model ở backend, `OrderEvent` với 23 event types, `session_id` đã flow từ frontend xuống API. Vấn đề không phải thiếu kiến trúc mà là **thiếu lifecycle management**: session được tạo nhưng không bao giờ kết thúc, cart key chung cho mọi session (`table_order_cart`), và history lưu theo `TABLE_ID` thay vì `session_id`. Đây toàn là bug dễ fix, không phải redesign.

Quan điểm của tôi rất rõ: **đừng xây thêm event sourcing ở client-side**. localStorage không phải event store — nó là cache. Backend đã có `OrderEvent` table với full indexing, composite indexes, correlation tracking. Việc duplicate event sourcing ở frontend chỉ tạo thêm complexity mà không mang lại giá trị. Client chỉ cần: (1) biết session đang ở phase nào, (2) cache cart + history cho offline, (3) sync khi có mạng. Thế thôi.

Với 2-4 tuần Vanilla JS, tôi đề xuất tập trung vào **3 thứ duy nhất**: Session lifecycle (start → order → end), localStorage scoped theo session, và welcome/cleaning screen. Các tính năng fancy như grilling timer, AI upsell, course-based ordering — để sau. Một nhà hàng yakiniku ở Kawasaki cần iPad chạy ổn định, staff không cần training, khách đặt món được trong 10 giây. Không cần gì hơn.

---

## Q1: Session Lifecycle Design

### Minimum Viable: 3 Phases, Không Phải 6

Đề bài suggest flow 6 bước. Thực tế nhà hàng chỉ cần **3 phases** trên iPad:

```
WELCOME → ORDERING → CLEANING
```

**Tại sao chỉ 3?**
- "Khách vào bàn" = staff mở iPad, nhấn "Start" → `WELCOME → ORDERING`
- "Ăn" không phải phase riêng — khách vẫn gọi thêm món khi đang ăn (đặc thù yakiniku!)
- "Thanh toán" xảy ra ở POS, không phải iPad → iPad nhận event `SESSION_PAID` từ WebSocket
- "Dọn bàn" = `CLEANING` → staff nhấn "Done" → quay về `WELCOME`

### UI cho từng Phase

```
┌─────────────────────────────────────────────────────────┐
│ PHASE: WELCOME                                          │
│                                                         │
│              🔥 焼肉 じなん 🔥                           │
│              Yakiniku Jian                              │
│                                                         │
│              テーブル T5                                  │
│              Table T5                                    │
│                                                         │
│         ┌─────────────────────────┐                     │
│         │   ご来店ありがとう       │                     │
│         │  ございます！            │                     │
│         │                         │                     │
│         │  画面をタッチして        │                     │
│         │  ご注文ください          │                     │
│         │                         │                     │
│         │   [ タッチしてスタート ]  │                     │
│         └─────────────────────────┘                     │
│                                                         │
│  🔒 Staff: Long-press 3s for admin                      │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│ PHASE: ORDERING (= current app, unchanged)              │
│ ┌────────┐ ┌──────────────────────────────────┐ ┌────┐ │
│ │ 🥩肉   │ │  Menu Grid (existing)            │ │🛒 3│ │
│ │ 🍺飲物 │ │                                  │ │    │ │
│ │ 🥗サラダ│ │  [card] [card] [card] [card]     │ │    │ │
│ │ 🍚ご飯 │ │  [card] [card] [card] [card]     │ │    │ │
│ │ 🍲一品 │ │                                  │ │    │ │
│ │ 🍨デザ │ │          < 1/2 >                 │ │    │ │
│ │ 🍱セット│ │                                  │ │    │ │
│ └────────┘ └──────────────────────────────────┘ └────┘ │
│ ┌──────────────────────────────────────────────────────┐│
│ │ 🛒 3品 ¥4,500                    [注文する]          ││
│ └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│ PHASE: CLEANING (locked - chỉ staff unlock)             │
│                                                         │
│              🧹 テーブル準備中                            │
│              Preparing table...                         │
│                                                         │
│              T5 - Session #a1b2c3                        │
│              Total: ¥12,500 | 8 items                   │
│              Duration: 72 min                           │
│                                                         │
│         ┌─────────────────────────┐                     │
│         │  🔒 Staff only          │                     │
│         │                         │                     │
│         │  [ 準備完了 ]            │                     │
│         │  (Long-press 3s)        │                     │
│         └─────────────────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Transitions

| From | To | Trigger | Auto/Manual |
|------|----|---------|-------------|
| WELCOME | ORDERING | Khách touch screen | **Auto** (khách tự làm) |
| ORDERING | CLEANING | POS gửi `SESSION_PAID` via WS **hoặc** staff long-press | **Manual** (staff/POS) |
| CLEANING | WELCOME | Staff nhấn "準備完了" (long-press 3s) | **Manual** (staff) |

### Implementation — State Machine đơn giản

```javascript
// Thêm vào app.js — KHÔNG cần file mới
const SESSION_PHASES = { WELCOME: 'welcome', ORDERING: 'ordering', CLEANING: 'cleaning' };

// Thêm vào state object hiện tại
// sessionPhase: SESSION_PHASES.WELCOME,

function transitionTo(newPhase) {
    const allowed = {
        welcome: ['ordering'],
        ordering: ['cleaning'],
        cleaning: ['welcome']
    };

    if (!allowed[state.sessionPhase]?.includes(newPhase)) {
        console.warn(`Invalid transition: ${state.sessionPhase} → ${newPhase}`);
        return false;
    }

    const oldPhase = state.sessionPhase;
    state.sessionPhase = newPhase;

    // Persist
    localStorage.setItem(`session_phase_${TABLE_ID}`, newPhase);

    // Handle side effects
    switch (newPhase) {
        case 'ordering':
            startNewSession();  // Generate new session_id, clear old cart
            showOrderingUI();
            break;
        case 'cleaning':
            endCurrentSession();
            showCleaningUI();
            break;
        case 'welcome':
            clearSessionData();
            showWelcomeUI();
            break;
    }

    // Fire event to backend (best-effort, don't block)
    fireSessionEvent(oldPhase, newPhase);
    return true;
}

function startNewSession() {
    // New session ID
    state.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('session_id', state.sessionId);

    // Clear cart (scoped to new session)
    state.cart = [];
    localStorage.removeItem(`cart_${TABLE_ID}`);

    // Clear history
    state.orderHistory = [];
    localStorage.removeItem(`history_${TABLE_ID}`);
}

function endCurrentSession() {
    // Save summary for analytics (lightweight)
    const summary = {
        sessionId: state.sessionId,
        tableId: TABLE_ID,
        totalItems: state.orderHistory.reduce((s, i) => s + i.quantity, 0),
        totalAmount: state.orderHistory.reduce((s, i) => s + i.price * i.quantity, 0),
        duration: Date.now() - parseInt(state.sessionId.split('_')[1]),
        endedAt: new Date().toISOString()
    };

    // Append to completed sessions log (keep last 50)
    const log = JSON.parse(localStorage.getItem(`completed_sessions_${TABLE_ID}`) || '[]');
    log.push(summary);
    if (log.length > 50) log.splice(0, log.length - 50);
    localStorage.setItem(`completed_sessions_${TABLE_ID}`, JSON.stringify(log));
}

function fireSessionEvent(oldPhase, newPhase) {
    const eventType = newPhase === 'ordering' ? 'session.started' : 'session.ended';

    fetch(`${CONFIG.API_URL}/tableorder/events/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event_type: eventType,
            event_source: 'table-order',
            branch_code: CONFIG.BRANCH_CODE,
            table_id: TABLE_ID,
            session_id: state.sessionId,
            data: { from_phase: oldPhase, to_phase: newPhase }
        })
    }).catch(err => console.log('Event fire failed (offline ok):', err));
}
```

### Edge Cases — Giải pháp thực tế

| Edge Case | Giải pháp | Lý do |
|-----------|-----------|-------|
| **Khách bỏ về không trả tiền** | Staff long-press → CLEANING, POS handles refund riêng | iPad không cần biết payment status |
| **iPad crash/restart** | Đọc `session_phase_${TABLE_ID}` từ localStorage khi init | Phase persist qua crash |
| **Đổi bàn** | Staff kết thúc session cũ, start mới ở bàn mới. iPad bàn cũ auto → CLEANING | Đổi bàn là rare, manual OK |
| **Mất điện** | Welcome screen là default. Nếu localStorage còn session → resume ORDERING | Fail-safe: default WELCOME |
| **2 khách cùng ngồi xuống** | Không xảy ra — 1 iPad/bàn, staff kiểm soát | Over-engineering nếu handle |

**Thời gian ước tính**: 3-4 ngày cho state machine + 3 screens.

---

## Q2: Event Sourcing Strategy

### Quan điểm thẳng: KHÔNG làm event sourcing ở client

**Lý do:**

1. **Backend đã có `OrderEvent` table** với full event sourcing — 23 event types, composite indexes, correlation tracking. Tại sao duplicate?
2. **localStorage không phải event store** — nó là key-value cache. Không có query, không có index, không có transaction. Max ~5MB trên iPad Safari.
3. **Replay from events ở client** = over-engineering cho Vanilla JS app. State machine đơn giản hơn 10x và dễ debug hơn.
4. **Offline events queue** thì có — nhưng đó là message queue, không phải event sourcing.

### Cái cần làm: Offline Event Queue (Simple)

```javascript
// ============ Offline Queue ============
// Khi offline, queue events. Khi online, flush.

const QUEUE_KEY = `offline_queue_${TABLE_ID}`;

function queueEvent(eventData) {
    // Always try to send immediately
    if (state.isOnline) {
        sendEvent(eventData).catch(() => {
            // Failed? Queue it.
            pushToQueue(eventData);
        });
    } else {
        pushToQueue(eventData);
    }
}

function pushToQueue(eventData) {
    const queue = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
    queue.push({
        ...eventData,
        queued_at: new Date().toISOString(),
        client_id: state.sessionId  // For dedup on server
    });
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

async function flushQueue() {
    const queue = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
    if (queue.length === 0) return;

    console.log(`Flushing ${queue.length} queued events...`);

    // Send as batch — single API call
    try {
        const response = await fetch(`${CONFIG.API_URL}/tableorder/events/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ events: queue })
        });

        if (response.ok) {
            localStorage.removeItem(QUEUE_KEY);
            console.log('Queue flushed successfully');
        }
    } catch (err) {
        console.log('Queue flush failed, will retry:', err);
    }
}

async function sendEvent(eventData) {
    return fetch(`${CONFIG.API_URL}/tableorder/events/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
    });
}

// Flush when coming back online
window.addEventListener('online', () => {
    state.isOnline = true;
    flushQueue();
});
```

### localStorage Schema — Minimal & Flat

```javascript
// KEY NAMING CONVENTION: yakiniku_{scope}_{TABLE_ID}

// Current session state
localStorage['session_id']                     // "session_1738857600_x7k2m"
localStorage['session_phase_T5']               // "ordering"

// Cart (current session only)
localStorage['cart_T5']                        // JSON: [{id, name, price, qty, notes}]

// Order history (current session only)
localStorage['history_T5']                     // JSON: [{name, qty, price, orderedAt, delivered}]

// Offline event queue
localStorage['offline_queue_T5']               // JSON: [{event_type, data, queued_at}]

// Completed sessions log (lightweight summaries)
localStorage['completed_sessions_T5']          // JSON: [{sessionId, total, items, duration}]

// App config (persists across sessions)
localStorage['table_id']                       // "T5"
localStorage['preferred_lang']                 // "ja"
```

**Tổng dung lượng ước tính:** ~50KB max per table. Không bao giờ gần 5MB limit.

### Sync Strategy

| Data | Sync khi nào | Method |
|------|-------------|--------|
| Orders | Ngay khi submit (existing flow) | POST `/api/tableorder/` |
| Session events | Best-effort, fire-and-forget | POST `/api/tableorder/events/` |
| Offline queue | Khi reconnect | Batch POST |
| Completed session summaries | Không sync — local analytics only | N/A |

### Retention Policy

```javascript
// Tự động cleanup khi transition CLEANING → WELCOME
function clearSessionData() {
    localStorage.removeItem(`cart_${TABLE_ID}`);
    localStorage.removeItem(`history_${TABLE_ID}`);
    // Keep: session_phase, completed_sessions, table_id, preferred_lang
}

// Completed sessions: keep last 50 (roughly 1 week of data cho 1 bàn)
// Auto-trim trong endCurrentSession() — đã implement ở trên
```

### Conflict Resolution khi Reconnect

**Đơn giản: Last-Write-Wins, backend là source of truth.**

Không cần CRDT, không cần vector clocks. Lý do:
1. Mỗi iPad = 1 bàn = 1 writer. Không có concurrent writes.
2. Order submission là idempotent (backend check duplicate bằng `session_id` + `order_number`).
3. Events là append-only — không conflict by definition.

Trường hợp duy nhất cần handle: **double submit khi offline → online**. Solution: thêm `client_order_id` (UUID) vào mỗi order, backend dedup.

```javascript
// Thêm vào submitOrder()
const clientOrderId = crypto.randomUUID(); // Built-in, mọi browser modern
orderData.client_order_id = clientOrderId;
```

**Thời gian ước tính**: 2-3 ngày cho offline queue + localStorage migration.

---

## Q3: Yakiniku-specific UX Features

### ROI Analysis — Thực tế nhất trước

| Feature | Customer Delight | Dev Effort | ROI | Verdict |
|---------|-----------------|------------|-----|---------|
| Course-based menu tabs | ⭐⭐⭐⭐ | 1 ngày | **Cao** | ✅ Ship now |
| "Gọi thêm" prompt sau 15 phút | ⭐⭐⭐ | 0.5 ngày | **Cao** | ✅ Ship now |
| Pairing suggestion (static) | ⭐⭐⭐ | 1 ngày | **Trung bình** | ✅ Ship now |
| Grilling timer | ⭐⭐ | 3-5 ngày | **Thấp** | ❌ Phase 2 |
| AI-based upsell | ⭐⭐ | 2 tuần+ | **Thấp** | ❌ Phase 3 |
| 食べ放題 mode | ⭐⭐⭐⭐ | 3-5 ngày | **Cao** | ⚠️ Phase 2 (nếu có plan) |
| Course/tempo ordering | ⭐⭐ | 1 tuần | **Thấp** | ❌ Phase 3 |

### Feature 1: Course-based Category Ordering (1 ngày)

Thực ra **đã có sẵn**! Categories trong demo menu đã theo thứ tự yakiniku tự nhiên:
```
🥩 肉 → 🍺 飲物 → 🥗 サラダ → 🍚 ご飯 → 🍲 一品 → 🍨 デザート → 🍱 セット
```

Chỉ cần thêm **course labels** và **"recommended now" indicator**:

```javascript
// Course timing logic - dựa trên thời gian session, không phải AI
function getRecommendedCourse() {
    const sessionMinutes = getSessionDurationMinutes();

    if (sessionMinutes < 5) return 'drinks';      // Đầu tiên: gọi đồ uống
    if (sessionMinutes < 10) return 'meat';        // Bắt đầu nướng
    if (sessionMinutes < 30) return 'meat';        // Vẫn đang nướng
    if (sessionMinutes < 50) return 'rice';        // Gần no → cơm/mì
    if (sessionMinutes < 70) return 'dessert';     // Tráng miệng
    return null;  // Hết recommend
}

// Render course indicator trên category tab
function renderCategories() {
    const recommended = getRecommendedCourse();
    const container = document.getElementById('categoryList');
    container.innerHTML = state.categories.map(cat => `
        <div class="category-tab ${cat.category === state.currentCategory ? 'active' : ''}
             ${cat.category === recommended ? 'recommended' : ''}"
             onclick="selectCategory('${cat.category}')">
            <span class="cat-icon">${cat.icon}</span>
            <span class="cat-label">${cat.category_label}</span>
            ${cat.category === recommended ? '<span class="rec-dot">●</span>' : ''}
        </div>
    `).join('');
}
```

CSS cho recommended dot:
```css
.category-tab.recommended { border-color: var(--accent-orange); }
.rec-dot { color: var(--accent-orange); font-size: 8px; position: absolute; top: 4px; right: 4px; }
```

### Feature 2: "Gọi thêm không?" Prompt (0.5 ngày)

Yakiniku = khách gọi nhiều lần. Nhưng đừng annoy — chỉ hỏi **1 lần**, sau khi đã order và im lặng 15 phút.

```javascript
let reorderPromptShown = false;

function checkReorderPrompt() {
    if (reorderPromptShown) return;
    if (state.orderHistory.length === 0) return;

    const lastOrderTime = new Date(state.orderHistory[state.orderHistory.length - 1].orderedAt);
    const minutesSinceLastOrder = (Date.now() - lastOrderTime.getTime()) / 60000;

    if (minutesSinceLastOrder >= 15) {
        reorderPromptShown = true;
        showReorderSuggestion();
    }
}

function showReorderSuggestion() {
    // Suggest: drinks refill + rice/noodle (typical yakiniku pattern)
    showNotification('追加注文はいかがですか？🍺🍚', 'info', 5000);
}

// Check every 5 minutes
setInterval(checkReorderPrompt, 5 * 60 * 1000);
```

### Feature 3: Static Pairing Suggestions (1 ngày)

Không cần AI. Yakiniku pairing là predictable:

```javascript
// Pairing rules — hardcoded, curated by restaurant
const PAIRINGS = {
    'meat': ['drinks', 'salad'],           // Thịt → Bia + Salad
    'drinks': ['meat', 'side'],             // Uống → Thịt + Snack
    'rice': ['side'],                       // Cơm → Canh
    'dessert': ['drinks'],                  // Tráng miệng → Trà
};

// Hiển thị ở cuối modal chi tiết món
function getPairingText(currentCategory) {
    const pairs = PAIRINGS[currentCategory];
    if (!pairs) return '';

    const suggestions = pairs.map(catKey => {
        const cat = state.categories.find(c => c.category === catKey);
        return cat ? `${cat.icon} ${cat.category_label}` : '';
    }).filter(Boolean);

    return suggestions.length > 0
        ? `💡 おすすめ: ${suggestions.join('、')}もいかがですか？`
        : '';
}
```

### Grilling Timer — Tại sao KHÔNG nên làm bây giờ

1. **Phức tạp UX**: Timer cần biết loại thịt, độ dày, mức chín → thêm 3-4 screens
2. **Liability**: Nếu timer sai → khách ăn thịt sống → vấn đề pháp lý
3. **Không ai nhìn iPad khi đang nướng**: Khách nướng bằng mắt + kinh nghiệm, không bằng timer
4. **Alternative đủ tốt**: Thêm `cooking_note` vào menu item description. VD: "焼き時間目安: 片面30秒" (thời gian nướng: mỗi mặt 30 giây). Zero dev effort, chỉ cần data.

### 食べ放題 (All-You-Can-Eat) Mode — Phase 2 nhưng design bây giờ

Nếu nhà hàng có plan 食べ放題, đây là killer feature. Nhưng cần backend changes (time limit, menu filtering, pricing rules). Design bây giờ, build sau:

```javascript
// Chỉ cần thêm vào session state
// sessionType: 'alacarte' | 'tabehodai_90' | 'tabehodai_120'
// tabehodaiEndTime: timestamp (nếu tabehodai)

// UI change: hiển thị countdown timer ở header
// Menu change: filter items theo plan (一部の肉は食べ放題対象外)
// Order change: không hiển thị giá (đã included)
```

**Thời gian ước tính**: 2 ngày cho 3 tính năng (course labels + reorder prompt + static pairing).

---

## Q4: "Dọn bàn" Mode & Staff Handoff

### Thiết kế tối giản nhất mà vẫn hoạt động

**Nguyên tắc**: iPad ở nhà hàng phải **dummy-proof**. Staff busy, tay ướt, tiếng ồn. Mọi thứ phải 1-2 tap max.

### Ai trigger phase change?

| Transition | Trigger | Tại sao |
|-----------|---------|---------|
| ORDERING → CLEANING | **POS gửi WebSocket event** (primary) | POS biết khi nào thanh toán xong |
| ORDERING → CLEANING | Staff long-press trên iPad (backup) | Khi POS offline hoặc khách bỏ về |
| CLEANING → WELCOME | Staff long-press "準備完了" | Chỉ staff mới biết bàn sạch chưa |

### Staff Protection: Long-Press Pattern

Không dùng PIN code (staff quên, chậm). Long-press 3 giây = đủ để ngăn khách nhấn nhầm.

```javascript
// Long-press handler — generic, reusable
function setupLongPress(element, callback, duration = 3000) {
    let timer = null;
    let progressEl = null;

    element.addEventListener('touchstart', (e) => {
        e.preventDefault();
        progressEl = element.querySelector('.long-press-progress');
        if (progressEl) {
            progressEl.style.transition = `width ${duration}ms linear`;
            progressEl.style.width = '100%';
        }
        timer = setTimeout(() => {
            // Haptic feedback (iPad supports)
            if (navigator.vibrate) navigator.vibrate(50);
            callback();
        }, duration);
    });

    element.addEventListener('touchend', () => {
        clearTimeout(timer);
        if (progressEl) {
            progressEl.style.transition = 'none';
            progressEl.style.width = '0%';
        }
    });

    element.addEventListener('touchcancel', () => {
        clearTimeout(timer);
        if (progressEl) {
            progressEl.style.transition = 'none';
            progressEl.style.width = '0%';
        }
    });
}
```

### CLEANING Screen — Minimal Info

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  🧹 テーブル準備中 / Preparing Table                     │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │                                             │       │
│  │  T5 — 本日 3回目                             │       │
│  │  滞在時間: 1時間12分                          │       │
│  │  注文数: 8品  合計: ¥12,500                  │       │
│  │                                             │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │                                             │       │
│  │  ██████████░░░░░░░░░░  長押しで完了          │       │
│  │                                             │       │
│  │  [ 準備完了 — 3秒長押し ]                     │       │
│  │                                             │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  ※ テーブルの清掃が終わったら長押ししてください            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Tại sao hiện summary?** → Staff biết bàn này đã phục vụ bao nhiêu, useful cho shift handoff.

### WELCOME Screen — Cho khách mới

```javascript
function showWelcomeUI() {
    // Hide ordering UI
    document.getElementById('mainContent').style.display = 'none';

    // Show welcome
    const welcome = document.getElementById('welcomeScreen');
    welcome.classList.add('active');
    welcome.innerHTML = `
        <div class="welcome-container">
            <div class="welcome-logo">🔥</div>
            <h1 class="welcome-title">焼肉 じなん</h1>
            <p class="welcome-subtitle">Yakiniku Jian</p>
            <p class="welcome-table">テーブル ${state.tableNumber}</p>
            <button class="welcome-start-btn" onclick="transitionTo('ordering')">
                タッチしてご注文
            </button>
            <p class="welcome-hint">Touch to start ordering</p>
        </div>
    `;
}
```

### WebSocket Integration cho POS → iPad

```javascript
// Thêm vào handleWebSocketMessage() hiện tại
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'order_status_changed':
            if (data.new_status === 'ready') {
                showNotification(t('notify.orderReady', { number: data.order_number }), 'success');
            }
            break;
        case 'menu_updated':
            loadMenu();
            break;
        // === NEW ===
        case 'session_paid':
            if (data.table_id === TABLE_ID) {
                showNotification('お会計ありがとうございました！', 'success', 3000);
                setTimeout(() => transitionTo('cleaning'), 3000);
            }
            break;
        case 'session_ended':
            if (data.table_id === TABLE_ID && state.sessionPhase === 'ordering') {
                transitionTo('cleaning');
            }
            break;
    }
}
```

**Thời gian ước tính**: 2-3 ngày cho welcome screen + cleaning screen + long-press + WS handler.

---

## Q5: Data Architecture

### localStorage Schema — Final Design

```
┌─────────────────────────────────────────────────────────────────┐
│ KEY                              │ VALUE          │ LIFECYCLE   │
├─────────────────────────────────────────────────────────────────┤
│ PERSISTENT (survive sessions)                                   │
├─────────────────────────────────────────────────────────────────┤
│ table_id                         │ "T5"           │ Forever     │
│ preferred_lang                   │ "ja"           │ Forever     │
│ session_phase_{TABLE_ID}         │ "ordering"     │ Forever     │
│ completed_sessions_{TABLE_ID}    │ [{summary}]    │ Last 50     │
├─────────────────────────────────────────────────────────────────┤
│ SESSION-SCOPED (cleared on CLEANING → WELCOME)                  │
├─────────────────────────────────────────────────────────────────┤
│ session_id                       │ "session_..."  │ Per session │
│ cart_{TABLE_ID}                  │ [{item}]       │ Per session │
│ history_{TABLE_ID}               │ [{order}]      │ Per session │
│ offline_queue_{TABLE_ID}         │ [{event}]      │ Per session │
└─────────────────────────────────────────────────────────────────┘
```

### Migration từ Schema hiện tại

Cần migrate 2 keys:
```javascript
// Run once on app init
function migrateLocalStorage() {
    // Old: 'table_order_cart' → New: 'cart_{TABLE_ID}'
    const oldCart = localStorage.getItem('table_order_cart');
    if (oldCart) {
        localStorage.setItem(`cart_${TABLE_ID}`, oldCart);
        localStorage.removeItem('table_order_cart');
    }

    // Old: 'yakiniku_history_{TABLE_ID}' → New: 'history_{TABLE_ID}'
    const oldHistory = localStorage.getItem(`yakiniku_history_${TABLE_ID}`);
    if (oldHistory) {
        localStorage.setItem(`history_${TABLE_ID}`, oldHistory);
        localStorage.removeItem(`yakiniku_history_${TABLE_ID}`);
    }

    localStorage.setItem('migration_v2', 'done');
}

// Gọi 1 lần
if (!localStorage.getItem('migration_v2')) {
    migrateLocalStorage();
}
```

### Completed Session Summary Schema

```javascript
// Mỗi entry ~200 bytes. 50 entries = ~10KB. Rất nhẹ.
{
    "sessionId": "session_1738857600_x7k2m",
    "tableId": "T5",
    "branchCode": "hirama",
    "guestCount": 4,
    "totalItems": 8,
    "totalAmount": 12500,
    "orderCount": 3,            // Số lần gọi món
    "duration": 4320000,        // ms (72 phút)
    "startedAt": "2026-02-06T18:00:00Z",
    "endedAt": "2026-02-06T19:12:00Z",
    "topCategory": "meat"       // Category gọi nhiều nhất
}
```

### Staff Analytics — Đâu cần gì phức tạp

Staff cần gì từ session data? Hỏi thật: **gần như không gì từ iPad**. Analytics nên ở **dashboard app** (đã có), đọc từ backend database.

iPad chỉ cần hiển thị trên CLEANING screen:
- Số session hôm nay cho bàn này (đếm từ `completed_sessions`)
- Session duration trung bình
- Doanh thu bàn hôm nay

```javascript
function getTodayStats() {
    const log = JSON.parse(localStorage.getItem(`completed_sessions_${TABLE_ID}`) || '[]');
    const today = new Date().toDateString();
    const todaySessions = log.filter(s => new Date(s.endedAt).toDateString() === today);

    return {
        count: todaySessions.length,
        avgDuration: todaySessions.length > 0
            ? Math.round(todaySessions.reduce((s, x) => s + x.duration, 0) / todaySessions.length / 60000)
            : 0,
        totalRevenue: todaySessions.reduce((s, x) => s + x.totalAmount, 0)
    };
}
```

### Privacy — Giữ đơn giản

**iPad không lưu dữ liệu cá nhân (PII).**

Kiểm tra:
- ❌ Không có tên khách
- ❌ Không có email/phone
- ❌ Không có payment info
- ✅ Chỉ có: order items, prices, timestamps

→ **Không cần GDPR compliance ở client side**. Backend xử lý PII (từ booking, checkin apps). Table-order app anonymous by design.

Nếu sau này thêm loyalty program (QR scan → link customer), lúc đó mới cần xử lý privacy. Nhưng đó là Phase 3+.

---

## Tổng kết & Priorities

### Sprint Plan: 2 tuần

```
┌───────────────────────────────────────────────────────────┐
│ WEEK 1 (5 ngày)                                          │
├───────────────────────────────────────────────────────────┤
│ Day 1-2: Session State Machine                            │
│   - 3 phases: WELCOME → ORDERING → CLEANING              │
│   - transitionTo() + phase persistence                    │
│   - localStorage migration (old → new keys)               │
│                                                           │
│ Day 3-4: Welcome & Cleaning Screens                       │
│   - Welcome screen (touch to start)                       │
│   - Cleaning screen (long-press to complete)              │
│   - Long-press handler utility                            │
│                                                           │
│ Day 5: Offline Queue + Cart Scoping                       │
│   - Cart key: cart_{TABLE_ID} (per session)               │
│   - History key: history_{TABLE_ID} (per session)         │
│   - Offline event queue with flush-on-reconnect           │
├───────────────────────────────────────────────────────────┤
│ WEEK 2 (5 ngày)                                          │
├───────────────────────────────────────────────────────────┤
│ Day 6: WebSocket Handler cho POS Events                   │
│   - Handle session_paid event                             │
│   - Auto-transition ORDERING → CLEANING                   │
│                                                           │
│ Day 7: Course-based Category Indicators                   │
│   - Recommended course dot based on time                  │
│   - Static pairing suggestions in item modal              │
│                                                           │
│ Day 8: Reorder Prompt + Session Summary                   │
│   - 15-min inactivity prompt                              │
│   - Completed session summary on CLEANING screen          │
│   - Today's table stats                                   │
│                                                           │
│ Day 9-10: Testing + Polish                                │
│   - iPad Safari testing (touch events, localStorage)      │
│   - Offline mode testing (airplane mode)                  │
│   - Demo mode verification (no backend needed)            │
│   - i18n for new strings (ja + en)                        │
└───────────────────────────────────────────────────────────┘
```

### Cái KHÔNG làm (và tại sao)

| Feature | Tại sao skip |
|---------|-------------|
| Client-side event sourcing | Backend đã có. Duplicate = waste |
| Grilling timer | Liability risk, khách không nhìn iPad khi nướng |
| AI upsell | Cần ML pipeline, overkill cho 1 nhà hàng |
| 食べ放題 mode | Cần backend pricing logic, Phase 2 |
| Course/tempo ordering | Over-constrain UX, yakiniku = tự do gọi |
| CRDT/vector clocks | 1 iPad = 1 writer, không có conflict |
| PIN code cho staff | Long-press 3s đủ rồi, PIN = chậm + quên |
| Customer authentication | Table-order app = anonymous, đó là feature |

### Files cần thay đổi

| File | Thay đổi |
|------|----------|
| [apps/table-order/js/app.js](apps/table-order/js/app.js) | Session state machine, phase transitions, localStorage migration, course recommendations |
| [apps/table-order/js/config.js](apps/table-order/js/config.js) | Thêm `SESSION_PHASES` constant |
| [apps/table-order/css/style.css](apps/table-order/css/style.css) | Welcome screen, cleaning screen, long-press animation, recommended dot |
| [apps/table-order/index.html](apps/table-order/index.html) | Thêm `<div id="welcomeScreen">`, `<div id="cleaningScreen">` |
| [backend/app/domains/tableorder/router.py](backend/app/domains/tableorder/router.py) | Thêm batch event endpoint |
| [apps/table-order/js/i18n/ja.json](apps/table-order/js/i18n/) | Thêm strings cho welcome/cleaning/prompt |

### Metrics để đánh giá thành công

1. **Session completion rate**: % sessions kết thúc đúng flow (WELCOME → ORDERING → CLEANING → WELCOME) vs bị abandon
2. **Avg session duration**: Tracking → optimize table turnover
3. **Orders per session**: > 2 = good (yakiniku đặc thù gọi nhiều lần)
4. **Offline queue depth**: Nếu >5 events thường xuyên → WiFi có vấn đề

**Bottom line**: 10 ngày code, 90% giá trị. Đừng over-engineer. Ship, observe, iterate.
