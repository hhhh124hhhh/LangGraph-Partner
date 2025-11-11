"""
Vector database utilities for AI Partner skill.

This module provides functions to query the vector database programmatically.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer


class NoteRetriever:
    """Handle vector database operations for note retrieval."""

    def __init__(self, db_path: str = "./vector_db"):
        """
        Initialize the retriever with a database path.

        Args:
            db_path: Path to ChromaDB database
        """
        self.db_path = db_path
        self.model = None
        self.client = None
        self.collection = None

    def _ensure_initialized(self):
        """Lazy initialization of model and database connection."""
        if self.model is None:
            self.model = SentenceTransformer('BAAI/bge-m3')

        if self.client is None:
            try:
                self.client = chromadb.PersistentClient(path=self.db_path)
                self.collection = self.client.get_collection("notes")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to connect to database at {self.db_path}. "
                    f"Please run init_vector_db.py first. Error: {e}"
                )

    def query(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        Query the vector database for similar notes.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of dicts with 'content', 'path', 'filename' keys
        """
        self._ensure_initialized()

        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        similar_notes = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                similar_notes.append({
                    'content': results['documents'][0][i],
                    'filepath': metadata.get('filepath', ''),
                    'filename': metadata.get('filename', ''),
                    'date': metadata.get('date', ''),
                    'chunk_id': metadata.get('chunk_id', ''),
                    'chunk_type': metadata.get('chunk_type', ''),
                })

        return similar_notes


def get_relevant_notes(query: str, db_path: str = "./vector_db", top_k: int = 5) -> List[Dict[str, str]]:
    """
    Convenience function to retrieve relevant notes.

    Args:
        query: Query text
        db_path: Path to vector database
        top_k: Number of results to return

    Returns:
        List of dicts with 'content', 'path', 'filename' keys
    """
    retriever = NoteRetriever(db_path)
    return retriever.query(query, top_k)
