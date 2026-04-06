"""
Ultron Empire — Knowledge Base Seeder
Loads all JSON knowledge files into ChromaDB for semantic search.
Uses sentence-transformers (free, local) for embeddings.

Usage: python -m scripts.seed_knowledge_base
"""

import json
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vectorstore.embeddings import upsert_knowledge, get_collection_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")


def flatten_json(data: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Recursively flatten a JSON structure into (key, text) pairs for embedding."""
    chunks = []
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if key == "metadata":
            continue
        if isinstance(value, str):
            chunks.append((full_key, f"{key}: {value}"))
        elif isinstance(value, (int, float, bool)):
            chunks.append((full_key, f"{key}: {value}"))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    sub = flatten_json(item, f"{full_key}[{i}]")
                    chunks.extend(sub)
                elif isinstance(item, str):
                    chunks.append((f"{full_key}[{i}]", f"{key}: {item}"))
        elif isinstance(value, dict):
            # Create a summary chunk for this section
            summary = json.dumps(value, indent=2, ensure_ascii=False)
            if len(summary) < 2000:
                chunks.append((full_key, f"{key}: {summary}"))
            else:
                sub = flatten_json(value, full_key)
                chunks.extend(sub)
    return chunks


def seed_file(filename: str, doc_type: str) -> int:
    """Seed a single JSON file into ChromaDB."""
    filepath = os.path.join(KB_DIR, filename)
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = flatten_json(data)
    seeded = 0

    for key, text in chunks:
        if len(text.strip()) < 10:
            continue

        doc_id = f"{doc_type}-{key}".replace(" ", "-").replace("[", "-").replace("]", "")
        metadata = {
            "type": doc_type,
            "source": filename,
            "section": key.split(".")[0] if "." in key else key,
        }

        if upsert_knowledge(doc_id, text, metadata):
            seeded += 1

    return seeded


def seed_all():
    """Seed all knowledge base files."""
    files = [
        ("sebi_regulations.json", "regulation"),
        ("pms_universe.json", "fund"),
        ("aif_universe.json", "fund"),
        ("tax_rules.json", "tax"),
        ("risk_profiles.json", "risk"),
        ("fee_structures.json", "fee"),
        ("glossary.json", "glossary"),
        ("benchmarks.json", "benchmark"),
        ("mf_categories.json", "fund"),
        ("ishaan_preferences.json", "preference"),
    ]

    total = 0
    for filename, doc_type in files:
        count = seed_file(filename, doc_type)
        logger.info(f"Seeded {count} chunks from {filename}")
        total += count

    stats = get_collection_stats()
    logger.info(f"Seeding complete. Total chunks: {total}. Collection: {stats}")
    return total


def seed_fund_database():
    """Also seed fund data from the SQLite database."""
    try:
        from backend.db.database import SessionLocal
        from backend.db.models import FundData
        from backend.vectorstore.embeddings import upsert_fund_data

        session = SessionLocal()
        funds = session.query(FundData).all()
        session.close()

        if not funds:
            logger.info("No funds in database to seed")
            return 0

        fund_dicts = [
            {
                "id": f.id,
                "fund_name": f.fund_name,
                "fund_house": f.fund_house,
                "category": f.category,
                "strategy": f.strategy,
            }
            for f in funds
        ]

        count = upsert_fund_data(fund_dicts)
        logger.info(f"Seeded {count} fund records from database")
        return count
    except Exception as e:
        logger.warning(f"Fund database seeding failed: {e}")
        return 0


if __name__ == "__main__":
    logger.info("Starting knowledge base seeding...")
    total_kb = seed_all()
    total_funds = seed_fund_database()
    logger.info(f"Done! Seeded {total_kb} knowledge chunks + {total_funds} fund records")
