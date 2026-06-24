"""Global application configuration module using Pydantic Settings."""

import json
import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Standard Docker Secrets path exposed as a clean constant
DOCKER_SECRET_GROQ = Path("/run/secrets/groq_api_key")


class Settings(BaseSettings):
    """Container class for validated environment variables and secrets."""

    PROJECT_NAME: str = "Biomedical RAG OPs"
    API_V1_STR: str = "/api/v1"

    # Initialized as empty to prevent initial Pydantic parsing errors
    GROQ_API_KEY: str = ""
    VECTOR_DB_DIR: str = "./chroma_db_local"
    LOG_LEVEL: str = "INFO"

    @field_validator("GROQ_API_KEY", mode="before")
    @classmethod
    def load_and_validate_api_key(cls, value: str) -> str:
        """Hierarchically resolves and validates the source of GROQ_API_KEY.

        Load Priority:
        1. Docker Secrets (Production / Secure container deployment)
        2. AWS Secrets Manager (Injected JSON object in system environment)
        3. Injected parameter / .env file (Local development with Compose)
        4. System environment variable (os.environ fallback string plano)
        """
        # 1. Try loading from Docker Secrets
        if DOCKER_SECRET_GROQ.is_file():
            secret_value = DOCKER_SECRET_GROQ.read_text(encoding="utf-8").strip()
            if secret_value:
                return secret_value

        # Capturar el entorno del sistema para verificar inyecciones de AWS
        env_value = os.getenv("GROQ_API_KEY", "").strip()

        # 2. Si la variable empieza con '{', es el JSON stringificado de AWS
        if env_value.startswith("{"):
            try:
                secret_json = json.loads(env_value)
                if "GROQ_API_KEY" in secret_json:
                    return secret_json["GROQ_API_KEY"].strip()
            except Exception:
                pass  # Si el JSON está mal formado, continúa con los fallbacks

        # 3. Check if a clean value was passed via Pydantic init or .env file
        if value and value.strip():
            return value.strip()

        # 4. Direct fallback to system environment variables (String plano tradicional)
        if env_value and not env_value.startswith("{"):
            return env_value

        # Raise a clean exception if no key is provided by any source
        raise ValueError(
            "Critical Failure: GROQ_API_KEY was not found in any of the configured sources "
            "(Docker Secrets, AWS JSON Secrets, .env file, or system environment variables)."
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Global instance ready to be imported across the ecosystem (main.py, rag_engine.py, etc.)
settings = Settings()