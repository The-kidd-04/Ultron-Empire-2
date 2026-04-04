"""
Ultron Empire — Company Annual Report Analyzer
Extracts key financial metrics from company annual reports.
"""

import logging

logger = logging.getLogger(__name__)


def analyze_annual_report(pdf_path: str) -> dict:
    """Analyze a company annual report PDF.

    Extracts: Revenue, PAT, EPS, ROE, ROCE, debt-to-equity,
    management commentary highlights, segment breakdown.
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages[:30]:  # First 30 pages usually have financials
                full_text += (page.extract_text() or "") + "\n"

        text_lower = full_text.lower()

        extracted = {}
        financial_keywords = [
            "revenue from operations", "profit after tax", "earnings per share",
            "return on equity", "return on capital employed", "debt to equity",
            "operating margin", "net profit margin", "dividend per share",
        ]

        for kw in financial_keywords:
            if kw in text_lower:
                idx = text_lower.index(kw)
                context = full_text[idx:idx + 200]
                extracted[kw] = context.strip()

        # Look for management discussion
        md_start = text_lower.find("management discussion")
        if md_start == -1:
            md_start = text_lower.find("directors' report")
        if md_start >= 0:
            extracted["management_discussion_excerpt"] = full_text[md_start:md_start + 1000]

        return {
            "pages_analyzed": min(30, len(full_text.split("\f"))),
            "financial_metrics_found": len(extracted),
            "extracted": extracted,
            "note": "For detailed analysis, send to Ultron agent with the extracted text.",
        }

    except Exception as e:
        logger.error(f"Annual report analysis failed: {e}")
        return {"error": str(e)}
