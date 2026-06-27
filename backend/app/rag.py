import logging
import os

import yaml

from common.rag import (
    GeminiEmbeddingFunction,
    get_chroma_client,
    get_collection,
    ingest_guideline,
    query_guidelines,
)

__all__ = [
    "GeminiEmbeddingFunction",
    "get_chroma_client",
    "get_collection",
    "ingest_guideline",
    "query_guidelines",
    "seed_default_guidelines",
]

logger = logging.getLogger("dementiacare-rag")

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def seed_default_guidelines():
    rag_guidelines_dir = os.path.join(_BACKEND_DIR, "data", "rag", "guidelines")
    old_file_path = os.path.join(_BACKEND_DIR, "data", "dementia_care_guidelines.md")

    use_new_structure = os.path.exists(rag_guidelines_dir)

    if not use_new_structure and not os.path.exists(old_file_path):
        logger.error(
            f"Neither RAG guidelines directory ({rag_guidelines_dir}) "
            f"nor old guidelines file ({old_file_path}) found."
        )
        return

    try:
        client = get_chroma_client()
        try:
            client.delete_collection("dementia_guidelines")
            logger.info("Deleted existing ChromaDB collection 'dementia_guidelines' for re-seeding.")
        except Exception as e:
            logger.warning(f"Could not delete collection (might not exist yet): {e}")

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

                metadata = {
                    "source_file": filename,
                    "title": title,
                    "category": category,
                }
                optional_fields = ["scenario", "risk_level", "audience", "requires_escalation_check"]
                for field in optional_fields:
                    if field in frontmatter:
                        val = frontmatter[field]
                        metadata[field] = val if isinstance(val, bool) else str(val)

                if "scenario_triggers" in frontmatter:
                    triggers = frontmatter["scenario_triggers"]
                    metadata["scenario_triggers"] = (
                        ", ".join(triggers) if isinstance(triggers, list) else str(triggers)
                    )

                doc_id = filename.replace(".md", "")
                collection.upsert(ids=[doc_id], documents=[body], metadatas=[metadata])
                logger.info(f"Ingested guideline: {title} ({category}) from {filename}")

            logger.info("Successfully seeded dementia care guidelines from multi-file RAG data.")
        else:
            logger.info(f"Seeding guidelines from old file path: {old_file_path}")
            with open(old_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            sections = content.split("##")[1:]
            for idx, sec in enumerate(sections):
                lines = sec.strip().split("\n")
                title = lines[0].strip()
                body = "\n".join(lines[1:]).strip()
                doc_id = (
                    title.lower()
                    .replace(" ", "_")
                    .replace("/", "_")
                    .replace("&", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                ingest_guideline(doc_id=doc_id, text=body, category="Dementia Care Protocol", title=title)

            logger.info("Successfully seeded dementia care guidelines from old markdown file.")
    except Exception as e:
        logger.error(f"Error seeding guidelines: {e}")
        raise e
