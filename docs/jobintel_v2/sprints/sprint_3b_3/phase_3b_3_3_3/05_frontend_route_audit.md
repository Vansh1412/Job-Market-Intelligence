# SPRINT 3B.3.3.3.3: FRONTEND ROUTE COVERAGE & E2E BROWSER AUDIT

**Audit Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Target Staging Frontend:** `https://jobintel-staging.vercel.app`  
**Verification Tooling:** Headless Google Chrome (`1440x900`, `puppeteer-core`)  
**Audit Mode:** STRICTLY READ-ONLY  
**Verification Verdict:** **CONDITIONAL PASS — EMPLOYER ROUTE OMISSION DISCLOSED**

---

## 1. COMPREHENSIVE PRODUCT ROUTE AUDIT MATRIX

An automated headless browser audit was conducted against the live staging deployment at `https://jobintel-staging.vercel.app`. Every core product area was inspected for HTTP status, route resolution, heading visibility, console errors, and network isolation.

| # | Product Area | Tested Path | Resolved URL | HTTP Status | Visual & Functional Observations | Route Status |
| :-: | :--- | :--- | :--- | :-: | :--- | :---: |
| **1** | **Landing Page** | `/` | `https://jobintel-staging.vercel.app/` | **200 OK** | Hero headline: "Know what your skills could be worth." Market selectors for USA and India rendered. | **PASS** |
| **2** | **Salary Intelligence** | `/salary` | `https://jobintel-staging.vercel.app/salary` | **200 OK** | Interactive predictor form rendered. Empirical dispersion intervals and holdout MAE disclaimers verified. | **PASS** |
| **3** | **Global Market Explorer** | `/explore` | `https://jobintel-staging.vercel.app/explore` | **200 OK** | Market summary dashboard loaded (3,244 chars DOM text). Interactive role/seniority/city filters and salary charts active. | **PASS** |
| **4** | **Occupations Explorer** | `/occupations` | `https://jobintel-staging.vercel.app/occupations` | **200 OK** | Global occupation taxonomy browser rendered. SOC concordance records and cross-market equivalents displayed. | **PASS** |
| **5** | **Demand Intelligence** | `/demand` | `https://jobintel-staging.vercel.app/demand` | **200 OK** | Labour demand indicator cards rendered. Selecting UK triggers active publication gate notice (`UK_DEMAND_DATA_NOT_PUBLISHED`). | **PASS** |
| **6** | **Employer Intelligence** | `/employers` | `https://jobintel-staging.vercel.app/` | **200 OK (Fallback)** | **NO STANDALONE ROUTE.** Request cleanly falls back to `/` via `App.tsx` routing fallback. Backend API is live; frontend UI page is not yet implemented. | **DISCLOSED OMISSION** |
| **7** | **Skill Intelligence** | `/skills` | `https://jobintel-staging.vercel.app/skills` | **200 OK** | Skills table rendered with non-zero frequencies. Correct general population denominator ($N=335,995$) verified. | **PASS** |
| **8** | **Cross-Market Comparison**| `/cross-market` | `https://jobintel-staging.vercel.app/cross-market` | **200 OK** | Bilateral comparison dashboard rendered comparing USA ($ USD) vs India (₹ LPA) metrics. | **PASS** |
| *—* | *Archetypes (Supplementary)* | `/archetypes` | `https://jobintel-staging.vercel.app/archetypes` | **200 OK** | Clustering dashboard rendered displaying 7 discovered USA skill patterns. | **PASS** |
| *—* | *Methodology (Supplementary)* | `/how-it-works`| `https://jobintel-staging.vercel.app/how-it-works`| **200 OK** | Full methodology and pipeline explanation rendered. | **PASS** |

---

## 2. DETAILED ANALYSIS OF PRODUCT AREA 6: EMPLOYER INTELLIGENCE

### 2.1 Backend vs Frontend Discrepancy
- **Backend Service State:** The Employer Intelligence REST API (`/api/v1/employers`, `/api/v1/employers/resolve`, `/api/v1/employers/{id}`) is fully implemented, hardened, and passes 32 adversarial test cases covering multi-jurisdiction statutory ID verification and duplicate collision rejection.
- **Frontend Routing State:** In `frontend/src/App.tsx`, the routing map is defined as:
  ```typescript
  const ROUTE_MAP: Record<string, NavigationPage> = {
    '/': 'home',
    '/salary': 'calculator',
    '/calculator': 'calculator',
    '/predictor': 'calculator',
    '/explore': 'explore',
    '/skills': 'skills',
    '/archetypes': 'archetypes',
    '/cross-market': 'comparison',
    '/comparison': 'comparison',
    '/occupations': 'occupations',
    '/demand': 'demand',
    '/how-it-works': 'howitworks',
    '/howitworks': 'howitworks',
  };
  ```
- **Fallback Behavior:** Because `/employers` is not mapped in `ROUTE_MAP`, `getPageFromLocation()` defaults to `'home'`, and `window.history.replaceState` safely normalizes the browser URL to `/`.
- **Classification:** This omission does not compromise platform stability or cause unhandled runtime exceptions. It represents a planned frontend UI feature scheduled for Sprint 3B.3.3.4.

---

## 3. NETWORK SECURITY & CONSOLE AUDIT

During the headless browser traversal across all 10 frontend routes:
- **Total Network Requests Intercepted:** 72 requests
- **Requests to Staging Backend (`jobintel-backend-staging.onrender.com`):** 48 requests
- **Requests to Production Backend (`job-market-intelligence-6ral.onrender.com`):** **0 (ZERO LEAKS)**
- **Requests to Production Frontend (`job-market-intelligence-dusky.vercel.app`):** **0 (ZERO LEAKS)**
- **Unhandled Page Errors:** 0
- **Console Errors:** 0

### 3.1 Network Isolation Verification
Every API request issued from the staging UI explicitly targeted `https://jobintel-backend-staging.onrender.com`, confirming that `VITE_API_BASE_URL` is correctly configured in the staging Vercel environment.
