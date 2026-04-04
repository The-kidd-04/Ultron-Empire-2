"""Test Ultron alert pipeline with simulated events."""

import asyncio
from backend.graphs.alert_graph import alert_pipeline


async def main():
    # Test critical market crash
    result = await alert_pipeline.ainvoke({
        "event_type": "market_crash",
        "event_data": {
            "title": "Nifty crashes 3.5% intraday",
            "nifty_change": -3.5,
            "trigger": "Global risk-off due to US banking concerns",
        },
        "severity": "",
        "affected_clients": [],
        "alert_message": "",
        "delivery_channels": [],
        "delivered": False,
    })
    print(f"Alert severity: {result['severity']}")
    print(f"Delivered: {result['delivered']}")
    print(f"Channels: {result['delivery_channels']}")
    print(f"Message: {result['alert_message'][:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
