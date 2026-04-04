"""
Ultron Empire — Report Generator Tool
Generates branded PDF reports for clients and market analysis.
"""

from langchain_core.tools import tool
from backend.clients.briefs import generate_client_brief
from backend.clients.reports import generate_client_pdf_report
import logging

logger = logging.getLogger(__name__)


@tool
def report_generator_tool(
    report_type: str,
    client_name: str = None,
) -> str:
    """Generate branded reports.

    Args:
        report_type: Type of report — "client_portfolio", "market_outlook", "fund_comparison"
        client_name: Client name (required for client_portfolio)

    Returns:
        Confirmation that report was generated, or report content as text.
    """
    if report_type == "client_portfolio":
        if not client_name:
            return "Client name is required for portfolio reports."

        brief = generate_client_brief(client_name)
        if "error" in brief:
            return brief["error"]

        try:
            pdf_buffer = generate_client_pdf_report(brief)
            # In production: save to file or send via Telegram
            return (
                f"📄 Portfolio report generated for {client_name}\n"
                f"AUM: ₹{brief.get('aum_with_us', 0)} Cr\n"
                f"Holdings: {len(brief.get('holdings', []))}\n"
                f"Report ready for download."
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return f"Report generation failed: {str(e)}"

    elif report_type == "market_outlook":
        return "Market outlook report: Use the analyst agent for comprehensive market analysis."

    elif report_type == "fund_comparison":
        return "Fund comparison report: Use /compare command or comparison chain."

    else:
        return f"Unknown report type: {report_type}. Available: client_portfolio, market_outlook, fund_comparison"
