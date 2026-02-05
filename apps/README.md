# Yakiniku Apps

Multi-app architecture với domain-based routing.

## Structure

```
apps/
├── web/                    # Customer website
│   ├── index.html          # Landing page
│   ├── css/style.css       # Mobile-first styles
│   ├── js/app.js           # Booking + Chat logic
│   └── assets/             # Images, fonts
│
├── dashboard/              # Staff/Admin dashboard (NEW - Static)
│   ├── index.html          # SPA entry point
│   ├── css/dashboard.css   # Dashboard styles
│   └── js/
│       ├── config.js       # Configuration
│       ├── websocket.js    # WebSocket manager
│       ├── api.js          # REST API client
│       ├── components.js   # UI components
│       ├── app.js          # Main app
│       └── pages/          # Page modules
│           ├── home.js
│           ├── bookings.js
│           ├── tables.js
│           └── customers.js
│
├── table-order/            # Table ordering system
├── kitchen/                # Kitchen display system
├── checkin/                # Self check-in kiosk
└── pos/                    # Point of sale
```

## Domain Routing

| App | Development | Production |
|-----|-------------|------------|
| web | http://localhost:8080 | https://yakiniku-jp |
| dashboard | http://localhost:8081 | https://dashboard.yakiniku-jp |
| api | http://localhost:8000 | https://api.yakiniku-jp |
| table-order | http://localhost:8082 | https://order.yakiniku-jp |
| kitchen | http://localhost:8083 | https://kitchen.yakiniku-jp |
| checkin | http://localhost:8084 | https://checkin.yakiniku-jp |
| pos | http://localhost:8085 | https://pos.yakiniku-jp |

## Quick Start

```bash
# Start all services
cd yakiniku

# 1. Backend API + WebSocket
cd backend && uvicorn app.main:app --reload --port 8000

# 2. Customer website
cd apps/web && python -m http.server 8080

# 3. Dashboard
cd apps/dashboard && python -m http.server 8081
```

## Tech Stack

| App | Frontend | Communication |
|-----|----------|---------------|
| web | Vanilla JS + AOS | REST API |
| dashboard | Vanilla JS | **WebSocket** + REST |
| table-order | Vanilla JS | WebSocket |
| kitchen | Vanilla JS | WebSocket |
| checkin | Vanilla JS | REST API |
| pos | Vanilla JS | REST API |

## WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard?branch=jinan');
```

### Subscribe to channels
```json
{"type": "subscribe", "channel": "bookings"}
{"type": "subscribe", "channel": "tables"}
```

### Server Events
```json
{"type": "booking:created", "data": {...}, "channel": "bookings"}
{"type": "booking:updated", "data": {...}, "channel": "bookings"}
{"type": "table:status", "data": {...}, "channel": "tables"}
{"type": "notification", "data": {"title": "...", "message": "..."}}
```

## Team Workflow

Mỗi app có domain riêng → dễ track và deploy độc lập:

1. **Development**: Mỗi app chạy trên port riêng
2. **CI/CD**: Build và deploy từng app độc lập
3. **Monitoring**: Metrics theo subdomain
4. **Team assignment**: Mỗi team quản lý app riêng

Xem [shared/config/domains.toml](../shared/config/domains.toml) để config chi tiết.
