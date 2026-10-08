# Phase 5 Scientific Audit & Methodological Review
**INT234 Predictive Analytics — Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning**

**Audit Conducted By:** Senior Machine Learning Researcher, Statistical Reviewer & Reproducibility Auditor  
**Date:** October 2026  
**Audit Baseline:** Phase 4.2 Frozen Baseline & Phase 5 Supervised Salary Modeling Execution  
**Operating Mode:** `/ponytail` Controlled Academic & Methodological Audit

---

## 1. Audit Scope & Objectives

This audit provides an independent, skeptical, and rigorous evaluation of the Phase 5 implementation, quantitative outputs, and reporting artifacts. The audit does not seek to optimize metrics or rerun expensive pipelines unnecessarily; rather, it verifies:
1. **Target and Partitioning Fidelity:** Verification that $N = 34,036$, target definitions, and 80/20 train/test isolation comply with project protocols.
2. **Leakage Elimination:** End-to-end tracing of predictor matrices, scalers, PCA transformers, K-Means clusterers, and encoders to ensure zero target or exploratory archetype leakage.
3. **Feature Set Validity (A vs. B vs. C):** Verification of the fold-safe construction of Feature Sets A (123 features), B (56 features), and C (130 features).
4. **Model Selection & Governance:** Verification that hyperparameter tuning and model selection were governed exclusively by 5-fold cross-validation on the training set, with the test set evaluated exactly once.
5. **Empirical Consistency:** Cross-checking values across source scripts, saved CSV/JSON tables, high-DPI figures, the executed notebook, model card, executive summary, and comprehensive research report.
6. **Scientific Claim Calibration:** Eliminating unsupported causal statements, philosophical absolutes, and overclaims regarding cluster value or model explanatory power.

---

## 2. Implementation Findings & Checklist

| Audit Checkpoint | Expected Criteria | Actual Implementation | Audit Status |
|---|---|---|---|
| **Target Definition** | `salary_midpoint` in USD ($30k–$600k) | Verified in `data.py`: arithmetic midpoint of `salary_min` and `salary_max`. Zero nulls. | **PASS** |
| **Cohort Size** | $N = 34,036$ | Exactly 34,036 rows loaded from `modeling_dataset.parquet`. | **PASS** |
| **Train/Test Split** | Strict 80% / 20% holdout split | $N_{\text{train}} = 27,228$ ($80.0\%$), $N_{\text{test}} = 6,808$ ($20.0\%$), locked at `random_state = 42`. | **PASS** |
| **Test Set Isolation** | Strict isolation until final model freeze | Test set evaluated only once after CV and tuning (lines 246–287 of `run_phase5_experiments.py`). | **PASS** |
| **Target Leakage** | Complete removal of target-derived variables | `salary_min`, `salary_max`, `salary_band`, `log_salary`, `job_id` quarantined. 0 leaked columns. | **PASS** |
| **Archetype Leakage** | No use of precomputed exploratory clusters | Exploratory `job_archetype_assignments.parquet` was never merged into CV predictors. | **PASS** |
| **Fold-Safe Transformations** | Preprocessing fitted strictly on train folds | `MetadataTransformer`, `FoldSafeSkillPCA`, and `FoldSafeArchetypeTransformer` fit strictly on fold training data. | **PASS** |
| **Feature Set A** | Explicit metadata + 82 binary skills | 123 columns: 5 seniority, 18 role, 16 city, remote flag, skill count, 82 binary skills. | **PASS** |
| **Feature Set B** | Metadata + 15 fold-safe PCs | 56 columns: 41 metadata + 15 centered covariance PCs. | **PASS** |
| **Feature Set C** | Set A + 7 fold-safe archetype indicators | 130 columns: 123 Set A + 7 one-hot indicators assigned via fold training centroids. | **PASS** |
| **Cross-Validation** | 5-Fold CV on training partition only | 5 folds with `random_state = 42` across Dummy, Ridge, RF, GBDT, XGB, and MLP. | **PASS** |
| **Hyperparameter Tuning** | Controlled search on training set only | 4-point grid on XGBoost using 5-fold CV; optimal parameters selected without test leakage. | **PASS** |
| **Final Test Evaluation** | Single holdout benchmark | Single execution comparing final candidate models on the 6,808 isolated test instances. | **PASS** |
| **RQ1 Triangulation** | Distinguish importance, coefs, and associations | Explicitly separates tree gain, permutation importance, Ridge coefs, and descriptive differences. | **PASS** |
| **RQ3 Statistical Test** | Non-parametric test on archetype errors | Kruskal-Wallis $H = 88.10$, $p = 7.53 \times 10^{-17}$ ($p < 0.001$) on absolute prediction errors. | **PASS** |

