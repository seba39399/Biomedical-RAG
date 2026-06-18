"""Aplicación Frontend de Streamlit para el portafolio de Ingeniería Biomédica.

Soporta internacionalización (Español / Inglés) de toda la interfaz gráfica,
incluyendo gestión de infraestructura, stack tecnológico y limpieza de historial.
"""

import os
import streamlit as st
import requests

# Configuración de URL del backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Biomedical RAG Assistant",
    page_icon="🧬",
    layout="wide"
)

# --- TRADUCCIÓN COMPLETA DE LA INTERFAZ (i18n) ---
I18N = {
    "ES": {
        "title": "🧬 Asistente RAG para Auditoría y Regulación Biomédica",
        "caption": "Fusión de Ingeniería Biomédica y MLOps para la verificación automatizada de estándares regulatorios.",
        "sidebar_lang_header": "🌐 Idioma / Language",
        "sidebar_lang_label": "Seleccione el Idioma de la Interfaz",
        "btn_clear": "🗑️ Limpiar Historial de Chat",
        "sidebar_header": "⚙️ Gestión de Infraestructura",
        "sidebar_subheader": "Subir Documentación Oficial",
        "file_uploader_label": "Cargar guías o leyes en formato PDF",
        "btn_ingest": "🚀 Ingestar en VectorDB",
        "spinner_ingest": "Procesando embeddings e indexando en Chroma...",
        "success_ingest": "¡Éxito! Indexados {} fragmentos de '{}'.",
        "chat_input_placeholder": "Pregúntame sobre los requisitos de un dispositivo médico o normativas específicas...",
        "spinner_query": "Analizando concordancia regulatoria en el espacio latente...",
        "error_conn": "No se pudo conectar con el servicio Backend de FastAPI.",
        "stack_title": "💻 Stack Tecnológico Desplegado:",
        "stack_backend": "**Backend:** FastAPI (Python)",
        "stack_frontend": "**Frontend:** Streamlit UI",
        "stack_vector": "📂 **VectorStore:** ChromaDB",
        "stack_orchestration": "🛠️ **Orquestación:** LangChain / uv Environment",
        "stack_infra": "⚡ **Infraestructura LLM:** Groq LPU Cloud"
    },
    "EN": {
        "title": "🧬 Biomedical RAG Assistant for Regulatory Auditing",
        "caption": "Fusion of Biomedical Engineering and MLOps for automated verification of regulatory standards.",
        "sidebar_lang_header": "🌐 Language / Idioma",
        "sidebar_lang_label": "Select Interface Language",
        "btn_clear": "🗑️ Clear Chat History",
        "sidebar_header": "⚙️ Infrastructure Management",
        "sidebar_subheader": "Upload Official Documentation",
        "file_uploader_label": "Upload guidelines or regulations in PDF format",
        "btn_ingest": "🚀 Ingest into VectorDB",
        "spinner_ingest": "Processing embeddings and indexing into Chroma...",
        "success_ingest": "Success! Indexed {} chunks from '{}'.",
        "chat_input_placeholder": "Ask me about medical device requirements or specific regulations...",
        "spinner_query": "Analyzing regulatory compliance in latent space...",
        "error_conn": "Could not connect to the FastAPI Backend service.",
        "stack_title": "💻 Deployed Technological Stack:",
        "stack_backend": "**Backend:** FastAPI (Python)",
        "stack_frontend": "**Frontend:** Streamlit UI",
        "stack_vector": "📂 **VectorStore:** ChromaDB",
        "stack_orchestration": "🛠️ **Orchestration:** LangChain / uv Environment",
        "stack_infra": "⚡ **LLM Infrastructure:** Groq LPU Cloud"
    }
}

# --- BARRA LATERAL: Selector de idioma y control de la App ---
with st.sidebar:
    # 1. Inicializar la variable en la sesión si no existe
    if "lang" not in st.session_state:
        st.session_state.lang = "ES"

    # Determinar el índice actual para que el componente visual no se reinicie
    current_index = 0 if st.session_state.lang == "ES" else 1

    st.header(I18N["ES"]["sidebar_lang_header"] if st.session_state.lang == "ES" else I18N["EN"]["sidebar_lang_header"])
    
    # 2. El selectbox ahora mantiene el estado real usando 'key' e 'index' sincronizados
    lang = st.selectbox(
        I18N["ES"]["sidebar_lang_label"] if st.session_state.lang == "ES" else I18N["EN"]["sidebar_lang_label"], 
        ["ES", "EN"], 
        index=current_index,
        key="lang_selector"
    )
    
    # Actualizar la sesión con el cambio del usuario
    st.session_state.lang = lang
    
    # Asignamos los textos del diccionario activo
    text = I18N[st.session_state.lang]
    
    # --- BOTÓN PARA LIMPIAR CHAT INTEGRADO ---
    st.markdown(" ")
    if st.button(text["btn_clear"], use_container_width=True):
        st.session_state.messages = []  # Vaciamos el historial de mensajes
        st.rerun()                      # Forzamos el rediseño inmediato de la UI limpia
        
    st.markdown("---")
    st.header(text["sidebar_header"])
    st.subheader(text["sidebar_subheader"])
    uploaded_file = st.file_uploader(text["file_uploader_label"], type=["pdf"])
    
    if uploaded_file is not None:
        if st.button(text["btn_ingest"]):
            with st.spinner(text["spinner_ingest"]):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(text["success_ingest"].format(data['chunks_indexed'], data['filename']))
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.exceptions.ConnectionError:
                    st.error(text["error_conn"])

    st.markdown("---")
    st.markdown(f"### {text['stack_title']}")
    st.info(f"{text['stack_backend']}\n\n{text['stack_frontend']}\n\n{text['stack_vector']}\n\n{text['stack_orchestration']}\n\n{text['stack_infra']}")

# --- PANEL CENTRAL DE CONVERSACIÓN ---
st.title(text["title"])
st.caption(text["caption"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Dibujar el historial en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto del chat
if user_question := st.chat_input(text["chat_input_placeholder"]):
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("assistant"):
        with st.spinner(text["spinner_query"]):
            try:
                # OJO AQUÍ: Enviamos explícitamente el idioma guardado en la sesión
                payload = {"question": user_question, "language": st.session_state.lang}
                response = requests.post(f"{BACKEND_URL}/query", json=payload)
                
                if response.status_code == 200:
                    assistant_answer = response.json()["answer"]
                    st.markdown(assistant_answer)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_answer})
                else:
                    st.error(f"API Error: {response.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error(text["error_conn"])