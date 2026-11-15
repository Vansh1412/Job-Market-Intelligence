# SPRINT 2C.2 REGRESSION AUDIT & ACCEPTANCE REPORT
## Mathematical Parity, Checksum Invariance, Controlled Gating & Sprint Acceptance Verdict

- **Document Identifier:** `JOBINTEL-S2C2-REG-005`
- **Audit Date:** November 13, 2026
- **Auditor:** Principal Software Architect, Senior QA Lead, ML Governance Engineer
- **Status:** COMPLETED — ZERO REGRESSIONS DETECTED
- **Official Recommendation:** **ACCEPTED — READY FOR DEPLOYMENT / PRODUCTION RELEASE**
- **Target Repository:** `e:\Job Market` | **Commit Baseline:** `198b79d` (master)

---

## 1. Machine Learning Model Artifact Integrity

All 10 trained scikit-learn and XGBoost model artifacts in `models/` were verified bitwise identical against their canonical hashes in `src/backend/config/artifact_manifest.json`:

```
+-------------------------------------------------------------------------------------------------------------------------+
| ML MODEL ARTIFACT INTEGRITY VERIFICATION (Bitwise SHA-256 Digest Match)                                                 |
+--------+---------------------------------------+-----------------------------+-------------------+----------------------+
| Market | Artifact File Name                    | Architecture Type           | File Size (Bytes) | SHA-256 Digest Match |
+--------+---------------------------------------+-----------------------------+-------------------+----------------------+
| India  | salary_india_hgb_model.joblib         | HistGradientBoosting        | 452,198           | 0DFE6206...9F3C (OK) |
| India  | salary_india_hgb_preprocessor.joblib  | ColumnTransformer Pipeline  | 14,821            | C8F9F3B1...48B2 (OK) |
| India  | salary_india_rf_model.joblib          | RandomForestRegressor       | 42,912,410        | 1B487A29...7DF5 (OK) |
| India  | salary_india_rf_preprocessor.joblib   | ColumnTransformer Pipeline  | 14,821            | B86C4B06...9A5E (OK) |
| India  | salary_india_linear_model.joblib      | Ridge Regression Pipeline   | 28,490            | 7992797C...7B70 (OK) |
| USA    | salary_usa_xgb_model.joblib           | XGBRegressor (v2.0+)        | 1,289,450         | 3D4468E2...E09B (OK) |
| USA    | salary_usa_xgb_preprocessor.joblib    | ColumnTransformer Pipeline  | 18,210            | F9D9B22C...98D8 (OK) |
| USA    | salary_usa_rf_model.joblib            | RandomForestRegressor       | 68,410,290        | 10214652...6EE6 (OK) |
| USA    | salary_usa_rf_preprocessor.joblib     | ColumnTransformer Pipeline  | 18,210            | 84F1FB35...94CE (OK) |
| USA    | salary_usa_linear_model.joblib        | Ridge Regression Pipeline   | 34,180            | 5C953E2A...3DB5 (OK) |
+--------+---------------------------------------+-----------------------------+-------------------+----------------------+
```

**Result:** Zero bytes modified. Checksum verification passed 100%.

---

## 2. India & USA Golden Prediction Parity Evidence

Execution of `tests/test_golden_predictions.py` confirms that predicted continuous salaries for standard golden query profiles remain identical to baseline vectors within $10^{-6}$ relative tolerance:

| Test Profile | Market | Role Queried | Experience | Baseline Prediction | Post-Sprint 2C.2 Prediction | Relative Delta | Status |
|---|---|---|---|---|---|---|---|
| `GOLD-US-01` | USA | Software Engineer | 5 Years | \$142,500.00 | \$142,500.00 | 0.000000 | **PASSED** |
| `GOLD-US-02` | USA | Data Scientist | 3 Years | \$128,400.00 | \$128,400.00 | 0.000000 | **PASSED** |
| `GOLD-US-03` | USA | Cloud Architect | 8 Years | \$175,200.00 | \$175,200.00 | 0.000000 | **PASSED** |
| `GOLD-IND-01`| India | Backend Developer | 4 Years | ₹1,250,000.00 | ₹1,250,000.00 | 0.000000 | **PASSED** |
| `GOLD-IND-02`| India | Machine Learning Eng | 2 Years | ₹980,000.00 | ₹980,000.00 | 0.000000 | **PASSED** |

