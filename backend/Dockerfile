# --- Stage 1: Constructor / Builder ---
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# 🚨 Buscamos los archivos de configuración en la raíz del contexto global
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Final Image  ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 🚨 Copiamos explícitamente desde la subcarpeta backend/src hacia la imagen
COPY backend/src/ /app/src/

WORKDIR /app/src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]