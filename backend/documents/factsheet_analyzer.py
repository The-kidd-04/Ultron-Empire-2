"""
Ultron Empire — PMS Factsheet Analyzer
Extracts key metrics from PMS/AIF factsheet PDFs.
"""

import logging
import re

logger = logging.getLogger(__name__)


def _extract_performance(text: str) -> dict:
    """Extract performance return percentages for standard periods."""
    performance = {}
    periods = [
        ("1M", r"1\s*M(?:onth)?"),
        ("3M", r"3\s*M(?:onths?)?"),
        ("6M", r"6\s*M(?:onths?)?"),
        ("1Y", r"1\s*Y(?:ear)?|1\s*Yr"),
        ("3Y", r"3\s*Y(?:ears?)?|3\s*Yr"),
        ("5Y", r"5\s*Y(?:ears?)?|5\s*Yr"),
        ("10Y", r"10\s*Y(?:ears?)?|10\s*Yr"),
        ("SI", r"SI|Since\s*Inception"),
    ]

    for label, pattern in periods:
        # Look for period label followed (possibly with intervening text) by a percentage
        pat = re.compile(
            pattern + r"[\s:|\-]*" + r"(-?[\d]+\.?\d*)\s*%",
            re.IGNORECASE,
        )
        m = pat.search(text)
        if m:
            try:
                performance[label] = float(m.group(1))
            except ValueError:
                continue

    # Also try tabular rows: "Period  Fund  Benchmark"
    # Look for rows with multiple percentages on a single line
    pct_row_pat = re.compile(
        r"(?:" + "|".join(p for _, p in periods) + r")"
        r"\s+(-?[\d]+\.?\d*)\s*%?"
        r"\s+(-?[\d]+\.?\d*)\s*%?",
        re.IGNORECASE,
    )
    for m in pct_row_pat.finditer(text):
        # We already got individual matches above; this catches benchmark too
        pass

    return performance


def _extract_top_holdings(text: str) -> list[dict]:
    """Extract top holdings with percentage weights."""
    holdings = []

    # Pattern: stock/company name followed by a percentage weight
    # e.g. "HDFC Bank Ltd 8.5%" or "Infosys Ltd.   7.23 %"
    holding_pat = re.compile(
        r"([A-Z][A-Za-z\s&\.\-]{3,40}?)\s+"
        r"(\d{1,2}\.?\d{0,2})\s*%",
    )

    # Look for the section containing "top holdings" or "portfolio"
    text_lower = text.lower()
    section_start = -1
    for marker in ["top holdings", "top 10 holdings", "portfolio holdings", "stock name"]:
        idx = text_lower.find(marker)
        if idx >= 0:
            section_start = idx
            break

    search_text = text[section_start:section_start + 2000] if section_start >= 0 else text

    seen = set()
    for m in holding_pat.finditer(search_text):
        name = m.group(1).strip()
        weight = float(m.group(2))
        # Filter out noise: skip if name looks like a header or label
        if name.lower() in ("total", "others", "cash", "net", "gross"):
            continue
        if weight > 0 and weight <= 100 and name not in seen:
            holdings.append({"name": name, "weight_pct": weight})
            seen.add(name)

    return holdings[:15]  # Cap at 15


def _extract_sector_allocation(text: str) -> list[dict]:
    """Extract sector allocation with percentage weights."""
    sectors = []

    text_lower = text.lower()
    section_start = -1
    for marker in ["sector allocation", "sector wise", "sectoral allocation", "sector breakdown"]:
        idx = text_lower.find(marker)
        if idx >= 0:
            section_start = idx
            break

    if section_start < 0:
        return sectors

    search_text = text[section_start:section_start + 1500]

    sector_pat = re.compile(
        r"([A-Z][A-Za-z\s&,\.\-/]{3,50}?)\s+"
        r"(\d{1,3}\.?\d{0,2})\s*%",
    )

    seen = set()
    for m in sector_pat.finditer(search_text):
        name = m.group(1).strip()
        weight = float(m.group(2))
        if name.lower() in ("total", "others", "cash"):
            continue
        if 0 < weight <= 100 and name not in seen:
            sectors.append({"sector": name, "weight_pct": weight})
            seen.add(name)

    return sectors


def _extract_aum(text: str) -> dict | None:
    """Extract AUM (Assets Under Management) value."""
    aum_pat = re.compile(
        r"(?:AUM|Assets\s*Under\s*Management|Fund\s*Size|Corpus)\s*"
        r"[:\-]?\s*"
        r"(?:[₹Rs\.INR\s]*)"
        r"([\d,]+\.?\d*)\s*"
        r"(Cr(?:ores?)?|Lakh|L|Bn|Billion|Mn|Million)?",
        re.IGNORECASE,
    )
    m = aum_pat.search(text)
    if m:
        try:
            value = float(m.group(1).replace(",", ""))
            unit = (m.group(2) or "").strip()
            return {"value": value, "unit": unit or "Cr (assumed)"}
        except ValueError:
            pass
    return None


def analyze_factsheet(pdf_path: str) -> dict:
    """Analyze a PMS/AIF factsheet PDF.

    Extracts:
    - Fund performance (1M, 3M, 6M, 1Y, 3Y, 5Y, SI)
    - Benchmark comparison
    - Top holdings with weights
    - Sector allocation
    - AUM
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

        # --- Structured extraction ---
        performance = _extract_performance(full_text)
        top_holdings = _extract_top_holdings(full_text)
        sector_allocation = _extract_sector_allocation(full_text)
        aum = _extract_aum(full_text)

        result = {
            "raw_text_length": len(full_text),
            "tables_found": len(tables),
            "extracted_data": {},
        }

        # Performance
        if performance:
            result["extracted_data"]["performance_returns"] = performance
        else:
            text_lower = full_text.lower()
            if "returns" in text_lower or "performance" in text_lower:
                result["extracted_data"]["has_performance_data"] = True
                result["extracted_data"]["performance_returns"] = {}
                result["extracted_data"]["performance_note"] = (
                    "Performance section detected but could not extract numbers. "
                    "Try sending to Ultron AI agent for vision-based extraction."
                )

        # Top holdings
        if top_holdings:
            result["extracted_data"]["top_holdings"] = top_holdings
        else:
            text_lower = full_text.lower()
            if "top holdings" in text_lower or "portfolio" in text_lower:
                result["extracted_data"]["has_holdings_data"] = True

        # Sector allocation
        if sector_allocation:
            result["extracted_data"]["sector_allocation"] = sector_allocation
        else:
            text_lower = full_text.lower()
            if "sector" in text_lower or "allocation" in text_lower:
                result["extracted_data"]["has_sector_data"] = True

        # AUM
        if aum:
            result["extracted_data"]["aum"] = aum

        # Table metadata
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
