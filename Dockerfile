# ---- Build stage ----
FROM python:3.11-slim AS build

# Dependencias del sistema necesarias para playwright + lxml
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        ca-certificates \
        wget \
        curl \
        fonts-liberation \
        libasound2 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libglib2.0-0 \
        libnspr4 \
        libnss3 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements
COPY requirements.txt .

# 🚀 Instalar dependencias en dos pasos (para aprovechar cache)
# Primero livianas
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir uvicorn[standard] fastapi httpx lxml python-dotenv google-genai firecrawl requests langchain-ollama smolagents[tools] ddgs smolagents[litellm] markdownify playwright

# Después pesadas (si cambian estas, sí se tarda)
RUN pip install --no-cache-dir sentence_transformers

# Instalar chromium para playwright
RUN python -m playwright install chromium

# ---- Final stage ----
FROM python:3.11-slim

# Dependencias mínimas runtime (incluyendo chromium headless)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        curl \
        fonts-liberation \
        libasound2 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libglib2.0-0 \
        libnspr4 \
        libnss3 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Crear user no-root
RUN useradd --no-create-home appuser
WORKDIR /app

# Copiar dependencias ya instaladas
COPY --from=build /usr/local /usr/local
COPY --from=build /root/.cache/ms-playwright /root/.cache/ms-playwright

# Cambiar a user
USER appuser
WORKDIR /app

# Copiar código
COPY --chown=appuser:appuser . /app

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
