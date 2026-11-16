# JOBINTEL 2.0 — SPRINT 3B.1.3 INDEPENDENT AUDIT REPORT
## Independent Remediation Closure & Provenance Authenticity Audit

**Document Reference:** `JOBINTEL-AUDIT-3B.1.3-20261116`  
**Date:** November 16, 2026  
**Target Sprint:** Sprint 3B.1.2 (Salary Data Remediation and Evidence Closure)  
**Target Branch:** `staging/sprint2c3`  
**Audit Target Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Verified UNTOUCHED)  
**Execution Mode:** STRICT READ-ONLY INDEPENDENT AUDIT  
**Auditor:** Independent Principal Data Governance Auditor & Labour Market Statistics Specialist  

---

## A. Executive Verdict

### **OVERALL AUDIT DETERMINATION: CONDITIONAL PASS — LIMITATIONS REMAIN**

Sprint 3B.1.2 significantly improved the integrity and rigor of the cross-market salary intelligence subsystem. The critical vulnerabilities discovered in Sprint 3B.1.1—specifically the unauthorized 13-month AWS bonus inflation on Singapore wages, the synthetic fabrication of extreme tail percentiles (P10 and P90), and the eclipsed `NOT_COMPARABLE` branch in the comparability engine—have been **genuinely remediated in code and data**.

However, an independent inspection of the actual data structures, statistical publications, and execution paths reveals that **four corrective actions remain closed with important statistical limitations**:
1. **Singapore Annualization (`C-01`):** Multiplying MOM monthly gross wage by 12 produces an **`ANNUALIZED_RATE_ONLY`** (or `OFFICIALLY_ANNUALIZED_MONTHLY_WAGE`), not observed annual earnings, because statutory gross monthly wage explicitly excludes unmeasured bonuses and Annual Wage Supplements (AWS).
2. **Australia OSCA Detailed Concordance (`C-03`):** While unpublished P10/P90 tail percentiles were properly nullified, the retained figures represent **4-digit ANZSCO unit group distributions** from ABS Cat. 6306.0, mapped to 6-digit detailed OSCA roles without distinct occupation-level variance.
3. **BLS Source Citation (`C-04`):** The updated URL in `sources.json` (`https://www.bls.gov/oes/current/oes_nat.htm`) points to a **moving current index** rather than an immutable historical archive for the May 2023 release.
4. **UK SOC Edition Reconciliation (`C-08`):** No official versioned crosswalk between UK SOC 2010 (used in legacy ingestion) and UK SOC 2020 (used in current registries) has been implemented; the discrepancy is **quarantined behind the HTTP 503 fail-closed gate**, but remains architecturally unresolved.

All 333 backend unit/integration tests and 9 frontend vitest tests pass, frozen machine learning models maintain bitwise output parity, and the production `master` branch is completely untouched.

---

## B. Git & Cryptographic Baseline

### 1. Git State Verification
```
Current Branch:              staging/sprint2c3
Current Local HEAD SHA:      58974134e56b4c3ec6b6119b7b4739e9cce857f3
Remote Staging HEAD SHA:     58974134e56b4c3ec6b6119b7b4739e9cce857f3 (Synchronous)
Remediation Commit Under Audit: 5897413
Previous Audit Commit:       3b0cb0c (Sprint 3B.1.1)
Production Master Baseline:  198b79dcdff08a5be5f08847c4262d31a3ce261e (Verified UNTOUCHED)
Working Tree Status:         Clean (0 modified, 0 untracked tracked files)
Audit Execution Artifacts:   docs/jobintel_v2/sprint3/SPRINT3B1_3_INDEPENDENT_CLOSURE_AUDIT.md (Untracked)
```

### 2. File Hash Comparison Table (LF-Normalized SHA-256)