---

## 3. Deep-Dive Leakage Audit

A comprehensive code trace was conducted across `src/phase5/preprocessing.py`, `src/phase5/feature_sets.py`, and `src/phase5/evaluation.py`:
1. **Target Variables:** The predictor matrix $X$ is explicitly constructed from `metadata_cols` and `tech_skills`. In `data.py`, lines 96–103 explicitly quarantine `salary_min`, `salary_max`, `salary_midpoint`, `log_salary`, and `salary_band`.
2. **Exploratory Clustering Isolation:** The 116,830-row exploratory cluster assignments generated in Phase 4.1 (`job_archetype_assignments.parquet`) were **never accessed** by the supervised feature construction modules.
3. **Training Fold Independence:** In `evaluation.py`, lines 92–104 iterate over the 5 cross-validation folds. For each fold, `builder.build_feature_set_C(X_tr_fold, X_val_fold)` is invoked:
   - `FoldSafeSkillPCA.fit` is called exclusively on `X_tr_fold[tech_skills]`.
   - `FoldSafeArchetypeTransformer.fit` is called exclusively on the training PCA projection.
   - Validation observations (`X_val_fold`) are projected into PCA space using training components and assigned to archetypes via Euclidean distance minimization to training centroids (`self.kmeans.predict(pca_val)`).
4. **Holdout Test Isolation:** When generating Feature Set C for the holdout test set (lines 213–216 of `run_phase5_experiments.py`), transformers were fitted on `X_train_df` and applied to `X_test_df` strictly via `transform()`.

**Audit Conclusion:** The implemented pipeline contains no identified target or archetype leakage. Learned transformations are fitted within training folds, and the holdout test set remains isolated until final evaluation.

---

## 4. Feature Set A vs. B vs. C Audit

The central thesis of Phase 5 is whether unsupervised archetype discovery provides incremental predictive value beyond explicit skills and metadata.

### Empirical Evidence from Verified Artifacts:
- **Feature Set A (Original Features, 123 cols):**
  - Tuned XGBoost CV MAE: **$\$36,072 \pm \$185$** | CV $R^2 = 0.4192$
  - Holdout Test MAE: **$\$36,380.64$** | Test RMSE = **$\$51,082.06$** | Test $R^2 = \mathbf{0.4233}$
- **Feature Set B (PCA Features, 56 cols):**
  - Default XGBoost CV MAE: **$\$37,089 \pm \$212$** | CV $R^2 = 0.3906$
  - Ridge CV MAE: drops to **$\$39,027$** ($R^2 = 0.3306$)
- **Feature Set C (Archetype-Augmented, 130 cols):**
  - Default XGBoost CV MAE: **$\$36,947 \pm \$204$** | CV $R^2 = 0.3950$ (essentially identical to Set A default of $\$36,944$)
  - Tuned XGBoost Holdout Test MAE: **$\$36,424.84$** | Test RMSE = **$\$50,986.96$** | Test $R^2 = \mathbf{0.4255}$
- **Observed Difference (Set C vs. Set A on Test Set):**
  - $\Delta \text{MAE} = +\$44.20$ (Set C error is $0.12\%$ higher than Set A).
  - $\Delta R^2 = +0.0022$.

### Audit Calibration:
Previous narrative text stated: *"Outcome 2 (C ≈ A) is conclusively supported."* While the empirical metrics are practically identical, claiming formal statistical equivalence without a two-one-sided $t$-test (TOST) or formal equivalence testing is technically overstated.
- **Calibrated Statement:** **Feature Set C provides no practically meaningful improvement over Feature Set A.** The discovered skill archetypes do not materially improve supervised salary prediction beyond explicit skill indicators and role metadata. High-resolution binary skill matrices already supply the principal predictive signal available from the observed job characteristics.

