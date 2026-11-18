# SPRINT 3B.3.3.4.4 — TEST AND ARTIFACT INTEGRITY REPORT
**Sprint:** 3B.3.3.4.4 — Controlled Five-Employer Staging Ingestion, Provenance Validation & Live Registry Qualification  
**Date:** 2026-11-18  
**Role:** Principal QA Lead, Automated Testing Specialist & DevOps Engineer  
**Status:** 100% PASSED — ZERO REGRESSIONS

---

## 1. Test Suite Execution Summary

All automated test suites across backend and frontend repositories were executed in the staging environment.

```
+-------------------------------------------------------------------------------+
| Test Suite          | Files | Tests Run | Passed | Failed | Duration | Pass % |
+---------------------+-------+-----------+--------+--------+----------+--------+
| Backend Pytest      | 14    | 411       | 411    | 0      | 40.03s   | 100%   |
| Frontend Vitest     | 8     | 51        | 51     | 0      | 3.55s    | 100%   |
+---------------------+-------+-----------+--------+--------+----------+--------+
| Total Automated     | 22    | 462       | 462    | 0      | 43.58s   | 100%   |
+-------------------------------------------------------------------------------+
```

---

## 2. Backend Pytest Execution Evidence

```
$ python -m pytest tests -q
........................................................................ [ 17%]
........................................................................ [ 35%]
........................................................................ [ 52%]
........................................................................ [ 70%]
........................................................................ [ 87%]
...................................................                      [100%]
411 passed in 40.03s
```

### Key Test Suite Highlights

1. **`tests/test_employers_pilot.py` (4 tests):**
   - `test_production_environment_is_strictly_forbidden` — **PASSED**
   - `test_candidate_profiles_pydantic_schema_and_counts` — **PASSED**
   - `test_dry_run_validation_passes` — **PASSED**
   - `test_staging_execute_and_rollback_lifecycle` — **PASSED**
2. **`tests/test_global_foundation.py` (26 tests):**
   - Verified empty registry contract, market catalogs, observation models, and additive `/api/v1` routes — **26 PASSED**
3. **`tests/test_employer_resolver.py` (32 tests):**
   - Verified 32 adversarial, cross-market, statutory ID, and pagination test cases — **32 PASSED**
4. **All Regression Suites (349 tests):**
   - India salary prediction, USA salary prediction, UK ASHE ingestion, Cloud contracts, routing contracts, and governance rules — **349 PASSED**

---

## 3. Frontend Vitest Execution Evidence

```
$ cd frontend; npx vitest run

 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/routing.test.ts (3 tests)
 ✓ src/__tests__/prediction_display.test.ts (4 tests)
 ✓ src/__tests__/employers_contract.test.ts (14 tests)
 ✓ src/__tests__/calculator.test.ts (3 tests)
 ✓ src/__tests__/skills_contract.test.ts (3 tests)
 ✓ src/__tests__/demand_contract.test.ts (8 tests)
 ✓ src/__tests__/employers_api_route.test.ts (9 tests)
 ✓ src/__tests__/employers_ui.test.tsx (7 tests)

 Test Files  8 passed (8)
      Tests  51 passed (51)
   Duration  3.55s
```

---

## 4. Cryptographic Artifact Checksum Manifest

All 19 machine learning models, preprocessors, and foundational data tables recorded in `src/backend/config/artifact_manifest.json` were verified via automated SHA-256 hashing.

| Artifact Path | Expected SHA-256 | Actual SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `models/india/xgb_model.json` | `f87928e08daee8ee12adad0c20173dbfba8ce74ec45fb7ec982eebe9b168a44b` | `f87928e08daee8ee12adad0c20173dbfba8ce74ec45fb7ec982eebe9b168a44b` | **MATCH** |
| `models/india/catboost_model.cbm` | `bc2c8e31e67fa807530510dd169beea0622204c3cf26bf46c3ef6d028b0304ec` | `bc2c8e31e67fa807530510dd169beea0622204c3cf26bf46c3ef6d028b0304ec` | **MATCH** |
| `models/india/lightgbm_model.txt` | `a37ea18b2b6477d9f78cc9d2ea06cbfe5283f6f9efc53db199949603fb86e680` | `a37ea18b2b6477d9f78cc9d2ea06cbfe5283f6f9efc53db199949603fb86e680` | **MATCH** |
| `models/india/gradient_boosting_model.joblib` | `88370d069695d7eb8f714eb61f365d95cf27ffb4e8e19c01c0db9f1b2b801452` | `88370d069695d7eb8f714eb61f365d95cf27ffb4e8e19c01c0db9f1b2b801452` | **MATCH** |
| `models/india/random_forest_model.joblib` | `9d554a991f8687a4128032d66050b1bc01d51a66ff55938bf76f3f01c4e7fae4` | `9d554a991f8687a4128032d66050b1bc01d51a66ff55938bf76f3f01c4e7fae4` | **MATCH** |
| `models/india/preprocessor.joblib` | `05ffc4f52f4c45b78ff3bfb0660424a106f2ba0646c8e3c49a60e0a53b218408` | `05ffc4f52f4c45b78ff3bfb0660424a106f2ba0646c8e3c49a60e0a53b218408` | **MATCH** |
| `models/usa/catboost_model.cbm` | `8db891d4e0407a111a43a7582b27aa497df5a3c9b7e7a858e99881ae9320e6f6` | `8db891d4e0407a111a43a7582b27aa497df5a3c9b7e7a858e99881ae9320e6f6` | **MATCH** |
| `models/usa/lightgbm_model.txt` | `9b578c773121546736203cf3f99339e5539ff51f158976df022dfad97394ca51` | `9b578c773121546736203cf3f99339e5539ff51f158976df022dfad97394ca51` | **MATCH** |
| `models/usa/xgboost_model.json` | `5c7e1933bf9e2c60e33ef74ffc1555fe8dc3cf305f88fc30f55098ffbe61f00d` | `5c7e1933bf9e2c60e33ef74ffc1555fe8dc3cf305f88fc30f55098ffbe61f00d` | **MATCH** |
| `models/usa/gradient_boosting_model.joblib` | `77d13b7782161cc46124707611a91cf64b8bb26cbaae188cb8292c3a504ef564` | `77d13b7782161cc46124707611a91cf64b8bb26cbaae188cb8292c3a504ef564` | **MATCH** |
| `models/usa/random_forest_model.joblib` | `9280d90d80c06155ee032e361239c948b3b44b8ee0b753d6ebef4fc3e887d1df` | `9280d90d80c06155ee032e361239c948b3b44b8ee0b753d6ebef4fc3e887d1df` | **MATCH** |
| `models/usa/preprocessor.joblib` | `b3c0cce5e2526e033989c745fc307613768f533a1e95fc1d7c0f188fa6c57fba` | `b3c0cce5e2526e033989c745fc307613768f533a1e95fc1d7c0f188fa6c57fba` | **MATCH** |
| `data/processed/ashe_2025_revised/dataset.parquet` | `6689d608c996ce1efbbf82bd5b9fef3f4fab01cd1a2f1cafba0b5931d9bb6ba9` | `6689d608c996ce1efbbf82bd5b9fef3f4fab01cd1a2f1cafba0b5931d9bb6ba9` | **MATCH** |

---

## 5. Ingestion Seed Manifest Integrity

- **File Path:** `data/processed/staging_employers.json`
- **Computed SHA-256:** `0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5`
- **Record Count:** Exactly 5 validated profiles
- **Encoding:** UTF-8 JSON formatted with sorted keys
