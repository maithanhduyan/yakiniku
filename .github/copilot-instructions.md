# Yakiniku.io — AI Agent Instructions

## Project Overview
Multi-tenant Japanese Yakiniku (BBQ) restaurant platform. Vanilla JS frontend apps + FastAPI async backend. Default branch: `hirama`.

## Architecture

```
apps/                         # Vanilla JS frontends (no build step)
├── table-order/              # iPad ordering — 4-phase session lifecycle, offline-capable
├── kitchen/                  # KDS display — WebSocket-driven
├── dashboard/                # Admin SPA — class-based page routing
├── pos/                      # Point of sale
├── checkin/                  # Self check-in kiosk (largest domain: 539 lines)
└── web/                      # Customer website + booking
backend/app/
├── domains/                  # New features go HERE (not routers/)
│   ├── tableorder/           # Event-sourced: router, schemas, events, event_service, event_router
│   ├── kitchen/              # KDS: router only (imports shared models)
│   ├── pos/                  # Checkout: router + schemas
│   ├── checkin/              # ✅ Has OWN models (CheckIn, WaitingList with real FKs)
│   ├── booking/              # CRUD: router + schemas (re-exports legacy models)
│   └── shared/               # Cross-domain re-exports: Order, Table, Branch models + base schemas
├── routers/                  # Legacy REST endpoints (kept for backward compat)
├── models/                   # SQLAlchemy models (source of truth for DB schema)
└── services/                 # notification (SSE), chat (OpenAI), table_optimization
```

## Development

```bash
# Use VS Code task "Backend: Start" or:
cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontends via Live Server (port 5500) — NO build step needed:
# http://127.0.0.1:5500/table-order/
# http://127.0.0.1:5500/kitchen/
# http://127.0.0.1:5500/dashboard/

# Seed DB (CSV-driven, drops all tables first):
cd backend && .venv\Scripts\python.exe -m data.seed_data
```

- **No automated tests exist** — use Playwright MCP for E2E testing
- **No migrations** — uses `Base.metadata.create_all`; schema changes require drop+recreate
- **Dual DB**: SQLite (dev, auto-detected from URL) / PostgreSQL (prod, asyncpg)
- Package manager: `uv` — Python ≥3.13

## Critical Patterns

### Frontend CONFIG (every app: `apps/*/js/config.js`)
```javascript
const API_HOST = window.location.hostname;  // Dynamic — avoids CORS mismatch
const CONFIG = { API_URL: `http://${API_HOST}:8000/api`, WS_URL: `ws://${API_HOST}:8000/ws`, BRANCH_CODE: 'hirama' };
Object.freeze(CONFIG);
```
⚠️ Dashboard config hardcodes `localhost:8000` — inconsistent with table-order's dynamic pattern.

### Table-Order: 4-Phase Session State Machine
`WELCOME → ORDERING → BILL_REVIEW → CLEANING → WELCOME` (cyclic). Defined in `config.js` as `SESSION_PHASES` + `SESSION_TRANSITIONS`. Transitions validated by `transitionTo()` in app.js. Phase persisted in localStorage for crash recovery.
- WELCOME→ORDERING: generates new `session_id`
- ORDERING→BILL_REVIEW: fires `call-staff` event, renders bill summary
- BILL_REVIEW→ORDERING: "追加注文" (add more) allowed
- CLEANING→WELCOME: requires 3s long-press, calls `clearSessionData()`

### Domain Router Registration (`backend/app/main.py`)
Two-tier system — both coexist:
```python
# Legacy: app.include_router(menu.router, prefix="/api/menu")
# Domain: app.include_router(tableorder_router, prefix="/api/tableorder")
```
New features → create domain in `domains/`, register under "Domain Routers" section.

### Event Sourcing (tableorder only)
- `events.py`: `EventType` enum (25+ types), `EventSource` enum, `OrderEvent` model (append-only)
- `event_service.py`: `EventService` — log events, query timelines, detect gateway failures
- Correlation chain: `correlation_id` + `sequence_number` link related events across systems

### Demo Mode (No FK Constraints on Orders)
`Order.table_id`, `OrderItem.menu_item_id` — intentionally NO foreign keys. Frontend sends denormalized `item_name`, `item_price` with every order so the system works without seeded data.

### WebSocket (`backend/app/routers/websocket.py`)
- `/ws?branch_code=&table_id=` — table-order connections (auto-subscribes to `orders` + `table:{id}`)
- `/ws/dashboard?branch=` — dashboard connections (manual subscribe/unsubscribe)
- Channel pub/sub via `ConnectionManager` singleton, branch-scoped
- Frontend `WebSocketManager` class: auto-reconnect, event emitter pattern, `on(event, callback)` returns unsubscribe fn

## API Conventions

- **Trailing slash required on POST**: `/api/tableorder/` (not `/api/tableorder`)
- **Multi-tenancy**: `?branch_code=hirama` query param on most endpoints
- **CORS**: Both `localhost` and `127.0.0.1` for ports 5500, 8080-8084 (`backend/app/config.py`)
- **IDs**: UUID v4 as `String(36)`, never auto-increment — `default=lambda: str(uuid.uuid4())`
- **Async everywhere**: `async def` endpoints, `AsyncSession`, `await session.execute()`
- **Price type**: `Numeric(10,0)` in DB → arrives as string in JSON. Frontend must `Number(price)` before `.toLocaleString()`

## Language Convention
- **UI text**: Japanese (日本語) — translations in `apps/*/js/i18n/{ja,en}.js`
- **Code/comments**: English
- **Internal docs/comments**: Vietnamese (in services, some models)

## Common Pitfalls

| Symptom | Cause & Fix |
|---------|------------|
| CORS error on POST | Missing trailing slash in URL, or hostname mismatch (use `window.location.hostname`) |
| Menu API returns empty | `branch_code` mismatch — DB has `hirama`, check query param |
| Grid shows wrong item count | `calculateItemsPerPage()` ran while container was `hidden` — use `requestAnimationFrame` after showing |
| Price shows without commas | DB returns string "1800" — wrap with `Number()` before `toLocaleString()` |
| WebSocket 403 | No matching endpoint — table-order uses `/ws`, dashboard uses `/ws/dashboard` |
| FK violation | Order/OrderItem fields are intentionally FK-free for demo mode |

## Key Reference Files
- [backend/app/main.py](backend/app/main.py) — Router registration (legacy + domain)
- [backend/app/config.py](backend/app/config.py) — CORS origins, DB URL, default branch
- [backend/app/domains/tableorder/events.py](backend/app/domains/tableorder/events.py) — Event types & OrderEvent model
- [backend/app/domains/tableorder/event_service.py](backend/app/domains/tableorder/event_service.py) — Event sourcing service
- [apps/table-order/js/config.js](apps/table-order/js/config.js) — Frontend config + session phases
- [apps/table-order/js/app.js](apps/table-order/js/app.js) — State machine, SessionLog, offline fallback
- [backend/app/routers/websocket.py](backend/app/routers/websocket.py) — WebSocket connection manager
