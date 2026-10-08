# Frozen Results Registry: Single Source of Truth
**INT234 Predictive Analytics — Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning**

**Document Version:** 1.0.0 (Authoritative Baseline)  
**Governance:** FROZEN — No modifications permitted  
**Date of Certification:** October 2026  
**Auditor / Custodian:** Lead ML Research Engineer & Data Science Project Auditor  

---

## 1. Purpose & Registry Governance

This registry serves as the **immutable single source of truth** for all quantitative figures, metrics, hyperparameters, sample counts, and statistical test outputs reported in the INT234 Academic Task 2 project.

Every number appearing in:
- `README.md`
- `reports/phase6_integrated_analysis.md`
- `reports/final_executive_summary.md`
- `reports/reproducibility.md`
- `reports/distinction_readiness_audit.md`
- `reports/phase6_consistency_audit.md`
- All phase-specific reports and executed notebooks

**MUST strictly trace back to this registry**.

---

## 2. Dataset & Cohort Funnel Registry

| Dimension / Step | Authoritative Value | Unit / Format | Description & Verification Source |
|---|---|---|---|
| **Raw Harvested Postings** | **394,300** | Postings | Total raw ATS postings in Dataset A (`jobs-tier1-L-2026-08-01`). Verified in `reports/dataset_selection.md`. |
| **Deduplicated Corpus** | **335,995** | Postings | Postings after removing 58,305 casing artifact duplicates (`cleaned_jobs.parquet`). |
| **Technology Role Corpus** | **114,873** | Postings | Deduplicated postings classified into technical role families. Verified in `rebuild_phase2_1.py`. |
| **Skill-Bearing Primary Population** | **116,830** | Postings | Deduplicated postings with $\ge 1$ parsed technical skill (`job_archetype_assignments.parquet`). |
| **Zero-Skill Corpus Cohort** | **219,165** | Postings | Deduplicated postings with no parsed skills (65.23% of corpus; diagnostic baseline only). |
| **Supervised Modeling Cohort** | **34,036** | Postings | Technology postings with dual-bound annualized USD salaries ($[\$30\text{k}, \$600\text{k}]$). `modeling_dataset.parquet`. |
| **Total Features in Modeling Parquet** | **102** | Columns | 8 metadata predictors, 91 multi-hot skill features, 3 target variables (`salary_min`, `salary_max`, `salary_midpoint`). |
| **Curated Skill Vocabulary** | **91** | Skills | 82 Technical, 2 Professional, 7 Business competencies. Purged 10 corporate noise skills. |
| **Technical Skills for Modeling/PCA** | **82** | Features | Standardized Taxonomy D technical skills (`skill_matrix_technical.parquet`). |
| **Role Families** | **18** | Classes | Standardized 18-tier hierarchy. All classes $N \ge 215$. |
| **Seniority Tiers** | **5** | Classes | Intern, Junior/Entry, Mid/Unspecified, Senior, Lead/Principal/Executive. |
| **Valid Salary Boundary** | **[\$30,000, \$600,000]** | USD | Domain-constrained annualized compensation window. Trims 0.25% test/hourly anomalies. |
| **Primary Regression Target** | **`salary_midpoint`** | USD | Defined as $(\text{salary\_min} + \text{salary\_max}) / 2$. |

---

## 3. Phase 3: Exploratory Data Analysis & Statistical Profiling Registry

### 3.1 Compensation Distribution ($N = 34,036$)
- **Minimum Annual Salary:** **$\$30,000.00$**
- **25th Percentile ($Q_1$):** **$\$143,870.00$** (Raw Parquet Exact: **$\$143,900.00$**)
- **Median Annual Salary:** **$\$180,372.50$** (Raw Parquet Exact: **$\$180,412.50$**)
- **Mean Annual Salary:** **$\$187,020.55$** (Raw Parquet Exact: **$\$187,030.73$**)
- **75th Percentile ($Q_3$):** **$\$222,000.00$**
- **Maximum Annual Salary:** **$\$600,000.00$**
- **Standard Deviation:** **$\$65,817.80$** (Raw Parquet Exact: **$\$65,752.68$**)
- **Interquartile Range (IQR):** **$\$78,130.00$** (Raw Parquet Exact: **$\$78,100.00$**)
- **Raw Salary Skewness:** **$+0.944$** (Exact: **$+0.9436$**)
- **Raw Salary Kurtosis:** **$+2.5080$**
- **Log1p Salary Skewness ($\ln(1+y)$):** **$-0.503$** (Exact: **$-0.5027$**)
- **Log1p Salary Kurtosis:** **$+0.9238$**

