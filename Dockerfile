# ---- Build stage ----
FROM python:3.11-slim AS build


# Dependencias del sistema necesarias para playwright + lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxkbcommon0 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libnspr4 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
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



# Crear el directorio de cache deseado
RUN mkdir -p /tmp/huggingface \
    && chmod -R 777 /tmp/huggingface

# Crear directorio para navegadores de playwright
RUN mkdir -p /tmp/ms-playwright \
    && chmod -R 777 /tmp/ms-playwright

# Establecer variables de entorno para que HuggingFace use /tmp/huggingface
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface/transformers
ENV HF_HUB_CACHE=/tmp/huggingface/hub
# opcionales si usas datasets, etc.
ENV HF_DATASETS_CACHE=/tmp/huggingface/datasets
ENV HF_ASSETS_CACHE=/tmp/huggingface/assets
ENV PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright




# Dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*


# Copiamos requirements
COPY requirements.txt .

# 🚀 Instalar dependencias en dos pasos (para aprovechar cache)
# Primero livianas
# RUN python -m pip install --upgrade pip \
#     && pip install --no-cache-dir uvicorn[standard] fastapi httpx lxml python-dotenv google-genai firecrawl requests langchain-ollama smolagents[tools] ddgs smolagents[litellm] markdownify playwright

# Después pesadas (si cambian estas, sí se tarda)
# RUN pip install --no-cache-dir sentence_transformers

# Instalamos dependencias globalmente
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Instalar chromium para playwright
RUN playwright install --with-deps chromium
RUN python -m playwright install chromium

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers>=4.41.0
RUN pip install --no-cache-dir "sentence-transformers[onnx]"


# ---- Final stage ----
FROM python:3.11-slim

# Dependencias mínimas runtime (incluyendo chromium headless)
# Dependencias del sistema necesarias para playwright + lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxkbcommon0 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libnspr4 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
 && rm -rf /var/lib/apt/lists/*



# Crear directorio cache en la imagen final
RUN mkdir -p /tmp/huggingface \
    && chmod -R 777 /tmp/huggingface

# Crear directorio para navegadores de playwright
RUN mkdir -p /tmp/ms-playwright \
    && chmod -R 777 /tmp/ms-playwright

# Establecer las mismas variables
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface/transformers
ENV HF_HUB_CACHE=/tmp/huggingface/hub
ENV HF_DATASETS_CACHE=/tmp/huggingface/datasets
ENV HF_ASSETS_CACHE=/tmp/huggingface/assets
ENV PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright


# Crear user no-root
RUN useradd --no-create-home appuser
WORKDIR /app

# Copiar dependencias ya instaladas
COPY --from=build /usr/local /usr/local
# COPY --from=build /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=build /tmp/ms-playwright /tmp/ms-playwright
RUN chown -R appuser:appuser /tmp/ms-playwright


# Cambiar a user
USER appuser
WORKDIR /app

# Copiar código
COPY --chown=appuser:appuser . /app



EXPOSE 8080
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
