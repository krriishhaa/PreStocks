# PreStocks — Paper Trading & Education Platform

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Setup

#### Backend
```bash
cd prestocks-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
alembic upgrade head
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd prestocks-frontend
npm install
npm run dev
```

Visit: http://localhost:3000

### Architecture
[See ARCHITECTURE.md]

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| State | Redux Toolkit, TanStack Query |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL 15 + TimescaleDB |
| Cache | Redis 7 |
| Background Jobs | Celery |
| AI/ML | LangGraph, Claude API, FinBERT |
| Auth | JWT (access + refresh tokens) |

### Key Features
- Paper trading with $10k simulated cash
- 8+ risk flag types with AI explanations
- Tiered learning modules (Beginner → Intermediate → Advanced)
- Social feed for sharing trade reasoning
- Real-time price updates via WebSocket

### API Documentation
Once running: http://localhost:8000/docs (Swagger UI)
