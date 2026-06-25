import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    app_name: str = "DementiaCare Coach API"
    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini API Settings
    gemini_api_key: str = ""

    # Security Keys
    admin_api_key: str = ""
    user_api_key: str = ""

    # RAG / Database Settings
    chroma_db_path: str = "chroma_db"
    chroma_server_host: str = ""
    chroma_server_port: int = 8000
    db_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dementia_care.db")
    database_url: str = ""
    db_user: str = ""
    db_password: str = ""
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    backend_public_url: str = "http://localhost:8000"

    # CORS Settings
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
