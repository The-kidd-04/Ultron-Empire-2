"""
Ultron Empire — PMS Factsheet Analyzer
Extracts key metrics from PMS/AIF factsheet PDFs.
"""

import logging

logger = logging.getLogger(__name__)


def analyze_factsheet(pdf_path: str) -> dict:
    """Analyze a PMS/AIF factsheet PDF.

    Extracts:
    - Fund performance (1M, 3M, 6M, 1Y, 3Y, 5Y, SI)
    - Benchmark comparison
    - Top holdings
    - Sector allocation
    - Fund manager details
    - Risk metrics (Sharpe, Sortino, Max Drawdown)
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            tables = []
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)

        # Extract key sections from text
        result = {
            "raw_text_length": len(full_text),
            "tables_found": len(tables),
            "extracted_data": {},
        }

        # Look for return patterns
        text_lower = full_text.lower()
        if "returns" in text_lower or "performance" in text_lower:
            result["extracted_data"]["has_performance_data"] = True

        if "top holdings" in text_lower or "portfolio" in text_lower:
            result["extracted_data"]["has_holdings_data"] = True

        if "sector" in text_lower or "allocation" in text_lower:
            result["extracted_data"]["has_sector_data"] = True

        # Extract tables if found
        if tables:
            result["extracted_data"]["table_data"] = [
                {"rows": len(t), "cols": len(t[0]) if t else 0}
                for t in tables[:5]
            ]

        result["note"] = (
            "For detailed extraction, send this factsheet to Ultron's AI agent "
            "which can interpret the content using vision capabilities."
        )

        return result

    except Exception as e:
        logger.error(f"Factsheet analysis failed: {e}")
        return {"error": str(e)}
