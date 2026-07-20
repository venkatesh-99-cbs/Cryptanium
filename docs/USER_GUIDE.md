# Cryptanium User & Operator Guide

## 1. Quickstart Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Git

### Running Backend Locally
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Start FastAPI development server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

### Running Frontend Locally
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node packages
npm install

# 3. Start Vite dev server
npm run dev
```
Open your browser at `http://localhost:3000`

---

## 2. Docker Setup

```bash
# Build and run backend + PostgreSQL database
docker compose up --build -d
```
The backend API service will run on port `8000` connected to PostgreSQL on port `5432`.

---

## 3. How to Perform a Repository Security Audit

1. **Log In**: Open `http://localhost:3000` and click "Login with GitHub" or "Enter Demo Mode".
2. **Select Repository**: Go to the **Repositories** page and click "Add Repository". Enter the GitHub repository URL (e.g. `https://github.com/venkatesh-99-cbs/Cryptanium`).
3. **Trigger Security Scan**: Click **Run Security Scan**. Cryptanium will clone the repository, run SAST/secret/dependency scanners, calculate the Trust Score, and generate AI insights.
4. **View Audit Details**: Navigate to **Scan Details** to view:
   - Trust Score gauge & Risk Tier (`Excellent`, `Good`, `Moderate`, `Risky`, `Critical`).
   - Executive AI Summary & Deployment Readiness verdict.
   - Prioritized Remediation Action Plan.
   - OWASP Top 10 Mapping.
5. **Download Reports**: Click **Download PDF Audit Report** or **Export JSON Data**.
