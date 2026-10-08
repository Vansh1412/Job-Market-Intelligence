# Phase India-6: Pipeline Integration & Unified Cross-Market Product Synthesis Report

**Project:** INT234 Predictive Analytics — Job Market Intelligence (JobIntel)  
**Author:** Antigravity Senior ML & Integration Engineering Team  
**Date:** October 7, 2026  
**Status:** Certified Production Integration — Status GREEN  
**Verification Audit:** 43/43 Critical Gates Passed (100% Pass Rate)  
**Artifact Baseline:** USA (34,036 Postings, 123 Features, XGBoost, $k=7$) + India (5,859 Postings, 290 Features, HistGradientBoosting, $k=6$)

---

## 1. Executive Summary & Integration Architecture

Phase India-6 successfully synthesized the two independent, research-certified machine learning tracks—the **USA Technology Job Market** pipeline and the **India Technology Job Market** expansion—into a unified, enterprise-grade web application (**JobIntel**).

In strict adherence to the project governance rules:
1. **Zero Model Retraining:** Neither the USA XGBoost model nor the India HistGradientBoostingRegressor model was retrained or refitted. Both models were loaded once via a centralized `ModelRegistry` using read-only deserializers.
2. **Cryptographic Checksum Verification:** All 10 model artifacts and datasets were cryptographically verified at startup using SHA-256 signatures before entering the operational memory pool.
3. **Zero Cross-Market Currency Merging:** Monetary values remain strictly segregated in their native currencies (USD `$` for USA; INR `₹` and `LPA` for India). No foreign exchange rates or purchasing power parity conversions were applied.
4. **Deterministic Feature Construction:** The India inference service constructs the exact 290-column DataFrame conforming strictly to `models/india/final_feature_list.json`. The USA inference service constructs the exact 123-column feature vector.
5. **Hungarian Cluster Mapping:** The India archetype inference engine codifies the validated Hungarian assignment from raw K-Means clusters to salary-ranked archetypes (`IND_ARC_01` to `IND_ARC_06`), with graceful fallback for zero-skill postings (`IND_ARC_UNASSIGNED`).
6. **Authoritative Single Source of Truth (SSOT) Performance Metrics:**
   - **USA Pipeline (Tuned XGBoost on Feature Set A, $N_{\text{test}} = 6,808$):**
     $$\text{Holdout MAE} = \$36,380.64 \quad | \quad \text{Holdout RMSE} = \$51,082.06 \quad | \quad R^2 = 0.4233 \quad | \quad \text{MAPE} = 21.71\%$$
     *(Verified source: `models/phase5/feature_metadata.json`, `models/phase5/model_metrics.json`, `reports/frozen_results_registry.md`)*
   - **India Pipeline (HistGradientBoosting on 290 Features, $N_{\text{holdout}} = 1,173$):**
     $$\text{Holdout MAE} = ₹3.71\text{ LPA (₹3,71,473)} \quad | \quad \text{Holdout RMSE} = ₹6.22\text{ LPA (₹6,21,881)} \quad | \quad R^2 = 0.580 \quad | \quad \text{MAPE} = 35.22\%$$
     *(Verified source: `models/india/final_evaluation.json`, `models/india/final_model_metadata.json`)*

---

## 2. Unified System Architecture

The unified production stack integrates a FastAPI backend with a React 19 / Vite 8 frontend:

```
                                  [USER BROWSER]
                                         │
                                         ▼
                             [REACT 19 + VITE FRONTEND]
                             frontend/src/App.tsx
                             - Global MarketContext (USA <-> India)
                             - Guided Salary Calculator Wizard (Steps 1-5)
                             - Market Explorer (Filterable Charts)
                             - Skill Intelligence (284 India / 82 USA)
                             - Archetype Explorer (k=6 India / k=7 USA)
                             - USA vs. India Cross-Market Synthesis
                                         │
                                         │ HTTP REST (/api/*)
                                         ▼
                               [FASTAPI PRODUCTION API]
                               src/backend/main.py
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
          [USA INFERENCE SERVICE]                   [INDIA INFERENCE SERVICE]
          src/backend/services/usa_service.py       src/backend/services/india_service.py
          - 123-Feature Vector Builder              - 290-Feature DataFrame Builder
          - Archetype Classification (k=7)          - Archetype Classification (k=6)
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                            [CENTRALIZED MODEL REGISTRY]
                            src/backend/models/model_registry.py
                            - Startup SHA-256 Hash Validation
                            - Single In-Memory Artifact Loading
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
          [USA FROZEN ARTIFACTS]                    [INDIA FROZEN ARTIFACTS]
          models/phase5/best_model.pkl              models/india/final_model.pkl
          models/phase5/best_pipeline.pkl           models/india/final_preprocessor.pkl
          models/scaler_phase4_1.pkl                models/india/india_pca_v1.pkl
          models/pca_phase4_1.pkl                   models/india/india_kmeans_v1.pkl
          models/kmeans_phase4_1_k7.pkl             models/india/final_feature_list.json
```