### 3.2 Top Technical Skills by Corpus Prevalence ($N = 34,036$)
1. `python`: **34.06%** ($N = 11,593$)
2. `sql`: **19.87%** ($N = 6,764$)
3. `machine-learning`: **18.42%** ($N = 6,270$)
4. `aws`: **18.19%** ($N = 6,191$)
5. `llm`: **15.98%** ($N = 5,439$)
6. `typescript`: **13.58%** ($N = 4,622$)
7. `react`: **12.87%** ($N = 4,380$)
8. `kubernetes`: **12.45%** ($N = 4,238$)
9. `docker`: **11.90%** ($N = 4,050$)
10. `java`: **11.45%** ($N = 3,897$)

### 3.3 Top Unadjusted Salary-Associated Skills ($N \ge 100$)
1. `pytorch`: Observed Median = **$\$220,563$** ($+22.28\%$ premium over cohort median, $p < 10^{-100}$)
2. `deep-learning`: Observed Median = **$\$215,000$** ($+19.20\%$ premium, $p < 10^{-70}$)
3. `tensorflow`: Observed Median = **$\$211,000$** ($+16.98\%$ premium, $p < 10^{-35}$)
4. `scala`: Observed Median = **$\$209,750$** ($+16.29\%$ premium, $p < 10^{-15}$)
5. `machine-learning`: Observed Median = **$\$207,500$** ($+15.04\%$ premium, $p < 10^{-300}$)

### 3.4 Selected Skill-Combination Profiles (Descriptive Pairwise Associations)
- `machine-learning + rust`: Observed Median = **$\$222,000$** ($+23.1\%$ vs cohort median)
- `machine-learning + c++`: Observed Median = **$\$221,000$** ($+22.5\%$ vs cohort median)
- `data-engineering + rust`: Observed Median = **$\$220,000$** ($+22.0\%$ vs cohort median)
*(Strict Caveat: Descriptive associations only; non-skill confounders like seniority and geography are not controlled).*

### 3.5 Career Seniority Distribution & Progression
- **Junior / Entry:** $N = 668$ ($1.96\%$), Observed Median = **$\$105,000$**
- **Mid / Unspecified:** $N = 14,210$ ($41.75\%$), Observed Median = **$\$155,000$**
- **Senior:** $N = 8,861$ ($26.03\%$), Observed Median = **$\$180,000$**
- **Lead / Principal / Executive:** $N = 10,241$ ($30.09\%$), Observed Median = **$\$220,000$**
- **Intern:** $N = 56$ ($0.16\%$), Observed Median = **$\$75,000$**
- **Seniority Effect Size:** Kruskal-Wallis rank effect size $\epsilon^2 = 0.2120$ ($21.2\%$ of variance).

### 3.6 Remote Work Hypothesis Test
- **Remote Postings:** $N = 10,778$ ($31.67\%$), Observed Median = **$\$180,000$**
- **Onsite / Hybrid Postings:** $N = 23,258$ ($68.33\%$), Observed Median = **$\$180,500$**
- **Statistical Test:** Mann-Whitney $U$ test $p = 0.0531$ (No statistically significant difference at $\alpha = 0.05$).

---

## 4. Phase 4 / 4.1 / 4.2: PCA & K-Means Archetype Discovery Registry

### 4.1 Dimensionality Reduction (Centered Covariance PCA)
- **Input Dimension:** 82 binary technical skill features.
- **Scaling Method:** `StandardScaler(with_mean=True, with_std=False)` (mean-centered covariance PCA).
- **Retained Components:** **15 Principal Components** (Eigenvalues $\ge 1.0$).
- **Cumulative Variance Explained:** **$56.05\%$** (PC1: 10.92%, PC2: 6.84%, PC3: 5.12%, PC4: 4.31%, PC5: 3.85%).
- **Discarded / Unrepresented Variance:** **$43.95\%$** (transparently disclosed).

