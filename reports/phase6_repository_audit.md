# Phase India-6: Comprehensive Repository & Integration Architecture Audit

**Project:** INT234 Predictive Analytics -- Job Market Intelligence (JobIntel)  
**Author:** Antigravity Senior ML & Integration Engineering Team  
**Date:** October 7, 2026  
**Status:** Certified Repository Audit Baseline -- Integration Phase Ready  
**Scope:** Frozen USA Pipeline + Frozen India Pipeline -> Unified JobIntel Platform  

---

## 1. Executive Summary & Audit Mandate

Phase India-6 is strictly an **integration and synthesis phase**. Its primary objective is to unite the two certified, frozen machine learning pipelines--the USA Tech Job Market pipeline (34,036 modeling cohort, 123 predictors, XGBoost regressor, $k=7$ archetypes) and the India Tech Job Market pipeline (5,859 modeling cohort, 290 predictors, HistGradientBoostingRegressor, $k=6$ archetypes)--into a single, cohesive, production-grade web application (**JobIntel**).

### Absolute Governance Constraints
1. **Zero Retraining:** Under no circumstances will the USA or India salary models be retrained, refitted, or hyperparameter-tuned.
2. **Zero Methodology Alteration:** Dimensionality reduction (PCA), clustering (K-Means), feature vocabularies, cohort definitions, and evaluation metrics are immutable.
3. **Zero Cross-Market Currency Merging:** USA predictions and statistics remain strictly in United States Dollars ($ USD). India predictions and statistics remain strictly in Indian Rupee Lakhs Per Annum (₹ LPA). Predictions must never be converted using foreign exchange rates.
4. **Zero Fabrication:** No simulated market numbers, fake prediction endpoints, or ungrounded causal claims are permitted.

This audit inspects the complete codebase across source files, models, datasets, frontend components, and analytical reports prior to any code edits.

---

## 2. End-to-End System Architecture & Dependency Map

The operational data flow connecting raw datasets to the live user experience is mapped below:

```
[USA DATA]                                                    [INDIA DATA]
data/raw/dataset_A                                            data/raw/india/indian-job-market-dataset-2025.xlsx
     │                                                             │
     ▼                                                             ▼
[USA PREPROCESSING]                                           [INDIA PREPROCESSING]
src/phase5/preprocessing.py                                   src/india/cleaning.py, role_mapping.py, feature_engineering.py
data/processed/modeling_dataset.parquet (N=34,036)            data/processed/india/india_modeling_cohort.parquet (N=5,859)
data/processed/skill_matrix_technical.parquet (N=335,995)     284 Curated Technical Skills (98.58% Sparsity)
     │                                                             │
     ├──────────────────────────┐                                  ├──────────────────────────┐
     ▼                          ▼                                  ▼                          ▼
[USA SALARY MODEL]      [USA ARCHETYPES]                     [INDIA SALARY MODEL]    [INDIA ARCHETYPES]
models/phase5/          models/                              models/india/           models/india/
best_model.pkl          scaler_phase4_1.pkl                  final_model.pkl         india_pca_v1.pkl (15 PCs)
best_pipeline.pkl       pca_phase4_1.pkl                     final_preprocessor.pkl  india_kmeans_v1.pkl (K=6)
(123 Predictors,        kmeans_phase4_1_k7.pkl               (290 Predictors,        5,323 Skill-Bearing Postings
 XGBoost Regressor)     (82 Skills -> K=7)                   HistGradientBoosting)   (IND_ARC_01 to IND_ARC_06)
     │                          │                                  │                          │
     └─────────────┬────────────┘                                  └─────────────┬────────────┘
                   │                                                             │
                   ▼                                                             ▼
        [USA INFERENCE SERVICE]                                       [INDIA INFERENCE SERVICE]
        src/backend/services/usa_service.py                           src/backend/services/india_service.py
                   │                                                             │
                   └──────────────────────────────┬──────────────────────────────┘
                                                  ▼
                                      [UNIFIED MODEL REGISTRY]
                                      src/backend/models/model_registry.py
                                      - Startup SHA-256 Hash Verification
                                      - Single In-Memory Artifact Loading
                                                  │
                                                  ▼
                                       [FASTAPI BACKEND SERVICE]
                                       src/backend/main.py
                                       - /api/usa/* (Options, Predict, Archetype, Market)
                                       - /api/india/* (Options, Predict, Archetype, Market)
                                       - /api/cross-market/* (Comparative Analytics)
                                                  │
                                                  ▼
                                      [REACT + VITE FRONTEND APP]
                                      frontend/src/App.tsx
                                      - Country State Switcher (USA <-> India)
                                      - Guided Salary Calculator
                                      - Market Explorer (8 Filterable Visualizations)
                                      - Archetype Taxonomy Navigator
                                      - Cross-Market Comparative Intelligence
                                                  │
                                                  ▼
                                          [USER EXPERIENCE]
                                  JobIntel Live Interactive Experience
```

