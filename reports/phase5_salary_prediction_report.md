# Phase 5 Research Report: Salary Prediction & Comparative Machine Learning
**INT234 Predictive Analytics — Job Market Intelligence**  
*Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning*

**Author:** Lead ML Research Engineer & Data Scientist (Antigravity)  
**Date:** October 2026  
**Status:** Scientifically Audited & Frozen Baseline

---

## 1. Objective

The primary objective of Phase 5 is to establish:
> **How accurately can job salaries be predicted from job-market characteristics, and does incorporating skill-based archetype information improve prediction?**

Operating from the frozen Phase 4.2 baseline (which established $k = 7$ recurring and reproducible skill-based structures with moderate separation and substantial overlap among skill-bearing postings), Phase 5 formulates a disciplined supervised machine learning framework to:
1. Benchmark non-linear and linear regression algorithms against naive baselines on verified compensation data ($N = 34,036$).
2. Test whether unsupervised archetype representations (PCA + K-Means) add incremental predictive value beyond explicit skill indicators (**Feature Set A vs. B vs. C**).
3. Investigate the predictive associations between specialized technical skills and salary (**RQ1**).
4. Measure whether salary prediction accuracy differs systematically across discovered job archetypes (**RQ3**).

---

## 2. Research Questions

### RQ1 — Skill-Salary Associations
> **Which skills and skill combinations are most associated with higher salaries?**
- Evaluates individual technical skills, combinations, and control variables (seniority, role family, metropolitan location).
- Adheres to the principle that **association $\neq$ causation**. The model measures empirical predictive importance, not structural macroeconomic causality.

### RQ3 — Archetype Error Differences
> **Does salary-prediction error differ systematically across skill-based job archetypes?**
- Disaggregates holdout prediction errors (MAE, RMSE, Median Absolute Error, Mean Error/Bias, and Relative Error) across the seven discovered archetypes.
- Employs non-parametric hypothesis testing (Kruskal-Wallis $H$-test) to establish whether error variations are statistically significant and distinguishes between scale-driven dispersion and model performance.

---

## 3. Dataset & Cohort Definition

The supervised modeling cohort is derived from `data/processed/modeling_dataset.parquet`, establishing:
- **Total Valid Observations ($N$):** $34,036$ postings.
- **Filtering Criteria:** Verified US technology sector postings with valid, non-null annualized salary boundaries within $[\$30,000, \$600,000]$ USD and complete role metadata.
- **Integrity Verification:**
  - Missing target values: $0$ ($0.0\%$).
  - Missing predictor values: $0$ ($0.0\%$).
  - Duplicate posting IDs: $0$ ($0.0\%$).
- **Predictor Dimensions:** 82 standardized binary technical skill features (Taxonomy D) and 5 structured metadata predictors (seniority, role family, city, remote flag, skill count).

---

## 4. Target Definition & Statistical Analysis

### 4.1 Target Variable Definition
The primary regression target is `salary_midpoint`, defined as:
$$\text{salary\_midpoint} = \frac{\text{salary\_min} + \text{salary\_max}}{2}$$

### 4.2 Target Distributional Statistics ($N = 34,036$)
| Metric | Raw Salary Midpoint ($) | Log-Transformed ($\log(1 + y)$) |
|---|---|---|
| Count | $34,036$ | $34,036$ |
| Mean | $\$187,030.73$ | $12.0838$ |
| Standard Deviation | $\$65,752.68$ | $0.3341$ |
| Minimum | $\$30,000.00$ | $10.3090$ |
| 25th Percentile ($Q_1$) | $\$143,900.00$ | $11.8769$ |
| Median ($Q_2$) | $\$180,412.50$ | $12.1030$ |
| 75th Percentile ($Q_3$) | $\$222,000.00$ | $12.3104$ |
| Maximum | $\$600,000.00$ | $13.3047$ |
| Interquartile Range (IQR) | $\$78,100.00$ | $0.4335$ |
| Skewness | $+0.9436$ | $-0.5027$ |
| Kurtosis | $+2.5080$ | $+0.9238$ |

### 4.3 Target Selection Justification
While the log-transformed target reduces right-tail skewness (from $+0.94$ to $-0.50$), comparative validation experiments indicated that direct optimization on raw salary midpoint achieves superior RMSE without introducing prediction bias in back-transformed dollar space ($\Delta \text{MAE} < \$350$). Direct raw dollar prediction was therefore retained as the primary target for maximum interpretability in labor market economics, with log models serving as consistency checks.

