# Phase 4.1 to Phase 5 Technical Handoff & Architecture Blueprint
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Task:** Transition from Phase 4.1 (Surgically Corrected Archetypes) to Phase 5 (Salary Prediction Modeling)  
**Author:** Antigravity Senior ML & Statistical Research Team  
**Date:** October 2026  
**Status:** Certified & Signed Off  

---

## 1. Corrected Primary Archetype Solution ($k = 7$)

Following the surgical methodology correction of Phase 4.1, the definitive primary archetype discovery pipeline is established as:
- **Primary Archetype Population:** Postings with $\ge 1$ qualifying technical skill ($N = 116,830$)
- **Optimal Cluster Count:** **$k = 7$ Skill-Based Archetypes**
- **Latent Feature Subspace:** 15 Principal Components (Centered Covariance PCA, 56.05% cumulative variance explained)
- **Primary Exploratory Artifact:** [`data/processed/job_archetype_assignments.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments.parquet) ($N = 116,830$, 0 nulls, 0 duplicate IDs)
- **Diagnostic Sensitivity Baseline:** [`data/processed/job_archetype_assignments_full_corpus_diagnostic.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments_full_corpus_diagnostic.parquet) ($N = 335,995$)
- **Trained Model Artifacts (Exploratory Skill-Bearing Baseline):**
  - Scaler: [`models/scaler_phase4_1.pkl`](file:///e:/Job%20Market/models/scaler_phase4_1.pkl)
  - PCA: [`models/pca_phase4_1.pkl`](file:///e:/Job%20Market/models/pca_phase4_1.pkl)
  - K-Means: [`models/kmeans_phase4_1_k7.pkl`](file:///e:/Job%20Market/models/kmeans_phase4_1_k7.pkl)

---

## 2. Master Archetype Dictionary & Taxonomic Blueprint

| Cluster ID | Short Code | Archetype Title | Defining Skills (Prevalence & Lift) | Primary Role Families | Median Salary ($N=30.9\text{k}$) | Analytical Significance for Phase 5 |
|:---:|---|---|---|---|---:|---|
| **0** | `FOUND_TECH` | **Foundational & Broad Technical Roles** | `qa_testing` (10.7%), `robotics` (1.4x lift), `security` (8.8%) | Other Tech (44.1%), Software Eng (13.0%), ML/AI (8.3%) | **\$170,500** | Single-skill or general tech postings without deep stack clustering. |
| **1** | `DEVOPS_PLAT` | **DevOps & Cloud Infrastructure Engineering** | `kubernetes` (80.0%), `ci_cd` (77.9%), `docker` (8.3x), `terraform` (8.3x) | DevOps / Cloud (37.0%), Software Eng (20.0%) | **\$187,500** | Cloud-native containerization, deployment pipelines, and infrastructure-as-code. |
| **2** | `WEB_FRONT` | **Frontend & Modern Web Application Engineering** | `react` (80.7%), `typescript` (80.0%), `next.js` (11.8x), `react-native` (11.2x) | Software Eng (25.0%), Frontend Dev (22.4%), Full-Stack (20.2%) | **\$195,000** | Reactive web clients, mobile hybrid frameworks, and stateful browser applications. |
| **3** | `CLOUD_ARCH` | **Multi-Cloud & Enterprise Cloud Architecture** | `aws` (98.6%), `azure` (88.1%), `gcp` (84.1%), `databricks` (4.3x lift) | ML / AI Eng (19.3%), Software Eng (17.1%), DevOps / Cloud (12.1%) | **\$190,000** | Enterprise multi-cloud orchestration, data warehousing, and hybrid cloud migrations. |
| **4** | `DATA_BI` | **Data Engineering & Business Analytics** | `sql` (99.9%), `looker` (4.6x lift), `tableau` (4.3x lift), `dbt` (4.0x lift) | Other Tech (23.7%), Software Eng (17.2%), Data Eng (12.7%) | **\$166,500** | Relational data engineering, analytical pipelines, and enterprise BI reporting. |
| **5** | `AI_ML` | **AI / Machine Learning & LLM Engineering** | `llm` (100.0%), `machine_learning` (34.0%), `nlp` (4.3x), `deep_learning` (3.8x) | ML / AI Engineer (69.6%), Tech Product (7.5%), Software Eng (6.6%) | **\$204,000** | Generative AI, large language models, neural network architectures, and NLP pipelines. |
| **6** | `SYS_ENG` | **Systems & Core Backend Engineering** | `python` (99.5%), `c++` (4.9x lift), `embedded` (4.1x lift), `rust` (3.2x lift) | Software Engineer (47.4%), ML / AI Eng (16.2%), Data Scientist (5.2%) | **\$185,000** | High-performance compiled runtimes, Linux OS internals, and algorithmic backend systems. |

---

## 3. Mandatory Predictive Feature Sets for Phase 5

Phase 5 evaluates whether latent dimensionality reduction (PCA) and archetype indicators (K-Means) improve out-of-sample salary prediction accuracy over baseline explicit features.

### Feature Set A: Original Explicit Features (Baseline)
- **Description:** Traditional tabular feature representation using explicit skills and job metadata.
- **Composition:**
  - One-hot / Target encoded `role_family` (18 categories)
  - Ordinal / Target encoded `seniority` (5 tiers: Intern, Junior, Mid, Senior, Lead/Principal)
  - Binary `is_remote` indicator
  - Target encoded / frequency encoded `city_clean` / geography
  - Numerical `num_skills`
  - 82 binary technical skill indicators ($x_j \in \{0, 1\}$)

### Feature Set B: PCA Dimensionality Reduction Features
- **Description:** Replaces or complements explicit skill indicators with orthogonal continuous latent components.
- **Composition:**
  - Baseline metadata from Feature Set A (`role_family`, `seniority`, `is_remote`, `city_clean`, `num_skills`)
  - **15 Continuous Principal Components (PC1 through PC15)** fitted on the technical skill matrix *strictly within each cross-validation training fold*.

### Feature Set C: Archetype-Augmented Feature Set
- **Description:** Augments explicit features with categorical archetype assignments to test whether non-linear archetype clustering adds predictive power.
- **Composition:**
  - Full Feature Set A (Original Features)
  - **Categorical Archetype Indicator (`cluster_id` $\in \{0 \dots 6\}$)** or 7 one-hot binary indicators generated via *fold-specific K-Means nearest centroid assignment*.

---

## 4. Strict Leakage Prevention & Predictive Clustering Protocol

> **CRITICAL ARCHITECTURAL RULE:**  
> **Phase 5 must NOT use the full-data exploratory cluster labels from `job_archetype_assignments.parquet` directly as predictive features.**

The cluster assignments in `job_archetype_assignments.parquet` were generated during exploratory analysis across the entire skill-bearing corpus ($N = 116,830$) to answer RQ2. Joining these precomputed cluster labels into the Phase 5 modeling dataset before cross-validation would cause **catastrophic data leakage**:
1. The test-set instances would have influenced the PCA covariance matrix $\Sigma$.
2. The test-set instances would have influenced the K-Means cluster centroids $\mu_k$.
3. Out-of-sample error estimates (RMSE, MAE, $R^2$) would be artificially biased downward.

### The Mandatory Cross-Validation Protocol:

```text
TRAIN FOLD (80%)
       │
       ▼
1. Fit Preprocessing (centering on training skill matrix)
2. Fit PCA (15 components on centered training skill matrix)
3. Fit K-Means (k=7 on training PCA coordinates)
4. Assign training clusters (kmeans.labels_)
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
Fit Regressors on Train Fold          Transform Validation / Test Fold (20%)
(Ridge, RF, XGBoost on A, B, C)       1. Transform skills via Train Centering
                                      2. Project into PCA via Train PCA matrix
                                      3. Assign nearest centroid via Train KMeans
                                      4. Predict salary on transformed test fold
                                                │
                                                ▼
                                      Evaluate Out-of-Fold Metrics
                                      (RMSE, MAE, R², MAPE)
```

**Never Execute:**
$$\text{Full Data} \longrightarrow \text{PCA} \longrightarrow \text{K-Means} \longrightarrow \text{Split} \longrightarrow \text{Regression} \quad [\textbf{STRICTLY PROHIBITED}]$$

---

## 5. Scope Boundary Enforcement

### Deliverables Certified in Phase 4.1:
- [x] Surgical methodology correction removing 219,165 zero-skill postings from primary clustering.
- [x] Primary archetype population validated ($N = 116,830$, 82 technical skills).
- [x] PCA recomputed: 15 components, 56.05% cumulative variance explained.
- [x] K-Means evaluated across $k=2 \dots 10$; $k=7$ independently selected based on multi-criteria analysis.
- [x] Partition stability verified across 10 random seed pairs (Mean ARI = 0.7901, Mean AMI = 0.8030).
- [x] Primary Archetype Dictionary, skill prevalence, skill lift, and role family crosswalk generated.
- [x] Full-corpus diagnostic preserved in `data/processed/job_archetype_assignments_full_corpus_diagnostic.parquet`.
- [x] Secondary salary-cohort sensitivity analysis verified cross-cohort archetype replication.
- [x] Predictive clustering protocol and anti-leakage rules documented.

### Phase 5 Tasks (Held in Reserve — Awaiting Explicit Approval):
- Supervised salary regression across 8 candidate algorithms (Dummy Median, Ridge, Lasso, ElasticNet, Random Forest, Gradient Boosting, XGBoost, LightGBM, MLP).
- 5-Fold Cross-Validation with strict fold-specific feature generation (Feature Sets A, B, C).
- Statistical hypothesis testing comparing model performance across feature sets.
- Residual auditing across archetypes and seniority tiers (Answering RQ3).
- Feature importance and SHAP interpretability analysis.

**Phase 4.1 is complete. Do NOT begin Phase 5 until explicit user approval is granted.**