---

## 5. Model Selection & Cross-Validation Audit

- **Baseline Comparison:** Naive median prediction yields CV MAE = $\$49,502 \pm \$398$ and Test MAE = $\$50,805.56$ ($R^2 = -0.0117$). All supervised models significantly outperform this naive benchmark.
- **Linear vs. Non-linear Models:**
  - Ridge achieves Test MAE = $\$39,147.25$ ($R^2 = 0.3526$).
  - Random Forest achieves Test MAE = $\$37,699.17$ ($R^2 = 0.3972$).
  - Gradient Boosting achieves Test MAE = $\$37,445.96$ ($R^2 = 0.3997$).
  - Default XGBoost achieves Test MAE = $\$37,459.91$ ($R^2 = 0.3991$).
  - Tuned XGBoost achieves Test MAE = **$\$36,380.64$** ($R^2 = \mathbf{0.4233}$).
- **Governance Integrity:** Model selection prioritized CV MAE and stability. XGBoost was chosen on the basis of training CV performance ($\text{MAE} = \$36,072$) before holdout evaluation. The holdout test set was not used as a selection criterion.

---

## 6. RQ1 (Skill Associations) Audit & Triangulation

RQ1 asks: *Which skills and skill combinations are most associated with higher salaries?*

### Audit Findings on Triangulation:
The repository evaluates four distinct quantities:
1. **Tree Split Gain (`phase5_feature_importance.csv`):** Measures the relative contribution of each feature to variance reduction across tree splits in XGBoost.
2. **Permutation Importance (`phase5_permutation_importance.csv`):** Evaluates the mean increase in test MAE when a feature's values are randomly permuted.
3. **Standardized Ridge Coefficients (`src/phase5/interpretability.py`):** Captures conditional linear associations under $L_2$ regularization.
4. **Descriptive Profile Differences:** Empirical median comparisons from Phase 3 and Phase 5.

### Key Skills Identified:
- `machine_learning`: Tree gain = $0.0384$, Permutation impact = $+\$812$, Ridge coef = $+\$5,124$.
- `pytorch`: Permutation impact = $+\$645$, Ridge coef = $+\$6,380$.
- `deep_learning`: Permutation impact = $+\$548$, Ridge coef = $+\$5,892$.
- `aws`: Permutation impact = $+\$582$, Ridge coef = $+\$3,845$.
- `python`: Permutation impact = $+\$465$, Ridge coef = $+\$2,914$.
- `kubernetes`: Permutation impact = $+\$486$, Ridge coef = $+\$4,120$.
- `golang`: Ridge coef = $+\$4,890$.
- `c++`: Ridge coef = $+\$4,310$.

### Required Calibration:
- **Association $\neq$ Causation:** Previous drafts occasionally used phrases such as *"command distinct premiums"* or *"raise an engineer's salary"*. These have been calibrated to **"observed salary differences between selected skill profiles"** and **"model-derived conditional associations"**.
- Confounding by seniority, role family, metropolitan location, and candidate experience must be explicitly acknowledged.

---

## 7. RQ3 (Archetype Error Differences) Audit

RQ3 asks: *Does salary-prediction error differ systematically across skill-based job archetypes?*

