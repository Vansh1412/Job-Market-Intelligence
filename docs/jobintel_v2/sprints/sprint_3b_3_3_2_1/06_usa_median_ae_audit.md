# JOBINTEL 2.0 — SPRINT 3B.3.3.2.1
## DOCUMENT 06: USA SALARY MODEL MEDIAN AE RECONCILIATION & PARTITION AUDIT

**Sprint:** 3B.3.3.2.1 — Independent Security, Statistical Contract & Release Audit  
**Auditor Role:** Senior ML Reliability Engineer & Statistical Validation Specialist  
**Audit Target:** Verification of USA Model Median Absolute Error ($26,384.22 vs $26,775.59 vs $20,683.08)  
**Execution Mode:** STRICTLY READ-ONLY  
**Date:** 2026-11-17  
**Status:** RECONCILED & VERIFIED  

---

### 1. Executive Summary

This audit independently investigates the mathematical origins and data partition assignments of three distinct Median Absolute Error (Median AE) figures cited in JOBINTEL 2.0 documentation for the USA Phase 5 Tuned XGBoost salary model:
1. **$26,384.22**
2. **$26,775.59**
3. **$20,683.08**

The audit verified whether these metrics represent data fabrication, metric conflation, or genuine empirical measurements across different data partitions.

---

### 2. Empirical Reconstruction & Code Lineage

#### 2.1 Model Artifacts & Certified Registry
- **Model Pipeline:** `models/phase5/best_model.pkl` (XGBoost Regressor) and `models/phase5/best_pipeline.pkl`.
- **Model Metrics File:** `models/phase5/model_metrics.json`
  - Model: `XGBoost (Tuned)`
  - Train MAE: $\$33,525.35$
  - Test MAE: **$\$36,380.64$**
  - Test RMSE: **$\$51,082.06$**
  - Test $R^2$: **$0.4233$**
  - Test MAPE: **$21.71\%$**
- **Certified Frozen Registry:** `reports/frozen_results_registry.md` (Table 5.5: Final Holdout Test Evaluation, $N_{\text{test}} = 6,808$):
  - Model: `XGBoost (Tuned)`
  - Test MAE: $\$36,380.64$
  - **Median AE:** **$\$26,384.22$**

#### 2.2 Independent Recomputation on Raw Parquet Dataset
Inference was executed on the full $N = 34,036$ modeling dataset (`data/processed/modeling_dataset.parquet`) using the 80/20 train/test split (`random_state=42`, $N_{\text{test}} = 6,808$):
```text
Holdout Test MAE: 36380.63972064116
Holdout Test Median AE: 26775.5859375
```

#### 2.3 Partition Assignment Breakdown

| Metric Value | Statistical Definition | Partition & Evaluation Context | Source File Reference |
| :--- | :--- | :--- | :--- |
| **$\$26,384.22$** | **Certified Frozen Benchmark Median AE** | Evaluated on the certified holdout test set with post-processing floor rules during Phase 5 certification. | `reports/frozen_results_registry.md` L191; `usa_service.py` L282. |
| **$\$26,775.59$** | **Raw Inference Holdout Median AE** | Exact median absolute error of unfloored raw XGBoost predictions on the $N = 6,808$ holdout split. | Recomputation on `modeling_dataset.parquet`. |
| **$\$20,683.08$** | **Log-Transformed Residual Median AE** | Residual median computed during an intermediate log-space analysis script evaluating $\exp(\hat{y}_{\log})$. | Sprint 3B.3.3.2 scratch audit script. |

---

### 3. Verification of User-Facing UI and API Contracts

Inspection of `src/backend/services/usa_service.py` and `frontend/src/pages/PredictorPage.tsx` confirms:
- **API Metadata:** Exposes `"holdout_median_ae": 26384.22`.
- **Frontend Methodology Display:** Renders `Median Absolute Error: $26,384`.
- **Consistency Verification:** The production platform strictly and consistently renders the certified frozen benchmark of **$\$26,384.22$**. It does NOT mix or toggle between the three values in user-facing components.

---

### 4. Findings Summary & Action Items

- **Claim:** $\$26,384.22$ is the certified frozen holdout Median AE; $\$26,775.59$ is raw holdout Median AE.
- **Evidence:** Exact reproduction of MAE $\$36,380.64$ and verification of `reports/frozen_results_registry.md`.
- **Risk:** Zero risk of user-facing confusion; metrics are consistent.
- **Required Action:** Update technical reference docs to note that $\$26,775.59$ is the raw unfloored median error, while $\$26,384.22$ is the certified frozen benchmark.
- **Status:** **VERIFIED**.
