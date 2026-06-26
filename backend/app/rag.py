import logging
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from typing import cast
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
                import hashlib
                h = hashlib.sha256(text.encode('utf-8')).digest()
                vector = []
                for i in range(768):
                    val = (h[i % len(h)] + i) % 256
                    vector.append((val / 255.0) - 0.5)
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
        # Parse into a friendly list of dicts
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
                        "id": ids[0][i] if ids and len(ids) > 0 and ids[0] is not None and len(ids[0]) > i else f"doc_{i}",
                        "document": doc_list[i],
                        "metadata": metadatas[0][i] if metadatas and len(metadatas) > 0 and metadatas[0] is not None and len(metadatas[0]) > i else {},
                        "distance": distances[0][i] if distances and len(distances) > 0 and distances[0] is not None and len(distances[0]) > i else None
                    })
        return parsed_results
    except Exception as e:
        logger.error(f"Error querying guidelines: {e}")
        return []

def seed_default_guidelines():
    import os
    import yaml

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rag_guidelines_dir = os.path.join(backend_dir, "data", "rag", "guidelines")
    old_file_path = os.path.join(backend_dir, "data", "dementia_care_guidelines.md")

    # Determine which path to seed from
    use_new_structure = os.path.exists(rag_guidelines_dir)

    if not use_new_structure and not os.path.exists(old_file_path):
        logger.error(f"Neither RAG guidelines directory ({rag_guidelines_dir}) nor old guidelines file ({old_file_path}) found.")
        return

    try:
        # Recreate the collection to clear out any old/stale documents
        client = get_chroma_client()
        try:
            client.delete_collection("dementia_guidelines")
            logger.info("Deleted existing ChromaDB collection 'dementia_guidelines' for re-seeding.")
        except Exception as e:
            logger.warning(f"Could not delete collection (might not exist yet): {e}")

        # Get fresh collection
        collection = get_collection()

        if use_new_structure:
            logger.info(f"Seeding guidelines from directory: {rag_guidelines_dir}")
            files = [f for f in os.listdir(rag_guidelines_dir) if f.endswith(".md")]
            if not files:
                logger.warning(f"No markdown files found in: {rag_guidelines_dir}")
                return

            for filename in sorted(files):
                file_path = os.path.join(rag_guidelines_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                frontmatter = {}
                body = content
                content_stripped = content.strip()
                if content_stripped.startswith("---"):
                    parts = content_stripped.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            frontmatter = yaml.safe_load(parts[1]) or {}
                        except Exception as e:
                            logger.warning(f"Failed to parse frontmatter in {filename}: {e}")
                        body = parts[2].strip()

                title = frontmatter.get("title", filename.replace(".md", "").replace("_", " ").title())
                category = frontmatter.get("category", "Dementia Care Protocol")

                # Prepare metadata (ensure all values are simple types required by ChromaDB)
                metadata = {
                    "source_file": filename,
                    "title": title,
                    "category": category,
                }

                # Map optional fields from frontmatter into metadata if present
                optional_fields = ["scenario", "risk_level", "audience", "requires_escalation_check"]
                for field in optional_fields:
                    if field in frontmatter:
                        val = frontmatter[field]
                        if isinstance(val, bool):
                            metadata[field] = val
                        else:
                            metadata[field] = str(val)

                # Handle scenario_triggers if present (convert list to comma-separated string)
                if "scenario_triggers" in frontmatter:
                    triggers = frontmatter["scenario_triggers"]
                    if isinstance(triggers, list):
                        metadata["scenario_triggers"] = ", ".join(triggers)
                    else:
                        metadata["scenario_triggers"] = str(triggers)

                # doc_id is the filename without extension
                doc_id = filename.replace(".md", "")

                collection.upsert(
                    ids=[doc_id],
                    documents=[body],
                    metadatas=[metadata]
                )
                logger.info(f"Ingested guideline: {title} ({category}) from {filename}")

            logger.info("Successfully seeded dementia care guidelines from multi-file RAG data.")
        else:
            logger.info(f"Seeding guidelines from old file path: {old_file_path}")
            with open(old_file_path, "r", encoding="utf-8") as f:
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
            logger.info("Successfully seeded dementia care guidelines from old markdown file.")
    except Exception as e:
        logger.error(f"Error seeding guidelines: {e}")
        raise e
