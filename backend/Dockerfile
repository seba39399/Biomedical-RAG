# --- Stage 1: Constructor / Builder ---
# Cambiamos alpine por debian-slim
FROM ghcr.io/astral-sh/uv:python3.12-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copiar configuración de dependencias
COPY pyproject.toml uv.lock ./

# Sincronizar dependencias ignorando el modo desarrollo
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Imagen Final de Producción ---
# Cambiamos alpine por slim para compatibilidad con binarios como onnxruntime
FROM python:3.12-slim

WORKDIR /app

# Copiar el entorno virtual construido
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código fuente del backend
COPY backend/src/ /app/src/

WORKDIR /app/src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]