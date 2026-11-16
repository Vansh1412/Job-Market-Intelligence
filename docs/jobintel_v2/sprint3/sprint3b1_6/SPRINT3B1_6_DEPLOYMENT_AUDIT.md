# JOBINTEL 2.0 — SPRINT 3B.1.6
## CONTROLLED VERCEL STAGING FRONTEND DEPLOYMENT & INTEGRATION AUDIT REPORT

**Document ID:** `JOBINTEL-V2-SPRINT3B1-6-DEPLOYMENT-AUDIT`  
**Execution Date:** 2026-11-16  
**Auditor / Roles:** Principal Deployment Engineer, Cloud Infrastructure Auditor, QA & Browser Verification Lead  
**Branch:** `staging/sprint2c3`  
**Target Source Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Staging Frontend Project:** `jobintel-staging` (`prj_Og513XzDt3k6UygBsL0KUkXD89jk`)  
**Staging Frontend Alias:** `https://jobintel-staging.vercel.app`  
**New Deployment URL:** `https://jobintel-staging-5zch5osg1-vansh1412s-projects.vercel.app`  
**New Deployment ID:** `dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb`  
**Staging Backend URL:** `https://jobintel-backend-staging.onrender.com`  
**Production Frontend URL:** `https://job-market-intelligence-dusky.vercel.app`  
**Production Backend URL:** `https://job-market-intelligence-6ral.onrender.com`  

---

## A. EXECUTIVE SUMMARY

Sprint 3B.1.6 successfully resolved the staging frontend staleness defect identified in Sprint 3B.1.5 (**DEF-3B15-01**). A controlled manual deployment of the verified frontend implementation was executed from commit `58974134e56b4c3ec6b6119b7b4739e9cce857f3` directly to Vercel project `jobintel-staging`, strictly adhering to all production isolation and non-mutation rules:

1. **Deployment Execution:** Deployed to `jobintel-staging` (`prj_Og513XzDt3k6UygBsL0KUkXD89jk`) as deployment `dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb` with `--build-env VITE_API_BASE_URL="https://jobintel-backend-staging.onrender.com"` without using `--prod`.
2. **Alias Promotion:** Explicitly aliased `jobintel-staging.vercel.app` to the new deployment URL (`https://jobintel-staging-5zch5osg1-vansh1412s-projects.vercel.app`).
3. **Platform-Reported Git Provenance:** The Vercel Platform API metadata explicitly records `githubCommitSha: 58974134e56b4c3ec6b6119b7b4739e9cce857f3` and `githubCommitRef: staging/sprint2c3`.
4. **Browser Integration Verification:** Full headless Chromium test suite verified that `/occupations` renders the new Global Occupation Intelligence suite with all 4 tabs, including Cross-Market Salary Intelligence.
5. **Salary Feature Data Integrity:** Singapore displays $90,000 SGD median with P10/P90 as `"N/A"` (never `$0`); Australia displays $121,500 AUD with P10/P90 as `"N/A"`; India displays ₹12.00L CTC labeled `MODEL_PREDICTION`; UK displays fail-closed governance withholding banner (`UK_DATA_NOT_PUBLISHED`).
6. **Network Isolation:** 100% staging-only traffic. Exactly **0** requests targeted the production backend (`job-market-intelligence-6ral.onrender.com`) or production frontend (`job-market-intelligence-dusky.vercel.app`).
7. **Production Safety:** Production master (`198b79d`) and live production infrastructure remain completely untouched.

**Final Verdict:** **`PASS — STAGING FRONTEND DEPLOYMENT VERIFIED`**

---

## B. PRE-DEPLOYMENT BASELINE CONFIRMATION

Inspection executed via read-only Git commands before deployment:

| Field | Value | Verification Status |
| :--- | :--- | :---: |
| **Local Branch** | `staging/sprint2c3` | **PASS** |
| **Local HEAD SHA** | `58974134e56b4c3ec6b6119b7b4739e9cce857f3` | **PASS** |
| **Remote Staging SHA** | `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (`origin/staging/sprint2c3`) | **PASS** |
| **Production Master SHA** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`origin/master`) | **PASS** |
| **Working Tree Status** | Clean (only untracked markdown audit reports present) | **PASS** |
| **Staging vs Master Delta** | 12 commits ahead, 0 behind | **PASS** |

---

## C. VERCEL PROJECT IDENTITY

Inspection of Vercel project configuration via CLI and platform API:

| Parameter | Configured Value | Verification Source |
| :--- | :--- | :--- |
| **Project Name** | `jobintel-staging` | Vercel Project API / `vercel project ls` |
| **Project ID** | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | Vercel Project API |
| **Project Owner** | `vansh1412s-projects` | Vercel Project API |
| **Framework Preset** | `vite` | Vercel Project Settings |
| **Frontend Directory** | `frontend` | Local Git Repository |
| **Build Machine** | 2 vCPU, 8192 MiB RAM | Vercel Assigned Deployment Specs |
| **Assigned Staging Alias** | `jobintel-staging.vercel.app` | Vercel Alias Registry |
| **Production Alias (Separate)** | `job-market-intelligence-dusky.vercel.app` (Untouched) | Vercel Alias Registry |

---

## D. DEPLOYMENT PROVENANCE

The provenance chain establishes strict traceability from local source to live staging URL:

1. **Locally Verified Source Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (`staging/sprint2c3`).
2. **Deployment Invocation:**
   ```bash
   npx vercel deploy frontend --project jobintel-staging --build-env VITE_API_BASE_URL="https://jobintel-backend-staging.onrender.com" --yes
   ```
   *Execution Mode: Preview deployment (NO `--prod` flag).*
3. **Deployment ID Returned:** `dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb`.
4. **Vercel Platform-Reported Metadata (API Verified):**
   - `githubCommitSha`: `58974134e56b4c3ec6b6119b7b4739e9cce857f3`
   - `githubCommitRef`: `staging/sprint2c3`
   - `githubCommitMessage`: `fix(salary): remediate cross-market salary data integrity, provenance, and methodology (Sprint 3B.1.2)`
   - `githubCommitAuthor`: `Vansh14125` (`chopravansh1412@gmail.com`)
   - `gitRootDirectory`: `frontend`
   - `actor`: `antigravity`
   - `readyState`: `READY`
5. **Explicit Alias Association:**
   ```bash
   npx vercel alias set jobintel-staging-5zch5osg1-vansh1412s-projects.vercel.app jobintel-staging.vercel.app
   ```
   *Status: `Success! https://jobintel-staging.vercel.app now points to jobintel-staging-5zch5osg1-vansh1412s-projects.vercel.app`.*

---

## E. BUILD EVIDENCE

- **Node.js Runtime:** `v24.14.0`
- **npm Package Manager:** `11.9.0`
- **Build Engine:** `tsc -b && vite build` (Vite 8.3.3)
- **Local Pre-Deployment Build:** 2,892 modules transformed, 0 errors, duration 396ms.
- **Remote Vercel Build:** Succeeded in 14s.
- **Bundle File Output:**
  - `dist/index.html` (1.49 kB)
  - `dist/assets/index-ghKHOxN1.css` (5.12 kB)
  - `dist/assets/index-Bi5ktUQS.js` (323.85 kB) — *New build bundle*
  - `dist/assets/vendor-C9EEoyVf.js` (207.23 kB)
  - `dist/assets/recharts-kC6ixw-D.js` (374.34 kB)
  - `dist/assets/icons-CG0klYij.js` (20.57 kB)
- **Zero Build Warnings or Errors.**

---

## F. REAL BROWSER ROUTE VERIFICATION (PUPPETEER + CHROMIUM)

Tested directly against `https://jobintel-staging.vercel.app` using desktop viewport (`1400x900`):

| Route Tested | HTTP Status | React Mounted | Rendered View / Heading | Direct Navigation | Refresh | Status |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| `/` | 200 | True | HomePage (`Understand your worth`) | PASS | PASS | **PASS** |
| `/occupations` | 200 | True | Occupations Explorer (`Global Occupation Intelligence`) | PASS | PASS | **PASS** |
| `/salary` | 200 | True | PredictorPage (`Compensation Predictor`) | PASS | PASS | **PASS** |
| `/cross-market` | 200 | True | CrossMarketPage (`USA vs India`) | PASS | PASS | **PASS** |

**Zero fatal JavaScript exceptions or page crashes (`pageErrors: 0`).**

---

## G. FEATURE AND UI DATA INTEGRITY VERIFICATION

### 1. Occupations Explorer (`/occupations`)
- Verified live rendering of top application header including the new **`Occupations`** navigation link with globe icon.
- Renders the 4 primary sub-tabs:
  1. `Cross-Market Concordance`
  2. `National Taxonomy Explorer`
  3. `Canonical Career Concepts`
  4. `Cross-Market Salary Intelligence`
- Default view loads 8 national classification systems (US SOC, UK SOC, AU OSCA, SG SSOC, IN NCO, ISCO-08, ESCO, O*NET).

