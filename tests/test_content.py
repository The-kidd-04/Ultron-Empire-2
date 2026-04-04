"""Ultron Empire — Content Generation Tests (unit level)"""

def test_morning_brief_template():
    from backend.content.templates.morning_brief import MORNING_BRIEF
    assert "{date}" in MORNING_BRIEF
    assert "Global Cues" in MORNING_BRIEF
    assert "PMS Sahi Hai" in MORNING_BRIEF

def test_critical_alert_template():
    from backend.content.templates.alert_critical import CRITICAL_ALERT, IMPORTANT_ALERT, INFO_ALERT
    assert "{headline}" in CRITICAL_ALERT
    assert "{headline}" in IMPORTANT_ALERT
    assert "🔴" in CRITICAL_ALERT
    assert "🟡" in IMPORTANT_ALERT
