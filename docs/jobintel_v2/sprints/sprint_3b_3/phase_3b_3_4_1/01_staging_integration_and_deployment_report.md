# Sprint 3B.3.3.4.1: Controlled Staging Integration, Deployment & Live Verification Report

## 1. Executive Summary

| Attribute | Specification |
|---|---|
| **Sprint** | Sprint 3B.3.3.4.1 |
| **Mission** | Controlled Staging Release of Employer Intelligence & End-to-End Verification |
| **Role** | Principal DevOps Engineer, Release Manager, Full-Stack Architect, Security Engineer & QA Lead |
| **Repository** | `https://github.com/Vansh1412/Job-Market-Intelligence` |
| **Branch** | `staging/sprint2c3` |
| **Initial Git HEAD** | `d0b176a7f47e18919861c115749cb0cc6a225167` |
| **Final Git HEAD** | `031eebc9b8860e2e7ff09a28849dafa212aa2440` |
| **Staging Frontend** | `https://jobintel-staging.vercel.app` |
| **Staging Backend** | `https://jobintel-backend-staging.onrender.com` |
| **Vercel Deployment ID** | `dpl_5nBGZGKUQvt2oWiKfWRAFQrojFG6` |
| **Production Target** | `https://job-market-intelligence-dusky.vercel.app` (Isolated, 0 deployments) |
| **Production Master SHA**| `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Untouched) |
| **Final Release Verdict**| **BLOCKED — RELEASE NOT VERIFIED** |

---

## 2. Git Lineage & State Forensics

- **Initial Baseline Commit**: `d0b176a7f47e18919861c115749cb0cc6a225167`
- **Release Commit**: `031eebc9b8860e2e7ff09a28849dafa212aa2440`
- **Lineage Proof**: `git merge-base --is-ancestor d0b176a 031eebc` (Exit Code 0; direct child commit)
- **Production Master Isolation**: Pinned strictly to `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Master was neither modified nor pushed).

---

## 3. Exact Committed File Inventory

The release commit staged strictly and only the 8 audited implementation and test files (no audit reports, no temporary scripts, no screenshots, and no credentials):

| File Path | Mode | Change Summary |
|---|---|---|
| `frontend/src/App.tsx` | Tracked (Modified) | Adds lazy-loaded route `/employers` |
| `frontend/src/components/AppHeader.tsx` | Tracked (Modified) | Adds `Employers` navigation link with `data-testid="nav-employers"` |
| `frontend/src/types.ts` | Tracked (Modified) | Defines statutory enums & 6 domain interfaces |
| `frontend/src/services/api.ts` | Tracked (Modified) | Adds `getEmployers`, `resolveEmployer`, `getEmployerDetail` |
| `frontend/src/pages/EmployersPage.tsx` | Untracked (New) | Complete 3-tab Employer Intelligence experience |
| `frontend/src/__tests__/routing.test.ts` | Tracked (Modified) | Verifies route contract for `/employers` |
| `frontend/src/__tests__/employers_contract.test.ts` | Untracked (New) | 14 contract unit tests |
| `frontend/src/__tests__/employers_ui.test.tsx` | Untracked (New) | 7 UI behavioral integration tests |

---

## 4. Commit Details & Push Verification

- **Commit SHA**: `031eebc9b8860e2e7ff09a28849dafa212aa2440`
- **Commit Message**:
  ```
  feat(frontend): integrate Employer Intelligence module and qualification tests (Sprint 3B.3.3.4.1)

  - Add /employers route with code-splitting and global navigation in AppHeader
  - Implement EmployersPage with Entity Resolution, Registry Explorer, and Statutory Standards tabs
  - Reconcile TypeScript interfaces with backend Pydantic models (39/39 fields matching)
  - Enforce strict statutory identity standards, duplicate collision defense, and lexical similarity disclaimers
  - Add comprehensive Vitest test coverage: employers_contract (14 tests) and employers_ui (7 tests)
  - Audited and verified in Sprint 3B.3.3.4.0.1
  ```
- **Remote Push**: `git push origin staging/sprint2c3`
  ```
  To https://github.com/Vansh1412/Job-Market-Intelligence.git
     d0b176a..031eebc  staging/sprint2c3 -> staging/sprint2c3
  ```
- **Remote Verification**: `origin/staging/sprint2c3` is confirmed at `031eebc9b8860e2e7ff09a28849dafa212aa2440`.

---

## 5. Render Staging Backend Verification & Deployed Source Identity

- **Target**: `https://jobintel-backend-staging.onrender.com`
- **Deployment Behavior**: Configured to track `staging/sprint2c3`.
- **Authoritative SHA Verification**: **UNVERIFIED**. Cloudflare edge proxy strips git commit headers, and `RENDER_API_KEY` is not present in local environment.
- **Health & Readiness Check**:
  - `GET /health` -> 200 OK (`{"status":"healthy","service":"JobIntel Unified API","version":"2.0.0"}`)
  - `GET /api/ready` -> 200 OK (`{"status":"ready","ready":true,"artifacts_verified_count":9,"markets":["USA","India"]}`)
  - 9/9 mandatory ML artifacts verified with authentic cryptographic SHA-256 hashes.

