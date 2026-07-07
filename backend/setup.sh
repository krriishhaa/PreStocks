#!/bin/bash
# PreStocks Backend — Local Development Setup
# Usage: ./setup.sh

set -e

echo "=== PreStocks Backend Setup ==="

# Check Python version
python3 --version 2>/dev/null || { echo "Error: Python 3.11+ required"; exit 1; }

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy env file
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "  ⚠ Edit .env with your API keys before running"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "Starting PostgreSQL and Redis via Docker Compose..."
    docker-compose up -d postgres redis
    echo "  Waiting for services to be ready..."
    sleep 3
else
    echo "  ⚠ Docker not found — start PostgreSQL and Redis manually"
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head || echo "  ⚠ Migration failed — ensure PostgreSQL is running"

# Seed stock data
echo "Seeding stock data..."
python -m app.scripts.seed_stocks || echo "  ⚠ Seeding failed — will retry on first run"

# Seed learning modules
echo "Seeding learning modules..."
python -m app.scripts.seed_modules || echo "  ⚠ Module seeding failed — will retry on first run"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Start the API server:"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Start Celery worker (in separate terminal):"
echo "  celery -A app.celery_app worker --loglevel=info"
echo ""
echo "Start Celery beat (in separate terminal):"
echo "  celery -A app.celery_app beat --loglevel=info"
echo ""
echo "API docs: http://localhost:8000/docs"
