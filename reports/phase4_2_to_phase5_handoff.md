# Phase 4.2 to Phase 5 Technical Handoff & Governance Blueprint
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Task:** Transition from Phase 4.2 (Audited Archetypes) to Phase 5 (Salary Prediction Modeling)  
**Author:** Lead ML Research Engineer & Statistical Reviewer  
**Date:** October 2026  
**Status:** Certified, Audited & Frozen  

---

## 1. Frozen Primary Archetype Solution ($k = 7$)

Following the Phase 4.2 statistical audit, the primary archetype solution is formally frozen as:
- **Primary Archetype Discovery Population:** $N = 116,830$ postings with $\ge 1$ qualifying technical skill.
- **Dimensionality Reduction:** 15 Principal Components (Centered Covariance PCA, 56.05% cumulative variance explained).
- **Cluster Resolution:** $k = 7$ skill-based archetypes, retained as a defensible multi-criteria compromise.
- **Exploratory Data Artifact:** [`data/processed/job_archetype_assignments.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments.parquet) ($N = 116,830$).
- **Diagnostic Baseline Artifact:** [`data/processed/job_archetype_assignments_full_corpus_diagnostic.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments_full_corpus_diagnostic.parquet) ($N = 335,995$).
- **Supervised Modeling Domain for Phase 5:** [`data/processed/modeling_dataset.parquet`](file:///e:/Job%20Market/data/processed/modeling_dataset.parquet) ($N = 34,036$).

---

## 2. Frozen Master Archetype Taxonomy

| Cluster ID | Short Code | Archetype Title | Postings ($N$) | Primary Share (%) | Defining Skills (Prevalence & Lift) | Primary Role Families | Median Salary ($N=30.9\text{k}$) | Analytical Role in Phase 5 |
|:---:|---|---|---:|---:|---|---|---:|---|
| **0** | `FOUND_TECH` | **Foundational & Broad Technical Roles** | 57,791 | 49.47% | `qa_testing` (10.7%), `robotics` (1.4x), `security` (8.8%), isolated single skills | Other Tech (44.1%), Software Eng (13.0%) | **\$170,500** | Foundational baseline; low skill-density postings. |
| **1** | `DEVOPS_PLAT` | **DevOps & Cloud Infrastructure Engineering** | 8,365 | 7.16% | `kubernetes` (80.0%), `ci_cd` (77.9%), `docker` (8.3x), `terraform` (8.3x) | DevOps / Cloud (37.0%), Software Eng (20.0%) | **\$187,500** | Containerization, CI/CD, and platform infrastructure. |
| **2** | `WEB_FRONT` | **Frontend & Modern Web Application Engineering** | 6,149 | 5.26% | `react` (80.7%), `typescript` (80.0%), `next.js` (11.8x), `react-native` (11.2x) | Software Eng (25.0%), Frontend Dev (22.4%) | **\$195,000** | Reactive web clients, mobile apps, and UI frameworks. |
| **3** | `CLOUD_ARCH` | **Multi-Cloud & Enterprise Cloud Architecture** | 7,704 | 6.59% | `aws` (98.6%), `azure` (88.1%), `gcp` (84.1%), `databricks` (4.3x lift) | ML / AI Eng (19.3%), Software Eng (17.1%) | **\$190,000** | Multi-cloud warehousing, orchestration, and migration. |
| **4** | `DATA_BI` | **Data Engineering & Business Analytics** | 14,971 | 12.81% | `sql` (99.9%), `looker` (4.6x lift), `tableau` (4.3x lift), `dbt` (4.0x lift) | Other Tech (23.7%), Software Eng (17.2%) | **\$166,500** | Relational databases, ETL pipelines, and BI reporting. |
| **5** | `AI_ML` | **AI / Machine Learning & LLM Engineering** | 10,171 | 8.71% | `llm` (100.0%), `machine_learning` (34.0%), `nlp` (4.3x), `deep_learning` (3.8x) | ML / AI Engineer (69.6%), Tech Product (7.5%) | **\$204,000** | Neural networks, foundation models, and AI algorithms. |
| **6** | `SYS_ENG` | **Systems & Core Backend Engineering** | 11,679 | 10.00% | `python` (99.5%), `c++` (4.9x lift), `embedded` (4.1x lift), `rust` (3.2x lift) | Software Engineer (47.4%), ML / AI Eng (16.2%) | **\$185,000** | High-performance runtimes, Linux OS, and low-level code. |

---

## 3. Mandatory Predictive Feature Sets for Phase 5

Phase 5 will evaluate whether latent dimensionality reduction and archetype indicators improve out-of-sample salary prediction accuracy over baseline explicit features.

### Feature Set A: Original Explicit Features (Baseline)
- **Role & Seniority:** One-hot / Target encoded `role_family` (18 classes), Ordinal / Target encoded `seniority` (5 tiers).
- **Metadata:** Binary `is_remote` indicator, Target / Frequency encoded `city_clean`, Numerical `num_skills`.
- **Explicit Skills:** 82 binary technical skill indicators ($x_j \in \{0, 1\}$).

### Feature Set B: PCA Dimensionality Reduction Features
- **Metadata:** Non-skill features from Feature Set A (`role_family`, `seniority`, `is_remote`, `city_clean`, `num_skills`).
- **Latent Features:** **15 Continuous Principal Components (PC1 to PC15)** fitted on the technical skill matrix *strictly within each cross-validation training fold*.

### Feature Set C: Archetype-Augmented Feature Set
- **Baseline Features:** Full Feature Set A (Original Features).
- **Archetype Features:** **Categorical Archetype Indicator (`cluster_id` $\in \{0 \dots 6\}$)** or 7 one-hot binary indicators generated via *fold-specific K-Means nearest centroid assignment*.

---

## 4. Strict Leakage Prevention Architecture

> **CRITICAL DATA-LEAKAGE GOVERNANCE RULE:**  
> **Under NO CIRCUMSTANCES should the full-data exploratory cluster labels from `job_archetype_assignments.parquet` be joined into the Phase 5 training and test datasets prior to cross-validation splitting.**

Doing so would cause catastrophic data leakage:
1. The test-set feature variance would influence the PCA transformation matrix.
2. The test-set feature values would influence the K-Means cluster centroid positions.
3. Out-of-sample generalization errors (RMSE, MAE, $R^2$) would be artificially optimistic.

### The Mandatory Cross-Validation Implementation Pipeline:

```python
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

kf = KFold(n_splits=5, shuffle=True, random_state=42)

for fold, (train_idx, val_idx) in enumerate(kf.split(df_modeling)):
    # 1. Partition Data
    df_train = df_modeling.iloc[train_idx]
    df_val = df_modeling.iloc[val_idx]
    
    # 2. Extract Skill Matrix
    X_train_skills = df_train[skill_cols].values.astype(float)
    X_val_skills = df_val[skill_cols].values.astype(float)
    
    # 3. Fit Preprocessing & PCA Strictly on Training Partition
    scaler = StandardScaler(with_mean=True, with_std=False).fit(X_train_skills)
    X_train_centered = scaler.transform(X_train_skills)
    X_val_centered = scaler.transform(X_val_skills)
    
    pca = PCA(n_components=15, random_state=42).fit(X_train_centered)
    X_train_pca = pca.transform(X_train_centered)
    X_val_pca = pca.transform(X_val_centered)
    
    # 4. Fit K-Means Strictly on Training PCA Coordinates
    kmeans = KMeans(n_clusters=7, random_state=42, n_init=10).fit(X_train_pca)
    train_clusters = kmeans.labels_
    val_clusters = kmeans.predict(X_val_pca)  # Nearest centroid assignment
    
    # 5. Assemble Feature Sets A, B, C for Train and Validation
    # 6. Fit Supervised Regressors (Dummy, Ridge, RF, XGBoost, LightGBM, MLP)
    # 7. Predict on Held-Out Validation Partition and Compute Out-of-Fold Metrics
```

---

## 5. Scope Boundary Enforcement

### Deliverables Certified in Phase 4.2:
- [x] Comprehensive statistical audit completed with zero unaddressed methodology gaps.
- [x] All 14 mandatory quality gates passed and documented.
- [x] Exaggerated and unsupported language purged from all reports.
- [x] PCA Covariance scaling empirically justified over Correlation PCA.
- [x] Formal cross-cohort sensitivity correspondence established (Hungarian match 74.51%, centroid cosine 0.8708).
- [x] Structural heterogeneity in Cluster 0 formally disclosed.
- [x] Anti-leakage cross-validation architecture established.

### Phase 5 Tasks Held in Reserve (Awaiting Explicit User Approval):
- Supervised salary regression across 8 candidate models.
- 5-Fold cross-validation across Feature Sets A, B, and C.
- Model performance comparison (MAE, RMSE, $R^2$, MAPE).
- Archetype-specific error auditing to answer RQ3.
- SHAP value and feature importance interpretability analysis.

**Phase 4 is complete, audited, and frozen. Awaiting user command to begin Phase 5.**
