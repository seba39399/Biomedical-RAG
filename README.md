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

### Prerequisites

- **Docker Desktop** (with WSL2 backend enabled for Windows users).
- **Groq API Key** (Get yours via the [Groq Cloud Console](https://console.groq.com/)).

### 1. Environment Setup

Clone the repository template and instantiate your local configuration file.

```bash
# Clone the template layout
cp .env.example .env
```

Open the newly created .env file and append your clean credentials:

GROQ_API_KEY=gsk_your_actual_groq_api_key_stream_here

Important Windows Encoding Note: Ensure your .env file is explicitly saved in UTF-8 plain text format. Avoid using basic PowerShell redirection methods like echo > .env as they enforce native UTF-16 LE with BOM encodings, which disrupt Linux container initialization routines.

### 2. Environment Setup

Boot up the full application stack using Docker Compose:

```bash
docker compose down
docker compose up -d --force-recreate
```

### 3. Verification & Live Monitoring

Track the live initialization process and weight downloading state of the RAG platform:

```bash
docker compose logs backend -f
```

Once the Uvicorn engine outputs state parameters successfully, navigate to the following ports on your host environment:

- Analytical Frontend (Streamlit): http://localhost:8501
- Core API Ecosystem (FastAPI Documentation): http://localhost:8000/docs

## Production-Grade Security Configuration

The platform architecture implements strict variable precedence handling inside config.py to prevent credential exposure in pipeline stages:

1. Docker Secrets Path (/run/secrets/groq_api_key): Checked first for infrastructure deployment setups.

2. Local Environment Context (.env parsing): Handled during container staging environments.

3. OS Level Environment Fallbacks (os.getenv): Used during bare-metal infrastructure testing.

## License

Distributed under the MIT License. See LICENSE for more information.
