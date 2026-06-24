import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest import mock
import chromadb
from app.config import settings
from app.rag import (
    GeminiEmbeddingFunction,
    get_chroma_client,
    get_collection,
    ingest_guideline,
    query_guidelines,
    seed_default_guidelines
)

def test_gemini_embedding_function_mock():
    """
    Verifies that the Gemini embedding function returns 768-dimension vectors under mock mode.
    """
    embedding_fn = GeminiEmbeddingFunction(api_key="")
    texts = ["How to handle medication refusal?", "Positive approach to care."]
    embeddings = embedding_fn(texts)

    assert len(embeddings) == len(texts)
    assert len(embeddings[0]) == 768
    assert all(isinstance(val, (float, int)) or hasattr(val, "dtype") for val in embeddings[0])


def test_chroma_client_initialization():
    """
    Verifies that PersistentClient initializes correctly with settings path.
    """
    client = get_chroma_client()
    assert client is not None
    assert hasattr(client, "heartbeat")


def test_guideline_ingest_and_query():
    """
    Verifies that documents can be ingested into ChromaDB and successfully retrieved.
    """
    # Ingest a mock guideline
    doc_id = "test_guideline_id_123"
    text = "Always validate the patient before trying to redirect them."
    category = "Test Protocol"
    title = "Validation Rule"

    ingest_guideline(
        doc_id=doc_id,
        text=text,
        category=category,
        title=title
    )

    # Query guidelines
    results = query_guidelines("Always validate the patient before trying to redirect them.", n_results=1)

    assert len(results) > 0
    match = None
    for r in results:
        if r["id"] == doc_id:
            match = r
            break

    assert match is not None
    assert match["document"] == text
    assert match["metadata"]["category"] == category
    assert match["metadata"]["title"] == title


def test_seed_default_guidelines():
    """
    Verifies that seeding operation parses the markdown file and inserts records.
    """
    # Execute seeding
    seed_default_guidelines()

    # Query database and verify counts/content exist
    collection = get_collection()
    count = collection.count()
    assert count > 0

    # Query for standard guidelines
    results = query_guidelines("wandering", n_results=1)
    assert len(results) > 0
    assert results[0]["document"]
