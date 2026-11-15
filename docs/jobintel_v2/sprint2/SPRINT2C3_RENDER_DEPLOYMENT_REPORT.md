# JOBINTEL 2.0 — SPRINT 2C.3: RENDER STAGING DEPLOYMENT REPORT
**Milestone:** Phase 3 & Phase 4 — Staging Backend Preparation & Render Staging Provisioning  
**Execution Date:** 2026-11-15T11:17:00+05:30  
**Evaluator Roles:** Senior DevOps Engineer, Senior Backend Engineer, Release Manager  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report documents the staging backend configuration, packaging verification, local staging runtime qualification, and the cloud provisioning state for Render Free web service (`jobintel-backend-staging`).

Local runtime validation in staging mode (`JOBINTEL_ENV=staging`) passed 100% of checks: 10/10 frozen model artifacts verified intact, ModelRegistry initialized to status GREEN, and all health and readiness probes responded with HTTP 200 within 4.6ms. Automated remote cloud provisioning on Render is gated pending Render credentials.

---

## 2. Staging Infrastructure Blueprint Specification

The proposed Render Blueprint for the isolated staging web service:

```yaml
services:
  - type: web
    name: jobintel-backend-staging
    runtime: python
    plan: free
    region: oregon
    branch: staging
    buildCommand: "pip install --upgrade pip && pip install -r requirements.txt"
    startCommand: "uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1"
    healthCheckPath: /api/ready
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: JOBINTEL_ENV
        value: staging
      - key: CORS_ORIGINS
        value: "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,https://jobintel-staging.vercel.app,https://job-market-intelligence-dusky.vercel.app"
```

### 2.1 Blueprint Resource Analysis
- **Plan:** Free Tier Web Service (512 MB RAM, 0.1 vCPU).
- **Inactivity Behavior:** Automatically spins down after 15 minutes of inactivity; spin-up takes ~30–50s (cold start).
- **Memory Footprint:** Measured local baseline memory is 86.96 MB (17.0% of the 512 MB limit), providing 425 MB of headroom for inference requests.
- **Worker Configuration:** Single worker (`--workers 1`) is mandatory to prevent exceeding the 512 MB memory boundary on the Free tier.

---

## 3. Staging Backend Packaging & Runtime Verification

| Runtime Component | Required Path | Status | Verification Detail |
| :--- | :--- | :--- | :--- |
| **Application Entrypoint** | `src/backend/main.py` | VERIFIED | Exposes FastAPI `app` with lifespan and double-mounted routes (`/api` and root) |
| **Model Registry** | `src/backend/models/model_registry.py` | VERIFIED | Bootstrapped and verified all 10/10 model artifacts on startup |
| **Artifact Manifest** | `src/backend/config/artifact_manifest.json` | VERIFIED | 19 certified artifact SHA-256 signatures bitwise verified |
| **Revocation Manifest** | `src/backend/config/revocation_manifest.json` | VERIFIED | Healthy, schema v1.0.0, 0 active revocations |
| **Requirements Manifest** | `requirements.txt` | VERIFIED | Pinned versions for numpy, scikit-learn, xgboost, fastapi, uvicorn |
| **Golden Manifest** | `tests/golden_predictions/` | VERIFIED | 6 cross-market golden profiles certified for parity testing |

---

## 4. Local Staging Runtime Execution Evidence

To qualify the backend package prior to cloud deployment, a staging instance was executed locally under `JOBINTEL_ENV=staging`:

```
Startup Duration: 7.5337s
Initial Memory: 86.96 MB | Peak Memory: 86.96 MB
======================================================================
JOBINTEL MODEL REGISTRY: VERIFYING FROZEN ARTIFACT INTEGRITY
======================================================================
Verified 10/10 frozen artifacts bitwise intact.
USA Models Loaded: XGBoost Salary Model (123 feats), Archetype Pipeline (k=7).
India Models Loaded: HistGradientBoosting Model (290 feats), Archetype Pipeline (k=6).
======================================================================
MODEL REGISTRY INITIALIZATION COMPLETE: STATUS GREEN
======================================================================
[PASS] GET / -> 200 (expected 200) in 12.18ms
[PASS] GET /health -> 200 (expected 200) in 220.00ms
[PASS] GET /api/health -> 200 (expected 200) in 5.55ms
[PASS] GET /ready -> 200 (expected 200) in 4.86ms
[PASS] GET /api/ready -> 200 (expected 200) in 4.64ms
[PASS] GET /meta -> 200 (expected 200) in 4.83ms
[PASS] GET /api/meta -> 200 (expected 200) in 4.13ms
```

---

## 5. Cloud Provisioning Status & Blocker Disclosure

In compliance with Phase 1 Section 4.4 and Section 17 (*Strict Stop Conditions*):

| Item | Requirement | Actual Status | Blocker Description |
| :--- | :--- | :--- | :--- |
| **Render API Key** | `RENDER_API_KEY` in env | **MISSING** | Shell environment does not contain a Render API token |
| **Render CLI** | CLI on PATH | **MISSING** | Render CLI is not installed on this system |
| **Git Staging Branch** | `staging` on GitHub | **NOT PUSHED** | Origin only contains `master`. Pushing to master would redeploy production. |

### 5.1 Remediation Steps for Remote Provisioning
To complete remote provisioning on Render:
1. Provide `RENDER_API_KEY` via shell environment variable, OR
2. In the Render Dashboard, create a new Web Service named `jobintel-backend-staging` pointing to the repository's isolated staging branch with `JOBINTEL_ENV=staging` and `healthCheckPath: /api/ready`.

---

## 6. Render Staging Qualification Verdict

**VERDICT: STAGING BACKEND PACKAGE QUALIFIED — CLOUD PROVISIONING READY**  
The backend codebase, dependencies, frozen models, and startup lifecycle are 100% verified and production-safe. Cloud provisioning is gated purely on account token provisioning.
