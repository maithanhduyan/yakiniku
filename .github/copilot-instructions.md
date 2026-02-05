# Yakiniku.io - AI Agent Instructions

## Project Overview
Multi-tenant Japanese Yakiniku (BBQ) restaurant platform with modular apps: customer website, table ordering (iPad), kitchen display, POS, check-in kiosk, and admin dashboard.

## Architecture

```
yakiniku/
├── apps/                   # Frontend applications (Vanilla JS)
│   ├── web/                # Customer website + booking
│   ├── table-order/        # iPad ordering (offline-capable)
│   ├── kitchen/            # Kitchen display system
│   ├── pos/                # Point of sale
│   ├── checkin/            # Self check-in kiosk
│   └── dashboard/          # Admin SPA
├── backend/                # FastAPI + SQLAlchemy (async)
│   └── app/
│       ├── domains/        # Domain-driven modules (NEW)
│       │   ├── tableorder/ # Event-sourced order system
│       │   ├── kitchen/
│       │   ├── pos/
│       │   └── checkin/
│       ├── routers/        # Legacy REST endpoints
│       └── models/         # SQLAlchemy models
└── shared/                 # Cross-app config & branding
```

## Development Commands

```bash
# Backend (required first) - Use VS Code task "Backend: Start"
cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend URLs** (Live Server port 5500):
- `http://127.0.0.1:5500/apps/table-order/`
- `http://127.0.0.1:5500/apps/kitchen/`
- `http://127.0.0.1:5500/apps/dashboard/`

## Critical Patterns

### 1. Frontend Config Pattern (`apps/*/js/config.js`)
Each app has frozen CONFIG object with API_HOST auto-detection:
```javascript
const API_HOST = window.location.hostname;  // Avoids CORS issues
const CONFIG = {
    API_URL: `http://${API_HOST}:8000/api`,
    WS_URL: `ws://${API_HOST}:8000/ws`,
    BRANCH_CODE: 'hirama',  // Default branch
};
```

### 2. Domain-Driven Backend (`backend/app/domains/`)
New features go in domains, not routers:
- `domains/tableorder/` - Event-sourced with `events.py`, `event_service.py`
- Each domain: `router.py`, `models.py`, `schemas.py`
- Registered in `main.py` under "Domain Routers" section

### 3. Demo Mode (No FK Constraints)
Models allow demo data without seeded DB:
- `Order.table_id` - No FK to tables
- `OrderItem.menu_item_id` - No FK to menu_items
- Frontend sends `item_name`, `item_price` with orders

### 4. Event Sourcing (`tableorder/events.py`)
```python
EventType.ORDER_CREATED, GATEWAY_SENT, GATEWAY_FAILED  # Track delivery
EventSource.TABLE_ORDER, KITCHEN, POS, SYSTEM          # Origin tracking
```

### 5. CORS Configuration (`backend/app/config.py`)
Allowed origins include both `localhost` and `127.0.0.1` variants for ports 5500, 8080-8084.

## API Conventions

- **Trailing slash required**: POST `/api/tableorder/` (not `/api/tableorder`)
- **Branch code**: Query param `?branch_code=hirama` or header `X-Branch`
- **WebSocket**: `ws://host:8000/ws?branch_code=hirama&table_id=xxx`

## Testing with Playwright MCP

1. Start backend first (task "Backend: Start")
2. Navigate to `http://127.0.0.1:5500/apps/table-order/`
3. Test flows: Menu → Cart → Submit Order
4. Check backend logs for `200 OK`

## Language Usage
- **UI**: Japanese (日本語)
- **Code/Comments**: English
- **Internal docs**: Vietnamese

## Common Issues

| Issue | Solution |
|-------|----------|
| CORS error on submit | Ensure URL has trailing slash, use same hostname |
| FK violation on demo | Models should not have FK constraints for demo fields |
| WebSocket 403 | Expected in demo mode, app falls back to offline |
| Menu not loading | Check `branch_code` param, uses offline fallback |

## Key Files
- [backend/app/main.py](backend/app/main.py) - Router registration
- [backend/app/config.py](backend/app/config.py) - CORS origins, DB URL
- [apps/table-order/js/config.js](apps/table-order/js/config.js) - Frontend config pattern
- [backend/app/domains/tableorder/events.py](backend/app/domains/tableorder/events.py) - Event types

## Documentation
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Multi-tenant design
- [docs/BACKEND.md](docs/BACKEND.md) - API & database schema