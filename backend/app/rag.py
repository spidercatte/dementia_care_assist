import logging
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai
from google.genai import errors
from app.config import settings

logger = logging.getLogger("dementiacare-rag")
logging.basicConfig(level=logging.INFO)

# Custom embedding function utilizing the Gemini API's text-embedding-004 model
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        self.client = None
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            logger.warning("No Gemini API key provided. RAG embeddings will fail if API key is not supplied later.")

    def __call__(self, texts: Documents) -> Embeddings:
        if not self.client:
            # Try to initialize client if key is set in settings now
            if settings.gemini_api_key:
                self.client = genai.Client(api_key=settings.gemini_api_key)
            else:
                logger.warning("Gemini API Client is not initialized. Generating dummy mock embeddings.")
                return [[0.0] * 768 for _ in texts]

        try:
            embeddings = []
            for text in texts:
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                embeddings.append(response.embeddings[0].values)
            return embeddings
        except Exception as e:
            logger.warning(f"Failed to generate embeddings via Gemini API: {e}. Falling back to deterministic mock embeddings.")
            embeddings = []
            for text in texts:
                import hashlib
                h = hashlib.sha256(text.encode('utf-8')).digest()
                vector = []
                for i in range(768):
                    val = (h[i % len(h)] + i) % 256
                    vector.append((val / 255.0) - 0.5)
                embeddings.append(vector)
            return embeddings

def get_chroma_client():
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
        # Parse into a friendly list of dicts
        parsed_results = []
        if results and results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                parsed_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
                })
        return parsed_results
    except Exception as e:
        logger.error(f"Error querying guidelines: {e}")
        return []

def seed_default_guidelines():
    import os
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    file_path = os.path.join(data_dir, "dementia_care_guidelines.md")

    if not os.path.exists(file_path):
        logger.error(f"Guidelines markdown file not found at: {file_path}")
        return

    try:
        collection = get_collection()
        try:
            if collection.count() > 0:
                logger.info("ChromaDB guidelines collection already has documents. Skipping seeding.")
                return
        except Exception as e:
            logger.warning(f"Could not check ChromaDB collection count: {e}. Proceeding with seeding.")

        with open(file_path, "r") as f:
            content = f.read()

        sections = content.split("##")
        # First section is '# Clinical Dementia Care Guidelines\n\n', discard it
        sections = sections[1:]

        for idx, sec in enumerate(sections):
            lines = sec.strip().split("\n")
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()

            # Simple slug generator for ID
            doc_id = title.lower().replace(" ", "_").replace("/", "_").replace("&", "_").replace("(", "").replace(")", "")

            ingest_guideline(
                doc_id=doc_id,
                text=body,
                category="Dementia Care Protocol",
                title=title
            )
        logger.info("Successfully seeded default dementia care guidelines from markdown file.")
    except Exception as e:
        logger.error(f"Error seeding guidelines from file: {e}")
        raise e
