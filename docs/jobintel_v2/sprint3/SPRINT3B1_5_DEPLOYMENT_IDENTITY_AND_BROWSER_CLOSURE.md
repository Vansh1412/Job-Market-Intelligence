# JOBINTEL 2.0 — SPRINT 3B.1.5
## DEPLOYMENT IDENTITY & BROWSER EVIDENCE CLOSURE REPORT

**Document ID:** `JOBINTEL-V2-SPRINT3B1-5-IDENTITY-BROWSER-CLOSURE`  
**Execution Date:** 2026-11-16  
**Auditor / Roles:** Principal Deployment Verification Engineer, Cloud Infrastructure Auditor, Browser Automation Engineer  
**Branch:** `staging/sprint2c3`  
**Expected Staging Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Staging Backend URL:** `https://jobintel-backend-staging.onrender.com`  
**Staging Frontend URL:** `https://jobintel-staging.vercel.app`  
**Production Backend URL:** `https://job-market-intelligence-6ral.onrender.com`  
**Production Frontend URL:** `https://job-market-intelligence-dusky.vercel.app`  

---

## A. EXECUTIVE VERDICT

### Overall Verdict: **CONDITIONAL PASS — PROVENANCE CLOSED, VERCEL STAGING ALIAS STALE**

This independent verification milestone successfully investigated and closed the deployment provenance, browser evidence, and readiness semantics gaps identified in Sprint 3B.1.4:

1. **Vercel Deployment Identity:** **VERIFIED**. Direct platform API inspection of `jobintel-staging` confirmed the active deployment ID is `dpl_FnGQsqsfU58WPbEPtLUQZes187jr`, deployed at Git commit `1f82f496cc16a36bda37badd1ef16d4e8c080409` (Sprint 2C.3.4 SPA routing fix). This commit is a verified ancestor of `5897413`, but is **stale**: the project lacks automatic GitHub webhooks (`link: None`), meaning Sprint 3A and 3B.1 frontend updates are not yet live on `https://jobintel-staging.vercel.app`.
2. **Render Deployment Identity:** **RENDER_DEPLOYMENT_IDENTITY_UNVERIFIED (STRICT)**. Because `RENDER_API_KEY` is not provisioned in the execution environment and Render reverse proxies strip commit metadata from public HTTP headers, the exact commit SHA cannot be independently extracted from public headers alone. However, functional verification confirms 100% SHA-256 parity across 9/9 ML model artifacts and live execution of all Sprint 3B.1.2 endpoints.
3. **Browser Automation & Network Isolation:** **PASS**. Headless Chromium executed across 8 routes (180 total network requests). Exactly **zero** requests targeted the production backend (`job-market-intelligence-6ral.onrender.com`).
4. **CORS Security:** **PASS**. Strict preflight checks confirmed that `https://jobintel-staging.vercel.app` is permitted with credentials, while untrusted origins (`https://malicious-origin.com`) are rejected with HTTP 400 (`Disallowed CORS origin`).
5. **Readiness Semantics:** **READINESS_SEMANTICS_VERIFIED**. Source inspection of `src/backend/main.py` confirmed that `/api/ready` is a container readiness probe verifying the operational status of trained ML prediction models (USA XGBoost and India HGBR). It is not a catalog of registered product markets (`/api/v1/markets`), and the frontend does not use it for market selection.

---

## B. GIT BASELINE CONFIRMATION

Inspection executed via read-only Git commands:

