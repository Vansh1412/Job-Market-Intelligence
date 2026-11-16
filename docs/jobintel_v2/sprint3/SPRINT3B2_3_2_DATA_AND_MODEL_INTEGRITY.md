# JOBINTEL 2.0 — SPRINT 3B.2.3.2
# PHASE 4 & 5 — DATASET, SOURCE REGISTRY & MODEL ARTIFACT INTEGRITY

**Sprint:** 3B.2.3.2 — Final Diff Review & Controlled Staging Commit Preparation  
**Date:** 2026-11-16  
**Auditor:** Data Governance Auditor, Machine Learning Engineer & QA Architect  

---

## 1. Executive Summary

This audit independently verified the integrity, cryptographic hashes, provenance, foreign keys, and source licensing across all demand datasets (`src/backend/data/demand/`) and all frozen machine learning model artifacts (`models/`).

**Key Integrity Findings:**
- **Demand Datasets:** 10 registered sources, 7 standard metric definitions, exactly 28 demand observations across 5 markets, 5 shortage indicators, 11 skill profiles.
- **Foreign Key Validity:** 100% of observations reference valid `source_id` and `metric_type` keys. Zero dangling references.
- **Model Artifact Hashes:** 19 out of 19 cryptographic SHA-256 hashes in `src/backend/config/artifact_manifest.json` match the filesystem artifacts to the exact byte (100% verified). Zero retraining or re-serialization occurred.

---

## 2. Demand Datasets & Source Registry Audit

### 2.1 Sources Registry (`src/backend/data/demand/sources.json`)
The registry contains 10 verified data sources across 5 national markets:

| Source ID | Source Name | Market | Publication Status | License Reference |
| :--- | :--- | :---: | :---: | :--- |
| `us.bls.ep` | US BLS Employment Projections 2023-2033 | US | `PUBLISHED` | Public Domain (17 U.S.C. § 105) |
| `us.onet.skills` | O*NET Technology Skills and KSA Content Model | US | `PUBLISHED` | CC BY 4.0 |
| `au.jsa.ivi` | Jobs and Skills Australia Internet Vacancy Index | AU | `PUBLISHED` | CC BY 4.0 |
| `au.jsa.spl` | Jobs and Skills Australia Skills Priority List 2024 | AU | `PUBLISHED` | CC BY 4.0 |
| `uk.ons.labour-demand` | ONS Labour Demand Volumes by SOC 2020 | UK | `REVIEW_REQUIRED` | OGL v3.0 / Textkernel Terms Under Review |
| `uk.gov.shortage` | UK Immigration Salary List & Shortage Indicators | UK | `PUBLISHED` | Open Government Licence v3.0 (OGL v3.0) |
| `sg.mom.vacancies` | Singapore MOM Job Vacancy Report | SG | `PUBLISHED` | Singapore Open Data Licence v1.0 |
| `sg.ssg.skills` | SkillsFuture Singapore ICT Skills Framework | SG | `PUBLISHED` | Singapore Government Open Access |
| `in.mospi.plfs` | Periodic Labour Force Survey (PLFS) Annual Report | IN | `PUBLISHED` | Government Open Data Licence - India (GODL) |
| `in.jobintel.tech-demand`| JobIntel Tech Demand Benchmark Corpus | IN | `PUBLISHED` | Open Academic & Research Use |

### 2.2 Observations Inventory (`src/backend/data/demand/observations.json`)
- **Total Observations:** Exactly 28
- **Market Distribution:**
  - United States (US): 7 observations
  - Australia (AU): 4 observations
  - United Kingdom (UK): 8 observations
  - Singapore (SG): 6 observations
  - India (IN): 3 observations
- **Provenance Breakdown:**
  - `OFFICIALLY_DERIVED`: 25 observations (derived through reproducible concordance/annualization from official government statistics).
  - `JOBINTEL_CURATED`: 3 observations (strictly for India tech-hub empirical sample benchmark; accompanied by explicit non-MoSPI benchmark disclaimers).
- **UK Gated Observations:** All 8 UK observations remain gated under `uk.ons.labour-demand` (`REVIEW_REQUIRED`) and are sanitized to `None` in public endpoints.
- **Zero Fabricated Values:** No synthetic data exists in production datasets.

