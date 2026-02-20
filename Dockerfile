# ============================================================
# TenderAI Production Dockerfile (Multi-stage build)
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Final stage — minimal image
# ============================================================
FROM python:3.12-slim

WORKDIR /app

# Curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Python packages from builder
COPY --from=builder /install /usr/local

# Uygulama dosyaları
COPY . .

# Config
COPY .streamlit/config.toml .streamlit/config.toml

# Dizinler
RUN mkdir -p logs data/uploads data/reports

# Non-root user
RUN useradd -m -u 1000 tenderai && chown -R tenderai:tenderai /app
USER tenderai

# Port
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD curl -sf http://localhost:8501/_stcore/health || exit 1

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Başlat
CMD ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
