# JOBINTEL 2.0 — SPRINT 3B.2.3 INDEPENDENT CLOSURE AUDIT & RELEASE QUALIFICATION REPORT
## Multi-Market Labour Demand Analytics, Provenance Transparency, UK Publication Gate & Staging Readiness

**Project:** JOBINTEL 2.0 — A Global Career and Employer Intelligence Platform  
**Sprint:** 3B.2.3 (Independent Closure Audit & Release Qualification)  
**Auditor:** Independent Principal Software Architect, Data Governance Auditor, Labour Market Statistics Specialist & Release Qualification Lead  
**Audit Baseline:** Sprint 3B.2.2 Remediation & Sprint 3B.2.1 Independent Demand Data Provenance Audit  
**Staging Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Audit Execution Mode:** STRICT READ-ONLY INDEPENDENT AUDIT (0 Code Changes, 0 Commits, 0 Pushes, 0 Remote Deployments)  
**Date:** November 16, 2026  
**Final Release Qualification Verdict:** **CONDITIONAL PASS — DOCUMENTED LIMITATIONS**

---

## A. EXECUTIVE SUMMARY

An independent audit was conducted on the JOBINTEL 2.0 Global Job Demand Intelligence module following the completion of Sprint 3B.2.2. The purpose of this audit was to independently verify whether the implementation genuinely resolved the seven findings identified in Sprint 3B.2.1, and to evaluate release qualification for controlled staging deployment.

### Summary of Audit Findings:
1. **Implementation Authenticity:** All seven corrective actions reported in Sprint 3B.2.2 genuinely exist in the codebase and operate as described.
2. **Provenance Rigor:** All 28 demand observations are classified under a formal schema (`DemandProvenance`). The exact distribution is **25 `OFFICIALLY_DERIVED`** and **3 `JOBINTEL_CURATED`**. Zero records are classified as `OFFICIAL_PUBLISHED` because all 25 official observations bundle derived sub-national distributions.
3. **UK Publication Gate:** The technical gate is **100% operational**. Querying UK endpoints in public view zeroes numerical values (`0.0`), returns empty time-series (`[]`), returns empty regional breakdowns (`[]`), and sets `publication_gate_active: true` with reason code `UK_DEMAND_DATA_NOT_PUBLISHED`. Zero numerical leakage was detected across all 8 demand endpoints.
4. **Regional & Inheritance Transparency:** US OEWS employment-weight state allocation notices, Australian 4-digit ANZSCO unit group inheritance warnings, and Singapore synthetic planning-area proxy warnings are verified live in API payloads and UI views.
5. **India Benchmark Integrity:** All 3 Indian observations are bound to `JOBINTEL_CURATED` tech cluster samples and display persistent disclaimers clarifying the absence of a MoSPI national establishment vacancy survey.
6. **Skill Gap Formulation:** The mathematical formula $\text{Coverage} = \frac{W_{\text{matched}}}{W_{\text{total}}} \times 100$ is mathematically verified, zero-division protected, and strictly free of probabilistic hiring or employability claims.
7. **Test & Build Reproducibility:** Independently re-executed test suites confirmed:
   - Backend Pytest: **367 passed in 34.89s** (100% green).
   - Frontend Vitest: **16 passed in 1.08s** (100% green).
   - Frontend Production Bundler: **Clean build in 333ms** (0 TypeScript errors).
8. **Regression Invariants:** 100% preserved. Zero ML models retrained; mandatory 9/9 models verified intact; UK descriptive salary HTTP 503 fail-closed gate preserved.
9. **Final Release Verdict:** **`CONDITIONAL PASS — DOCUMENTED LIMITATIONS`**. The codebase is technically sound and verified locally, but release qualification is conditional upon:
   - Unresolved commercial redistribution licensing terms for the UK ONS / Textkernel vacancy feed.
   - Pydantic non-nullable float typing causing gated values to serialize as `0.0` rather than `null`.
   - Deployment identity remaining `DEPLOYMENT_IDENTITY_UNVERIFIED` pending authorized commit, push, and cloud staging deployment.

---

## B. REPOSITORY & ENVIRONMENT BASELINE

