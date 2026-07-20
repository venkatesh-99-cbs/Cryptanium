# Cryptanium REST API Documentation

The Cryptanium REST API provides endpoints for authentication, repository management, security scanning orchestration, trust score retrieval, AI summary generation, and PDF/JSON report exports.

## Base URL
- **Local Development**: `http://localhost:8000/api`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Authentication

### `GET /auth/login`
Redirects user to GitHub OAuth login consent page.

### `GET /auth/github/callback`
Processes GitHub OAuth authorization code exchange.
- **Parameters**: `code` (string, query)
- **Response**: JWT Token string

### `POST /auth/demo-login`
Generates immediate JWT access token for demo testing mode without requiring GitHub OAuth credentials.
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "username": "demo_user",
      "email": "demo@cryptanium.io"
    }
  }
  ```

### `GET /auth/me`
Retrieves currently authenticated user profile.

---

## Repositories API

### `GET /repositories`
Retrieves list of all registered repositories.

### `POST /repositories`
Registers a new repository for security monitoring.
- **Request Body**:
  ```json
  {
    "name": "Cryptanium",
    "clone_url": "https://github.com/venkatesh-99-cbs/Cryptanium",
    "default_branch": "main"
  }
  ```

### `GET /repositories/{id}`
Retrieves detailed information for a specific repository.

### `POST /repositories/{id}/sync`
Triggers a fresh GitHub metadata sync for the specified repository.

### `DELETE /repositories/{id}`
Deletes a repository and associated scan history.

---

## Scans API

### `POST /scan`
Triggers an immediate end-to-end security scan for a repository.
- **Request Body**:
  ```json
  {
    "repository_name": "venkatesh-99-cbs/Cryptanium",
    "branch": "main"
  }
  ```
- **Response**:
  ```json
  {
    "scan_id": 1,
    "repository_name": "venkatesh-99-cbs/Cryptanium",
    "status": "completed",
    "trust_score": 85.0,
    "findings_count": 5,
    "summary": {
      "total_findings": 5,
      "high_severity_count": 1,
      "medium_severity_count": 1,
      "low_severity_count": 1
    }
  }
  ```

### `GET /scans`
Lists all scan jobs in reverse chronological order.

### `GET /scans/{id}`
Retrieves complete scan results including findings, trust score, and timing.

### `GET /scans/{id}/summary`
Retrieves executive AI summary generated for scan ID.

### `GET /scans/{id}/recommendations`
Retrieves prioritized remediation action plan for scan ID.

---

## Reports API

### `GET /reports`
Lists all generated report metadata.

### `GET /reports/{id}/pdf`
Downloads binary PDF executive security audit report.
- **Content-Type**: `application/pdf`

### `GET /reports/{id}/json`
Downloads structured JSON security audit report.
- **Content-Type**: `application/json`

---

## Status & Error Responses

| Status Code | Description |
| :--- | :--- |
| **200 OK** | Request succeeded |
| **201 Created** | Resource created successfully |
| **400 Bad Request** | Invalid payload or missing required parameter |
| **401 Unauthorized** | Missing or expired JWT Bearer token |
| **404 Not Found** | Requested repository, scan, or report ID does not exist |
| **500 Internal Error** | Internal scanner or engine execution failure |