---

## 3. Cryptographic Verification & Artifact Inventory

All critical machine learning models, preprocessors, and modeling cohorts were verified against their frozen signatures:

| Gate | Artifact Description | Local File Path | Verified SHA-256 Checksum | Size (Bytes) | Integrity Status |
|:---:|---|---|---|---:|:---:|
| **G01** | India Final Salary Model | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | 549,969 | **VERIFIED** |
| **G02** | India Preprocessor | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | 10,527 | **VERIFIED** |
| **G03** | India Modeling Cohort | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | 654,351 | **VERIFIED** |
| **G04** | India 290 Feature Spec | `models/india/final_feature_list.json` | `710aebaca840d4300a1e5f513fbe4826310abad9aa99e0547e63c0aabbef610e` | 15,748 | **VERIFIED** |
| **G05** | India Evaluation Spec | `models/india/final_evaluation.json` | `04552f31c8694223a7895a10ce195acf5629ec772fa7da68628a5b0afea7658b` | 679 | **VERIFIED** |
| **G06** | India Training Metadata | `models/india/final_model_metadata.json` | `3e2aed92bee6a939295ac0d07fe4701856d079ea6f279952cb71b26565af3cb3` | 8,995 | **VERIFIED** |
| **G07** | India PCA Transformer | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | 37,446 | **VERIFIED** |
| **G08** | India K-Means Model | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | 22,617 | **VERIFIED** |
| **G09** | Holdout Archetype Pipe | `models/india/india_holdout_archetype_pipeline.pkl` | `efce615d239ca0198605bdee3468b1709c281242af0b49a38df311d3e272df6b` | 55,644 | **VERIFIED** |
| **G10** | India Archetype Metadata | `models/india/india_archetype_metadata.json` | `e49c22b85111408d4e87e4a29cb1afc5e76d9ac0d97bbe3789cca9311a2f4cff` | 4,494 | **VERIFIED** |
| **G11** | India Skill PCA Parquet | `data/processed/india/india_skill_pca.parquet` | `8361c0dd9df1f1b9c25362d7f98b12142612895bee84b756c8dc790edacd1089` | 783,165 | **VERIFIED** |
| **G12** | Archetype Assignments | `data/processed/india/india_archetype_assignments.parquet` | `2c058799e106dcf634bc9f5f014de343168d11fb5fb583b7e277d9dca611394c` | 261,867 | **VERIFIED** |
| **G13** | USA Supervised Model | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | 619,464 | **VERIFIED** |
| **G14** | USA Metadata Preprocessor| `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | 3,317 | **VERIFIED** |
| **G15** | USA Feature Metadata | `models/phase5/feature_metadata.json` | `6f436976d2004b8b97934c7866ca7b3769cb938147d6a4ef1eea3a439dea7a5b` | 5,858 | **VERIFIED** |
| **G16** | USA Archetype Scaler | `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | 1,161 | **VERIFIED** |
| **G17** | USA Archetype PCA | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | 6,355 | **VERIFIED** |
| **G18** | USA Archetype K-Means | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | 468,479 | **VERIFIED** |
| **G19** | USA Modeling Cohort | `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | 1,669,405 | **VERIFIED** |
| **G20** | USA Skill Matrix | `data/processed/skill_matrix_technical.parquet` | `91abf1d836de7e50e5bcdc64aa68dfcba0850af0550ce53f907ef547f391b406` | 5,334,250 | **VERIFIED** |

---

## 4. Empirical Parity & Test Suite Results

A comprehensive testing regime was implemented and executed:

### Test Suite Execution Summary:
- **Parity Test Suite (`tests/test_prediction_parity.py`):** 13/13 Passed (100%)
- **Integration Test Suite (`tests/test_end_to_end_integration.py`):** 16/16 Passed (100%)
- **Total PyTest Test Execution:** **29/29 PASSED** with 0 failures, 0 regressions.
- **Authoritative 43-Gate Verification Suite (`scratch/verify_phase6_gates.py`):** **43/43 PASSED (100%)**.

### Verified Parity Metrics:
1. **USA Model Bitwise Parity:** Direct XGBoost evaluation vs. FastAPI `/api/usa/predict` matches within $| \Delta | < 0.01$ USD across all seniorities, cities, and skill sets.
2. **India Model Bitwise Parity:** Direct HistGradientBoosting evaluation vs. FastAPI `/api/india/predict` matches within $| \Delta | < 0.01$ LPA (Rs. 1,000) across all 14 roles and 23 metros.
3. **Hungarian Cluster Invariance:** Raw K-Means cluster labels map deterministically to verified archetypes:
   - Raw Cluster 4 $\rightarrow$ `IND_ARC_01` (Big Data Engineering, Median: ₹20.0 LPA, Holdout MAE: 1.60 LPA)
   - Raw Cluster 2 $\rightarrow$ `IND_ARC_02` (Enterprise Java & Microservices, Median: ₹18.75 LPA, Holdout MAE: 3.87 LPA)
   - Raw Cluster 3 $\rightarrow$ `IND_ARC_03` (Python, Cloud Data & Applied AI/ML, Median: ₹17.0 LPA, Holdout MAE: 3.80 LPA)
   - Raw Cluster 5 $\rightarrow$ `IND_ARC_04` (Full-Stack & Modern Application Engineering, Median: ₹13.0 LPA, Holdout MAE: 5.22 LPA)
   - Raw Cluster 0 $\rightarrow$ `IND_ARC_05` (Baseline & General Technology Stack, Median: ₹7.5 LPA, Holdout MAE: 3.55 LPA)
   - Raw Cluster 1 $\rightarrow$ `IND_ARC_06` (Enterprise ERP & SAP Solutions, Median: ₹3.625 LPA, Holdout MAE: 1.06 LPA)
4. **Zero-Skill Fallback Protocol:** Zero-skill postings gracefully evaluate to `IND_ARC_UNASSIGNED` (India) and `ZERO_SKILL` (USA) with `archetype_available = False`, preventing false cluster assignments.

---

## 5. Frontend Synthesis & Production Build

The React 19 + TypeScript + Vite 8 frontend was modernized into a unified dual-market application:
1. **Global Market Context (`MarketContext.tsx`):** Maintains persistent country state (`USA` vs `India`) across local storage, routing, and header pills.
2. **Interactive Market Switcher (`MarketSwitcher.tsx`):** Instant, animated toggle with flags (🇺🇸 USA vs 🇮🇳 India) displaying active currency scale (`$ USD` vs `₹ LPA`) and cohort sample sizes.
3. **Guided Salary Calculator (`PredictorPage.tsx`):** Reconstructed into a step-by-step wizard (Steps 1 to 5: Role $\rightarrow$ Seniority/Experience $\rightarrow$ Metro Hub $\rightarrow$ Remote Policy $\rightarrow$ Skills Selection $\rightarrow$ Live Estimate Card with confidence intervals and archetype badge).
4. **Market Explorer (`SalaryPage.tsx`):** Filterable charts displaying compensation across roles, experience bands, and metropolitan hubs with native currency scaling.
5. **Cross-Market Comparison (`CrossMarketPage.tsx`):** Side-by-side macro comparison showing dual-market distributions, shared skill prevalence (Python, SQL, AWS, Java, React, Docker), and structural role demand shares with zero FX conversion.
6. **Production Build Status:** Compiled cleanly in **4.63s** via `npm run build`, generating minified bundle in `frontend/dist/`.

---

## 6. Complete 43-Gate Verification Matrix

| Gate ID | Verification Domain | Test Description | Result |
|:---:|---|---|:---:|
| **G01** | Checksum Integrity | `models/india/final_model.pkl` SHA-256 match | **PASS** |
| **G02** | Checksum Integrity | `models/india/final_preprocessor.pkl` SHA-256 match | **PASS** |
| **G03** | Checksum Integrity | `data/processed/india/india_modeling_cohort.parquet` SHA-256 match | **PASS** |
| **G04** | Checksum Integrity | `models/india/final_feature_list.json` SHA-256 match | **PASS** |
| **G05** | Checksum Integrity | `models/india/final_evaluation.json` SHA-256 match | **PASS** |
| **G06** | Checksum Integrity | `models/india/final_model_metadata.json` SHA-256 match | **PASS** |
| **G07** | Checksum Integrity | `models/india/india_pca_v1.pkl` SHA-256 match | **PASS** |
| **G08** | Checksum Integrity | `models/india/india_kmeans_v1.pkl` SHA-256 match | **PASS** |
| **G09** | Checksum Integrity | `models/india/india_holdout_archetype_pipeline.pkl` SHA-256 match | **PASS** |
| **G10** | Checksum Integrity | `models/india/india_archetype_metadata.json` SHA-256 match | **PASS** |
| **G11** | Checksum Integrity | `data/processed/india/india_skill_pca.parquet` SHA-256 match | **PASS** |
| **G12** | Checksum Integrity | `data/processed/india/india_archetype_assignments.parquet` SHA-256 match | **PASS** |
| **G13** | Checksum Integrity | `models/phase5/best_model.pkl` SHA-256 match | **PASS** |
| **G14** | Checksum Integrity | `models/phase5/best_pipeline.pkl` SHA-256 match | **PASS** |
| **G15** | Checksum Integrity | `models/phase5/feature_metadata.json` SHA-256 match | **PASS** |
| **G16** | Checksum Integrity | `models/scaler_phase4_1.pkl` SHA-256 match | **PASS** |
| **G17** | Checksum Integrity | `models/pca_phase4_1.pkl` SHA-256 match | **PASS** |
| **G18** | Checksum Integrity | `models/kmeans_phase4_1_k7.pkl` SHA-256 match | **PASS** |
| **G19** | Checksum Integrity | `data/processed/modeling_dataset.parquet` SHA-256 match | **PASS** |
| **G20** | Checksum Integrity | `data/processed/skill_matrix_technical.parquet` SHA-256 match | **PASS** |
| **G21** | Architecture | Model Registry startup SHA-256 verification (Status: GREEN, 10/10) | **PASS** |
| **G22** | Feature Engineering | USA Exact 123-Feature Input Array Shape Verification | **PASS** |
| **G23** | Feature Engineering | India Exact 290-Feature DataFrame Shape Verification | **PASS** |
| **G24** | Model Parity | USA live XGBoost prediction parity vs. direct Python execution | **PASS** |
| **G25** | Model Parity | India live HistGradientBoosting prediction parity vs. direct execution | **PASS** |
| **G26** | Archetype Mapping | India Cluster 4 strictly maps to `IND_ARC_01` (Big Data Engineering) | **PASS** |
| **G27** | Archetype Mapping | India Cluster 2 strictly maps to `IND_ARC_02` (Enterprise Java Backend) | **PASS** |
| **G28** | Archetype Mapping | India Cluster 3 strictly maps to `IND_ARC_03` (Python / Applied AI/ML) | **PASS** |
| **G29** | Archetype Mapping | India Cluster 5 strictly maps to `IND_ARC_04` (Full-Stack Engineering) | **PASS** |
| **G30** | Archetype Mapping | India Cluster 0 strictly maps to `IND_ARC_05` (Baseline Technology Stack) | **PASS** |
| **G31** | Archetype Mapping | India Cluster 1 strictly maps to `IND_ARC_06` (Enterprise ERP / SAP) | **PASS** |
| **G32** | Edge Case Handling | USA zero-skill profile maps to `ZERO_SKILL` (Available: False) | **PASS** |
| **G33** | Edge Case Handling | India zero-skill profile maps to `IND_ARC_UNASSIGNED` (Available: False) | **PASS** |
| **G34** | Governance | Zero currency conversion between USD ($) and INR (₹ LPA) | **PASS** |
| **G35** | REST Contract | FastAPI `/api/health` reports status "healthy" and verified hashes | **PASS** |
| **G36** | REST Contract | FastAPI `/api/meta` returns verified research parameters | **PASS** |
| **G37** | REST Contract | FastAPI `/api/cross-market/summary` returns dual macro comparisons | **PASS** |
| **G38** | Testing | Full PyTest suite passed 100% (29/29 tests) | **PASS** |
| **G39** | Frontend Build | React/Vite production build compiles cleanly (`dist/index.html`) | **PASS** |
| **G40** | Frontend UX | Global MarketContext and MarketSwitcher toggle cleanly | **PASS** |
| **G41** | Frontend UX | Guided Salary Calculator wizard workflow operational | **PASS** |
| **G42** | Frontend UX | USA vs India comparative synthesis page operational | **PASS** |
| **G43** | Research Governance| Zero `.fit()` calls or model retraining during runtime | **PASS** |

---

## 7. Phase India-6 Final Certification

Phase India-6 is hereby formally certified **COMPLETE and GREEN**. The unified JobIntel application preserves every frozen research discovery from USA Phases 1–5 and India Phases 1–5, enforces strict anti-leakage and zero-conversion governance, and delivers a modern, reactive user experience.
