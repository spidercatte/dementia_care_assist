import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    app_name: str = "DementiaCare Coach API"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Gemini API Settings
    gemini_api_key: str = ""
    
    # RAG / Database Settings
    chroma_db_path: str = "chroma_db"
    
    # CORS Settings
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
