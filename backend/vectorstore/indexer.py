"""
Ultron Empire — Knowledge Base Indexer
Indexes all knowledge_base JSON files and fund data into Pinecone.

Usage:
    python -m backend.vectorstore.indexer
"""

import json
import logging
import os
import re
import sys
from pathlib import Path

from backend.vectorstore.embeddings import upsert_fund_data, upsert_knowledge

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token-aware chunking (approximate: 1 token ~ 4 chars for English)
# ---------------------------------------------------------------------------

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50
CHARS_PER_TOKEN = 4  # rough estimate


def _chunk_text(text: str) -> list[str]:
    """Split *text* into overlapping chunks of ~500 tokens each."""
    chunk_chars = CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN
    overlap_chars = CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN

    if len(text) <= chunk_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_chars
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_chars - overlap_chars
    return [c for c in chunks if c]


# ---------------------------------------------------------------------------
# Flatten JSON into readable text
# ---------------------------------------------------------------------------


def _flatten_json(data, prefix: str = "") -> str:
    """Recursively flatten a JSON object into human-readable text."""
    lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            label = f"{prefix}{key}" if not prefix else f"{prefix} > {key}"
            if isinstance(value, (dict, list)):
                lines.append(_flatten_json(value, label))
            else:
                lines.append(f"{label}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                lines.append(_flatten_json(item, f"{prefix}[{i}]"))
            else:
                lines.append(f"{prefix}: {item}")
    else:
        lines.append(f"{prefix}: {data}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Index knowledge_base JSON files
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"


def index_knowledge_base() -> int:
    """Index all JSON files from the knowledge_base/ directory.

    Returns the total number of chunks upserted.
    """
    if not KNOWLEDGE_BASE_DIR.exists():
        logger.warning("knowledge_base directory not found at %s", KNOWLEDGE_BASE_DIR)
        return 0

    json_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.json"))
    if not json_files:
        logger.warning("No JSON files found in %s", KNOWLEDGE_BASE_DIR)
        return 0

    total_chunks = 0
    for filepath in json_files:
        filename = filepath.stem  # e.g. "pms_universe"
        logger.info("Indexing knowledge file: %s", filepath.name)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("Failed to read %s: %s", filepath.name, e)
            continue

        # Extract description from metadata if present
        description = ""
        if isinstance(data, dict) and "metadata" in data:
            description = data["metadata"].get("description", "")

        # Flatten to text and chunk
        text = _flatten_json(data)
        chunks = _chunk_text(text)

        for idx, chunk in enumerate(chunks):
            doc_id = f"kb-{filename}-{idx:04d}"
            metadata = {
                "source": filepath.name,
                "source_type": "knowledge_base",
                "description": description,
                "chunk_index": idx,
                "total_chunks": len(chunks),
            }
            success = upsert_knowledge(doc_id, chunk, metadata)
            if success:
                total_chunks += 1

        logger.info(
            "  -> %s: %d chunks indexed", filepath.name, len(chunks)
        )

    logger.info("Knowledge base indexing complete: %d total chunks", total_chunks)
    return total_chunks


# ---------------------------------------------------------------------------
# Index fund data from database
# ---------------------------------------------------------------------------


def index_fund_data() -> int:
    """Load all funds from the database and index them into Pinecone.

    Returns the number of fund vectors upserted.
    """
    try:
        from backend.db.database import SessionLocal
        from backend.db.models import FundData
    except Exception as e:
        logger.error("Cannot import database modules: %s", e)
        return 0

    session = SessionLocal()
    try:
        funds = session.query(FundData).all()
        if not funds:
            logger.warning("No funds found in database — nothing to index")
            return 0

        fund_dicts = []
        for f in funds:
            description_parts = []
            if f.fund_manager:
                description_parts.append(f"Managed by {f.fund_manager}")
            if f.aum:
                description_parts.append(f"AUM {f.aum} Cr")
            if f.returns_1y is not None:
                description_parts.append(f"1Y return {f.returns_1y:+.1f}%")
            if f.benchmark:
                description_parts.append(f"Benchmark: {f.benchmark}")

            fund_dicts.append(
                {
                    "id": f.id,
                    "fund_name": f.fund_name,
                    "fund_house": f.fund_house or "",
                    "category": f.category or "",
                    "strategy": f.strategy or "",
                    "description": ". ".join(description_parts),
                }
            )

        logger.info("Indexing %d funds from database...", len(fund_dicts))
        return upsert_fund_data(fund_dicts)
    except Exception as e:
        logger.error("Fund indexing failed: %s", e)
        return 0
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_full_index():
    """Run a complete indexing pipeline: knowledge base + fund data."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    logger.info("=" * 60)
    logger.info("Ultron Empire — Pinecone Indexer Starting")
    logger.info("=" * 60)

    kb_count = index_knowledge_base()
    fund_count = index_fund_data()

    logger.info("=" * 60)
    logger.info(
        "Indexing complete: %d knowledge chunks, %d fund vectors",
        kb_count,
        fund_count,
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    run_full_index()
