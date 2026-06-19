"""Automated tests for the application configuration layer."""

import os
import sys
from pathlib import Path

# Forzar de forma absoluta la inyección de 'backend/src' en el path del sistema
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend" / "src"))

import pytest
# Ahora importamos directamente el módulo config que está dentro de src
import config
from config import Settings


def test_settings_load_from_environment(monkeypatch):
    """Test that Settings correctly resolves GROQ_API_KEY from environment variables."""
    # Mock system environment variable
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_environment_key_12345")
    
    # Force re-instantiation to test logic
    test_settings = Settings()
    
    assert test_settings.PROJECT_NAME == "Biomedical RAG OPs"
    assert test_settings.GROQ_API_KEY == "gsk_test_environment_key_12345"


def test_settings_critical_failure_when_empty(monkeypatch):
    """Test that a ValueError is raised when no API key is found anywhere."""
    # Ensure environment is clean
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    # Mock Docker Secret path to a non-existent file
    monkeypatch.setattr(config, "DOCKER_SECRET_GROQ", Path("/nonexistent/path"))
    
    # Pydantic validation should fail inside our field_validator
    with pytest.raises(ValueError, match="Critical Failure"):
        Settings(GROQ_API_KEY="")