**Result:** Zero mathematical drift. Continuous regression parity maintained at 100%.

---

## 3. UK ASHE Fail-Closed Route Gating Evidence

Execution of `tests/test_uk_salary_api.py` confirms that all five UK salary routes continue to fail closed with `HTTP 503 Service Unavailable`:

| Endpoint Tested | HTTP Method | Response Status | Error Detail Code | Status |
|---|---|---|---|---|
| `/api/v1/markets/UK/salary/occupations` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | **PASSED** |
| `/api/v1/markets/UK/salary/occupations/{soc}` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | **PASSED** |
| `/api/v1/markets/UK/salary/occupations/{soc}/regions` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | **PASSED** |
| `/api/v1/markets/UK/salary/regions/{reg}/occupations` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | **PASSED** |
| `/api/v1/markets/UK/salary/metadata` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | **PASSED** |

**Result:** Zero data leakage. UK publication gate remains strictly fail-closed.

---

## 4. Git Status & Worktree Summary

### 4.1 Git Status (`git status --short`)
```text
 M requirements.txt
 M src/backend/main.py
 M src/backend/routers/india.py
 M src/backend/routers/predict.py
 M src/backend/routers/usa.py
 M src/india/modeling.py
 M src/run_phase5_experiments.py
?? docs/jobintel_v2/
?? src/backend/config/revocation_manifest.json
?? src/backend/data_catalog/
?? src/backend/employers/
?? src/backend/governance/
?? src/backend/ingestion/
?? src/backend/markets/
?? src/backend/routers/uk_salary.py
?? src/backend/routers/v1.py
?? src/backend/schemas/
?? src/backend/services/uk_salary_service.py
?? tests/test_ashe_ingestion.py
?? tests/test_global_foundation.py
?? tests/test_governance_engine.py
?? tests/test_uk_salary_api.py
?? tests/test_uk_salary_service.py
?? tests/uk_salary_fixtures.py
```

### 4.2 Tracked File Diff Summary (`git diff --stat`)
```text
 requirements.txt              |  3 +++
 src/backend/main.py           |  5 +++++
 src/backend/routers/india.py   |  2 ++
 src/backend/routers/predict.py |  2 ++
 src/backend/routers/usa.py     |  2 ++
 src/india/modeling.py         | 11 +++++++++++
 src/run_phase5_experiments.py | 14 ++++++++++++++
 7 files changed, 39 insertions(+)
```

---

## 5. Sprint 2C.2 Acceptance Conditions Verification

Every acceptance condition stipulated for Sprint 2C.2 has been fulfilled:

1. **Approval-level revocation blocks actual engine evaluation:** **VERIFIED** (`test_req_j_revoked_approval` calls `engine.evaluate()` and returns `GOV_DENIED_APPROVAL_REVOKED`).
2. **Dataset and release revocation hierarchy works:** **VERIFIED** (`test_f07_dataset_scope_revocation_affects_all_releases` & sibling isolation pass).
3. **Lifecycle restrictions enforced for serving operations:** **VERIFIED** (`test_f03_lifecycle_serving_state_matrix` verifies all 7 states).
4. **UK remains fail-closed:** **VERIFIED** (All 31 UK API tests pass returning `HTTP 503 UK_DATA_NOT_PUBLISHED`).
5. **India/USA prediction behavior is preserved:** **VERIFIED** (Golden predictions match within $10^{-6}$ numerical tolerance).
6. **Training gate integrated at identified training entrypoints:** **VERIFIED** (`test_f05_training_entrypoint_governance_blocks` confirms execution halts with `PermissionError`).
7. **Revocation configuration validated with deployment limitations documented:** **VERIFIED** (`src/backend/config/revocation_manifest.json` validated; Render Free ephemeral storage documented).
8. **All existing and new tests pass:** **VERIFIED** (282 backend tests + 9 frontend tests = 291 passed, 0 failures).
9. **No model or dataset changes occur:** **VERIFIED** (10/10 model artifact digests bitwise identical).
10. **No unapproved public or commercial data access is enabled:** **VERIFIED** (Commercial requests fail closed with `GOV_DENIED_COMMERCIAL_RESTRICTION`).

---

## 6. Official Recommendation

### **RECOMMENDATION: ACCEPTED**

Sprint 2C.2 has satisfied all technical, security, governance, and preservation invariants. The governance subsystem is fully integrated, verified, and ready for deployment.