### Verified Metrics by Archetype ($N_{\text{test}} = 6,808$):
| Archetype ID & Name | Test $N$ | Median Actual Salary | MAE ($) | RMSE ($) | Median AE ($) | Relative MAE (%) | Archetype $R^2$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Cluster 5 (AI_ML)** | $490$ | $\$187,250$ | **$\$27,002$** | $\$36,135$ | $\$21,244$ | **$14.42\%$** | $0.4651$ |
| **Cluster 4 (DATA_BI)** | $831$ | $\$170,000$ | **$\$31,985$** | $\$43,325$ | $\$23,319$ | **$18.81\%$** | $0.4516$ |
| **Cluster 1 (DEVOPS_PLAT)** | $441$ | $\$195,000$ | **$\$32,745$** | $\$44,106$ | $\$24,377$ | **$16.79\%$** | $0.3799$ |
| **Cluster 6 (SYS_ENG)** | $420$ | $\$190,000$ | **$\$34,651$** | $\$47,761$ | $\$27,488$ | **$18.24\%$** | $0.4797$ |
| **Cluster 2 (WEB_FRONT)** | $863$ | $\$165,650$ | **$\$35,096$** | $\$49,908$ | $\$26,042$ | **$21.19\%$** | $0.3849$ |
| **Cluster 0 (FOUND_TECH)** | $2,950$ | $\$170,000$ | **$\$37,664$** | $\$51,966$ | $\$28,027$ | **$22.16\%$** | $0.3930$ |
| **Cluster 3 (CLOUD_ARCH)** | $813$ | $\$220,000$ | **$\$46,098$** | $\$66,848$ | $\$33,333$ | **$20.95\%$** | $0.2818$ |

### Hypothesis Test Verification:
The Kruskal-Wallis test on absolute prediction errors yields:
$$H = 88.10, \quad p = 7.53 \times 10^{-17} \quad (p < 0.001)$$
- **Calibrated Interpretation:** Prediction-error distributions differ significantly across the identified archetypes. The Kruskal-Wallis test confirms that these error distributions are statistically distinct, but the test statistic itself does not demonstrate the causal mechanism of the differences.
- `CLOUD_ARCH`'s elevated absolute MAE ($\$46,098$) is consistent with its significantly higher salary scale (median $\$220\text{k}$) and wider dispersion. Its relative error ($20.95\%$) is comparable to other domains.
- `FOUND_TECH`'s higher relative error ($22.16\%$) is consistent with the heterogeneous, broad nature of generic technical postings.

---

## 8. Bias-Variance & Residual Audit

- **Train vs. Test Error Gap:**
  - Train MAE = $\$33,525.35$ vs. Test MAE = $\$36,380.64$ ($\Delta \text{MAE} = \$2,855.29$, or $7.8\%$).
  - Train $R^2 = 0.4993$ vs. Test $R^2 = 0.4233$ ($\Delta R^2 = 0.0760$).
- **Calibrated Finding:** The relatively small train-to-test error gap indicates controlled generalization error and no evidence of severe overfitting.
- **Residual Distribution:** Mean residual on the test set is $-\$374.32$ (essentially unbiased centered error). The median absolute error is $\$26,384.22$.
- **Upper-Tail Behavior:** Postings with actual salaries exceeding $\$350,000$ exhibit underprediction. This is attributable to the empirical scarcity of extreme compensation observations in online job postings ($< 1\%$ of data $> \$400\text{k}$).

---

## 9. Comprehensive Claim Corrections Applied

1. **Feature Set C Value Proposition:**
   - *Previous:* "Outcome 2 (C ≈ A) holds conclusively."
   - *Calibrated:* **"Feature Set C provides no practically meaningful improvement over Feature Set A."** (Difference is $+\$44.20$ MAE, or $0.12\%$).
2. **Predictive Capacity:**
   - *Previous:* "...explicit skills supply complete predictive signal..."
   - *Calibrated:* **"...explicit skills supply the principal predictive signal available from the observed skill and job metadata."** (Test $R^2 \approx 0.4233$ explicitly acknowledged).
3. **Causal Language:**
   - *Previous:* "...command distinct premiums...", "...raise an engineer's salary..."
   - *Calibrated:* **"...observed salary differences between selected skill profiles..."**, explicitly noting confounding by seniority, role, geography, and experience.
4. **Generalization Overclaim:**
   - *Previous:* "...confirming absence of overfitting."
   - *Calibrated:* **"...the relatively small train-to-test error gap indicates controlled generalization error and no evidence of severe overfitting."**
5. **Leakage Assertion:**
   - *Previous:* "100% guaranteed zero leakage."
   - *Calibrated:* **"The implemented pipeline contains no identified target or archetype leakage: learned transformations are fitted within training folds, and the holdout test set is isolated until final evaluation."**

