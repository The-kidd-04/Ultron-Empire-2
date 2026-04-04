"""Ultron Empire — Client CRM Tests"""

def test_lifecycle_classification():
    from backend.clients.lifecycle import LIFECYCLE_STAGES
    assert "prospect" in LIFECYCLE_STAGES
    assert "active" in LIFECYCLE_STAGES
    assert "dormant" in LIFECYCLE_STAGES

def test_lead_scoring_tiers():
    from backend.clients.scoring import calculate_lead_score
    # High-value lead
    hot = calculate_lead_score(50, 45, "CEO", "Mumbai", "Aggressive", True)
    assert hot["score"] >= 80
    # Low-value lead
    cold = calculate_lead_score(0.3, 25, "Student", "Jaipur", "Conservative", False)
    assert cold["score"] < 40

def test_validators():
    from backend.utils.validators import validate_phone, validate_email, validate_pan
    assert validate_phone("+919876543210")
    assert validate_phone("9876543210")
    assert not validate_phone("12345")
    assert validate_email("test@example.com")
    assert not validate_email("invalid")
    assert validate_pan("ABCDE1234F")
