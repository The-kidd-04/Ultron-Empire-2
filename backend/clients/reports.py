"""
Ultron Empire — Client Report Generator
Generates branded PDF reports for client meetings.
"""

import logging
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from backend.utils.brand import DEEP_TEAL, EMERALD_GREEN, BRAND_NAME, TAGLINE, WEBSITE

logger = logging.getLogger(__name__)


def generate_client_pdf_report(brief: dict) -> BytesIO:
    """Generate a branded PDF report from a client brief.

    Args:
        brief: Client brief dict from briefs.generate_client_brief()

    Returns:
        BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BrandTitle",
        parent=styles["Title"],
        textColor=HexColor(DEEP_TEAL),
        fontSize=20,
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "BrandHeading",
        parent=styles["Heading2"],
        textColor=HexColor(EMERALD_GREEN),
        fontSize=14,
        spaceAfter=10,
    )

    elements = []

    # Title
    client = brief.get("client", {})
    elements.append(Paragraph(f"{BRAND_NAME} — Client Report", title_style))
    elements.append(Paragraph(f"Prepared for: {client.get('name', 'N/A')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Client Profile
    elements.append(Paragraph("Client Profile", heading_style))
    profile_data = [
        ["Name", client.get("name", "N/A")],
        ["Age", str(client.get("age", "N/A"))],
        ["Risk Profile", client.get("risk_profile", "N/A")],
        ["Horizon", f"{client.get('investment_horizon', 'N/A')} years"],
        ["Total Wealth", f"₹{brief.get('total_wealth', 0)} Cr"],
        ["AUM with Us", f"₹{brief.get('aum_with_us', 0)} Cr"],
    ]
    table = Table(profile_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#F5F7FA")),
        ("TEXTCOLOR", (0, 0), (0, -1), HexColor(DEEP_TEAL)),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D3D3D3")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Holdings
    elements.append(Paragraph("Current Holdings", heading_style))
    holdings = brief.get("holdings", [])
    if holdings:
        h_data = [["Fund", "Amount (Cr)", "1Y Return", "Since"]]
        for h in holdings:
            ret = f"{h['returns_1y']:+.1f}%" if h.get("returns_1y") else "N/A"
            h_data.append([h["product"], f"₹{h['amount_cr']}", ret, h.get("since", "N/A")])
        h_table = Table(h_data, colWidths=[180, 80, 80, 100])
        h_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor(EMERALD_GREEN)),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#D3D3D3")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(h_table)

    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph(
        f"{BRAND_NAME} | {TAGLINE} | {WEBSITE}",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=HexColor("#999999")),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
