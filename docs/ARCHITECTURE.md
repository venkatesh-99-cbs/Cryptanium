# Cryptanium Architecture Specification

## System Overview

Cryptanium is an AI-powered GitHub Repository Trust & Security Analysis Platform built following Clean Architecture principles.

```
+-----------------------------------------------------------------------+
|                       React + TypeScript Frontend                     |
|                   (Vite / Tailwind CSS / Lucide Icons)                |
+-----------------------------------------------------------------------+
                                   |
                             REST API (JSON)
                                   v
+-----------------------------------------------------------------------+
|                          FastAPI API Gateway                          |
|       (Routers: Auth, Repositories, Scans, Reports, AI, Health)       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                        Scanner Engine Orchestrator                    |
|       (Git Clone -> Project Detector -> Language Detector)            |
|       (Parallel Scanners: Semgrep, Bandit, Gitleaks, pip-audit)       |
+-----------------------------------------------------------------------+
                                   |
                          Normalized Findings
                                   v
+-----------------------------------------------------------------------+
|                         Trust Score Engine                            |
|     (Strategy Pattern: Severity, Secrets, Dependencies, Volume)       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    AI Summarization & Remediation Engine              |
|        (OpenRouter Client -> Nemotron Flash / Zero-Key Fallback)       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       Report Generation Pipeline                      |
|           (PDF Generator via ReportLab Platypus / JSON Export)        |
+-----------------------------------------------------------------------+
```

---

## Folder Structure

```
Cryptanium/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI Route Controllers
│   │   ├── core/         # Config, Security, Logging
│   │   ├── database/     # SQLAlchemy Database Models & Schemas
│   │   ├── services/     # Service Layer Business Logic
│   │   └── main.py       # FastAPI Application Entrypoint
│   ├── trust/            # Trust Score Engine & Scoring Rules
│   ├── ai/               # AI Summarizer, Recommendation Engine & OpenRouter Client
│   ├── reports/          # ReportLab PDF & JSON Export Generators
│   ├── services/         # Scanner Tool Execution & Detection Engines
│   └── utils/            # Parsers, Formatters & Test Runners
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI Components
│   │   ├── pages/        # Dashboard, Repositories, Scans, Reports
│   │   ├── services/     # Axios Centralized API Client
│   │   └── App.tsx       # Main Router Component
├── docs/                 # Documentation Suite
├── Dockerfile            # Multi-stage Container Build
├── docker-compose.yml    # PostgreSQL + Backend Orchestration
├── render.yaml           # Cloud Deployment Blueprint
└── README.md             # Project Overview & Quickstart Guide
```

---

## Scanner Pipeline

1. **Workspace Provisioning**: Creates an isolated temporary directory in `cryptanium_workspaces`.
2. **Clone Service**: Uses `git clone --depth 1` to clone the target repository branch.
3. **Detection Engine**: Detects primary programming language, frameworks (Django, React, FastApi), and dependency manifests (`requirements.txt`, `package.json`).
4. **Tool Selection**: Dynamically selects compatible security tools (`Bandit` for Python, `ESLint` for JS/TS, `Gitleaks` for exposed secrets, `Semgrep` for SAST patterns, `pip-audit` / `npm audit` for dependencies).
5. **Concurrent Execution**: Runs tools in parallel using `asyncio.gather`.
6. **Normalization**: Maps raw tool outputs into unified `Finding` objects.

---

## Trust Engine Strategy Pattern

The Trust Score Engine evaluates repository risk starting from 100.0 base score:

$$Score = \max\left(0.0, 100.0 - \sum \text{RuleDeductions}\right)$$

Rules applied:
- **SeverityDeductionRule**: Critical (-25.0), High (-15.0), Medium (-8.0), Low (-3.0), Info (-0.5).
- **SecretExposurePenaltyRule**: Deducts 15.0 points per exposed secret (max cap 40.0).
- **VulnerableDependencyPenaltyRule**: Deducts 10.0 points per vulnerable dependency (max cap 30.0).
- **FindingVolumePenaltyRule**: Applies scaling deduction for finding counts exceeding threshold 10.
