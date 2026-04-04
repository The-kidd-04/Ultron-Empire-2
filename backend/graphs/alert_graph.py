"""
Ultron Empire — Alert Processing Graph (LangGraph)
Pipeline: Event → Classify → Find Clients → Generate Alert → Deliver
"""

import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class AlertState(TypedDict):
    event_type: str
    event_data: dict
    severity: str
    affected_clients: List[dict]
    alert_message: str
    delivery_channels: List[str]
    delivered: bool


async def classify_event(state: AlertState) -> dict:
    """Classify event severity using Claude."""
    from backend.agents.alert_agent import classify_severity

    severity = await classify_severity(
        event_type=state["event_type"],
        event_data=state["event_data"],
    )
    return {"severity": severity}


async def find_affected_clients(state: AlertState) -> dict:
    """Find clients impacted by this event."""
    from backend.db.database import SessionLocal
    from backend.db.models import Client

    clients = []
    if state["severity"] in ("critical", "important"):
        session = SessionLocal()
        try:
            # For market-wide events, all clients are affected
            if state["event_type"] in ("market_crash", "sebi_circular"):
                all_clients = session.query(Client).all()
                clients = [{"id": c.id, "name": c.name} for c in all_clients]
            # For fund-specific events, find clients holding that fund
            elif "fund_name" in state["event_data"]:
                fund_name = state["event_data"]["fund_name"]
                all_clients = session.query(Client).all()
                for c in all_clients:
                    for h in (c.holdings or []):
                        if fund_name.lower() in h.get("product", "").lower():
                            clients.append({"id": c.id, "name": c.name})
                            break
        finally:
            session.close()

    return {"affected_clients": clients}


async def generate_alert(state: AlertState) -> dict:
    """Generate branded alert message."""
    from backend.agents.alert_agent import generate_alert_message

    message = await generate_alert_message(
        severity=state["severity"],
        event_data=state["event_data"],
        affected_clients=state["affected_clients"],
    )
    return {"alert_message": message}


def route_delivery(state: AlertState) -> str:
    """Route to appropriate delivery channel based on severity."""
    if state["severity"] == "critical":
        return "deliver_all"
    elif state["severity"] == "important":
        return "deliver_telegram"
    else:
        return "deliver_dashboard"


async def deliver_telegram(state: AlertState) -> dict:
    """Send alert via Telegram."""
    from backend.alerts.telegram_bot import send_alert_to_telegram

    try:
        await send_alert_to_telegram(state["alert_message"], state["severity"])
        return {"delivered": True, "delivery_channels": ["telegram"]}
    except Exception as e:
        logger.error(f"Telegram delivery failed: {e}")
        return {"delivered": False, "delivery_channels": []}


async def deliver_all(state: AlertState) -> dict:
    """Send via all channels (critical alerts)."""
    from backend.alerts.telegram_bot import send_alert_to_telegram

    channels = []
    try:
        await send_alert_to_telegram(state["alert_message"], state["severity"])
        channels.append("telegram")
    except Exception as e:
        logger.error(f"Telegram delivery failed: {e}")

    # WhatsApp delivery would go here
    # channels.append("whatsapp")

    return {"delivered": len(channels) > 0, "delivery_channels": channels}


async def deliver_dashboard(state: AlertState) -> dict:
    """Store alert for dashboard display only."""
    from backend.db.database import SessionLocal
    from backend.db.models import Alert

    session = SessionLocal()
    try:
        alert = Alert(
            priority=state["severity"],
            category=state["event_type"],
            title=state["event_data"].get("title", "Alert"),
            message=state["alert_message"],
            event_data=state["event_data"],
            delivered_via=["dashboard"],
        )
        session.add(alert)
        session.commit()
        return {"delivered": True, "delivery_channels": ["dashboard"]}
    except Exception as e:
        session.rollback()
        logger.error(f"Dashboard storage failed: {e}")
        return {"delivered": False, "delivery_channels": []}
    finally:
        session.close()


# Build the graph
def build_alert_graph():
    graph = StateGraph(AlertState)

    graph.add_node("classify", classify_event)
    graph.add_node("find_clients", find_affected_clients)
    graph.add_node("generate", generate_alert)
    graph.add_node("deliver_telegram", deliver_telegram)
    graph.add_node("deliver_all", deliver_all)
    graph.add_node("deliver_dashboard", deliver_dashboard)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "find_clients")
    graph.add_edge("find_clients", "generate")
    graph.add_conditional_edges("generate", route_delivery, {
        "deliver_telegram": "deliver_telegram",
        "deliver_all": "deliver_all",
        "deliver_dashboard": "deliver_dashboard",
    })
    graph.add_edge("deliver_telegram", END)
    graph.add_edge("deliver_all", END)
    graph.add_edge("deliver_dashboard", END)

    return graph.compile()


alert_pipeline = build_alert_graph()