- **Local Branch:** `staging/sprint2c3`
- **Local HEAD:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`
- **Remote Staging HEAD:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (`origin/staging/sprint2c3` — in exact sync)
- **Production Master HEAD:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`origin/master` — untouched)
- **Staging vs Master Delta:** Staging is 12 commits ahead of master baseline, zero commits behind.
- **Working Tree Status:** Clean; zero tracked modifications. All audit reports remain untracked.

---

## C. RENDER DEPLOYMENT IDENTITY

- **Target Service:** `jobintel-backend-staging`
- **Target URL:** `https://jobintel-backend-staging.onrender.com`
- **Configured Branch:** `staging/sprint2c3` (per `render.yaml` specification)
- **Runtime:** Python 3.11 / Uvicorn (`x-render-origin-server: uvicorn`)
- **Public Header Analysis:** Cloudflare reverse proxy headers (`rndr-id`, `cf-cache-status`, `Server: cloudflare`). No commit SHA, branch, or deployment ID is exposed in public response headers.
- **Platform Metadata Audit:** `RENDER_API_KEY` and `RENDER_SERVICE_ID` are unconfigured in the local environment. Render CLI is not installed. Render does not publish commit statuses to GitHub.
- **Strict Identity Status:** **`RENDER_DEPLOYMENT_IDENTITY_UNVERIFIED`**
- **Semantic / Checksum Evidence:** All 9 mandatory production model artifacts in `/health` match local repository SHA-256 hashes bit-for-bit (e.g. `india_salary_model: 7a3490d7...`, `usa_salary_model: 55c1b7fd...`). All Sprint 3B.1.2 schema additions (`OFFICIALLY_DERIVED`, MOM OWS 2023, World Bank WDI `PA.NUS.PRVT.PP`, fail-closed UK 503) execute live.

---

## D. VERCEL DEPLOYMENT IDENTITY

Inspection executed via authorized read-only Vercel Platform API (`https://api.vercel.com/v13/deployments/`):

| Parameter | Observed Value | Evidence Source |
| :--- | :--- | :--- |
| **Project Name** | `jobintel-staging` | Vercel Project API |
| **Project ID** | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | Vercel Project API |
| **Active Staging Alias** | `https://jobintel-staging.vercel.app` | Vercel Deployment API |
| **Deployment ID** | `dpl_FnGQsqsfU58WPbEPtLUQZes187jr` | Vercel Deployment API |
| **Deployment URL** | `https://jobintel-staging-mykja4r7a-vansh1412s-projects.vercel.app` | Vercel Deployment API |
| **Deployment Status** | `READY` | Vercel Deployment API |
| **Creation Time** | Sun Nov 15 2026 15:25:40 GMT+0530 (`1794736540507`) | Vercel Deployment API |
| **Git Provider** | `github` | Vercel Deployment API |
| **Git Repository** | `Vansh1412/Job-Market-Intelligence` | Vercel Deployment API |
| **Git Branch** | `staging/sprint2c3` | Vercel Deployment API |
| **Exact Deployed Git SHA** | **`1f82f496cc16a36bda37badd1ef16d4e8c080409`** | Vercel Deployment API |
| **Commit Message** | `fix(vercel): enable SPA fallback by removing cleanUrls conflict in frontend vercel.json` | Vercel Deployment API |
| **Actor** | `antigravity` | Vercel Deployment API |
| **Build Status** | `success` (Build Duration: 14s) | Vercel Deployment API |
| **Git Ancestry Result** | **VERIFIED ANCESTOR** (`git merge-base --is-ancestor 1f82f49 HEAD` exited 0) | Git Engine |

### Root Cause of Vercel Staleness
Vercel Project API inspection of `prj_Og513XzDt3k6UygBsL0KUkXD89jk` reveals:
- `link: None` (The project is a CLI-deployed project, not linked to a GitHub repository webhook).
- When commits `13f362c` (Sprint 3A), `b4d86a3` (Sprint 3B.0), `0d0b2ed` (Sprint 3B.1), and `5897413` (Sprint 3B.1.2) were pushed to GitHub, Vercel Bot automatically built preview deployments under the *other* project (`job-market-intelligence`), but did **not** deploy to `jobintel-staging`.
- Therefore, the active alias `https://jobintel-staging.vercel.app` remains pinned to commit `1f82f49` (Sprint 2C.3.4).

---

## E. DEPLOYMENT LINEAGE AND CONSISTENCY TABLE

| Layer | Expected Branch | Expected Commit | Observed Commit | Lineage Status |
| :--- | :--- | :--- | :--- | :--- |
| **Git Local** | `staging/sprint2c3` | `5897413` | `5897413` | **SYNCED (HEAD)** |
| **Git Remote Staging** | `staging/sprint2c3` | `5897413` | `5897413` | **SYNCED (`origin`)** |
| **Render Staging Backend** | `staging/sprint2c3` | `5897413` | `5897413` (inferred) | **FUNCTIONALLY VERIFIED** (SHA unverified in public headers) |
| **Vercel Staging Frontend** | `staging/sprint2c3` | `5897413` | **`1f82f49`** | **STALE ANCESTOR** (Sprint 2C.3.4, missing Sprint 3 UI) |
| **Production Git** | `master` | `198b79d` | `198b79d` | **UNTOUCHED BASELINE** |
| **Production Backend** | `master` | `198b79d` | `198b79d` | **UNTOUCHED BASELINE** (Salary routes 404) |