---

## 10. Artifact Integrity & Cross-Validation Matrix

All 10 required CSV tables, 18 high-DPI figures, 4 serialized model files, and the executed Jupyter notebook were audited for numerical consistency:

| Artifact Path | Expected Contents | Verified Metrics / Details | Integrity Status |
|---|---|---|---|
| `models/phase5/best_model.pkl` | Tuned XGBoost regressor | Valid binary, 619,464 bytes | **VERIFIED** |
| `models/phase5/best_pipeline.pkl` | Feature Set A transformer | Valid binary, 3,317 bytes | **VERIFIED** |
| `models/phase5/feature_metadata.json` | Model metadata & test metrics | 123 features, Test MAE = $36,380.64, R² = 0.4233 | **VERIFIED** |
| `models/phase5/model_metrics.json` | Final candidate metrics | Matches test results table exactly | **VERIFIED** |
| `reports/tables/phase5/phase5_data_audit.csv` | Initial data audit | N = 34,036, 0 missing, target stats verified | **VERIFIED** |
| `reports/tables/phase5/phase5_cv_results.csv` | 5-Fold CV metrics | Baselines + Sets A, B, C across all models | **VERIFIED** |
| `reports/tables/phase5/phase5_model_comparison.csv` | Feature set comparison | Sets A, B, C comparative rows match code | **VERIFIED** |
| `reports/tables/phase5/phase5_hyperparameter_results.csv` | Tuning grid evaluations | 4 parameter configurations, depth 6 optimal | **VERIFIED** |
| `reports/tables/phase5/phase5_test_results.csv` | Holdout test evaluation | Train/Test MAE, RMSE, R², MAPE, Gaps | **VERIFIED** |
| `reports/tables/phase5/phase5_bias_variance.csv` | Bias/variance diagnostics | Train vs Test MAE and R² gaps | **VERIFIED** |
| `reports/tables/phase5/phase5_archetype_errors.csv` | Archetype-level errors | N, MAE, RMSE, Rel MAE across all 7 archetypes | **VERIFIED** |
| `reports/tables/phase5/phase5_feature_importance.csv` | Tree split gain importances | 123 features ranked | **VERIFIED** |
| `reports/tables/phase5/phase5_permutation_importance.csv` | Test permutation importances | 123 features with mean and std impact | **VERIFIED** |
| `reports/tables/phase5/phase5_rq1_skill_associations.csv` | Triangulated skill rankings | Composite ranking across tree, perm, and Ridge | **VERIFIED** |
| `notebooks/05_salary_modeling.ipynb` | Executed Jupyter Notebook | 24 sections, fully executed with embedded charts | **VERIFIED** |
| `reports/figures/phase5/` (18 PNGs) | High-DPI diagnostic plots | Figures 01 through 18 present and properly labeled | **VERIFIED** |

---

## 11. Remaining Methodological Limitations

1. **Unobserved Compensation Components:** ATS job descriptions lack data on equity (stock options/RSUs), performance bonuses, and sign-on incentives, which comprise a large portion of senior tech compensation.
2. **Text Parsing Resolution:** Keyword extraction confirms skill presence but does not measure candidate proficiency or required years of experience.
3. **Substantial Unexplained Variance:** An $R^2$ of $\sim 0.42$ and MAE of $\sim \$36\text{k}$ mean that individual salary predictions can still deviate substantially from actual ground truth. Macroeconomic factors, company prestige, funding stage, and negotiation dynamics remain unobserved.
4. **Upper-Tail Compression:** Observations with compensation above $\$400,000$ are empirically sparse, leading to underprediction in the extreme right tail.

---

## 12. Final Audit Verdict

Based on direct inspection of source code, execution pipelines, serialized models, and analytical outputs:
- The Phase 5 experimental architecture is methodologically sound, strictly fold-safe, and free of identified data leakage.
- The quantitative conclusions are supported by verified numerical artifacts.
- All overclaims and philosophical absolutes have been surgically corrected.

### Formal Status:
> **GREEN — PHASE 5 SCIENTIFICALLY AUDITED AND FROZEN**
