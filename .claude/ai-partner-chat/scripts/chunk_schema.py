"""
Chunk data format specification.

This module defines the required format for document chunks.
All chunking strategies (whether rule-based or AI-generated) must
produce chunks conforming to this schema.
"""

from typing import TypedDict, Optional


class ChunkMetadata(TypedDict, total=False):
    """
    Metadata for a document chunk.

    Required fields:
        filename: Name of source file
        filepath: Full path to source file
        chunk_id: Sequential ID within the file (starting from 0)
        chunk_type: Type of chunk (e.g., 'date_entry', 'section', 'paragraph')

    Optional fields:
        date: Date associated with chunk (YYYY-MM-DD format)
        title: Section or entry title
        sub_chunk_id: ID for sub-chunks when further splitting is needed
        tags: List of tags or keywords
    """
    filename: str
    filepath: str
    chunk_id: int
    chunk_type: str
    date: Optional[str]
    title: Optional[str]
    sub_chunk_id: Optional[int]
    tags: Optional[list[str]]


class Chunk(TypedDict):
    """
    Document chunk format.

    All chunks must have:
        content: The actual text content of the chunk
        metadata: ChunkMetadata with required fields
    """
    content: str
    metadata: ChunkMetadata


def validate_chunk(chunk: dict) -> bool:
    """
    Validate if a chunk conforms to the schema.

    Args:
        chunk: Chunk dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(chunk, dict):
        return False

    if 'content' not in chunk or 'metadata' not in chunk:
        return False

    if not isinstance(chunk['content'], str):
        return False

    metadata = chunk['metadata']
    required_fields = ['filename', 'filepath', 'chunk_id', 'chunk_type']

    for field in required_fields:
        if field not in metadata:
            return False

    return True


# Recommended chunk size constraints
MIN_CHUNK_SIZE = 50      # Minimum characters
MAX_CHUNK_SIZE = 2000    # Maximum characters (can be exceeded for semantic integrity)
TARGET_CHUNK_SIZE = 500  # Target size for optimal retrieval
