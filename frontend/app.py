"""Aplicación Frontend de Streamlit para el portafolio de Ingeniería Biomédica.

Proporciona una interfaz gráfica limpia para cargar documentos regulatorios
y sostener un chat interactivo con el sistema RAG mediante peticiones HTTP a FastAPI.
"""

import os
import streamlit as st
import requests

# Configuración de URL del backend leyendo variables del entorno de Docker
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Biomedical RAG Asisstant",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Asistente RAG para Auditoría y Regulación Biomédica")
st.caption("Fusión de Ingeniería Biomédica y MLOps para la verificación automatizada de estándares (FDA / INVIMA).")

# --- BARRA LATERAL: Control de Infraestructura e Ingesta ---
with st.sidebar:
    st.header("⚙️ Gestión de Infraestructura")
    st.subheader("Subir Documentación Oficial")
    uploaded_file = st.file_uploader("Cargar guías o leyes en formato PDF", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("🚀 Ingestar en VectorDB"):
            with st.spinner("Procesando embeddings e indexando en Chroma..."):
                # Preparamos el archivo para enviarlo vía multipart/form-data
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"¡Éxito! Indexados {data['chunks_indexed']} fragmentos de '{data['filename']}'.")
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail')}")
                except requests.exceptions.ConnectionError:
                    st.error("No se pudo conectar con el servicio Backend de FastAPI.")

    st.markdown("---")
    st.markdown("### Stack Tecnológico Desplegado:")
    st.info("**Backend:** FastAPI\n\n**Frontend:** Streamlit\n\n**VectorStore:** ChromaDB\n\n**Orquestación:** LangChain / `uv` Environment")

# --- PANEL CENTRAL: Chatbot con Historial de Sesión ---
# Inicialización limpia del estado de memoria del chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizado de los mensajes históricos guardados en memoria de Streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura de la nueva interacción del usuario
if user_question := st.chat_input("Pregúntame sobre los requisitos de un dispositivo médico o normativas específicas..."):
    # Mostramos la pregunta de inmediato en pantalla
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Petición HTTP POST hacia el backend asíncrono
    with st.chat_message("assistant"):
        with st.spinner("Analizando concordancia regulatoria en el espacio latente..."):
            try:
                payload = {"question": user_question}
                response = requests.post(f"{BACKEND_URL}/query", json=payload)
                
                if response.status_code == 200:
                    assistant_answer = response.json()["answer"]
                    st.markdown(assistant_answer)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_answer})
                else:
                    error_msg = f"Error en procesamiento API: {response.json().get('detail')}"
                    st.error(error_msg)
            except requests.exceptions.ConnectionError:
                st.error("Error de conexión. Asegúrate de que el contenedor de FastAPI esté corriendo.")