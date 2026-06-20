"""Main entry point for the FastAPI REST API.

It exposes the document ingestion and query services of the RAG chatbot,
handling temporary file persistence and system exceptions.
"""

import os
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from config import settings
from core.rag_engine import BiomedicalRAGEngine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API for the automated analysis of regulations and biomedical compliance.",
)

rag_engine = BiomedicalRAGEngine()


class QueryRequest(BaseModel):
    """Schema for validating input queries to the chatbot."""

    question: str
    language: str = "ES"


class QueryResponse(BaseModel):
    """Schema for validating output responses from the chatbot."""

    answer: str


@app.get("/")
def read_root():
    """Endpoint for system health check."""
    return {"status": "online", "application": settings.PROJECT_NAME}


@app.post(f"{settings.API_V1_STR}/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Asynchronous endpoint for uploading and processing PDF regulations.

    Raises:
        HTTPException: If the uploaded file does not comply with the PDF format.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file structure. Only PDFs are accepted."
        )

    temp_dir = "/tmp/biomedical_ingest"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = rag_engine.ingest_pdf(temp_file_path)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Critical failure in the MLOps pipeline: {str(e)}"
        )

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post(f"{settings.API_V1_STR}/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Asynchronous endpoint for interacting with the RAG engine."""
    try:
        answer = rag_engine.query(request.question, request.language)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in LLM inference: {str(e)}")