---

## 5. Leakage Prevention Protocol

Data leakage prevention represents the central methodological safeguard of Phase 5. The implemented pipeline contains no identified target or archetype leakage: learned transformations are fitted within training folds, and the holdout test set is isolated until final evaluation:
1. **Target Quarantine:** Columns `salary_min`, `salary_max`, `salary_band`, `log_salary`, and `job_id` were completely removed from all predictor sets.
2. **Exploratory Archetype Isolation:** The cluster labels in `job_archetype_assignments.parquet` (computed in Phase 4 on the full skill-bearing population) were **strictly barred** from the supervised training set.
3. **Fold-Safe Cross-Validation Architecture:**
   - In every cross-validation fold, preprocessing (categorical one-hot encoding, imputation, scaling), PCA decomposition, and K-Means clustering were fitted **strictly on the $80\%$ training fold**.
   - Validation fold instances were projected onto the fold-specific PCA basis and assigned to archetypes using **training centroid distance minimization**.
4. **Holdout Test Set Isolation:** An 80/20 train/test split was established with `random_state = 42`. The holdout test set ($N_{\text{test}} = 6,808$) remained locked and uninspected until final model verification.

---

## 6. Comparative Feature Sets

To evaluate the predictive utility of unsupervised archetype discovery, three feature representations were constructed:

### Feature Set A — Original Supervised Features (123 Columns)
- **Role Metadata (41 features):**
  - Seniority Tier (5 one-hot columns: Intern, Junior, Mid, Senior, Lead).
  - Role Family (18 one-hot columns: Software Engineer, Data Scientist, ML Engineer, DevOps, etc.).
  - Geographic Location (16 one-hot columns: San Francisco, New York, Seattle, Boston, etc.).
  - Work Arrangement (`is_remote`, 1 boolean column).
  - Skill Breadth (`num_skills`, 1 integer column).
- **Explicit Skills (82 features):** Standardized binary indicators for all Taxonomy D skills.

### Feature Set B — Skill PCA Features (56 Columns)
- **Role Metadata (41 features):** Identical to Feature Set A.
- **Skill PCA Components (15 continuous features):** The first 15 principal components extracted from the fold-specific centered covariance matrix of the 82 binary skills, capturing $\sim 56\%$ of skill variance.

### Feature Set C — Original Features + Fold-Safe Archetypes (130 Columns)
- **Feature Set A (123 features):** All metadata and explicit binary skill indicators.
- **Archetype Indicators (7 one-hot features):** Membership indicators for the $k = 7$ skill archetypes discovered via fold-safe K-Means clustering on the fold-specific PCA subspace.

---

## 7. Modeling Methodology & Candidate Algorithms

Six distinct modeling approaches were evaluated:
1. **Naive Baselines:** `DummyRegressor(strategy='median')` and `DummyRegressor(strategy='mean')` to quantify naive baseline performance.
2. **Regularized Linear Regression:** `Ridge(alpha=10.0)` with standardized continuous inputs.
3. **Bagged Ensembles:** `RandomForestRegressor` (100 estimators, max depth 15, min samples leaf 5).
4. **Gradient Boosted Trees:** `GradientBoostingRegressor` (100 estimators, max depth 5, learning rate 0.1).
5. **Extreme Gradient Boosting:** `XGBRegressor` (Hist-based gradient boosting, depth 5/6, learning rate 0.05/0.10, subsample 0.8).
6. **Multi-Layer Perceptron:** `MLPRegressor` (Hidden layers (128, 64), early stopping, Adam optimizer).

---

## 8. 5-Fold Cross-Validation Benchmark

Cross-validation was conducted across the 27,228 training observations using 5 stratified-style random folds.

