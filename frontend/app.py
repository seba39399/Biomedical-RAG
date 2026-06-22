"""Streamlit frontend application for the Biomedical Engineering RAG.

Supports internationalization (Spanish/English) of the entire graphical interface,
including infrastructure management, the technology stack, and history cleanup.
"""

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Biomedical RAG Assistant", page_icon="🧬", layout="wide")

# --- UI translated (i18n) ---
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
        "stack_infra": "⚡ **Infraestructura LLM:** Groq LPU Cloud",
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
        "stack_infra": "⚡ **LLM Infrastructure:** Groq LPU Cloud",
    },
}

# --- SIDEBAR ---
with st.sidebar:
    if "lang" not in st.session_state:
        st.session_state.lang = "ES"

    current_index = 0 if st.session_state.lang == "ES" else 1

    st.header(
        I18N["ES"]["sidebar_lang_header"]
        if st.session_state.lang == "ES"
        else I18N["EN"]["sidebar_lang_header"]
    )

    lang = st.selectbox(
        I18N["ES"]["sidebar_lang_label"]
        if st.session_state.lang == "ES"
        else I18N["EN"]["sidebar_lang_label"],
        ["ES", "EN"],
        index=current_index,
        key="lang_selector",
    )

    st.session_state.lang = lang

    text = I18N[st.session_state.lang]

    # --- CLEAN CHAT ---
    st.markdown(" ")
    if st.button(text["btn_clear"], use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.header(text["sidebar_header"])
    st.subheader(text["sidebar_subheader"])
    uploaded_file = st.file_uploader(text["file_uploader_label"], type=["pdf"])

    if uploaded_file is not None:
        if st.button(text["btn_ingest"]):
            with st.spinner(text["spinner_ingest"]):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/api/v1/ingest", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(
                            text["success_ingest"].format(
                                data["chunks_indexed"], data["filename"]
                            )
                        )
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except requests.exceptions.ConnectionError:
                    st.error(text["error_conn"])

    st.markdown("---")
    st.markdown(f"### {text['stack_title']}")
    st.info(
        f"{text['stack_backend']}\n\n{text['stack_frontend']}\n\n{text['stack_vector']}\n\n{text['stack_orchestration']}\n\n{text['stack_infra']}"
    )

# --- MAIN PANEL ---
st.title(text["title"])
st.caption(text["caption"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_question := st.chat_input(text["chat_input_placeholder"]):
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("assistant"):
        with st.spinner(text["spinner_query"]):
            try:
                payload = {"question": user_question, "language": st.session_state.lang}
                response = requests.post(f"{BACKEND_URL}/api/v1/query", json=payload)

                if response.status_code == 200:
                    assistant_answer = response.json()["answer"]
                    st.markdown(assistant_answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_answer}
                    )
                else:
                    st.error(f"API Error: {response.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error(text["error_conn"])
