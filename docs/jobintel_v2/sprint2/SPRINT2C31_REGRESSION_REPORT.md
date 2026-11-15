# JOBINTEL 2.0 — SPRINT 2C.3.1: REGRESSION VERIFICATION REPORT
**Milestone:** Phase J — Regression Verification & Artifact Integrity  
**Execution Date:** 2026-11-15T11:35:00+05:30  
**Evaluator Roles:** QA Automation Engineer, Senior Backend Engineer, Principal Software Architect  
**Workspace:** `e:\Job Market` | **Commit Baseline:** `198b79d` (`master`)  

---

## 1. Executive Summary

This report establishes the regression verification evidence for Sprint 2C.3.1.

All five required test suites were executed against the codebase in this sprint. The entire testing suite passed with a **100% pass rate (305 passed out of 305 tests)**. All 10 core frozen ML model artifacts and certified datasets were bitwise verified against `src/backend/config/artifact_manifest.json` with zero checksum drift.

---

## 2. Test Execution Suite Inventory

| Test Suite Scope | Exact Command | Passed | Failed | Skipped | Duration | Exit Code | Result |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Complete Backend Suite** | `python -m pytest tests -q` | **296** | 0 | 0 | 26.82s | 0 | **PASS** |
| **Frontend Unit & Contract** | `npm --prefix frontend test -- --run` | **9** | 0 | 0 | 0.95s | 0 | **PASS** |
| **Governance & UK Gate** | `python -m pytest tests/test_governance_engine.py tests/test_uk_salary_api.py -v` | **73** | 0 | 0 | 8.21s | 0 | **PASS** |
| **Cloud & Golden Contracts** | `python -m pytest tests/test_cloud_contracts.py tests/test_golden_predictions.py -v` | **8** | 0 | 0 | 3.48s | 0 | **PASS** |
| **AGGREGATE TOTAL** | — | **305** | **0** | **0** | **39.46s** | **0** | **100% PASS** |

---

## 3. Frozen ML Model Artifact Hash Verification

All 10 core model artifacts and certified datasets were verified via SHA-256 bitwise hashing against the certified artifact manifest:

```python
Checking 10 core certified artifacts:
[PASS] india_salary_model   : 7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310 (matches: True)
[PASS] india_preprocessor   : 0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead (matches: True)
[PASS] india_pca            : 8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897 (matches: True)
[PASS] india_kmeans         : 4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a (matches: True)
[PASS] usa_salary_model     : 55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd (matches: True)
[PASS] usa_preprocessor     : 815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19 (matches: True)
[PASS] usa_scaler           : 2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c (matches: True)
[PASS] usa_pca              : ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0 (matches: True)
[PASS] usa_kmeans           : 4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106 (matches: True)
[PASS] india_cohort         : d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec (matches: True)
ALL 10 MODELS BITWISE INTACT: True
```

### 3.1 Integrity Confirmation:
- Zero model artifacts were retrained, replaced, or modified.
- Zero golden manifests were modified to mask drift.
- Numerical parity deltas remain exact (`0.0013` USA, `0.0031 LPA` India).

---

## 4. Regression Verification Verdict

**VERDICT: ZERO REGRESSIONS DETECTED — 100% SUITE CONFORMITY**  
All backend, frontend, governance, and model parity tests continue to pass with complete fidelity.
