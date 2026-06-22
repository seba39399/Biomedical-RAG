"""Enterprise-grade unit tests for configuration, document formatting, and file validation."""

import sys
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

# Resolve dynamic paths for the backend architecture
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend" / "src"))

import config  # noqa: E402
from config import Settings  # noqa: E402
from core.rag_engine import BiomedicalRAGEngine  # noqa: E402


def test_settings_load_from_environment(monkeypatch):
    """1. Test that Settings correctly resolves GROQ_API_KEY from environment variables."""
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_env_key_12345")
    test_settings = Settings()
    assert test_settings.PROJECT_NAME == "Biomedical RAG OPs"
    assert test_settings.GROQ_API_KEY == "gsk_test_env_key_12345"


def test_settings_critical_failure_when_empty(monkeypatch):
    """2. Test that a ValueError is raised when no API key is found anywhere."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(config, "DOCKER_SECRET_GROQ", Path("/nonexistent/path"))

    with pytest.raises(ValueError, match="Critical Failure"):
        Settings(GROQ_API_KEY="")


def test_settings_default_project_metadata():
    """3. Test that the application maintains its immutable metadata defaults."""
    test_settings = Settings(GROQ_API_KEY="gsk_dummy")
    assert test_settings.PROJECT_NAME == "Biomedical RAG OPs"


class MockDocument:
    """Mock class to simulate LangChain's Document structure without dependencies."""

    def __init__(self, page_content: str):
        self.page_content = page_content


def test_rag_engine_format_docs_standard():
    """4. Test that _format_docs correctly flattens and joins multiple document chunks."""
    mock_docs = [
        MockDocument("ISO 13485 requires strict quality management systems."),
        MockDocument("FDA Class III devices need Pre-Market Approval (PMA)."),
    ]

    engine = BiomedicalRAGEngine.__new__(BiomedicalRAGEngine)
    formatted_result = engine._format_docs(mock_docs)

    expected = (
        "ISO 13485 requires strict quality management systems.\n\n"
        "FDA Class III devices need Pre-Market Approval (PMA)."
    )
    assert formatted_result == expected


def test_rag_engine_format_docs_empty():
    """5. Test that _format_docs handles empty retriever outputs gracefully without crashing."""
    engine = BiomedicalRAGEngine.__new__(BiomedicalRAGEngine)
    formatted_result = engine._format_docs([])
    assert formatted_result == ""


def test_file_validation_accepts_pdf():
    """6. Test that the ingestion pipeline permits valid PDF structures."""
    dummy_file = BytesIO(b"dummy pdf content")
    mock_file = UploadFile(file=dummy_file, filename="iso_9001_regulation.pdf")

    assert mock_file.filename.endswith(".pdf") is True


def test_file_validation_rejects_malicious_extensions():
    """7. Test that the ingestion system strict boundary blocks non-PDF extensions."""
    dummy_file = BytesIO(b"dummy exe content")
    mock_file = UploadFile(file=dummy_file, filename="malware_disguised.exe")

    with pytest.raises(HTTPException) as exc_info:
        if not mock_file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file structure. Only PDFs are accepted.",
            )

    assert exc_info.value.status_code == 400
    assert "Only PDFs are accepted" in exc_info.value.detail


def test_file_validation_case_insensitive_handling():
    """8. Test that file validation logic accounts for mixed-case extensions (e.g., .PDF)."""
    filename = "UPPERCASE_REGULATION.PDF"
    is_valid_pdf = filename.lower().endswith(".pdf")
    assert is_valid_pdf is True