### 5-Fold CV Performance Across Models & Feature Sets
| Feature Set | Model | CV MAE ($) | CV RMSE ($) | CV $R^2$ | Fit Time (s) |
|---|---|---:|---:|---:|---:|
| **Baseline** | Dummy (Median) | $\$49,502 \pm \$398$ | $\$65,733 \pm \$512$ | $-0.0089 \pm 0.0018$ | 0.05 |
| **Set A (Original)** | Ridge | $\$38,544 \pm \$410$ | $\$52,853 \pm \$530$ | $0.3477 \pm 0.0099$ | 0.5 |
| **Set A (Original)** | Random Forest | $\$37,202 \pm \$241$ | $\$51,158 \pm \$627$ | $0.3888 \pm 0.0134$ | 26.0 |
| **Set A (Original)** | Gradient Boosting | $\$37,010 \pm \$180$ | $\$51,001 \pm \$492$ | $0.3926 \pm 0.0066$ | 94.1 |
| **Set A (Original)** | **XGBoost (Default)** | **$\$36,944 \pm \$199$** | **$\$50,865 \pm \$449$** | **$0.3959 \pm 0.0069$** | 4.3 |
| **Set A (Original)** | MLP Regressor | $\$36,943 \pm \$184$ | $\$50,751 \pm \$345$ | $0.3986 \pm 0.0071$ | 57.0 |
| **Set B (PCA 15)** | Ridge | $\$39,027 \pm \$406$ | $\$53,540 \pm \$520$ | $0.3306 \pm 0.0106$ | 0.9 |
| **Set B (PCA 15)** | Random Forest | $\$36,683 \pm \$89$ | $\$50,776 \pm \$487$ | $0.3980 \pm 0.0076$ | 44.7 |
| **Set B (PCA 15)** | Gradient Boosting | $\$37,222 \pm \$260$ | $\$51,265 \pm \$458$ | $0.3863 \pm 0.0087$ | 155.4 |
| **Set B (PCA 15)** | XGBoost | $\$37,089 \pm \$212$ | $\$51,086 \pm \$446$ | $0.3906 \pm 0.0055$ | 2.1 |
| **Set B (PCA 15)** | MLP Regressor | $\$37,698 \pm \$216$ | $\$51,757 \pm \$385$ | $0.3744 \pm 0.0104$ | 44.2 |
| **Set C (Archetype)** | Ridge | $\$38,469 \pm \$441$ | $\$52,755 \pm \$537$ | $0.3501 \pm 0.0105$ | 4.3 |
| **Set C (Archetype)** | Random Forest | $\$37,180 \pm \$212$ | $\$51,159 \pm \$538$ | $0.3888 \pm 0.0114$ | 32.5 |
| **Set C (Archetype)** | Gradient Boosting | $\$36,982 \pm \$165$ | $\$50,991 \pm \$399$ | $0.3929 \pm 0.0067$ | 114.3 |
| **Set C (Archetype)** | XGBoost | $\$36,947 \pm \$204$ | $\$50,900 \pm \$385$ | $0.3950 \pm 0.0075$ | 3.9 |
| **Set C (Archetype)** | MLP Regressor | $\$37,062 \pm \$267$ | $\$50,787 \pm \$425$ | $0.3977 \pm 0.0071$ | 59.9 |

---

## 9. Hyperparameter Tuning

XGBoost demonstrated the optimal balance between prediction accuracy ($\text{MAE} \approx \$36.9\text{k}$), stability, and training efficiency ($4.3$ seconds). A controlled grid search was conducted on the training set:

| Max Depth | Learning Rate | N Estimators | Mean CV MAE ($) | Mean CV RMSE ($) | Mean CV $R^2$ |
|---|---|---|---:|---:|---:|
| 4 | 0.05 | 150 | $\$37,192 \pm \$195$ | $\$51,192 \pm \$471$ | $0.3881$ |
| 5 | 0.10 | 100 | $\$36,944 \pm \$199$ | $\$50,865 \pm \$449$ | $0.3959$ |
| 6 | 0.05 | 150 | $\$36,547 \pm \$188$ | $\$50,381 \pm \$432$ | $0.4074$ |
| **6** | **0.10** | **150** | **$\$36,072 \pm \$185$** | **$\$49,886 \pm \$412$** | **$0.4192$** |

**Selected Configuration:** `max_depth = 6`, `learning_rate = 0.10`, `n_estimators = 150`. Hyperparameter tuning reduced CV MAE by an additional **$\$872$** and improved $R^2$ by **$+0.0233$**.

---

## 10. Model Comparison & Archetype Value Proposition

The comparative experiment addresses a central thesis: **Does incorporating skill-based archetype information improve salary prediction?**

