"""Automated tests for the application configuration layer."""

import sys
from pathlib import Path

# Resolve dynamic paths for the backend architecture
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend" / "src"))

import pytest  # noqa: E402

import config  # noqa: E402
from config import Settings  # noqa: E402


def test_settings_load_from_environment(monkeypatch):
    """Test that Settings correctly resolves GROQ_API_KEY from environment variables."""
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_environment_key_12345")

    test_settings = Settings()

    assert test_settings.PROJECT_NAME == "Biomedical RAG OPs"
    assert test_settings.GROQ_API_KEY == "gsk_test_environment_key_12345"


def test_settings_critical_failure_when_empty(monkeypatch):
    """Test that a ValueError is raised when no API key is found anywhere."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    monkeypatch.setattr(config, "DOCKER_SECRET_GROQ", Path("/nonexistent/path"))

    with pytest.raises(ValueError, match="Critical Failure"):
        Settings(GROQ_API_KEY="")