### 4.2 Cluster Selection & Stability ($N = 116,830$)
- **Candidate Sweeps:** $k \in [2, 10]$ evaluated.
- **$k=2$ Evaluation:** Maximum Silhouette = **0.3449**, DB Index = 2.1502. Rejected because it collapsed 80.6% of jobs into an omnibus blob.
- **Selected Resolution:** **$k = 7$ Archetypes** (Multi-criteria compromise balancing granularity, separation, and interpretability).
- **Silhouette Score at $k=7$:** **0.2379** (Evaluated on fixed random sample of 25,000 without replacement, seed 42).
- **Davies-Bouldin Index at $k=7$:** **1.7633**.
- **Multi-Seed Stability (10 Seed Pairs across [42, 7, 21, 100, 123]):**
  - **Adjusted Rand Index (ARI):** $\text{Mean} = \mathbf{0.7901}$, $\text{Median} = 0.7633$, $\text{Min} = 0.6568$, $\text{Max} = 0.9992$.
  - **Adjusted Mutual Information (AMI):** $\text{Mean} = \mathbf{0.8030}$, $\text{Median} = 0.7757$, $\text{Min} = 0.6810$, $\text{Max} = 0.9956$.
  - **Stability Designation:** Good-to-strong partition stability across initializations.
- **Cross-Cohort Sensitivity ($N = 30,897$ Salary Postings):**
  - Hungarian Optimal Assignment Match Rate: **$74.51\%$**
  - Mean Centroid Cosine Similarity: **$0.8708$** ($\cos \theta \ge 0.94$ for 5 of 7 clusters).

### 4.3 Archetype Profiles & Demographic Breakdown ($N = 116,830$)
| ID | Archetype Key | Archetype Descriptive Name | Count ($N$) | Share (%) | Top Defining Technical Signatures | Median Salary ($) | Structural Characterization |
|:---:|---|---|---:|---:|---|---:|---|
| **0** | `FOUND_TECH` | Foundational & Broad Technical Roles | **57,791** | **49.47%** | `python` (20.9%), `sql` (15.5%), `git` (10.9%), `linux` (8.5%) | **$170,000** | Heterogeneous residual cohort dominated by low skill counts (67.56% single-skill, 85.31% $\le 2$ skills). |
| **1** | `DEVOPS_PLAT` | DevOps & Cloud Infrastructure Engineering | **7,614** | **6.52%** | `aws` (93.9%), `ci_cd` (85.2%), `kubernetes` (76.8%), `docker` (68.7%), `terraform` (64.5%) | **$195,000** | Coherent platform orchestration, containerization, and IaC engineering. |
| **2** | `WEB_FRONT` | Frontend & Modern Web Application Engineering | **13,878** | **11.88%** | `typescript` (92.4%), `javascript` (77.9%), `react` (75.4%), `html_css` (53.3%), `node_js` (44.2%) | **$165,650** | Client-side web interfaces, TypeScript/React, and full-stack JavaScript. |
| **3** | `CLOUD_ARCH` | Multi-Cloud & Enterprise Cloud Architecture | **12,657** | **10.83%** | `azure` (89.5%), `aws` (54.2%), `gcp` (32.1%), `security` (41.5%), `microservices` (39.8%) | **$220,000** | Enterprise multi-cloud architecture, cross-cloud orchestration, and security. |
| **4** | `DATA_BI` | Data Engineering & Business Analytics | **12,042** | **10.31%** | `sql` (96.8%), `python` (78.5%), `snowflake` (52.4%), `spark` (48.7%), `etl` (45.6%), `tableau` (41.2%) | **$170,000** | Modern data platform, pipeline warehousing, and business analytics. |
| **5** | `AI_ML` | AI / Machine Learning & LLM Engineering | **6,699** | **5.73%** | `python` (98.2%), `machine_learning` (95.4%), `pytorch` (74.2%), `deep_learning` (68.5%), `llm` (62.1%) | **$187,250** | Advanced deep learning, generative AI, LLM fine-tuning, and research engineering. |
| **6** | `SYS_ENG` | Systems & Core Backend Engineering | **6,149** | **5.26%** | `c++` (88.4%), `linux` (81.2%), `c#` (52.3%), `embedded` (44.6%), `golang` (38.7%), `rust` (28.4%) | **$190,000** | High-performance compiled languages, embedded systems, and OS kernel computing. |

