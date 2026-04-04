# Ultron Empire

**AI-Powered Wealth Management Operating System**
Built for [PMS Sahi Hai](https://www.pmssahihai.com) — India's 1st AI Powered PMS & AIF Marketplace

## Quick Start

```bash
# 1. Clone and setup
cp .env.example .env
# Fill in your API keys (Anthropic, Telegram, Tavily, etc.)

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Start services (Docker)
docker-compose up -d

# 4. Seed database
python -m backend.db.seed

# 5. Run backend
make dev          # FastAPI on :8000

# 6. Run Telegram bot
make bot          # Telegram polling

# 7. Run frontend
cd frontend && npm install && npm run dev  # Next.js on :3000
```

## Architecture

```
Telegram Bot / WhatsApp / Web Dashboard
         ↓
    FastAPI (9 API routes)
         ↓
    Agent Layer (LangChain + LangGraph + CrewAI)
    ├── Analyst Agent (core brain)
    ├── Alert Agent
    ├── Content Agent
    └── 4-Agent Crew (Research + Risk + Client + Compliance)
         ↓
    Tool Registry (9 tools)
    ├── fund_lookup, nav_fetcher, market_data
    ├── news_search, sebi_checker, client_lookup
    └── portfolio_analyzer, calculator, backtester
         ↓
    Data Layer
    ├── PostgreSQL (Supabase) — clients, funds, market data
    ├── Pinecone / ChromaDB — vector search
    ├── Redis — cache, task queues
    └── Mem0 — cross-session AI memory
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Chat with Ultron analyst |
| `/api/v1/alerts` | GET/POST | Alert management |
| `/api/v1/clients` | CRUD | Client CRM |
| `/api/v1/market` | GET | Market data |
| `/api/v1/content` | POST | Generate content |
| `/api/v1/reports` | POST | Generate reports |
| `/api/v1/documents` | POST | Process PDFs |
| `/api/v1/predictions` | GET/POST | Market signals, Monte Carlo |
| `/api/v1/webhooks` | POST | Telegram/WhatsApp webhooks |

## Telegram Commands

`/start` `/ask` `/brief` `/client` `/compare` `/market` `/news` `/alert` `/predict` `/help`

## Tech Stack

- **LLM:** Claude API (Anthropic) + GPT-4o backup
- **Agents:** LangChain 0.3+ / LangGraph / CrewAI
- **Backend:** Python 3.11+ / FastAPI
- **Database:** PostgreSQL / Pinecone / Redis / Mem0
- **Frontend:** Next.js 14 / Tailwind CSS
- **Workers:** Celery + Redis (11 scheduled tasks)
- **Delivery:** Telegram, WhatsApp (Gupshup), Web Dashboard

## Budget

Target: ₹8,000 - ₹20,000/month running cost

---

Built with care for PMS Sahi Hai | Ultron Capital Private Limited
