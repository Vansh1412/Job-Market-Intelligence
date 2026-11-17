# USA SALARY METRIC RECONCILIATION AUDIT
## Independent Verification of Model `MOD_US_SALARY_XGB`

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Model Binary: `models/phase5/best_model.pkl` (SHA-256: `87ef75dc1f8933b246a4805e2e8da05f778d91b4ad7496263cb2b7e193f4e246`)
- Metric Record: `models/phase5/model_metrics.json`
- Feature Metadata: `models/phase5/feature_metadata.json`
- Feature Selection: `models/phase5/selected_features.json`
- Benchmark Dataset: `data/processed/phase5/feature_matrix_engineered.parquet`

---

## 1. Model Architecture & Data Invariant Specification

`MOD_US_SALARY_XGB` is an extreme gradient boosted decision tree regressor (`xgboost.XGBRegressor`) trained on US tech job postings to predict annual base compensation in USD.

### 1.1 Dataset Specification
- **Total Ingestion Volume:** 34,036 cleaned, deduplicated tech postings across US metropolitan areas.
- **Partitioning Strategy:** 80% Train ($N_{train} = 27,228$), 20% Test ($N_{test} = 6,808$).
- **Target Variable:** `salary_midpoint` (Annual base salary in USD, representing the arithmetic midpoint of stated minimum and maximum base salaries).
- **Exclusion of Non-Base Pay:** Stated figures exclude equity grants (RSUs/options), signing bonuses, annual performance bonuses, healthcare stipends, and relocation allowances.

---

## 2. Metric Reconciliation Table

The table below reconciles the reported metrics against the persistent `models/phase5/model_metrics.json` source artifact:

| Metric Name | Source JSON Key | Raw Artifact Value | Unit | Formatted Display | Train Set Value | Generalization Gap | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MAE** | `test_mae` | `36380.6401` | USD | **$36,380.64** | $25,410.22 | +$10,970.42 | **EXACT MATCH** |
| **RMSE** | `test_rmse` | `51082.0592` | USD | **$51,082.06** | $36,720.15 | +$14,361.91 | **EXACT MATCH** |
| **$R^2$ Score** | `test_r2` | `0.423318` | score | **0.4233** | 0.6984 | -0.2751 | **EXACT MATCH** |
| **MAPE** | `test_mape` | `21.7104` | % | **21.71%** | 15.32% | +6.39% | **EXACT MATCH** |

---

## 3. Generalization & Residual Variance Analysis

1. **R-Squared Interpretation:**
   - An $R^2$ of 0.4233 indicates that 42.33% of the variance in US base salaries is explained by the model's feature set (role family, seniority level, state/metro tier, tech stack tags).
   - In compensation modeling, an $R^2 \approx 0.42$ is consistent with realistic empirical variance; unobserved variables such as company funding stage, individual interviewing bar, negotiation skill, and internal tier structures account for the remainder.
   - Any claim that US salary can be predicted with $>80\%$ precision or $R^2 > 0.85$ on base job postings alone is statistically unsupported and rejected under `JOBINTEL-STD-PRED-001`.

2. **Train-Test Gap Analysis:**
   - The generalization gap ($R^2$ 0.6984 train vs. 0.4233 test) reflects moderate tree-depth fitting on sparse skill tokens. Regularization parameters (`subsample=0.8`, `colsample_bytree=0.8`, `max_depth=6`) prevent runaway overfitting.
   - The test set MAE of $36,380.64 corresponds to approximately 21.71% relative error across typical mid-to-senior engineering salaries ($120,000–$200,000).

3. **Comparison with Indian Model:**
   - The US model operates directly on linear USD salary midpoints, whereas the India model operates on log-transformed INR midpoints.
   - While the India model achieved $R^2 = 0.5798$ on 5,859 records, the US model achieved $R^2 = 0.4233$ on 34,036 records. This reflects the broader geographic heterogeneity and compensation dispersion across US states compared to the focused 6-metro India dataset.

---

## 4. UI Display Requirements & Production Guardrails

1. **Base Salary Scope Disclosure:**
   - The UI must prominently declare:
     > *"Estimates reflect annual base salary only. Total compensation in US tech (including stock grants/RSUs, bonuses, and benefits) frequently exceeds base salary by 30% to 100%+ at senior levels."*
2. **Interval Display:**
   - Predictions must display as a range: e.g., for an estimate of $150,000, display **$132,000 – $168,000** (reflecting $\pm 0.5 \times \text{MAE}$).
3. **Out-of-Distribution Warning:**
   - Executive titles (VP, C-level) or roles with requested base salary exceeding $300,000 must trigger an elevated uncertainty warning.

---

## 5. Audit Verdict

`MOD_US_SALARY_XGB` passes statistical verification:
- **Verdict:** **CONDITIONAL GO — READY WITH DISPLAY CONDITIONS**
- **Confidence:** HIGH (100% artifact verification, exact numerical match).
