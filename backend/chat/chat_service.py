"""
Chat service — convenience wrapper around the RAG pipeline.
"""

from typing import Dict

from rag.pipeline import rag_pipeline


def chat(message: str, user_id: str = "anonymous") -> Dict:
    """Process a chat message through the full RAG pipeline.

    Args:
        message: The user's raw question.
        user_id: Identifier of the requesting user.

    Returns:
        Pipeline result dict (see :func:`rag.pipeline.rag_pipeline`).
    """
    return rag_pipeline(query=message, user_id=user_id)