### 2. Cross-Market Salary Intelligence Tab (Tab 4)
Verified through visual and DOM text extraction:
- **Benchmark Role Selected:** `Software Developers (US)` (`US_SOC_2018:15-1252`).
- **Singapore (`SG_SSOC_2024:25121`):**
  - Displays $90,000 SGD median (`NOMINAL USD: $66,914.46 USD`, `PPP INT$: $107,142.84 Int$`).
  - Percentiles: `p10: N/A`, `p50 (Med): 90,000`, `p90: N/A`. *(Nulls explicitly rendered as `"N/A"`, never `$0`).*
  - Quality Flag: `OFFICIALLY_DERIVED`.
  - Caveats: Discloses MOM 12× monthly gross wage, excludes bonuses & AWS, P10/P90 unpublished.
- **Australia (`AU_OSCA_2024:261313`):**
  - Displays $121,500 AUD median (`NOMINAL USD: $79,934.24 USD`, `PPP INT$: $85,563.34 Int$`).
  - Percentiles: `p10: N/A`, `p50 (Med): 121,500`, `p90: N/A`. *(Nulls explicitly rendered as `"N/A"`, never `$0`).*
  - Quality Flag: `OFFICIALLY_DERIVED`.
  - Caveats: Discloses 52× weekly ordinary time wage and 4-digit unit group inheritance.
- **India (`IN_NCO_2015:2512.0100`):**
  - Displays ₹12.00L INR CTC median.
  - Quality Flag: `MODEL_PREDICTION`.
  - Caveats: Discloses CTC breakdown (basic, allowances, 12% PF, 4.81% gratuity) from predictive ML model across tech metros.
- **United Kingdom (`UK_SOC_2020:2134`):**
  - Displays: `🔒 Data Withheld by Governance Gate: UK ASHE salary publication is withheld by governance policy gate (fail-closed HTTP 503 policy).`
  - Zero wage numbers or percentiles leaked.
- **Methodology & Decoupling Notice:**
  - Distinct side-by-side columns for `NOMINAL USD MEDIAN` (blue) and `PPP INT$ MEDIAN` (green).
  - Explicit decoupling warning rendered: *"Nominal reflects global exchange value; PPP reflects domestic consumption price equivalence... MUST NEVER be averaged or blended."*

---

## H. NETWORK ISOLATION AND BACKEND INTEGRATION

All network requests during the browser verification session were captured and categorized:

| Traffic Category | Request Count | Target Domain | Isolation Verdict |
| :--- | :---: | :--- | :---: |
| **Staging Frontend Assets** | 114 | `https://jobintel-staging.vercel.app` | **PASS** |
| **Staging Backend APIs** | 10 | `https://jobintel-backend-staging.onrender.com` | **PASS** |
| **Third-Party Static Assets** | 64 | `fonts.googleapis.com`, `fonts.gstatic.com` | **PASS** |
| **Production Backend Requests** | **0** | `https://job-market-intelligence-6ral.onrender.com` | **PERFECT ISOLATION** |
| **Production Frontend Requests** | **0** | `https://job-market-intelligence-dusky.vercel.app` | **PERFECT ISOLATION** |
| **Failed Critical Requests** | 0 | None (All 200 OK or 304 Not Modified) | **PASS** |

### Staging Backend Endpoints Invoked by Browser:
1. `GET /v1/occupations/classifications` (HTTP 200 OK)
2. `GET /v1/occupations/canonical` (HTTP 200 OK)
3. `GET /v1/occupations/coverage` (HTTP 200 OK)
4. `GET /v1/occupations/classifications/UK_SOC_2020/occupations?page=1&page_size=50` (HTTP 200 OK)
5. `GET /v1/occupations/compare?source_occupation_id=UK_SOC_2020%3A2134` (HTTP 200 OK)
6. `GET /v1/salary/rates` (HTTP 200 OK)
7. `GET /v1/salary/sources?active_only=true` (HTTP 200 OK)
8. `GET /v1/salary/compare?occupation_id=US_SOC_2018%3A15-1252` (HTTP 200 OK)
9. `GET /v1/salary/occupations/US_SOC_2018%3A15-1252` (HTTP 200 OK)
10. `GET /v1/salary/convert?amount=1200000&from_currency=INR` (HTTP 200 OK)

---

## I. REGRESSION TEST SUITE OUTCOMES

All local test suites executed on `staging/sprint2c3` (`5897413`):

1. **Python Test Suite (`python -m pytest tests/ -q`):**
   - **333 passed** in 26.54s.
2. **Golden Predictions & Parity Suite:**
   - `python -m pytest tests/test_golden_predictions.py tests/test_prediction_parity.py -q`
   - **15 passed** in 4.73s.
