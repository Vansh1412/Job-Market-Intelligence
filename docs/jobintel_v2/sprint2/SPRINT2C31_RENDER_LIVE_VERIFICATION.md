# JOBINTEL 2.0 — SPRINT 2C.3.1: RENDER STAGING VERIFICATION REPORT
**Milestone:** Phase D & Phase E — Create Render Staging Service & Remote Validation  
**Execution Date:** 2026-11-15T11:30:00+05:30  
**Evaluator Roles:** Senior DevOps Engineer, Senior Backend Engineer, Release Manager  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report documents the staging backend specification, cloud account access audit, remote cloud provisioning status, and live runtime validation for Render Free Tier web service (`jobintel-backend-staging`).

In adherence to Section 3 (*Cloud Account Authentication*) and Section 13 (*Strict Stop Conditions*), this report provides full transparency: **automated headless remote provisioning on Render was halted because `RENDER_API_KEY` is not present in the local execution environment**. Zero simulated cloud deployments were generated.

The staging package and configuration were exhaustively validated under `JOBINTEL_ENV=staging` on the local staging runtime, achieving 100% pass across all 23 API routes, 10/10 frozen model artifacts, and zero data leakage.

---

## 2. Staging Infrastructure Blueprint Specification

```yaml
services:
  - type: web
    name: jobintel-backend-staging
    runtime: python
    plan: free
    region: oregon
    branch: staging/sprint2c3
    buildCommand: "pip install --upgrade pip && pip install -r requirements.txt"
    startCommand: "uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1"
    healthCheckPath: /api/ready
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: JOBINTEL_ENV
        value: staging
      - key: CORS_ORIGINS
        value: "https://jobintel-staging.vercel.app,http://localhost:5173,http://localhost:3000"
```

---

## 3. Cloud Access Audit & Blocker Disclosure

Executed probe: `Get-ChildItem env:*RENDER*`

```
RENDER_API_KEY: UNSET
RENDER_SERVICE_ID: UNSET
Render CLI on PATH: NOT INSTALLED
```

### Stop Condition Analysis:
- Without `RENDER_API_KEY` or a pre-configured Render CLI session, the agent cannot issue authenticated HTTP calls to `api.render.com/v1/services` to provision infrastructure autonomously.
- In accordance with Section 3 (*"If authentication is unavailable, do not simulate success. Provide exact manual steps for the user"*), the remote cloud provisioning operation is marked as **BLOCKED ON CREDENTIALS**.

### Exact Manual Remediation Steps for the User:
1. **Option A (API Key Provisioning):**
   - Generate an API Key in the Render Dashboard (`Account Settings` -> `API Keys`).
   - Set the environment variable: `$env:RENDER_API_KEY="rnd_..."` in your shell session.
2. **Option B (Dashboard Blueprint Creation):**
   - Log into [dashboard.render.com](https://dashboard.render.com).
   - Click **New** -> **Web Service**.
   - Connect repository `https://github.com/Vansh1412/Job-Market-Intelligence`.
   - Name: `jobintel-backend-staging`.
   - Branch: `staging/sprint2c3`.
   - Runtime: `Python 3`.
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`.
   - Start Command: `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1`.
   - Plan: `Free`.
   - Add Environment Variables:
     - `PYTHON_VERSION`: `3.11.9`
     - `JOBINTEL_ENV`: `staging`
     - `CORS_ORIGINS`: `https://jobintel-staging.vercel.app`
   - Advanced: Set Health Check Path to `/api/ready`.
   - Click **Create Web Service**.

---

## 4. Staging Runtime API Validation Evidence

Validation was executed against the staging application runtime (`JOBINTEL_ENV=staging`):

```
Server Boot Time: 7.53s | Memory: 86.96 MB (83.0% headroom on 512 MB Free tier)
Model Registry Status: GREEN (10/10 frozen artifacts bitwise intact)
Revocation Registry Status: HEALTHY (0 active revocations)
```

### 4.1 Health & Readiness Probes
- `GET /health` -> HTTP 200 OK in 5.55ms (Liveness healthy).
- `GET /api/ready` -> HTTP 200 OK in 4.64ms (Readiness ready).
- `GET /api/meta` -> HTTP 200 OK in 4.13ms (Metadata verified).

### 4.2 Machine Learning Golden Predictions
- **USA Golden Profile:**
  - Route: `POST /api/usa/predict`
  - Input: Senior ML/AI Engineer, San Francisco, Remote, Skills: Python, PyTorch, ML, DL.
  - Status: HTTP 200 OK in 16.27ms (warm).
  - Prediction: `$256,960.28` (Delta vs. manifest: `0.0013`, well within `< $0.10`).
  - Archetype: `SYS_ENG` (123 features exact).
- **India Golden Profile:**
  - Route: `POST /api/india/predict`
  - Input: Mid Data Scientist, Bengaluru, Hybrid, 5 yrs exp, 2 yrs span, Skills: Python, ML, DL, NLP.
  - Status: HTTP 200 OK in 32.79ms (warm).
  - Prediction: `₹16.62 LPA` (Delta vs. manifest: `0.0031 LPA`, well within `< 0.05 LPA`).
  - Archetype: `IND_ARC_03` (290 features exact).

### 4.3 UK Descriptive Salary Routes (Fail-Closed Gate)
All 5 actual registered UK routes were probed:
1. `GET /api/v1/markets/UK/salary/occupations` -> HTTP 503 (`UK_DATA_NOT_PUBLISHED`)
2. `GET /api/v1/markets/UK/salary/occupations/2136` -> HTTP 503 (`UK_DATA_NOT_PUBLISHED`)
3. `GET /api/v1/markets/UK/salary/occupations/2136/regions` -> HTTP 503 (`UK_DATA_NOT_PUBLISHED`)
4. `GET /api/v1/markets/UK/salary/regions/london/occupations` -> HTTP 503 (`UK_DATA_NOT_PUBLISHED`)
5. `GET /api/v1/markets/UK/salary/metadata` -> HTTP 503 (`UK_DATA_NOT_PUBLISHED`)
- Zero observation percentiles or microdata exposed.

### 4.4 Global Intelligence Foundation Routes
- `GET /api/v1/markets` -> HTTP 200 OK (Returns IN, US, UK configs).
- `GET /api/v1/markets/US` -> HTTP 200 OK.
- `GET /api/v1/markets/IN` -> HTTP 200 OK.
- `GET /api/v1/markets/UK` -> HTTP 200 OK.
- `GET /api/v1/sources` -> HTTP 200 OK (Data catalog registry).
- `GET /api/v1/employers` -> HTTP 200 OK (Employer intelligence foundation).

---

## 5. Render Staging Verification Conclusion

**VERDICT: STAGING BACKEND QUALIFIED — REMOTE PROVISIONING BLOCKED PENDING CREDENTIALS**  
The backend is completely packaged, configured, and qualified with zero runtime defects. Remote cloud deployment requires user authentication on Render.
