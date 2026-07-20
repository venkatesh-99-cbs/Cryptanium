# Multi-stage Dockerfile for Cryptanium Platform
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the scanner runtime self-contained and deterministic.
RUN pip install --no-cache-dir semgrep bandit pip-audit && \
    npm install --global eslint && \
    curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_8.24.2_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
