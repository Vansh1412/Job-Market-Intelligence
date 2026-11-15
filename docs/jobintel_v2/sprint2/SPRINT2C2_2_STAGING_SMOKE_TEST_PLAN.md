# SPRINT 2C.2.2 — TASK 5: STAGING DEPLOYMENT & SMOKE-TEST PLAN

**Document:** `SPRINT2C2_2_STAGING_SMOKE_TEST_PLAN.md`  
**Author:** Principal Software Architect, Senior Backend Engineer, DevOps Engineer  
**Date:** November 13, 2026  
**Status:** READY FOR OPERATIONAL EXECUTION (Awaiting Explicit User Authorization)  
**Repository:** `e:\Job Market` (`master` branch)

---

## 1. PRE-FLIGHT NOTIFICATION & EXECUTION POLICY

> [!IMPORTANT]
> In accordance with the non-negotiable project rules, **no cloud deployment will be executed without explicit user authorization**. This document details the exact, reproducible operational runbook for executing the staging deployment and smoke-test sequence once authorized.

---

## 2. STEP-BY-STEP STAGING DEPLOYMENT PLAN

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Provision Render Staging Web Service               │
│ - Name: jobintel-backend-staging                            │
│ - Plan: Free / Starter (Region: Oregon)                     │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Configure Staging Environment Variables             │
│ - PYTHON_VERSION = 3.11.9                                   │
│ - JOBINTEL_ENV = staging                                    │
│ - CORS_ORIGINS = https://jobintel-staging.vercel.app,...    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Trigger Backend Staging Deployment & Probe Check    │
│ - Health check target: /api/ready                           │
│ - Wait for status: Live (HTTP 200 OK)                       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Deploy Vercel Staging Frontend Preview              │
│ - Target preview: jobintel-staging.vercel.app               │
│ - Verify rewrites: /api/* -> jobintel-backend-staging.render│
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Execute Automated Smoke Test Suite                  │
│ - Probes (/health, /api/ready)                              │
│ - USA Salary Inference (Golden Parity)                      │
│ - India Salary Inference (Golden Parity)                    │
│ - UK Salary 5-Endpoint Fail-Closed (HTTP 503)               │
│ - Log Sanitization & Stack Trace Inspection                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. DETAILED OPERATIONAL PROCEDURES

### Step 1: Create Separate Render Staging Service
- In the Render Dashboard (or via Render API using Blueprint):
  - Service Type: `Web Service`
  - Name: `jobintel-backend-staging`
  - Repository: `Job Market`
  - Branch: `master`
  - Root Directory: `.`
  - Runtime: `Python 3`
  - Region: `Oregon (US West)`
  - Plan: `Free` (or `Starter` if testing non-sleeping performance)
  - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
  - Start Command: `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1`
  - Health Check Path: `/api/ready`

### Step 2: Configure Environment Variables
Set the following environment variables in the Render staging web service dashboard:

| Variable Key | Staging Value | Purpose |
|---|---|---|
| `PYTHON_VERSION` | `3.11.9` | Locks Python runtime version matching local build |
| `JOBINTEL_ENV` | `staging` | Designates staging execution environment |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000,https://jobintel-staging.vercel.app,https://job-market-intelligence-staging.vercel.app` | Restricts CORS strictly to staging and local test origins |

### Step 3: Deploy Backend to Staging
- Trigger manual deploy from `master` branch.
- Monitor Render build logs:
  1. Ensure `pip install -r requirements.txt` succeeds without dependency conflicts.
  2. Ensure Uvicorn initializes and invokes `lifespan(app)`.
  3. Ensure `Cloud Artifact Sync Report` logs `Verified: 10/10`.
  4. Ensure `Model Registry Status` logs `GREEN (Artifacts Verified: 10/10)`.
  5. Ensure Render health check prober receives HTTP 200 from `/api/ready`.

### Step 4: Deploy Vercel Preview Frontend
- In Vercel:
  - Branch: `staging` or create preview deployment from `master`.
  - Deployment URL: `https://jobintel-staging.vercel.app`.
  - Environment Variables in Vercel:
    `VITE_API_URL=https://jobintel-backend-staging.onrender.com`
  - Verify `vercel.json` rewrites routes `/api/(.*)` to `https://jobintel-backend-staging.onrender.com/api/$1`.

### Step 5: Verify Frontend-to-Backend Routing & CORS
- Issue test `OPTIONS` and `GET` requests from browser console or curl with `Origin: https://jobintel-staging.vercel.app`:
  ```bash
  curl -I -X OPTIONS "https://jobintel-backend-staging.onrender.com/api/ready" \
       -H "Origin: https://jobintel-staging.vercel.app" \
       -H "Access-Control-Request-Method: GET"
  ```
- **Acceptance Criteria:** Response header `Access-Control-Allow-Origin: https://jobintel-staging.vercel.app` is returned. No wildcard `*` is present.

---

## 4. SMOKE-TEST SCRIPT & TEST PAYLOADS

Once deployed, run `scripts/deployment/smoke_test.py` against the staging URL:

```bash
python scripts/deployment/smoke_test.py --base-url https://jobintel-backend-staging.onrender.com
```

### Test 1: Readiness & Liveness Probes
- **Request:** `GET https://jobintel-backend-staging.onrender.com/api/ready`
- **Expected Status:** `200 OK`
- **Expected Body:** `{"status": "ready", "ready": true, "artifacts_verified_count": 10, "markets": ["USA", "India"]}`

### Test 2: USA Salary Inference Parity
- **Request:** `POST https://jobintel-backend-staging.onrender.com/api/predict/salary`
- **Payload:**
  ```json
  {
    "country": "USA",
    "role_name": "Data Scientist",
    "experience_level": "Senior",
    "skills": ["Python", "Machine Learning", "SQL", "AWS"]
  }
  ```
- **Expected Status:** `200 OK`
- **Expected Body:** Contains `predicted_salary_usd`, `confidence_interval`, and valid archetype metadata.

### Test 3: India Salary Inference Parity
- **Request:** `POST https://jobintel-backend-staging.onrender.com/api/india/salary/predict`
- **Payload:**
  ```json
  {
    "role_name": "Machine Learning Engineer",
    "min_experience_years": 4,
    "max_experience_years": 8,
    "location": "Bengaluru",
    "skills": ["Python", "SQL", "Machine Learning"]
  }
  ```
- **Expected Status:** `200 OK`
- **Expected Body:** Contains `predicted_midpoint_lpa`, `predicted_midpoint_inr`, and archetype cluster metrics.

### Test 4: UK Salary Gating & Fail-Closed Enforcement
Execute requests to all 5 UK endpoints:
1. `GET /api/v1/markets/UK/salary/occupations`
2. `GET /api/v1/markets/UK/salary/occupations/2136`
3. `GET /api/v1/markets/UK/salary/occupations/2136/regions`
4. `GET /api/v1/markets/UK/salary/regions/London/occupations`
5. `GET /api/v1/markets/UK/salary/metadata`
- **Expected Status for All 5:** `503 Service Unavailable`
- **Expected Detail:** `{"code": "UK_DATA_NOT_PUBLISHED", "message": "UK salary analytics are not currently published."}`
- **Leakage Check:** Confirm body contains zero observations or salary numbers.

### Test 5: Cold-Start Latency & Resource Monitoring
- Monitor Render Metrics tab:
  - Cold-start container boot time must complete within 25 seconds.
  - Steady-state RAM consumption must remain below 420 MB (within 512 MB Free tier ceiling).
  - CPU usage spikes during artifact verification must settle to < 5% at idle.

### Test 6: Log Sanitization & Security Review
- Inspect the Render live log stream:
  - Confirm no stack traces appear during normal or rejected UK requests.
  - Confirm no filesystem paths (`C:\...`, `/home/...`) or secrets leak into log lines.
  - Confirm every USA/India prediction logs structured audit reference at `DEBUG` level:
    `"Governance inference recorded: market=USA, model=usa_salary_xgboost_v1, allowed=True, code=GOV_ALLOWED_RESEARCH_INFERENCE, ref=gov-eval-..."`

---

## 5. ROLLBACK RUNBOOK

If any staging smoke test fails:
1. **Render Rollback:** In Render Dashboard -> Events -> Click on previous stable deployment -> Click "Rollback to this deploy".
2. **DNS / Routing Isolation:** Set Render staging service to "Suspended" immediately if any confidential data or unexpected route exposure occurs.
3. **Issue Diagnosis:** Pull deployment logs using Render CLI or Dashboard, reproduce locally using unit tests, and resolve findings before re-triggering staging rollout.

