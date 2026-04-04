"""
Ultron Empire — Sector Rotation Detection (Feature 2.8)
Detects money flow between sectors using index + MF flow data.
"""

import logging
from backend.data.sector_data import get_sector_performance, identify_sector_rotation

logger = logging.getLogger(__name__)


def detect_rotation() -> dict:
    """Detect current sector rotation patterns."""
    rotation = identify_sector_rotation(short_period="1mo", long_period="3mo")

    improving = [s for s, d in rotation.items() if d["signal"] == "Improving"]
    weakening = [s for s, d in rotation.items() if d["signal"] == "Weakening"]

    implication = ""
    if improving and weakening:
        implication = (
            f"Money rotating FROM {', '.join(weakening)} TO {', '.join(improving)}. "
            f"Consider rebalancing clients heavy on {weakening[0]}-focused PMSes."
        )

    return {
        "rotation_data": rotation,
        "money_flowing_into": improving,
        "money_flowing_out_of": weakening,
        "implication": implication,
        "recommendation": f"Review PMSes with high {weakening[0]} allocation" if weakening else "No significant rotation detected",
    }
