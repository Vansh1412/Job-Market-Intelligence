# JOBINTEL 2.0 — SPRINT 2C.3.2A: DEPLOYMENT CONFIGURATION AUDIT
**Milestone:** Phase D — Deployment Configuration & CI/CD Trigger Isolation  
**Execution Timestamp:** 2026-11-15T12:09:00+05:30  
**Evaluator Roles:** Senior DevOps Engineer, Principal Software Architect, Release Manager  
**Workspace:** `E:\Job Market` | **Branch:** `staging/sprint2c3`  

---

## 1. Executive Summary

This report establishes the deployment configuration audit for the JOBINTEL 2.0 application, evaluating Render Blueprints, GitHub Actions workflows, container definitions, and CORS/entrypoint wiring.

A critical investigation was conducted into branch isolation: **pushing to `staging/sprint2c3` will NOT trigger Render production deployment and will NOT trigger GitHub Actions CI pipelines**. Production services are completely isolated from staging branch operations.

---

## 2. Render Blueprint Specification Audit (`render.yaml`)

```yaml
services:
  - type: web
    name: jobintel-backend
    runtime: python
    plan: free
    region: oregon
    branch: master
    buildCommand: "pip install --upgrade pip && pip install -r requirements.txt"
    startCommand: "uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1"
    healthCheckPath: /api/ready
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: JOBINTEL_ENV
        value: production
      - key: CORS_ORIGINS
        value: "http://localhost:5173,http://localhost:3000,https://job-market-intelligence-dusky.vercel.app,https://job-market-intelligence.vercel.app,https://jobintel.vercel.app"
```

### Production Isolation Analysis:
- **Production Target:** Render service `jobintel-backend` is explicitly bound to `branch: master`.
- **Staging Isolation:** Pushing to `staging/sprint2c3` has zero effect on the production web service.
- **Root Directory:** Repository root (`.`) is the correct working directory for Render; dependencies in `requirements.txt` and entrypoint in `src/backend/main.py` resolve natively from root.
- **Start Command:** `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1` is verified.
- **Readiness Probe:** `/api/ready` correctly verifies that all required models and registries are operational before routing traffic.

---

## 3. GitHub Actions CI/CD Trigger Audit (`.github/workflows/`)

| Workflow File | Trigger Conditions (`on:`) | Execution on `staging/sprint2c3` Push? | Production Deployment Risk? |
| :--- | :--- | :---: | :---: |
| `ci.yml` | `push: branches: [main, master]`<br>`pull_request: branches: [main, master]` | **NO** (Triggers on main/master only) | **ZERO** |
| `docker-build-manual.yml` | `workflow_dispatch:` | **NO** (Manual trigger only) | **ZERO** |
| `docker-release-gate.yml` | `workflow_dispatch:` | **NO** (Manual self-hosted trigger only) | **ZERO** |

*Conclusion:* No automated pipeline will trigger upon pushing `staging/sprint2c3`. Zero risk of automated deployment to production.

---

## 4. Backend Application Server & Router Registration (`src/backend/main.py`)

- **FastAPI Lifespan:** Synchronizes artifacts, initializes `ModelRegistry`, verifies 10/10 models, loads `RevocationRegistry`.
- **Dual Router Mounting:** All domain routers are mounted under both `/api` and root `/` prefixes, guaranteeing backward compatibility:
  - USA & India routers
  - Overview & Skills routers
  - Methodology & Models routers
  - Global Foundation `/v1` router
  - Descriptive UK Salary `/v1/markets/UK/salary` router
- **CORS Architecture:**
  - Whitelists localhost development origins and production Vercel domains.
  - Merges `CORS_ORIGINS` dynamically while strictly forbidding wildcard (`*`) entries.

---

## 5. Deployment Audit Verdict

**VERDICT: DEPLOYMENT CONFIGURATION AUDIT PASSED**  
Pushing `staging/sprint2c3` is 100% isolated from Render production auto-deployments and GitHub Actions workflows. The backend packaging and start commands are fully validated.
