# Yakiniku.io - AI Agent Instructions

## Project Overview
Multi-tenant Japanese Yakiniku (BBQ) restaurant management platform with booking widget, AI chat, and restaurant dashboard. **Mobile-first design** for customer website.

**Domain**: `yakiniku.io` - Platform for managing Yakiniku restaurant chains.

## Architecture (Multi-Tenant Ready)

```
yakiniku/
├── web/              # Customer website (static)
│   ├── index.html    # Main page
│   ├── css/style.css # Mobile-first styles (~1580 lines)
│   └── js/app.js     # Booking + chat logic (~710 lines)
├── backend/          # FastAPI server
│   └── app/          # Python application
├── dashboard/        # Admin panel (HTMX + Jinja2)
│   └── templates/    # Dashboard views
├── shared/           # Cross-component resources
└── docs/             # Architecture documentation
```

## Tech Stack
| Component | Technology |
|-----------|------------|
| Web | HTML5 + CSS3 + Vanilla JS + AOS |
| Backend | FastAPI + SQLAlchemy + OpenAI |
| Dashboard | HTMX + Jinja2 + TailwindCSS |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Cache | Redis |

## Development Commands

```bash
# Customer website
cd web && python -m http.server 8080

# Backend API
cd backend && uvicorn app.main:app --reload --port 8000

# Full stack (Docker)
docker-compose up -d
```

## Design System
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-color` | #1a1a1a | Dark background |
| `--accent-color` | #d4af37 | Gold accent |
| `--touch-target` | 48px | Mobile touch targets |

## Key Patterns

### 1. Mobile Touch Targets (48px minimum)
```css
.btn-booking { min-height: var(--touch-target); }
```

### 2. iOS Form Zoom Prevention
```css
input, select, textarea { font-size: 16px; }
```

### 3. Booking Widget (web/js/app.js)
6-step wizard: Date → Time → Guests → Info → Confirm → Success
- State: `bookingData` object
- Navigation: `goToStep(n)`, `nextStep()`, `prevStep()`

### 4. Chat Widget with Customer Insights
- Preferences in `customerInsights` object
- localStorage keys: `yakiniku_customer`, `yakiniku_chat_history`
- **No LINE** - centralized insights system

### 5. Multi-Branch Support (backend)
- Branch detection via subdomain or `X-Branch` header
- Schema: `branches`, `global_customers`, `branch_customers`
- Per-branch preferences and VIP tracking

## Language
- **UI**: Japanese (日本語)
- **Code/Docs**: English/Vietnamese mix

## Testing
Playwright MCP with mobile viewport `375x812`:
```
1. Navigate to http://localhost:8080
2. Test booking flow
3. Test chat widget
```

## Common Tasks

### Add menu item
Edit `web/index.html`, add `.menu-card` following existing pattern.

### Add chat keyword
In `web/js/app.js`, add to `responses` in `processMessage()`.

### Add new branch
Insert into `branches` table with unique `code` and `subdomain`.

## Documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Multi-tenant design
- [BACKEND.md](docs/BACKEND.md) - API & database schema

## Language Usage
- Tiếng Việt cho tài liệu kỹ thuật nội bộ.
- English cho code và chú thích.
- 日本語 cho giao diện người dùng và trải nghiệm khách hàng (đa ngôn ngữ English).