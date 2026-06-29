import os
import shutil
import tempfile
import pytest
from common.config import settings

@pytest.fixture(scope="session", autouse=True)
def temp_chroma_db():
    # Create a temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp(prefix="chroma_test_")
    original_path = settings.chroma_db_path
    settings.chroma_db_path = temp_dir

    yield temp_dir

    # Restore original path and clean up
    settings.chroma_db_path = original_path
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass
