"""Ultron Empire — Data Pipeline Tests"""

def test_sector_correlation():
    from backend.prediction.correlation import get_sector_correlation
    assert get_sector_correlation("Banking", "Banking") == 1.0
    assert get_sector_correlation("Banking", "IT") < 1.0
    assert get_sector_correlation("IT", "Banking") == get_sector_correlation("Banking", "IT")

def test_date_utils():
    from backend.utils.date_utils import now_ist, today_ist, format_date_ist, last_trading_day
    assert now_ist() is not None
    assert today_ist() is not None
    assert "2026" in format_date_ist(today_ist())
    assert last_trading_day() is not None

def test_brand_constants():
    from backend.utils.brand import BRAND_NAME, WEBSITE, DEEP_TEAL, EMERALD_GREEN
    assert BRAND_NAME == "PMS Sahi Hai"
    assert "pmssahihai.com" in WEBSITE
    assert DEEP_TEAL.startswith("#")
    assert EMERALD_GREEN.startswith("#")
