"""
Ultron Empire — Input Validators
Validation for user inputs, fund queries, and client data.
"""

import re


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number."""
    return bool(re.match(r"^(\+91)?[6-9]\d{9}$", phone.replace(" ", "")))


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


def validate_pan(pan: str) -> bool:
    """Validate Indian PAN number."""
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan.upper()))


def validate_risk_profile(profile: str) -> bool:
    """Validate risk profile value."""
    return profile.lower() in {"conservative", "moderate", "aggressive"}


def sanitize_fund_query(query: str) -> str:
    """Clean and sanitize fund search query."""
    query = query.strip()
    query = re.sub(r"[^\w\s\-&.]", "", query)
    return query[:200]


def validate_amount_cr(amount: float) -> bool:
    """Validate investment amount in crores (PMS min ₹50L = 0.5 Cr)."""
    return 0 < amount <= 10000