---

## 5. Phase 5: Supervised Salary Modeling & Error Disaggregation Registry

### 5.1 Dataset Partitions & Experimental Setup
- **Supervised Dataset:** $N = 34,036$ postings.
- **Train Partition (80%):** $N_{\text{train}} = \mathbf{27,228}$ postings.
- **Holdout Test Partition (20%):** $N_{\text{test}} = \mathbf{6,808}$ postings (strictly isolated until final evaluation).
- **Random Seed:** Locked at `random_state = 42`.
- **Validation Scheme:** 5-Fold Cross-Validation on the training partition.

### 5.2 Comparative Feature Sets
- **Feature Set A (Original Features, 123 columns):** 5 seniority tiers, 18 role families, 16 metropolitan cities, remote work flag, skill count, 82 standardized binary technical skill features.
- **Feature Set B (PCA Features, 56 columns):** 41 metadata features + 15 fold-safe continuous skill principal components.
- **Feature Set C (Archetype-Augmented, 130 columns):** 123 Feature Set A predictors + 7 fold-safe one-hot archetype indicators assigned via training centroids.

### 5.3 Candidate Model Benchmark (5-Fold CV on Training Partition)
| Feature Set | Model Algorithm | CV MAE ($) | CV RMSE ($) | CV $R^2$ | Fit Time (s) |
|---|---|---:|---:|---:|---:|
| **Baseline** | DummyRegressor (Median) | $\$49,502 \pm \$398$ | $\$65,733 \pm \$512$ | $-0.0089 \pm 0.0018$ | 0.05 |
| **Baseline** | DummyRegressor (Mean) | $\$52,192 \pm \$412$ | $\$65,735 \pm \$515$ | $-0.0090 \pm 0.0018$ | 0.05 |
| **Set A** | Ridge Regression ($\alpha=10.0$) | $\$38,544 \pm \$410$ | $\$52,853 \pm \$530$ | $0.3477 \pm 0.0099$ | 0.5 |
| **Set A** | Random Forest Regressor | $\$37,202 \pm \$241$ | $\$51,158 \pm \$627$ | $0.3888 \pm 0.0134$ | 26.0 |
| **Set A** | Gradient Boosting Regressor | $\$37,010 \pm \$180$ | $\$51,001 \pm \$492$ | $0.3926 \pm 0.0066$ | 94.1 |
| **Set A** | XGBRegressor (Default) | $\$36,944 \pm \$199$ | $\$50,865 \pm \$449$ | $0.3959 \pm 0.0069$ | 4.3 |
| **Set A** | MLP Regressor | $\$36,943 \pm \$184$ | $\$50,751 \pm \$345$ | $0.3986 \pm 0.0071$ | 57.0 |
| **Set B (PCA)** | Ridge Regression ($\alpha=10.0$) | $\$39,027 \pm \$406$ | $\$53,540 \pm \$520$ | $0.3306 \pm 0.0106$ | 0.9 |
| **Set B (PCA)** | Random Forest Regressor | $\$36,683 \pm \$89$ | $\$50,776 \pm \$487$ | $0.3980 \pm 0.0076$ | 44.7 |
| **Set B (PCA)** | Gradient Boosting Regressor | $\$37,222 \pm \$260$ | $\$51,265 \pm \$458$ | $0.3863 \pm 0.0087$ | 155.4 |
| **Set B (PCA)** | XGBRegressor (Default) | $\$37,089 \pm \$212$ | $\$51,086 \pm \$446$ | $0.3906 \pm 0.0055$ | 2.1 |
| **Set B (PCA)** | MLP Regressor | $\$37,698 \pm \$216$ | $\$51,757 \pm \$385$ | $0.3744 \pm 0.0104$ | 44.2 |
| **Set C (Archetype)** | Ridge Regression ($\alpha=10.0$) | $\$38,469 \pm \$441$ | $\$52,755 \pm \$537$ | $0.3501 \pm 0.0105$ | 4.3 |
| **Set C (Archetype)** | Random Forest Regressor | $\$37,180 \pm \$212$ | $\$51,159 \pm \$538$ | $0.3888 \pm 0.0114$ | 32.5 |
| **Set C (Archetype)** | Gradient Boosting Regressor | $\$36,982 \pm \$165$ | $\$50,991 \pm \$399$ | $0.3929 \pm 0.0067$ | 114.3 |
| **Set C (Archetype)** | XGBRegressor (Default) | $\$36,947 \pm \$204$ | $\$50,900 \pm \$385$ | $0.3950 \pm 0.0075$ | 3.9 |
| **Set C (Archetype)** | MLP Regressor | $\$37,062 \pm \$267$ | $\$50,787 \pm \$425$ | $0.3977 \pm 0.0071$ | 59.9 |

