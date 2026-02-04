# System Architecture - Yakiniku Chain

> Kiến trúc mở rộng cho chuỗi nhà hàng (Multi-Tenant)

---

## 1. Tổng quan

```
                              ┌─────────────────────┐
                              │   Load Balancer     │
                              │   (Nginx/Traefik)   │
                              └──────────┬──────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│   web/          │           │   backend/      │           │   dashboard/    │
│   (Static)      │           │   (FastAPI)     │           │   (Admin)       │
│                 │           │                 │           │                 │
│ jinan.com       │           │ api.jinan.com   │           │ admin.jinan.com │
│ shibuya.jinan.  │           │                 │           │                 │
│ shinjuku.jinan. │           │                 │           │                 │
└────────┬────────┘           └────────┬────────┘           └────────┬────────┘
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │   PostgreSQL        │
                            │   (Multi-tenant)    │
                            └──────────┬──────────┘
                                       │
                            ┌──────────┴──────────┐
                            ▼                     ▼
                     ┌───────────┐         ┌───────────┐
                     │  Redis    │         │  S3/Minio │
                     │  (Cache)  │         │  (Assets) │
                     └───────────┘         └───────────┘
```

---

## 2. Multi-Tenant Strategy

### Option A: Schema-per-Tenant (Recommended for <50 branches)

```sql
-- Shared database, separate schemas
CREATE SCHEMA branch_jinan;      -- Hiraama original
CREATE SCHEMA branch_shibuya;    -- Shibuya branch
CREATE SCHEMA branch_shinjuku;   -- Shinjuku branch

-- Each schema has identical tables
branch_jinan.customers
branch_jinan.bookings
branch_jinan.preferences
```

**Pros:**
- Easy to query across branches (analytics)
- Single database backup
- Schema migrations apply to all

**Cons:**
- Limited to ~50-100 branches
- Shared DB resources

### Option B: Database-per-Tenant (For large chains)

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  db_jinan       │  │  db_shibuya     │  │  db_shinjuku    │
│  PostgreSQL     │  │  PostgreSQL     │  │  PostgreSQL     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  db_central     │
                    │  (Analytics,    │
                    │   Users, Config)│
                    └─────────────────┘
```

**Pros:**
- Full isolation
- Independent scaling
- Compliant with data residency

**Cons:**
- Complex deployment
- Cross-branch queries harder

---

## 3. Branch Configuration

### Database Model

```sql
-- Central config table (shared DB)
CREATE TABLE branches (
    id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE,      -- 'jinan', 'shibuya'
    name VARCHAR(255),            -- '焼肉ジナン 平間本店'
    subdomain VARCHAR(100),       -- 'jinan', 'shibuya'

    -- Contact
    phone VARCHAR(20),
    address TEXT,

    -- Branding
    theme_primary_color VARCHAR(7),   -- '#d4af37'
    logo_url TEXT,

    -- Operations
    opening_time TIME,
    closing_time TIME,
    closed_days INTEGER[],        -- [2] = Tuesday
    max_capacity INTEGER,

    -- Features
    features JSONB,               -- {"chat": true, "ai_booking": true}

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
);
```

### Per-Branch Customization

```python
# backend/app/config.py
class BranchConfig:
    """Dynamic config loaded from DB"""

    def __init__(self, branch_code: str):
        branch = get_branch_by_code(branch_code)

        self.name = branch.name
        self.phone = branch.phone
        self.theme = {
            "primary": branch.theme_primary_color,
            "logo": branch.logo_url
        }
        self.hours = {
            "open": branch.opening_time,
            "close": branch.closing_time,
            "closed_days": branch.closed_days
        }
        self.features = branch.features
```

---

## 4. URL Routing Strategy

### Option A: Subdomain-based (Recommended)

```
jinan.yakiniku.com      → Branch: jinan (本店)
shibuya.yakiniku.com    → Branch: shibuya
admin.yakiniku.com      → Dashboard (all branches)
api.yakiniku.com        → Backend API
```

### Option B: Path-based

```
yakiniku.com/jinan      → Branch: jinan
yakiniku.com/shibuya    → Branch: shibuya
yakiniku.com/admin      → Dashboard
yakiniku.com/api        → Backend API
```

### Nginx Config (Subdomain)

```nginx
# Web - per branch
server {
    server_name ~^(?<branch>.+)\.yakiniku\.com$;

    location / {
        root /var/www/web;
        # Pass branch to JS via header
        add_header X-Branch $branch;
    }
}

# API - single backend
server {
    server_name api.yakiniku.com;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header X-Branch $http_x_branch;
    }
}

# Dashboard - single admin
server {
    server_name admin.yakiniku.com;

    location / {
        proxy_pass http://dashboard:3000;
    }
}
```

---

## 5. API Design for Multi-Branch

### Branch Context

```python
# backend/app/middleware/tenant.py
from fastapi import Request, HTTPException

async def get_current_branch(request: Request) -> str:
    """Extract branch from subdomain or header"""

    # From subdomain
    host = request.headers.get("host", "")
    if ".yakiniku.com" in host:
        branch = host.split(".")[0]
        return branch

    # From header (for API clients)
    branch = request.headers.get("X-Branch")
    if branch:
        return branch

    raise HTTPException(400, "Branch not specified")