### Empirical Findings:
1. **Feature Set A vs. Feature Set C in CV:**
   - Default XGBoost CV MAE: Set A = $\$36,944$ vs. Set C = $\$36,947$ ($\Delta = +\$3$).
   - Ridge CV MAE: Set A = $\$38,544$ vs. Set C = $\$38,469$ ($\Delta = -\$75$).
   - Gradient Boosting CV MAE: Set A = $\$37,010$ vs. Set C = $\$36,982$ ($\Delta = -\$28$).
2. **Holdout Test Comparison:**
   - Tuned XGBoost on Feature Set A: $\text{MAE} = \$36,380.64$, $R^2 = 0.4233$.
   - Tuned XGBoost on Feature Set C: $\text{MAE} = \$36,424.84$, $R^2 = 0.4255$.
   - Observed Difference: **$\Delta \text{MAE} = +\$44.20$** (relative difference $\approx 0.12\%$).

### Scientific Verdict:
**Feature Set C provides no practically meaningful improvement over Feature Set A.**
> The discovered skill archetypes do not materially improve supervised salary prediction beyond explicit skill indicators and role metadata. Because high-resolution binary skill matrices already supply the principal predictive signal available from the observed skill and job metadata to gradient boosted decision trees, clustering assignments compress rather than enrich the signal. Archetypes serve as invaluable descriptive and taxonomic frameworks for market navigation, but they provide minimal incremental predictive lift in supervised regression.

---

## 11. Final Holdout Test Evaluation ($N_{\text{test}} = 6,808$)

The final candidate models were fitted on the complete $80\%$ training partition ($N_{\text{train}} = 27,228$) and evaluated once on the frozen holdout test set:

| Model | Feature Set | Train MAE ($) | Test MAE ($) | Test RMSE ($) | Test $R^2$ | Test MAPE | MAE Improvement over Dummy |
|---|---|---:|---:|---:|---:|---:|---:|
| Dummy (Median) | Set A | $\$49,497$ | $\$50,806$ | $\$67,660$ | $-0.0117$ | $31.46\%$ | — |
| Ridge | Set A | $\$38,357$ | $\$39,147$ | $\$54,123$ | $0.3526$ | $23.65\%$ | $22.9\%$ |
| Random Forest | Set A | $\$34,306$ | $\$37,699$ | $\$52,226$ | $0.3972$ | $22.60\%$ | $25.8\%$ |
| Gradient Boosting | Set A | $\$35,784$ | $\$37,446$ | $\$52,119$ | $0.3997$ | $22.54\%$ | $26.3\%$ |
| XGBoost (Default) | Set A | $\$35,765$ | $\$37,460$ | $\$52,143$ | $0.3991$ | $22.55\%$ | $26.3\%$ |
| **XGBoost (Tuned)** | **Set A** | **$\$33,525$** | **$\$36,381$** | **$\$51,082$** | **$0.4233$** | **$21.71\%$** | **$28.4\%$** |
| XGBoost (Archetype) | Set C | $\$33,465$ | $\$36,425$ | $\$50,987$ | $0.4255$ | $21.77\%$ | $28.3\%$ |

The tuned XGBoost regressor achieves an MAE of **$\$36,381$**, an RMSE of **$\$51,082$**, and an $R^2$ of **$0.4233$**, establishing a **$\$14,425$ error reduction ($28.4\%$ relative improvement)** over the naive median baseline. However, an MAE of approximately $\$36\text{k}$ means that individual salary predictions can still deviate substantially from the observed salary midpoint.

---

## 12. Bias-Variance & Generalization Diagnostics

| Model | Train MAE ($) | Test MAE ($) | Generalization Gap MAE ($) | Train $R^2$ | Test $R^2$ | Generalization Gap $R^2$ |
|---|---:|---:|---:|---:|---:|---:|
| Ridge | $\$38,357$ | $\$39,147$ | $\$790$ | $0.3536$ | $0.3526$ | $0.0010$ |
| Random Forest | $\$34,306$ | $\$37,699$ | $\$3,393$ | $0.4775$ | $0.3972$ | $0.0803$ |
| Gradient Boosting | $\$35,784$ | $\$37,446$ | $\$1,662$ | $0.4317$ | $0.3997$ | $0.0320$ |
| **XGBoost (Tuned)** | **$\$33,525$** | **$\$36,381$** | **$\$2,855$** | **$0.4993$** | **$0.4233$** | **$0.0760$** |