```text
git status --short --branch
## staging/sprint2c3...origin/staging/sprint2c3
 M frontend/src/App.tsx
 M frontend/src/__tests__/routing.test.ts
 M frontend/src/components/AppHeader.tsx
 M frontend/src/services/api.ts
 M frontend/src/types.ts
 M src/backend/main.py
?? docs/jobintel_v2/sprint3/...
?? frontend/src/__tests__/demand_contract.test.ts
?? frontend/src/pages/DemandPage.tsx
?? src/backend/data/demand/
?? src/backend/routers/demand.py
?? src/backend/schemas/demand.py
?? src/backend/services/demand_service.py
?? tests/test_demand_intelligence.py

git branch --show-current: staging/sprint2c3
git rev-parse HEAD: 58974134e56b4c3ec6b6119b7b4739e9cce857f3
git rev-parse master: 198b79dcdff08a5be5f08847c4262d31a3ce261e
git rev-parse origin/master: 198b79dcdff08a5be5f08847c4262d31a3ce261e
git rev-parse origin/staging/sprint2c3: 58974134e56b4c3ec6b6119b7b4739e9cce857f3
```

- **Production Master Isolation:** Certified intact. Zero commits or diffs between local `master` and `origin/master`.
- **Staging Working Tree:** Contains 6 tracked modified files and untracked demand modules from Sprint 3B.2.2. Zero commits created.

---

## C. SPRINT 3B.2.2 IMPLEMENTATION VERIFICATION

The audit independently verified the actual implementation in source code:

| Component | Source Path | Verification Evidence |
|---|---|---|
| **Demand Schemas** | `src/backend/schemas/demand.py` | `DemandProvenance`, `PROVENANCE_METADATA`, gate codes, derivation fields verified (lines 33–65, 149–162, 177–244). |
| **Demand Service** | `src/backend/services/demand_service.py` | UK gate enforcement (lines 385–404), disclosure attachments (lines 369–384), formula calculation (lines 720–749). |
| **Demand Router** | `src/backend/routers/demand.py` | 10 REST endpoints with `public_view=True` sanitization (lines 34–197). |
| **Observation Data** | `src/backend/data/demand/observations.json` | All 28 observations contain provenance, derivation summaries, and derived regional points. |
| **Source Catalog** | `src/backend/data/demand/sources.json` | `uk.ons.labour-demand` tagged `publication_status: "REVIEW_REQUIRED"` with rights notices. |
| **Frontend UI** | `frontend/src/pages/DemandPage.tsx` | Provenance pills, modal ledger, UK gate banner, India benchmark badge, formula breakdown card. |
| **TypeScript Types** | `frontend/src/types.ts` | 100% 1:1 match with backend Pydantic schemas. |

---

## D. PROVENANCE AUDIT

The audit executed an exhaustive enumeration of all 28 observations in `src/backend/data/demand/observations.json`:

```text
Provenance Category Breakdown:
  OFFICIAL_PUBLISHED: 0 (0.0%)
  OFFICIALLY_DERIVED: 25 (89.3%)
  JOBINTEL_CURATED: 3 (10.7%)
  JOBINTEL_MODEL_ESTIMATE: 0 (0.0%)
  SYNTHETIC_TEST_FIXTURE: 0 (0.0%)
  UNVERIFIED: 0 (0.0%)
TOTAL: 28 observations
```

### Analysis of the 25 `OFFICIALLY_DERIVED` Observations:
- **United States (7 observations):** Derived via `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS`. National openings derive from BLS EP Table 1.7; state distributions derive from OEWS employment weights.
- **Australia (4 observations):** Derived via `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING`. Granular 6-digit OSCA occupations inherit scaled monthly volumes from 4-digit ANZSCO 2613 group data.
- **United Kingdom (8 observations):** Derived via `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX`. Monthly index calculated by ONS using digital job board data from Textkernel.
- **Singapore (6 observations):** Derived via `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES`. National vacancies derive from MOM establishment survey; regional shares derive from planning area proxies.

### Analysis of the 3 `JOBINTEL_CURATED` Observations:
- **India (3 observations):** Curated via `JOBINTEL_EMPIRICAL_TECH_HUB_POSTINGS_BENCHMARK`. Sampled job postings across Bangalore, Hyderabad, NCR, and Pune.

*Integrity Check:* 28/28 source IDs resolve to registered entries in `sources.json`. 28/28 metric types resolve in `metrics.json`. Zero broken foreign keys or duplicate observations.

---

## E. UK PUBLICATION GATE & LEAKAGE AUDIT

The audit tested all demand endpoints with UK parameters using FastAPI `TestClient`:

1. **Gate Behavior:**
   - In public view (`public_view=True`), `primary_metric_value` returns `0.0`.
   - `trend_time_series` returns empty array `[]`.
   - `regional_distribution` returns empty array `[]`.
   - `trend_direction` returns `INSUFFICIENT_DATA`.
   - `publication_gate_active` returns `true`.
   - `publication_gate_code` returns `"UK_DEMAND_DATA_NOT_PUBLISHED"`.
   - `publication_gate_message` returns `"UK demand data is currently withheld pending source-use and redistribution review."`
