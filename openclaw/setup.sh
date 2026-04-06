#!/usr/bin/env bash
# =============================================================================
# OpenClaw Setup for Ultron Empire
# Run this once to install and configure OpenClaw
# =============================================================================

set -euo pipefail

echo "=== Ultron Empire — OpenClaw Setup ==="
echo ""

# 1. Check Node.js
if ! command -v node &>/dev/null; then
    echo "ERROR: Node.js is required. Install Node 22.16+ or 24+"
    echo "  https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "WARNING: Node $NODE_VERSION detected. OpenClaw needs Node 22.16+ or 24+"
fi

# 2. Install OpenClaw globally
echo "[1/4] Installing OpenClaw..."
npm install -g openclaw@latest

# 3. Build the Ultron tools plugin
echo "[2/4] Building Ultron tools plugin..."
cd "$(dirname "$0")/plugins/ultron-tools"
npm install
npm run build
cd ../..

# 4. Copy config to OpenClaw home
OPENCLAW_HOME="${HOME}/.openclaw"
mkdir -p "$OPENCLAW_HOME"

echo "[3/4] Setting up configuration..."

# Copy config (don't overwrite if exists)
if [ ! -f "$OPENCLAW_HOME/openclaw.json" ]; then
    cp openclaw.json "$OPENCLAW_HOME/openclaw.json"
    echo "  Copied openclaw.json -> $OPENCLAW_HOME/openclaw.json"
else
    echo "  openclaw.json already exists — skipping (check for updates manually)"
fi

# Copy .env template
if [ ! -f "$OPENCLAW_HOME/.env" ]; then
    cp .env.example "$OPENCLAW_HOME/.env"
    echo "  Copied .env.example -> $OPENCLAW_HOME/.env"
    echo ""
    echo "  >>> IMPORTANT: Edit $OPENCLAW_HOME/.env with your API keys <<<"
    echo ""
else
    echo "  .env already exists — skipping"
fi

# Copy skills
mkdir -p "$OPENCLAW_HOME/workspace/skills"
cp -r skills/ultron "$OPENCLAW_HOME/workspace/skills/"
echo "  Copied skills -> $OPENCLAW_HOME/workspace/skills/ultron"

# 5. Install daemon
echo "[4/4] Installing OpenClaw daemon..."
openclaw onboard --install-daemon 2>/dev/null || true

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit ~/.openclaw/.env with your API keys"
echo "  2. Make sure Ultron backend is running (make dev)"
echo "  3. Start OpenClaw:  openclaw start"
echo "  4. Link WhatsApp:   openclaw channels login"
echo "  5. Open control UI: http://localhost:18789"
echo ""
echo "Channels configured: Telegram, WhatsApp, Discord, Slack"
echo "Tools registered: 12 Ultron API endpoints"
echo ""
