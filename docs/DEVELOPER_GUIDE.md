# Cryptanium Developer & Contributor Guide

## 1. Project Organization & Architecture

Cryptanium follows a clean multi-module structure:

- `backend/app/`: FastAPI REST API routes, Pydantic schemas, SQLAlchemy models, database setup.
- `backend/services/`: Scanner tool execution engine, cloning, and project framework detection.
- `backend/trust/`: Trust Score Engine strategy rules (`SeverityDeductionRule`, `SecretExposurePenaltyRule`, etc.).
- `backend/ai/`: OpenRouter client, zero-hallucination prompts, AI summarizer, and recommendation generator.
- `backend/reports/`: ReportLab Platypus PDF report builder and JSON export generator.
- `frontend/`: React + TypeScript + Vite + Tailwind CSS dashboard interface.

---

## 2. Adding a New Security Scanner

To add a new SAST or security tool (e.g. `Trivy` or `Checkov`):

1. **Create Scanner Class**: Create `backend/services/scanner/scanners/my_tool_scanner.py` inheriting from `BaseScanner`.
2. **Implement `execute`**: Invoke the tool binary via `CommandRunner` and parse JSON output into `Finding` objects.
3. **Register in Factory**: Add the scanner class to `ScannerFactory.get_scanners()` in `backend/services/scanner/scanner_factory.py`.

---

## 3. Running Unit & Integration Tests

```bash
# Run Member 4 Unit Tests
python -m unittest backend/utils/test_member4.py

# Run Scanner Engine Tests
pytest tests/
```
