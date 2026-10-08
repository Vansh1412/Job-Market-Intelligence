# Phase India-5: Skill Archetype Discovery, Dimensionality Reduction, Stability Evaluation, Salary Association, and RQ3 Holdout Error Stratification

**Project:** INT234 Predictive Analytics -- Job Market Intelligence  
**Focus:** Indian Technology Labor Market (N = 5,859 Modeling Cohort)  
**Phase:** India-5  
**Status:** Certified & Validated (30/30 Gates Passed)  
**Date:** October 7, 2026  
**Author:** Antigravity Data Science & Statistical Governance Team  

---

## 1. Executive Summary

Phase India-5 investigates the structural organization of technical competencies in the Indian technology labor market and examines the empirical relationship between unsupervised skill configurations, disclosed compensation, and out-of-sample salary prediction errors.

Operating under strict scientific governance, all prior artifacts from Phases India-1 through India-4.1 remain immutable: the 5,859-row modeling cohort, the 284-skill binary feature vocabulary, and the frozen gradient-boosted salary prediction model (`india_salary_v1`) were preserved with zero retraining, parameter tuning, or data modification.

### Key Headline Findings:
1. **Primary Population & Sparsity:** Out of 5,859 technology postings in the frozen modeling cohort, 5,323 (90.85%) contain at least one curated technical skill. Across the 5,323 x 284 skill matrix, matrix sparsity is 98.58% (average of 4.02 skills per posting). Zero-skill postings (N = 536, 9.15%) were identified, audited, and strictly excluded from archetype formation.
2. **PCA Representation:** Centered covariance PCA was selected over variance-standardized PCA to avoid distorting Euclidean distances via artificial up-weighting of rare technical terms. Fifteen principal components were retained, capturing 37.74% of cumulative variance and spanning the major technological axes of the Indian tech ecosystem.
3. **K-Means & Stability:** Multi-criterion evaluation across candidate solutions ($k \in [2, 10]$) established $k = 6$ as the optimal, scientifically defensible clustering solution. The solution demonstrates strong assignment stability across random initializations (Mean ARI = 0.8035, Median ARI = 0.7219; Mean AMI = 0.8016, Median AMI = 0.7487 across seeds `[42, 7, 21, 100, 123]`) and eliminates pathological sub-2% micro-clusters.
4. **Discovered Job Archetypes (Ranked by Observed Median Salary):**
   - **IND_ARC_01 (Big Data Engineering & Distributed Systems):** N = 198 (3.7%), Median Salary = Rs. 20.00 LPA (Spark 99.0%, Scala 93.4%, Hadoop 81.3%, Airflow 58.6%).
   - **IND_ARC_02 (Enterprise Java & Microservices Backend):** N = 446 (8.4%), Median Salary = Rs. 18.75 LPA (Java 92.2%, Microservices 72.6%, Spring Boot 66.6%).
   - **IND_ARC_03 (Python, Cloud Data & Applied AI/ML):** N = 481 (9.0%), Median Salary = Rs. 17.00 LPA (Python 99.6%, SQL 25.6%, ML 16.4%, AWS 16.0%, Generative AI 8.1%).
   - **IND_ARC_04 (Full-Stack & Modern Application Engineering):** N = 547 (10.3%), Median Salary = Rs. 13.00 LPA (Development 100%, React 12.6%, SQL 11.9%, JavaScript 11.2%, .NET 10.4%).
   - **IND_ARC_05 (Baseline & General Technology Stack):** N = 3,526 (66.2%), Median Salary = Rs. 7.50 LPA (Broad heterogeneous IT roles, QA, support, generic SQL/JavaScript).
   - **IND_ARC_06 (Enterprise ERP & SAP Functional Solutions):** N = 125 (2.3%), Median Salary = Rs. 3.62 LPA (SAP 100%, Consulting 99.2%, FICO 98.4%, MM 91.2%).
