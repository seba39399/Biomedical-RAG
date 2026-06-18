# --- Stage 1: Constructor / Builder ---
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copiar archivos de configuración compartidos desde la raíz
COPY pyproject.toml uv.lock ./

# Sincronizar dependencias ignorando el modo desarrollo
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Imagen Final ---
FROM python:3.12-alpine

WORKDIR /app

# Copiar el entorno virtual empaquetado en el Stage 1
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el script de la interfaz desde la carpeta frontend/ del repositorio
COPY frontend/app.py /app/app.py

EXPOSE 8501

# Configuración de Streamlit optimizada para contenedores
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]