"""Test Telegram bot connectivity."""

import asyncio
from backend.alerts.telegram_bot import send_alert_to_telegram


async def main():
    success = await send_alert_to_telegram("🟢 Ultron Empire test message — all systems operational.", "info")
    print(f"Telegram test: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    asyncio.run(main())
