# Yakiniku Jinan - Restaurant Booking System
[![Deploy static content to Pages](https://github.com/maithanhduyan/yakiniku/actions/workflows/static.yml/badge.svg)](https://github.com/maithanhduyan/yakiniku/actions/workflows/static.yml)
> Multi-tenant restaurant booking platform with AI-powered customer insights.

## Architecture

```
yakiniku/
├── web/           # Customer website (HTML/CSS/JS)
├── backend/       # FastAPI server (Python)
├── dashboard/     # Admin panel (HTMX + Jinja2)
├── shared/        # Shared configs & branding
└── docs/          # Documentation
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## Quick Start

### Development (Local)

```bash
# 1. Start web server
cd web
python -m http.server 8080

# 2. Start backend (in another terminal)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Production (Docker)

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Web | http://localhost:8080 | Customer website |
| API | http://localhost:8000 | Backend API |
| Dashboard | http://localhost:8000/admin | Admin panel |
| API Docs | http://localhost:8000/docs | Swagger UI |

## Features

### Customer Website (`web/`)
- 📅 Step-by-step booking widget
- 💬 AI chat with customer insights
- 📱 Mobile-first design

### Backend API (`backend/`)
- 🔐 Multi-tenant architecture
- 🤖 LLM integration (OpenAI)
- 📊 Customer preference extraction

### Dashboard (`dashboard/`)
- 📅 Booking calendar
- 👤 Customer insights management
- 📈 Analytics & reports
- 🏢 Multi-branch management

## Multi-Branch Support

System is designed for chain restaurants:

```
jinan.yakiniku.com      → 平間本店
shibuya.yakiniku.com    → 渋谷店
admin.yakiniku.com      → Dashboard (all branches)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for multi-tenant strategy.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design & multi-tenant
- [BACKEND.md](docs/BACKEND.md) - API & database schema
- [UX.md](docs/UX.md) - UX optimization strategies

## License

Private - Yakiniku Jinan
