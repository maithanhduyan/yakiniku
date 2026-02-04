# Backend - Yakiniku API

FastAPI server cho hệ thống đặt bàn và customer insights.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run Development

```bash
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
DATABASE_URL=sqlite:///./yakiniku.db
OPENAI_API_KEY=sk-xxx
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