---

## 3. Existing Backend Audit (`src/backend/`)

### Current Structure:
- `src/backend/main.py`: FastAPI entrypoint exposing 33 endpoints across 8 routers.
- `src/backend/inference_service.py`: Contains live inference for the USA XGBoost model and $k=7$ archetype assignment.
- `src/backend/data_service.py`: Loads USA models and analytical CSV tables using `@lru_cache`.
- `src/backend/routers/`: 8 domain routers (`overview`, `salary`, `skills`, `archetypes`, `predict`, `models`, `error_analysis`, `methodology`).

### Key Audit Findings & Deficiencies:
1. **100% USA Centricity:** The current backend exclusively supports the USA pipeline. There are zero endpoints for India salary predictions, zero endpoints for India archetype assignments, and zero endpoints for cross-market comparisons.
2. **Absence of Unified Model Registry:** Models are loaded through disparate functions in `data_service.py` without cryptographic checksum checks on startup.
3. **Hardcoded Metadata Baseline:** `inference_service.py` hardcodes `COHORT_BASELINE = 180413.0` rather than sourcing baseline values dynamically from metadata.
4. **Ad-Hoc Distribution Percentiles:** `predict.py` injects hardcoded quantile points (`[95000, 140000, 180413, 225000, 275000]`) rather than generating them from analytical tables.

---

## 4. Existing Frontend Audit (`frontend/`)

### Current Structure:
- Framework: React 19.2.8 + Vite 8.3.0 + TypeScript 6.0.2 + Recharts 3.10.1 + Lucide-react 1.52.0.
- Build Status: Compiles cleanly with zero errors (`npm run build` completed in 9.60s, outputting 312.62 kB bundle).
- Pages in `frontend/src/pages/`: `OverviewPage`, `SalaryPage`, `SkillsPage`, `ArchetypesPage`, `PredictorPage`, `ModelEvalPage`, `ErrorAnalysisPage`, `MethodologyPage`.

### Key Audit Findings & Deficiencies:
1. **No Market Selection Context:** The user interface has no mechanism to select or switch between USA and India.
2. **Fixed USA Domain Vocabularies:** Predictor dropdowns are hardcoded to USA roles (18 role families), USA cities (San Francisco, New York, Seattle, Austin, etc.), and USA seniority tiers.
3. **Missing Guided Calculator Workflow:** `PredictorPage.tsx` currently displays an unguided form rather than a modern step-by-step wizard.
4. **Missing Dedicated Cross-Market Page:** No comparative view exists to contrast USA tech compensation against Indian tech compensation across roles, skills, and archetypes.
5. **Missing Home Landing Page:** The root view immediately opens the technical Overview rather than an inspiring product landing page with clear value propositions and CTAs.

---

## 5. Frozen Artifact Inventory & Checksum Verification

All critical machine learning models, preprocessors, and modeling cohorts have been audited. Checksums are verified against their frozen signatures:

