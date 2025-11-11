"""
Vector database utilities for indexing chunks.

This module provides core functionality to:
1. Accept chunks conforming to chunk_schema
2. Generate embeddings using bge-m3
3. Store in ChromaDB

Chunking logic is handled by Claude Code directly, not by pre-written scripts.
"""

import os
from pathlib import Path
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer


class VectorIndexer:
    """Handle vector database indexing operations."""

    def __init__(self, db_path: str = "./vector_db", model_name: str = "BAAI/bge-m3"):
        """
        Initialize indexer.

        Args:
            db_path: Path to ChromaDB database
            model_name: Sentence transformer model name
        """
        self.db_path = db_path
        self.model_name = model_name
        self.model = None
        self.client = None
        self.collection = None

    def initialize_db(self):
        """Initialize or recreate vector database."""
        print(f"🤖 Loading embedding model ({self.model_name})...")
        self.model = SentenceTransformer(self.model_name)

        print(f"💾 Initializing vector database at: {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Delete existing collection
        try:
            self.client.delete_collection("notes")
            print("   Deleted existing collection")
        except:
            pass

        # Create new collection
        self.collection = self.client.create_collection(
            name="notes",
            metadata={"hnsw:space": "cosine"}
        )
        print("   Created new collection")

    def index_chunks(self, chunks: List[Dict]) -> None:
        """
        Index chunks into vector database.

        Args:
            chunks: List of chunks conforming to chunk_schema.Chunk format
        """
        if not self.collection:
            raise RuntimeError("Database not initialized. Call initialize_db() first")

        print(f"🔄 Indexing {len(chunks)} chunks...")

        for i, chunk in enumerate(chunks):
            try:
                # Validate chunk has required fields
                if 'content' not in chunk or 'metadata' not in chunk:
                    print(f"  ⚠️  Skipping chunk {i}: missing content or metadata")
                    continue

                # Generate embedding
                embedding = self.model.encode(chunk['content']).tolist()

                # Prepare metadata (convert all to strings for ChromaDB)
                metadata = {}
                for key, value in chunk['metadata'].items():
                    metadata[key] = str(value) if value is not None else ""

                # Add to collection
                self.collection.add(
                    ids=[f"chunk_{i}"],
                    embeddings=[embedding],
                    documents=[chunk['content']],
                    metadatas=[metadata]
                )

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"  ✓ Indexed {i + 1}/{len(chunks)} chunks")

            except Exception as e:
                print(f"  ✗ Failed to index chunk {i}: {e}")

        print(f"\n✅ Successfully indexed {len(chunks)} chunks")
        print(f"   Database location: {os.path.abspath(self.db_path)}")


def index_chunks_to_db(chunks: List[Dict], db_path: str = "./vector_db") -> None:
    """
    Convenience function to index chunks.

    Args:
        chunks: List of chunks conforming to chunk_schema.Chunk
        db_path: Path to vector database
    """
    indexer = VectorIndexer(db_path=db_path)
    indexer.initialize_db()
    indexer.index_chunks(chunks)
