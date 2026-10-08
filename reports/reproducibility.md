# INT234 Reproducibility Protocol & Pipeline Execution Map
**Project Title:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning  
**Author:** Lead ML Research Engineer & Reproducibility Auditor  
**Date:** October 2026 | **Governance:** Fully Certified & Deterministic  

---

## 1. System & Environment Specifications

- **Operating System:** Windows 11 / Linux (POSIX compatible)
- **Base Python Version:** Python 3.13.9 (Supported: Python $\ge 3.11$)
- **Core Package Versions:**
  - `numpy`: 2.2.6
  - `pandas`: 2.3.3
  - `scipy`: 1.15.2
  - `scikit-learn`: 1.7.2
  - `xgboost`: 3.2.0
  - `matplotlib`: 3.10.1
  - `seaborn`: 0.13.2
  - `pyarrow`: 19.0.1
  - `joblib`: 1.4.2
  - `nbformat`: 5.10.4
  - `nbconvert`: 7.16.6

To install exact dependencies:
```bash
pip install -r requirements.txt
```

---

## 2. Deterministic Seeds & Randomness Controls

All stochastic algorithms and data-partitioning processes are strictly pinned to `random_state = 42`:
- **Train/Test Splitting:** `train_test_split(..., test_size=0.20, random_state=42)`
- **Cross-Validation Folding:** `KFold(n_splits=5, shuffle=True, random_state=42)`
- **PCA Decomposition:** `PCA(n_components=15, random_state=42)`
- **K-Means Clustering:** `KMeans(n_clusters=7, random_state=42, n_init=10)`
- **Tree Ensembles & Gradient Boosters:** `RandomForestRegressor(..., random_state=42)`, `GradientBoostingRegressor(..., random_state=42)`, `XGBRegressor(..., random_state=42)`
- **Permutation Importance:** `permutation_importance(..., random_state=42)`

---

## 3. End-to-End Pipeline Execution Map

The research pipeline can be executed completely and deterministically from raw data to final outputs through the following sequenced execution order:

```text
PHASE 1: Dataset Provenance Audit
  ↳ Source: data/raw/dataset_A/ (jobs-tier1-L-2026-08-01)
  ↳ Evaluates schema, license, paired salary coverage
  ↳ Report: reports/dataset_selection.md

PHASE 2 & 2.1: Data Cleaning & Taxonomy Repair
  ↳ Script: python src/rebuild_phase2_1.py
  ↳ Ingests raw data (394,300), deduplicates (335,995), filters tech roles (114,873)
  ↳ Generates: data/processed/cleaned_jobs.parquet
  ↳ Generates: data/processed/modeling_dataset.parquet (N = 34,036)
  ↳ Generates: data/processed/skill_matrix_technical.parquet (82 skills)
  ↳ Report: reports/phase2_1_before_after.md

PHASE 3: Exploratory Data Analysis
  ↳ Script: python src/run_phase3_eda.py
  ↳ Generates: reports/tables/phase3/ (all CSV profiles)
  ↳ Generates: reports/figures/phase3/ (all exploratory plots)
  ↳ Executable Notebook: notebooks/03_eda.ipynb
  ↳ Reports: reports/phase3_eda_report.md, reports/phase3_executive_summary.md

PHASE 4.1: Corrected Skill-Bearing Archetype Discovery
  ↳ Script: python src/run_phase4_1_archetype_correction.py
  ↳ Restricts to skill-bearing postings (N = 116,830)
  ↳ Fits Centered Covariance PCA (15 PCs) and K-Means (k=7)
  ↳ Generates: models/scaler_phase4_1.pkl, models/pca_phase4_1.pkl, models/kmeans_phase4_1_k7.pkl
  ↳ Generates: data/processed/job_archetype_assignments.parquet
  ↳ Executable Notebook: notebooks/04_1_archetype_correction.ipynb
  ↳ Reports: reports/phase4_1_archetype_report.md, reports/phase4_1_executive_summary.md

PHASE 4.2: Statistical Audit of Archetypes
  ↳ Audits PCA scaling, k=7 trade-off, stability metrics, Hungarian sensitivity
  ↳ Report: reports/phase4_2_statistical_audit.md

PHASE 5: Supervised Salary Modeling & Subgroup Error Analysis
  ↳ Script: python src/run_phase5_experiments.py
  ↳ Partitions 80% Train (N = 27,228) and 20% Test (N = 6,808)
  ↳ Executes 5-fold CV across Feature Sets A, B, and C
  ↳ Tunes XGBoost on training set; evaluates ONCE on holdout test set
  ↳ Disaggregates errors by archetype (Kruskal-Wallis H-test)
  ↳ Generates: models/phase5/best_model.pkl, best_pipeline.pkl, feature_metadata.json, model_metrics.json
  ↳ Generates: reports/tables/phase5/ (10 CSVs), reports/figures/phase5/ (18 PNGs)
  ↳ Executable Notebook: notebooks/05_salary_modeling.ipynb
  ↳ Reports: reports/phase5_salary_prediction_report.md, reports/phase5_model_card.md, reports/phase5_scientific_audit.md

PHASE 6: Final Integration, Research Synthesis & Submission Finalization
  ↳ Canonical Registry: reports/frozen_results_registry.md
  ↳ Repository Audit: reports/phase6_repository_audit.md
  ↳ Integrated Report: reports/phase6_integrated_analysis.md
  ↳ Executive Summary: reports/final_executive_summary.md
  ↳ Consistency Audit: reports/phase6_consistency_audit.md
  ↳ Distinction Audit: reports/distinction_readiness_audit.md
  ↳ Presentation README: README.md
```

