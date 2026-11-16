# JOBINTEL 2.0 — SPRINT 3B.1.2 API REGRESSION REPORT
## API Contract Verification, Comparative Engine Regression & Parity Validation

**Document Reference:** `JOBINTEL-API-REGRESSION-3B.1.2-20261116`  
**Date:** November 16, 2026  
**Sprint:** 3B.1.2 (Salary Data Remediation and Evidence Closure)  
**Target Branch:** `staging/sprint2c3`  
**Test Framework:** Pytest 8.4.2 / FastAPI TestClient / Vitest 5.0.3  
**Status:** **ALL 333 BACKEND TESTS PASSED · ALL 9 FRONTEND TESTS PASSED · ZERO REGRESSIONS**

---

## 1. Executive Summary

Sprint 3B.1.2 executed critical remediations on the cross-market salary intelligence layer:
1. Reverted Singapore annualization to $12 \times \text{monthly gross wage}$ ($90,000 SGD median for Software Developers).
2. Nullified unpublished extreme tail percentiles (P10 and P90) across all Singapore and Australia occupations.
3. Added the explicit `NOT_COMPARABLE` evaluation branch when concordance mapping confidence is $< 0.50$ or unmapped.
4. Updated static 2024 reference FX and World Bank WDI private consumption PPP metadata.
5. Pointed US BLS OEWS base metadata to the parent national index.

This regression audit verified that all 7 modern salary endpoints, legacy salary endpoints, UK fail-closed governance gates, golden prediction models, and frontend client views operate in complete conformance with their contracts.

---

## 2. Comprehensive Endpoint Verification

### 2.1 Modern Salary API Endpoints (`/v1/salary/*`)

| Endpoint | Method | Test Scenario | Expected Status | Actual Status | Verification Summary |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `/v1/salary/sources` | `GET` | List all 5 institutional sources | `200 OK` | `200 OK` | Returns 5 sources (`US_BLS`, `UK_ONS`, `AU_ABS`, `SG_MOM`, `IN_JOBINTEL`). Updated URLs and pay concepts verified. |
| `/v1/salary/sources/{source_id}` | `GET` | Retrieve valid source (`US_BLS_OEWS_2023`) | `200 OK` | `200 OK` | Returns verified metadata. Base URL is `https://www.bls.gov/oes/current/oes_nat.htm`. |
| `/v1/salary/sources/{source_id}` | `GET` | Lookup non-existent source (`UNKNOWN`) | `404 Not Found` | `404 Not Found` | Returns clean HTTP 404 with error detail. |
| `/v1/salary/rates` | `GET` | Retrieve 2024 FX and PPP conversion rates | `200 OK` | `200 OK` | Validates separation invariant warning, `fx_description` (Static 2024 Reference Average), and `ppp_description` (`PA.NUS.PRVT.PP`). |
| `/v1/salary/convert` | `GET` | Dual conversion: ₹12,00,000 INR to USD | `200 OK` | `200 OK` | Nominal USD: \$14,371.20 | PPP USD: \$50,420.17 (PPP is > 3.5x higher than Nominal). |
| `/v1/salary/convert` | `GET` | Invalid currency parameter (`XYZ`) | `400 Bad Request` | `400 Bad Request` | Returns HTTP 400 error cleanly. |
| `/v1/salary/observations` | `GET` | List all 28 national observations | `200 OK` | `200 OK` | All 28 observations returned. 7 US, 8 UK, 4 AU, 6 SG, 3 IN. |
| `/v1/salary/observations?market_id=SG` | `GET` | Filter observations by market (`SG`) | `200 OK` | `200 OK` | Exactly 6 SG observations returned with `p10=null`, `p90=null`, and 12x annual medians. |
| `/v1/salary/observations?market_id=AU` | `GET` | Filter observations by market (`AU`) | `200 OK` | `200 OK` | Exactly 4 AU observations returned with `p10=null`, `p90=null`, and derived 52x weekly earnings. |
| `/v1/salary/occupations/{occ_id}` | `GET` | Retrieve US Software Dev (`US_SOC_2018:15-1252`) | `200 OK` | `200 OK` | Median: \$132,270 USD. All 5 percentiles populated. |
| `/v1/salary/occupations/{occ_id}` | `GET` | Retrieve UK Programmer (`UK_SOC_2020:2134`) | `503 Unavailable` | `503 Unavailable` | **Strict Fail-Closed Enforcement:** Returns `UK_DATA_NOT_PUBLISHED`. |
| `/v1/salary/occupations/{occ_id}` | `GET` | Non-existent occupation ID | `404 Not Found` | `404 Not Found` | Returns clean HTTP 404. |
| `/v1/salary/compare?occupation_id=...` | `GET` | US Software Dev as source | `200 OK` | `200 OK` | Returns 4 cross-market comparisons: UK (withheld, 503 equivalent), AU (ADJUSTMENTS), SG (ADJUSTMENTS, \$90,000 SGD), IN (MAJOR_CAVEATS). |
| `/v1/salary/compare?occupation_id=...` | `GET` | UK Programmer as source | `503 Unavailable` | `503 Unavailable` | Source query fails closed with `UK_DATA_NOT_PUBLISHED`. |
| `/v1/salary/compare?occupation_id=...` | `GET` | Non-existent occupation ID | `404 Not Found` | `404 Not Found` | Returns HTTP 404 without raising 500. |

