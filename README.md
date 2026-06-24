# Biomedical RAG Assistant for Regulatory Auditing

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Groq](https://img.shields.io/badge/LLM-Groq--Cloud-F55036?style=for-the-badge)](https://groq.com/)
[![AWS](https://img.shields.io/badge/AWS-Cloud--Infrastructure-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![AWS CDK](https://img.shields.io/badge/AWS--CDK-IaC-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/cdk/)

An enterprise-grade Retrieval-Augmented Generation (RAG) system engineered for automated compliance verification, regulatory auditing, and standards checking within the Biomedical Engineering domain. 

This production-ready architecture bridges the gap between complex regulatory frameworks (such as FDA guidances, INVIMA decrees, and clinical equipment manuals) and engineering operations by leveraging cross-lingual LLM orchestration, semantic vector indexing, and isolated microservices deployed seamlessly via Infrastructure as Code (IaC).

### Key Capabilities

* **Deterministic Knowledge Retrieval:** Implements an advanced splitting strategy using contextual-aware token text chunking alongside dense vector representations (`all-MiniLM-L6-v2`) to prevent LLM hallucinations on sensitive medical safety standards.
* **Dual-Language Adaptive Prompting:** Orchestrates dynamic system-level instructions supporting seamless real-time switching between English and Spanish, forcing the underlying LLM to enforce strict technical taxonomy based on the ingested documentation.
* **Cloud-Native Microservices Architecture:** Fully decoupled infrastructure utilizing a high-performance FastAPI asynchronous backend for processing vector retrieval queries, and an intuitive Streamlit frontend UI for auditor interactions.
* **Production-Grade DevSecOps & IaC:** Outfitted with an automated CI/CD pipeline using GitHub Actions to compile multi-stage Docker builds, backed by absolute configuration security utilizing programmatic AWS Secrets Manager ingestion and AWS CDK automated resource provisioning (ECS Fargate Serverless Cluster).

---

## Project Architecture

```text
CHATBOT-RAG/
├── .github/
│   └── workflows/
│       └── docker-ci.yml      # CI/CD Pipeline (Automated multi-container building & testing)
├── backend/                   # API Microservice Layer
│   ├── src/
│   │   ├── core/
│   │   │   └── rag_engine.py  # Biomedical RAG Engine & Embedding processing logic
│   │   ├── config.py          # Hierarchical configuration management (Pydantic Settings)
│   │   └── main.py            # FastAPI Application & REST API Endpoints
│   └── Dockerfile             # Production multi-stage Docker blueprint for Backend
├── frontend/                  # User Interface Microservice Layer
│   ├── app.py                 # Streamlit UI Application (Multi-language ES/EN support)
│   └── Dockerfile             # Production Docker blueprint for Frontend
├── infrastructure/            # Infrastructure as Code (IaC) Layer
│   ├── cdk_stack.py           # AWS CDK Construct definitions for ECS Fargate & Secrets Manager
│   ├── app.py                 # CDK Cloud Application entrypoint
│   └── cdk.json               # AWS Cloud Development Kit configuration blueprint
├── tests/                     # Automated Testing Suite (Pytest framework verification)
├── docker-compose.yml         # Local orchestration file for multi-container development
├── .env.example               # Public template for environment variables configuration
└── .gitignore                 # Exclusion configuration for local caches, venv, and data directories
```

---

## Local Development & Quick Start

Follow these steps to spin up the entire multi-container architecture locally for testing and development.

### Prerequisites

Before running the application, ensure you have the following installed and configured:
- **Docker Desktop** (with WSL2 backend enabled for Windows users).
- **Groq API Key** (Obtain your credentials via the [Groq Cloud Console](https://console.groq.com/)).

---

### Step-by-Step Setup

#### 1. Environment Configuration

Clone the public environment blueprint and instantiate your local configuration file:

```bash
# Copy the environment template
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

## Production-Grade Security & Configuration Hierarchy

The platform architecture implements a strict, hierarchical configuration layer powered by **Pydantic Settings**. This ensures decoupled environment management, strong type-safety, and absolute credential isolation across different pipeline execution stages, enforcing a clear variable precedence workflow:

1. **Production Infrastructure (AWS Secrets Manager & ECS Fargate):** In cloud deployment contexts, secrets are never hardcoded or baked into Docker images. Credentials like `GROQ_API_KEY` are provisioned programmatically via Infrastructure as Code (AWS CDK) and injected directly into the running container's memory space at the task definition level.
2. **Local Multi-Container Staging (`.env` Parsing via Docker Compose):** During local development and testing, configurations are resolved utilizing isolated environment files. Docker Compose orchestrates the injection of these variables securely into the backend container runtime without leaking host machine system details.
3. **OS-Level Environment Fallbacks (`os.environ` Precedence):** Used primarily during automated continuous integration pipelines (GitHub Actions) or bare-metal unit testing suites, allowing runtime configurations to be overridden dynamically by the host system runner.

> **Security Guarantee:** The `.env` file is explicitly blacklisted in `.gitignore`. The architecture is fully compliant with Twelve-Factor App methodologies, guaranteeing zero horizontal credential leakage across repository commits or production pipeline logs.

## System Demostration (Video Walkthrough)

Click on the image below to watch the full demonstration on Loom. In this video, I explain the cloud-native architecture, the FDA document ingestion process, and real-time semantic queries:

[![Biomedical RAG Assistant Demo](https://cdn.loom.com/sessions/thumbnails/04250c05b8884e3ba5cf3213829333a7-with-play.gif)](https://www.loom.com/share/04250c05b8884e3ba5cf3213829333a7)

*Note: The video showcases the production-ready integration between FastAPI, Streamlit UI, and semantic retrieval utilizing Llama 3.1 via Groq.*

## Author

Juan Sebastian Peña Valderrama, Biomedical Engineer and Software Developer.

## License

Distributed under the MIT License. See LICENSE for more information.
