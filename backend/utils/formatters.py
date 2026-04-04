"""
Ultron Empire — Number & Currency Formatters
Indian-style formatting: ₹, Cr, L, with proper separators.
"""


def format_inr(amount_cr: float) -> str:
    """Format amount in crores to readable INR string.

    Examples:
        format_inr(2.5) → "₹2.5 Cr"
        format_inr(0.45) → "₹45 L"
        format_inr(0.008) → "₹80,000"
    """
    if amount_cr >= 1:
        if amount_cr == int(amount_cr):
            return f"₹{int(amount_cr)} Cr"
        return f"₹{amount_cr:.1f} Cr"
    elif amount_cr >= 0.01:
        lakhs = amount_cr * 100
        if lakhs == int(lakhs):
            return f"₹{int(lakhs)} L"
        return f"₹{lakhs:.1f} L"
    else:
        rupees = amount_cr * 10_000_000
        return f"₹{rupees:,.0f}"


def format_pct(value: float, with_sign: bool = True) -> str:
    """Format percentage with optional sign.

    Examples:
        format_pct(12.5) → "+12.5%"
        format_pct(-3.2) → "-3.2%"
        format_pct(12.5, with_sign=False) → "12.5%"
    """
    if with_sign:
        return f"{value:+.1f}%"
    return f"{value:.1f}%"


def format_number(value: float, decimals: int = 1) -> str:
    """Format large numbers with Indian notation.

    Examples:
        format_number(25000) → "25,000"
        format_number(1500000) → "15,00,000"
    """
    if value >= 10_000_000:  # 1 Cr+
        return f"{value / 10_000_000:.{decimals}f} Cr"
    elif value >= 100_000:  # 1 L+
        return f"{value / 100_000:.{decimals}f} L"
    else:
        return f"{value:,.0f}"


def format_returns_table(fund_data: dict) -> str:
    """Format fund returns as a clean text table."""
    periods = ["1M", "3M", "6M", "1Y", "3Y", "5Y", "SI"]
    keys = [
        "returns_1m", "returns_3m", "returns_6m",
        "returns_1y", "returns_3y", "returns_5y", "returns_si",
    ]
    header = " | ".join(f"{p:>5}" for p in periods)
    values = " | ".join(
        f"{fund_data.get(k, 0):+5.1f}" if fund_data.get(k) is not None else "   --"
        for k in keys
    )
    return f"       {header}\nReturns {values}"
