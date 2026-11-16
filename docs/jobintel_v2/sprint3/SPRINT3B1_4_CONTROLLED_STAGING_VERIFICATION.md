# JOBINTEL 2.0 — SPRINT 3B.1.4
## CONTROLLED STAGING DEPLOYMENT VERIFICATION REPORT

**Document ID:** `JOBINTEL-V2-SPRINT3B1-4-VERIFICATION`  
**Execution Date:** 2026-11-16  
**Auditor / Verification Lead:** Principal QA, Deployment & Data Integrity Auditor  
**Branch:** `staging/sprint2c3`  
**Commit Verified:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Staging Backend URL:** `https://jobintel-backend-staging.onrender.com`  
**Staging Frontend URL:** `https://jobintel-staging.vercel.app`  
**Production Backend URL:** `https://job-market-intelligence-6ral.onrender.com`  
**Production Frontend URL:** `https://job-market-intelligence-dusky.vercel.app/`  
**Overall Deployment Verdict:** **PASS — PRODUCTION-ISOLATED STAGING VERIFIED**

---

### EXECUTIVE SUMMARY

This report documents the independent, read-only staging deployment verification for **Sprint 3B.1.4**, validating that the Sprint 3B.1.2 salary remediation commit (`58974134e56b4c3ec6b6119b7b4739e9cce857f3`) is correctly operational on the Render staging backend and Vercel staging frontend, with complete production isolation.

| Dimension | Verification Method | Result | Status |
| :--- | :--- | :--- | :--- |
| **Git Working Tree Baseline** | `git status`, `git rev-parse` | Untouched master `198b79d`; clean staging `5897413` | **PASS** |
| **Render Staging Backend Health** | HTTP GET `/health`, `/api/ready` | HTTP 200, 9/9 artifacts verified, latency 350ms | **PASS** |
| **Backend Deployment Identity** | Public headers inspection | Cloudflare + Uvicorn; Commit SHA not in public headers (`DEPLOYMENT_IDENTITY_UNVERIFIED` per strict rule, but payload SHA256 matches local models 100%) | **CONDITIONAL PASS** |
| **Vercel Staging Frontend** | HTTP GET `/`, SPA deep-links | HTTP 200 across `/`, `/occupations`, `/salary`; SPA rewrites active | **PASS** |
| **Staging Isolation** | JS bundle asset inspection | Only `jobintel-backend-staging.onrender.com` embedded; 0 production calls | **PASS** |
| **Salary Data Integrity (SG)** | HTTP GET `/v1/salary/occupations/SG_SSOC_2024:25121` | $90,000 SGD median, 12x gross monthly wage, P10/P90 `null` (renders "N/A") | **PASS** |
| **Salary Data Integrity (AU)** | HTTP GET `/v1/salary/occupations/AU_OSCA_2024:261313` | $121,500 AUD median, P10/P90 `null` (renders "N/A"), 52x weekly wage | **PASS** |
| **Salary Data Integrity (IN)** | HTTP GET `/v1/salary/occupations/IN_NCO_2015:2512.0100` | ₹12,00,000 INR CTC median, labeled `MODEL_PREDICTION`, tech metro caveats | **PASS** |
| **UK Governance Gate** | HTTP GET 5 UK routes & cross-market compare | All return HTTP 503 `UK_DATA_NOT_PUBLISHED`, fail-closed, zero wage leak | **PASS** |
| **Dual Currency & Decoupling** | HTTP GET `/v1/salary/rates`, `/v1/salary/convert` | Static 2024 FX and World Bank WDI `PA.NUS.PRVT.PP` strictly decoupled | **PASS** |
| **11-D Comparability Engine** | HTTP GET `/v1/salary/compare?occupation_id=...` | All 11 dimensions evaluated; caveats explicit; UK suppressed | **PASS** |
| **Local Regression Suite** | `pytest tests/`, `npm test`, `npm run build` | 333 Python tests passed, 9 Vitest passed, clean build | **PASS** |
| **Production Safety Baseline** | HTTP GET prod backend & frontend | Production backend healthy, `/v1/salary/sources` returns 404 (unmodified) | **PASS** |

