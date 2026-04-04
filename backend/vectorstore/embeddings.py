"""
Ultron Empire — Pinecone Vector Store Integration
Handles embeddings generation and semantic search via Pinecone.
"""

import logging
from typing import Optional

from openai import OpenAI

from backend.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pinecone + OpenAI clients (lazy-initialized)
# ---------------------------------------------------------------------------
_pinecone_index = None
_openai_client = None

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


def _get_openai_client() -> Optional[OpenAI]:
    """Return a cached OpenAI client, or None if no key is configured."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not configured — embeddings unavailable")
        return None
    _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _get_pinecone_index():
    """Return a cached Pinecone Index object, or None if not configured."""
    global _pinecone_index
    if _pinecone_index is not None:
        return _pinecone_index
    if not settings.PINECONE_API_KEY:
        logger.warning("PINECONE_API_KEY not configured — vector search unavailable")
        return None
    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        _pinecone_index = pc.Index(settings.PINECONE_INDEX)
        logger.info(
            "Connected to Pinecone index '%s' in '%s'",
            settings.PINECONE_INDEX,
            settings.PINECONE_ENVIRONMENT,
        )
        return _pinecone_index
    except Exception as e:
        logger.error("Pinecone initialization failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for *text* using OpenAI text-embedding-3-small.

    Returns an empty list if the OpenAI client is not available.
    """
    client = _get_openai_client()
    if client is None:
        return []
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error("Embedding generation failed: %s", e)
        return []


def upsert_fund_data(funds: list[dict]) -> int:
    """Embed fund name+strategy+description and upsert into Pinecone.

    Each dict should have at minimum ``id``, ``fund_name``, and optionally
    ``strategy``, ``description``, ``category``, ``fund_house``.

    Returns the number of vectors upserted (0 if Pinecone is unavailable).
    """
    index = _get_pinecone_index()
    if index is None:
        logger.warning("Pinecone not available — skipping fund data upsert")
        return 0

    vectors = []
    for fund in funds:
        text = " ".join(
            filter(
                None,
                [
                    fund.get("fund_name", ""),
                    fund.get("strategy", ""),
                    fund.get("description", ""),
                    fund.get("category", ""),
                ],
            )
        )
        embedding = get_embedding(text)
        if not embedding:
            continue

        metadata = {
            "type": "fund",
            "fund_name": fund.get("fund_name", ""),
            "category": fund.get("category", ""),
            "strategy": fund.get("strategy", ""),
            "fund_house": fund.get("fund_house", ""),
        }
        vectors.append(
            {
                "id": f"fund-{fund.get('id', fund.get('fund_name', '').replace(' ', '-').lower())}",
                "values": embedding,
                "metadata": metadata,
            }
        )

    if not vectors:
        return 0

    # Pinecone recommends batches of 100
    batch_size = 100
    upserted = 0
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        try:
            index.upsert(vectors=batch)
            upserted += len(batch)
        except Exception as e:
            logger.error("Pinecone upsert batch failed: %s", e)
    logger.info("Upserted %d fund vectors to Pinecone", upserted)
    return upserted


def upsert_knowledge(doc_id: str, text: str, metadata: dict) -> bool:
    """Embed and store a single knowledge-base document chunk.

    Returns True on success, False otherwise.
    """
    index = _get_pinecone_index()
    if index is None:
        logger.warning("Pinecone not available — skipping knowledge upsert")
        return False

    embedding = get_embedding(text)
    if not embedding:
        return False

    meta = {**metadata, "type": "knowledge", "text": text[:1000]}
    try:
        index.upsert(vectors=[{"id": doc_id, "values": embedding, "metadata": meta}])
        return True
    except Exception as e:
        logger.error("Knowledge upsert failed for '%s': %s", doc_id, e)
        return False


def search_similar(
    query: str,
    top_k: int = 5,
    filter: Optional[dict] = None,
) -> list[dict]:
    """Perform semantic search over the Pinecone index.

    Returns a list of dicts with keys ``id``, ``score``, and ``metadata``.
    Returns an empty list if Pinecone/OpenAI are not configured.
    """
    index = _get_pinecone_index()
    if index is None:
        logger.warning("Pinecone not available — returning empty search results")
        return []

    embedding = get_embedding(query)
    if not embedding:
        return []

    try:
        kwargs = {
            "vector": embedding,
            "top_k": top_k,
            "include_metadata": True,
        }
        if filter:
            kwargs["filter"] = filter
        response = index.query(**kwargs)

        results = []
        for match in response.get("matches", []):
            results.append(
                {
                    "id": match["id"],
                    "score": round(match["score"], 4),
                    "metadata": match.get("metadata", {}),
                }
            )
        return results
    except Exception as e:
        logger.error("Pinecone search failed: %s", e)
        return []
