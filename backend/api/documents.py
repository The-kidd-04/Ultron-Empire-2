"""
Ultron Empire — Documents API
Upload and analyze financial documents (CAS, factsheets, term sheets, annual reports).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_DOC_TYPES = {
    "cas": {
        "label": "CAS Statement",
        "description": "Consolidated Account Statement — lists all mutual fund holdings",
        "keywords": ["consolidated account statement", "cas", "mutual fund", "folio", "units", "nav"],
    },
    "factsheet": {
        "label": "PMS/AIF Factsheet",
        "description": "Portfolio Management Service or AIF factsheet with performance data",
        "keywords": ["factsheet", "fact sheet", "pms", "aif", "returns", "benchmark", "sharpe", "top holdings"],
    },
    "term_sheet": {
        "label": "AIF Term Sheet / PPM",
        "description": "Private Placement Memorandum or term sheet for an AIF",
        "keywords": ["term sheet", "ppm", "private placement", "hurdle rate", "management fee", "drawdown"],
    },
    "annual_report": {
        "label": "Company Annual Report",
        "description": "Annual report of a listed or private company",
        "keywords": ["annual report", "directors' report", "revenue from operations", "balance sheet", "profit and loss"],
    },
}


def _detect_document_type(text: str) -> str:
    """Auto-detect document type based on keyword density in the content."""
    text_lower = text.lower()
    scores: dict[str, int] = {}

    for doc_type, info in SUPPORTED_DOC_TYPES.items():
        score = sum(1 for kw in info["keywords"] if kw in text_lower)
        scores[doc_type] = score

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    if scores[best] == 0:
        return "unknown"
    return best


def _extract_preview_text(pdf_path: str, max_pages: int = 5) -> str:
    """Extract text from the first few pages for type detection."""
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages[:max_pages]
            return "\n".join(page.extract_text() or "" for page in pages)
    except ImportError:
        pass
    except Exception:
        pass

    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader

        reader = PdfReader(pdf_path)
        pages = reader.pages[:max_pages]
        return "\n".join(page.extract_text() or "" for page in pages)
    except Exception:
        pass

    return ""


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document.

    Accepts a PDF file, auto-detects its type (CAS, factsheet, term sheet,
    annual report), and returns structured extracted data.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Detect document type from first few pages
        preview_text = _extract_preview_text(tmp_path)
        doc_type = _detect_document_type(preview_text)

        # Route to the appropriate analyzer
        if doc_type == "cas":
            from backend.documents.cas_reader import parse_cas_statement
            result = parse_cas_statement(tmp_path)
        elif doc_type == "factsheet":
            from backend.documents.factsheet_analyzer import analyze_factsheet
            result = analyze_factsheet(tmp_path)
        elif doc_type == "term_sheet":
            from backend.documents.term_sheet_scanner import scan_term_sheet
            result = scan_term_sheet(tmp_path)
        elif doc_type == "annual_report":
            from backend.documents.annual_report import analyze_annual_report
            result = analyze_annual_report(tmp_path)
        else:
            # Unknown type — still try to use the AI agent for analysis
            try:
                from backend.agents.analyst import chat_with_ultron
                ai_result = await chat_with_ultron(
                    f"A document was uploaded: {file.filename}. "
                    f"Analyze it. If it's a CAS statement, map all holdings and identify gaps. "
                    f"If it's a factsheet, extract key metrics and compare with peers. "
                    f"If it's a term sheet, summarize key terms and flag any concerns."
                )
                result = {
                    "ai_analysis": ai_result.get("response", ""),
                    "tools_used": ai_result.get("tools_used", []),
                }
            except Exception as e:
                logger.warning(f"AI analysis fallback failed: {e}")
                result = {"note": "Could not determine document type or analyze content."}

        return {
            "filename": file.filename,
            "detected_type": doc_type,
            "type_label": SUPPORTED_DOC_TYPES.get(doc_type, {}).get("label", "Unknown"),
            "data": result,
        }
    finally:
        os.unlink(tmp_path)


@router.get("/types")
async def get_supported_document_types():
    """Return the list of supported document types and their descriptions."""
    return {
        "supported_types": [
            {"type": key, "label": info["label"], "description": info["description"]}
            for key, info in SUPPORTED_DOC_TYPES.items()
        ]
    }