2. **Leakage Audit:**
   - Evaluated response JSON for nested, cached, or explanatory leaks of original Textkernel numbers (e.g. `112.5`, `119.8`, `96.2`). **Zero leakage detected.**
3. **Internal Research Mode:**
   - Verified via direct service call `service.list_observations(market_id="UK", public_view=False)`. Original index values and time-series points remain preserved for internal audit reconciliation.
4. **Qualitative Shortage Status Authenticity:**
   - Retained status `NATIONAL_SHORTAGE` originates from `uk.gov.shortage` (UK Immigration Salary List published by Home Office / MAC / Skills England under Open Government Licence v3.0), which is independent of Textkernel digital advert feeds.
5. **Documented Architectural Limitation:**
   - Gated numeric metrics serialize as `0.0` rather than `null` due to Pydantic `float` typing. While mitigated in the frontend UI via `publication_gate_active`, API consumers could misinterpret `0.0` as measured zero. (Action item for Sprint 3B.3 schema update).

---

## F. REGIONAL DISCLOSURES AUDIT

- **United States:** `OEWS_STATE_EMPLOYMENT_WEIGHTS` allocation disclosure banner verified live in API and UI:
  > *"State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."*
- **Australia:** 4-digit ANZSCO unit group inheritance warning banner verified live in API and UI:
  > *"Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."*
- **Singapore:** Planning area proxy warning verified live in API and UI:
  > *"MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED. Sub-national shares are planning area proxies derived from enterprise cluster estimates."*

All sub-national regional points have `is_derived = True` and explicit `derivation_method` strings.

---

## G. INDIA BENCHMARK AUDIT

- **Classification:** 3/3 records classified as `JOBINTEL_CURATED`.
- **Metric Unit:** Explicitly defined as `"Benchmark Online Postings (Sample)"`.
- **Disclaimers:** Profile attaches persistent disclaimer:
  > *"Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."*
- **Selection Bias:** Formally documented in metadata: formal digital technology postings from Tier-1 tech clusters (Bangalore, Hyderabad, Pune, NCR); complete omission of informal economy and MSMEs.
- **Frontend UI:** Renders amber `CALIBRATED BENCHMARK — EMPIRICAL TECH SAMPLE` banner.

---

## H. SKILL GAP MATHEMATICAL & SEMANTIC AUDIT

- **Formula Invariance:**
  $$\text{Skill Coverage (\%)} = \left( \frac{W_{\text{matched}}}{W_{\text{total}}} \right) \times 100$$
- **Raw Weight Transparency:** API exposes raw components:
  - Example: User with `[Python, SQL, Git, Docker, REST APIs]` for US Software Developers yields $W_{\text{matched}} = 435.0$, $W_{\text{total}} = 1113.0$, $\text{Score} = 39.1\%$.
- **Edge Cases Verified:**
  - Empty input: $0.0\%$, $0.0 / 1113.0$ weight.
  - Duplicates: Deduplicated via set comprehension; single weight added.
  - Unrecognized skills: $0.0\%$.
  - All skills matched: $100.0\%$, $1113.0 / 1113.0$.
  - Division by zero: Protected via `or 1.0` fallback.
- **Predictive Claim Elimination:**
  - Mandatory disclaimer: *"Skill coverage measures alignment between candidate skills and employer-requested competencies... It is not an employability probability, hiring probability, or placement guarantee."*
  - Recommendations describe rule-based learning priority suggestions only.

---

## I. FRONTEND & API CONSISTENCY AUDIT

- Field-by-field parity between Pydantic models in `src/backend/schemas/demand.py` and TypeScript interfaces in `frontend/src/types.ts` is 100% complete.
- Dynamic data binding verified: 0 hardcoded figures in `DemandPage.tsx`.
- Asynchronous transitions are guarded against cross-market stale state.

---

## J. TEST RECONCILIATION & BUILD COMPILATION

Independently executed from terminal:

```powershell
# 1. Backend Pytest
python -m pytest tests/ -q
367 passed in 34.89s (100% green, 0 failures)

# 2. Frontend Vitest
npm --prefix frontend test -- --run
4 test files passed, 16 tests passed in 1.08s (100% green, 0 failures)

# 3. Production Bundler
npm --prefix frontend run build
Built in 333ms (0 TypeScript errors, 0 warnings)
```