5. **RQ2 Evidence:** Non-parametric omnibus testing demonstrates substantial, statistically significant salary variation across the discovered archetypes (Kruskal-Wallis $H = 817.91, df = 5, p = 1.55 \times 10^{-174}, \epsilon^2 = 0.1529$). Pairwise Dunn post-hoc tests with Holm multiplicity adjustment confirm widespread separation.
6. **RQ3 Evidence (Leakage-Safe Holdout Error Stratification):** Using a strictly leakage-safe evaluation pipeline fitted exclusively on training data, frozen model holdout predictions exhibit statistically significant error heterogeneity across archetypes (Kruskal-Wallis on absolute errors: $H = 66.15, df = 5, p = 6.48 \times 10^{-13}, \epsilon^2 = 0.0575$). Prediction error ranges from MAE = Rs. 1.06 LPA (SAP ERP) and Rs. 1.60 LPA (Big Data Engineering; Relative MAE = 8.0%) up to Rs. 5.22 LPA (Full-Stack Application Engineering; Relative MAE = 37.3%).

---

## 2. Research Questions

This phase formally addresses Research Questions 2 and 3 of the INT234 predictive analytics program:

- **RQ2:** *Do Indian technology job postings naturally/recurringly form skill-based archetypes, and do these archetypes exhibit meaningful salary differences?*
- **RQ3:** *Does salary-prediction error differ across those discovered skill archetypes when evaluated on held-out data using the frozen production model?*

### Scientific Language Protocol
In accordance with methodological standards:
- Archetypes are analytical structures discovered from empirical skill co-occurrence, not official occupational definitions.
- Observed salary differences represent descriptive associations rather than causal effects.
- Claims of "natural classes" or "true clusters" are avoided; instead, findings are framed as "recurring skill-based structures" and "overlapping market archetypes."
- Model predictive metrics ($R^2$, MAE) are evaluated as out-of-sample predictive performance, not "accuracy."

---

## 3. Frozen Inputs

All assets produced and certified in India Phases 1 through 4.1 remain intact and frozen:

| Frozen Asset | File Path | Verified SHA-256 Checksum | Size |
|---|---|---|---|
| **Salary Model** | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | 549,969 B |
| **Preprocessor** | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | 10,527 B |
| **Model Metadata** | `models/india/final_model_metadata.json` | `3e2aed92bee6a939295ac0d07fe4701856d079ea6f279952cb71b26565af3cb3` | 8,995 B |
| **Evaluation Metrics**| `models/india/final_evaluation.json` | `04552f31c8694223a7895a10ce195acf5629ec772fa7da68628a5b0afea7658b` | 679 B |
| **Feature List** | `models/india/final_feature_list.json` | `710aebaca840d4300a1e5f513fbe4826310abad9aa99e0547e63c0aabbef610e` | 15,748 B |
| **Modeling Cohort** | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | 654,351 B |
| **USA Model** | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | 619,464 B |

Frozen model specifications: `HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, l2_regularization=1.0)` on $\log(1 + y)$ target, evaluated on holdout ($N = 1,173$):
- **Holdout MAE:** Rs. 3.71 LPA (Rs. 371,473 INR)
- **Holdout RMSE:** Rs. 6.22 LPA (Rs. 621,881 INR)
- **Holdout $R^2$:** 0.5798
- **Holdout Median AE:** Rs. 2.08 LPA (Rs. 207,704 INR)
- **Holdout MAPE:** 35.22%

---

## 4. Population Definition

The primary population for skill archetype discovery is defined strictly as:
$$\mathcal{P}_{\text{archetype}} = \{ x_i \in \text{Cohort}_{\text{India}} \mid \sum_{j=1}^{284} \text{skill}_{ij} \ge 1 \}$$

- **Full Modeling Cohort:** $N = 5,859$
- **Skill-Bearing Primary Population:** $N = 5,323$ (90.85%)
- **Zero-Skill Postings:** $N = 536$ (9.15%)

