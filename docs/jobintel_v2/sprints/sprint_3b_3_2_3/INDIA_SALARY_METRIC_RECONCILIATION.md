# INDIA SALARY METRIC RECONCILIATION AUDIT
## Independent Verification of Model `MOD_IN_SALARY_HGBR`

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Model Binary: `models/india/final_model.pkl` (SHA-256: `7a450531fa4356e30018a4beae69837a281fb2b757ea56e483fc1eb09adfe2bb`)
- Evaluation Report: `models/india/final_evaluation.json`
- Model Metadata: `models/india/final_model_metadata.json`
- Preprocessor: `models/india/final_preprocessor.pkl`
- Feature Names: `models/india/final_feature_names.json`
- Benchmark Dataset: `data/processed/india/cleaned_jobs_india.parquet`

---

## 1. Model Architecture & Data Invariant Specification

`MOD_IN_SALARY_HGBR` is a supervised gradient boosted decision tree regressor (`sklearn.ensemble.HistGradientBoostingRegressor`) designed to estimate annualized software and tech industry compensation in India.

### 1.1 Dataset Specification
- **Total Ingestion Volume:** 5,859 records across verified tier-1 and tier-2 Indian tech hubs (Bengaluru, Hyderabad, Pune, Mumbai, NCR, Chennai).
- **Partitioning Strategy:** 80% Train ($N_{train} = 4,686$), 20% Stratified Holdout ($N_{test} = 1,173$).
- **Stratification Basis:** Stratified across discretized salary quantile bins and primary role taxonomy to prevent domain shift between train and test.
- **Target Variable:** `salary_midpoint_inr` (Annual base salary midpoint in Indian Rupees).
- **Target Transformation:** $\hat{y} = \text{expm1}(f(\mathbf{x}))$, where model trains on $z = \log(1 + y)$ to stabilize right-skewed compensation variance.

---

## 2. Metric Reconciliation Table

The following table compares the metrics reported in Sprint 3B.3.2.2 with the underlying source JSON artifacts:

| Metric Name | Source JSON Key | Raw Artifact Value | Unit | Formatted Display | Baseline Dummy | Error Reduction | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MAE (INR)** | `test_mae_inr` | `371472.7128` | INR | ₹3,71,472.71 | ₹7,72,569.80 | **51.92%** | **EXACT MATCH** |
| **MAE (LPA)** | `test_mae_lpa` | `3.714727` | Lakhs INR | **₹3.71 LPA** | ₹7.73 LPA | **51.92%** | **EXACT MATCH** |
| **Median AE (INR)** | `test_median_ae_inr` | `207703.9582` | INR | ₹2,07,703.96 | ₹6,45,000.00 | **67.80%** | **EXACT MATCH** |
| **Median AE (LPA)** | `test_median_ae_lpa` | `2.077040` | Lakhs INR | **₹2.08 LPA** | ₹6.45 LPA | **67.80%** | **EXACT MATCH** |
| **RMSE (INR)** | `test_rmse_inr` | `621880.9314` | INR | ₹6,21,880.93 | ₹9,58,720.10 | **35.13%** | **EXACT MATCH** |
| **RMSE (LPA)** | `test_rmse_lpa` | `6.218809` | Lakhs INR | **₹6.22 LPA** | ₹9.59 LPA | **35.13%** | **EXACT MATCH** |
| **$R^2$ Score** | `test_r2` | `0.579822` | score | **0.5798** | 0.0000 | N/A | **EXACT MATCH** |
| **MAPE** | `test_mape` | `35.2189` | % | **35.22%** | 84.12% | N/A | **EXACT MATCH** |

---

## 3. Discrepancy & Rounding Analysis

1. **Mean vs. Median Absolute Error:**
   - The holdout MAE is ₹3.71 LPA, while the Median Absolute Error is ₹2.08 LPA.
   - The ratio $\text{MAE} / \text{Median AE} = 1.79$ indicates the presence of a long right tail in tech executive compensation. For 50% of the candidate population, the prediction error is within ₹2.08 LPA.
   - In accordance with `JOBINTEL-STD-PRED-001`, both MAE and Median AE must be disclosed in documentation to accurately represent model behavior across mid-tier and senior-tier roles.

2. **Rounding Protocol:**
   - Display values of `₹3.71 LPA`, `₹2.08 LPA`, `₹6.22 LPA`, and `0.58` ($R^2$) are standard two-decimal representations of exact values (`3.7147`, `2.0770`, `6.2188`, `0.5798`). No truncation or artificial suppression occurred.

3. **Baseline Superiority:**
   - The dummy regressor (predicting median salary across all roles) incurs an MAE of ₹7.73 LPA.
   - `MOD_IN_SALARY_HGBR` cuts this error by more than half (51.92% gain), demonstrating strong predictive signal extraction from job metadata.

---

## 4. UI Display Requirements & Production Guardrails

To prevent misinterpretation by job seekers and employers, the following UI presentation rules are established:

1. **Explicit Interval Presentation:**
   - Single point estimates must never be displayed alone. The UI must present an empirical range $[\hat{y} - \Delta_{25}, \hat{y} + \Delta_{75}]$.
2. **Mandatory Caveat String:**
   > *"Estimated salary range based on verified Indian tech postings. Actual compensation varies by employer scale, candidate skills, interview performance, and variable bonus structures."*
3. **Out-of-Scope Warning:**
   - If user inputs exceed 20 years experience or roles outside the 46 canonical tech occupations, a clear disclaimer must appear: *"Experience exceeds dense benchmark distribution; estimate uncertainty is elevated."*

---

## 5. Audit Verdict

`MOD_IN_SALARY_HGBR` passes statistical verification:
- **Verdict:** **CONDITIONAL GO — READY WITH DISPLAY CONDITIONS**
- **Confidence:** HIGH (100% artifact verification, exact numerical match).