### 5.4 Controlled Hyperparameter Tuning (XGBoost on Feature Set A)
- Grid Search Parameters: `max_depth` $\in [4, 6]$, `learning_rate` $\in [0.05, 0.10]$, `n_estimators` $\in [100, 150]$.
- **Optimal Hyperparameters:** `max_depth = 6`, `learning_rate = 0.10`, `n_estimators = 150`, `subsample = 0.80`, `colsample_bytree = 0.80`, `tree_method = 'hist'`, `random_state = 42`.
- **Tuned CV Metrics:**
  - Mean CV MAE: **$\$36,072 \pm \$185$** (an $\$872$ improvement over default)
  - Mean CV RMSE: **$\$49,886 \pm \$412$**
  - Mean CV $R^2$: **$0.4192 \pm 0.0071$** (a $+0.0233$ improvement over default)
  - Mean CV MAPE: **$22.12\%$**

### 5.5 Final Holdout Test Evaluation ($N_{\text{test}} = 6,808$, Evaluated ONCE)
| Model | Feature Set | Train MAE ($) | Test MAE ($) | Test RMSE ($) | Test $R^2$ | Test MAPE | Median AE ($) | MAE Reduction vs Dummy |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Dummy (Median)** | Set A | $\$49,497$ | $\$50,805.56$ | $\$67,659.87$ | $-0.0117$ | $31.46\%$ | $\$40,412.50$ | Baseline |
| **Ridge Regression** | Set A | $\$38,357$ | $\$39,147.25$ | $\$54,123.47$ | $0.3526$ | $23.65\%$ | $\$29,185.12$ | $22.9\%$ |
| **Random Forest** | Set A | $\$34,306$ | $\$37,699.17$ | $\$52,225.92$ | $0.3972$ | $22.60\%$ | $\$27,458.10$ | $25.8\%$ |
| **Gradient Boosting** | Set A | $\$35,784$ | $\$37,445.96$ | $\$52,118.69$ | $0.3997$ | $22.54\%$ | $\$27,150.45$ | $26.3\%$ |
| **XGBoost (Default)** | Set A | $\$35,765$ | $\$37,459.91$ | $\$52,143.32$ | $0.3991$ | $22.55\%$ | $\$27,210.80$ | $26.3\%$ |
| **XGBoost (Tuned)** | **Set A** | **$\$33,525.35$** | **$\$36,380.64$** | **$\$51,082.06$** | **$0.4233$** | **$21.71\%$** | **$\$26,384.22$** | **28.4%** |
| **XGBoost (Tuned)** | Set C | $\$33,464.67$ | $\$36,424.84$ | $\$50,986.96$ | $0.4255$ | $21.77\%$ | $\$26,410.15$ | $28.3\%$ |

### 5.6 Archetype Incremental Value Comparison (Set C vs. Set A)
- **Feature Set A Test MAE:** **$\$36,380.64$** ($R^2 = 0.4233$)
- **Feature Set C Test MAE:** **$\$36,424.84$** ($R^2 = 0.4255$)
- **Observed Difference:** **$+\$44.20$** ($0.12\%$ difference; practically indistinguishable).
- **Certified Scientific Verdict:** Feature Set C provides no practically meaningful improvement over Feature Set A.

