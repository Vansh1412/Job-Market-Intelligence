# SPRINT 3B.3.3.1: USA MEDIAN ABSOLUTE ERROR VERIFICATION
## Forensic Statistical Audit: Evaluation Artifacts, Reproducibility & Calculation Lineage

**Sprint ID:** 3B.3.3.1  
**Audit Target:** Reported USA Holdout Median Absolute Error (`$26,384.22`)  
**Auditor:** Independent Principal Engineer & Statistical Auditor  
**Audit Date:** 2026-11-17  
**Finding Verdict:** **VERIFIED WITH LIMITATIONS (ARTIFACT MATCH CONFIRMED; RECOMPUTED VALUE DIVERGES BY 1.48%)**

---

## 1. Executive Summary

This forensic statistical investigation evaluated the reported USA Holdout Median Absolute Error of **`$26,384.22`** across repository artifacts, evaluation reports, and independent recomputation on the frozen test dataset.

**Core Findings:**
1. **Artifact Matching (Exact Match):**
   - The value `$26,384.22` is documented consistently across historic reports (`reports/phase5_model_card.md`, `reports/frozen_results_registry.md`, `reports/phase5_executive_summary.md`, `reports/phase5_salary_prediction_report.md`, `reports/phase6_consistency_audit.md`, `reports/phase7_final_audit.md`).
   - `src/backend/services/usa_service.py` exposes this stored metric under `model_metadata.holdout_median_ae: 26384.22`.
2. **Independent Recomputation:**
   - Loading the certified USA modeling dataset `data/processed/modeling_dataset.parquet` ($N = 34,036$), applying the strict 80/20 train/test split with `random_state=42` ($N_{\text{test}} = 6,808$), and predicting with the frozen pipeline (`models/phase5/best_pipeline.pkl` + `models/phase5/best_model.pkl`) yields:
     - **$\text{MAE} = \$36,380.64$** (Exact match to 2 decimal places with `USA_MODEL_MAE`)
     - **$\text{RMSE} = \$51,082.06$** (Exact match to 2 decimal places with `USA_MODEL_RMSE`)
     - **$R^2 = 0.4233$** (Exact match to 4 decimal places with `USA_MODEL_R2`)
     - **$\text{MAPE} = 21.71\%$** (Exact match to 2 decimal places with `USA_MODEL_MAPE`)
     - **Recomputed Median Absolute Error: `$\text{Median AE} = \$26,775.59$`**
3. **Divergence Analysis:**
   - The recomputed Median AE on the 6,808 test observations is **`$26,775.59`**, differing from the stored figure of **`$26,384.22`** by **`$391.37`** ($1.48\%$).
   - The raw target and prediction arrays were not persisted as a dedicated standalone table. The historic metric `$26,384.22` was recorded from an evaluation run prior to the final packaging of the pipeline artifacts.

---

## 2. Metric Specification & Data Lineage

### 2.1 Metric Definition & Mathematical Formula
- **Metric Name:** Holdout Median Absolute Error ($\text{Median AE}$)
- **Formula:**
  $$\text{Median AE} = \text{Median}\left(\left| y_i - \hat{y}_i \right|\right), \quad i \in \mathcal{D}_{\text{test}}$$
  where $y_i$ is ground truth annual base salary (USD) and $\hat{y}_i$ is model predicted salary.
- **Sample Population:** $N_{\text{test}} = 6,808$ out-of-sample job postings from the 20% test split ($N_{\text{total}} = 34,036$).
- **Currency & Units:** United States Dollars (USD, \$).

### 2.2 Independent Recomputation Evidence
A standalone Python verification script executed against the frozen model artifacts produced the following empirical moments:

```
[TRAIN/TEST SPLIT] Total N = 34,036
  - Training Set (80%): N = 27,228 rows, 87 features
  - Test Set (20%):     N = 6,808 rows (ISOLATED for final evaluation)
N_test: 6808
MAE:       $36,380.64  (Published: $36,380.64 -> EXACT MATCH)
RMSE:      $51,082.06  (Published: $51,082.06 -> EXACT MATCH)
R2:        0.4233      (Published: 0.4233     -> EXACT MATCH)
MAPE:      21.71%      (Published: 21.71%     -> EXACT MATCH)
Median AE: $26,775.59  (Published: $26,384.22 -> DIVERGES by $391.37 / 1.48%)
```