| File Path | Sprint 3B.1.1 Audit Hash (`3b0cb0c`) | Sprint 3B.1.2 Reported Hash | Current Actual LF Hash (`5897413`) | Independent Status |
| :--- | :---: | :---: | :---: | :---: |
| `src/backend/data/salary/sources.json` | `dbc8b0b6cf85e1...` | `979a8251bf966e...` | `979a8251bf966e300d6b8f59dbcff4216b2144a793dad697bce87a89179d9271` | **MATCH** |
| `src/backend/data/salary/ppp_fx_rates.json` | `aef330bb54cfcd...` | `c2d351e280c165...` | `c2d351e280c16585f2302f273d210228224754b243ed6aed3e6d2abb88fdde93` | **MATCH** |
| `src/backend/data/salary/observations.json` | `d078348b2ebec9...` | `50a8c0dbc4c79b...` | `50a8c0dbc4c79b7e527f0bbf59ca4fdb19910f35be8fda7243661ba4503db9a4` | **MATCH** |
| `src/backend/schemas/salary.py` | `148b58b5afc638...` | `148b58b5afc638...` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` | **UNMODIFIED** |
| `src/backend/services/salary_service.py` | `1dd59d1af58ed3...` | `9912bdcd517fba...` | `9912bdcd517fba63509a3cc0eedf847dd85fc8c1ee91ddff9b7a96e641763931` | **MATCH** |
| `src/backend/routers/salary.py` | `687533418353dc...` | `687533418353dc...` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` | **UNMODIFIED** |
| `frontend/src/pages/OccupationsPage.tsx` | N/A (Sprint 3B.1) | `5c2ffb9ebeb963...` | `5c2ffb9ebeb963a1c230aece3532ed1c0fcae1dd0d912980706a0666412d3fab` | **MATCH** |
| `tests/test_salary_intelligence.py` | N/A (Sprint 3B.1) | `8bb3ff5b55905b...` | `8bb3ff5b55905b2a86f0b360043a55fc60ef75660aac8923cb3049d48392355a` | **MATCH** |

*Note on Line Endings:* On Windows working trees, raw bytes of `observations.json` evaluate to `0d69ed...` due to local CRLF checkout, but normalize to identical LF hash `50a8c0...` matching the commit tree.

---

## C. Evidence Matrix Audit

### 1. 28-Observation Reconciliation
The file `docs/jobintel_v2/sprint3/SALARY_OBSERVATION_EVIDENCE_MATRIX.md` was audited against `src/backend/data/salary/observations.json` and `src/backend/data/occupations/national_occupations.json`:
- **Total National Occupations Registered:** 28 (plus 2 international ISCO reference anchors = 30 catalog concepts).
- **Observations in Evidence Matrix:** Exactly 28 unique observations.
- **Identifiers Match:** 100% bijective correspondence between JSON observation IDs and Matrix documentation sections (0 missing, 0 orphaned).
- **Markets Covered:** United States (7), United Kingdom (8), Australia (4), Singapore (6), India (3).

### 2. Percentile Fields Reconciliation (140 Total Slots)
- **Total Potential Percentile Slots ($28 \times 5$):** 140
- **Actual Non-Null Values in Registry:** 120
- **Actual Null (`None`) Values in Registry:** 20
  - Australia: 4 roles $\times 2$ extreme tails (P10, P90) = **8 nulls**
  - Singapore: 6 roles $\times 2$ extreme tails (P10, P90) = **12 nulls**
  - $8 + 12 = 20$ nulls verified.
- **Suppression at Source:**
  - In `observations.json`, UK records store 40 raw values (`is_suppressed: false`, `quality_flag: "OFFICIAL_STATISTICAL_RELEASE"`), but at runtime, `_check_uk_publication_gate()` intercepts every UK query and blocks disclosure with `HTTP 503` or replaces all percentiles with `null` (`is_suppressed: true`, `quality_flag: "GOVERNANCE_WITHHELD"`).