```

### Branch-Scoped Endpoints

```python
# backend/app/routers/bookings.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/bookings")

@router.get("/")
async def list_bookings(
    branch: str = Depends(get_current_branch),
    db: Session = Depends(get_db)
):
    """List bookings for current branch only"""
    return db.query(Booking).filter(
        Booking.branch_code == branch
    ).all()

@router.post("/")
async def create_booking(
    data: BookingCreate,
    branch: str = Depends(get_current_branch),
    db: Session = Depends(get_db)
):
    booking = Booking(**data.dict(), branch_code=branch)
    db.add(booking)
    db.commit()
    return booking
```

---

## 6. Dashboard: Multi-Branch Access Control

### Role-Based Access

```python
class UserRole(Enum):
    SUPER_ADMIN = "super_admin"   # All branches
    BRANCH_MANAGER = "manager"    # Single branch
    STAFF = "staff"               # Single branch, limited

class User:
    id: int
    email: str
    role: UserRole
    branch_codes: list[str]       # Empty = all branches (super admin)
```

### Dashboard Views

```
┌─────────────────────────────────────────────────────────────┐
│  🏢 焼肉ジナン Dashboard              [平間本店 ▼] [Logout]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ 予約    │  │ 顧客    │  │ 分析    │  │ 設定    │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  For Super Admin:                                          │
│  ┌─────────┐  ┌─────────┐                                  │
│  │ 全店舗  │  │ 店舗管理│                                  │
│  └─────────┘  └─────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Customer Insights: Cross-Branch

### Shared Customer Identity

```sql
-- Global customer (by phone)
CREATE TABLE global_customers (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP
);

-- Per-branch relationship
CREATE TABLE branch_customers (
    id UUID PRIMARY KEY,
    global_customer_id UUID REFERENCES global_customers(id),
    branch_code VARCHAR(50),
    visit_count INTEGER DEFAULT 0,
    last_visit TIMESTAMP,
    is_vip BOOLEAN DEFAULT false,

    UNIQUE(global_customer_id, branch_code)
);

-- Preferences (per branch, may differ)
CREATE TABLE customer_preferences (
    id UUID PRIMARY KEY,
    branch_customer_id UUID REFERENCES branch_customers(id),
    preference TEXT,
    category VARCHAR(50),
    confidence REAL
);
```

### Cross-Branch Analytics

```python
# "渡辺様 visited 3 branches, prefers レバ刺し everywhere"
def get_customer_chain_profile(phone: str):
    global_customer = get_global_customer(phone)

    branches_visited = db.query(BranchCustomer).filter(
        BranchCustomer.global_customer_id == global_customer.id
    ).all()

    all_preferences = []
    for bc in branches_visited:
        prefs = db.query(Preference).filter(
            Preference.branch_customer_id == bc.id
        ).all()
        all_preferences.extend(prefs)

    # Aggregate preferences across chain
    return {
        "customer": global_customer,
        "branches_visited": len(branches_visited),
        "total_visits": sum(bc.visit_count for bc in branches_visited),
        "preferences": aggregate_preferences(all_preferences)
    }
```

---

## 8. Deployment Strategy

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    volumes:
      - ./web:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db/yakiniku
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  dashboard:
    build: ./dashboard
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=yakiniku

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

### Production (Kubernetes)

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
├─────────────────────────────────────────────────────────┤
│  Ingress Controller (Traefik)                           │
│  ├── *.yakiniku.com → web-deployment                   │
│  ├── api.yakiniku.com → backend-deployment             │
│  └── admin.yakiniku.com → dashboard-deployment         │
├─────────────────────────────────────────────────────────┤
│  Deployments:                                           │
│  ├── web (3 replicas, static files)                    │
│  ├── backend (5 replicas, auto-scale)                  │
│  └── dashboard (2 replicas)                            │
├─────────────────────────────────────────────────────────┤
│  StatefulSets:                                          │
│  ├── postgresql (primary + replica)                    │
│  └── redis (cluster mode)                              │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Migration Path

### Phase 1: Current (Single Branch)
```
yakiniku/
├── web/        ← Move current files here
├── backend/    ← Build MVP
├── dashboard/  ← Build MVP
└── docs/
```

### Phase 2: Multi-Branch Ready
- Add `branches` table
- Add `branch_code` to all models
- Subdomain routing

### Phase 3: Second Branch Launch
- Clone web/ with different branding
- Add branch config to DB
- Same backend serves both

### Phase 4: Chain Scale
- Migrate to schema-per-tenant or DB-per-tenant
- Add cross-branch analytics
- Central management dashboard

---

## 10. File Structure After Restructure

```
yakiniku/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── middleware/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── dashboard/
│   ├── templates/
│   ├── static/
│   └── README.md
│
├── web/
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── assets/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BACKEND.md
│   └── API.md
│
├── docker-compose.yml
├── .env.example
├── .github/
│   └── copilot-instructions.md
└── README.md
```
