# 02. Backend API Contract Audit Report

## 1. Route Mounting & Architecture

In `src/backend/main.py`, routers are mounted onto the FastAPI application as follows:

```python
# src/backend/main.py:131
app.include_router(v1.router, prefix="/api")

# Legacy / root aliases for backwards-compatibility:
app.include_router(v1.salary_router)
app.include_router(v1.occupations_router)
```

### Forensic Finding: The Root Mount Discrepancy
- The root `/v1/employers` endpoint returns `404 Not Found`. This is **expected and by design**, because unlike `salary` and `occupations` (which have legacy un-prefixed mounts for backward compatibility with pre-2.0 clients), the newer Employer Intelligence router (`v1.router`) is mounted **exclusively** under the `/api` prefix.
- The frontend client in `frontend/src/services/api.ts` defines:
  ```typescript
  const API_BASE = import.meta.env.VITE_API_BASE
    ? import.meta.env.VITE_API_BASE.replace(/\/+$/, '')
    : '/api';
  ```
  And executes all calls as:
  ```typescript
  fetchJson<T>(`/v1/employers...`)
  ```
  Which concatenates to `${API_BASE}/v1/employers...` -> `/api/v1/employers...`.
- Therefore, the frontend client and backend router paths are **100% matched and aligned**.

---

## 2. Exact Backend Route Specifications

| Route Path | HTTP Method | Request Body | Response Model | Description |
|---|---|---|---|---|
| `/api/v1/employers` | `GET` | None (Query: `limit`, `offset`) | `List[EmployerProfile]` | Returns list of verified employer profiles (max limit 50). |
| `/api/v1/employers/resolve` | `POST` | `EmployerResolutionRequest` | `EmployerResolutionResponse` | Resolves entity identity against statutory registers and alias dictionaries. |
| `/api/v1/employers/{company_id}` | `GET` | None (Path: `company_id`) | `EmployerProfile` | Retrieves detailed employer profile; 404 if not found. |

---

## 3. Side-Effect Analysis (Statelessness Proof)

An audit of `src/backend/employers/resolver.py` and `src/backend/api/v1.py` confirms:
1. `EmployerEntityResolver.resolve()` is a **pure function** that performs string canonicalization, regex statutory parsing, and dictionary matching against read-only in-memory registers.
2. The endpoint contains **zero `INSERT`, `UPDATE`, `DELETE`, or file-write calls**.
3. All requests are strictly idempotent and side-effect free.

---

## 4. Live Staging API Verification Evidence

Live HTTP requests were executed directly against the deployed staging backend (`https://jobintel-backend-staging.onrender.com`):

### Probe Results

```json
{
  "probes": [
    {
      "test": "health_check",
      "url": "https://jobintel-backend-staging.onrender.com/health",
      "status": 200,
      "response": {
        "status": "healthy",
        "registry": "operational"
      }
    },
    {
      "test": "get_employers_default",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers",
      "status": 200,
      "response": []
    },
    {
      "test": "get_employers_pagination_5_0",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers?limit=5&offset=0",
      "status": 200,
      "response": []
    },
    {
      "test": "get_employers_pagination_10_100",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers?limit=10&offset=100",
      "status": 200,
      "response": []
    },
    {
      "test": "get_employers_limit_exceeded",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers?limit=100",
      "status": 422,
      "note": "Rejected because query param limit must be <= 50 (FastAPI Query validation)"
    },
    {
      "test": "get_employer_not_found",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers/unknown_synthetic_id_123",
      "status": 404,
      "response": {
        "detail": "Employer not found"
      }
    },
    {
      "test": "resolve_synthetic_name",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers/resolve",
      "status": 200,
      "response": {
        "match_type": "NO_MATCH",
        "resolved_company_id": null,
        "resolved_canonical_name": null,
        "similarity_score": 0.0,
        "review_status": "CONFIRMED_DISTINCT",
        "candidates": [],
        "warnings": [],
        "provenance_notes": [
          "No statutory or canonical match found in sovereign employer registers"
        ]
      }
    },
    {
      "test": "resolve_synthetic_us_cik",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers/resolve",
      "status": 200,
      "response": {
        "match_type": "NO_MATCH",
        "resolved_company_id": null,
        "review_status": "CONFIRMED_DISTINCT",
        "candidates": []
      }
    },
    {
      "test": "resolve_synthetic_in_cin",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers/resolve",
      "status": 200,
      "response": {
        "match_type": "NO_MATCH",
        "resolved_company_id": null,
        "review_status": "CONFIRMED_DISTINCT",
        "candidates": []
      }
    },
    {
      "test": "resolve_malformed_payload",
      "url": "https://jobintel-backend-staging.onrender.com/api/v1/employers/resolve",
      "status": 422,
      "note": "Field required: candidate_name"
    },
    {
      "test": "probe_unmounted_root_employers",
      "url": "https://jobintel-backend-staging.onrender.com/v1/employers",
      "status": 404,
      "note": "Expected 404 confirms router mounted exclusively under /api"
    }
  ]
}
```

### Empty Registry Interpretation
- The response `[]` from `GET /api/v1/employers` on staging is the authentic and correct state of the staging SQLite database when no seed employers have been persisted.
- The frontend `EmployersPage.tsx` correctly interprets `[]` as an empty state and displays a guidance card rather than throwing an unhandled exception or breaking the interface.