---

### 2.2 Comparability Engine Branch Verification

The remediated comparability engine in `src/backend/services/salary_service.py` was tested against all 5 decision branches:

| Branch / Verdict | Test Condition | Verified Outcome |
| :--- | :--- | :---: |
| **`INSUFFICIENT_DATA`** | Target is UK under active gate, or median is `null`. | **PASS** (Caveats disclose governance gate withholding). |
| **`NOT_COMPARABLE`** | `confidence_score < 0.50` (tested at 0.45), OR `relationship_type == "NO_SUPPORTED_MAPPING"`. | **PASS** (Explicitly assigns `NOT_COMPARABLE` with non-comparability caveat). |
| **`COMPARABLE_WITH_MAJOR_CAVEATS`** | Target is India (`MODEL_PREDICTION`), or relationship is `BROADER_THAN`/`NARROWER_THAN`. | **PASS** (Caveats disclose CTC overhead and model prediction provenance). |
| **`COMPARABLE_WITH_ADJUSTMENTS`** | Official government surveys across different currencies or reference years. | **PASS** (US vs SG returns `COMPARABLE_WITH_ADJUSTMENTS`). |
| **`DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS`** | Identical currency, same survey year, identical pay concept, high confidence. | **PASS** (Direct comparability within survey sampling error). |

---

### 2.3 Legacy Endpoints Compatibility Verification

All legacy salary endpoints remain 100% operational:
- `GET /api/salary/summary`: **HTTP 200 OK**
- `GET /api/salary/by-role`: **HTTP 200 OK**
- `GET /api/salary/comparator`: **HTTP 200 OK**

---

## 3. Regression Suite Execution Logs

### 3.1 Backend Test Results (`pytest`)
```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: E:\Job Market
plugins: anyio-4.10.0, hydra-core-1.3.6, typeguard-4.6.0
collected 333 items

tests\test_archetype_parity.py ...............                           [  4%]
tests\test_ashe_ingestion.py ...........................                 [ 12%]
tests\test_chart_contracts.py ........                                   [ 15%]
tests\test_cloud_contracts.py ......                                     [ 16%]
tests\test_end_to_end_integration.py ................                    [ 21%]
tests\test_global_foundation.py ..........................               [ 29%]
tests\test_golden_predictions.py ..                                      [ 30%]
tests\test_governance_engine.py ......................................   [ 41%]
tests\test_input_validation.py ........................                  [ 48%]
tests\test_market_analytics.py .....                                     [ 50%]
tests\test_occupation_intelligence.py ...................                [ 55%]
tests\test_prediction_parity.py .............                            [ 59%]
tests\test_routing_contracts.py ....                                     [ 60%]
tests\test_salary_intelligence.py .................                      [ 66%]
tests\test_schema_contracts.py .......                                   [ 68%]
tests\test_skill_integrity.py ............                               [ 71%]
tests\test_uk_salary_api.py ...................................          [ 82%]
tests\test_uk_salary_service.py ........................................ [ 94%]
.........                                                                [ 96%]
tests\test_zero_storage_deployment.py ..........                         [100%]

============================ 333 passed in 18.37s =============================
```

### 3.2 Frontend Test Suite (`vitest`)
```
 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/routing.test.ts (3 tests) 3ms
 ✓ src/__tests__/skills_contract.test.ts (3 tests) 4ms
 ✓ src/__tests__/calculator.test.ts (3 tests) 4ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Start at  16:52:02
   Duration  787ms
```

### 3.3 Frontend Production Build (`tsc -b && vite build`)
```
vite v8.3.3 building client environment for production...
transforming...
✓ 2892 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                             1.49 kB │ gzip:   0.76 kB
dist/assets/index-ghKHOxN1.css              5.12 kB │ gzip:   1.78 kB
dist/assets/rolldown-runtime-hePW80VL.js    0.71 kB │ gzip:   0.42 kB
dist/assets/icons-CG0klYij.js              20.57 kB │ gzip:   7.73 kB
dist/assets/vendor-C9EEoyVf.js            207.23 kB │ gzip:  64.96 kB
dist/assets/index-D341QgHh.js             324.20 kB │ gzip:  80.71 kB
dist/assets/recharts-kC6ixw-D.js          374.34 kB │ gzip: 107.64 kB

✓ built in 236ms
```

### 3.4 Golden Prediction & Parity Verification
- `test_golden_predictions.py`: 2 passed. Bitwise prediction outputs for reference profiles match historical golden references to 8 decimal places.
- `test_prediction_parity.py`: 13 passed. Parity between local Scikit-Learn models and deployment pipelines verified.
- `test_uk_salary_api.py` & `test_uk_salary_service.py`: 84 passed. UK fail-closed governance verified without leakage.
