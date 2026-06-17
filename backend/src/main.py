"""Punto de entrada principal para la API REST de FastAPI.

Expone los servicios de ingesta de documentos y consulta del chatbot RAG,
manejando la persistencia temporal de archivos y las excepciones del sistema.
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from core.rag_engine import BiomedicalRAGEngine
from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para el análisis automatizado de normativas y cumplimiento biomédico."
)

# Inicialización única del motor RAG (Singleton conceptual en runtime)
rag_engine = BiomedicalRAGEngine()


class QueryRequest(BaseModel):
    """Esquema de validación de entrada para las consultas al chatbot."""
    question: str


class QueryResponse(BaseModel):
    """Esquema de validación de salida para las respuestas del chatbot."""
    answer: str


@app.get("/")
def read_root():
    """Endpoint de verificación de salud del sistema (Health Check)."""
    return {"status": "online", "application": settings.PROJECT_NAME}


@app.post(f"{settings.API_V1_STR}/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Endpoint asíncrono para cargar y procesar regulaciones en PDF.
    
    Raises:
        HTTPException: Si el archivo cargado no cumple con el formato PDF.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Estructura de archivo inválida. Solo se admiten PDFs.")
    
    # Creamos un directorio temporal seguro para procesar el archivo
    temp_dir = "/tmp/biomedical_ingest"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Guardamos el archivo binario en el disco temporal
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ejecutamos el pipeline de extracción e indexación
        result = rag_engine.ingest_pdf(temp_file_path)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo crítico en el pipeline MLOps: {str(e)}")
        
    finally:
        # Eliminación estricta del residuo de archivo para optimizar almacenamiento del contenedor
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post(f"{settings.API_V1_STR}/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Endpoint asíncrono para interactuar con el chatbot RAG."""
    try:
        answer = rag_engine.query(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en inferencia del LLM: {str(e)}")