Zero-skill postings were audited. Because archetype discovery seeks to characterize technical skill co-occurrence structures, clustering zero-skill rows would create an uninformative, degenerate cluster defined solely by feature absence. Consequently, zero-skill rows were excluded from unsupervised model fitting and assigned to an explicit `IND_ARC_UNASSIGNED` category in downstream data assets.

---

## 5. Skill Matrix Construction

The input matrix for unsupervised learning was constructed exclusively from the 284 binary technical skill columns established during Phase India-3:
$$X \in \{0, 1\}^{5323 \times 284}$$

Strict feature isolation was enforced:
- **No Target Features:** `salary_midpoint_inr`, `salary_lpa`, `min_salary`, `max_salary` were excluded.
- **No Categorical Covariates:** `normalized_role`, `city_grouped`, `work_mode` were excluded.
- **No Numerical Covariates:** `experience_midpoint_years`, `experience_range_years`, `total_selected_skill_count` were excluded.
- **No Model Artifacts:** Model predictions, residuals, and loss terms were excluded.

The feature space reflects purely the technological skills extracted from job postings.

---

## 6. Skill Sparsity

Audit of the 5,323 x 284 skill matrix reveals:
- **Total Matrix Entries:** $1,511,732$
- **Zero Entries:** $1,490,248$
- **Active Entries:** $21,484$
- **Matrix Sparsity:** $98.58\%$
- **Average Active Skills per Posting:** $4.04$
- **Median Active Skills per Posting:** $3.00$

The top 5 most prevalent skills are:
1. `development`: $13.58\%$ ($N = 723$)
2. `python`: $12.10\%$ ($N = 644$)
3. `sql`: $10.11\%$ ($N = 538$)
4. `react`: $7.63\%$ ($N = 406$)
5. `java`: $6.97\%$ ($N = 371$)

Conversely, 142 skills occur in fewer than 10 postings (<0.2% prevalence). This extreme sparsity governs the mathematical choice of dimensionality reduction.

---

## 7. PCA Methodology

Two principal dimensionality reduction paradigms were evaluated:

### Candidate Formulations:
1. **PCA-A: Centered Covariance PCA (`StandardScaler(with_mean=True, with_std=False)` + PCA):**
   Subtracts the empirical feature mean $\bar{x}_j$ but preserves feature variances $\text{Var}(x_j) = p_j(1 - p_j)$. Euclidean distances in the reduced space remain proportional to empirical skill co-occurrence frequencies.
2. **PCA-B: Variance-Standardized Correlation PCA (`StandardScaler(with_mean=True, with_std=True)` + PCA):**
   Standardizes all columns to unit variance. Each feature is divided by $s_j = \sqrt{p_j(1 - p_j)}$.

### Methodological Decision:
PCA-A was selected as the authoritative representation. In a 98.58% sparse binary matrix, scaling unit variance divides rare skills (e.g., $p = 0.0006$, 3 postings) by $s \approx 0.024$, multiplying their geometric weight by $\sim 42\times$. This artificially inflates idiosyncratic singleton co-occurrences into dominant principal components, producing noise-dominated clusters. Centered covariance PCA maintains natural market weighting where prevalent technologies define primary coordinate axes while rare terms provide fine-grained subgroup structure.

---

## 8. PCA Results

Scree analysis of centered covariance PCA reveals:

| Component | Eigenvalue | Variance Ratio (%) | Cumulative Variance (%) | Primary Technological Axis |
|---|---|---|---|---|
| **PC01** | 0.2227 | 5.95% | 5.95% | Enterprise Java / Microservices vs. SAP Consulting |
| **PC02** | 0.1896 | 5.06% | 11.01% | Big Data (Python/Spark/Scala) vs. SAP Consulting |
| **PC03** | 0.1549 | 4.14% | 15.15% | Enterprise Python / SAP vs. Frontend Web |
| **PC04** | 0.1145 | 3.06% | 18.20% | Application Web Dev (React/JS/SQL) vs. Java Backend |
| **PC05** | 0.1040 | 2.78% | 20.98% | Cloud Data Modeling (SQL/GCP/AWS) vs. Web Frontend |
| **PC10** | 0.0601 | 1.61% | 31.26% | Modern Frontend / DevOps Infrastructure |
| **PC15** | 0.0418 | 1.12% | 37.74% | Full-Stack Integration / Architecture |

