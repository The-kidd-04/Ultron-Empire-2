"""
Ultron Empire — CAS Statement Reader
Parses Consolidated Account Statements to extract holdings.
"""

import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def parse_cas_statement(pdf_path: str) -> dict:
    """Parse a CAS (Consolidated Account Statement) PDF.

    Extracts:
    - All mutual fund holdings
    - Portfolio valuation
    - SIP details
    - Folio numbers

    Args:
        pdf_path: Path to the CAS PDF file

    Returns:
        Parsed CAS data with holdings breakdown.
    """
    try:
        import pdfplumber

        holdings = []
        total_value = 0

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""

            # Parse fund holdings from text
            # CAS format: Fund Name | Folio | Units | NAV | Value
            lines = full_text.split("\n")
            current_fund = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect fund names (typically in ALL CAPS or specific patterns)
                if "MUTUAL FUND" in line.upper() or "- GROWTH" in line.upper() or "- DIRECT" in line.upper():
                    current_fund = line

                # Detect value lines (contain ₹ or numeric patterns)
                if current_fund and any(c.isdigit() for c in line):
                    # Try to extract value
                    parts = line.split()
                    for part in parts:
                        try:
                            value = float(part.replace(",", "").replace("₹", ""))
                            if value > 100:  # Likely a portfolio value
                                holdings.append({
                                    "fund": current_fund,
                                    "value": value,
                                })
                                total_value += value
                                current_fund = None
                                break
                        except ValueError:
                            continue

        return {
            "holdings_count": len(holdings),
            "total_value": round(total_value, 2),
            "holdings": holdings,
            "raw_text_length": len(full_text),
            "note": "CAS parsing is approximate — verify with actual statement",
        }

    except Exception as e:
        logger.error(f"CAS parsing failed: {e}")
        return {"error": str(e)}
