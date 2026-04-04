"""
Ultron Empire — Application Configuration
Loads all settings from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # AI
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    OPENAI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ultron"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Vector Store
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX: str = "ultron-knowledge"

    # Memory
    MEM0_API_KEY: str = ""

    # Search
    TAVILY_API_KEY: str = ""

    # Web Scraping
    FIRECRAWL_API_KEY: str = ""

    # News
    NEWS_API_KEY: str = ""

    # Market Data
    ALPHA_VANTAGE_API_KEY: str = ""

    # Messaging
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    GUPSHUP_API_KEY: str = ""
    GUPSHUP_APP_NAME: str = "ultron-alerts"
    WHATSAPP_NUMBER: str = "917455899555"

    # Voice
    ELEVEN_LABS_API_KEY: str = ""
    ELEVEN_LABS_VOICE_ID: str = ""

    # Monitoring
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "ultron-empire"
    SENTRY_DSN: str = ""

    # App
    APP_NAME: str = "Ultron Empire"
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    SECRET_KEY: str = "change-me-in-production"

    # API Security
    API_KEYS: str = ""                  # comma-separated valid API keys
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440      # 24 hours
    RATE_LIMIT_PER_MINUTE: int = 60

    # Brand
    BRAND_NAME: str = "PMS Sahi Hai"
    BRAND_WEBSITE: str = "https://www.pmssahihai.com"
    ULTRON_APP_URL: str = "https://ultron.pmssahihai.com"
    BRAND_EMAIL: str = "info@pmssahihai.com"
    BRAND_PHONE: str = "+917455899555"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
