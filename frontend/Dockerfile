# --- Stage 1: Constructor / Builder ---
FROM python:3.12-slim AS builder

# Instalar uv de forma nativa e independiente
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Imagen Final ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el script de la interfaz
COPY frontend/app.py /app/app.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]