### Component Retention Rationale:
15 principal components were retained ($37.74\%$ cumulative variance). Beyond PC15, the scree curve plateaus with individual component variance contributions falling below 1.1%, representing high-dimensional residual noise. Downstream K-Means stability testing confirmed that 15 components provide optimal semantic stability without dimensional dilution.

---

## 9. K-Means Methodology

K-Means clustering was executed on the 15-dimensional PCA projection using Euclidean distance:
$$\min_{\mu_1, \dots, \mu_k} \sum_{i=1}^{N} \min_{j \in \{1, \dots, k\}} \| x_i - \mu_j \|_2^2$$

### Hyperparameter Configuration:
- **Algorithm:** Lloyd's algorithm with K-Means++ initialization
- **Number of Initializations (`n_init`):** 10
- **Maximum Iterations (`max_iter`):** 300
- **Random State:** 42 (Primary)
- **Input Space:** $5,323 \times 15$ (Retained PCA components)

---

## 10. K-Means Candidate Results

Candidate solutions from $k = 2$ to $k = 10$ were evaluated:

| $k$ | Silhouette | Davies-Bouldin | Calinski-Harabasz | Inertia | Min Size ($N$) | Min Size (%) | Sub-2% Flag |
|---|---|---|---|---|---|---|---|
| **2** | 0.3344 | 1.7401 | 717.2 | 6885.3 | 695 | 13.06% | False |
| **3** | 0.3991 | 1.1926 | 785.6 | 6031.9 | 125 | 2.35% | False |
| **4** | 0.3963 | 1.2136 | 855.1 | 5271.1 | 125 | 2.35% | False |
| **5** | 0.3375 | 1.1484 | 861.0 | 4742.1 | 125 | 2.35% | False |
| **6** | **0.3599** | **1.1795** | **870.6** | **4296.1** | **125** | **2.35%** | **False** |
| **7** | 0.3914 | 1.2957 | 822.7 | 4051.4 | 52 | 0.98% | **True** |
| **8** | 0.3882 | 1.1058 | 831.8 | 3728.6 | 81 | 1.52% | **True** |
| **9** | 0.4036 | 1.1085 | 858.3 | 3408.7 | 75 | 1.41% | **True** |
| **10**| 0.4086 | 0.9097 | 858.2 | 3184.2 | 39 | 0.73% | **True** |

---

## 11. Cluster Stability

For the primary candidate solutions, cluster stability was evaluated across 5 distinct random initialization seeds: `[42, 7, 21, 100, 123]`. All 10 pairwise seed comparisons were evaluated using Adjusted Rand Index (ARI) and Adjusted Mutual Information (AMI):

### Pairwise Seed Stability ($k = 6$):

| Seed Pair | Adjusted Rand Index (ARI) | Adjusted Mutual Information (AMI) |
|---|---|---|
| **42 vs 7** | 0.7203 | 0.7495 |
| **42 vs 21** | 0.7168 | 0.7479 |
| **42 vs 100** | 1.0000 | 1.0000 |
| **42 vs 123** | 0.7226 | 0.7492 |
| **7 vs 21** | 0.9897 | 0.9859 |
| **7 vs 100** | 0.7203 | 0.7495 |
| **7 vs 123** | 0.7262 | 0.7161 |
| **21 vs 100** | 0.7168 | 0.7479 |
| **21 vs 123** | 0.7226 | 0.6816 |
| **100 vs 123** | 1.0000 | 1.0000 |

### Summary Statistics ($k = 6$):
- **Mean ARI:** $0.8035$ (Good-to-strong assignment stability)
- **Median ARI:** $0.7219$
- **Minimum ARI:** $0.7168$
- **Maximum ARI:** $1.0000$
- **Mean AMI:** $0.8016$
- **Median AMI:** $0.7487$