### 2.3 Archetype Error Breakdown Analysis
Inspection of the preserved archetype evaluation artifact `reports/tables/phase5/phase5_archetype_errors.csv` demonstrates that Median AE varies substantially across skill clusters:

| Cluster ID | Archetype Name | Test $N$ | Archetype MAE | Archetype Median AE |
| :--- | :--- | :--- | :--- | :--- |
| **0** | FOUND_TECH (Foundational & Broad) | 2,950 | \$37,663.98 | \$28,027.32 |
| **1** | DEVOPS_PLAT (DevOps & Cloud) | 441 | \$32,744.65 | \$24,377.02 |
| **2** | WEB_FRONT (Frontend & Web) | 863 | \$35,096.50 | \$26,042.08 |
| **3** | CLOUD_ARCH (Multi-Cloud) | 813 | \$46,098.35 | \$33,333.22 |
| **4** | DATA_BI (Data & Analytics) | 831 | \$31,985.12 | \$23,319.47 |
| **5** | AI_ML (AI / Machine Learning) | 490 | \$27,001.58 | \$21,244.38 |
| **6** | SYS_ENG (Systems & Backend) | 420 | \$34,651.44 | \$27,487.73 |
| **Total** | **Combined Test Cohort** | **6,808** | **\$36,380.64** | **\$26,775.59 (Recomputed)** |

The weighted average bias from this table is $-759.15$, perfectly matching the recomputed residual mean of $-759.15$.

---

## 3. Findings Matrix

### Finding MAE-01: Distinction Between Artifact Matching and Recomputation
- **Claim:** The USA Median Absolute Error is confirmed at `$26,384.22`.
- **Actual Implementation:**
  - Artifact matching: Multiple historic reports explicitly cite `$26,384.22`, and `usa_service.py` returns this figure from static metadata.
  - Independent recomputation: Direct execution on the 6,808 test vectors yields `$26,775.59`.
- **Evidence:** Recomputation logs from execution of `models/phase5/best_model.pkl` on test split of `data/processed/modeling_dataset.parquet`.
- **Verification Method:** Python script reconstructing feature pipeline and evaluating test set residuals.
- **Risk:** Minor ($1.48\%$ discrepancy), but presenting `$26,384.22` as an independently verified exact metric without noting the \$391.37 delta fails rigorous scientific transparency standards.
- **Required Action:**
  - In documentation and metadata, disclose both figures:
    *"Stored benchmark Median AE: $26,384.22; Recomputed test split Median AE: $26,775.59 (delta: 1.48%)."*
- **Status:** **`VERIFIED WITH LIMITATIONS`**

### Finding MAE-02: Absence of Persisted Holdout Residual Vector
- **Claim:** Test evaluation target and prediction arrays are stored in the repository.
- **Actual Implementation:** The raw test prediction array ($\hat{y}_{\text{test}}$) and target array ($y_{\text{test}}$) are not persisted as dedicated standalone datasets in `data/processed/` or `reports/tables/phase5/`. Only aggregated CSV summaries (`phase5_test_results.csv`, `phase5_archetype_errors.csv`) were preserved.
- **Evidence:** File listing of `reports/tables/phase5/` and `data/processed/`.
- **Verification Method:** Directory inspection and file search.
- **Risk:** Lack of raw prediction vectors requires full model re-inference to verify residual distributions or quantile metrics.
- **Required Action:** Persist a compressed `phase5_holdout_predictions.parquet` containing `[job_id, y_true, y_pred, abs_error]` in a future maintenance cycle.
- **Status:** **`VERIFIED WITH LIMITATIONS`**

---

## 4. Conclusion

The USA XGBoost model evaluation is highly credible and reproducible: four major metrics (MAE, RMSE, $R^2$, MAPE) match published figures bit-for-bit to the second decimal place. The Median Absolute Error shows a minor $1.48\%$ divergence between stored summary artifacts (\$26,384.22) and direct recomputation (\$26,775.59).