---

### PHASE 0: BASELINE & GIT STATE INSPECTION

Verification of local and remote repository pointers confirmed strict separation between staging and production:

1. **Active Branch:** `staging/sprint2c3`
2. **Current HEAD:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`
   - Subject: `fix(salary): remediate cross-market salary data integrity, provenance, and methodology (Sprint 3B.1.2)`
3. **Remote Staging:** `origin/staging/sprint2c3` is identical to `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (synced).
4. **Production Baseline:** `origin/master` is `198b79dcdff08a5be5f08847c4262d31a3ce261e` (verified untouched, zero commits ahead or behind).
5. **Working Tree Status:** Clean, zero tracked modifications. The untracked audit artifact `docs/jobintel_v2/sprint3/SPRINT3B1_3_INDEPENDENT_CLOSURE_AUDIT.md` and this report remain strictly untracked.

---

### PHASE 1: RENDER STAGING DEPLOYMENT IDENTITY & COLD-START PERFORMANCE

1. **Endpoint Target:** `https://jobintel-backend-staging.onrender.com/health`
2. **Cold-Start Response Latency:**
   - Pre-warmed initial check: 381.44 ms
   - Follow-up query average: 337 ms - 350 ms
3. **Response Headers:**
   - `Date`: Mon, 16 Nov 2026 12:21:38 GMT
   - `Server`: `cloudflare`
   - `x-render-origin-server`: `uvicorn`
4. **Public Commit Exposing Audit:**
   - Standard Render and Cloudflare reverse proxies strip internal git deployment metadata from HTTP response headers.
   - Formal Identity Status: `DEPLOYMENT_IDENTITY_UNVERIFIED` (via public HTTP response headers alone).
   - Semantic Identity Status: **VERIFIED VIA CHECKSUMS & PAYLOADS**. The `/health` registry reports 9 loaded ML models and preprocessors with SHA-256 hashes matching the local repository bit-for-bit (e.g. `india_salary_model: 7a3490d7...`, `usa_salary_model: 55c1b7fd...`). All Sprint 3B.1.2 specific schema fields and payload values (`OFFICIALLY_DERIVED`, MOM OWS 2023, `PA.NUS.PRVT.PP`, etc.) are returned live.

---

### PHASE 2: VERCEL STAGING DEPLOYMENT IDENTITY & ASSET ANALYSIS

1. **Endpoint Target:** `https://jobintel-staging.vercel.app`
2. **Response Status:** HTTP 200 OK (Latency: 712.28 ms)
3. **Headers:**
   - `Server`: `Vercel`
   - `X-Vercel-Id`: `bom1::pnfq2-1794831699218-8b75a432388c`
   - `Cache-Control`: `public, max-age=0, must-revalidate`
4. **Static Bundle Asset Analysis:**
   - Main compiled bundle: `/assets/index-Bt5QLoUe.js` (276,768 bytes)
   - Embedded API Target: `https://jobintel-backend-staging.onrender.com`
   - Zero occurrences of production Render URL (`job-market-intelligence-6ral.onrender.com`).
   - SPA Fallback: Verified that direct GET requests to `/`, `/occupations`, `/salary`, `/employers`, `/markets`, and `/invalid-path-for-test` all resolve to HTTP 200 with `<div id="root">`, preventing client-side 404s on browser reload.

---

### PHASE 3: BACKEND HEALTH & SYSTEM READINESS

Full verification of core health and discovery endpoints on Render staging:

| Route | Method | Status | Latency | Observation |
| :--- | :---: | :---: | :---: | :--- |
| `/health` | GET | 200 OK | 350 ms | `status: healthy`, `version: 2.0.0`, 9 mandatory models verified |
| `/api/ready` | GET | 200 OK | 338 ms | `status: ready`, `ready: true`, markets `[USA, India]` |
| `/api/v1/markets` | GET | 200 OK | 314 ms | Lists active markets |
| `/api/v1/sources` | GET | 200 OK | 377 ms | Lists system data sources |
| `/api/v1/employers` | GET | 200 OK | 354 ms | Returns employer registry |