### Diagnostic Findings:
- **Generalization Ratio:** The test MAE exceeds training MAE by $7.8\%$ ($\$2,855$). The relatively small train-to-test error gap indicates controlled generalization error and no evidence of severe overfitting.
- **Learning Curve Behavior (`07_learning_curve.png`):** As training sample size increases from $5,400$ to $27,228$ observations, validation $R^2$ steadily ascends from $0.37$ to $0.42$, while training $R^2$ descends toward $0.50$, indicating stable learning dynamics.
- **Validation Curve Behavior (`09_validation_curve_xgboost.png`):** Testing tree depth across $[3, 7]$ confirms that validation MAE minimizes at `max_depth = 6`. Depths exceeding 7 induce mild overfitting.

---

## 13. Residual Analysis

Evaluation of holdout test predictions reveals:
1. **Predicted vs. Actual (`10_predicted_vs_actual.png`):** Predictions cluster along the $45^\circ$ reference line between $\$100,000$ and $\$300,000$, where posting density is highest.
2. **Residual vs. Predicted (`11_residual_vs_predicted.png`):**
   - Constant residual variance is largely maintained between $\$120\text{k}$ and $\$250\text{k}$.
   - Scarcity of extreme compensation observations above approximately $\$400\text{k}$ produces modest underprediction in the upper tail.
3. **Residual Distribution (`12_residual_distribution.png`):** Residuals are approximately normally distributed around a mean bias of $-\$374$, with mild leptokurtosis. The median absolute error is $\$26,384$, indicating that over half of predictions fall within $\$26.4\text{k}$ of ground truth.

---

## 14. Feature Importance & Permutation Analysis

### Top 15 Predictors by Test Permutation Importance (`phase5_permutation_importance.csv`)
| Rank | Feature Name | Category | Permutation MAE Increase ($) | Standard Deviation ($) |
|---|---|---|---:|---:|
| 1 | `seniority_Lead / Principal / Executive` | Metadata (Seniority) | **$+\$4,374** | $\$128$ |
| 2 | `role_family_Technical Product & PM` | Metadata (Role) | **$+\$2,641** | $\$95$ |
| 3 | `role_family_Data / BI Analyst` | Metadata (Role) | **$+\$2,382** | $\$84$ |
| 4 | `seniority_Senior` | Metadata (Seniority) | **$+\$1,735** | $\$68$ |
| 5 | `city_clean_San Francisco` | Metadata (Location) | **$+\$1,228** | $\$54$ |
| 6 | `skill_machine_learning` | Technical Skill | **$+\$812** | $\$42$ |
| 7 | `skill_pytorch` | Technical Skill | **$+\$645$** | $\$38$ |
| 8 | `city_clean_New York` | Metadata (Location) | **$+\$624$** | $\$35$ |
| 9 | `role_family_Engineering Management` | Metadata (Role) | **$+\$598$** | $\$31$ |
| 10 | `skill_aws` | Technical Skill | **$+\$582$** | $\$29$ |
| 11 | `skill_deep_learning` | Technical Skill | **$+\$548$** | $\$27$ |
| 12 | `num_skills` | Skill Breadth | **$+\$512$** | $\$24$ |
| 13 | `skill_kubernetes` | Technical Skill | **$+\$486$** | $\$22$ |
| 14 | `skill_python` | Technical Skill | **$+\$465$** | $\$26$ |
| 15 | `city_clean_Seattle` | Metadata (Location) | **$+\$441$** | $\$19$ |

Seniority tier, role family, and metropolitan geography dominate global feature importance, reflecting broad structural compensation drivers. Among technical skills, machine learning, cloud infrastructure, and distributed systems exert the strongest independent predictive pull.

---

## 15. RQ1 — Skill-Salary Association Analysis

Triangulating Phase 3 exploratory findings, tree split gains, test permutation importance, and standardized Ridge coefficients (`phase5_rq1_skill_associations.csv`) establishes the empirical skill associations:
- **Tree Split Gain:** Quantifies the relative contribution of each feature to variance reduction across decision trees.
- **Permutation Importance:** Measures the degradation in holdout test MAE when feature values are permuted.
- **Standardized Ridge Coefficients:** Captures conditional linear association under $L_2$ regularization.
- **Descriptive Profile Differences:** Empirical median differences observed across postings.

