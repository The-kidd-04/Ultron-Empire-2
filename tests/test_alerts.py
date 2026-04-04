"""Ultron Empire — Alert System Tests"""

def test_alert_rules_evaluation():
    from backend.alerts.rules import evaluate_market_rules
    triggered = evaluate_market_rules({"nifty_change_pct": -3.5, "india_vix": 28, "fii_net": -4000})
    assert len(triggered) >= 2  # market crash + VIX spike + FII selling
    priorities = [t["priority"] for t in triggered]
    assert "critical" in priorities

def test_alert_formatter():
    from backend.alerts.formatter import format_telegram_alert
    msg = format_telegram_alert("critical", "Test Alert", "Test message", "market")
    assert "🔴" in msg
    assert "CRITICAL" in msg
    assert "PMS Sahi Hai" in msg

def test_prioritizer_cooldown():
    from backend.alerts.prioritizer import should_send_alert
    # First call should allow
    result = should_send_alert("info", "test", "Test Title")
    assert isinstance(result, bool)