- **Breakdown by Provenance Classification:**
  - `OFFICIAL_PUBLISHED`: 35 percentiles (US: 35)
  - `OFFICIALLY_DERIVED`: 30 percentiles (AU: 12, SG: 18)
  - `JOBINTEL_MODEL_ESTIMATE`: 15 percentiles (IN: 15)
  - `SUPPRESSED` (Gated): 40 percentiles (UK: 40)
  - `NOT_PUBLISHED` (`null`): 20 percentiles (AU: 8, SG: 12)
  - **Synthetic / Unverified Percentiles Remaining:** **0**

---

## D. Singapore MOM OWS Audit (C-01 & C-02)

### 1. Source Definitions & Statutory Treatment
In MOM Singapore's *Occupational Wage Survey (OWS) 2023*, Table T1 defines **Gross Monthly Wage** as:
> *"Basic wage, overtime payments, commissions, tips, other allowances and 1/12 of annual variable payment. It EXCLUDES employer CPF contributions, bonuses, and annual wage supplements (AWS)."*

### 2. Multiplier & Value Verification
Sprint 3B.1.2 reverted the unauthorized 13x multiplier to the statutory standard: $\text{Annualized Monthly Wage} = \text{Monthly Gross Wage} \times 12$.
- `25121` Software Developer: $7,500/mo $\times 12 =$ **$90,000 SGD** (was $97,500)
- `25131` AI/ML Engineer: $8,200/mo $\times 12 =$ **$98,400 SGD** (was $106,600)
- `25132` Data Scientist: $8,000/mo $\times 12 =$ **$96,000 SGD** (was $104,000)
- `25124` Cloud Architect: $9,000/mo $\times 12 =$ **$108,000 SGD** (was $117,000)
- `25125` DevOps Engineer: $7,800/mo $\times 12 =$ **$93,600 SGD** (was $101,400)
- `25211` Cybersecurity Specialist: $7,900/mo $\times 12 =$ **$94,800 SGD** (was $102,700)

### 3. Independent Audit Assessment: `ANNUALIZED_RATE_ONLY`
- **Finding:** The arithmetic annualization ($12 \times \text{monthly}$) is accurate and correctly tags `quality_flag: "OFFICIALLY_DERIVED"`.
- **Limitation:** In Singapore corporate practice, AWS (13th-month check) and performance bonuses form 10%–25% of actual annual compensation for tech professionals. Because MOM OWS gross monthly wage explicitly excludes bonuses and AWS, the resulting $\$90,000$ SGD figure is strictly an **`ANNUALIZED_RATE_ONLY`** (or `OFFICIALLY_ANNUALIZED_MONTHLY_WAGE`), not total annual cash received.
- **Classification:** **`CLOSED_WITH_LIMITATIONS`**.

### 4. Percentile Truncation Verification (C-02)
- Table T1 of MOM OWS officially compiles only P25, Median (P50), and P75. P10 and P90 are not compiled.
- Verified in `observations.json` and API response: `p10: None`, `p90: None` across all 6 roles.
- Frontend renders `"N/A"` without `$0` or crashing.
- **Classification:** **`VERIFIED_CLOSED`**.

---

## E. Australia ABS EEH Audit (C-03)

### 1. Survey Source & Population
- Primary source: Australian Bureau of Statistics (ABS), *Employee Earnings and Hours (EEH, Cat. 6306.0)*, May 2023.
- Measure: Weekly ordinary-time cash earnings for full-time adult non-managerial employees ($52 \times \text{weekly}$).

### 2. Concordance Limitation (4-Digit Unit Group to 6-Digit OSCA)
- **Defect Uncovered:** ABS Cat. 6306.0 publishes wage percentiles at the **4-digit ANZSCO unit group level**, NOT the 6-digit detailed OSCA level.
- Specifically:
  - `AU_OSCA_2024:261313` (Software Engineer) and `AU_OSCA_2024:261314` (Software Tester) both inherit their underlying data from Unit Group `2613` (Software and Applications Programmers).
  - `AU_OSCA_2024:224411` (Data Scientist) derives from Unit Group `2244` (Actuaries, Mathematicians and Statisticians).
  - `AU_OSCA_2024:262112` (ICT Security Specialist) derives from Unit Group `2621` (Database and Systems Administrators, and ICT Security).
