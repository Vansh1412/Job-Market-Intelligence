# JOBINTEL 2.0 — MODEL EVALUATION AUDIT
## Independent Statistical Audit of Evaluation Methodologies, Benchmark Independence & Metric Integrity

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Statistical Auditor  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/evaluation_metrics.csv`  

---

## 1. EVALUATION METHODOLOGY AUDIT ACROSS SYSTEMS

Every predictive, classification, and resolution engine was evaluated on four critical dimensions of data integrity:
1. **Split Strategy & Independence:** Was the evaluation set strictly isolated prior to preprocessing and training?
2. **Data Leakage Risk:** Did target variables, future time horizons, or duplicate records contaminate the training pipeline?
3. **Metric Selection Validity:** Are the selected metrics appropriate for the statistical task and loss function?
4. **Generalization Boundaries:** What are the operational limits of the evaluated models?

```
+----------------------------------------------------------------------------------------------------+
| EVALUATION INTEGRITY SCORECARD                                                                     |
+---------------------+-------------------+-------------------+------------------+-------------------+
| System ID           | Split Strategy    | Leakage Status    | Metric Selection | Audit Rating      |
+---------------------+-------------------+-------------------+------------------+-------------------+
| MOD_IN_SALARY_HGBR  | Stratified Random | CLEAN_PREPROCESS  | MAE, RMSE, R2    | PASSED (AUDITED)  |
| MOD_US_SALARY_XGB   | Stratified Random | CLEAN_PREPROCESS  | MAE, RMSE, R2    | PASSED (AUDITED)  |
| SYS_OCC_MAPPER      | Gold Benchmark    | INDEPENDENT_TEST  | Acc, Macro F1,ECE| PASSED (AUDITED)  |
| SYS_EMP_RESOLVER_V2 | Gold Benchmark    | INDEPENDENT_TEST  | Prec, Recall, FPR| PASSED (AUDITED)  |
| SYS_SKILL_EXTRACTOR | Adversarial Suite | INDEPENDENT_TEST  | Accuracy, Spec   | PASSED (AUDITED)  |
+---------------------+-------------------+-------------------+------------------+-------------------+
```

---

## 2. SYSTEM-BY-SYSTEM DETAILED EVALUATION FINDINGS

### 2.1 India Salary Regressor (`MOD_IN_SALARY_HGBR`)
- **Evaluation Design:** 80/20 train/holdout split across 5,859 records ($N_{\text{train}} = 4,686$, $N_{\text{holdout}} = 1,173$).
- **Preprocessing Leakage Check:**
  - Standard Scaler and One-Hot Encoders were fit strictly on the training partition and applied out-of-sample to holdout records. Preprocessing leakage is **absent**.
- **Target Formulation Check:**
  - Target trained on $\log(1 + y)$ and inversely transformed ($\exp(\hat{y}) - 1$) before computing MAE, RMSE, and $R^2$. Residual analysis shows symmetric log-error distribution.
- **Identified Generalization Risk (RSK-PRED-005):**
  - The split is randomized across individual job records rather than grouped by employer (`GroupKFold`). Highly represented IT service employers (TCS, Infosys, Wipro) appear in both train and holdout splits, which may slightly inflate out-of-company generalization estimates. Group-based validation is recommended for future retrainings.

### 2.2 USA Salary Regressor (`MOD_US_SALARY_XGB`)
- **Evaluation Design:** 80/20 train/test split across 34,036 records ($N_{\text{train}} = 27,228$, $N_{\text{test}} = 6,808$).
- **Performance Characteristics:**
  - $\text{MAE} = \$36,380.64$ | $R^2 = 0.4233$ | $\text{MAPE} = 21.71\%$.
  - Generalization gap between training ($\text{MAE} = \$33,421.47$) and test ($\text{MAE} = \$36,380.64$) is only $\$2,959.17$ (8.8%), confirming low overfit and stable regularized gradient boosting.
- **Kruskal-Wallis Variance Analysis:**
  - Statistically significant variance in prediction error across career archetypes ($H = 88.10, p = 7.53 \times 10^{-17}$), with AI/ML roles achieving the lowest relative error and Cloud Architecture exhibiting higher residual variance.

### 2.3 Global Canonical Occupation Mapper (`SYS_OCC_MAPPER`)
- **Evaluation Design:** Evaluated against 100 gold-standard titles curated by labour market specialists across 12 canonical occupations.
- **Statistical Metric Discipline:**
  - Correctly Mapped: 97 / 100 (**97.0%**)
  - Misclassifications: 0 / 100 (**0.0%**)
  - Unmapped Fallback: 3 / 100 (**3.0%**)
  - Macro F1: **0.9852**
- **Auditor Note on Denominator Integrity:**
  - The 97.0% accuracy is calculated over the **full population of 100 evaluation titles** ($97 / 100$). Unmapped records ($3 / 100$) are retained in the denominator and penalized as unmapped fallback rather than silently excised to claim synthetic 100% conditional precision.

### 2.4 Employer Entity Resolution Engine V2 (`SYS_EMP_RESOLVER_V2`)
- **Evaluation Design:** 100-pair adversarial benchmark spanning suffix variations, trading names, parent-subsidiary domains, cross-market name collisions, staffing agencies, and shared ATS hosts.
- **Type I vs. Type II Trade-off:**
  - Precision: **100.00%** (31 / 31 predicted matches correct)
  - Recall: **68.89%** (31 / 45 actual matches captured; 14 trade-name and cross-market pairs routed to manual review queue)
  - False Merge Rate: **0.00%** (0 / 55 true negative pairs incorrectly merged)
  - Wilson 95% Confidence Interval: **`[0.00% - 6.53%]`**
- **Auditor Conclusion:**
  - The engine eliminates catastrophic False Merges at the cost of a modest recall penalty. This conservative stance is legally and operationally correct for corporate registry matching.

---

## 3. SUMMARY OF AUDIT RECOMMENDATIONS

1. **Retain Current Model Weights & Artifacts:** No retraining or hyperparameter changes are warranted. Existing models demonstrate strong, verifiable empirical baselines.
2. **Calibrate Presentation Semantics:** Update user-facing UI copy and tooltips to present models as empirical benchmark estimators rather than deterministic outcome engines.
3. **Plan Temporal & Grouped Re-evaluations:** In future major release cycles, evaluate temporal backtesting on salary observations and GroupKFold cross-validation across corporate employers.
