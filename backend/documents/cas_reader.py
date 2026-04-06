"""
Ultron Empire — CAS Statement Reader
Parses Consolidated Account Statements to extract holdings.
"""

import logging
import re
from io import BytesIO

logger = logging.getLogger(__name__)


def _extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using the best available library.

    Tries pdfplumber first (better table/layout extraction), then falls back
    to PyPDF2/pypdf for simpler text extraction.
    """
    # Try pdfplumber first — best for CAS statements with tabular data
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages)
        if text.strip():
            return text
    except ImportError:
        logger.info("pdfplumber not available, trying fallback PDF readers")
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}, trying fallback")

    # Fallback: pypdf (modern) or PyPDF2 (legacy)
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader

        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
        if text.strip():
            return text
    except ImportError:
        logger.warning("Neither pypdf nor PyPDF2 available")
    except Exception as e:
        logger.warning(f"PyPDF2/pypdf extraction failed: {e}")

    raise RuntimeError(
        "No PDF reader available. Install pdfplumber (`pip install pdfplumber`) "
        "or pypdf (`pip install pypdf`)."
    )


def _extract_fund_names(text: str) -> list[dict]:
    """Extract fund/scheme names from CAS text."""
    funds = []
    seen = set()

    # Pattern 1: Explicit "Fund Name:" or "Scheme Name:" labels
    label_pat = re.compile(
        r"(?:Fund\s*Name|Scheme\s*Name)\s*[:\-]\s*(.+)",
        re.IGNORECASE,
    )
    for m in label_pat.finditer(text):
        name = m.group(1).strip().rstrip("-").strip()
        if name and name not in seen:
            funds.append({"fund_name": name, "source": "label"})
            seen.add(name)

    # Pattern 2: Lines containing typical MF naming conventions
    mf_pat = re.compile(
        r"^(.+(?:Mutual\s+Fund|MUTUAL\s+FUND).*)$"
        r"|^(.+(?:-\s*(?:Direct|Regular)\s+(?:Plan|Growth|Dividend|IDCW)).*)$",
        re.MULTILINE | re.IGNORECASE,
    )
    for m in mf_pat.finditer(text):
        name = (m.group(1) or m.group(2) or "").strip()
        # Clean up stray numbers/values that might trail the name
        name = re.sub(r"\s{2,}.*", "", name)
        if name and len(name) > 5 and name not in seen:
            funds.append({"fund_name": name, "source": "pattern"})
            seen.add(name)

    return funds


def _extract_folio_numbers(text: str) -> list[str]:
    """Extract folio numbers (alphanumeric codes near 'Folio')."""
    folios = []
    folio_pat = re.compile(
        r"Folio\s*(?:No\.?|Number)?\s*[:\-]?\s*([A-Za-z0-9/\-]{4,20})",
        re.IGNORECASE,
    )
    for m in folio_pat.finditer(text):
        val = m.group(1).strip()
        if val and val not in folios:
            folios.append(val)
    return folios


def _extract_nav_values(text: str) -> list[dict]:
    """Extract NAV / Unit Price values."""
    results = []
    nav_pat = re.compile(
        r"(?:NAV|Unit\s*Price|Net\s*Asset\s*Value)\s*[:\-]?\s*"
        r"(?:[₹Rs\.INR\s]*)"
        r"([\d,]+\.?\d*)",
        re.IGNORECASE,
    )
    for m in nav_pat.finditer(text):
        try:
            val = float(m.group(1).replace(",", ""))
            results.append({"nav": val, "context": text[max(0, m.start() - 30):m.end() + 10].strip()})
        except ValueError:
            continue
    return results


def _extract_units(text: str) -> list[dict]:
    """Extract units held."""
    results = []
    units_pat = re.compile(
        r"(?:Units|Balance\s*Units|Unit\s*Balance|Quantity)\s*[:\-]?\s*"
        r"([\d,]+\.?\d*)",
        re.IGNORECASE,
    )
    for m in units_pat.finditer(text):
        try:
            val = float(m.group(1).replace(",", ""))
            if val > 0:
                results.append({"units": val})
        except ValueError:
            continue
    return results


def _extract_current_values(text: str) -> list[dict]:
    """Extract current/market values of holdings."""
    results = []
    val_pat = re.compile(
        r"(?:Current\s*Value|Market\s*Value|Valuation|Amount)\s*[:\-]?\s*"
        r"(?:[₹Rs\.INR\s]*)"
        r"([\d,]+\.?\d*)",
        re.IGNORECASE,
    )
    for m in val_pat.finditer(text):
        try:
            val = float(m.group(1).replace(",", ""))
            if val > 0:
                results.append({"value": val})
        except ValueError:
            continue
    return results


def parse_cas_statement(pdf_path: str) -> dict:
    """Parse a CAS (Consolidated Account Statement) PDF.

    Extracts:
    - All mutual fund holdings (fund names, folio numbers)
    - NAV values, units held, current values
    - Portfolio valuation and summary statistics

    Args:
        pdf_path: Path to the CAS PDF file

    Returns:
        Parsed CAS data with holdings breakdown and summary statistics.
    """
    try:
        full_text = _extract_text_from_pdf(pdf_path)

        # --- Structured extraction ---
        fund_names = _extract_fund_names(full_text)
        folio_numbers = _extract_folio_numbers(full_text)
        nav_values = _extract_nav_values(full_text)
        units_list = _extract_units(full_text)
        current_values = _extract_current_values(full_text)

        # --- Line-by-line holdings parsing (original heuristic, improved) ---
        holdings = []
        total_value = 0.0
        lines = full_text.split("\n")
        current_fund = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect fund names (ALL CAPS, or containing growth/direct/regular)
            if (
                "MUTUAL FUND" in line.upper()
                or "- GROWTH" in line.upper()
                or "- DIRECT" in line.upper()
                or "- REGULAR" in line.upper()
                or "- IDCW" in line.upper()
                or re.search(r"Scheme\s*Name\s*:", line, re.IGNORECASE)
            ):
                current_fund = line

            # Detect value lines (contain digits)
            if current_fund and any(c.isdigit() for c in line):
                parts = line.split()
                for part in parts:
                    try:
                        value = float(part.replace(",", "").replace("₹", "").replace("Rs", ""))
                        if value > 100:  # Likely a portfolio value, not a date or count
                            holdings.append({
                                "fund": current_fund,
                                "value": value,
                            })
                            total_value += value
                            current_fund = None
                            break
                    except ValueError:
                        continue

        # --- Summary statistics ---
        all_values = [h["value"] for h in holdings]
        summary = {
            "total_funds_found": len(fund_names) or len(holdings),
            "total_portfolio_value": round(total_value, 2),
            "folio_count": len(folio_numbers),
        }
        if all_values:
            summary["average_holding_value"] = round(sum(all_values) / len(all_values), 2)
            summary["largest_holding"] = round(max(all_values), 2)
            summary["smallest_holding"] = round(min(all_values), 2)

        return {
            "summary": summary,
            "holdings_count": len(holdings),
            "total_value": round(total_value, 2),
            "holdings": holdings,
            "fund_names": fund_names,
            "folio_numbers": folio_numbers,
            "nav_values": nav_values,
            "units": units_list,
            "current_values": current_values,
            "raw_text_length": len(full_text),
            "note": "CAS parsing is approximate — verify with actual statement",
        }

    except Exception as e:
        logger.error(f"CAS parsing failed: {e}")
        return {"error": str(e)}