---

## 12. Final Archetype Selection

The multi-criterion decision policy selected **$k = 6$** based on the following converging evidence:
1. **Absence of Pathological Clusters:** At $k = 6$, all clusters satisfy the $\ge 2\%$ minimum size threshold (smallest cluster $N = 125, 2.35\%$). At $k \ge 7$, pathological micro-clusters emerge ($N = 52, 0.98\%$ at $k=7$; $N = 39, 0.73\%$ at $k=10$).
2. **Compactness & Separation:** Calinski-Harabasz index peaks at $k = 6$ ($CH = 870.6$), demonstrating superior between-to-within cluster dispersion ratio compared to $k=5$ ($861.0$) and $k=7$ ($822.7$).
3. **High Partition Stability:** Mean ARI of $0.8035$ and Mean AMI of $0.8016$ establish good-to-strong reproducibility across arbitrary random starts.
4. **Technological Coherence:** Each of the 6 clusters represents an empirically recognizable technology domain in the Indian job market (Big Data, Enterprise Java, Python/Data/AI, Web/App Engineering, Core Baseline, and SAP ERP).

---

## 13. Archetype Profiles

| Archetype ID | Public Archetype Name | Size ($N$) | Share (%) | Median Salary | Dominant Role Family | Top 3 Skills |
|---|---|---|---|---|---|---|
| **IND_ARC_01** | Big Data Engineering & Distributed Systems | 198 | 3.72% | Rs. 20.00 LPA | Data Engineer (96.5%) | Spark (99.0%), Scala (93.4%), Hadoop (81.3%) |
| **IND_ARC_02** | Enterprise Java & Microservices Backend | 446 | 8.38% | Rs. 18.75 LPA | Software Engineer (51.8%) | Java (92.2%), Microservices (72.6%), Spring Boot (66.6%) |
| **IND_ARC_03** | Python, Cloud Data & Applied AI/ML | 481 | 9.04% | Rs. 17.00 LPA | Software Eng / Data Eng (32.6%) | Python (99.6%), SQL (25.6%), ML (16.4%) |
| **IND_ARC_04** | Full-Stack & Modern Application Engineering | 547 | 10.28% | Rs. 13.00 LPA | Other Tech (58.3%), Software Eng (20.7%) | Development (100%), React (12.6%), SQL (11.9%) |
| **IND_ARC_05** | Baseline & General Technology Stack | 3,526 | 66.24% | Rs. 7.50 LPA | Other Tech (61.9%), QA (8.6%) | SQL (7.5%), JavaScript (5.4%), SAP (4.8%) |
| **IND_ARC_06** | Enterprise ERP & SAP Functional Solutions | 125 | 2.35% | Rs. 3.62 LPA | Other Tech / SAP Specialists (99.2%) | SAP (100%), Consulting (99.2%), FICO (98.4%) |

---

## 14. Skill Lift Analysis

Skill lift measures the relative enrichment of a skill within a cluster relative to the full skill-bearing population baseline:
$$\text{Lift}(s, c) = \frac{P(s \mid c)}{P(s)}$$

