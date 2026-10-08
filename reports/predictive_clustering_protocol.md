# Methodological Protocol: Exploratory vs. Predictive Clustering & Leakage Prevention
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Author:** Antigravity Data Science & Statistical Governance Team  
**Date:** October 2026  
**Status:** Certified Protocol Standard  

---

## 1. Foundational Epistemological Distinction: RQ2 vs. Phase 5 Predictive Modeling

A fundamental error in applied unsupervised learning is confusing **exploratory structural discovery** with **predictive feature engineering**. In this project, unsupervised clustering serves two entirely distinct scientific objectives that operate under mutually exclusive governance rules:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TWO DISTINCT CLUSTERING PARADIGMS                               │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ TRACK A: Exploratory Clustering (RQ2)     │ TRACK B: Predictive Feature Clustering     │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Objective: Discover natural job           │ Objective: Evaluate whether cluster        │
│ archetypes across the technology labor    │ features improve out-of-sample salary      │
│ market.                                   │ prediction accuracy (Feature Set C).       │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Data Population: Corrected skill-bearing  │ Data Population: Supervised modeling       │
│ technology postings (N = 116,830) with    │ cohort (N = 34,036).                       │
│ full-corpus diagnostic (N = 335,995).     │                                            │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Fitting Scope: Global fitting across the  │ Fitting Scope: Strict FOLD-SPECIFIC        │
│ skill-bearing exploratory population.     │ fitting on training partitions only (80%). │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Evaluation Criteria: Cluster validation   │ Evaluation Criteria: Out-of-sample         │
│ metrics (Inertia, Silhouette, DB, ARI,    │ predictive metrics (RMSE, MAE, R², MAPE)   │
│ skill lift signatures).                   │ on held-out test folds (20%).              │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Valid Output: Master Archetype Dictionary │ Valid Output: Cross-validated regression   │
│ and skill-bearing corpus assignments.     │ pipeline transformers without leakage.     │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 2. The Data Leakage Threat: Why Global Clusters Cannot Be Predictive Features

If an analyst fits PCA and K-Means globally on the entire modeling cohort ($N = 34,036$) and then performs a train/test split, **data leakage** occurs via two distinct mechanisms:

### 2.1 Distributional Variance Leakage (PCA Contamination)
- The principal component transformation matrix $W \in \mathbb{R}^{82 \times 15}$ is derived from the eigenvectors of the empirical covariance matrix $\Sigma$:
  $$\Sigma = \frac{1}{N} (X - \mu)^T (X - \mu)$$
- If the held-out test observations are included in calculating $\mu$ and $\Sigma$, the coordinate axes of the PCA projection are rotated to accommodate the variance of test instances. 
- The model trained on these coordinates has implicitly "seen" the geometric orientation of the test set, producing artificially optimistic generalization metrics.

### 2.2 Centroid Coordinate Leakage (K-Means Contamination)
- K-Means minimizes the within-cluster sum of squares:
  $$J = \sum_{k=1}^K \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$
- If test instances influence the centroid coordinates $\mu_k$, then the cluster centers are shifted toward test-set points.
- When an out-of-sample observation is assigned to a cluster, it is being assigned to a centroid whose position was partially determined by that exact observation. This violates the core independence assumption of out-of-sample validation:
  $$P(X_{\text{test}} \mid \theta_{\text{train}}) \neq P(X_{\text{test}} \mid \theta_{\text{train} \cup \text{test}})$$

---

## 3. The Strict Cross-Validation Protocol for Phase 5

To ensure zero information contamination, the Phase 5 predictive modeling pipeline must adhere to the following deterministic sequence for every fold in $K$-Fold Cross-Validation:

### Protocol Rules:
1. **Split First:** The dataset must be partitioned into $X_{\text{train}}, y_{\text{train}}$ and $X_{\text{test}}, y_{\text{test}}$ **BEFORE** any scaling, PCA, or K-Means operation.
2. **Fit on Train Only:** The `StandardScaler`, `PCA(n_components=15)`, and `KMeans(n_clusters=7)` estimators must be called with `.fit()` strictly on $X_{\text{train}}^{\text{skills}}$.
3. **Transform Held-Out Sets:**
   - $X_{\text{test}}^{\text{skills}}$ is projected into PCA space using `pca_train.transform()`.
   - Test instances are assigned to clusters using `kmeans_train.predict()` (nearest centroid assignment based strictly on training-derived centroid coordinates).
4. **Independent Target Encoding:** All categorical encoders (for `role_family`, `city_clean`, or `seniority`) must compute target means strictly from $y_{\text{train}}$.
5. **Ensemble Pipeline:** Steps 2–4 must be packaged inside a `scikit-learn` `Pipeline` or explicit cross-validation loop.

### Correct Algorithmic Implementation Architecture:

```python
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

kf = KFold(n_splits=5, shuffle=True, random_state=42)

for fold, (train_idx, test_idx) in enumerate(kf.split(df)):
    # 1. Partition Data
    df_train = df.iloc[train_idx]
    df_test = df.iloc[test_idx]
    
    # 2. Extract Technical Skill Arrays
    X_train_skills = df_train[skill_cols].values
    X_test_skills = df_test[skill_cols].values
    
    # 3. Fit Pipeline Strictly on Training Partition
    scaler = StandardScaler(with_mean=True, with_std=False).fit(X_train_skills)
    X_train_centered = scaler.transform(X_train_skills)
    X_test_centered = scaler.transform(X_test_skills)
    
    pca = PCA(n_components=15, random_state=42).fit(X_train_centered)
    X_train_pca = pca.transform(X_train_centered)
    X_test_pca = pca.transform(X_test_centered)
    
    kmeans = KMeans(n_clusters=7, random_state=42, n_init=10).fit(X_train_pca)
    
    # 4. Generate Cluster Features via Nearest Centroid Assignment
    train_clusters = kmeans.labels_
    test_clusters = kmeans.predict(X_test_pca)
    
    # 5. Assemble Feature Sets A, B, and C
    # Feature Set A: Original metadata + 82 binary skills
    # Feature Set B: Original metadata + 15 PCA components (X_train_pca / X_test_pca)
    # Feature Set C: Feature Set A + One-Hot Encoded cluster indicators
    
    # 6. Fit Supervised Models (Ridge, Random Forest, XGBoost)
    # 7. Evaluate on Held-Out Test Fold
```

---

## 4. Phase 4.1 Certification of Compliance

We hereby certify that:
1. The cluster labels generated in Phase 4.1 and saved to [`data/processed/job_archetype_assignments.parquet`](file:///e:/Job%20Market/data/processed/job_archetype_assignments.parquet) ($N = 116,830$) represent **exploratory structural mappings** on the skill-bearing population designed exclusively to answer RQ2.
2. None of the Phase 4.1 cluster labels have been merged into [`data/processed/modeling_dataset.parquet`](file:///e:/Job%20Market/data/processed/modeling_dataset.parquet).
3. The modeling dataset remains clean and pristine, ready for fold-specific feature generation in Phase 5.
4. Any violation of this protocol in Phase 5 will be flagged as an immediate quality gate failure.

*Protocol signed and certified.*
