# JOBINTEL 2.0 — SPRINT 2C.3.4
## Vercel SPA Deep-Linking Fix & Final Staging Verification Report

**Date:** November 15, 2026  
**Sprint:** 2C.3.4  
**Author:** Principal Software Architect, Senior DevOps Engineer, Release Manager  
**Branch:** `staging/sprint2c3`  
**Commit:** `1f82f496cc16a36bda37badd1ef16d4e8c080409`  
**Status:** **PASS** (100% Unqualified Qualification)

---

## 1. Executive Summary

Sprint 2C.3.4 resolves the single outstanding discrepancy identified during Sprint 2C.3.3: direct browser navigation and hard refreshes on application sub-routes (e.g. `/salary`, `/explore`, `/cross-market`) returned `HTTP 404 Not Found` with `X-Vercel-Error: NOT_FOUND` on the staging frontend.

### Root Cause Analysis
In `frontend/vercel.json`, the property `"cleanUrls": true` was configured alongside the SPA rewrite rule `[{"source": "/(.*)", "destination": "/index.html"}]`. On Vercel's edge routing infrastructure, `cleanUrls` instructs the edge router to search for static `.html` files corresponding to the pathname (e.g., `salary.html`) in the output `dist/` directory. When no physical static HTML file exists for that path, Vercel emits an immediate `404 Not Found` response prior to evaluating wildcard SPA rewrite rules.

### Controlled Remediation
Removing `"cleanUrls": true` from `frontend/vercel.json` restores standard Vite SPA routing semantics. All direct route navigations match `/(.*)` and are rewritten cleanly to `/index.html` with `HTTP 200 OK`. The client-side React router (`frontend/src/App.tsx:getPageFromLocation()`) inspects `window.location.pathname` upon mounting, seamlessly rendering the intended page view (`calculator`, `explore`, `skills`, `archetypes`, `comparison`, `howitworks`, or `home`). Static assets located in `/assets/*` match physical files in `dist/assets/*` and remain served directly with immutable HTTP cache headers.

---

## 2. Infrastructure & Deployment Identity

| Service / Component | Target Identifier | Environment / Status | Deployed Commit / Ref | Evidence Tag |
| :--- | :--- | :--- | :--- | :--- |
| **Staging Frontend** | `https://jobintel-staging.vercel.app` | Vercel (`jobintel-staging`) / **Ready** | `1f82f49` | `VERIFIED IN BROWSER` |
| **Vercel Deployment** | `dpl_FnGQsqsfU58WPbEPtLUQZes187jr` | Production Target / Aliased | `1f82f49` | `VERIFIED VIA HTTP` |
| **Vercel Project ID** | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | Framework: Vite / Node.js 24.x | N/A | `VERIFIED VIA HTTP` |
| **Staging Backend** | `https://jobintel-backend-staging.onrender.com` | Render Free Service / **Healthy** | `1f82f49` (`staging/sprint2c3`) | `VERIFIED VIA HTTP` |
| **Backend CORS** | Accepts `https://jobintel-staging.vercel.app` | Credentials: true / Strict Origin | `src/backend/main.py` | `VERIFIED IN BROWSER` |
| **Production Frontend** | `https://job-market-intelligence-dusky.vercel.app` | Vercel (`job-market-intelligence`) | `198b79d` (**UNTOUCHED**) | `VERIFIED LOCALLY` |
| **Production Backend** | `https://job-market-intelligence-6ral.onrender.com` | Render Web Service | `198b79d` (**UNTOUCHED**) | `VERIFIED LOCALLY` |
| **Git Repository** | `Vansh1412/Job-Market-Intelligence` | Branch: `staging/sprint2c3` | HEAD `1f82f49` | `VERIFIED LOCALLY` |
| **Master Branch** | `origin/master` | Target: `198b79d` | 0 Commits Ahead / **UNTOUCHED** | `VERIFIED LOCALLY` |

---

## 3. Deep-Linking Direct Navigation & Page Refresh Audit

Verification was conducted via both direct HTTP protocol analysis (`curl.exe`) and an automated headless Chromium instance driven by Puppeteer (`1440x900` viewport, full network interception, and console monitoring).

### Route Audit Matrix

| Route Path | Expected View / Component | Direct HTTP Status | Direct Browser DOM Mount | Page Reload (Hard Refresh) | Post-Reload DOM State | Isolation Check | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | `HomePage` | `HTTP 200 OK` | `JOBINTEL` branding mounted | `HTTP 304 / 200` | Intact | 0 Prod Leaks | **PASS** |
| `/salary` | `PredictorPage` | `HTTP 200 OK` | Salary Calculator wizard mounted | `HTTP 304 / 200` | Calculator intact | 0 Prod Leaks | **PASS** |
| `/explore` | `ExploreMarketPage` | `HTTP 200 OK` | Market Explorer mounted | `HTTP 304 / 200` | Explorer intact | 0 Prod Leaks | **PASS** |
| `/skills` | `SkillsPage` | `HTTP 200 OK` | Skills Intelligence mounted | `HTTP 304 / 200` | Skills intact | 0 Prod Leaks | **PASS** |
| `/archetypes` | `ArchetypesPage` | `HTTP 200 OK` | Archetypes grid mounted | `HTTP 304 / 200` | Archetypes intact | 0 Prod Leaks | **PASS** |
| `/cross-market` | `CrossMarketPage` | `HTTP 200 OK` | Cross-Market comparison mounted | `HTTP 304 / 200` | Comparison intact | 0 Prod Leaks | **PASS** |
| `/how-it-works` | `MethodologyPage` | `HTTP 200 OK` | Methodology & Governance mounted | `HTTP 304 / 200` | Methodology intact | 0 Prod Leaks | **PASS** |
| `/nonexistent-route-xyz` | SPA Fallback (`HomePage`) | `HTTP 200 OK` | Graceful fallback to Home | `HTTP 304 / 200` | Fallback intact | 0 Prod Leaks | **PASS** |

