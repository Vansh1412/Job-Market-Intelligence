# Phase 4 to Phase 5 Technical Handoff & Architecture Blueprint
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Task:** Transition from Phase 4 (Unsupervised Archetypes) to Phase 5 (Salary Prediction Modeling)  
**Author:** Antigravity Senior ML & Statistical Research Team  
**Date:** October 2026  
**Status:** Certified & Signed Off  

---

## 1. Final Discovered Archetype Solution

The definitive archetype discovery pipeline established in Phase 4 is designated as:
- **Optimal Cluster Count:** **$k = 7$ Archetype Clusters**
- **Underlying Latent Subspace:** 15 Principal Components (Covariance PCA, 58.52% variance explained)
- **Primary Data Artifact:** [`data/processed/job_archetype_assignments.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments.parquet) ($N = 335,995$)
- **Model Artifacts (Exploratory Full-Corpus Baseline):**
  - Scaler: [`models/scaler_phase4.pkl`](file:///e:/Job%20Market/models/scaler_phase4.pkl)
  - PCA: [`models/pca_phase4.pkl`](file:///e:/Job%20Market/models/pca_phase4.pkl)
  - K-Means: [`models/kmeans_phase4_k7.pkl`](file:///e:/Job%20Market/models/kmeans_phase4_k7.pkl)

---

## 2. Archetype Definitions & Taxonomic Blueprint

| Cluster ID | Short Code | Archetype Title | Defining Skills | Primary Role Families | Median Salary (Cohort $N=34\text{k}$) | Analytical Interpretation for Phase 5 |
|:---:|---|---|---|---|---:|---|
| **0** | `SYS_ENG` | **Systems & Core Backend Engineering** | `python`, `c++`, `linux`, `embedded`, `rust` | Software Engineer (50.2%), ML / AI (10.2%) | **\$176,000** | High-performance compiled runtimes, hardware/firmware, and foundational backend engineering. |
| **1** | `GEN_ATS` | **General / Non-Technical Postings** | Baseline zero/low technical skills (0.09 skills/job) | Other Tech / ATS General (87.5%) | **\$170,000** | Non-technical or broad administrative tech roles without deep computing specialization. |
| **2** | `CLOUD_ARCH` | **Multi-Cloud & Enterprise Cloud Architecture** | `aws`, `azure`, `gcp`, `databricks`, `snowflake` | ML / AI (18.5%), Software Eng (17.6%) | **\$190,000** | Enterprise cloud infrastructure, migrations, and distributed multi-cloud warehousing. |
| **3** | `AI_ML` | **AI / Machine Learning & Deep Learning** | `machine-learning`, `deep-learning`, `pytorch`, `tensorflow`, `llm` | ML / AI Engineer (64.9%), Data Scientist (9.0%) | **\$213,750** | Advanced mathematical algorithms, neural network research, and foundation model fine-tuning. |
| **4** | `DEVOPS_PLAT` | **DevOps & Cloud Infrastructure Engineering** | `ci-cd`, `kubernetes`, `docker`, `terraform`, `ansible`, `devops` | DevOps / Cloud (34.2%), Software Eng (20.8%) | **\$185,000** | Containerization, CI/CD pipelines, site reliability engineering, and infrastructure-as-code. |
| **5** | `WEB_FRONT` | **Frontend & Modern Web Application** | `typescript`, `react`, `react-native`, `next.js`, `node.js` | Software Engineer (52.4%), Frontend (16.2%) | **\$197,275** | Client-side reactive frameworks, mobile hybrid development, and full-stack interactive UI. |
| **6** | `DATA_BI` | **Data Engineering & Business Analytics** | `sql`, `looker`, `tableau`, `dbt`, `bigquery`, `power-bi` | Other Tech (24.8%), Software Eng (17.8%), Data Eng (12.7%) | **\$162,500** | Structured database pipelines, ETL batch processing, and enterprise business intelligence. |

---

## 3. Mandatory Predictive Feature Sets for Phase 5

Phase 5 will evaluate whether latent dimensionality reduction and unsupervised archetype discovery improve predictive performance for salary modeling. The following **three feature sets** are required:

### Feature Set A: Original Explicit Features
- **Description:** Baseline feature representation using original raw and engineered features.
- **Composition:**
  - One-hot / Target encoded `role_family` (18 classes)
  - Ordinal / Target encoded `seniority` (5 tiers)
  - Binary `is_remote` indicator
  - Target encoded / frequency encoded `city_clean` / geography
  - Numerical `num_skills`
  - 82 binary technical skill indicators ($x_j \in \{0, 1\}$)

### Feature Set B: PCA Dimensionality Reduction Features
- **Description:** Replacing or augmenting explicit skill indicators with orthogonal latent directions.
- **Composition:**
  - Non-skill metadata from Feature Set A (`role_family`, `seniority`, `is_remote`, `city_clean`, `num_skills`)
  - **15 Continuous Principal Components (PC1 through PC15)** fitted on the technical skill matrix *within the training fold*.

### Feature Set C: Archetype-Augmented Feature Set
- **Description:** Combining explicit features with discovered cluster archetype indicators.
- **Composition:**
  - Full Feature Set A (Original Features)
  - **Categorical Archetype Indicator (`cluster_id` $\in \{0 \dots 6\}$)** or 7 one-hot binary indicators generated via *fold-specific K-Means nearest centroid assignment*.

---

## 4. Critical Data Leakage Governance Protocol

> **CRITICAL DATA-LEAKAGE GOVERNANCE RULE (Section 37 & 38):**  
> Under NO CIRCUMSTANCES should the full-corpus assignments from `job_archetype_assignments.parquet` be joined into the Phase 5 training and test datasets prior to train/test partitioning.

Doing so would cause **target/feature leakage** by allowing test-set feature variance to influence the PCA transformation matrix and K-Means cluster centroid coordinates.

### The Required Fold-Specific Cross-Validation Pipeline:
For every fold in Phase 5 $K$-Fold Cross-Validation:

```text
Full Supervised Cohort (N = 34,036)
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Split into Training Fold (80%) and Test Fold (20%)       │
└─────────────────────────────────────────────────────────────┘
           │
           ├──────────────────────────────────────────────┐
           ▼                                              ▼
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│ TRAINING PARTITION (X_train)         │       │ TEST PARTITION (X_test)              │
│                                      │       │                                      │
│ 1. Fit StandardScaler (centering)    │       │                                      │
│ 2. Fit PCA (n_components=15)         │       │ 1. Transform X_test via Train Scaler │
│ 3. Transform X_train -> X_pca_train  │       │ 2. Transform X_test via Train PCA    │
│ 4. Fit KMeans (k=7) on X_pca_train   │       │ 3. Assign Nearest Centroid to X_test │
│ 5. Assign cluster_id to X_train      │       │ 4. Generate cluster_id for X_test    │
│ 6. Construct Feature Sets A, B, C    │       │ 5. Construct Feature Sets A, B, C    │
│ 7. Fit Regressors (Ridge, RF, XGB)   │       │ 6. Predict Salaries on Held-out Set  │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────────────────────────┐
                                               │ Compute Out-of-Fold Evaluation:      │
                                               │ RMSE, MAE, MAPE, R² across A, B, C   │
                                               └──────────────────────────────────────┘
```

---

## 5. Scope Boundary Enforcement

### What Phase 4 Has Delivered:
- [x] Complete PCA decomposition and mathematical loadings analysis.
- [x] Swept K-Means validation ($k = 2 \dots 10$) with optimal selection at $k=7$.
- [x] High multi-seed stability confirmed (Mean ARI = 0.9310).
- [x] Detailed skill prevalence, lift signatures, and archetype dictionary.
- [x] Descriptive salary, title, seniority, and role family profiles.
- [x] Verified full-corpus assignments parquet file.
- [x] Secondary sensitivity confirmation on the modeling cohort.

### What Phase 5 Will Execute (Upon Explicit Approval):
- Supervised regression modeling (Baseline Median, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost, LightGBM, MLP).
- Rigorous 5-fold cross-validation with fold-specific pipeline transformations.
- Comparative evaluation of Feature Set A vs. Feature Set B vs. Feature Set C.
- Model diagnostics (MAE, RMSE, $R^2$, MAPE, residual distributions).
- Subgroup error auditing across archetypes and seniority tiers (Answering RQ3).
- Model interpretability (Feature Importance & SHAP values).

**Phase 4 is complete. Awaiting user command to begin Phase 5.**