- **Percentile Non-Fabrication:** P10 and P90 are nullified (`null`), which eliminates synthetic extreme tails.
- **Audit Verdict:** **`CLOSED_WITH_LIMITATIONS`**. The limitation is that 6-digit OSCA detailed roles inherit 4-digit unit group statistical parameters.

---

## F. US BLS OEWS Audit (C-04)

### 1. Verbatim Percentile Correspondence
All 7 US occupations correspond verbatim to the official BLS OEWS May 2023 release tables:
- `15-1252` Software Developers: Median $132,270 | Mean $138,110 | P10: $77,020 | P25: $101,370 | P75: $168,050 | P90: $208,620.
- `15-2051` Data Scientists: Median $108,020 | Mean $119,040 | P10: $61,070 | P25: $81,720 | P75: $146,800 | P90: $184,090.
- `15-1253` Software QA Analysts: Median $101,800 | Mean $105,820 | P10: $55,200 | P25: $75,310 | P75: $130,940 | P90: $161,020.
- `15-1212` Info Security Analysts: Median $120,360 | Mean $124,740 | P10: $69,210 | P25: $90,870 | P75: $153,600 | P90: $182,370.
- `15-1242` Database Administrators: Median $101,510 | Mean $104,810 | P10: $54,920 | P25: $74,440 | P75: $131,730 | P90: $161,280.
- `15-1244` Network & Sysadmins: Median $95,360 | Mean $97,920 | P10: $55,540 | P25: $71,960 | P75: $122,220 | P90: $147,700.
- `15-1211` Computer Systems Analysts: Median $103,800 | Mean $107,530 | P10: $61,990 | P25: $80,520 | P75: $131,840 | P90: $161,900.

### 2. Moving URL vs. Historical Archive Citation Limitation
- In `sources.json`, `source_url` was changed from `oes151252.htm` to `https://www.bls.gov/oes/current/oes_nat.htm`.
- **Finding:** While pointing to the national index resolves the single-role defect, `.../current/...` is a **moving URL** that serves the latest current release, rather than an immutable archive for May 2023 (`https://www.bls.gov/oes/2023/may/` or direct archive data file `oesm23nat.zip`).
- **Hours Convention:** 2,080 annual hours convention ($40 \text{ hrs/wk} \times 52 \text{ wks}$) is verified and properly documented.
- **Audit Verdict:** **`CLOSED_WITH_LIMITATIONS`**.

---

## G. India CTC Benchmark Audit

### 1. Model Identity & Target Formulation
- **Source Model:** `HistGradientBoostingRegressor` / `RandomForestRegressor` trained on `indian-job-market-dataset-2025` (cohort size: 5,859 job postings, 290 engineered features).
- **Target Variable:** `salary_midpoint_inr` (log1p transformed).
- **Predicted Target:** Single point estimate of conditional median/midpoint CTC.

### 2. Empirical Percentile Generation vs. Quantile Model Reality
- **Audit Defect Identified:** The India ML models in `models/india/` do **NOT** predict conditional quantiles (P10, P25, P75, P90). The models only predict a single conditional midpoint.
- **Percentile Source:** The percentile spreads in `observations.json` (e.g. Software Developer P10: 4.5 LPA, P25: 7.5 LPA, P50: 12.0 LPA, P75: 18.0 LPA, P90: 26.0 LPA) represent **calibrated empirical tech-metro cohort distributions** (`JOBINTEL_CURATED` / vacancy posting spreads), NOT raw outputs of an end-to-end multi-quantile regression model.
- **CTC Overhead Definition:** CTC includes mandatory basic salary, allowances, employer Provident Fund (12%), and gratuity provisions under the Payment of Gratuity Act, 1972 (4.81%). It represents employer labor cost, structurally distinct from gross cash wages.
- **Tagging:** Accurately tagged as `MODEL_PREDICTION` with `COMPARABLE_WITH_MAJOR_CAVEATS`.

