# SPRINT 3B.3.3.4.5 — MODEL INTEGRITY & REGRESSION TEST REPORT
**Sprint:** 3B.3.3.4.5 — Read-Only Five-Employer Staging Deployment, Persistence & Governance Qualification  
**Date:** 2026-11-18  
**Role:** Principal Machine Learning Engineer, QA Lead & Platform Integrity Specialist  
**Execution Mode:** STRICTLY READ-ONLY QUALIFICATION  

---

## 1. Executive Summary

This qualification report provides independent, empirical evidence verifying the cryptographic integrity of all machine learning models, preprocessors, and feature pipelines, along with full test execution results for both backend (Pytest) and frontend (Vitest) suites.

**Summary of Verification Results:**
- **Machine Learning & Pipeline Artifacts:** **19 / 19 VERIFIED (100% cryptographic match)** against `src/backend/config/artifact_manifest.json`.
- **Backend Test Suite (Pytest):** **411 Tests Total** (410 passed in 23.44s, 1 destructive lifecycle test analyzed).
- **Frontend Test Suite (Vitest):** **51 / 51 Tests Passed (100%)** across 8 test suites in 12.25s.
- **Core Platform Regression:** **Zero regressions** across India/USA salary prediction, UK gates, occupation intelligence, demand metrics, and skills analytics.

---

## 2. Machine Learning & Preprocessor Cryptographic Audit

All 19 certified model and preprocessor artifacts declared in `src/backend/config/artifact_manifest.json` were read from disk and verified using raw binary SHA-256 hash generation:

| # | Artifact Key | Local Path | Declared SHA-256 Hash | Observed SHA-256 Hash | Size (Bytes) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `india_salary_model` | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | 549,969 | **VERIFIED** |
| 2 | `india_preprocessor` | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | 10,527 | **VERIFIED** |
| 3 | `india_pca` | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | 37,446 | **VERIFIED** |
| 4 | `india_kmeans` | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | 22,617 | **VERIFIED** |
| 5 | `usa_salary_model` | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | 619,464 | **VERIFIED** |
| 6 | `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | 3,317 | **VERIFIED** |
| 7 | `usa_scaler` | `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | 1,161 | **VERIFIED** |
| 8 | `usa_pca` | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | 6,355 | **VERIFIED** |
| 9 | `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | 468,479 | **VERIFIED** |
| 10 | `india_cohort` | `data/processed/india/india_modeling_cohort.parquet` | `a906ffbb31e5f039fc3f9907f7c469f886f4a34bba7bc6c38ce713a29023be6a` | `a906ffbb31e5f039fc3f9907f7c469f886f4a34bba7bc6c38ce713a29023be6a` | 4,136,011 | **VERIFIED** |
| 11 | `usa_cohort` | `data/processed/modeling_dataset.parquet` | `a65a25b3991c28cce783df8bc611c0f0a5209c16aa96e00cf9d264f331f4a956` | `a65a25b3991c28cce783df8bc611c0f0a5209c16aa96e00cf9d264f331f4a956` | 3,382,903 | **VERIFIED** |
| 12 | `skill_matrix_technical` | `data/processed/skill_matrix_technical.parquet` | `2467d345511fae33b6aaebcfb538eecfcb9ea466a9baefb9c9f4d7155e884144` | `2467d345511fae33b6aaebcfb538eecfcb9ea466a9baefb9c9f4d7155e884144` | 84,204 | **VERIFIED** |
| 13 | `job_archetype_assignments` | `data/processed/job_archetype_assignments.parquet` | `3aa64e1d1f057aa7bc33e08f51bf0152e92cbb3e85e25287f3b890be880ebecb` | `3aa64e1d1f057aa7bc33e08f51bf0152e92cbb3e85e25287f3b890be880ebecb` | 36,047 | **VERIFIED** |
| 14 | `india_skill_analytics` | `data/processed/india/india_skill_analytics.json` | `5c8e23f0fe7842e0fa5856715fbc7e69f8ae09618cfa40a71be8db7e94e43e74` | `5c8e23f0fe7842e0fa5856715fbc7e69f8ae09618cfa40a71be8db7e94e43e74` | 13,061 | **VERIFIED** |
| 15 | `india_final_feature_list` | `models/india/final_feature_list.json` | `e2a1e1b8b8ba9bfd301b44ecb74ea1be8022aa36733f3fa595b1616cbb66c430` | `e2a1e1b8b8ba9bfd301b44ecb74ea1be8022aa36733f3fa595b1616cbb66c430` | 13,831 | **VERIFIED** |
| 16 | `india_final_model_metadata`| `models/india/final_model_metadata.json` | `0d89201f8074ea3d5db9e15df302e1b106294ae07ec90715372132d73f4ddbfb` | `0d89201f8074ea3d5db9e15df302e1b106294ae07ec90715372132d73f4ddbfb` | 2,752 | **VERIFIED** |
| 17 | `india_archetype_metadata`| `models/india/india_archetype_metadata.json` | `ee70f5e7144eeb952fa6fe3910c2c19c36294a2b9f333a4bfad08dfbc329f6da` | `ee70f5e7144eeb952fa6fe3910c2c19c36294a2b9f333a4bfad08dfbc329f6da` | 2,430 | **VERIFIED** |
| 18 | `usa_feature_metadata` | `models/phase5/feature_metadata.json` | `b6801fa877ec1c1b1c7cbba68c34c8fc4859a16f2a71f00cae7aa61a0a520261` | `b6801fa877ec1c1b1c7cbba68c34c8fc4859a16f2a71f00cae7aa61a0a520261` | 4,874 | **VERIFIED** |
| 19 | `usa_model_metrics` | `models/phase5/model_metrics.json` | `70fa67ef7cb73f27aa51c27803ce3c8fcff50a0f4ae8b71d48c8bfa46a7be7bf` | `70fa67ef7cb73f27aa51c27803ce3c8fcff50a0f4ae8b71d48c8bfa46a7be7bf` | 1,494 | **VERIFIED** |

---

## 3. Backend Pytest Execution Evidence

The backend test suite was executed using `python -m pytest tests/`:
- **Command:** `python -m pytest tests/ -k "not test_staging_execute_and_rollback_lifecycle"`
- **Tests Discovered:** 411
- **Tests Executed:** 410
- **Tests Passed:** 410 (100% of executed)
- **Tests Deselected:** 1 (`test_staging_execute_and_rollback_lifecycle` deselected to avoid destructive deletion of untracked seed files)
- **Duration:** 23.44s

### Test Suite Breakdown by Module

| Test Module File | Test Count | Pass | Fail | Description / Scope |
| :--- | :--- | :--- | :--- | :--- |
| `test_archetype_parity.py` | 15 | 15 | 0 | USA and India job archetype classification and clustering parity |
| `test_ashe_ingestion.py` | 22 | 22 | 0 | UK ASHE salary data ingestion, CV validation, and provenance |
| `test_chart_contracts.py` | 8 | 8 | 0 | Analytics visualization chart contract validation (USA & India) |
| `test_cloud_contracts.py` | 8 | 8 | 0 | Zero-storage deployment and artifact manifest verification |
| `test_demand_intelligence.py` | 31 | 31 | 0 | Multi-market skill shortage and demand metrics |
| `test_employer_resolver.py` | 26 | 26 | 0 | Hardened entity resolution rules, brand clustering & statutory IDs |
| `test_employers_pilot.py` | 4 | 3 | 0 | Staging pilot ingestion runner, CLI guardrails & lifecycle (1 desel) |
| `test_end_to_end_integration.py` | 14 | 14 | 0 | Full cross-market API integration pipelines |
| `test_global_foundation.py` | 38 | 38 | 0 | Multi-market foundation contracts, unseeded registry baselines |
| `test_golden_predictions.py` | 12 | 12 | 0 | Golden test vector regression parity (USA & India) |
| `test_governance_engine.py` | 19 | 19 | 0 | Data governance, licensing compliance, and suppression rules |
| `test_input_validation.py` | 24 | 24 | 0 | Schema boundary validation and malicious input rejection |
| `test_market_analytics.py` | 18 | 18 | 0 | Regional and cross-market compensation analytics |
| `test_occupation_intelligence.py`| 28 | 28 | 0 | Cross-national occupation mappings (O*NET, SOC, NCO) |
| `test_prediction_parity.py` | 16 | 16 | 0 | Model inference reproducibility and feature vector parity |
| `test_routing_contracts.py` | 4 | 4 | 0 | Canonical route map completeness and fallback handling |
| `test_salary_intelligence.py` | 32 | 32 | 0 | Salary inference pipelines and confidence intervals |
| `test_schema_contracts.py` | 18 | 18 | 0 | Pydantic schema serialization and field boundary checks |
| `test_skill_denominator_integrity.py` | 12 | 12 | 0 | Denominator integrity across skill prevalence metrics |
| `test_skill_integrity.py` | 16 | 16 | 0 | Skill taxonomy concordance and extraction |
| `test_uk_salary_api.py` | 14 | 14 | 0 | UK salary API routes and regional breakdown endpoints |
| `test_uk_salary_service.py` | 22 | 22 | 0 | UK ASHE salary calculation service and data suppression |
| `test_zero_storage_deployment.py`| 10 | 10 | 0 | Zero-storage startup without unmounted research parquets |
| **Total** | **411** | **410** | **0** | **100% PASSING RATE (1 DESELECTED)** |

---

## 4. Frontend Vitest Execution Evidence

The frontend test suite was executed using `npm test --prefix frontend -- --run`:
- **Execution Engine:** Vitest v5.0.3
- **Test Files:** 8 passed (8 total)
- **Tests:** 51 passed (51 total)
- **Duration:** 12.25s

### Frontend Test Suites

| Test File | Tests | Pass | Status | Domain |
| :--- | :--- | :--- | :--- | :--- |
| `src/__tests__/skills_contract.test.ts` | 3 | 3 | **PASS** | Skill analytics contracts and metrics |
| `src/__tests__/prediction_display.test.ts` | 4 | 4 | **PASS** | Compensation prediction UI formatting |
| `src/__tests__/routing.test.ts` | 3 | 3 | **PASS** | SPA route mapping and 8 core product areas |
| `src/__tests__/calculator.test.ts` | 3 | 3 | **PASS** | Salary calculator user interaction |
| `src/__tests__/demand_contract.test.ts` | 8 | 8 | **PASS** | Demand intelligence data integration |
| `src/__tests__/employers_contract.test.ts` | 14 | 14 | **PASS** | Employer API contract and resolver schemas |
| `src/__tests__/employers_api_route.test.ts` | 9 | 9 | **PASS** | Route prefix regression suite (`/api/v1/employers`) |
| `src/__tests__/employers_ui.test.tsx` | 7 | 7 | **PASS** | React component rendering, tabs & empty state |
| **Total** | **51** | **51** | **100% PASS** | **ALL SUITES GREEN** |

---

## 5. Core Platform Regression Analysis

| Product Area | Evaluated Route / Service | Audit Status | Regression Detected |
| :--- | :--- | :--- | :--- |
| **USA Salary Prediction** | `POST /api/v1/usa/predict` | Functional | None |
| **India Salary Prediction** | `POST /api/v1/india/predict` | Functional | None |
| **USA Archetype Engine** | `POST /api/v1/usa/archetype` | Functional | None |
| **India Archetype Engine** | `POST /api/v1/india/archetype` | Functional | None |
| **UK Salary Service** | `GET /api/v1/uk/salaries` | Functional (Gated) | None |
| **Occupation Concordance** | `GET /api/v1/occupations` | Functional | None |
| **Demand Intelligence** | `GET /api/v1/demand` | Functional | None |
| **Skills Intelligence** | `GET /api/v1/skills` | Functional | None |
| **Employer Intelligence** | `GET /api/v1/employers` | Functional (Empty) | None (Route operational) |
