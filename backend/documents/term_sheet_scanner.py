"""
Ultron Empire — AIF Term Sheet / PPM Scanner
Analyzes AIF Private Placement Memorandums for key terms.
"""

import logging

logger = logging.getLogger(__name__)

KEY_TERMS_TO_EXTRACT = [
    "management fee",
    "performance fee",
    "hurdle rate",
    "minimum investment",
    "lock-in period",
    "drawdown schedule",
    "distribution waterfall",
    "investment strategy",
    "target return",
    "fund tenure",
    "exit provisions",
    "key person clause",
]


def scan_term_sheet(pdf_path: str) -> dict:
    """Scan an AIF PPM/term sheet for key terms and red flags.

    Args:
        pdf_path: Path to the term sheet PDF

    Returns:
        Extracted terms, red flags, and summary.
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"

        text_lower = full_text.lower()
        found_terms = {}
        for term in KEY_TERMS_TO_EXTRACT:
            if term in text_lower:
                # Find the paragraph containing the term
                idx = text_lower.index(term)
                context = full_text[max(0, idx - 50):idx + 200]
                found_terms[term] = context.strip()

        # Red flags
        red_flags = []
        if "no hurdle" in text_lower or "hurdle rate: 0" in text_lower:
            red_flags.append("No hurdle rate — fund earns performance fee from first rupee of profit")
        if "lock-in" in text_lower:
            # Check for long lock-ins
            if "5 year" in text_lower or "7 year" in text_lower:
                red_flags.append("Long lock-in period detected (5-7 years)")
        if "no exit" in text_lower or "no redemption" in text_lower:
            red_flags.append("Limited/no exit provisions")

        return {
            "terms_found": len(found_terms),
            "extracted_terms": found_terms,
            "red_flags": red_flags,
            "total_pages": len(full_text.split("\f")) + 1,
            "note": "Manual review recommended for legal accuracy",
        }

    except Exception as e:
        logger.error(f"Term sheet scan failed: {e}")
        return {"error": str(e)}
