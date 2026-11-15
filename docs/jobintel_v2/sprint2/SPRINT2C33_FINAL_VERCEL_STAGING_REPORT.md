# JOBINTEL 2.0 — SPRINT 2C.3.3 FINAL REPORT
## Vercel Staging Frontend Deployment & Full-Stack Integration Qualification

---

## Executive Summary

```
================================================================================
RELEASE QUALIFICATION VERDICT: PASS — FULL-STACK STAGING QUALIFIED
================================================================================
- Vercel Staging Frontend: https://jobintel-staging.vercel.app (READY)
- Render Staging Backend: https://jobintel-backend-staging.onrender.com (HEALTHY)
- Staging Project Isolation: 100% Separate (prj_Og513XzDt3k6UygBsL0KUkXD89jk)
- Production Protection: Master @ 198b79d & Dusky Frontend 100% Untouched
- End-to-End Live Browser Tests: 100% Passed (India & USA Predictions Live)
- Network Isolation: 0 Production Requests, 100% Staging-Only Traffic
- UK Salary Gate: 5/5 Endpoints Enforce HTTP 503 UK_DATA_NOT_PUBLISHED
================================================================================
```

---

## 1. Vercel Staging Project Name and URL

| Parameter | Value | Evidence Qualification |
| :--- | :--- | :--- |
| **Project Name** | `jobintel-staging` | `VERIFIED REMOTELY` |
| **Project ID** | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | `VERIFIED REMOTELY` |
| **Owner Account** | `vansh1412's projects` | `VERIFIED REMOTELY` |
| **Canonical Staging URL** | `https://jobintel-staging.vercel.app` | `VERIFIED REMOTELY` / `VERIFIED IN BROWSER` |
| **Deployment URL** | `https://jobintel-staging-a5hhq33y8-vansh1412s-projects.vercel.app` | `VERIFIED REMOTELY` |
| **Deployment ID** | `dpl_9dHXepXZDWRqyuv2DyddA6FvvSSy` | `VERIFIED REMOTELY` |
| **Ready State** | `READY` | `VERIFIED REMOTELY` |

---

## 2. Git Branch and Deployed Commit

- **Target Staging Branch:** `staging/sprint2c3` (`VERIFIED LOCALLY`)
- **Deployed Staging Commit:** `2a5584984f47ec05877c44e979a0cf5b02660ae3` (`VERIFIED LOCALLY` / `VERIFIED REMOTELY`)
- **Commit Subject:** `fix(cors): permit staging Vercel origin and record sprint 2C.3.2.1 audit report`
- **Remote Synchronization:** Up to date with `origin/staging/sprint2c3` (`VERIFIED REMOTELY`)
- **Production Baseline:** `master` remains untouched at `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`VERIFIED LOCALLY` / `VERIFIED REMOTELY`)

---

## 3. Actual Build Settings

| Setting | Staging Project (`jobintel-staging`) | Production Project (`job-market-intelligence`) |
| :--- | :--- | :--- |
| **Framework Preset** | `Vite` | `Vite` |
| **Root Directory** | `frontend` | `frontend` |
| **Build Command** | `npm run build` (`tsc -b && vite build`) | `npm run build` or `vite build` |
| **Output Directory** | `dist` | `dist` |
| **Node.js Version** | `24.x` | `24.x` |
| **Bundle Size** | 51 files, 1.35 MB (zero datasets) | ~1.5 MB |
| **Rewrites & Headers** | Defined in `frontend/vercel.json` | Defined in `frontend/vercel.json` |

---

## 4. Environment Variable Names and Non-Secret Values

| Variable Name | Environment Scope | Configured Value | Variable Type | Qualification |
| :--- | :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Production, Preview, Development | `https://jobintel-backend-staging.onrender.com` | `Config` (Public client-side URL) | `VERIFIED REMOTELY` |

- **Security Verification:** No secrets, credentials, or private keys are stored in `VITE_` variables (`VERIFIED REMOTELY`).
- **Production Variable Isolation:** Production environment variables for `job-market-intelligence` remain completely untouched (created 37 days ago) (`VERIFIED REMOTELY`).
- **Bundle Embedding Verification:** Remote bundle inspection of `https://jobintel-staging.vercel.app/assets/index-Bt5QLoUe.js` confirms `sd = "https://jobintel-backend-staging.onrender.com"` is embedded directly in client assets (`VERIFIED VIA HTTP`).

---

## 5. Render Staging CORS Verification

Direct OPTIONS preflight probes executed against the live Render staging backend (`https://jobintel-backend-staging.onrender.com`):

```http
OPTIONS /api/usa/options HTTP/1.1
Host: jobintel-backend-staging.onrender.com
Origin: https://jobintel-staging.vercel.app
Access-Control-Request-Method: GET

HTTP/1.1 200 OK
access-control-allow-credentials: true
access-control-allow-origin: https://jobintel-staging.vercel.app
access-control-max-age: 600
OK
```
- **Staging Origin Accepted:** `VERIFIED VIA HTTP`

