# Dashboard - Yakiniku Admin

Restaurant management dashboard với HTMX + Jinja2.

## Features

- 📅 Booking calendar view
- 👤 Customer insights management
- 📊 Analytics dashboard
- 🏢 Multi-branch support (Super Admin)

## Tech Stack

- FastAPI (shared with backend)
- Jinja2 templates
- HTMX for interactivity
- TailwindCSS for styling

## Run

Dashboard chạy cùng backend:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Access: http://localhost:8000/admin/
