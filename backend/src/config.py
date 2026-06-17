"""Módulo de configuración global de la aplicación utilizando Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Clase contenedora de las variables de entorno validadas."""
    PROJECT_NAME: str = "Biomedical RAG OPs"
    API_V1_STR: str = "/api/v1"
    
    # Infraestructura y APIs (Cambiado a Groq)
    GROQ_API_KEY: str
    VECTOR_DB_DIR: str = "./chroma_db_local"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )


settings = Settings()