| Pipeline | Artifact Description | Local File Path | Verified SHA-256 Checksum | Size | Frozen Status |
|---|---|---|---|---|:---:|
| **India** | Supervised Salary Model | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | 549,969 B | **FROZEN** |
| **India** | Column Preprocessor | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | 10,527 B | **FROZEN** |
| **India** | Modeling Cohort | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | 654,351 B | **FROZEN** |
| **India** | Feature Specification | `models/india/final_feature_list.json` | `710aebaca840d4300a1e5f513fbe4826310abad9aa99e0547e63c0aabbef610e` | 15,748 B | **FROZEN** |
| **India** | Model Evaluation Metadata | `models/india/final_evaluation.json` | `04552f31c8694223a7895a10ce195acf5629ec772fa7da68628a5b0afea7658b` | 679 B | **FROZEN** |
| **India** | Model Training Metadata | `models/india/final_model_metadata.json` | `3e2aed92bee6a939295ac0d07fe4701856d079ea6f279952cb71b26565af3cb3` | 8,995 B | **FROZEN** |
| **India** | Archetype PCA Transformer | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | 37,446 B | **FROZEN** |
| **India** | Archetype K-Means Model | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | 22,617 B | **FROZEN** |
| **India** | Holdout Archetype Pipeline | `models/india/india_holdout_archetype_pipeline.pkl` | `efce615d239ca0198605bdee3468b1709c281242af0b49a38df311d3e272df6b` | 55,644 B | **FROZEN** |
| **India** | Archetype Metadata | `models/india/india_archetype_metadata.json` | `e49c22b85111408d4e87e4a29cb1afc5e76d9ac0d97bbe3789cca9311a2f4cff` | 4,494 B | **FROZEN** |
| **India** | PCA Component Parquet | `data/processed/india/india_skill_pca.parquet` | `8361c0dd9df1f1b9c25362d7f98b12142612895bee84b756c8dc790edacd1089` | 783,165 B | **FROZEN** |
| **India** | Archetype Assignments | `data/processed/india/india_archetype_assignments.parquet` | `2c058799e106dcf634bc9f5f014de343168d11fb5fb583b7e277d9dca611394c` | 261,867 B | **FROZEN** |
| **USA** | Supervised Salary Model | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | 619,464 B | **FROZEN** |
| **USA** | Metadata Preprocessor | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | 3,317 B | **FROZEN** |
| **USA** | Feature Specification | `models/phase5/feature_metadata.json` | `6f436976d2004b8b97934c7866ca7b3769cb938147d6a4ef1eea3a439dea7a5b` | 5,858 B | **FROZEN** |
| **USA** | Evaluation Metrics | `models/phase5/model_metrics.json` | `06f372ff9cfde71890f5ef2be9ecafeceea6bc50ef503f173ee13124301b52c3` | 3,051 B | **FROZEN** |
| **USA** | Archetype Scaler | `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | 1,161 B | **FROZEN** |
| **USA** | Archetype PCA Transformer | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | 6,355 B | **FROZEN** |
| **USA** | Archetype K-Means Model | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | 468,479 B | **FROZEN** |
| **USA** | Supervised Modeling Cohort| `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | 1,669,405 B | **FROZEN** |
| **USA** | Skill Matrix Technical | `data/processed/skill_matrix_technical.parquet` | `91abf1d836de7e50e5bcdc64aa68dfcba0850af0550ce53f907ef547f391b406` | 5,334,250 B | **FROZEN** |

---

## 6. API Route & Contract Inventory

### Current API Inventory (33 Endpoints):
- `/health`, `/`
- `/api/overview/*`: `kpis`, `funnel`, `research-questions`, `data-flow`
- `/api/salary/*`: `summary`, `by-role`, `by-seniority`, `by-location`, `comparator`
- `/api/skills/*`: `frequency`, `salary-association`, `landscape`, `cooccurrence`, `detail/{skill_name}`
- `/api/archetypes/*`: `list`, `skill-lifts/{id}`, `role-profiles/{id}`, `all-skill-lifts`
- `/api/predict/*`: `options`, `estimate`
- `/api/models/*`: `benchmarks`, `feature-sets`, `feature-importance`
- `/api/error-analysis/*`: `archetype-breakdown`, `statistical-test`, `hypotheses`
- `/api/methodology/*`: `pipeline-stages`, `leakage-controls`, `limitations`