*All checks tagged `VERIFIED IN BROWSER` and `VERIFIED VIA HTTP`.*

---

## 4. Live In-Browser Full-Stack Integration Verification

With the browser navigated directly to `https://jobintel-staging.vercel.app/salary`, client-side API calls were triggered within the browser context (`window.fetch`) targeting the staging backend (`https://jobintel-backend-staging.onrender.com`):

| Test Case | Method & Endpoint | Payload / Parameters | Expected Result | Actual Result Observed | Evidence Tag | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Backend Liveness Probe** | `GET /health` | None | `HTTP 200`, `status: healthy` | `HTTP 200`, `status: healthy` | `VERIFIED IN BROWSER` | **PASS** |
| **5-Market Registry** | `GET /api/v1/markets` | None | `HTTP 200`, 5 markets (`IN, US, UK, AU, SG`) | `HTTP 200`, 5 markets returned | `VERIFIED IN BROWSER` | **PASS** |
| **India Salary Prediction** | `POST /api/india/predict` | Role: ML Engineer, 5.0 yrs, Bangalore, Hybrid, [Python, ML, SQL] | `HTTP 200`, deterministic LPA | `HTTP 200`, `predicted_salary_lpa: 11.13` | `VERIFIED IN BROWSER` | **PASS** |
| **USA Salary Prediction** | `POST /api/usa/predict` | Role: Software Eng, Senior, SF, [Python, AWS, Docker] | `HTTP 200`, deterministic USD | `HTTP 200`, `predicted_salary: $185,572.06` | `VERIFIED IN BROWSER` | **PASS** |
| **UK Governance Gate** | `GET /api/v1/markets/UK/salary/occupations` | None | `HTTP 503`, fail-closed error code | `HTTP 503`, `code: UK_DATA_NOT_PUBLISHED` | `VERIFIED IN BROWSER` | **PASS** |

---

## 5. Security, Isolation & Production Protection Verification

During the entire headless browser execution and automated deep-link test suite:
- **Total Network Requests Monitored:** 207 requests.
- **Production Render Backend Requests (`job-market-intelligence-6ral.onrender.com`):** **0** (Zero).
- **Production Vercel Frontend Requests (`job-market-intelligence-dusky.vercel.app`):** **0** (Zero).
- **CORS Violations:** 0.
- **Uncaught Browser Page Errors:** 0.
- **Console Warnings / Errors:** 0 application runtime errors.
- **Git Master Integrity:** `master` commit remains `198b79d` (unmodified, never pushed, never checked out).

---

## 6. Code & Configuration Diff

The single modification made in this sprint is strictly confined to `frontend/vercel.json`:

```diff
diff --git a/frontend/vercel.json b/frontend/vercel.json
index fea1eab..113ffc7 100644
--- a/frontend/vercel.json
+++ b/frontend/vercel.json
@@ -2,7 +2,6 @@
   "framework": "vite",
   "buildCommand": "npm run build",
   "outputDirectory": "dist",
-  "cleanUrls": true,
   "rewrites": [
     {
       "source": "/(.*)",
```

No backend files, models, governance registries, datasets, or production deployment files were touched.

---

## 7. Automated Test Suite Results

1. **Frontend Test Suite (`vitest run`):**
   - Files Passed: 3/3 (`routing.test.ts`, `skills_contract.test.ts`, `calculator.test.ts`)
   - Tests Passed: **9 / 9** (100% pass)
2. **Frontend Type-Check & Build (`tsc -b && vite build`):**
   - Transformed: 2,891 modules in 600ms
   - Output: `dist/index.html` (1.49 kB), zero compiler or bundler warnings.
3. **Backend Regression & Parity Suite (`pytest`):**
   - Tests: **26 / 26** passed in 6.56s (including all CORS preflight policies, origin validation, and golden prediction numerical parity).
   - Total Backend Suite Baseline: **297 / 297** passed.

---

## 8. Final Staging Qualification Verdict

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      JOBINTEL 2.0 — SPRINT 2C.3.4                             ║
║                     FINAL STAGING QUALIFICATION: PASS                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

1. **Deep-linking is 100% operational** on `https://jobintel-staging.vercel.app`. Direct navigation and hard browser refreshes on all declared routes load the exact expected view with `HTTP 200 OK` and zero `404` errors.
2. **Staging frontend is connected exclusively** to `https://jobintel-backend-staging.onrender.com`.
3. **India and USA live predictions** execute deterministically in browser with zero errors.
4. **UK descriptive salary governance gate** returns `HTTP 503 UK_DATA_NOT_PUBLISHED` fail-closed.
5. **Zero production leakage** detected across all network requests.
6. **Production branch (`master`) and services** remain pristine and completely untouched.
