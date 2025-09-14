# ---- Build stage ----
FROM python:3.11-slim AS build

# Dependencias del sistema necesarias para lxml
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libxml2-dev libxslt1-dev zlib1g-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos primero requirements.txt (mejora cacheo de capas)
COPY requirements.txt .

# Instalamos dependencias en carpeta temporal
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --target=/install -r requirements.txt

# ---- Final stage ----
FROM python:3.11-slim

# Dependencias mínimas en runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libxml2 libxslt1.1 zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Crear user no-root
RUN useradd --no-create-home appuser
WORKDIR /app

# Copiar dependencias desde build
COPY --from=build /install /usr/local

# Cambiar a appuser antes de copiar el código
USER appuser
WORKDIR /app

# Copiar código de la app (los archivos serán propiedad de appuser)
COPY --chown=appuser:appuser . /app

# Puerto expuesto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
