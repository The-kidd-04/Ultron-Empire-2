"""
Ultron Empire — Lead Scoring
Scores potential and existing clients for prioritization.
"""

import logging

logger = logging.getLogger(__name__)


def calculate_lead_score(
    total_wealth_cr: float,
    age: int,
    occupation: str,
    city: str,
    risk_profile: str,
    referral: bool = False,
) -> dict:
    """Score a lead from 0-100 for prioritization.

    Factors:
    - Wealth (40%): Higher wealth = higher score
    - Profile fit (25%): Age, occupation match
    - Location (15%): Metro cities preferred
    - Risk appetite (10%): Aggressive = more PMS suitable
    - Referral (10%): Referred leads convert 3x better
    """
    score = 0

    # Wealth (40 points)
    if total_wealth_cr >= 50:
        score += 40  # Family office level
    elif total_wealth_cr >= 10:
        score += 35
    elif total_wealth_cr >= 5:
        score += 28
    elif total_wealth_cr >= 1:
        score += 20
    elif total_wealth_cr >= 0.5:
        score += 15  # PMS minimum
    else:
        score += 5

    # Profile fit (25 points)
    high_value_occupations = ["industrialist", "ceo", "founder", "doctor", "lawyer", "ca", "nri"]
    if any(occ in occupation.lower() for occ in high_value_occupations):
        score += 25
    elif age >= 35 and age <= 60:
        score += 18
    else:
        score += 10

    # Location (15 points)
    metro_cities = ["mumbai", "delhi", "bengaluru", "hyderabad", "pune", "chennai", "kolkata"]
    if any(city.lower().startswith(c) for c in metro_cities):
        score += 15
    else:
        score += 8

    # Risk appetite (10 points)
    risk_scores = {"aggressive": 10, "moderate": 7, "conservative": 4}
    score += risk_scores.get(risk_profile.lower(), 5)

    # Referral bonus (10 points)
    if referral:
        score += 10

    # Classification
    if score >= 80:
        tier = "A+ (Hot Lead)"
    elif score >= 60:
        tier = "A (High Priority)"
    elif score >= 40:
        tier = "B (Medium Priority)"
    else:
        tier = "C (Low Priority)"

    return {
        "score": min(score, 100),
        "tier": tier,
        "recommended_action": _get_recommended_action(score),
    }


def _get_recommended_action(score: int) -> str:
    if score >= 80:
        return "Immediate personal call + meeting within 48 hours"
    elif score >= 60:
        return "Call within 1 week + send personalized PMS overview"
    elif score >= 40:
        return "Email introduction + add to newsletter list"
    else:
        return "Add to nurture campaign"
