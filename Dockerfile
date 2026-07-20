# Multi-stage Dockerfile for Cryptanium Platform
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    tar \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the scanner runtime self-contained and deterministic.
RUN pip install --no-cache-dir semgrep bandit pip-audit && \
    npm install --global eslint && \
    wget --tries=6 --waitretry=5 --timeout=30 --retry-on-http-error=429,500,502,503,504 \
      -O /tmp/gitleaks.tar.gz \
      "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz" && \
    test -s /tmp/gitleaks.tar.gz && \
    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks && \
    chmod 0755 /usr/local/bin/gitleaks && \
    rm -f /tmp/gitleaks.tar.gz && \
    gitleaks version

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
