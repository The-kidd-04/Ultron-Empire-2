"""
Ultron Empire — Vector Store Integration
Uses ChromaDB (local) + sentence-transformers for free, local semantic search.
No external API keys required.
"""

import logging
from typing import Optional

import chromadb

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding model (local, free)
# ---------------------------------------------------------------------------
_embedding_model = None


def _get_embedding_model():
    """Lazy-load the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not installed — embeddings unavailable")
            return None
        except Exception as e:
            logger.warning(f"Embedding model load failed: {e}")
            return None
    return _embedding_model


# ---------------------------------------------------------------------------
# ChromaDB client (local persistent storage)
# ---------------------------------------------------------------------------
_chroma_client = None
_collection = None

COLLECTION_NAME = "ultron_knowledge"
CHROMA_PATH = "./data/chroma_db"


def _get_collection():
    """Get or create the ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    try:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{COLLECTION_NAME}' ready ({_collection.count()} docs)")
        return _collection
    except Exception as e:
        logger.error(f"ChromaDB initialization failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector using local sentence-transformers model."""
    model = _get_embedding_model()
    if model is None:
        return []
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []


def upsert_fund_data(funds: list[dict]) -> int:
    """Embed fund data and store in ChromaDB."""
    collection = _get_collection()
    if collection is None:
        return 0

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for fund in funds:
        text = " ".join(filter(None, [
            fund.get("fund_name", ""),
            fund.get("strategy", ""),
            fund.get("description", ""),
            fund.get("category", ""),
            fund.get("fund_house", ""),
        ]))

        embedding = get_embedding(text)
        if not embedding:
            continue

        fund_id = f"fund-{fund.get('id', fund.get('fund_name', '').replace(' ', '-').lower())}"
        ids.append(fund_id)
        documents.append(text)
        metadatas.append({
            "type": "fund",
            "fund_name": fund.get("fund_name", ""),
            "category": fund.get("category", ""),
            "strategy": fund.get("strategy", ""),
            "fund_house": fund.get("fund_house", ""),
        })
        embeddings.append(embedding)

    if not ids:
        return 0

    try:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        logger.info(f"Upserted {len(ids)} fund vectors to ChromaDB")
        return len(ids)
    except Exception as e:
        logger.error(f"ChromaDB fund upsert failed: {e}")
        return 0


def upsert_knowledge(doc_id: str, text: str, metadata: dict) -> bool:
    """Embed and store a single knowledge-base document chunk."""
    collection = _get_collection()
    if collection is None:
        return False

    embedding = get_embedding(text)
    if not embedding:
        return False

    meta = {**metadata, "type": metadata.get("type", "knowledge"), "text": text[:1000]}
    try:
        collection.upsert(ids=[doc_id], documents=[text], metadatas=[meta], embeddings=[embedding])
        return True
    except Exception as e:
        logger.error(f"Knowledge upsert failed for '{doc_id}': {e}")
        return False


def search_similar(
    query: str,
    top_k: int = 5,
    filter: Optional[dict] = None,
) -> list[dict]:
    """Perform semantic search over the ChromaDB collection."""
    collection = _get_collection()
    if collection is None:
        return []

    embedding = get_embedding(query)
    if not embedding:
        return []

    try:
        kwargs = {
            "query_embeddings": [embedding],
            "n_results": top_k,
            "include": ["metadatas", "distances", "documents"],
        }
        if filter:
            kwargs["where"] = filter

        results = collection.query(**kwargs)

        output = []
        if results and results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances; convert to similarity score
                distance = results["distances"][0][i] if results.get("distances") else 0
                score = max(0, 1 - distance)  # cosine distance to similarity

                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                output.append({
                    "id": doc_id,
                    "score": round(score, 4),
                    "metadata": metadata,
                })
        return output
    except Exception as e:
        logger.error(f"ChromaDB search failed: {e}")
        return []


def get_collection_stats() -> dict:
    """Get stats about the ChromaDB collection."""
    collection = _get_collection()
    if collection is None:
        return {"status": "unavailable", "count": 0}
    return {
        "status": "ready",
        "count": collection.count(),
        "name": COLLECTION_NAME,
    }