---

## F. REAL BROWSER VERIFICATION (PUPPETEER + CHROMIUM)

A live browser audit was executed using headless Chromium (`1400x900` viewport) across 8 routes:

| Route Tested | HTTP Status | Initial Mount | Refresh Mount | Route Handling / Rendered View | Console Errors |
| :--- | :---: | :---: | :---: | :--- | :---: |
| `/` | 200 | True | True | HomePage (Hero, Feature cards, Market CTA) | 0 |
| `/occupations` | 200 | True | True | Fallback to HomePage (Route unmapped in `1f82f49`) | 0 |
| `/salary` | 200 | True | True | PredictorPage (Single-market salary calculator) | 0 |
| `/employers` | 200 | True | True | Fallback to HomePage (Route unmapped in `1f82f49`) | 0 |
| `/markets` | 200 | True | True | Fallback to HomePage (Route unmapped in `1f82f49`) | 0 |
| `/cross-market` | 200 | True | True | CrossMarketPage (USA vs India Sprint 2C comparison) | 0 |
| `/how-it-works` | 200 | True | True | MethodologyPage (Research methodology) | 0 |
| `/unknown-route-nonexistent` | 200 | True | True | Fallback to HomePage (`replaceState` to `/`) | 0 |

### Visual State & Routing Behavior
1. **React Application Mount:** React mounts cleanly across all routes with zero uncaught exceptions and zero page crashes (`pageErrors: 0`).
2. **SPA Deep-Linking & Unknown Routes:** The SPA router at commit `1f82f49` matches paths against `ROUTE_MAP`. If a path is unrecognized (e.g. `/occupations`, `/employers`, or unknown paths), it gracefully falls back to `'home'` and replaces the browser URL with `/`. It does not render a blank screen or broken 404 page.
3. **Salary UI Observation:** Because the frontend is deployed at commit `1f82f49`, the navigation bar displays the 7 Sprint 2C items: `Home`, `Salary Calculator`, `Explore Market`, `Skills`, `Archetypes`, `USA vs India`, `How It Works`. The new Tab 4 ("Cross-Market Salary Intelligence") in `OccupationsPage.tsx` is contained in local code (`5897413`), but not rendered in this deployed build.

---

## G. ACTUAL NETWORK AUDIT & STAGING ISOLATION

During the headless browser session, all 180 network requests across all 8 route visits were intercepted and categorized:

| Request Category | Request Count | Result / Target Domain | Status |
| :--- | :---: | :--- | :--- |
| **Staging Frontend Assets** | 112 | `https://jobintel-staging.vercel.app` (HTML, JS, CSS, icons) | **PASS** |
| **Staging Backend APIs** | 4 | `https://jobintel-backend-staging.onrender.com` | **PASS** |
| **Third-Party Static Assets** | 64 | Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) | **PASS** |
| **Analytics / Telemetry** | 0 | None | **PASS** |
| **Production Backend Requests** | **0** | `https://job-market-intelligence-6ral.onrender.com` | **PERFECT ISOLATION** |
| **Failed Critical Requests** | 0 | None (All returned 200/304) | **PASS** |

**Zero production backend requests occurred.** Staging frontend network traffic remains strictly isolated.

---

## H. CORS PREFLIGHT VERIFICATION

Live OPTIONS preflight probes against `https://jobintel-backend-staging.onrender.com`:

1. **Authorized Staging Origin (`https://jobintel-staging.vercel.app`):**
   - Endpoints tested: `/api/v1/markets`, `/v1/salary/rates`.
   - Response: `HTTP 200 OK`.
   - `access-control-allow-origin: https://jobintel-staging.vercel.app`
   - `access-control-allow-credentials: true`
   - `access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, QUERY`
   - `access-control-max-age: 600`
2. **Untrusted / Malicious Origin (`https://malicious-origin.com`):**
   - Response: `HTTP 400 Bad Request`.
   - Body: `Disallowed CORS origin`.
   - `access-control-allow-origin: null` (Origin rejected; zero headers granted).

---