---

## 4. Leakage Prevention Protocol Verification

To guarantee scientific credibility and prevent data leakage:
1. **Target Feature Quarantine:** Predictor matrices never contain `salary_min`, `salary_max`, `salary_midpoint`, `salary_band`, `log_salary`, or `job_id`.
2. **Exploratory Label Isolation:** Exploratory cluster assignments from Phase 4.1 (`job_archetype_assignments.parquet`) were **never merged** into the predictive dataset.
3. **Fold-Safe Cross-Validation:** For every cross-validation fold:
   - Categorical encoders (`MetadataTransformer`) are fitted strictly on `X_train_fold`.
   - PCA dimensionality reduction (`FoldSafeSkillPCA`) is fitted strictly on `X_train_fold[tech_skills]`.
   - K-Means clusterers (`FoldSafeArchetypeTransformer`) are fitted strictly on the training PCA projection.
   - Validation fold observations are transformed using training components and assigned to archetypes via training centroids only.
4. **Holdout Test Isolation:** The $20\%$ test partition ($N_{\text{test}} = 6,808$) remained locked and uninspected during exploratory analysis, cross-validation, and hyperparameter tuning. Only **ONE final evaluation** was conducted on the frozen winning model.

---

## 5. Artifact Storage Locations & Checksums

| Artifact Category | Primary Filepath | Description |
|---|---|---|
| **Raw Data** | `data/raw/dataset_A/` | Original sliced postings package (`jobs-tier1-L-2026-08-01`) |
| **Cleaned Parquet** | `data/processed/cleaned_jobs.parquet` | Deduplicated tech corpus ($N = 335,995$) |
| **Modeling Parquet** | `data/processed/modeling_dataset.parquet` | Verified modeling cohort ($N = 34,036$) |
| **Technical Skills Parquet**| `data/processed/skill_matrix_technical.parquet` | 82 binary skill features ($N = 335,995 \times 82$) |
| **Archetypes Parquet** | `data/processed/job_archetype_assignments.parquet` | Primary 7 archetypes ($N = 116,830$) |
| **Unsupervised Models** | `models/scaler_phase4_1.pkl`, `pca_phase4_1.pkl`, `kmeans_phase4_1_k7.pkl` | Phase 4.1 exploratory clustering objects |
| **Supervised Models** | `models/phase5/best_model.pkl`, `best_pipeline.pkl` | Tuned XGBoost regressor and Feature Set A pipeline |
| **Model Metadata** | `models/phase5/feature_metadata.json`, `model_metrics.json` | Pinned feature names and evaluation metrics |
| **Executed Notebooks** | `notebooks/03_eda.ipynb`, `04_1_archetype_correction.ipynb`, `05_salary_modeling.ipynb` | Top-to-bottom executed notebooks |
| **Analytical Tables** | `reports/tables/phase3/`, `phase4_1/`, `phase5/` | All computed quantitative metric CSVs |
| **Figures** | `reports/figures/phase3/`, `phase4_1/`, `phase5/` | All high-DPI diagnostic publication figures |

---

## 6. Verification Commands

To verify that the complete environment and codebase execute top-to-bottom without error:
```bash
# 1. Verify data preparation
python src/rebuild_phase2_1.py

# 2. Verify exploratory analysis
python src/run_phase3_eda.py

# 3. Verify archetype discovery
python src/run_phase4_1_archetype_correction.py

# 4. Verify salary modeling experiments
python src/run_phase5_experiments.py
```
*Total pipeline run time: Approximately 4–6 minutes on modern 8-core CPU hardware.*