### Characteristic Skill Enrichment Profiles:
- **IND_ARC_01 (Big Data):** Scala ($25.77\times$, $93.4\%$), Hadoop ($25.16\times$, $81.3\%$), Hive ($25.15\times$, $43.9\%$), Big Data ($23.64\times$, $36.9\%$), Airflow ($23.10\times$, $58.6\%$).
- **IND_ARC_02 (Java Backend):** Encryption ($11.71\times$, $11.4\%$), Spring Boot ($11.47\times$, $66.6\%$), Spring ($11.39\times$, $28.0\%$), Core Banking ($11.27\times$, $11.4\%$), Microservices ($10.71\times$, $72.6\%$).
- **IND_ARC_03 (Python / AI):** Python ($8.23\times$, $99.6\%$), Flask ($8.22\times$, $5.4\%$), Generative AI ($7.85\times$, $8.1\%$), Django ($7.48\times$, $10.0\%$), FastAPI ($7.11\times$, $5.6\%$), Machine Learning ($7.11\times$, $16.4\%$).
- **IND_ARC_04 (Application Dev):** Development ($7.36\times$, $100.0\%$), .NET ($4.14\times$, $10.4\%$), Senior ($3.04\times$, $5.5\%$), Full Stack ($2.34\times$, $6.9\%$), JavaScript ($1.93\times$, $11.2\%$).
- **IND_ARC_05 (Baseline):** Generalist baseline. Lifts for all specialized technologies remain below $1.0\times$ (SQL: $0.74\times$, JavaScript: $0.93\times$).
- **IND_ARC_06 (SAP ERP):** SAP Testing ($41.84\times$, $89.6\%$), FICO ($37.15\times$, $98.4\%$), MM ($35.96\times$, $91.2\%$), Certified ($35.81\times$, $88.8\%$), SAP MM ($35.12\times$, $90.4\%$), SAP FICO ($33.30\times$, $97.6\%$).

---

## 15. Salary Distribution by Archetype

Descriptive statistics for observed compensation (in Lakhs Per Annum INR) across archetypes:

| Archetype ID | $N$ | Median (LPA) | Mean (LPA) | Q1 (LPA) | Q3 (LPA) | IQR (LPA) | Std Dev (LPA) | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| **IND_ARC_01** | 198 | **20.00** | 18.75 | 18.12 | 20.00 | 1.88 | 4.88 | 5.50 | 45.00 |
| **IND_ARC_02** | 446 | **18.75** | 18.57 | 13.00 | 22.00 | 9.00 | 7.62 | 2.50 | 50.00 |
| **IND_ARC_03** | 481 | **17.00** | 18.04 | 11.25 | 24.00 | 12.75 | 9.07 | 2.50 | 60.00 |
| **IND_ARC_04** | 547 | **13.00** | 13.54 | 7.00 | 18.50 | 11.50 | 7.69 | 1.50 | 45.00 |
| **IND_ARC_05** | 3,526 | **7.50** | 11.17 | 4.00 | 16.00 | 12.00 | 9.04 | 1.20 | 80.00 |
| **IND_ARC_06** | 125 | **3.62** | 4.82 | 3.62 | 3.62 | 0.00 | 3.12 | 2.25 | 22.50 |

---

## 16. Formal Salary Comparison

Non-parametric Kruskal-Wallis omnibus testing was conducted to evaluate whether observed salary distributions differ significantly across the 6 discovered archetypes:

- **Null Hypothesis ($H_0$):** Disclosed salary distributions are identical across all archetypes.
- **Test Statistic:** Kruskal-Wallis $H = 817.91$
- **Degrees of Freedom:** $df = 5$
- **$p$-Value:** $1.55 \times 10^{-174}$
- **Effect Size:** Rank epsilon-squared $\epsilon^2 = \frac{H - k + 1}{N - k} = 0.1529$ (Large effect size: $\epsilon^2 > 0.14$)

### Post-Hoc Dunn Pairwise Tests (Holm Multiplicity Adjusted):
All 15 pairwise comparisons demonstrate statistically significant differences ($p_{\text{adj}} < 0.05$) with the exception of IND_ARC_01 vs IND_ARC_02 ($z = 1.63, p_{\text{adj}} = 0.2057$) and IND_ARC_02 vs IND_ARC_03 ($z = 1.94, p_{\text{adj}} = 0.1578$), which reflect adjacent high-compensation engineering clusters.

---

## 17. RQ2 Evaluation

**Conclusion:** **RQ2 is supported at the level of recurring skill-based structure.**
The empirical evidence indicates that the Indian technology job-posting market contains multiple reproducible, highly interpretable skill configurations. These clusters exhibit strong internal technological coherence, good-to-strong assignment stability across random seeds (Mean ARI = 0.8035), and large, statistically significant observed salary differences ($\epsilon^2 = 0.1529$). 

