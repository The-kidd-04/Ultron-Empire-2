"""
Ultron Empire — Documents API
POST /documents — Process uploaded documents (CAS, factsheets, etc.)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.agents.analyst import chat_with_ultron
import tempfile
import os

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await chat_with_ultron(
            f"A document was uploaded: {file.filename}. "
            f"Analyze it. If it's a CAS statement, map all holdings and identify gaps. "
            f"If it's a factsheet, extract key metrics and compare with peers. "
            f"If it's a term sheet, summarize key terms and flag any concerns."
        )

        return {
            "filename": file.filename,
            "analysis": result["response"],
            "tools_used": result["tools_used"],
        }
    finally:
        os.unlink(tmp_path)