### Target Unified API Architecture:
To satisfy Section 11 of the directive without breaking existing routes, the API will be restructured into country-namespaced modular endpoints with backward-compatible fallbacks:
1. **Core System:**
   - `GET /api/health` (Reports service status, verifies loaded model hashes)
   - `GET /api/meta` (Exposes metadata, versions, and verified cohort metrics)
2. **USA Services:**
   - `GET /api/usa/options` (Roles, cities, seniority, 82 technical skills)
   - `POST /api/usa/predict` (Real-time live XGBoost salary inference)
   - `POST /api/usa/archetype` (PCA + K-Means $k=7$ cluster assignment)
   - `GET /api/usa/market-summary` (KPIs, salary percentiles, distributions)
   - `GET /api/usa/skills` (Prevalence, lifts, associations)
   - `GET /api/usa/archetypes` (7 archetype profiles, sizes, representative skills)
3. **India Services:**
   - `GET /api/india/options` (14 roles, 23 cities, work modes, 284 technical skills)
   - `POST /api/india/predict` (Real-time live HistGradientBoosting salary inference)
   - `POST /api/india/archetype` (PCA + K-Means $k=6$ cluster assignment)
   - `GET /api/india/market-summary` (KPIs, salary percentiles, distributions)
   - `GET /api/india/skills` (Prevalence, lifts, associations)
   - `GET /api/india/archetypes` (6 archetype profiles, sizes, representative skills)
4. **Cross-Market Services:**
   - `GET /api/cross-market/summary` (Comparative distributions, role structures, skill overlap, model performance)

---

## 7. Frontend Page Inventory & Target Experience

| Page Index | Target Page | Key User Capabilities & Components | Status |
|---|---|---|:---:|
| **Page 1** | **Home (Landing)** | Hero value proposition ("Understand Your Value in the Job Market"), Country Switcher (USA / India), Feature Highlights, Direct CTA to Calculator and Market Explorer. | *To Implement* |
| **Page 2** | **Salary Calculator** | Multi-step guided wizard: Country -> Role -> Experience -> Location -> Work Mode -> Skills -> Live Estimate Card with contextual interpretation, archetype tag, and error bounds. | *To Upgrade* |
| **Page 3** | **Market Explorer** | Filterable market intelligence: KPI cards, Salary by Role, Salary by Experience, Salary by Metro, Disclosed Distribution, Archetype Distributions. | *To Upgrade* |
| **Page 4** | **Skills Explorer** | Searchable skill taxonomy: Prevalence vs Salary Association, Top Enrichment Lifts, Key Skill Stacks, Clear separation of observational correlation vs predictive importance. | *To Upgrade* |
| **Page 5** | **Archetype Explorer** | Interactive taxonomy cards for India (6 archetypes) and USA (7 archetypes): Size, share, signature skills, median salary, observed error context. | *To Upgrade* |
| **Page 6** | **USA vs India** | Macro cross-market comparison: Dual-axis compensation distributions, structural role demand comparison, shared vs market-specific skills, model diagnostic comparison. | *To Implement* |
| **Page 7** | **How It Works** | Comprehensive technical methodology: Provenance, feature engineering, model architectures, validation protocols, anti-leakage governance, and known empirical limitations. | *To Upgrade* |

---

## 8. Technical Debt & Code Duplication Audit

1. **Legacy Streamlit Dashboard (`app.py`, `src/dashboard/`):**  
   22 files containing Streamlit-specific caching and widgets. These represent historical Phase 7 code that has been superseded by the React + Vite frontend. They will be maintained untouched for historical reference but excluded from the production FastAPI / Vite application loop.
2. **Missing Input Normalization Layer:**  
   The existing backend expects raw string inputs without strict Pydantic validation for role/city mapping. A dedicated validation and feature builder module (`src/backend/utils/feature_builder.py`) is required to guarantee that incoming payloads are transformed into the exact column sequence expected by the preprocessors.
3. **Absence of Integration Tests:**  
   While individual phase verification scripts exist in `scratch/`, there is no unified pytest suite verifying end-to-end API response parity against direct model execution.

---

## 9. Critical Integration Risks & Mitigation Strategies

