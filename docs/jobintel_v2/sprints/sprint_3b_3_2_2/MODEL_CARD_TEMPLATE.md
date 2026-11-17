# JOBINTEL 2.0 — STANDARDIZED MODEL CARD TEMPLATE
## Formal Model Governance Specification, Documentation Protocol & Concrete Model Cards

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Model Governance Lead  
**Standard Reference:** `JOBINTEL-STD-PRED-001`  

---

## 1. STANDARDIZED MODEL CARD SPECIFICATION

Every machine learning model, regression estimator, and statistical scoring pipeline deployed in JOBINTEL 2.0 must maintain an audited Model Card containing the following 20 standardized sections:

```
+----------------------------------------------------------------------------------------------------+
| JOBINTEL STANDARDIZED MODEL CARD SCHEMA                                                            |
+----+------------------------------+----------------------------------------------------------------+
| #  | Section Header               | Required Content Description                                   |
+----+------------------------------+----------------------------------------------------------------+
| 1  | Model Identity               | Unique Model ID, Architecture, Framework, and Maintainer Lead  |
| 2  | Model Version & Date         | Semantic version (e.g. 1.0.0), git commit SHA, timestamp       |
| 3  | Sovereign Market Scope       | Designated national market (IN, US, UK, AU, SG, or GLOBAL)     |
| 4  | Intended Product Use         | Specific approved product features and user scenarios          |
| 5  | Out-of-Scope & Prohibited Use| Explicitly barred use cases (e.g. guaranteed contract offers)   |
| 6  | Training Dataset Description | Source identity, collection methodology, cohort filtering rules|
| 7  | Dataset Limitations & Bias   | Missing segments, survivorship bias, geographic skew           |
| 8  | Input Feature Contract       | Complete list of raw and transformed input features            |
| 9  | Target Variable Formulation  | Target definition, measurement unit, mathematical transform    |
| 10 | Evaluation Methodology       | Train/test partitioning strategy, split ratio, isolation audit |
| 11 | Evaluation Sample Size       | Number of training, validation, and holdout/test instances     |
| 12 | Primary Evaluation Metrics   | Task-specific metrics (MAE, RMSE, R2, Precision, Recall, etc.) |
| 13 | Confidence Intervals         | Statistical uncertainty intervals (e.g. Wilson, Bootstrap)     |
| 14 | Probability Calibration      | Calibration status, Raw ECE, Post-hoc scaling parameters       |
| 15 | Known Failure Modes          | Identified edge cases, outlier sensitivity, extreme ranges    |
| 16 | Demographic & Subgroup Bias  | Subgroup variance (e.g. Kruskal-Wallis across archetypes)      |
| 17 | Data Leakage Assessment      | Audit of target, preprocessing, and duplicate leakage vectors  |
| 18 | Reproducibility Credentials  | Exact script path, random seeds, environment dependencies      |
| 19 | Artifact Cryptographic Hash  | SHA-256 digest of serialized model and preprocessor files      |
| 20 | Formal Approval Status       | APPROVED / APPROVED_CONDITIONAL / REVIEW_REQUIRED / REVOKED    |
+----+------------------------------+----------------------------------------------------------------+
```

---

## 2. CONCRETE MODEL CARD 1: INDIA SALARY REGRESSOR (`MOD_IN_SALARY_HGBR`)

- **1. Model Identity:** `MOD_IN_SALARY_HGBR` | `HistGradientBoostingRegressor` (Scikit-Learn).
- **2. Model Version & Date:** Version 1.0.0 | October 2026.
- **3. Sovereign Market:** India (IN).
- **4. Intended Product Use:** Benchmark annual CTC estimation for software engineering and data roles in India based on role, experience, location, and technical skills.
- **5. Out-of-Scope Use:** Guaranteed compensation quotes; executive directors (> 20 years experience); non-tech job profiles.
- **6. Training Dataset:** `indian-job-market-dataset-2025` (Phase-3 Cleaned Tech Modeling Cohort).
- **7. Dataset Limitations:** Sourced from public job board postings; reflects advertised salary midpoints, not final negotiated compensation.
- **8. Feature Contract:** 290 raw features $\to$ 327 post-preprocessed inputs (role, experience bounds, city groupings, work mode, 284 skill flags).
- **9. Target Variable:** `salary_midpoint_inr` with `log1p` transformation. Displayed in Lakhs Per Annum (LPA).
- **10. Evaluation Methodology:** 80/20 Stratified Random Split.
- **11. Sample Size:** Total: 5,859 | Train: 4,686 | Holdout: 1,173.
- **12. Primary Metrics:**
  - $\text{MAE} = \text{₹3,71,472.71}$ (3.71 LPA)
  - $\text{Median Absolute Error} = \text{₹2,07,703.96}$ (2.08 LPA)
  - $\text{RMSE} = \text{₹6,21,880.93}$ (6.22 LPA)
  - $R^2 = 0.5798$ (~58.0% explained variance)
  - $\text{MAPE} = 35.22\%$
  - $\text{Improvement vs Baseline Dummy} = 51.92\%$
