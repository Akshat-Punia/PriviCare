"""
Text chunking utilities.

Splits long documents into overlapping segments suitable for embedding
and retrieval.
"""

import re
from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:
    """Split *text* into overlapping chunks, respecting sentence boundaries.

    The function tries to break on sentence endings (``. ? !``) that fall
    within the target *chunk_size*.  When no sentence boundary is found the
    chunk is cut at exactly *chunk_size* characters.

    Args:
        text: The full document text.
        chunk_size: Target maximum characters per chunk.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not text or not text.strip():
        return []

    # Pre-compile a pattern that matches sentence-ending punctuation
    # followed by whitespace (or end-of-string).
    sentence_end_re = re.compile(r"[.!?]\s+")

    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # If we haven't reached the very end, try to snap to a sentence
        # boundary so we don't cut mid-sentence.
        if end < text_len:
            window = text[start:end]
            # Find the *last* sentence boundary in the window.
            last_boundary = -1
            for match in sentence_end_re.finditer(window):
                last_boundary = match.end()

            if last_boundary > 0:
                end = start + last_boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance the start pointer, applying overlap.
        start = end - overlap if end < text_len else text_len

    return chunks
