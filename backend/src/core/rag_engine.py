"""Módulo central del motor RAG utilizando Groq y Embeddings Locales."""

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
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vector_store = Chroma(
            persist_directory=settings.VECTOR_DB_DIR,
            embedding_function=self.embeddings,
            collection_name="biomedical_docs"
        )
        
        # El modelo vigente y ultra rápido de Groq
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

    def query(self, question: str, language: str = "ES") -> str:
        """Realiza una búsqueda de similitud y genera una respuesta fundamentada con Groq.
        
        Soporta respuestas adaptativas según el idioma seleccionado de la UI.
        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        # Prompt del sistema dinámico según el idioma seleccionado en la interfaz
        if language == "ES":
            system_prompt = (
                "Eres un asistente experto en auditoría de dispositivos médicos y regulaciones biomédicas.\n"
                "Usa los siguientes fragmentos de contexto recuperados para responder la pregunta.\n"
                "Si no sabes la respuesta o el contexto no la contiene, di claramente que no dispones "
                "de la información regulatoria oficial en tu base de datos. No intentes inventar.\n"
                "Responde SIEMPRE en ESPAÑOL. Mantén un tono profesional, técnico y riguroso.\n\n"
                "Contexto:\n{context}"
            )
        else:
            system_prompt = (
                "You are an expert assistant in medical device auditing and biomedical regulations.\n"
                "Use the following retrieved context fragments to answer the question.\n"
                "If you do not know the answer or the context does not contain it, clearly state that "
                "you do not have the official regulatory information in your database. Do not try to invent.\n"
                "ALWAYS answer in ENGLISH. Maintain a professional, technical, and rigorous tone.\n\n"
                "Context:\n{context}"
            )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}"),
        ])
        
        # Pipeline LCEL determinista
        rag_chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain.invoke(question)