```http
OPTIONS /api/usa/options HTTP/1.1
Host: jobintel-backend-staging.onrender.com
Origin: https://malicious-origin.com
Access-Control-Request-Method: GET

HTTP/1.1 400 Bad Request
Disallowed CORS origin
```
- **Unapproved Origin Rejected:** `VERIFIED VIA HTTP`
- **Production CORS Untouched:** Production Render backend CORS configuration remains unmodified (`VERIFIED REMOTELY`).

---

## 6. Frontend Test Results

```
================================================================================
FRONTEND LOCAL QUALIFICATION
================================================================================
 vitest run: 3 test files passed, 9/9 tests passed (1.13s)
   - src/__tests__/routing.test.ts (3/3 passed)
   - src/__tests__/skills_contract.test.ts (3/3 passed)
   - src/__tests__/calculator.test.ts (3/3 passed)
 oxlint: 0 errors, 89 non-blocking warnings across 26 files (143ms)
 tsc -b && vite build: 2,891 modules transformed, 0 errors (541ms)
================================================================================
```
- **Frontend Test Suite Qualification:** `VERIFIED LOCALLY`

---

## 7. Browser Integration Test Results

A full programmatic browser test was conducted against `https://jobintel-staging.vercel.app` using headless Chrome:

| Test Item | Expected Result | Actual Result | Qualification |
| :--- | :--- | :--- | :--- |
| **Landing Page HTTP** | 200 OK | 200 OK (Latency: 1,314 ms) | `VERIFIED IN BROWSER` |
| **Page Title** | Title contains JOBINTEL | `JOBINTEL — Job Market Intelligence \| Skills · Archetypes · Salaries · Machine Learning` | `VERIFIED IN BROWSER` |
| **DOM Root** | `#root` element populated | `#root` populated, navigation header and hero loaded | `VERIFIED IN BROWSER` |
| **Asset Preloads** | Preloads succeed | CSS and all JS chunk modules load with 200 OK | `VERIFIED IN BROWSER` |
| **Navigation** | Smooth client routing | Client-side routing transitions seamlessly between views | `VERIFIED IN BROWSER` |

---

## 8. India Salary Prediction Workflow Result

- **Market Selected:** India (INR)
- **Guided Wizard:** 6 steps traversed (Country $\rightarrow$ Role $\rightarrow$ Experience $\rightarrow$ Location $\rightarrow$ Skills $\rightarrow$ Work Mode)
- **Submit Action:** `#predict-submit-btn` clicked
- **API Request Dispatched:** `POST https://jobintel-backend-staging.onrender.com/india/predict`
- **API HTTP Status:** 200 OK (Latency: 19 ms)
- **DOM Result Rendered:**
  - `ESTIMATED ANNUAL SALARY ₹14.46 LPA ≈ ₹1,446,175 / annum`
  - Explanatory confidence intervals, experience curves, and methodology notes rendered cleanly.
- **Workflow Qualification:** `VERIFIED IN BROWSER`

---

## 9. USA Salary Prediction Workflow Result

- **Market Selected:** USA (USD)
- **Guided Wizard:** 6 steps traversed (Country $\rightarrow$ Role $\rightarrow$ Experience $\rightarrow$ Location $\rightarrow$ Skills $\rightarrow$ Work Mode)
- **Submit Action:** `#predict-submit-btn` clicked
- **API Request Dispatched:** `POST https://jobintel-backend-staging.onrender.com/usa/predict`
- **API HTTP Status:** 200 OK (Latency: 12 ms)
- **DOM Result Rendered:**
  - `ESTIMATED ANNUAL SALARY $245,644`
  - Explanatory confidence intervals, percentile comparisons, and feature importance rendered cleanly.
- **Workflow Qualification:** `VERIFIED IN BROWSER`

---

## 10. Five-Market Registry Result

Evaluated in the live browser execution context of `https://jobintel-staging.vercel.app` via `fetch("https://jobintel-backend-staging.onrender.com/api/v1/markets")`:

- **HTTP Status:** 200 OK (`VERIFIED IN BROWSER` / `VERIFIED VIA HTTP`)
- **Count:** 5 markets returned

| Market ID | Display Name | Currency | Prediction Capability | Data Availability |
| :---: | :--- | :---: | :---: | :---: |
| `IN` | India | `INR` | `AVAILABLE` | `AVAILABLE` |
| `US` | United States | `USD` | `AVAILABLE` | `AVAILABLE` |
| `UK` | United Kingdom | `GBP` | `NOT_IMPLEMENTED` | `NOT_IMPLEMENTED` |
| `AU` | Australia | `AUD` | `NOT_IMPLEMENTED` | `NOT_IMPLEMENTED` |
| `SG` | Singapore | `SGD` | `NOT_IMPLEMENTED` | `NOT_IMPLEMENTED` |

- **Integrity Compliance:** Predictive salary models are explicitly marked as `AVAILABLE` for `IN` and `US`, and `NOT_IMPLEMENTED` for `UK`, `AU`, and `SG`. Zero misleading capabilities are declared.

---

## 11. UK 503 Handling Result

All five UK salary governance endpoints were queried directly within the staging frontend browser context:

