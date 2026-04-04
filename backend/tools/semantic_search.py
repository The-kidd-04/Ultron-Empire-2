"""
Ultron Empire — Semantic Search Tool
LangChain tool that performs semantic similarity search over the
Pinecone knowledge base (funds, regulations, glossary, etc.).
"""

import logging

from langchain_core.tools import tool

from backend.vectorstore.embeddings import search_similar

logger = logging.getLogger(__name__)


@tool
def semantic_search_tool(query: str, category: str = None) -> str:
    """Search the knowledge base using semantic similarity for fund information, regulations, glossary terms.

    Use this when you need to find relevant background knowledge, definitions,
    regulatory details, or fund information that may not be in the structured
    database.

    Args:
        query: Natural language search query (e.g., "What are SEBI PMS regulations?")
        category: Optional filter — "fund", "knowledge", or None for all

    Returns:
        Formatted string with top matching results and relevance scores.
    """
    filter_dict = None
    if category:
        filter_dict = {"type": category}

    try:
        results = search_similar(query=query, top_k=5, filter=filter_dict)
    except Exception as e:
        logger.error("Semantic search failed: %s", e)
        return f"Semantic search encountered an error: {e}"

    if not results:
        return (
            f"No semantic matches found for '{query}'. "
            "The knowledge base may not be indexed yet, or Pinecone is not configured. "
            "Try using the fund_lookup tool for structured database queries."
        )

    output_parts = []
    for i, result in enumerate(results, 1):
        meta = result.get("metadata", {})
        score = result.get("score", 0)
        relevance = "High" if score > 0.8 else "Medium" if score > 0.6 else "Low"

        text_preview = meta.get("text", "")[:300]
        source = meta.get("source", meta.get("fund_name", "unknown"))
        doc_type = meta.get("type", "unknown")

        entry = (
            f"[{i}] Relevance: {relevance} ({score:.2f})\n"
            f"    Source: {source} | Type: {doc_type}\n"
        )
        if meta.get("fund_name"):
            entry += f"    Fund: {meta['fund_name']}"
            if meta.get("category"):
                entry += f" ({meta['category']})"
            if meta.get("strategy"):
                entry += f" — {meta['strategy']}"
            entry += "\n"
        if text_preview:
            entry += f"    Content: {text_preview}..."

        output_parts.append(entry)

    header = f"Found {len(results)} semantic matches for '{query}':\n"
    return header + "\n\n".join(output_parts)
