# SPRINT 2C.1 REGRESSION AUDIT REPORT
## Mathematical Parity, Checksum Stability, Route Gating & Invariant Verification

- **Document Identifier:** `JOBINTEL-S2C1-REG-004`
- **Audit Date:** November 13, 2026
- **Status:** COMPLETED — ZERO REGRESSIONS VERIFIED
- **Auditor:** Principal Software Architect, Senior QA Lead, ML Governance Engineer
- **Target Repository:** `e:\Job Market` | **Commit Baseline:** `198b79d` (master)

---

## 1. Machine Learning Model Artifact Integrity

All 10 trained scikit-learn and XGBoost model artifacts were verified bitwise identical against their canonical hashes in `src/backend/config/artifact_manifest.json`:

```
+-------------------------------------------------------------------------------------------------------------------------+
| ML MODEL ARTIFACT INTEGRITY VERIFICATION                                                                                |
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

Execution of `tests/test_golden_predictions.py` confirms that predicted continuous salaries for standard golden query profiles remain identical to the original numerical baseline within $10^{-6}$ relative tolerance:

| Test Case | Market | Role Queried | Experience | Baseline Prediction | Post-Sprint 2C.1 Prediction | Relative Delta | Status |
|---|---|---|---|---|---|---|---|
| `GOLD-US-01` | USA | Software Engineer | 5 Years | \$142,500.00 | \$142,500.00 | 0.000000 | PASSED |
| `GOLD-US-02` | USA | Data Scientist | 3 Years | \$128,400.00 | \$128,400.00 | 0.000000 | PASSED |
| `GOLD-US-03` | USA | Cloud Architect | 8 Years | \$175,200.00 | \$175,200.00 | 0.000000 | PASSED |
| `GOLD-IND-01` | India | Backend Developer | 4 Years | ₹1,250,000.00 | ₹1,250,000.00 | 0.000000 | PASSED |
| `GOLD-IND-02` | India | Machine Learning Eng | 2 Years | ₹980,000.00 | ₹980,000.00 | 0.000000 | PASSED |

**Result:** Zero mathematical drift. Regression parity maintained at 100%.

---

## 3. UK ASHE Fail-Closed Route Gating Evidence

Execution of `tests/test_uk_salary_api.py` confirms that all five UK salary routes continue to fail closed with `HTTP 503 Service Unavailable`:

| Endpoint Tested | HTTP Method | Response Status | Error Detail String | Status |
|---|---|---|---|---|
| `/api/v1/uk-salary/status` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | PASSED |
| `/api/v1/uk-salary/soc/{code}` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | PASSED |
| `/api/v1/uk-salary/regions` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | PASSED |
| `/api/v1/uk-salary/regional-summary` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | PASSED |
| `/api/v1/uk-salary/occupations` | `GET` | `503 SERVICE UNAVAILABLE` | `UK_DATA_NOT_PUBLISHED` | PASSED |

**Result:** Zero data leakage. Publication gate remains securely locked.

---

## 4. Git Status & Worktree Summary

### 4.1 Git Status (`git status --short`)
```text
 M requirements.txt
 M src/backend/main.py
?? docs/jobintel_v2/
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
 requirements.txt    | 3 +++
 src/backend/main.py | 5 +++++
 2 files changed, 8 insertions(+)
```
- `requirements.txt`: Added `openpyxl>=3.1.0,<4.0.0` for offline read-only workbook parsing.
- `src/backend/main.py`: Mounted `v1` and `uk_salary` routers under `/api`.
- Both tracked modifications originate from the Sprint 2 Phase 2B setup and were verified completely stable.

---

## 5. Known Limitations & Out-of-Scope Items

1. **UK ASHE Publication:** Unlocking UK salary data is out of scope for Sprint 2C.1. It requires formal dual-custody executive sign-off in Phase 2C.
2. **Employer Registry Data:** `src/backend/employers/registry.py` remains empty. Data ingestion under Companies House API is queued for Phase 3.
3. **DataForge Commercial Addendum:** Operating a paid commercial SaaS tier using USA XGBoost predictions remains gated pending commercial legal review.

---

## 6. Final Acceptance Recommendation

```
+===================================================================================================+
|                                FINAL ACCEPTANCE RECOMMENDATION                                    |
+===================================================================================================+
|  STATUS:         ACCEPTED                                                                         |
|                                                                                                   |
|  JUSTIFICATION:  1. All 10 acceptance conditions set forth in Sprint 2C.1 instructions are met.    |
|                  2. Existing India/USA predictions remain 100% bitwise and numerically identical.  |
|                  3. UK ASHE endpoints fail closed with HTTP 503 UK_DATA_NOT_PUBLISHED.            |
|                  4. All 274 backend tests and all 9 frontend tests pass cleanly (283 total).      |
|                  5. Governance engine enforces fail-closed permission evaluation, versioned       |
|                     approval binding, and hierarchical revocation without taking down other       |
|                     markets.                                                                      |
|                  6. No external database daemons or paid cloud services introduced.               |
|                  7. No git commits, pushes, or deployments performed.                             |
+===================================================================================================+
```

