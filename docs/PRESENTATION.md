# Cryptanium - Hackathon & Technical Presentation Guide

## 1. Problem Statement
Modern software engineering relies heavily on third-party repositories, open-source dependencies, and rapid CI/CD deployments. Security teams struggle to evaluate repository risk holistically due to fragmented security tooling outputs, noisy SAST reports, and missing executive-level remediation guidance.

## 2. Solution Overview
Cryptanium provides an AI-powered GitHub Repository Trust Platform that orchestrates SAST, secret detection, and dependency scanning into a single normalized pipeline. It generates an objective **Repository Trust Score (0-100)**, risk tiers, zero-hallucination executive AI summaries (via Nemotron Flash / OpenRouter), and publication-ready PDF audit reports.

## 3. Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend API**: Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT.
- **Scanner Engine**: Semgrep, Bandit, Gitleaks, pip-audit, npm audit, ESLint.
- **AI Engine**: OpenRouter API, Nemotron Flash (`nvidia/nemotron-4-340b-instruct`), Zero-Key Rule Engine Fallback.
- **Reporting**: ReportLab Platypus PDF Generator, NumberedCanvas two-pass pagination.
- **Infrastructure**: Docker, Docker Compose, PostgreSQL, Render Cloud Deployment.

## 4. Key Highlights & Innovation
1. **Unified Trust Score Metric**: Replaces scattered scanner outputs with a single, transparent mathematical trust score.
2. **Zero-Hallucination AI Remediation**: System prompts enforce strict grounding in verified scanner outputs.
3. **Graceful Offline Fallback**: Works 100% offline without API keys using rule-based deterministic fallback summarization.
4. **Clean Modular Architecture**: Separation of scanning, scoring, AI processing, and reporting allows independent module extensibility.