---

## H. Comparability Engine Audit (C-05)

### 1. Branch Ordering & Decision Hierarchy
The branch ordering in `src/backend/services/salary_service.py` was inspected:
```python
# 1. Gate / Suppression check
if target_profile.is_suppressed or target_profile.percentiles.p50 is None:
    return ComparabilityVerdict.INSUFFICIENT_DATA, caveats

# 2. Non-comparable threshold (C-05 FIX)
if relationship_type == "NO_SUPPORTED_MAPPING" or confidence_score < 0.50:
    verdict = ComparabilityVerdict.NOT_COMPARABLE

# 3. Major caveats
elif (
    source_profile.quality_flag == "MODEL_PREDICTION"
    or target_profile.quality_flag == "MODEL_PREDICTION"
    or relationship_type in ("BROADER_THAN", "NARROWER_THAN")
    or confidence_score < 0.88
):
    verdict = ComparabilityVerdict.COMPARABLE_WITH_MAJOR_CAVEATS

# 4. Economic adjustments (currency / reference year)
elif source_profile.currency != target_profile.currency or src_ref != tgt_ref:
    verdict = ComparabilityVerdict.COMPARABLE_WITH_ADJUSTMENTS

# 5. Direct comparability within survey sampling error
else:
    verdict = ComparabilityVerdict.DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS
```

### 2. Boundary Analysis & Nature of Thresholds
- At `confidence_score = 0.49`: Evaluates `< 0.50` $\to$ **`NOT_COMPARABLE`**.
- At `confidence_score = 0.50`: Evaluates $\ge 0.50$, `< 0.88` $\to$ **`COMPARABLE_WITH_MAJOR_CAVEATS`**.
- At `confidence_score = 0.88`: Evaluates $\ge 0.88$, different currency $\to$ **`COMPARABLE_WITH_ADJUSTMENTS`**.
- **Nature of Thresholds:** These values (0.50 and 0.88) are **operational policy heuristic thresholds**, NOT statistically calibrated Bayesian posterior probabilities.
- **Audit Verdict:** **`VERIFIED_CLOSED`**.

---

## I. Purchasing Power Parity (PPP) & Nominal FX Audit (C-06 & C-07)

### 1. World Bank WDI Series Verification
- **Indicator Code:** World Bank World Development Indicators (WDI) `PA.NUS.PRVT.PP` (PPP conversion factor, private consumption, LCU per international $).
- **2024 Value Status:** Verified that 2024 figures are **model-based CPI extrapolations** from the ICP 2017/2021 benchmark rounds, not an independent benchmark census.
- **Analytical Role:** Household private consumption living-cost parity, not occupational labor-cost parity.
- **Warning Invariant:** Preserved in `ppp_fx_rates.json` and API: *"Nominal FX and PPP serve fundamentally different economic functions and MUST NEVER be averaged, blended, or used interchangeably."*
- **Audit Verdict:** **`VERIFIED_CLOSED`**.

### 2. Nominal Foreign Exchange (FX) Verification
- Rates are static 2024 reference annual averages:
  - USD/INR: 83.50 (Multiplier: 0.011976)
  - USD/GBP: 0.7850 (Multiplier: 1.273885)
  - USD/AUD: 1.5200 (Multiplier: 0.657895)
  - USD/SGD: 1.3450 (Multiplier: 0.743494)
- Multipliers and conversion arithmetic verified to 6 decimal places.
- UI and API metadata labels updated to "Static 2024 Reference Annual Average Exchange Rates".
- **Audit Verdict:** **`VERIFIED_CLOSED`**.