- **13. Confidence Intervals:** Residual P25–P75 illustrative prediction interval: $[-1.64\text{ LPA}, +1.82\text{ LPA}]$.
- **14. Calibration Status:** N/A (Continuous Regression).
- **15. Known Failure Modes:** Tends to under-predict specialist executive salaries ($> \text{₹50 LPA}$).
- **16. Subgroup Bias:** Residual errors scale with experience; higher variance in non-metro locations.
- **17. Data Leakage:** Preprocessors fit strictly on train set. Target midpoints dropped from feature inputs. Group employer contamination identified for future mitigation.
- **18. Reproducibility:** Pipeline reproduced via `src/india/modeling.py` with random seed 42.
- **19. Artifact Hash:** `7a450531fa4356e30018a4beae69837a281fb2b757ea56e483fc1eb09adfe2bb`
- **20. Approval Status:** **`APPROVED_CONDITIONAL`** (Subject to prediction range display in UI).

---

## 3. CONCRETE MODEL CARD 2: USA SALARY REGRESSOR (`MOD_US_SALARY_XGB`)

- **1. Model Identity:** `MOD_US_SALARY_XGB` | `XGBRegressor` (XGBoost).
- **2. Model Version & Date:** Version 1.0.0 | October 2026.
- **3. Sovereign Market:** United States (US).
- **4. Intended Product Use:** Benchmark annual gross base salary estimation for US technology roles across seniority, city, and tech skills.
- **5. Out-of-Scope Use:** Total compensation (equity RSUs, bonus) estimation; non-tech job profiles.
- **6. Training Dataset:** USA Tech Jobs Modeling Cohort (Phase 5 Feature Set A).
- **7. Dataset Limitations:** Excludes equity, health benefits, and performance bonuses.
- **8. Feature Contract:** 123 model inputs (seniority tiers, role families, remote status, city groupings, 82 technical skills).
- **9. Target Variable:** `salary_midpoint` (Annual continuous USD base salary).
- **10. Evaluation Methodology:** 80/20 Stratified Train/Test Split.
- **11. Sample Size:** Total: 34,036 | Train: 27,228 | Test: 6,808.
- **12. Primary Metrics:**
  - $\text{MAE} = \$36,380.64$
  - $\text{RMSE} = \$51,082.06$
  - $R^2 = 0.4233$ (~42.3% explained variance)
  - $\text{MAPE} = 21.71\%$
- **13. Confidence Intervals:** Residual P25–P75 illustrative interval: $[-\$24,500, +\$26,200]$.
- **14. Calibration Status:** N/A (Continuous Regression).
- **15. Known Failure Modes:** Higher residual variance in senior/staff engineering tiers.
- **16. Subgroup Bias:** Kruskal-Wallis test confirms significant variance across archetypes ($H = 88.10, p < 10^{-16}$). Lowest error in AI/ML; highest error in Multi-Cloud Architecture.
- **17. Data Leakage:** Preprocessor pipeline fit on train set. Target midpoint dropped from feature matrix.
- **18. Reproducibility:** Pipeline reproduced via `src/phase5/` with random seed 42.
- **19. Artifact Hash:** `87ef75dc1f8933b246a4805e2e8da05f778d91b4ad7496263cb2b7e193f4e246`
- **20. Approval Status:** **`APPROVED_CONDITIONAL`** (Subject to base-salary-only disclosure).
