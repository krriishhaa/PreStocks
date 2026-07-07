# PreStocks Backend

FastAPI + PostgreSQL backend for user accounts, portfolio management, trade execution, and learning progress.

## Quick Start (Docker)

```bash
cd backend
docker compose up --build
```

This starts:
- **PostgreSQL 16** on port `5432`
- **FastAPI** on port `8000` (with auto-reload + auto-migration)

The API will be available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Quick Start (Local, no Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres (e.g. via Homebrew or Postgres.app)
# Make sure DATABASE_URL in .env matches your local Postgres

alembic upgrade head
python seed.py
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Create account → returns JWT |
| POST | `/auth/login` | Login → returns JWT + user |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |
| POST | `/auth/logout` | Invalidate sessions |

### Portfolio
| Method | Path | Description |
|--------|------|-------------|
| GET | `/portfolio` | Full portfolio + holdings |
| GET | `/portfolio/summary` | Quick portfolio snapshot |
| POST | `/portfolio/trades` | Execute a buy/sell trade |
| GET | `/portfolio/trades` | Trade history |
| GET | `/portfolio/risk-summary` | Concentration/diversification |

### Learning
| Method | Path | Description |
|--------|------|-------------|
| GET | `/learning/modules` | List all modules with progress |
| GET | `/learning/modules/{id}` | Module detail + quiz |
| POST | `/learning/modules/{id}/start` | Mark module started |
| POST | `/learning/modules/{id}/progress` | Update progress % |
| POST | `/learning/modules/{id}/complete` | Mark complete |
| POST | `/learning/modules/{id}/quiz` | Submit quiz answers |
| GET | `/learning/progress` | Overall learning progress |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/prestocks_dev` | Postgres connection |
| `JWT_SECRET_KEY` | `dev-secret-...` | JWT signing key |
| `DEBUG` | `true` | Enables /docs |

## Database Migrations

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```