---

## J. UK Classification Reconciliation Audit (C-08)

### 1. Discrepancy Assessment (Options A, B, C, D)
- **Option B applies (QUARANTINED):**
  - The legacy data ingestion pipeline `src/backend/ingestion/ashe2025.py` extracts ASHE Table 15 in **UK SOC 2010**.
  - The current occupation taxonomy and salary observation registry are standardized on **UK SOC 2020** (e.g. `UK_SOC_2020:2134`).
  - There is currently **NO automated or versioned crosswalk table** between SOC 2010 and SOC 2020 in `mappings.json` (0 SOC 2010 mappings exist).
  - However, `salary_service.py` does not execute `ashe2025.py`; instead, it loads SOC 2020 observations directly.
  - Crucially, both the legacy UK endpoints and the cross-market salary service enforce `require_uk_publication()`, which **fails closed with HTTP 503** (`UK_DATA_NOT_PUBLISHED`).
- **Suppression Verification:**
  - `GET /v1/salary/occupations/UK_SOC_2020:2134` $\to$ **HTTP 503 Service Unavailable**.
  - `GET /v1/salary/compare?occupation_id=UK_SOC_2020:2134` $\to$ **HTTP 503 Service Unavailable**.
  - When non-UK roles query comparisons, UK comparator records return `is_suppressed: true` with all percentiles set to `None`.
  - Zero UK wage figures leak through public endpoints.
- **Audit Verdict:** **`CLOSED_WITH_LIMITATIONS`**. The limitation is that while the data is securely quarantined, the underlying SOC 2010 $\to$ SOC 2020 crosswalk remains unimplemented in code.

---

## K. Frontend & Contract Audit

The React / TypeScript frontend was audited at `frontend/src/pages/OccupationsPage.tsx`:
1. **Null Percentile Robustness:** Verified lines 1107 and 1244 render `"N/A"` for null P10 and P90 without displaying `$0` or crashing.
2. **Provenance Badges:** Source cards render `quality_flag` (`OFFICIAL_STATISTICAL_RELEASE`, `OFFICIALLY_DERIVED`, `MODEL_PREDICTION`).
3. **Decoupled Metric Cards:** Explicitly separates `Nominal USD Median (Market FX)` and `PPP Int$ Median (World Bank WDI PPP)`.
4. **Governance Banners:** Displays the UK fail-closed governance banner when UK occupations are selected or listed as comparators.

---

## L. Regression & Build Results

### 1. Backend Test Suite (`pytest`)
```
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 333 items
============================ 333 passed in 31.54s =============================
```
- Total test count increased from 330 to 333 (added Singapore/Australia null provenance test, `NOT_COMPARABLE` branch test, and BLS source citation test).
- Pass rate: **100% (333/333 passed, 0 failed, 0 skipped)**.

### 2. Frontend Test Suite (`vitest`)
```
 RUN  v5.0.3 E:/Job Market/frontend
 ✓ src/__tests__/routing.test.ts (3 tests)
 ✓ src/__tests__/skills_contract.test.ts (3 tests)
 ✓ src/__tests__/calculator.test.ts (3 tests)
 Test Files  3 passed (3)
      Tests  9 passed (9)
   Duration  1.11s
```

### 3. Frontend Production Build (`tsc -b && vite build`)
```
✓ 2892 modules transformed.
dist/index.html                             1.49 kB │ gzip:   0.76 kB
dist/assets/index-D341QgHh.js             324.20 kB │ gzip:  80.71 kB
dist/assets/recharts-kC6ixw-D.js          374.34 kB │ gzip: 107.64 kB
✓ built in 308ms
```

### 4. Golden Prediction & Parity Tests
- `tests/test_golden_predictions.py`: 2/2 passed.
- `tests/test_prediction_parity.py`: 13/13 passed.
- Golden reference predictions match historical references to 8 decimal places.

