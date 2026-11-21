"""
Retrieval helper — combines embedding generation with vector search.
"""

from typing import List

from rag.embeddings import generate_embedding
from rag.vector_db import search


def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List[str]:
    """Embed *query* and retrieve the most relevant document chunks.

    Args:
        query: The user's natural-language query (already anonymised).
        top_k: Maximum number of chunks to return.

    Returns:
        A list of chunk text strings, ordered by similarity.
    """
    query_vector = generate_embedding(query)
    results = search(query_vector, top_k=top_k)
    return [r["text"] for r in results if "text" in r]
