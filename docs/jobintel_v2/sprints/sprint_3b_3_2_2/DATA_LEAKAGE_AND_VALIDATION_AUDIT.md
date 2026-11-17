# JOBINTEL 2.0 — DATA LEAKAGE & VALIDATION AUDIT
## Forensic Audit of Training Pipelines, Contamination Vectors & Statistical Biases

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Data Governance Lead  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/evaluation_risks.csv`  

---

## 1. THE 16-DIMENSION DATA INTEGRITY AUDIT

A forensic examination across the platform's machine learning, clustering, and heuristic pipelines was conducted across 16 potential data leakage and bias dimensions:

```
+----------------------------------------------------------------------------------------------------+
| 16-DIMENSION DATA INTEGRITY & LEAKAGE AUDIT MATRIX                                                 |
+----+-----------------------------+---------------------+-------------------+----------------------+
| #  | Integrity Dimension         | India Salary Model  | USA Salary Model  | Entity Resolver V2   |
+----+-----------------------------+---------------------+-------------------+----------------------+
| 1  | Train/Test Contamination    | CLEAN (Stratified)  | CLEAN (80/20)     | ISOLATED (Gold Test) |
| 2  | Duplicate Record Leakage    | CHECKED (De-duped)  | CHECKED (De-duped)| CURATED (100 Pairs)  |
| 3  | Temporal Lookahead Leakage  | N/A (Cross-Section) | N/A (Single Epoch)| N/A (Registry Snapshot)|
| 4  | Target Feature Leakage      | ZERO LEAKAGE        | ZERO LEAKAGE      | ZERO LEAKAGE         |
| 5  | Preprocessing / Scaler Leak | CLEAN (Fit on Train)| CLEAN (Fit on Train)| N/A                |
| 6  | Class Imbalance Discipline  | Log-transformed     | Stratified sample | 45 Pos / 55 Neg Pairs|
| 7  | Sample Selection Bias       | TECH COHORT ONLY    | TECH COHORT ONLY  | ENTERPRISE ANCHORS   |
| 8  | Survivorship Bias           | Filtered active ads | Filtered active ads| Active companies only|
| 9  | Label Measurement Noise     | Midpoint approx.    | Advertised midpoint| Verified legal names |
| 10 | Missing Data Imputation     | Explicit indicator  | Explicit indicator| Sentinel nulls       |
| 11 | Outlier Sensitivity         | Log1p dampens tails | Capped at high tier| Exact string matching|
| 12 | Covariate Distribution Shift| Monitored (2025 ed.)| Monitored (Phase 5)| Current filings      |
| 13 | Data Freshness Tracking     | Fiscal FY24-25      | Annual epoch      | Real-time API links  |
| 14 | Source Coverage Breadth     | Tech job boards     | Tech job boards   | 5 Sovereign markets  |
| 15 | Small Sample Instability    | N = 5,859 (Stable)  | N = 34,036 (Stable)| N = 100 (Uncertain CI)|
| 16 | Cross-Market Comparability  | STRICTLY ISOLATED   | STRICTLY ISOLATED | JURISDICTION-ISOLATED|
+----+-----------------------------+---------------------+-------------------+----------------------+
```

---

## 2. DEEP AUDIT OF LEAKAGE VECTORS

### 2.1 Preprocessing & Transformation Leakage (VERIFIED CLEAN)
- **Investigation:** Did standard scalers, mean imputers, or one-hot encoders compute global statistics over the combined dataset before partitioning into train and test?
- **Finding:** In both `src/india/modeling.py` and `src/phase5/` pipelines, preprocessor pipelines (`ColumnTransformer`, `StandardScaler`, `OneHotEncoder`) are instantiated within `Pipeline` objects and fit strictly on `X_train`, followed by out-of-sample `.transform()` calls on `X_test`. Preprocessing leakage is **absent**.

### 2.2 Target Leakage (VERIFIED CLEAN)
- **Investigation:** Were any input features derived from the target variable (e.g. salary range max, salary bounds)?
- **Finding:** Target midpoints were computed from explicit compensation fields (`salary_min`, `salary_max`), which were subsequently dropped from the feature matrix `X`. The input feature vector contains only role titles, experience requirements, location flags, and binary skill indicators. Target leakage is **absent**.

### 2.3 Group / Employer Contamination (IDENTIFIED RISK — RSK-PRED-005)
- **Investigation:** Did individual job postings from the same corporate employer appear in both train and holdout splits?
- **Finding:** The train/test split utilized random stratification. Because large IT employers (e.g. TCS, Infosys, Amazon, Microsoft) contribute dozens of job postings, records from the same employer appear in both sets.
- **Impact:** While the model accurately predicts compensation for companies represented in the training set, its out-of-sample error on completely new, unobserved employers may be slightly higher than the measured holdout MAE.
- **Mitigation Mandate:** In the next major training iteration, implement `GroupKFold(groups=company_name)` to measure pure out-of-company generalization.

---

## 3. SAMPLE SELECTION & SURVIVORSHIP BIAS DISCLOSURES

1. **Tech Cohort Limitation:**
   - Both the India and USA models were trained on tech-focused job postings.
   - **Mandatory UI Disclosure:** Models must be restricted to technology, software, data, and engineering roles. The API must reject or append an `OUT_OF_DOMAIN` warning if queried for non-tech occupations (e.g. healthcare, retail store management, primary agriculture).
2. **Advertised vs. Realized Compensation Bias:**
   - Training datasets record *advertised job posting salaries*, not *actual signed employment contracts*.
   - In tech hiring, final realized compensation is frequently subject to candidate negotiation, prior salary history, and competitive counter-offers.
   - **Mandatory UI Disclosure:** *"Estimates reflect advertised compensation benchmarks in hiring requisitions; finalized contractual compensation may vary based on candidate negotiation."*
