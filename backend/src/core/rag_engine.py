"""Módulo central del motor RAG utilizando Groq y Embeddings Locales.

Optimizado con sintaxis LCEL para máxima estabilidad de versiones.
"""

import os
from typing import Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_groq import ChatGroq                    
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config import settings


class BiomedicalRAGEngine:
    """Clase controladora para las operaciones RAG optimizadas con Groq."""

    def __init__(self) -> None:
        """Inicializa los componentes de IA gratuitos y la VectorDB."""
        # Embeddings gratis que corren localmente en tu PC
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Conexión persistente a ChromaDB
        self.vector_store = Chroma(
            persist_directory=settings.VECTOR_DB_DIR,
            embedding_function=self.embeddings,
            collection_name="biomedical_docs"
        )
        
        # Cargamos el LLM de Groq usando tu API key
        self.llm = ChatGroq(
            temperature=0.1,
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant"
        )
        
    def ingest_pdf(self, file_path: str) -> Dict[str, Any]:
        """Procesa, segmenta e ingresa un documento PDF en la base de datos vectorial."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        self.vector_store.add_documents(chunks)
        
        return {
            "status": "success",
            "filename": os.path.basename(file_path),
            "chunks_indexed": len(chunks)
        }

    def _format_docs(self, docs) -> str:
        """Une el contenido de los documentos recuperados en una sola cadena de texto."""
        return "\n\n".join(doc.page_content for doc in docs)

    def query(self, question: str) -> str:
        """Realiza una búsqueda de similitud y genera una respuesta fundamentada con Groq."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        system_prompt = (
            "Eres un asistente experto en auditoría de dispositivos médicos y regulaciones biomédicas.\n"
            "Usa los siguientes fragmentos de contexto recuperados para responder la pregunta.\n"
            "Si no sabes la respuesta o el contexto no la contiene, di claramente que no dispones "
            "de la información regulatoria oficial en tu base de datos. No intentes inventar.\n"
            "Responde SIEMPRE en español. Mantén un tono profesional, técnico y riguroso.\n\n"
            "Contexto:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}"),
        ])
        
        # --- PIPELINE LCEL DETERMINISTA ---
        # Definimos el flujo: Recuperar contexto -> Unirlo -> Pasar al Prompt -> LLM -> Parsear a String
        rag_chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Ejecución directa de la cadena secuencial
        return rag_chain.invoke(question)