- **Local Browser Review Evidence:** Script `scratch/test_browser_sprint3b2_2.cjs` verified live rendering in Chrome headless against local dev server. 8 full-page screenshots preserved in artifact directory.

---

## K. PRODUCTION & STAGING ISOLATION

- **Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (verified 100% identical to `origin/master`). Zero production modifications.
- **Staging Remote Baseline:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3` (verified identical to `origin/staging/sprint2c3`).
- **Cloud Staging Deployment Status:** `DEPLOYMENT_IDENTITY_UNVERIFIED` (Demand Intelligence has been verified locally, but has not yet been pushed or deployed to Render/Vercel staging).
- **Secret Hygiene:** 0 API keys or private tokens detected in git diff.

---

## L. FINDINGS CLASSIFICATION REGISTER

| Finding ID | Audit Finding & Dimension | Severity | Classification Status | Evidence & Resolution Notes |
|---|---|---|---|---|
| **F-01** | Record-level provenance integrity | Medium | **VERIFIED_CLOSED** | All 28 observations tagged under `DemandProvenance` (25 `OFFICIALLY_DERIVED`, 3 `JOBINTEL_CURATED`). |
| **F-02** | US derived state allocation disclosure | High | **VERIFIED_CLOSED** | OEWS employment-weight state allocation notice verified in API, schemas, and UI. |
| **F-03** | Australian occupation inheritance disclosure | High | **VERIFIED_CLOSED** | 4-digit ANZSCO unit group inheritance warning banner verified in API and UI. |
| **F-04** | Singapore regional proxy disclosure | High | **VERIFIED_CLOSED** | `MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED` planning area warning verified. |
| **F-05** | UK publication gate & leakage | Critical | **CLOSED_WITH_LIMITATIONS** | Technical withholding gate verified operational (0 leakage). Commercial redistribution licensing remains under formal review. |
| **F-06** | India calibrated benchmark disclosure | High | **VERIFIED_CLOSED** | Badged as `CALIBRATED BENCHMARK` with MoSPI national vacancy survey disclaimer. |
| **F-07** | Skill gap formula and interpretation | High | **VERIFIED_CLOSED** | Exact mathematical formula card exposed ($W_{\text{matched}} / W_{\text{total}}$); predictive wording eliminated. |
| **F-08** | Gated numeric metric serialization | Medium | **CLOSED_WITH_LIMITATIONS** | Gated values return `0.0` instead of `null` due to Pydantic `float` typing. Mitigated in frontend by `publication_gate_active`. |
| **F-09** | Cloud staging deployment status | Low | **NOT_VERIFIED** | Cloud staging deployment has not been executed; local working tree remains uncommitted pending release authorization. |

---

## M. REMAINING DOCUMENTED LIMITATIONS

1. **UK ONS / Textkernel Commercial Terms:** The technical publication gate withholds data from public view. However, formal commercial redistribution terms with Textkernel BV remain unresolved. The gate must remain active until written licensing clearance is obtained.
2. **Pydantic Non-Nullable Float Typing:** Gated numeric metrics in `DemandObservation` and `OccupationDemandProfile` serialize as `0.0` rather than `null`. In Sprint 3B.3, schema typing should be updated to `float | None = None`.
3. **Cloud Deployment State:** Cloud staging on Render and Vercel currently runs commit `58974134`. The newly hardened Demand Intelligence features reside in the local working tree awaiting authorized release.

---

## N. RELEASE RECOMMENDATION

```text
================================================================================
RELEASE RECOMMENDATION: READY FOR CONTROLLED STAGING RELEASE PREPARATION
The codebase is technically sound, methodologically rigorous, and passes 100%
of automated tests and local browser verifications.
The audit qualifies the implementation for:
  1. Creating a controlled staging release commit on staging/sprint2c3.
  2. Pushing to origin/staging/sprint2c3.
  3. Conducting cloud staging verification (Render/Vercel) with UK gate active.
================================================================================
```

---

## O. NEXT MILESTONE

The recommended next milestone is:
**Sprint 3B.2.4: Controlled Staging Deployment & Cloud Integration Verification**
1. Stage and commit the verified Sprint 3B.2.2 implementation on `staging/sprint2c3`.
2. Push to `origin/staging/sprint2c3` to trigger staging builds on Render and Vercel.
3. Conduct cloud deployment verification and browser audit against staging URLs:
   - Frontend: `https://jobintel-staging.vercel.app/demand`
   - Backend: `https://jobintel-backend-staging.onrender.com/api/v1/demand/markets`
4. Confirm cloud parity with local audit results.