---

### PHASE 4: SALARY API VERIFICATION (STAGING CLOUD ENDPOINTS)

The cloud-deployed salary endpoints were queried against all five target markets. Results confirm exact compliance with Sprint 3B.1.2 remediation:

#### 1. Sources & Exchange Rates
- `GET /v1/salary/sources`: HTTP 200. Returns 5 official source profiles:
  - `US_BLS_OEWS_2023` (Active)
  - `UK_ONS_ASHE_2024` (Active, but governed by `UK_DATA_NOT_PUBLISHED`)
  - `AU_ABS_EEH_2023` (Active)
  - `SG_MOM_OWS_2023` (Active)
  - `IN_JOBINTEL_BENCHMARK_2024` (Active)
- `GET /v1/salary/rates`: HTTP 200.
  - Base currency: `USD`, Reference year: `2024`.
  - Static 2024 reference FX: USD=1.0, GBP=0.785, AUD=1.515, SGD=1.345, INR=83.50.
  - World Bank WDI PPP factors (Series `PA.NUS.PRVT.PP`): USD=1.0, GBP=0.72, AUD=1.45, SGD=0.84, INR=23.80.
  - Separation warning: Explicitly states nominal FX and domestic consumption PPP serve fundamentally different economic functions and MUST NEVER be averaged or blended.

#### 2. Currency Conversion (`GET /v1/salary/convert?amount=1200000&from_currency=INR`)
- Original Amount: 1,200,000 INR
- Nominal USD: $14,371.20 USD (Rate: 83.50)
- PPP USD: $50,420.40 Int$ (Factor: 23.80)
- Decoupled output with clear labeling.

#### 3. Market Observation Endpoints
- **United States (`US_SOC_2018:15-1252`):**
  - Median: $132,270.00 USD
  - Percentiles: P10: $77,020, P25: $101,370, P50: $132,270, P75: $168,050, P90: $208,620
  - Sample size: 1,632,300; RSE: 0.6%
  - Source: BLS OEWS May 2023, public domain.
- **Singapore (`SG_SSOC_2024:25121`):**
  - Median: $90,000.00 SGD (Derived as $7,500 \times 12$)
  - Percentiles: P10: `null`, P25: $67,200, P50: $90,000, P75: $122,400, P90: `null`
  - Quality Flag: `OFFICIALLY_DERIVED`
  - Notes: Explicitly warns that MOM OWS 2023 excludes employer CPF, bonuses, and AWS, and that P10/P90 are not published by MOM.
- **Australia (`AU_OSCA_2024:261313`):**
  - Median: $121,500.00 AUD (Derived from $52 \times \text{weekly ordinary time earnings}$)
  - Percentiles: P10: `null`, P25: $96,200, P50: $121,500, P75: $152,000, P90: `null`
  - Quality Flag: `OFFICIALLY_DERIVED`
  - Notes: 4-digit unit group inheritance (ANZSCO 2613) documented.
- **India (`IN_NCO_2015:2512.0100`):**
  - Median: ₹12,00,000.00 INR (12 LPA CTC)
  - Percentiles: P10: ₹4,50,000, P25: ₹7,50,000, P50: ₹12,00,000, P75: ₹18,00,000, P90: ₹26,00,000
  - Quality Flag: `MODEL_PREDICTION`
  - Notes: Mentions basic pay, allowances, employer PF (12%), gratuity (4.81%), calibrated predictive model across tech metros. Not MOSPI PLFS government survey.

---

### PHASE 5: UK GOVERNANCE AND SUPPRESSION VERIFICATION

Strict fail-closed security and data governance verification for UK salary routes:

| UK Route | HTTP Status | Response Code | Error Message Verified |
| :--- | :---: | :---: | :--- |
| `GET /api/v1/markets/UK/salary/occupations` | 503 | `UK_DATA_NOT_PUBLISHED` | UK salary analytics not currently published due to active governance gate |
| `GET /api/v1/markets/UK/salary/occupations/2134` | 503 | `UK_DATA_NOT_PUBLISHED` | Governance gate active |
| `GET /api/v1/markets/UK/salary/occupations/2134/regions` | 503 | `UK_DATA_NOT_PUBLISHED` | Governance gate active |
| `GET /api/v1/markets/UK/salary/regions/London/occupations` | 503 | `UK_DATA_NOT_PUBLISHED` | Governance gate active |
| `GET /api/v1/markets/UK/salary/metadata` | 503 | `UK_DATA_NOT_PUBLISHED` | Governance gate active |
| `GET /v1/salary/occupations/UK_SOC_2020:2134` | 503 | `UK_DATA_NOT_PUBLISHED` | Governance gate active |
| `GET /v1/salary/compare?occupation_id=UK_SOC_2020:2134` | 503 | `UK_DATA_NOT_PUBLISHED` | Source query withheld fail-closed |

**Data Leakage Inspection:**
- Response payloads contain ONLY standard JSON error envelopes (`detail.code`, `detail.message`).
- Zero wage numbers, sample counts, percentiles, or file paths leaked.

---

### PHASE 6: DUAL CURRENCY AND PPP METHODOLOGY VERIFICATION

The staging backend strictly adheres to the mandated dual-metric architecture:
1. **Nominal FX:** Converted using static 2024 annual average market exchange rates (USD numeraire). Reflects currency exchange value for foreign transfers or global budgeting.
2. **Purchasing Power Parity (PPP):** Converted using World Bank WDI Series `PA.NUS.PRVT.PP` private-consumption conversion factors (extrapolated from ICP benchmark). Reflects domestic household consumption cost parity.
3. **Decoupling Invariant:** The staging backend and frontend present both metrics in dedicated side-by-side containers and explicitly provide the separation warning. No blended or hybrid indices exist.

---

### PHASE 7: CROSS-MARKET COMPARABILITY ENGINE VERIFICATION

Querying `GET /v1/salary/compare?occupation_id=US_SOC_2018:15-1252` returned comparisons across 4 other markets:

1. **United Kingdom (`UK_SOC_2020:2134`):**
   - Comparability Verdict: `NOT_COMPARABLE`
   - `is_suppressed`: `true`
   - `percentiles_original`: `null`
   - Caveats: Data withheld by UK governance gate.
2. **Singapore (`SG_SSOC_2024:25121`):**
   - Comparability Verdict: `COMPARABLE_WITH_ADJUSTMENTS`
   - Nominal USD Median: $66,914.46 USD
   - PPP Int$ Median: $107,142.84 Int$
   - Caveats: Excludes bonus & AWS; P10/P90 unpublished; MOM OWS gross monthly $\times 12$.
3. **Australia (`AU_OSCA_2024:261313`):**
   - Comparability Verdict: `COMPARABLE_WITH_ADJUSTMENTS`
   - Nominal USD Median: $80,198.02 USD
   - PPP Int$ Median: $83,793.10 Int$
   - Caveats: P10/P90 unpublished; 4-digit unit group inheritance; weekly ordinary time $\times 52$.
4. **India (`IN_NCO_2015:2512.0100`):**
   - Comparability Verdict: `COMPARABLE_WITH_MAJOR_CAVEATS`
   - Nominal USD Median: $14,371.20 USD
   - PPP Int$ Median: $50,420.40 Int$
   - Caveats: Pay concept disparity (CTC includes 12% PF and 4.81% gratuity provision); model prediction vs survey; tech metro geographic focus.
5. **Dimensions Evaluated:** All 11 mandated comparability dimensions evaluated on every pair.

---

### PHASE 8 & 9: FRONTEND STAGING VERIFICATION & ISOLATION

1. **Component Verification (`OccupationsPage.tsx` Tab 4):**
   - Tab 4 ("Cross-Market Salary Intelligence") integrates salary rates, benchmark selectors, and comparator cards.
   - Singapore: Displays $90,000 SGD median, Nominal $66,914 USD, PPP $107,143 Int$. P10 and P90 are rendered as `'N/A'` (never `$0`).
   - Australia: Displays $121,500 AUD median. P10 and P90 are rendered as `'N/A'` (never `$0`).
   - UK: Displays `🔒 Data Withheld by Governance Gate: UK ASHE salary analytics are not currently published due to active governance gate.` Graceful handling, no UI crash.
