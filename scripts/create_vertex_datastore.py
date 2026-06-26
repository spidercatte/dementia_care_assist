#!/usr/bin/env python3
"""
Creates a Vertex AI Search datastore and imports RAG guideline documents from GCS.
Called by deploy_vertex_search.sh — reads config from environment variables.
Safe to re-run: handles AlreadyExists gracefully and triggers a full re-import.
"""

import os
import sys
import time

from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import discoveryengine_v1 as discoveryengine

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
LOCATION = os.environ.get("VERTEX_SEARCH_LOCATION", "global")
DATASTORE_ID = os.environ.get("VERTEX_SEARCH_DATASTORE_ID", "dementia-care-guidelines")
GCS_BUCKET = os.environ["GCS_BUCKET"]
GCS_PREFIX = os.environ.get("GCS_PREFIX", "rag/guidelines")

COLLECTION = "default_collection"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}"
DATASTORE_NAME = f"{PARENT}/dataStores/{DATASTORE_ID}"
BRANCH = f"{DATASTORE_NAME}/branches/default_branch"


def create_datastore() -> None:
    client = discoveryengine.DataStoreServiceClient()

    datastore = discoveryengine.DataStore(
        display_name="Dementia Care Guidelines",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
    )

    try:
        operation = client.create_data_store(
            parent=PARENT,
            data_store=datastore,
            data_store_id=DATASTORE_ID,
        )
        print(f"    Creating datastore '{DATASTORE_ID}'...")
        result = operation.result(timeout=300)
        print(f"    Datastore created: {result.name}")
    except AlreadyExists:
        print(f"    Datastore '{DATASTORE_ID}' already exists, reusing.")


def import_documents() -> None:
    client = discoveryengine.DocumentServiceClient()

    gcs_uri = f"gs://{GCS_BUCKET}/{GCS_PREFIX}/*.txt"
    print(f"    Importing documents from: {gcs_uri}")

    request = discoveryengine.ImportDocumentsRequest(
        parent=BRANCH,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri],
            data_schema="content",
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )

    operation = client.import_documents(request=request)
    print(f"    Import operation started: {operation.operation.name}")
    print("    Waiting for import to complete (this may take a few minutes)...")

    result = operation.result(timeout=600)
    meta = operation.metadata

    success = getattr(meta, "success_count", "?")
    failure = getattr(meta, "failure_count", "?")
    print(f"    Import complete — success: {success}, failures: {failure}")

    if hasattr(result, "error_samples") and result.error_samples:
        print("    Import errors (sample):")
        for err in result.error_samples[:5]:
            print(f"      - {err}")


def main() -> None:
    print(f"  Project  : {PROJECT_ID}")
    print(f"  Location : {LOCATION}")
    print(f"  Datastore: {DATASTORE_ID}")
    print()

    create_datastore()
    import_documents()


if __name__ == "__main__":
    main()
