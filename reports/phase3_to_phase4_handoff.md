# Phase 3 to Phase 4 Technical Handoff & Governance Protocol
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Task:** Transition from Phase 3 (EDA) to Phase 4 (Unsupervised Archetype Discovery)  
**Date:** October 5, 2026  
**Status:** Certified & Signed Off  

---

## 1. Primary Feature Matrix for Phase 4 Archetype Discovery

The primary feature input for unsupervised learning (PCA + K-Means) is formally designated as:

- **Target Matrix File:** [`data/processed/skill_matrix_technical.parquet`](file:///e:/Job%20Market/data/processed/skill_matrix_technical.parquet)
- **Matrix Dimensions:**
  - Full Corpus: **335,995 observations $\times$ 82 technical skills**
  - Supervised Modeling Cohort: **34,036 observations $\times$ 82 technical skills**
- **Feature Sparsity:** **94.88%** across deduplicated postings.
- **Data Type:** Multi-hot binary indicators ($\{0, 1\}$).
- **Skill Domain Scope:** Pure computing and technical competencies (14 programming languages, 12 cloud/DevOps tools, 21 AI/ML/data technologies, 5 databases, 17 web/mobile frameworks, 4 analytical querying tools, and 9 systems/security tools).
- **Explicit Exclusions:** All soft collaborative skills (`communication`, `project-management`) and business software tools (`crm`, `salesforce`, `sap`, `excel`) are strictly excluded from the archetype discovery matrix.

---

## 2. Preprocessing & Scaling Strategy for Phase 4

Because the input matrix consists of sparse binary indicators with heterogeneous frequencies (ranging from Python at 34.06% to Redis at 1.74%), Phase 4 must evaluate two distinct scaling approaches:

1. **StandardScaler (Centering & Unit Variance):**
   - $z = \frac{x - \mu}{\sigma}$
   - Centers features to zero mean and scales to unit variance, allowing rarer specialized skills (e.g., PyTorch, Rust, Kubernetes) to exert equal geometric weight as ubiquitous skills (Python, SQL).
2. **Uncentered / TruncatedSVD Formulation:**
   - Preserves matrix sparsity without explicit zero-centering, preventing memory blowup while discovering orthogonal directions of maximum variance.
3. **MinMaxScaler / TF-IDF Weighting:**
   - Evaluates whether term-frequency / inverse-document-frequency (TF-IDF) weighting provides superior cluster separation compared to unweighted binary indicators.

> **Methodological Mandate:**  
> The final PCA dimensionality ($k$) must NOT be chosen arbitrarily. Phase 4 must empirically determine $k$ using:
> - Individual explained variance ratio
> - Scree plot "elbow" analysis
> - Cumulative explained variance thresholds (e.g., 70%, 80%, 90%)
> - Semantic interpretability of principal component loadings

---

## 3. Mandatory Clustering Data Leakage Rule

To ensure zero target contamination between unsupervised clustering and downstream predictive modeling (Phase 5), the following protocol is permanently codified:

### Protocol A: Unsupervised Exploratory Archetype Discovery (RQ2 Track)
- For the descriptive investigation of RQ2 (*Do job postings naturally form skill-based archetypes?*), PCA and K-Means may be fitted on the designated technical skill population to map the global topology of the technology labor market.

### Protocol B: Predictive Modeling Feature Generation (RQ3 Track)
- For all supervised regression models where PCA components (Feature Set B) or K-Means cluster labels (Feature Set C) are utilized as predictive features:
  - **The scaler, PCA transformer, and K-Means estimator MUST be fitted strictly within the 80% training partition ($X_{\text{train}}$) of each cross-validation fold.**
  - The held-out test partition ($X_{\text{test}}$) must be transformed using the training-fitted parameters and assigned to the nearest fixed cluster centroids.
  - **STRICT PROHIBITION:** Fitting PCA or K-Means globally on the entire 34,036 cohort prior to train/test partitioning constitutes data leakage and is strictly prohibited.

```text
CORRECT CROSS-VALIDATION PIPELINE:
Raw Training Set (80%) ──► Fit Scaler ──► Fit PCA ──► Fit K-Means ──► Train Model (e.g., Ridge / RF / XGB)
                                │              │             │                     │
Held-Out Test Set (20%) ──► Transform ───► Transform ──► Assign Cluster ──► Evaluate Metrics (RMSE, MAE, R²)
```

---

## 4. Distinction Between Role Family and Archetype Cluster

Role family and future skill archetypes represent conceptually distinct constructs that must not be conflated:

| Dimension | Role Family | Skill-Based Archetype (Phase 4) |
|---|---|---|
| **Origin** | Top-down heuristic classification | Bottom-up unsupervised discovery |
| **Feature Basis** | Title text regex syntax + primary skills | High-dimensional geometric skill matrix |
| **Taxonomy Type** | Categorical job title conventions (18 classes) | Latent multi-skill bundles (K-Means clusters) |
| **Analytical Function** | Benchmark industry categorization | Empirical mapping of real-world computing stacks |

Phase 4 will explicitly measure the contingency overlap (Normalized Mutual Information / Adjusted Rand Index) between role families and discovered clusters to evaluate how well formal job titles reflect actual technical requirements.

---

## 5. Phase 4 Readiness Certification

- [x] Technical skill matrix isolated and verified ($N = 335,995 \times 82$, $N = 34,036 \times 82$).
- [x] Sparsity confirmed at 94.88%.
- [x] Top technical skills and co-occurrence structures documented.
- [x] Zero PCA or K-Means code present in Phase 3 artifacts.
- [x] Leakage prevention protocols formally established.

**Phase 4 is certified ready to begin upon user approval.**