| Risk | Description | Probability | Impact | Mitigation Strategy |
|---|---|:---:|:---:|---|
| **Feature Schema Mismatch** | India model expects strictly 290 columns in exact order; missing one skill column causes preprocessor crash. | High | Critical | Build a deterministic feature builder that initializes all 284 skills to `0.0`, maps user input, and validates column count against `final_feature_list.json` before calling `.transform()`. |
| **Currency Contamination** | Unintentional FX conversion between USD and INR in UI comparison cards. | Medium | Critical | Strictly enforce separate presentation contexts: USA components only display USD ($); India components only display INR (₹ / LPA). No FX rate constants permitted. |
| **Archetype Label Permutation** | India K-Means assigns cluster indices $0 \dots 5$ which must map to salary-ranked archetype IDs (`IND_ARC_01` to `IND_ARC_06`). | High | High | Codify the frozen Hungarian cluster-to-archetype map in `india_service.py` (`{4: 'IND_ARC_01', 2: 'IND_ARC_02', 3: 'IND_ARC_03', 5: 'IND_ARC_04', 0: 'IND_ARC_05', 1: 'IND_ARC_06'}`). |
| **Zero-Skill Input Handling** | User submits salary request with zero skills. | Medium | Medium | Salary models handle zero skills natively (using metadata features). Archetype engine flags profile as `IND_ARC_UNASSIGNED` with clear explanatory guidance. |
| **Model Drift / Silent Retraining** | Accidental refitting of models during service execution. | Low | Critical | Load models exclusively via read-only joblib/pickle loaders inside `model_registry.py`. Verify SHA-256 hashes at startup; abort launch on mismatch. |

---

## 10. Recommended Implementation Order (Phases 6.2 - 6.19)

In accordance with Section 41 of the Master Directive, implementation will proceed systematically through the following milestones:

- **Phase 6.2:** Centralized Model Registry (`src/backend/models/model_registry.py`) with cryptographic startup integrity verification.
- **Phase 6.3:** Refactor USA Inference Service (`src/backend/services/usa_service.py`) for clean dependency isolation.
- **Phase 6.4:** Implement India Inference Service (`src/backend/services/india_service.py`) with exact 290-feature vector construction.
- **Phase 6.5:** Implement Archetype Inference Services for real-time cluster projection.
- **Phase 6.6:** Implement Unified REST API Contracts and routers (`src/backend/routers/usa.py`, `india.py`, `cross_market.py`).
- **Phase 6.7:** Prediction Parity Tests (Verifying direct Python vs. FastAPI API output bitwise equivalence).
- **Phase 6.8:** Market Analytics Service serving pre-aggregated analytical tables.
- **Phase 6.9:** Frontend Architecture & Navigation update with global Market Context (`USA` / `India`).
- **Phase 6.10:** Implement Unified Guided Salary Calculator (Wizard workflow, country-aware dropdowns).
- **Phase 6.11:** Implement Unified Market Explorer (Interactive charts, role & metro filters).
- **Phase 6.12:** Implement Skills Explorer (Prevalence, lift, salary associations).
- **Phase 6.13:** Implement Archetype Explorer (India 6-archetype + USA 7-archetype cards).
- **Phase 6.14:** Implement USA vs. India Cross-Market Comparison Page.
- **Phase 6.15:** Implement How It Works Technical Page (Methodology, anti-leakage, limitations).
- **Phase 6.16:** Responsive UX Polish (Mobile breakpoints, loading states, zero overflow).
- **Phase 6.17:** End-to-End Integration Testing Suite (`tests/integration/`).
- **Phase 6.18:** Documentation update (`README.md` and `reports/phase6_integration_report.md`).
- **Phase 6.19:** Final Integration Audit & 40-Gate Verification.

---

## 11. Audit Certification

This audit confirms that:
- [x] All 21 frozen research artifacts exist and their SHA-256 hashes are verified.
- [x] Zero code attempts to retrain or modify frozen models.
- [x] The exact feature schemas (USA: 123 columns; India: 290 columns) are documented.
- [x] The repository is clean, builds without compilation errors, and is ready for Phase India-6 implementation.
