#!/bin/bash
# ============================================================================
# Ultron Empire — One-Click Deployment Script
# Run on your server (AWS EC2 / Railway / Oracle Cloud)
# ============================================================================

set -e

echo "🟢 Deploying Ultron Empire..."

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required. Install: docs.docker.com"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose required."; exit 1; }

# 2. Ensure .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and fill in your API keys."
    echo "   cp .env.example .env && nano .env"
    exit 1
fi

# 3. Build and start all services
echo "📦 Building containers..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 4. Wait for API to be ready
echo "⏳ Waiting for API to start..."
sleep 10
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy!"
        break
    fi
    sleep 2
done

# 5. Seed database
echo "🌱 Seeding database..."
docker-compose -f docker-compose.prod.yml exec -T api python -m backend.db.seed 2>/dev/null || echo "Seed skipped (may already exist)"

# 6. Set up Telegram webhook (if domain is configured)
DOMAIN=$(grep API_DOMAIN .env 2>/dev/null | cut -d= -f2)
TOKEN=$(grep TELEGRAM_BOT_TOKEN .env 2>/dev/null | cut -d= -f2)
if [ -n "$DOMAIN" ] && [ -n "$TOKEN" ]; then
    echo "🔗 Setting Telegram webhook..."
    curl -s "https://api.telegram.org/bot${TOKEN}/setWebhook?url=https://${DOMAIN}/telegram/webhook"
    echo ""
fi

# 7. Show status
echo ""
echo "============================================"
echo "✅ Ultron Empire is LIVE!"
echo "============================================"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "API:       http://localhost:8000"
echo "Health:    http://localhost:8000/health"
echo "Docs:      http://localhost:8000/docs"
echo ""
echo "Ultron will run 24/7. Auto-restarts on crash."
echo "To stop:   docker-compose -f docker-compose.prod.yml down"
echo "To logs:   docker-compose -f docker-compose.prod.yml logs -f"