3. **Frontend Vitest Suite (`npm --prefix frontend test -- --run`):**
   - **9 passed** across 3 test files in 703ms.
4. **Production Build Typecheck (`npm --prefix frontend run build`):**
   - Clean compilation, 0 TypeScript errors.

---

## J. PRODUCTION SAFETY BASELINE AUDIT

1. **Production Backend:** `https://job-market-intelligence-6ral.onrender.com`
   - `/health`: HTTP 200 OK (`version: 2.0.0`, status: `healthy`).
   - `/v1/salary/sources`: **HTTP 404 Not Found** (Sprint 3B salary endpoints remain completely absent from production).
2. **Production Frontend:** `https://job-market-intelligence-dusky.vercel.app`
   - Responding HTTP 200 OK.
   - Deployed from master baseline 38 days ago; zero alias modifications.
3. **Git Master Baseline:** `origin/master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` remains untouched.

---

## K. KNOWN DATA LIMITATIONS (RETAINED)

1. **Render Public Commit Header:** Render's managed reverse proxy does not emit commit hashes in public HTTP response headers (`RENDER_DEPLOYMENT_IDENTITY_UNVERIFIED` by HTTP header; verified via SHA-256 payload checksums).
2. **Singapore Annualized Wage Rate:** MOM OWS gross monthly wage annualized ($7,500 × 12 = $90,000 SGD) is an annualized rate, not total annual cash compensation. Bonuses and AWS are excluded; P10/P90 are unpublished.
3. **Australia Unit Group Inheritance:** Detailed OSCA occupations inherit 4-digit ANZSCO unit group salary parameters; P10/P90 are unpublished.
4. **UK Data Withheld:** UK ASHE 2024 data remains gated (`UK_DATA_NOT_PUBLISHED`, HTTP 503 fail-closed).
5. **India CTC Model Prediction:** India figures represent Cost to Company (CTC) from calibrated machine learning benchmarks across tech metros, not MOSPI PLFS government surveys.
6. **BLS URL Dynamism:** The US BLS `/oes/current/` URL is an active reference link, not an immutable May 2023 snapshot.

---

## L. DEFECT REGISTER STATUS

| Defect ID | Description | Severity | Status in Sprint 3B.1.6 |
| :--- | :--- | :---: | :---: |
| **DEF-3B15-01** | Vercel staging alias pointed to stale commit `1f82f49` (Sprint 2C.3.4), missing Sprint 3 UI. | **Medium** | **CLOSED / RESOLVED** (Deployed `dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb` from `5897413` and updated alias). |
| **DEF-3B15-02** | Render commit SHA not emitted in public HTTP response headers. | **Low** | **DOCUMENTED LIMITATION** (Platform architecture constraint; verified via SHA-256 model registry). |

---

## M. FINAL SIGN-OFF & ACCEPTANCE SUMMARY

| Acceptance Criterion | Description | Result |
| :--- | :--- | :---: |
| **AC-01** | Correct repository and staging branch verified | **PASS** |
| **AC-02** | Intended source commit verified | **PASS** |
| **AC-03** | Correct Vercel project ID verified (`prj_Og513XzDt3k6UygBsL0KUkXD89jk`) | **PASS** |
| **AC-04** | Frontend build passes cleanly | **PASS** |
| **AC-05** | Staging backend URL configured (`jobintel-backend-staging.onrender.com`) | **PASS** |
| **AC-06** | New staging deployment reaches READY (`dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb`) | **PASS** |
| **AC-07** | Staging alias points to new deployment | **PASS** |
| **AC-08** | Occupations Explorer renders correctly | **PASS** |
| **AC-09** | Cross-Market Salary Intelligence renders correctly | **PASS** |
| **AC-10** | Direct route navigation and refresh work | **PASS** |
| **AC-11** | Browser network isolation passes (0 production requests) | **PASS** |
| **AC-12** | No UK salary leakage (fail-closed HTTP 503 banner rendered) | **PASS** |
| **AC-13** | Backend integration checks pass (10/10 endpoints return 200 OK) | **PASS** |
| **AC-14** | Relevant regression tests pass (333 Python + 15 Parity + 9 Vitest) | **PASS** |
| **AC-15** | Production remains unchanged | **PASS** |
| **AC-16** | Deployment audit report completed | **PASS** |

**Final Recommendation:** **`APPROVE FOR SPRINT 3B.2`**  
All frontend deployment, backend integration, and browser evidence gaps are closed. The staging environment is qualified for cross-market salary intelligence feature expansion.