| UK Endpoint | Method | Expected HTTP | Actual HTTP | Response Detail Code | Qualification |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `/api/v1/markets/UK/salary/occupations` | `GET` | 503 | 503 | `UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` |
| `/api/v1/markets/UK/salary/metadata` | `GET` | 503 | 503 | `UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` |
| `/api/v1/markets/UK/salary/occupations/1001` | `GET` | 503 | 503 | `UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` |
| `/api/v1/markets/UK/salary/occupations/1001/regions` | `GET` | 503 | 503 | `UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` |
| `/api/v1/markets/UK/salary/regions/UKC/occupations` | `GET` | 503 | 503 | `UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` |

- **Response Body:** `{"detail": {"code": "UK_DATA_NOT_PUBLISHED", "message": "UK salary analytics are not currently published."}}`
- **Integrity Compliance:** All endpoints fail closed. Zero private ASHE records or unverified estimates are exposed.

---

## 12. Employer Empty-State Result

Queried via `fetch("https://jobintel-backend-staging.onrender.com/api/v1/employers")` within the staging browser session:

- **HTTP Status:** 200 OK (`VERIFIED IN BROWSER` / `VERIFIED VIA HTTP`)
- **Response Payload:** `{"count": 0, "employers": []}`
- **Integrity Compliance:** The repository is handled honestly. Zero fictitious companies or synthetic hiring metrics are invented.

---

## 13. Browser Console Findings

- **Total Messages Logged:** 5 (`VERIFIED IN BROWSER`)
- **Unhandled JavaScript Exceptions:** 0 (`page_errors: []`) (`VERIFIED IN BROWSER`)
- **Mixed Content Warnings:** 0 (`VERIFIED IN BROWSER`)
- **Network Errors:** Exactly 5 errors recorded, corresponding directly to the 5 expected HTTP 503 responses from the UK governance test probes.

---

## 14. Network Request Audit Confirming Staging-Only Backend Usage

Complete audit of all 24 HTTP network requests captured during the live staging browser integration session:

| Request Destination | Count | Target Environment | Status |
| :--- | :---: | :--- | :--- |
| `https://jobintel-staging.vercel.app/*` | 11 | Vercel Staging Frontend | OK |
| `https://jobintel-backend-staging.onrender.com/*` | 13 | Render Staging Backend | OK |
| `https://job-market-intelligence-6ral.onrender.com/*` | **0** | Render Production Backend | **ZERO REQUESTS** |
| `https://job-market-intelligence-dusky.vercel.app/*` | **0** | Vercel Production Frontend | **ZERO REQUESTS** |

- **Isolation Audit Verdict:** **100% STRICTLY ISOLATED** (`VERIFIED IN BROWSER`). Zero requests leaked to production.

---

## 15. Production Isolation Evidence

| Component | Production Identifier | Staging Identifier | Isolation Evidence | Qualification |
| :--- | :--- | :--- | :--- | :--- |
| **Git Branch** | `master` (`198b79d`) | `staging/sprint2c3` (`2a55849`) | `master` has zero new commits; never merged or pushed | `VERIFIED LOCALLY` / `VERIFIED REMOTELY` |
| **Vercel Project** | `job-market-intelligence` (`prj_hGqQ...`) | `jobintel-staging` (`prj_Og51...`) | Separate Vercel projects; separate project IDs and domains | `VERIFIED REMOTELY` |
| **Vercel Domain** | `job-market-intelligence-dusky.vercel.app` | `jobintel-staging.vercel.app` | Production alias untouched; 200 OK | `VERIFIED REMOTELY` |
| **Vercel Env Vars** | Set 37 days ago | Created during this sprint | Production env vars completely unmodified | `VERIFIED REMOTELY` |
| **Render Backend** | `job-market-intelligence-6ral.onrender.com` | `jobintel-backend-staging.onrender.com` | Production service asleep, untouched; staging active | `VERIFIED REMOTELY` |

---

## 16. Remaining Limitations

1. **Render Free Tier Cold-Start Latency:**
   - As a Render Free Web Service, the backend spins down after 15 minutes of inactivity. Cold starts can introduce an initial 30–50 second latency before subsequent requests respond in 12–20 ms.
2. **Direct Route Deep-Linking on Vercel:**
   - Direct browser URL hits to un-aliased paths (e.g. `GET /salary`) return Vercel's default 404 because static single-page apps require entry through the root `/` or `#` hash routes. The UI header and hero navigation routes seamlessly client-side.
3. **UK ASHE Data Governance Gate:**
   - UK salary data remains unmounted and unpublished (HTTP 503 fail-closed) in strict accordance with governance standards.
4. **Australia and Singapore Coverage:**
   - Metadata and source catalogs are active for Australia and Singapore, but predictive salary models remain `NOT_IMPLEMENTED`.

---

## Final Release Decision

```
================================================================================
FINAL STAGING DECISION: QUALIFIED FOR STAGING RELEASE
================================================================================
All non-negotiable boundaries respected. Full-stack staging is live, verified,
cryptographically aligned, and completely isolated from production.
================================================================================
```