---

## 3. Machine Learning Model Artifact Cryptographic Verification

All 19 model, preprocessor, and dataset artifacts registered in `src/backend/config/artifact_manifest.json` were cryptographically hashed using SHA-256 and compared against certified SSOT values:

| Artifact Identifier | Filesystem Path | Expected SHA-256 (SSOT) | Actual SHA-256 (Calculated) | Status |
| :--- | :--- | :--- | :--- | :---: |
| `india_salary_model` | `models/india/final_model.pkl` | `7a3490d7...` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **MATCH** |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | `0ee1dabf...` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **MATCH** |
| `india_pca` | `models/india/india_pca_v1.pkl` | `8591e3d3...` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **MATCH** |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | `4465a3d8...` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **MATCH** |
| `usa_salary_model` | `models/phase5/best_model.pkl` | `55c1b7fd...` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **MATCH** |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | `815fd9a3...` | `815fd9a30283c7604f767858c2b794dca76a1660ca373c68df8eb4bbf94935ee` | **MATCH** |
| `usa_scaler` | `models/scaler_phase4_1.pkl` | `2d969acd...` | `2d969acd270a6c6e768165c6978430a91173872fbef7ea44eef7bf9266a2fc5d` | **MATCH** |
| `usa_pca` | `models/pca_phase4_1.pkl` | `ef4ef56b...` | `ef4ef56be5e73ef5e00b656b825da1bc1e3e7f5255ce714c63cfd29aa63640b6` | **MATCH** |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509...` | `4d6d2509503463945c71d600609553c834a3194098495577e923e070e6538b36` | **MATCH** |
| `india_cohort` | `data/processed/india_modeling_cohort.parquet` | `d4e32be4...` | `d4e32be425514f7b6b150c95024b33c0be7fae4eb207fc11c1d4ce8c3818e381` | **MATCH** |
| `usa_cohort` | `data/processed/modeling_dataset.parquet` | `68895e38...` | `68895e38481ff250fb19565aa2198031d451cb528296a848c08ecfe13c7908c6` | **MATCH** |
| `skill_matrix_technical` | `data/processed/skill_matrix_technical.parquet` | `91abf1d8...` | `91abf1d86d526fa4bfa7fdbdb10d287bb2e7e4ca61cba4772097e3a9c78fe256` | **MATCH** |
| `job_archetype_assignments` | `data/processed/job_archetype_assignments.parquet` | `c4f2fb93...` | `c4f2fb93c0429f6350eb55d04584e03b222956cf04a085b462fb5286520ec689` | **MATCH** |
| `india_skill_analytics` | `reports/tables/india/india_skill_analytics.json` | `08875b53...` | `08875b53e839e917d23a652e9e735ea7873b82142dfa84f32997b69248ee5f59` | **MATCH** |
| `india_final_feature_list` | `models/india/final_feature_list.json` | `9085e3a0...` | `9085e3a0a382be57c4c9e47264f331b24bf20aa394339e80111eb03323ae3b21` | **MATCH** |
| `india_final_model_metadata`| `models/india/final_model_metadata.json` | `077a4c29...` | `077a4c292931291845fe3108c3d21c35a8bc3dbeebbc74254bb70eec1a95e7c1` | **MATCH** |
| `india_archetype_metadata` | `models/india/india_archetype_metadata.json` | `7d49f6a0...` | `7d49f6a061404c107be618c7e902b3780517726715f5c4ce117498c4b95d3369` | **MATCH** |
| `usa_feature_metadata` | `models/phase5/feature_metadata.json` | `c4b72be3...` | `c4b72be3f155c82006bf2b5889a7fb3a504c540938f32aa76bbd5573fa5ca237` | **MATCH** |
| `usa_model_metrics` | `models/phase5/model_metrics.json` | `9d777fa4...` | `9d777fa4d4128f6bfe862826ea1d2346fb65a7d0363ae1bb7ffbf6a06ae04533` | **MATCH** |

---

## 4. Verification Conclusion

Zero model drift, zero unauthorized artifact modification, zero re-serialization, and 100% data provenance fidelity are established.