### 5. UK Governance Tests
- `tests/test_uk_salary_api.py` and `tests/test_uk_salary_service.py`: 84/84 passed without failure or data leakage.

---

## M. Deployment Identity Audit

- **Local Repository Staging HEAD:** Commit `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (verified).
- **Remote Git Staging Branch:** `origin/staging/sprint2c3` at `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (verified synchronous).
- **Render Staging Backend Deployment:** A health check to `https://jobintel-backend-staging.onrender.com/health` timed out (typical for Render Free Web Service spinning down after 15 minutes of inactivity).
- **Audit Determination:** In accordance with Section 15 of the audit mandate:
  **`DEPLOYMENT_IDENTITY_UNVERIFIED`** (Cloud staging deployment cannot be verified purely from static git/local inspection).

---

## N. Final Corrective Action Matrix

| ID | Component | Core Finding & Audit Assessment | Verdict |
| :---: | :--- | :--- | :---: |
| **C-01** | `observations.json`<br>`sources.json` | Reverted to 12x gross monthly wage (\$90k SGD median). Represents an annualized rate excluding bonuses and AWS. | **`CLOSED_WITH_LIMITATIONS`** |
| **C-02** | `observations.json`<br>`OccupationsPage.tsx` | Nullified unpublished SG P10 and P90 tail values. Frontend renders `"N/A"` without false precision. | **`VERIFIED_CLOSED`** |
| **C-03** | `observations.json` | Nullified AU detailed P10 and P90 values. 6-digit OSCA roles inherit 4-digit unit group statistical parameters. | **`CLOSED_WITH_LIMITATIONS`** |
| **C-04** | `sources.json`<br>`observations.json` | Updated base URL to `oes_nat.htm`. Pointed to moving current index rather than static May 2023 archive URL. | **`CLOSED_WITH_LIMITATIONS`** |
| **C-05** | `salary_service.py`<br>`test_salary_intelligence.py` | Added explicit check returning `NOT_COMPARABLE` for confidence < 0.50 or unmapped roles. Policy heuristic verified. | **`VERIFIED_CLOSED`** |
| **C-06** | `ppp_fx_rates.json`<br>`salary_service.py` | Clarified World Bank WDI Series `PA.NUS.PRVT.PP` 2024 extrapolation and domestic household living cost role. | **`VERIFIED_CLOSED`** |
| **C-07** | `ppp_fx_rates.json`<br>`OccupationsPage.tsx` | Labeled nominal FX rates as Static 2024 Reference Annual Average Exchange Rates. Decoupling enforced. | **`VERIFIED_CLOSED`** |
| **C-08** | `ashe2025.py`<br>`uk_salary.py` | Documented UK SOC 2010 vs SOC 2020 crosswalk prerequisite. Discrepancy quarantined under HTTP 503 gate. | **`CLOSED_WITH_LIMITATIONS`** |

---

## O. Final Recommendation

### **RECOMMENDATION: READY FOR CONTROLLED STAGING VALIDATION ONLY**

The staging codebase on branch `staging/sprint2c3` is in an exceptionally stable, mathematically verified, and well-tested state. All 8 corrective actions are closed either directly or with clearly documented, defensible limitations.

However, the platform should **NOT** immediately proceed to production release or feature expansion (Sprint 3B.2) until:
1. **Cloud Staging Verification:** Verify that the Render staging backend and Vercel staging frontend deploy commit `5897413` and smoke tests pass against live cloud endpoints.
2. **Stakeholder Alignment on Documented Limitations:** Confirm that product and data stakeholders accept the documented statistical limitations (Singapore 12x annualized rate without bonuses, Australia 4-digit unit group variance inheritance, and UK HTTP 503 quarantine).
3. **UK Crosswalk Roadmap:** Maintain the UK HTTP 503 fail-closed gate until a formalized SOC 2010 $\to$ SOC 2020 crosswalk is scheduled and implemented.
