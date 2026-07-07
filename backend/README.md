# PreStocks Backend

A FastAPI-based backend for the PreStocks paper trading and financial education platform.

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (async)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+ with TimescaleDB extension
- **Cache**: Redis
- **Background Jobs**: Celery + Redis
- **Auth**: JWT (access + refresh tokens)
- **AI/ML**: LangGraph + Claude API + FinBERT + ChromaDB

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)

### With Docker (recommended)

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# API is available at http://localhost:8000
# Docs at http://localhost:8000/docs (when DEBUG=true)
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start PostgreSQL and Redis (via Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/auth/signup` | Create new account |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/risk-profile` | Submit risk assessment |
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update profile |
| GET | `/stocks/search?q=` | Search stocks |
| GET | `/stocks/{ticker}` | Get stock detail |
| GET | `/stocks/{ticker}/prices` | Get price history |
| GET | `/portfolio` | Get full portfolio |
| GET | `/portfolio/summary` | Get portfolio summary |
| POST | `/portfolio/trades` | Place a trade |
| GET | `/portfolio/trades` | Get trade history |
| GET | `/flags/stock/{ticker}` | Get risk flags |
| GET | `/flags/stock/{ticker}/score` | Get composite score |
| GET | `/flags/portfolio/risk-summary` | Portfolio risk summary |
| GET | `/learning/modules` | List learning modules |
| GET | `/learning/modules/{id}` | Get module detail |
| POST | `/learning/modules/{id}/quiz` | Submit quiz answers |
| POST | `/learning/modules/{id}/complete` | Mark module complete |
| GET | `/social/feed` | Get social feed |
| POST | `/social/posts` | Create a post |
| POST | `/social/posts/{id}/like` | Toggle like |
| GET | `/social/posts/{id}/comments` | Get comments |
| POST | `/social/posts/{id}/comments` | Add comment |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── core/                # Config, security, constants
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── database/            # Engine, session setup
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── agents/              # LangGraph AI workflows
│   ├── ml_pipelines/        # Sentiment, embeddings, backtesting
│   ├── tasks/               # Celery background jobs
│   └── utils/               # API clients, Redis, logging
├── tests/                   # pytest test suite
├── alembic/                 # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Running Tests

```bash
pytest tests/ -v
```

## Background Tasks

Celery workers handle:
- **Price updates** — every 1 min during market hours
- **Flag calculations** — every 5 min during market hours
- **News ingestion** — hourly
- **Insider filing ingestion** — daily