---

## 6. Vercel Staging Frontend Deployment & Alias Assignment

- **Target Project**: `jobintel-staging` (Project ID: `prj_Og513XzDt3k6UygBsL0KUkXD89jk`)
- **Deployment Command**: `cd frontend; npx vercel --yes` (Preview deployment; zero `--prod` flag)
- **Deployment ID**: `dpl_5nBGZGKUQvt2oWiKfWRAFQrojFG6`
- **Deployment URL**: `https://jobintel-staging-nm6id2xsd-vansh1412s-projects.vercel.app`
- **Assigned Staging Alias**: `https://jobintel-staging.vercel.app`
- **Alias Command**: `npx vercel alias set jobintel-staging-nm6id2xsd-vansh1412s-projects.vercel.app jobintel-staging.vercel.app`
- **Alias Status**: Verified (`https://jobintel-staging.vercel.app now points to jobintel-staging-nm6id2xsd-vansh1412s-projects.vercel.app`)

---

## 7. Full Local Validation Results (Pre-Commit)

| Test Suite | Framework | Total Tests | Passed | Failed | Duration |
|---|---|---|---|---|---|
| **Backend Suite** | `pytest 8.4.2` | 407 | 407 | 0 | 20.10s |
| **Frontend Suite** | `Vitest 5.0.3` | 42 | 42 | 0 | 2.47s |
| **Production Build** | `Vite 8.3.3` + `tsc` | 2,894 modules | Built clean | 0 | 351ms |
| **Model Parity / Hashes** | SHA-256 verification | 20/20 artifacts | 20 unchanged | 0 | - |

---

## 8. Backend API Verification Matrix (Live Staging Backend)

Probed against `https://jobintel-backend-staging.onrender.com`:

| Endpoint / Scenario | HTTP Method | Expected Status | Observed Status | Response Summary |
|---|---|---|---|---|
| `/health` | `GET` | 200 | 200 OK | Status healthy, 9 artifacts verified |
| `/api/ready` | `GET` | 200 | 200 OK | Ready true, artifacts verified count 9 |
| `/api/v1/employers` (Empty) | `GET` | 200 | 200 OK | `[]` (Authentic empty database) |
| `/api/v1/employers?limit=5&offset=0` | `GET` | 200 | 200 OK | `[]` |
| `/api/v1/employers?limit=10&offset=100` | `GET` | 200 | 200 OK | `[]` |
| `/api/v1/employers?limit=100` | `GET` | 422 | 422 Unprocessable | Rejected: limit must be <= 50 |
| `/api/v1/employers/nonexistent_id` | `GET` | 404 | 404 Not Found | `{"detail": "Employer not found"}` |
| `POST /api/v1/employers/resolve` (US CIK) | `POST` | 200 | 200 OK | `NO_MATCH`, `resolved_company_id: null`, `CONFIRMED_DISTINCT` |
| `POST /api/v1/employers/resolve` (IN CIN) | `POST` | 200 | 200 OK | `NO_MATCH`, `resolved_company_id: null`, `CONFIRMED_DISTINCT` |
| `POST /api/v1/employers/resolve` (UK CRN) | `POST` | 200 | 200 OK | `NO_MATCH`, `resolved_company_id: null`, `CONFIRMED_DISTINCT` |
| `POST /api/v1/employers/resolve` (AU ABN) | `POST` | 200 | 200 OK | `NO_MATCH`, `resolved_company_id: null`, `CONFIRMED_DISTINCT` |
| `POST /api/v1/employers/resolve` (SG UEN) | `POST` | 200 | 200 OK | `NO_MATCH`, `resolved_company_id: null`, `CONFIRMED_DISTINCT` |
| `POST /api/v1/employers/resolve` (Empty `{}`) | `POST` | 422 | 422 Unprocessable | Field required: `candidate_name` |
| `POST /api/v1/employers/resolve` (Empty `""`) | `POST` | 422 | 422 Unprocessable | Min length 1 required |
| `/api/skills/detail/python` (Regression) | `GET` | 200 | 200 OK | Total corpus: 335,995; Postings: 31,676; Prev: 9.43% |
| `/api/india/skills/Development` (Regression) | `GET` | 200 | 200 OK | Cohort: 5,323; Postings: 723; Demand: 13.6% |
| `/api/v1/markets/UK/salary/occupations` | `GET` | 503 | 503 Service Unavail | `UK_DATA_NOT_PUBLISHED` (Gate intact) |
| `/v1/demand/occupations/2134?market=UK` | `GET` | 200 | 200 OK | UK demand disclosure note (Gate intact) |

---

## 9. Live Browser Verification & Forensic Defect Discovery

Executed automated Headless Chrome verification directly on `https://jobintel-staging.vercel.app`:

### Route Navigation Matrix
- `/`: **PASS** (Title: *"JOBINTEL — Job Market Intelligence | Skills · Archetypes · Salaries · Machine Learning"*)
- `/employers`: **PASS** (Direct navigation loads `<EmployersPage />`; page refresh avoids 404 via SPA rewrites)
- `/predictor`: **PASS** (Interactive estimation form renders properly)
- `/skills`: **PASS** (Skills intelligence landscape renders)
- `/occupations`: **PASS** (Occupations explorer renders)
- `/demand`: **PASS** (Demand intelligence renders)
- `/market-explorer`: **PASS** (Global market explorer renders)

---

## 10. CRITICAL BLOCKER: Runtime Route Prefix Mismatch (`/v1/employers` vs `/api/v1/employers`)

During live interactive testing of the `/employers` workflow on `https://jobintel-staging.vercel.app`, the headless browser captured the following network errors:

```
Failed to load resource: the server responded with a status of 404 ()
  URL: https://jobintel-backend-staging.onrender.com/v1/employers?limit=10&offset=0 (Status: 404)
Failed to load resource: the server responded with a status of 404 ()
  URL: https://jobintel-backend-staging.onrender.com/v1/employers/resolve (Status: 404)
```

### Forensic Root Cause Analysis
1. **Backend Mounting**: In `src/backend/main.py:131`, `v1.router` is mounted **exclusively** with `prefix="/api"`:
   ```python
   app.include_router(v1.router, prefix="/api")
   ```
   Unlike legacy routers (`occupations`, `salary`, `demand`) which were mounted both at root and with `prefix="/api"`, `v1.router` exists **only** at `/api/v1/employers*`.
2. **Frontend Service Client**: In `frontend/src/services/api.ts:820-840`:
   ```typescript
   getEmployers: (params?: { limit?: number; offset?: number }) => {
     ...
     return fetchJson<EmployerProfile[]>(`/v1/employers${qs ? `?${qs}` : ''}`);
   },
   resolveEmployer: (payload: EmployerResolutionRequest) =>
     fetchJson<EmployerResolutionResponse>('/v1/employers/resolve', ...),
   getEmployerDetail: (companyId: string) =>
     fetchJson<EmployerProfile>(`/v1/employers/${encodeURIComponent(companyId)}`),
   ```
3. **Environment Construction in Live Staging**:
   On Vercel staging, `VITE_API_BASE_URL` is configured as:
   `https://jobintel-backend-staging.onrender.com`
   When `fetchJson('/v1/employers')` is called:
   `fullUrl = ${API_BASE}${normalizedUrl}`
   `fullUrl = "https://jobintel-backend-staging.onrender.com/v1/employers"`
   This URL bypasses `/api`, hitting the unmounted root path on Render and returning `HTTP 404 Not Found`.

### Stop Condition Invocations (Non-Negotiable)
Section 6 explicitly specified:
> *"Employer list endpoint uses the correct `/api/v1` prefix."*

Section 13 explicitly mandates:
> *"Immediately stop the release if... A runtime defect requires code modification after deployment. If a defect is discovered after deployment, do not quietly patch and continue. Record the defect, stop, and request a separate corrective sprint."*

Section 15 Verdict Rules state:
> *"BLOCKED — RELEASE NOT VERIFIED: Use this if any critical test, API, browser, security, deployment, or production-isolation check fails."*

We strictly follow this mandate. **We do not quietly patch this defect in the deployment sprint.**

---

## 11. Production Isolation Verification

- **Production Master Baseline**: Verified at `198b79dcdff08a5be5f08847c4262d31a3ce261e`.
- **Production Commits / Pushes**: Zero commits, zero pushes to `master`.
- **Production Vercel Deployments**: `job-market-intelligence-dusky.vercel.app` remains 39 days old; zero production deployments initiated.
- **Production Backend Isolation**: Zero requests sent to `https://job-market-intelligence-6ral.onrender.com`.

---

## 12. Final Release Verdict

### **VERDICT: BLOCKED — RELEASE NOT VERIFIED**

**Reason**: Live browser qualification revealed that `frontend/src/services/api.ts` queries `/v1/employers` and `/v1/employers/resolve` rather than `/api/v1/employers` and `/api/v1/employers/resolve`. When built with `VITE_API_BASE_URL="https://jobintel-backend-staging.onrender.com"`, live browser requests fail with HTTP 404.

---

## 13. Recommended Corrective Next Step

Authorize **Sprint 3B.3.3.4.2 (Targeted API Client Route Correction & Re-Release)**:
1. In `frontend/src/services/api.ts`, update employer endpoints to explicitly call `/api/v1/employers`, `/api/v1/employers/resolve`, and `/api/v1/employers/${encodeURIComponent(companyId)}` (or alternatively mount `v1.router` at root in `src/backend/main.py`).
2. Run Vitest and build verification.
3. Commit the correction to `staging/sprint2c3`.
4. Redeploy staging Vercel and verify live resolution and registry workflows.
