# --- Stage 1: Constructor / Builder ---
FROM python:3.12-slim AS builder

# Instalar uv de forma nativa e independiente
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copiar archivos de configuración compartidos
COPY pyproject.toml uv.lock ./

# Sincronizar dependencias usando el binario de uv instalado
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Imagen Final de Producción ---
FROM python:3.12-slim

WORKDIR /app

# Copiar el entorno virtual empaquetado en el Stage 1
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código fuente desde el contexto raíz
COPY backend/src/ /app/src/

WORKDIR /app/src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]