## I. READINESS SEMANTICS INVESTIGATION

### Inquiry
Why does `/api/ready` report `markets: ["USA", "India"]` while `/api/v1/markets` reports five markets?

### Evidence & Findings
1. **Implementation Code (`src/backend/main.py` lines 165-179):**
   ```python
   @app.get("/api/ready")
   def readiness_check():
       """Readiness probe: answers 'Are all required production models available?'."""
       registry = get_model_registry()
       status = registry.get_status_report()
       is_ready = status["status"] == "GREEN" and ...
       if is_ready:
           return {
               "status": "ready",
               "ready": True,
               "artifacts_verified_count": status["artifacts_verified_count"],
               "markets": ["USA", "India"],
           }
   ```
2. **Architectural Purpose:**
   - `/api/ready` is the Kubernetes/Render container readiness probe (configured in `render.yaml` as `healthCheckPath: /api/ready`).
   - It verifies that the machine learning prediction models in `ModelRegistry` (USA XGBoost Regressor and India HistGradientBoostingRegressor) are loaded and cryptographically verified.
   - UK, Australia, and Singapore are **descriptive statistical benchmark markets** based on government releases (ONS, ABS, MOM) and do not have trained ML predictive models in `ModelRegistry`.
3. **Product Catalog (`/api/v1/markets`):**
   - Implemented via `src/backend/markets/registry.py`, which defines the five platform jurisdictions (USA, India, UK, Australia, Singapore).
4. **Frontend Consumer Audit:**
   - AST search across `frontend/src/` confirmed zero usages of `/api/ready` or `/ready`. The frontend consumes `/api/v1/markets` for market listings and does not misinterpret `/api/ready`.
5. **Conclusion:** **`READINESS_SEMANTICS_VERIFIED`**. The separation between ML prediction readiness and descriptive market registration is architectural and intentional.

---

## J. PREVIOUS DATA LIMITATIONS CONFIRMATION

All five previously documented data limitations remain disclosed and preserved:
1. **BLS URL Dynamism:** US BLS `/oes/current/` URL is an active reference link, not an immutable May 2023 snapshot.
2. **Singapore Annualized Wage Rate:** MOM OWS gross monthly wage annualized (monthly gross × 12) is a wage rate, not total annual cash compensation (bonuses and AWS are excluded).
3. **Australia Unit Group Inheritance:** Detailed OSCA 6-digit occupations inherit 4-digit ANZSCO unit group earnings.
4. **UK Data Withheld:** UK ASHE 2024 data remains gated (`UK_DATA_NOT_PUBLISHED`, HTTP 503 fail-closed).
5. **India CTC vs Survey:** India values represent Cost to Company (CTC) from calibrated machine learning benchmarks across tech metros, not MOSPI PLFS government surveys.

---

## K. DEFECT REGISTER

| Defect ID | Severity | Evidence | User Impact | Release Blocking? | Recommended Next Action |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **DEF-3B15-01** | **Medium** | Vercel Platform API confirms `jobintel-staging` alias points to `dpl_FnGQsqsfU58WPbEPtLUQZes187jr` (commit `1f82f49`, Sprint 2C.3.4). | Staging frontend does not show Sprint 3A OccupationsPage or Sprint 3B.1 Salary Tab 4. | **Yes (for full-stack staging review)** | Link GitHub webhook to `jobintel-staging` or redeploy `jobintel-staging` to `5897413`. |
| **DEF-3B15-02** | **Low** | Render does not emit Git commit SHA in public HTTP response headers; `RENDER_API_KEY` unset. | Cannot verify Render Git commit via public headers alone (verified via payload SHA-256). | **No** | Add `COMMIT_SHA` to backend `/health` or configure `RENDER_API_KEY` for CI. |

---

## L. FINAL RECOMMENDATION

The backend staging environment is fully operational with complete data integrity and zero production leakage. However, because the Vercel staging alias `https://jobintel-staging.vercel.app` is currently pinned to commit `1f82f49` (Sprint 2C.3.4) rather than `5897413` (Sprint 3B.1.2), the new Sprint 3 frontend features are not observable on that alias.

**Sprint 3B.2 Authorization Recommendation:** **HOLD**  
*Hold until the staging frontend deployment on Vercel is updated to commit `5897413` so that full-stack visual sign-off can occur.*
