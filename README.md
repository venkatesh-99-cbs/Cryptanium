# Cryptanium

> **Forging Trust. Securing Code.**

Cryptanium is an AI-powered Repository Trust & Security Analysis Platform that scans GitHub repositories using multiple SAST, secret, and dependency scanners, calculates a transparent **Repository Trust Score**, and generates executive AI summaries and prioritized remediation guidance before deployment.

---

## Key Features

- **Automated Multi-Tool Security Scanning**: Integrates Semgrep, Bandit, Gitleaks, pip-audit, npm audit, and ESLint.
- **Repository Trust Score Engine**: Pluggable Strategy pattern calculating objective security trust scores $[0, 100]$ with risk classifications (`Excellent`, `Good`, `Moderate`, `Risky`, `Critical`).
- **Zero-Hallucination AI Summaries & Remediation**: Powered by OpenRouter and Nemotron Flash (`nvidia/nemotron-4-340b-instruct`) with deterministic offline rule fallbacks.
- **Publication-Ready PDF Audit Reports**: Dynamic ReportLab Platypus reports with OWASP mappings, breakdown tables, and two-pass page numbering.
- **Clean Architecture & RESTful API**: Built with FastAPI, Pydantic v2, SQLAlchemy ORM, and React + TypeScript + Vite.
- **Docker & Cloud Deployment**: Full Docker Compose setup and Render deployment readiness.

---

## Quickstart

### 1. Clone & Setup Environment
```bash
git clone https://github.com/venkatesh-99-cbs/Cryptanium.git
cd Cryptanium
cp .env.example .env
```

### 2. Run Locally with Docker
```bash
docker compose up --build -d
```
- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

### 3. Run Backend Without Docker
```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open browser at `http://localhost:3000`.

---

## Documentation Links

- 📖 [REST API Documentation](docs/API.md)
- 📐 [Architecture Specification](docs/ARCHITECTURE.md)
- 🚀 [Presentation & Pitch Guide](docs/PRESENTATION.md)
- 👤 [User & Operator Guide](docs/USER_GUIDE.md)
- 🛠️ [Developer & Contributor Guide](docs/DEVELOPER_GUIDE.md)

---

## License
MIT License - see `LICENSE` for details.