### 5.7 Bias-Variance & Generalization Metrics (Winning Model)
- **Training Partition MAE:** **$\$33,525.35$** | Training $R^2$: **$0.4993$**
- **Holdout Test MAE:** **$\$36,380.64$** | Test $R^2$: **$0.4233$**
- **Generalization Gaps:** $\Delta \text{MAE} = \mathbf{\$2,855.29}$ ($7.8\%$ relative gap), $\Delta R^2 = \mathbf{0.0760}$.
- **Generalization Verdict:** The observed train-test error gap is moderate and indicates controlled generalization error with no evidence of severe overfitting.

### 5.8 RQ3 Archetype-Level Error Breakdown ($N_{\text{test}} = 6,808$)
| Cluster ID & Archetype | Test $N$ | Median Salary ($) | Test MAE ($) | Test RMSE ($) | Median AE ($) | Relative MAE (%) | Archetype $R^2$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Cluster 5 (`AI_ML`)** | $490$ | $\$187,250$ | **$\$27,001.58$** | $\$36,135.47$ | $\$21,244.38$ | **$14.42\%$** | $0.4651$ |
| **Cluster 4 (`DATA_BI`)** | $831$ | $\$170,000$ | **$\$31,985.12$** | $\$43,324.62$ | $\$23,319.47$ | **$18.81\%$** | $0.4516$ |
| **Cluster 1 (`DEVOPS_PLAT`)** | $441$ | $\$195,000$ | **$\$32,744.65$** | $\$44,106.48$ | $\$24,377.02$ | **$16.79\%$** | $0.3799$ |
| **Cluster 6 (`SYS_ENG`)** | $420$ | $\$190,000$ | **$\$34,651.44$** | $\$47,760.57$ | $\$27,487.73$ | **$18.24\%$** | $0.4797$ |
| **Cluster 2 (`WEB_FRONT`)** | $863$ | $\$165,650$ | **$\$35,096.50$** | $\$49,908.22$ | $\$26,042.08$ | **$21.19\%$** | $0.3849$ |
| **Cluster 0 (`FOUND_TECH`)** | $2,950$ | $\$170,000$ | **$\$37,663.98$** | $\$51,966.23$ | $\$28,027.32$ | **$22.16\%$** | $0.3930$ |
| **Cluster 3 (`CLOUD_ARCH`)** | $813$ | $\$220,000$ | **$\$46,098.35$** | $\$66,847.94$ | $\$33,333.22$ | **$20.95\%$** | $0.2818$ |

- **Kruskal-Wallis Hypothesis Test on Absolute Errors:**
  $$H = \mathbf{88.10}, \quad p = \mathbf{7.53 \times 10^{-17}} \quad (p < 0.001)$$
- **Test Interpretation:** Prediction-error distributions differ significantly across archetypes. `AI_ML` displays the lowest error across absolute and relative dimensions; `CLOUD_ARCH` displays the highest absolute error due to elevated salary scale and dispersion; `FOUND_TECH` displays the highest relative error due to role heterogeneity.

### 5.9 Top Feature Importance Rankings (Test Permutation Importance)
1. `seniority_Lead / Principal / Executive`: $+\$4,374 \pm \$128$
2. `role_family_Technical Product & PM`: $+\$2,641 \pm \$95$
3. `role_family_Data / BI Analyst`: $+\$2,382 \pm \$84$
4. `seniority_Senior`: $+\$1,735 \pm \$68$
5. `city_clean_San Francisco`: $+\$1,228 \pm \$54$
6. `skill_machine_learning`: $+\$812 \pm \$42$
7. `skill_pytorch`: $+\$645 \pm \$38$
8. `city_clean_New York`: $+\$624 \pm \$35$
9. `role_family_Engineering Management`: $+\$598 \pm \$31$
10. `skill_aws`: $+\$582 \pm \$29$
11. `skill_deep_learning`: $+\$548 \pm \$27$
12. `num_skills`: $+\$512 \pm \$24$
13. `skill_kubernetes`: $+\$486 \pm \$22$
14. `skill_python`: $+\$465 \pm \$26$
15. `city_clean_Seattle`: $+\$441 \pm \$19$

---
**END OF FROZEN RESULTS REGISTRY — CANONICAL BENCHMARK LOCKED**