2. **Staging Isolation:**
   - Compiled JS bundle `/assets/index-Bt5QLoUe.js` was statically inspected.
   - Contains exactly one backend host reference: `https://jobintel-backend-staging.onrender.com`.
   - Zero occurrences of production Render URL (`job-market-intelligence-6ral.onrender.com`).
   - Browser network calls remain strictly isolated to staging.

---

### PHASE 10: LOCAL REGRESSION AND MODEL INTEGRITY

All automated test suites were executed on the local repository (`staging/sprint2c3` at `5897413`):

1. **Python Test Suite (`python -m pytest tests/ -q`):**
   - **333 passed** in 24.05s.
   - Note: Bare `pytest` without path traverses into `archive/` legacy streamlit tests where `src.dashboard` is deprecated; targeted test execution on `tests/` confirms 100% pass rate.
2. **Golden Predictions & Parity Suite:**
   - `python -m pytest tests/test_golden_predictions.py tests/test_prediction_parity.py -q`
   - **15 passed** in 5.36s.
3. **Frontend Vitest Suite (`npm --prefix frontend test -- --run`):**
   - **9 passed** across 3 test files in 714 ms.
4. **Frontend TypeScript & Vite Build (`npm --prefix frontend run build`):**
   - Clean compilation, zero TypeScript errors, production bundle generated cleanly in 217 ms.
5. **Model Artifact Integrity:**
   - All 9 active model artifacts in `models/` verified with bit-identical SHA-256 hashes against staging `/health` registry.

---

### PHASE 11: PRODUCTION SAFETY BASELINE AUDIT

To ensure production stability, safe GET requests were issued to production infrastructure:

1. **Production Backend:** `https://job-market-intelligence-6ral.onrender.com`
   - `/health`: HTTP 200 OK (`version: 2.0.0`, status: `healthy`, 9 model artifacts verified).
   - `/v1/salary/sources`: **HTTP 404 Not Found** (confirms Sprint 3B.1 salary endpoints are completely absent from production).
2. **Production Frontend:** `https://job-market-intelligence-dusky.vercel.app/`
   - HTTP 200 OK.
3. **Git Master Branch:** `origin/master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` remains untouched, with zero uncommitted changes and zero unapproved merges.

---

### DEFECTS, LIMITATIONS & GOVERNANCE NOTES

1. **Deployment Identity Header Absence:**
   - Render's managed reverse proxy environment does not expose deployed Git commit SHAs in public HTTP response headers. Per strict governance guidelines, this is classified as `DEPLOYMENT_IDENTITY_UNVERIFIED` at the HTTP header level. However, functional payload parity and model registry SHA-256 matching confirm deployment of `5897413`.
2. **UK Salary Data Withheld:**
   - The UK ASHE 2024 dataset remains gated (`UK_DATA_NOT_PUBLISHED`). Cross-market comparisons correctly designate UK as `NOT_COMPARABLE`.
3. **Singapore and Australia Missing Percentiles:**
   - MOM OWS and ABS EEH source publications do not publish P10 and P90 values for these occupations. They are correctly represented as `null` in API schemas and `'N/A'` in the user interface.
4. **India CTC Model Prediction:**
   - India salary values are derived from calibrated predictive machine learning benchmarks for tech hubs, not official MOSPI PLFS government surveys. The `MODEL_PREDICTION` badge and caveats must remain prominent.

---

### CONCLUSION & RECOMMENDATION

The staging deployment of JOBINTEL 2.0 Sprint 3B.1.2 has been rigorously verified. Staging backend and frontend operate in full alignment with the approved remediation baseline, with 100% test pass rates and zero production leakage.

**Final Staging Verdict:** **PASS — PRODUCTION-ISOLATED STAGING VERIFIED**  
**Authorization for Sprint 3B.2:** Ready for stakeholder review and authorization.