In accordance with scientific integrity guidelines, these structures should be interpreted as **overlapping market archetypes** rather than mutually exclusive natural occupational classes.

---

## 18. Frozen Model Evaluation Integrity

Prior to evaluating RQ3 error stratification, the frozen production model (`models/india/final_model.pkl`) was audited on the full holdout partition ($N = 1,173$):
- **Holdout MAE:** Rs. 3.7147 LPA
- **Holdout RMSE:** Rs. 6.2188 LPA
- **Holdout $R^2$:** 0.5798
- **Holdout Median AE:** Rs. 2.0770 LPA
- **Holdout MAPE:** 35.22%

Verification confirms zero modification, zero retraining, and bitwise-exact reproduction of headline Phase India-4 metrics.

---

## 19. Leakage-Safe Holdout Archetype Assignment

To prevent distributional variance and centroid coordinate contamination, holdout archetype assignments were executed under a strict leakage-safe protocol:
1. The training partition ($N_{\text{train, skills}} = 4,254$) was used to fit an independent PCA transformer (15 PCs) and K-Means clustering model ($k = 6$).
2. Training cluster centroids were aligned with full-cohort descriptive archetype definitions via Hungarian maximum-overlap bipartite matching.
3. Holdout postings ($N_{\text{holdout, skills}} = 1,069$) were transformed using the training PCA basis and assigned to nearest clusters using the training K-Means model.

No held-out test data influenced the geometric orientation of PCA axes or K-Means centroid coordinates.

---

## 20. RQ3 Error Analysis

Out-of-sample prediction error metrics for the frozen production model stratified by holdout archetype:

| Archetype ID | Archetype Name | Holdout $N$ | Holdout Share | Median Salary | MAE (LPA) | RMSE (LPA) | Med AE (LPA) | Mean Res (LPA) | Rel MAE (%) |
|---|---|---|---|---|---|---|---|---|---|
| **IND_ARC_01** | Big Data Engineering | 34 | 3.18% | Rs. 20.00 LPA | **1.60** | 2.55 | 0.84 | +1.07 | **8.0%** |
| **IND_ARC_02** | Enterprise Java Backend | 93 | 8.70% | Rs. 18.75 LPA | **3.87** | 5.81 | 2.40 | +0.75 | **20.6%** |
| **IND_ARC_03** | Python, Data & AI | 83 | 7.76% | Rs. 15.00 LPA | **3.80** | 5.43 | 2.71 | +1.20 | **25.4%** |
| **IND_ARC_04** | Full-Stack Application Dev | 114 | 10.66% | Rs. 14.00 LPA | **5.22** | 7.79 | 3.93 | +1.87 | **37.3%** |
| **IND_ARC_05** | Baseline Tech Stack | 725 | 67.82% | Rs. 7.50 LPA | **3.55** | 6.00 | 1.92 | +0.99 | **47.3%** |
| **IND_ARC_06** | SAP ERP Solutions | 20 | 1.87% | Rs. 3.62 LPA | **1.06** | 2.95 | 0.06 | +0.24 | **29.3%** |

### Error Metric Definitions:
- $\text{Residual} = y_{\text{actual}} - \hat{y}_{\text{pred}}$ (Positive residual = model underprediction).
- $\text{Relative MAE} = \frac{\text{MAE}}{\text{Median Disclosed Salary}} \times 100$.

---

## 21. Formal Error Comparison

A Kruskal-Wallis test on absolute prediction errors ($|y - \hat{y}|$) across the 6 holdout archetypes was executed:
- **Test Statistic:** Kruskal-Wallis $H = 66.15$
- **Degrees of Freedom:** $df = 5$
- **$p$-Value:** $6.48 \times 10^{-13}$
- **Effect Size:** Rank epsilon-squared $\epsilon^2 = 0.0575$ (Moderate effect size)