### Top 15 Technical Skills Associated with Salary
| Skill Name | Tree Gain Importance | Permutation MAE Impact ($) | Ridge Standardized Coef ($) | Composite Rank | Market Domain |
|---|---:|---:|---:|---:|---|
| **machine_learning** | $0.0384$ | $+\$812$ | $+\$5,124$ | **1.0** | AI & Data Science |
| **pytorch** | $0.0291$ | $+\$645$ | $+\$6,380$ | **2.0** | Deep Learning / AI |
| **deep_learning** | $0.0245$ | $+\$548$ | $+\$5,892$ | **3.0** | Advanced AI |
| **aws** | $0.0212$ | $+\$582$ | $+\$3,845$ | **4.0** | Cloud & Infrastructure |
| **python** | $0.0198$ | $+\$465$ | $+\$2,914$ | **5.0** | Core Programming |
| **kubernetes** | $0.0185$ | $+\$486$ | $+\$4,120$ | **6.0** | DevOps & Containers |
| **sql** | $0.0164$ | $+\$392$ | $-\$1,845$ | **7.0** | Data Management |
| **golang** | $0.0152$ | $+\$368$ | $+\$4,890$ | **8.0** | Systems Programming |
| **c++** | $0.0148$ | $+\$354$ | $+\$4,310$ | **9.0** | High-Performance Systems |
| **databricks** | $0.0135$ | $+\$312$ | $+\$3,980$ | **10.0** | Modern Data Platform |
| **spark** | $0.0128$ | $+\$298$ | $+\$3,410$ | **11.0** | Big Data Processing |
| **terraform** | $0.0119$ | $+\$285$ | $+\$3,250$ | **12.0** | Infrastructure as Code |
| **docker** | $0.0112$ | $+\$264$ | $+\$1,980$ | **13.0** | Containerization |
| **snowflake** | $0.0108$ | $+\$248$ | $+\$3,120$ | **14.0** | Cloud Data Warehouse |
| **java** | $0.0102$ | $+\$235$ | $+\$1,450$ | **15.0** | Enterprise Backend |

### Observed Salary Differences Between Selected Skill Profiles:
- **AI/ML Profile (`python` + `machine_learning` + `pytorch`):** Postings specifying this deep learning profile exhibit an observed median salary of **$\$192,500$** vs. $\$165,000$ for postings specifying Python without specialized ML skills.
- **Cloud Infrastructure Profile (`aws` + `kubernetes` + `terraform`):** Associated with an observed median salary of **$\$198,000$**.
- **Modern Data Profile (`python` + `sql` + `spark` + `databricks`):** Displays an observed median of **$\$185,000$** vs. $\$135,000$ for traditional SQL analyst postings.

*Methodological Caveat:* These rankings represent statistical associations within technology job postings. They do not demonstrate that acquiring a single skill will mechanically raise an individual's salary; compensation is jointly determined by seniority tier, geographic market, organization size, candidate experience, and unobserved negotiation dynamics.

---

## 16. RQ3 — Archetype-Level Error Analysis

Holdout test set observations were mapped into the seven skill-based archetypes using training K-Means centroids:

### Error Breakdown Across Archetypes ($N_{\text{test}} = 6,808$)
| Archetype ID | Archetype Name | Test $N$ | Median Salary ($) | MAE ($) | RMSE ($) | Median AE ($) | Mean Error ($) | Relative MAE | Archetype $R^2$ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | **AI_ML (AI / Machine Learning)** | $490$ | $\$187,250$ | **$\$27,002$** | **$\$36,135$** | $\$21,244$ | $+\$1,797$ | **$14.42\%$** | $0.4651$ |
| 4 | **DATA_BI (Data & Analytics)** | $831$ | $\$170,000$ | **$\$31,985$** | **$\$43,325$** | $\$23,319$ | $+\$793$ | **$18.81\%$** | $0.4516$ |
| 1 | **DEVOPS_PLAT (DevOps & Cloud)** | $441$ | $\$195,000$ | **$\$32,745$** | **$\$44,106$** | $\$24,377$ | $+\$1,575$ | **$16.79\%$** | $0.3799$ |
| 6 | **SYS_ENG (Systems & Backend)** | $420$ | $\$190,000$ | **$\$34,651$** | **$\$47,761$** | $\$27,488$ | $-\$2,876$ | **$18.24\%$** | $0.4797$ |
| 2 | **WEB_FRONT (Frontend & Web)** | $863$ | $\$165,650$ | **$\$35,096$** | **$\$49,908$** | $\$26,042$ | $+\$997$ | **$21.19\%$** | $0.3849$ |
| 0 | **FOUND_TECH (Foundational & Broad)** | $2,950$ | $\$170,000$ | **$\$37,664$** | **$\$51,966$** | $\$28,027$ | $-\$1,166$ | **$22.16\%$** | $0.3930$ |
| 3 | **CLOUD_ARCH (Multi-Cloud)** | $813$ | $\$220,000$ | **$\$46,098$** | **$\$66,848$** | $\$33,333$ | $-\$4,448$ | **$20.95\%$** | $0.2818$ |

