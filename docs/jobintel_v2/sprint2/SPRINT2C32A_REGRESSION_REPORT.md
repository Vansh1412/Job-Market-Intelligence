# JOBINTEL 2.0 — SPRINT 2C.3.2A: REGRESSION VALIDATION REPORT
**Milestone:** Phase E — Comprehensive Pre-Commit Regression Validation  
**Execution Timestamp:** 2026-11-15T12:10:00+05:30  
**Evaluator Roles:** QA Automation Engineer, Senior Backend Engineer, Principal Software Architect  
**Workspace:** `E:\Job Market` | **Branch:** `staging/sprint2c3`  

---

## 1. Executive Summary

This report establishes the complete pre-commit regression validation results across all 10 required verification checks for Sprint 2C.3.2A.

All tests were executed against the actual supported environment. **A total of 305 tests (296 backend + 9 frontend) passed with 100% green status.** All 10 core frozen ML model artifacts match their certified SHA-256 signatures, golden prediction parity is confirmed, and UK descriptive salary routes remain strictly fail-closed.

---

## 2. Inventory of 10 Mandatory Validation Checks

| Check # | Required Verification Scope | Exact Command / Procedure | Result | Verification Detail |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Governance Engine Tests | `python -m pytest tests/test_governance_engine.py` | **PASS** | 38 passed; verifies permission states, approvals, revocations |
| **2** | UK Salary API Tests | `python -m pytest tests/test_uk_salary_api.py` | **PASS** | 35 passed; verifies all 5 UK routes fail closed with HTTP 503 |
| **3** | UK Ingestion Tests | `python -m pytest tests/test_ashe_ingestion.py` | **PASS** | 22 passed; deterministic workbook parsing and cell classification |
| **4** | Global Foundation API Tests | `python -m pytest tests/test_global_foundation.py` | **PASS** | 24 passed; catalog metadata and observation models |
| **5** | Cloud Contract Tests | `python -m pytest tests/test_cloud_contracts.py` | **PASS** | 6 passed; feature vector counts (123 USA, 290 India) |
| **6** | Golden Prediction Parity | `python -m pytest tests/test_golden_predictions.py` | **PASS** | 2 passed; numerical parity against frozen model objects |
| **7** | Complete Backend Suite | `python -m pytest tests -q` | **PASS** | 296 passed in 26.82s (0 failures, 0 skips) |
| **8** | Frontend Vitest Suite | `npm --prefix frontend test -- --run` | **PASS** | 9 passed in 0.95s across 3 test files |
| **9** | Frontend Production Build | `npm --prefix frontend run build` | **PASS** | 2,891 modules transformed in 1m 8s; 0 TypeScript errors |
| **10** | Model Artifact Hashes | SHA-256 Bitwise Verification Script | **PASS** | 10/10 core models match certified signatures |

---

## 3. Frozen ML Model Artifact Hash Verification (Check 10)

```
[PASS] india_salary_model   : 7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310
[PASS] india_preprocessor   : 0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead
[PASS] india_pca            : 8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897
[PASS] india_kmeans         : 4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a
[PASS] usa_salary_model     : 55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd
[PASS] usa_preprocessor     : 815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19
[PASS] usa_scaler           : 2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c
[PASS] usa_pca              : ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0
[PASS] usa_kmeans           : 4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106
[PASS] india_cohort         : d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec
```

**Result:** `ALL 10 MODELS BITWISE INTACT: True`  
Zero models were retrained, modified, or replaced.

---

## 4. Golden Prediction Parity & UK Gate Status

- **USA Golden Prediction Parity:**
  - Evaluated on Golden Profile `USA_GOLDEN_01_ML_AI`.
  - Direct Model Output: `$256,960.28`.
  - API Output: `$256,960.28`.
  - Parity Delta: `0.0013` (Well within `< $0.10` tolerance).
- **India Golden Prediction Parity:**
  - Evaluated on Golden Profile `IND_GOLDEN_01_PYTHON_AI`.
  - Direct Model Output: `16.6231 LPA`.
  - API Output: `16.62 LPA`.
  - Parity Delta: `0.0031 LPA` (Well within `< 0.05 LPA` tolerance).
- **UK Descriptive Salary Fail-Closed Behavior:**
  - All 5 routes (`occupations`, `occupations/2136`, `occupations/2136/regions`, `regions/london/occupations`, `metadata`) return HTTP 503 `UK_DATA_NOT_PUBLISHED`.
  - Zero salary observations, medians, percentiles, or sample sizes are exposed.

---

## 5. Regression Validation Verdict

**VERDICT: ALL 10 PRE-COMMIT CHECKS PASSED — READY FOR STAGING COMMIT**  
The entire testing matrix is green, numerical parity is preserved, and governance controls remain fail-closed.
