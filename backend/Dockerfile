# --- Stage 1: Constructor / Builder ---
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Final Image ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 🚨 Inyección perfecta de la API Key desde el CDK
ARG GROQ_API_KEY
ENV GROQ_API_KEY=$GROQ_API_KEY

# Copia tu código fuente
COPY src/ /app/src/

# 🔥 EL CAMBIO SEGURO: Nos paramos dentro de src para el entorno de ejecución
WORKDIR /app/src

EXPOSE 8000

# Lanzamos la app directo llamando a main:app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]