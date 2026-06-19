# Biomedical RAG Assistant for Regulatory Auditing

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Groq](https://img.shields.io/badge/LLM-Groq--Cloud-F55036?style=for-the-badge)](https://groq.com/)

An enterprise-grade Retrieval-Augmented Generation (RAG) system engineered for automated compliance verification, regulatory auditing, and standards checking within the Biomedical Engineering domain.

---

## Key Features

- **Biomedical Context Awareness:** Seamless ingestion and vector indexing of complex medical standards and auditing documentation.
- **Hybrid Configuration Management:** Production-ready Pydantic Settings layer supporting multi-source resolution (Docker Secrets, `.env` files, and local system environment fallbacks).
- **Decoupled Architecture:** Microservices-based ecosystem separating the high-performance FastAPI backend from the intuitive Streamlit analytical frontend.
- **Deterministic Isolation:** Containerized environment leveraging Docker Network security and cross-platform compatibility (WSL2 / Linux).

---

## Project Architecture

```text
chatbot-rag/
├── src/
│   ├── config.py          # Hierarchical configuration layer (Pydantic Settings)
│   ├── main.py            # FastAPI Application & Endpoints core entrypoint
│   └── core/
│       └── rag_engine.py  # Biomedical RAG Engine & Embedding processing
├── .env.example           # Public deployment environment blueprint
├── docker-compose.yml     # Multi-container multi-service orchestrator
└── pyproject.toml         # Dependency lock definition file
```

---

## Local Development & Quick Start
