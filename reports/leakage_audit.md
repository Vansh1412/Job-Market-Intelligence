# Data Leakage Prevention and Feature Audit Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Modeling Dataset:** `data/processed/modeling_dataset.parquet` ($N = 34,036$)  
**Date:** October 5, 2026 (Updated Phase 2.1)  

---

## 1. Zero-Tolerance Data Leakage Policy

In predictive analytics, data leakage occurs when information from outside the training partition—or directly from the target variable—contaminates feature engineering, model fitting, or hyperparameter evaluation. A rigorous zero-leakage protocol was implemented during Phase 2 dataset construction and strengthened in Phase 2.1 to guarantee the academic integrity and generalization validity of all downstream models.

---

## 2. Target Variable Audit & Feature Partitioning

### 2.1 Explicit Target Variables
The target variables are isolated strictly as dependent ground truth ($y$):
1. `salary_midpoint`: Continuous target (USD/year) representing $(\text{salary\_min} + \text{salary\_max}) / 2$.
2. `log_salary`: Continuous natural log target $\ln(\text{salary\_midpoint})$ for log-transformed regression modeling.
3. `salary_band`: Categorical target (Low, Medium, High tertiles) strictly reserved for the secondary classification track.

### 2.2 Prohibited Features (Verified Excluded from Feature Matrix $X$)
The following fields exist in raw or intermediate tables but are **strictly banned** from all predictor matrices:
- `salary_min`: **BANNED.** Directly constitutes 50% of the target mathematical definition.
- `salary_max`: **BANNED.** Directly constitutes 50% of the target mathematical definition.
- `salary_period`: **BANNED.** Constant (`year`) in the modeling population; contains period leakage.
- `salary_currency`: **BANNED.** Constant (`USD`) in the modeling population.
- `salary_from_text`: **BANNED.** Metadata flag indicating ATS vs body text origin of salary.
- Target encodings or historical salary aggregates grouped by company, location, or title computed across the full dataset: **BANNED.** Any target statistics must be computed inside cross-validation folds.

---

## 3. Predictor Feature Space Verification

The feature matrix $X$ in `modeling_dataset.parquet` contains **99 independent predictor variables** constructed entirely prior to target observation:

| Feature Category | Count | Fields Included | Leakage Risk Assessment |
|---|---:|---|---|
| **Seniority** | 1 | `seniority` (5 tiers: Intern, Junior/Entry, Mid/Unspecified, Senior, Lead/Exec) | **Zero Leakage:** Derived purely from job title syntax via regular expressions. |
| **Role Family** | 1 | `role_family` (18 classes: SWE, ML/AI, Data Sci, DevOps, Mobile, Embedded, etc.) | **Zero Leakage:** Derived exclusively from title text and skill memberships. |
| **Work Mode** | 1 | `is_remote` (Binary boolean) | **Zero Leakage:** Direct ATS operational metadata flag. |
| **Location** | 1 | `city_clean` (Categorical: Top 15 US tech hubs + "Other") | **Zero Leakage:** Parsed from geographical posting strings. |
| **Skill Complexity** | 1 | `num_skills` (Integer count of valid tech skills) | **Zero Leakage:** Derived solely from the multi-hot technical skill indicator sum. |
| **Skill Multi-Hot** | 91 | 91 binary columns (82 tech + 2 prof + 7 biz) | **Zero Leakage:** Controlled vocabulary indicators from structured job post text. |

---

## 4. Preprocessing & Downstream Machine Learning Safeguards

To prevent subtle leakage during Phase 4 (Clustering) and Phase 5 (Supervised Modeling):

1. **Train/Test Splitting Precedence:**
   - The modeling dataset ($N = 34,036$) will be partitioned using an **80/20 train-test split** (`random_state=42`) **before** any feature scaling, one-hot encoding, or PCA transformations are fitted.
2. **Encoders and Scalers:**
   - `StandardScaler` and `OneHotEncoder` will be fitted **exclusively on the 80% training set** ($X_{\text{train}}$) and applied transformatively to the 20% test set ($X_{\text{test}}$).
3. **PCA Dimensionality Reduction:**
   - In supervised experiment **Feature Set B (PCA Features)**, PCA will be fitted **strictly on $X_{\text{train}}$** to prevent eigenvector contamination from the held-out evaluation data.
4. **Archetype Cluster Features:**
   - In supervised experiment **Feature Set C (Archetype Label Feature)**, the K-Means clustering model will be fitted on training skill representations, with cluster centroids fixed before predicting labels on test observations.
5. **Cross-Validation Integrity:**
   - All hyperparameter tuning (GridSearchCV / RandomizedSearchCV) will utilize scikit-learn `Pipeline` objects to ensure scaling, imputation, and transformation happen strictly inside each fold.

---

## 5. Leakage Audit Sign-Off

- [x] Target fields isolated and excluded from $X$.
- [x] Zero target-derived features present in feature space.
- [x] Feature space comprised solely of pre-hire job requirements (seniority, role, location, remote, technical skills).
- [x] Transformation pipeline design strictly enforces train-only parameter estimation.
