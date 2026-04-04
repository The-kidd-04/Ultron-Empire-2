.PHONY: dev up down logs migrate seed test lint

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run backend locally (no Docker)
dev:
	uvicorn backend.main:app --reload --port 8000

# Run Telegram bot locally
bot:
	python -m telegram_bot.bot

# Run Celery worker locally
worker:
	celery -A workers.celery_app worker --loglevel=info

# Run Celery beat locally
beat:
	celery -A workers.celery_app beat --loglevel=info

# Database migrations
migrate:
	alembic upgrade head

# Create new migration
migration:
	alembic revision --autogenerate -m "$(msg)"

# Seed database
seed:
	python -m scripts.seed_pms_data
	python -m scripts.seed_mf_data
	python -m scripts.seed_aif_data

# Run tests
test:
	pytest tests/ -v --cov=backend

# Lint
lint:
	ruff check backend/ telegram_bot/ workers/
	ruff format backend/ telegram_bot/ workers/

# Install dependencies
install:
	pip install -e ".[dev]"
