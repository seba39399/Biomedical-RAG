# --- Stage 1: Constructor / Builder ---
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Sincronizar dependencias ignorando el modo desarrollo
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Imagen Final de Producción ---
FROM python:3.12-alpine

WORKDIR /app

# Copiar el entorno virtual construido en el Stage 1
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código fuente del backend
COPY src/ /app/src/

WORKDIR /app/src

EXPOSE 8000

# Comando de arranque optimizado para contenedores (sin --reload en producción)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]