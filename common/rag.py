import hashlib
import logging
from typing import cast

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai

from common.config import settings

logger = logging.getLogger("dementiacare-rag")


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        self.client = None
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            logger.warning("No Gemini API key provided. RAG embeddings will fail if API key is not supplied later.")

    def __call__(self, texts: Documents) -> Embeddings:
        if not self.client:
            if settings.gemini_api_key:
                self.client = genai.Client(api_key=settings.gemini_api_key)
            else:
                logger.warning("Gemini API Client is not initialized. Generating dummy mock embeddings.")
                return cast(Embeddings, [[0.0] * 768 for _ in texts])
        try:
            embeddings = []
            for text in texts:
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if response.embeddings and len(response.embeddings) > 0 and response.embeddings[0].values:
                    embeddings.append(response.embeddings[0].values)
                else:
                    embeddings.append([0.0] * 768)
            return cast(Embeddings, embeddings)
        except Exception as e:
            logger.warning(f"Failed to generate embeddings via Gemini API: {e}. Falling back to deterministic mock embeddings.")
            embeddings = []
            for text in texts:
                h = hashlib.sha256(text.encode("utf-8")).digest()
                vector = [(((h[i % len(h)] + i) % 256) / 255.0) - 0.5 for i in range(768)]
                embeddings.append(vector)
            return cast(Embeddings, embeddings)


def get_chroma_client():
    if settings.chroma_server_host:
        return chromadb.HttpClient(
            host=settings.chroma_server_host,
            port=settings.chroma_server_port
        )
    return chromadb.PersistentClient(path=settings.chroma_db_path)


def get_collection():
    client = get_chroma_client()
    embedding_function = GeminiEmbeddingFunction(api_key=settings.gemini_api_key)
    return client.get_or_create_collection(
        name="dementia_guidelines",
        embedding_function=embedding_function
    )


def ingest_guideline(doc_id: str, text: str, category: str, title: str):
    collection = get_collection()
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[{"category": category, "title": title}]
    )
    logger.info(f"Ingested guideline: {title} ({category})")


def query_guidelines(query_text: str, n_results: int = 3):
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        parsed_results = []
        if results and results.get("documents") is not None:
            documents = results.get("documents")
            assert documents is not None
            if len(documents) > 0 and documents[0] is not None and len(documents[0]) > 0:
                doc_list = documents[0]
                metadatas = results.get("metadatas")
                ids = results.get("ids")
                distances = results.get("distances")
                for i in range(len(doc_list)):
                    parsed_results.append({
                        "id": ids[0][i] if ids and ids[0] and len(ids[0]) > i else f"doc_{i}",
                        "document": doc_list[i],
                        "metadata": metadatas[0][i] if metadatas and metadatas[0] and len(metadatas[0]) > i else {},
                        "distance": distances[0][i] if distances and distances[0] and len(distances[0]) > i else None
                    })
        return parsed_results
    except Exception as e:
        logger.error(f"Error querying guidelines: {e}")
        return []