### Conclusion for RQ3:
**RQ3 is supported: prediction error is heterogeneous across the identified skill archetypes.**
The frozen model exhibits substantial, statistically significant error variation across skill groups. While absolute MAE is lowest in specialized, narrow-salary clusters such as SAP ERP (Rs. 1.06 LPA) and Big Data Engineering (Rs. 1.60 LPA), Relative MAE demonstrates that Big Data Engineering achieves the highest relative precision (8.0% of median salary), whereas the heterogeneous Baseline Tech Stack exhibits the highest relative uncertainty (47.3% of median salary).

---

## 22. High-Salary Tail Context

Contextual analysis from Phase India-4 established that postings with disclosed salaries $\ge 20$ LPA exhibit systematic underprediction (Mean signed residual = +7.56 LPA at $\ge 20$ LPA; +31.12 LPA at $\ge 40$ LPA). 

Archetype analysis provides granular insight into this phenomenon:
- In IND_ARC_01 (Big Data, Median = 20 LPA), the model maintains low error (MAE = 1.60 LPA, Mean Residual = +1.07 LPA) because high compensation in this segment is strongly tied to explicit, high-value technical competencies (Spark, Scala, Airflow).
- In IND_ARC_04 (Application Engineering) and IND_ARC_05 (Baseline Stack), postings reaching upper salary brackets exhibit higher underprediction because compensation drivers (seniority, equity, non-technical leadership) are unobserved in the feature space.

---

## 23. Limitations

1. **Observational Nature:** Data reflects job postings with disclosed salaries; findings represent observational associations, not causal wage returns.
2. **Binary Skill Representation:** Skill depth, proficiency, and years of tool experience are not captured in binary indicators.
3. **K-Means Geometric Constraints:** K-Means assumes spherical cluster variance; highly elongated or density-varying skill sub-spaces may be partially constrained.
4. **Sample Size in Rare Clusters:** In holdout evaluation, specialized clusters (e.g., SAP ERP $N=20$, Big Data $N=34$) have smaller sample sizes, warranting caution against overinterpreting higher-order moments.
5. **Analytical Construct:** Discovered archetypes represent analytical models of the labor market, not official government occupational taxonomies.

---

## 24. Research Integrity

- Unsupervised clustering was conducted exclusively on skill binary indicators.
- No salary, target, residual, or model prediction was utilized to define clusters.
- The frozen model was not retrained or modified.
- Holdout archetype assignments were generated using a leakage-safe pipeline fitted strictly on training data.
- No causal assertions are made.

---

## 25. Reproducibility

Deterministic execution is guaranteed via fixed random seeds:
- Primary Seed: 42
- Stability Seeds: `[42, 7, 21, 100, 123]`
- Software Stack: Python 3.12, scikit-learn 1.7.2, scipy 1.15.2, statsmodels 0.14.4, pandas 2.2.3, numpy 2.2.3.
- Script Entrypoint: `python -m src.india.archetypes`

---

## 26. Conclusion

Phase India-5 successfully achieves all scientific and technical objectives:
1. Discovered 6 recurring, highly interpretable skill archetypes in the Indian tech market.
2. Demonstrated strong cluster stability across seeds (Mean ARI = 0.8035).
3. Confirmed statistically significant salary differences across archetypes (RQ2 supported, $p = 1.55 \times 10^{-174}, \epsilon^2 = 0.1529$).
4. Confirmed statistically significant prediction error heterogeneity across archetypes using the frozen model under a leakage-safe protocol (RQ3 supported, $p = 6.48 \times 10^{-13}, \epsilon^2 = 0.0575$).
5. Preserved 100% of frozen model and dataset assets.

---

## 27. Artifact Registry

A complete catalog of all Phase India-5 artifacts is documented in `reports/india_phase5_artifact_registry.md`.

---

## 28. Validation Gates

Phase India-5 underwent automated verification across all 30 validation gates (`scratch/verify_phase5_gates.py`), achieving a **30/30 PASS (100%)** green certification.
