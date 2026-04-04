"""
Ultron Empire — Alert Rules
Defines trigger conditions for different alert types.
"""

ALERT_RULES = {
    "market_crash": {
        "condition": "Nifty down > 2% intraday",
        "threshold": -2.0,
        "priority": "critical",
        "category": "market",
        "check_field": "nifty_change_pct",
    },
    "market_surge": {
        "condition": "Nifty up > 2% intraday",
        "threshold": 2.0,
        "priority": "important",
        "category": "market",
        "check_field": "nifty_change_pct",
    },
    "vix_spike": {
        "condition": "India VIX > 25",
        "threshold": 25.0,
        "priority": "important",
        "category": "market",
        "check_field": "india_vix",
    },
    "fii_heavy_selling": {
        "condition": "FII net selling > ₹3000 Cr",
        "threshold": -3000,
        "priority": "important",
        "category": "market",
        "check_field": "fii_net",
    },
    "fii_heavy_buying": {
        "condition": "FII net buying > ₹3000 Cr",
        "threshold": 3000,
        "priority": "info",
        "category": "market",
        "check_field": "fii_net",
    },
    "sector_crash": {
        "condition": "Any sector index down > 3%",
        "threshold": -3.0,
        "priority": "important",
        "category": "market",
    },
    "nav_milestone": {
        "condition": "Fund NAV hits new all-time high",
        "priority": "info",
        "category": "nav",
    },
    "nav_significant_drop": {
        "condition": "Fund NAV drops > 5% in a week",
        "threshold": -5.0,
        "priority": "important",
        "category": "nav",
    },
    "client_review_due": {
        "condition": "Client review date within 7 days",
        "priority": "client",
        "category": "client",
    },
    "sebi_new_circular": {
        "condition": "New SEBI circular affecting PMS/AIF",
        "priority": "critical",
        "category": "sebi",
    },
}


def evaluate_market_rules(market_data: dict) -> list:
    """Evaluate alert rules against current market data."""
    triggered = []

    nifty_change = market_data.get("nifty_change_pct", 0)
    if nifty_change <= ALERT_RULES["market_crash"]["threshold"]:
        triggered.append({
            **ALERT_RULES["market_crash"],
            "value": nifty_change,
            "title": f"Market Crash Alert: Nifty down {nifty_change:.1f}%",
        })
    elif nifty_change >= ALERT_RULES["market_surge"]["threshold"]:
        triggered.append({
            **ALERT_RULES["market_surge"],
            "value": nifty_change,
            "title": f"Market Surge: Nifty up {nifty_change:.1f}%",
        })

    vix = market_data.get("india_vix", 0)
    if vix >= ALERT_RULES["vix_spike"]["threshold"]:
        triggered.append({
            **ALERT_RULES["vix_spike"],
            "value": vix,
            "title": f"VIX Spike Alert: India VIX at {vix:.1f}",
        })

    fii_net = market_data.get("fii_net", 0)
    if fii_net <= ALERT_RULES["fii_heavy_selling"]["threshold"]:
        triggered.append({
            **ALERT_RULES["fii_heavy_selling"],
            "value": fii_net,
            "title": f"Heavy FII Selling: ₹{abs(fii_net):.0f} Cr net sold",
        })

    return triggered