### Statistical Testing:
A non-parametric Kruskal-Wallis test on absolute prediction errors yields:
$$H = 88.10, \quad p = 7.53 \times 10^{-17} \quad (p < 0.001)$$
**Interpretation:** Prediction-error distributions differ significantly across the identified archetypes. The Kruskal-Wallis test confirms that error distributions vary across groups, but the test statistic alone does not explain the underlying structural mechanisms driving these differences:
1. **Lowest Absolute & Relative Error:** `AI_ML` achieves both the lowest absolute MAE ($\$27,002$) and lowest relative error ($14.42\%$). Highly specialized AI/ML job requirements constrain market compensation bands, yielding more predictable pricing.
2. **Highest Absolute Error:** `CLOUD_ARCH` displays the highest absolute MAE ($\$46,098$). However, its median salary is $\$220,000$ (the highest across all archetypes), and its salary variance is wider ($\sigma > \$85\text{k}$). In **relative error terms**, `CLOUD_ARCH` ($20.95\%$) is comparable to `WEB_FRONT` ($21.19\%$) and lower than `FOUND_TECH` ($22.16\%$).
3. **Broad / Generalist Roles:** `FOUND_TECH` exhibits the highest relative error ($22.16\%$). The elevated relative error is consistent with the heterogeneous and broad composition of this archetype, which spans a wide range of job tiers and compensation bands.

---

## 17. Limitations

1. **Unobserved Compensation Components:** Postings omit equity grants, signing bonuses, and annual performance bonuses, which constitute a significant share of total compensation in senior tech roles.
2. **Text Parsing Resolution:** Keyword extraction confirms skill presence but does not measure candidate proficiency or required years of experience.
3. **Substantial Unexplained Variance:** An $R^2$ of $\sim 0.42$ and MAE of $\sim \$36\text{k}$ mean that individual salary predictions can still deviate substantially from actual ground truth. Macroeconomic factors, company prestige, funding stage, and negotiation dynamics remain unobserved.
4. **Upper-Tail Compression:** Scarcity of extreme compensation observations above approximately $\$400\text{k}$ produces modest underprediction in the upper tail.
5. **Salary Disclosure Bias:** Postings with transparent salary ranges may differ systematically from postings without disclosed compensation.

---

## 18. Conclusions & Summary

1. **Predictive Feasibility:** Supervised gradient boosting predicts tech salaries with a test MAE of **$\$36,381$** ($21.7\%$ typical percentage error) and an $R^2$ of **$0.4233$**, outperforming naive median baselines by **$28.4\%$**.
2. **Archetype Incremental Value:** Incorporating unsupervised archetypes into supervised regression yields virtually identical accuracy ($+\$44.20$ test MAE difference), demonstrating that **Feature Set C provides no practically meaningful improvement over Feature Set A**. Archetypes provide powerful organizational clarity for labor market navigation, but explicit skills preserve the principal predictive signal captured by the supervised models.
3. **RQ1 Resolution:** Premium salaries are most strongly associated with deep learning (`pytorch`, `deep_learning`), modern AI (`machine_learning`), cloud containerization (`kubernetes`, `aws`), and systems languages (`golang`, `c++`), conditioned heavily on seniority and metropolitan market.
4. **RQ3 Resolution:** Prediction-error distributions differ significantly across the identified archetypes ($p < 0.001$). Elevated absolute errors in multi-cloud architecture are primarily scale-driven, whereas generalist technical roles exhibit the highest relative dispersion consistent with role heterogeneity.
