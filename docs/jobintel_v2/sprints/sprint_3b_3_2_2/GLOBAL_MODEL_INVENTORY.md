# JOBINTEL 2.0 — GLOBAL MODEL INVENTORY
## Comprehensive Registry of Predictive Models, Clustering Pipelines & Decision Systems

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Statistical Auditor  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/model_inventory.csv`  

---

## 1. INVENTORY OVERVIEW

JOBINTEL 2.0 integrates eight core intelligence systems across five sovereign markets (Australia, United States, United Kingdom, Singapore, India).

These systems span:
- **Supervised Regression Models:** India HistGradientBoosting and USA XGBoost models predicting compensation benchmarks.
- **Unsupervised Clustering Pipelines:** Career archetype groupings in PCA latent space for India and the USA.
- **Deterministic Rule & Classification Systems:** Multi-market canonical occupation mapping, employer entity resolution, and context-guarded skill extraction.
- **Descriptive Statistical Engines:** Global demand and statutory headcount intelligence.

```
+----------------------------------------------------------------------------------------------------+
| GLOBAL MODEL & SYSTEM INVENTORY SCORECARD                                                          |
+---------------------+----------------------+---------------+------------+--------------------------+
| System ID           | System Name          | Type          | Market     | Governance Status        |
+---------------------+----------------------+---------------+------------+--------------------------+
| MOD_IN_SALARY_HGBR  | India Salary HGBR    | Supervised Reg| IN         | APPROVED_CONDITIONAL     |
| MOD_US_SALARY_XGB   | USA Salary XGBoost   | Supervised Reg| US         | APPROVED_CONDITIONAL     |
| MOD_IN_ARCHETYPE_KM | India Archetypes     | Unsupervised  | IN         | APPROVED_DESCRIPTIVE     |
| MOD_US_ARCHETYPE_KM | USA Archetypes       | Unsupervised  | US         | APPROVED_DESCRIPTIVE     |
| SYS_OCC_MAPPER      | Occupation Mapper    | Rule Matching | GLOBAL (5) | APPROVED_RULE_BASED      |
| SYS_EMP_RESOLVER_V2 | Employer Resolver V2 | Hybrid Rules  | GLOBAL (5) | APPROVED_RULE_BASED      |
| SYS_SKILL_EXTRACTOR | Skill Guard Engine   | Pattern Guard | GLOBAL (5) | APPROVED_PATTERN_BASED   |
| SYS_DEMAND_INTEL    | Demand Intelligence  | Statistical   | GLOBAL (5) | APPROVED_DESCRIPTIVE     |
+---------------------+----------------------+---------------+------------+--------------------------+
```

---

## 2. DETAILED MODEL SPECIFICATIONS

### 2.1 Model 1: India Salary Intelligence Regressor (`MOD_IN_SALARY_HGBR`)
- **Model Architecture:** `HistGradientBoostingRegressor` (Scikit-Learn).
- **Target Formulation:** Log-transformed salary midpoint (`target_transformation: log1p`), evaluated on raw INR and display Lakhs Per Annum (LPA).
- **Market:** India (IN).
- **Training Cohort:** `indian-job-market-dataset-2025` (Phase-3 Cleaned Tech Modeling Cohort).
  - Total Sample: 5,859 records.
  - Train Set: 4,686 records (80.0%).
  - Holdout Set: 1,173 records (20.0%).
- **Split Methodology:** Stratified random split by salary tier.
- **Feature Contract:** 290 raw input features $\to$ 327 post-preprocessing features (role, experience bounds, city groupings, work mode, and 284 binary skill flags).
- **Model Artifact Path:** `models/india/final_model.pkl`
- **SHA-256 Digest:** `7a450531fa4356e30018a4beae69837a281fb2b757ea56e483fc1eb09adfe2bb`
- **Measured Holdout Metrics:**
  - $\text{MAE} = \text{₹3,71,472.71}$ (3.71 LPA)
  - $\text{Median AE} = \text{₹2,07,703.96}$ (2.08 LPA)
  - $\text{RMSE} = \text{₹6,21,880.93}$ (6.22 LPA)
  - $R^2 = 0.5798$ (~0.58)
  - $\text{MAPE} = 35.22\%$
  - $\text{Improvement vs. Baseline Dummy MAE} = 51.92\%$ reduction.

### 2.2 Model 2: USA Salary Intelligence Regressor (`MOD_US_SALARY_XGB`)
- **Model Architecture:** `XGBRegressor` (Tuned XGBoost).
- **Target Formulation:** Annual continuous base salary midpoint in USD.
- **Market:** United States (US).
- **Training Cohort:** USA Tech Jobs Modeling Cohort (Phase 5 Feature Set A).
  - Total Sample: 34,036 records.
  - Train Set: 27,228 records (80.0%).
  - Test Set: 6,808 records (20.0%).
- **Split Methodology:** Stratified 80/20 train/test split.
- **Feature Contract:** 123 model inputs (seniority tiers, role families, remote status, city groupings, and 82 technical skill indicators).
- **Model Artifact Path:** `models/phase5/best_model.pkl`
- **SHA-256 Digest:** `87ef75dc1f8933b246a4805e2e8da05f778d91b4ad7496263cb2b7e193f4e246`
- **Measured Test Metrics:**
  - $\text{MAE} = \$36,380.64$
  - $\text{RMSE} = \$51,082.06$
  - $R^2 = 0.4233$ (~0.42)
  - $\text{MAPE} = 21.71\%$

### 2.3 System 3 & 4: Career Archetype Clustering Pipelines (`MOD_IN_ARCHETYPE_KM`, `MOD_US_ARCHETYPE_KM`)
- **Architecture:** Standard Scaler $\to$ Principal Component Analysis (10 components) $\to$ KMeans ($k=7$ clusters).
- **Artifacts:** `models/india/india_kmeans_v1.pkl` and `models/kmeans_phase4_1_k7.pkl`.
- **Function:** Descriptive segmentation of candidate profiles into 7 market archetypes (e.g. AI/ML, Cloud Architecture, Full Stack).
- **Governance Constraint:** Strictly descriptive; **never used to compute employment success probabilities**.

### 2.4 System 5: Global Canonical Occupation Mapper (`SYS_OCC_MAPPER`)
- **Architecture:** Two-stage taxonomic regex and pattern matching engine mapping job requisitions to the 12 canonical occupations (`CAN_OCC_001` to `CAN_OCC_012`).
- **Benchmark Performance (100 Gold Titles):**
  - Overall Accuracy: **97.00%**
  - Misclassification Rate: **0.00%**
  - Unmapped Fallback Rate: **3.00%**
  - Macro F1: **0.9852**
  - Raw Expected Calibration Error (ECE): **0.0587** (Calibrated with $T=1.24$: **0.0381**).

### 2.5 System 6: Employer Entity Resolution Engine V2 (`SYS_EMP_RESOLVER_V2`)
- **Architecture:** 4-tier hierarchical resolution engine enforcing Sovereign Market Isolation and ATS Host Blacklisting.
- **Benchmark Performance (100 Gold Pairs):**
  - Precision: **100.00%**
  - Recall: **68.89%**
  - Pairwise False Merge Rate: **0.00%** (95% Wilson CI: `[0.00% - 6.53%]`)
  - F1 Score: **0.8158**.

### 2.6 System 7: Contextual Skill Extractor (`SYS_SKILL_EXTRACTOR`)
- **Architecture:** Pattern matching with 5-token contextual co-occurrence window guard for single-letter and short tokens (`Go`, `C`, `R`, `SQL`, `AWS`, `ML`, `AI`).
- **Adversarial Benchmark Performance (20 Phrases):**
  - Classification Accuracy: **100.0%** (10/10 technical captured, 10/10 colloquial rejected).

### 2.7 System 8: Global Demand Intelligence System (`SYS_DEMAND_INTEL`)
- **Architecture:** Deterministic statistical aggregator ingesting official corporate filings (WGEA, Gender Pay Gap, SEC EDGAR, SEBI BRSR) and direct career portal feeds.
- **Governance Invariant:** Purely descriptive historical/current indicators. **UK vacancy demand strictly gated (`null`). Zero synthetic growth forecasting.**
