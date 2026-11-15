# JOBINTEL 2.0 — SPRINT 2C.3: POST-DEPLOYMENT REGRESSION REPORT
**Milestone:** Phase 10 — Post-Deployment Regression Testing & Artifact Verification  
**Execution Date:** 2026-11-15T11:22:00+05:30  
**Evaluator Roles:** QA Automation Engineer, Senior Backend Engineer, Principal Software Architect  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report establishes the post-deployment regression evidence for JOBINTEL 2.0 Sprint 2C.3.

All five authorized test suites were executed against the current repository state. A total of **305 tests (296 backend + 9 frontend)** were executed. **Zero tests failed. Zero tests were skipped.** Test pass rate is **100%**.

All 10 core frozen ML model artifacts and certified datasets were bitwise verified against the immutable artifact manifest.

---

## 2. Test Execution Suite Inventory

| Test Suite Scope | Execution Command | Tests Passed | Failed | Skipped | Duration | Exit Code | Result |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Complete Backend Suite** | `python -m pytest tests -q` | **296** | 0 | 0 | 69.71s | 0 | **PASS** |
| **Frontend Unit Suite** | `npm --prefix frontend test -- --run` | **9** | 0 | 0 | 10.26s | 0 | **PASS** |
| **Governance Engine Suite** | `python -m pytest tests/test_governance_engine.py -v` | **38** | 0 | 0 | 3.17s | 0 | **PASS** |
| **UK Salary Gate Suite** | `python -m pytest tests/test_uk_salary_api.py -v` | **35** | 0 | 0 | 5.23s | 0 | **PASS** |
| **Golden & Cloud Contracts** | `python -m pytest tests/test_cloud_contracts.py tests/test_golden_predictions.py -v` | **8** | 0 | 0 | 3.91s | 0 | **PASS** |
| **AGGREGATE TOTAL** | — | **305** | **0** | **0** | **92.28s** | **0** | **100% PASS** |

---

## 3. Detailed Test Suite Breakdown

### 3.1 Complete Backend Suite (`python -m pytest tests -q`)
- **Collected:** 296 items across 14 test modules.
- **Result:** `296 passed in 69.71s (0:01:09)`.
- **Coverage Areas:**
  - `test_global_foundation.py`: Multi-market catalog, cross-market schema validation.
  - `test_governance_engine.py`: Multi-scope revocation, lifecycle transitions, policy evaluations.
  - `test_uk_salary_api.py`: 5 UK endpoints fail-closed, information leakage protection.
  - `test_uk_salary_service.py`: Workbook parsing, percentile extraction, suppression rules.
  - `test_ashe_ingestion.py`: Ingestion pipeline reproducibility and determinism.
  - `test_cloud_contracts.py`: Feature vector counts (123 USA, 290 India), artifact hash verification.
  - `test_golden_predictions.py`: Numerical parity against frozen model objects.
  - Market router tests: USA, India, Cross-market, Overview, Skills, Archetypes.

### 3.2 Frontend Unit Suite (`npm --prefix frontend test -- --run`)
- **Test Files:** 3 passed (3).
- **Tests:** 9 passed (9).
- **Duration:** 10.26s.
- **Results:**
  - `src/__tests__/routing.test.ts`: 3/3 passed.
  - `src/__tests__/calculator.test.ts`: 3/3 passed.
  - `src/__tests__/skills_contract.test.ts`: 3/3 passed.

### 3.3 Governance Engine Suite (`tests/test_governance_engine.py`)
- **Collected:** 38 items.
- **Result:** 38 passed in 3.17s.
- **Verified Requirements:**
  - Unknown permissions denied by default.
  - Conditional permissions with unmet conditions rejected.
  - Approval bound to exact dataset hash and invalidated by version bump.
  - Scope-based revocation hierarchy (SOURCE > DATASET > RELEASE > MODEL).
  - Degraded revocation registry fails closed safely.

### 3.4 UK Salary API Suite (`tests/test_uk_salary_api.py`)
- **Collected:** 35 items.
- **Result:** 35 passed in 5.23s.
- **Verified Requirements:**
  - 100% fail-closed HTTP 503 `UK_DATA_NOT_PUBLISHED` behavior across all 5 routes.
  - Layer 1 (Revocation) and Layer 2 (Publication Approval) defense-in-depth verified.
  - Zero salary observation leakage across error responses.

### 3.5 Golden Predictions & Cloud Contracts Suite
- **Collected:** 8 items.
- **Result:** 8 passed in 3.91s.
- **Verified Requirements:**
  - USA feature count exact: 123.
  - India feature count exact: 290.
  - Market isolation contract verified.
  - Numerical parity delta < $0.10 for USA golden profiles.
  - Numerical parity delta < 0.05 LPA for India golden profiles.

---

## 4. Frozen ML Model Artifact Hash Verification

All 10 core frozen ML model artifacts and certified processed datasets were independently verified via SHA-256 bitwise comparison against `src/backend/config/artifact_manifest.json`:

```python
Checking 10 core certified artifacts:
[PASS] india_salary_model:   7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310 (matches: True)
[PASS] india_preprocessor:   0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead (matches: True)
[PASS] india_pca:            8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897 (matches: True)
[PASS] india_kmeans:         4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a (matches: True)
[PASS] usa_salary_model:     55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd (matches: True)
[PASS] usa_preprocessor:     815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19 (matches: True)
[PASS] usa_scaler:           2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c (matches: True)
[PASS] usa_pca:              ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0 (matches: True)
[PASS] usa_kmeans:           4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106 (matches: True)
[PASS] india_cohort:         d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec (matches: True)
ALL MATCH: True
```

---

## 5. Post-Deployment Regression Verdict

**VERDICT: ZERO REGRESSIONS — 100% TEST & ARTIFACT PARITY VERIFIED**  
The entire testing matrix (305/305 tests passing) and all 10 frozen model artifacts confirm zero functional, numerical, or architectural regressions.
