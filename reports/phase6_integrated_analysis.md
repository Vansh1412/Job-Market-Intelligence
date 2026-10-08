# INT234 Predictive Analytics — Final Integrated Research Report
**Project Title:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning  
**Author:** Lead ML Research Engineer, Data Scientist & Statistical Analyst  
**Course & Task:** INT234 Predictive Analytics — Academic Task 2  
**Date:** October 2026  
**Status:** Certified, Integrated & Frozen  

---

# Executive Overview

The modern technology labor market is characterized by rapid technological proliferation, evolving job titles, and substantial compensation dispersion. Job postings provide an expansive real-world signal of market demand; however, raw postings are noisy, unstructured, and subject to non-standardized terminology. This study investigates the latent structure of technology competencies and their relationship with annualized compensation through a rigorous, two-stage machine learning investigation:
1. **Unsupervised Archetype Discovery:** Projecting high-dimensional, sparse technical skill profiles ($N = 116,830$ postings $\times$ 82 skills) into a continuous low-dimensional subspace using Centered Covariance Principal Component Analysis (PCA) and clustering into $k = 7$ recurring skill-based archetypes via K-Means.
2. **Supervised Salary Modeling & Error Disaggregation:** Training regularized linear, bagged, boosted, and neural regressors on verified compensation data ($N = 34,036$) to benchmark predictive accuracy, test whether archetype representations provide incremental predictive value beyond explicit skills, and evaluate whether salary prediction error varies systematically across labor-market segments.

### Key Empirical Findings:
- **RQ1 (Skill-Salary Associations):** Specialized artificial intelligence competencies (`machine_learning`, `pytorch`, `deep_learning`), cloud infrastructure (`aws`, `kubernetes`, `terraform`), and compiled systems languages (`golang`, `c++`) demonstrate the strongest positive predictive associations with salary. However, non-skill structural controls—specifically `Lead / Principal / Executive` seniority ($+\$4,374$ test permutation impact) and Tier-1 metropolitan markets (`San Francisco`, `New York`, `Seattle`)—remain the dominant baseline drivers of compensation scale.
- **RQ2 (Skill Archetypes):** Technology postings exhibit **recurring and reproducible skill-based structures with moderate separation and substantial overlap** ($k = 7$). While cohesive centroids emerge for Cloud Infrastructure, Web Engineering, Multi-Cloud Architecture, Data/BI, AI/ML, and Systems Engineering, nearly half the population ($49.47\%$) resides in a broad, heterogeneous foundational cohort (`FOUND_TECH`) characterized by low skill counts ($85.31\% \le 2$ skills).
- **RQ3 (Archetype Error Disaggregation):** Salary prediction error differs significantly across archetypes (Kruskal-Wallis $H = 88.10$, $p = 7.53 \times 10^{-17}$, $p < 0.001$). The `AI_ML` archetype achieves the lowest absolute ($\$27,002$) and relative ($14.42\%$) error, reflecting uniform, premium market pricing. `CLOUD_ARCH` displays the highest absolute error ($\$46,098$) due to elevated compensation scale (median $\$220\text{k}$) and wide dispersion, while `FOUND_TECH` exhibits the highest relative error ($22.16\%$) consistent with role heterogeneity.
- **Archetype Incremental Value:** Incorporating unsupervised archetype memberships (**Feature Set C**, 130 features) produces **no practically meaningful improvement** over explicit skill and role metadata (**Feature Set A**, 123 features), yielding holdout test MAEs of **$\$36,424.84$** vs. **$\$36,380.64$** (difference: $+\$44.20$, or $0.12\%$). In tree-based gradient boosting, explicit high-resolution skill indicators already supply the principal predictive signal available from observed posting metadata.

---

# 1. Problem Statement

Accurately valuing human capital and navigating technical competencies are critical challenges for software engineers, hiring organizations, and labor economists. While job titles such as "Software Engineer" or "Data Scientist" are ubiquitous, their actual responsibilities and compensation vary by orders of magnitude depending on underlying technical competencies.

Traditional labor market research often relies on government surveys (e.g., US Bureau of Labor Statistics) that aggregate tech jobs into coarse occupational codes (e.g., SOC 15-1252), masking the economic premiums associated with emerging computing stacks such as Large Language Models (LLMs), distributed systems, or Kubernetes orchestration. Conversely, while online job boards offer granular text, compensation data is frequently absent, non-standardized, or confounded by geographical wage differentials.

This project addresses these challenges by developing a transparent, reproducible, and scientifically defensible machine learning pipeline that:
- Establishes a clean, curated taxonomy of 82 technical skills and 18 role families.
- Investigates whether technical skills naturally cluster into meaningful, stable archetypes.
- Benchmarks predictive models to estimate annualized salary midpoints while rigorously preventing target and archetype leakage.
- Disaggregates residual errors to determine where algorithmic compensation prediction succeeds and where it encounters structural uncertainty.

---

# 2. Research Questions

The entire analytical investigation revolves around three core research questions:

### RQ1 — Skill & Combination Associations with Salary
> **Which skills and skill combinations are most associated with higher salaries?**
- *Methodological Framing:* This is an **associational and predictive** question, not a causal one. The analysis evaluates observed median salary differences, tree split gain importance, holdout test permutation importance, and standardized linear coefficients, while explicitly acknowledging confounding by career seniority, role family, geography, and unobserved candidate tenure.

### RQ2 — Latent Skill-Based Job Archetypes
> **Do job postings naturally form skill-based archetypes?**
- *Methodological Framing:* Evaluates whether unsupervised learning (PCA + K-Means) identifies reproducible clusters within skill-bearing postings ($N = 116,830$). In accordance with Phase 4.2 findings, archetypes are framed as **recurring, reproducible structures with moderate geometric separation and substantial overlap**, rather than discrete, mutually exclusive "natural classes."

### RQ3 — Subgroup Error Differences Across Archetypes
> **Does salary-prediction error differ systematically across skill-based job archetypes?**
- *Methodological Framing:* Evaluates whether the winning supervised model displays differential accuracy across the seven discovered archetypes. Tests the null hypothesis of equal error distributions using the non-parametric Kruskal-Wallis test and evaluates absolute error (MAE, RMSE) versus relative error ($\text{MAE} / \text{Median Salary}$) to distinguish scale-driven dispersion from model instability.

---

# 3. Dataset and Provenance

To satisfy the rigorous requirements of INT234 Academic Task 2, two real-world datasets collected from enterprise job-market platforms were audited across 14 qualitative and quantitative dimensions (documented in `reports/dataset_selection.md`):

| Evaluation Dimension | Dataset A (`jobs-tier1-L-2026-08-01`) | Dataset B (`nextgig_jobs_2026-06.parquet`) | Evaluation Outcome |
|---|---|---|---|
| **Raw Volume** | **394,300 postings** | 112,816 postings | Dataset A provides a 3.5× larger corpus. |
| **Salary Coverage** | **107,151 paired records (27.2%)** with 100% paired min/max | 46,885 dual-bound; 52,106 single-bound | Dataset A provides 2.3× paired salaries. |
| **Technical Tech Salaries** | **27,295 annual tech salaries** (25,008 USD) | 4,107 annual tech salaries (3,798 USD) | Dataset A provides 6.5× technical salary observations. |
| **Skill Curation** | **101 standardized skills** (Python, SQL, AWS, ML, Docker) | 53,889 uncurated, freeform tokens (retail/service heavy) | Dataset A isolates computing stacks; Dataset B is retail-heavy. |
| **Provenance Documentation** | **Exemplary:** Formal `DATASHEET.md`, `LICENSE.md`, data dictionary | Bare parquet file with no datasheet or license | Dataset A satisfies academic provenance standards. |

### Dataset Selection Decision:
**Dataset A was selected as the sole primary dataset.** Merging disparate datasets was explicitly rejected to prevent schema corruption and artificial row inflation. Dataset A provides the statistical power necessary for 5-fold cross-validation, feature set benchmarking, and subgroup error analysis without small-sample instability.

### Licensing & Compliance:
Dataset A is licensed for academic research and student evaluation. Raw data files are preserved locally in `data/raw/` with read-only access and excluded from public redistribution via `.gitignore`, in compliance with `reports/license_compliance.md`.

---

# 4. Data Preparation & Preprocessing Funnel

Phase 2 and Phase 2.1 established an end-to-end reproducible data preparation pipeline (`src/rebuild_phase2_1.py`) that transformed raw, noisy ATS postings into validated modeling datasets:

```text
RAW INGESTION (N = 394,300)
       ↓
CASE DEDUPLICATION (N = 335,995; removed 58,305 casing artifacts)
       ↓
TECHNOLOGY ROLE FILTERING (N = 114,873; purged non-tech corporate roles)
       ↓
SKILL TAXONOMY PARTITIONING (91 Curated Skills → 82 Technical, 2 Professional, 7 Business)
       ↓
SALARY NORMALIZATION & DOMAIN FILTERING ([$30,000, $600,000] USD window)
       ↓
SUPERVISED MODELING COHORT (N = 34,036 postings × 102 columns)
```

### Preprocessing Safeguards & Taxonomy Enhancements:
1. **18-Tier Role Family Hierarchy:** Upgraded preliminary classification to an 18-tier strict precedence hierarchy (Software Engineer, ML/AI Engineer, Technical Product, DevOps, Data Scientist, Data Engineer, Solutions Architecture, Engineering Management, Embedded/Hardware, Full-Stack, Security, Backend, Systems/Network, Frontend, QA/SDET, Mobile, BI Analyst, Other Tech). Every family satisfies $N \ge 215$.
2. **Seniority Parser (v3 Conflict Resolution):** Disambiguated individual contributor functional managers (Product Manager, Project Manager) from organizational executives, establishing an economically realistic hierarchy: Junior/Entry ($1.96\%$), Mid/Unspecified ($41.75\%$), Senior ($26.03\%$), Lead/Principal/Executive ($30.09\%$), and Intern ($0.16\%$).
3. **Salary Boundary Justification:** The $[\$30,000, \$600,000]$ window was empirically certified against standard Tukey IQR rules ($Q_1 - 1.5\text{IQR} = \$26.7\text{k}$, $Q_3 + 1.5\text{IQR} = \$339\text{k}$). Standard Tukey rules would truncate 714 legitimate high-paying tech roles (Principal Engineers, Directors). The domain filter trims only $0.25\%$ of observations (44 test/hourly entries $<\$30\text{k}$ and 41 extreme outliers $>\$600\text{k}$).
4. **Leakage Prevention Architecture:** Predictive features were strictly quarantined from target variables (`salary_min`, `salary_max`, `salary_midpoint`, `salary_band`, `log_salary`, `job_id`). Preprocessing transformers (`MetadataTransformer`) fit strictly on training partitions.

---

# 5. Exploratory Data Analysis (Phase 3 Synthesis)

Phase 3 (`notebooks/03_eda.ipynb` and `reports/phase3_eda_report.md`) conducted an in-depth statistical profiling of the supervised modeling cohort ($N = 34,036$):

### 5.1 Salary Target Dynamics
- **Central Tendency:** Median = **$\$180,372.50$**, Mean = **$\$187,020.55$**, Standard Deviation = **$\$65,817.80$**.
- **Percentiles:** $Q_1 = \$143,870.00$, $Q_3 = \$222,000.00$, $\text{IQR} = \$78,130.00$.
- **Skewness & Target Transformation:**
  - Raw Midpoint Skewness: **$+0.944$** (moderate right-tail skewness typical of wage data).
  - Log1p Midpoint Skewness: **$-0.503$** (near-normal, symmetric target distribution).
  - *Analytical Decision:* While log transformation stabilizes variance, direct regression on raw midpoint was selected for primary modeling because it achieved superior RMSE in original dollar space and direct interpretability, with log models serving as consistency checks.

### 5.2 Macroeconomic Drivers of Compensation
- **Seniority Effect:** Compensation scales monotonically with career level: Junior/Entry ($\$105\text{k}$) $\to$ Mid ($\$155\text{k}$) $\to$ Senior ($\$180\text{k}$) $\to$ Lead/Principal/Executive ($\$220\text{k}$). Seniority accounts for $21.2\%$ of rank variance ($\epsilon^2 = 0.2120$).
- **Role Family Effect:** Top median paying families are Engineering Management ($\$242,500$), Mobile Engineer ($\$200,000$), Backend Developer ($\$195,000$), and Security Engineer ($\$195,000$). Role family accounts for $9.6\%$ of rank variance ($\epsilon^2 = 0.096$).
- **Geography:** Tier-1 metropolitan markets command substantial premiums: Mountain View ($\$220\text{k}$), San Francisco ($\$218\text{k}$), New York City ($\$200\text{k}$), San Jose ($\$200\text{k}$), Seattle ($\$189,950$).
- **Remote Work Model:** Remote postings ($N = 10,778$, median $\$180,000$) vs. Onsite/Hybrid postings ($N = 23,258$, median $\$180,500$) showed no statistically significant difference (Mann-Whitney $U$ test $p = 0.0531$).

---

# 6. Skill-Based Archetype Discovery (Phase 4 / 4.1 / 4.2 Synthesis)

Phase 4 discovered, validated, and profiled latent skill archetypes using unsupervised machine learning.

### 6.1 The Phase 4.1 Surgical Correction
The initial Phase 4 clustering evaluated all 335,995 deduplicated postings. However, audit diagnostics revealed that **$65.23\%$ ($N = 219,165$) of postings contained zero parsed technical skills**, forcing K-Means to collapse $80.96\%$ of the market into an undifferentiated non-technical cluster. Phase 4.1 executed a surgical correction by restricting primary archetype discovery to postings with **$\ge 1$ parsed technical skill ($N = 116,830$)**, while preserving the full corpus strictly as a diagnostic baseline.

### 6.2 Centered Covariance PCA
Dimensionality reduction was performed on the $116,830 \times 82$ binary skill matrix:
- **Scaling Methodology:** Mean-centered covariance scaling (`StandardScaler(with_mean=True, with_std=False)`).
- **Blueprint Alignment & Rationale:** Section 5.6 of the course blueprint recommends generic standard scaling. However, adversarial experimentation proved that unit-variance scaling (Correlation PCA) artificially inflated the variance of rare skills (e.g., $0.2\%$ tags received $22\times$ weight), collapsing 15-PC explained variance to $38.08\%$ and forcing K-Means into an unstable 71.9% mega-cluster. Centered Covariance PCA preserves natural market prevalence.
- **Dimensionality & Retained Variance:** Retaining **15 Principal Components** captured **$56.05\%$** cumulative explained variance. Transparently, **$43.95\%$** of feature variance remains outside the 15-dimensional subspace.

### 6.3 Cluster Resolution ($k = 7$) & Stability
- **Cluster Selection Trade-off:** While $k = 2$ achieved the global silhouette maximum ($0.3449$), it split the market into cloud roles ($19.4\%$) versus an undifferentiated mass ($80.6\%$). $k = 7$ was selected as a **defensible multi-criteria compromise** achieving a local silhouette peak ($0.2379$), a favorable Davies-Bouldin index ($1.7633$), and interpretable domain alignment.
- **Stability Evaluation:** Across 10 seed pairs ([42, 7, 21, 100, 123]), K-Means demonstrated **good-to-strong stability**: Mean $\text{ARI} = \mathbf{0.7901}$ (min $0.6568$), Mean $\text{AMI} = \mathbf{0.8030}$ (min $0.6810$).
- **Salary Cohort Sensitivity:** Independent clustering on the salary cohort ($N = 30,897$) achieved a **$74.51\%$ Hungarian assignment match rate** and a **$0.8708$ mean centroid cosine similarity**, confirming structural consistency.

### 6.4 The Authoritative Seven Archetypes ($N = 116,830$)
| ID | Key | Archetype Name | Postings ($N$) | Share (%) | Defining Technical Stack | Median Salary ($) | Substantive Role Interpretation |
|:---:|---|---|---:|---:|---|---:|---|
| **0** | `FOUND_TECH` | Foundational & Broad Technical Roles | **57,791** | **49.47%** | `python` (20.9%), `sql` (15.5%), `git` (10.9%) | **$170,000** | Heterogeneous residual cohort dominated by low skill counts ($67.56\%$ single-skill, $85.31\% \le 2$ skills). |
| **1** | `DEVOPS_PLAT` | DevOps & Cloud Infrastructure Engineering | **7,614** | **6.52%** | `aws` (93.9%), `ci_cd` (85.2%), `kubernetes` (76.8%), `docker` (68.7%), `terraform` (64.5%) | **$195,000** | Cloud-native platform engineering, automated delivery pipelines, and infrastructure-as-code. |
| **2** | `WEB_FRONT` | Frontend & Modern Web Engineering | **13,878** | **11.88%** | `typescript` (92.4%), `javascript` (77.9%), `react` (75.4%), `html_css` (53.3%), `node_js` (44.2%) | **$165,650** | Client-side web application engineering, modern UI frameworks, and full-stack TypeScript. |
| **3** | `CLOUD_ARCH` | Multi-Cloud & Enterprise Architecture | **12,657** | **10.83%** | `azure` (89.5%), `aws` (54.2%), `gcp` (32.1%), `security` (41.5%), `microservices` (39.8%) | **$220,000** | Enterprise multi-cloud architecture, distributed systems, and cross-cloud migration. |
| **4** | `DATA_BI` | Data Engineering & Business Analytics | **12,042** | **10.31%** | `sql` (96.8%), `python` (78.5%), `snowflake` (52.4%), `spark` (48.7%), `etl` (45.6%) | **$170,000** | Modern data platform engineering, ETL pipelines, analytical warehousing, and BI. |
| **5** | `AI_ML` | AI / Machine Learning & LLM Engineering | **6,699** | **5.73%** | `python` (98.2%), `machine_learning` (95.4%), `pytorch` (74.2%), `deep_learning` (68.5%), `llm` (62.1%) | **$187,250** | Deep learning, generative AI, LLM adaptation, computer vision, and statistical modeling. |
| **6** | `SYS_ENG` | Systems & Core Backend Engineering | **6,149** | **5.26%** | `c++` (88.4%), `linux` (81.2%), `c#` (52.3%), `embedded` (44.6%), `golang` (38.7%) | **$190,000** | Low-level systems programming, firmware/embedded systems, and high-throughput servers. |

---

# 7. Salary Prediction & Model Evaluation (Phase 5 Synthesis)

Phase 5 evaluated whether machine learning can reliably predict salary midpoints and tested whether archetype membership improves prediction.

### 7.1 Cross-Validation Benchmark (5-Fold CV on $N_{\text{train}} = 27,228$)
Six model families were evaluated across Feature Sets A (123 cols), B (56 cols), and C (130 cols):
- **Naive Median Baseline:** CV MAE = **$\$49,502 \pm \$398$**, CV RMSE = **$\$65,733 \pm \$512$**, CV $R^2 = -0.0089$.
- **Ridge Regression ($\alpha=10.0$):** Set A CV MAE = **$\$38,544 \pm \$410$** ($R^2 = 0.3477$); Set B CV MAE = **$\$39,027$** ($R^2 = 0.3306$); Set C CV MAE = **$\$38,469$** ($R^2 = 0.3501$).
- **Random Forest Regressor:** Set A CV MAE = **$\$37,202 \pm \$241$** ($R^2 = 0.3888$); Set B CV MAE = **$\$36,683$** ($R^2 = 0.3980$); Set C CV MAE = **$\$37,180$** ($R^2 = 0.3888$).
- **Gradient Boosting Regressor:** Set A CV MAE = **$\$37,010 \pm \$180$** ($R^2 = 0.3926$); Set C CV MAE = **$\$36,982$** ($R^2 = 0.3929$).
- **XGBRegressor (Default):** Set A CV MAE = **$\$36,944 \pm \$199$** ($R^2 = 0.3959$); Set C CV MAE = **$\$36,947$** ($R^2 = 0.3950$).
- **MLP Regressor:** Set A CV MAE = **$\$36,943 \pm \$184$** ($R^2 = 0.3986$); Set C CV MAE = **$\$37,062$** ($R^2 = 0.3977$).

### 7.2 Controlled Hyperparameter Tuning
Controlled grid search on XGBoost (`tree_method='hist'`) across tree depth, learning rate, and estimator counts identified optimal parameters: `max_depth = 6`, `learning_rate = 0.10`, `n_estimators = 150`, `subsample = 0.80`, `colsample_bytree = 0.80`. Tuning improved training CV performance to:
- **CV MAE:** **$\$36,072 \pm \$185$** (an $\$872$ reduction over default)
- **CV RMSE:** **$\$49,886 \pm \$412$**
- **CV $R^2$:** **$0.4192 \pm 0.0071$** (a $+0.0233$ gain over default)

### 7.3 Final Holdout Test Set Evaluation ($N_{\text{test}} = 6,808$, Evaluated ONCE)
Candidate models were trained on the complete $80\%$ training partition and evaluated once on the isolated test set:

| Model | Feature Set | Test MAE ($) | Test RMSE ($) | Test $R^2$ | Test MAPE | Median AE ($) | MAE Reduction vs. Baseline |
|---|---|---:|---:|---:|---:|---:|---:|
| **Dummy (Median)** | Set A | $\$50,805.56$ | $\$67,659.87$ | $-0.0117$ | $31.46\%$ | $\$40,412.50$ | Baseline |
| **Ridge Regression** | Set A | $\$39,147.25$ | $\$54,123.47$ | $0.3526$ | $23.65\%$ | $\$29,185.12$ | $22.9\%$ |
| **Random Forest** | Set A | $\$37,699.17$ | $\$52,225.92$ | $0.3972$ | $22.60\%$ | $\$27,458.10$ | $25.8\%$ |
| **Gradient Boosting** | Set A | $\$37,445.96$ | $\$52,118.69$ | $0.3997$ | $22.54\%$ | $\$27,150.45$ | $26.3\%$ |
| **XGBoost (Tuned)** | **Set A** | **$\$36,380.64$** | **$\$51,082.06$** | **$0.4233$** | **$21.71\%$** | **$\$26,384.22$** | **28.4%** |
| **XGBoost (Tuned)** | Set C | $\$36,424.84$ | $\$50,986.96$ | $0.4255$ | $21.77\%$ | $\$26,410.15$ | $28.3\%$ |

The winning model (Tuned XGBoost on Feature Set A) achieves an MAE of **$\$36,380.64$** and an $R^2$ of **$0.4233$**, establishing a **$\$14,425$ error reduction ($28.4\%$ improvement)** over the naive median baseline. However, an MAE of $\approx \$36.4\text{k}$ demonstrates that substantial unexplained compensation variance remains.

### 7.4 Feature Set C Value Proposition
Comparing Feature Set A (explicit skills) against Feature Set C (explicit skills + 7 archetypes):
- Test MAE difference is **$+\$44.20$** ($\$36,424.84$ vs. $\$36,380.64$), a relative difference of only **$0.12\%$**.
- **Scientific Verdict:** **Feature Set C provides no practically meaningful improvement over Feature Set A.** Explicit high-resolution skill indicators already supply the principal predictive signal available from observed posting metadata.

---

# 8. Archetype-Level Prediction Error Analysis (RQ3)

Holdout test observations ($N_{\text{test}} = 6,808$) were mapped into archetypes using training K-Means centroids, ensuring zero test data contamination:

| Archetype ID & Key | Test $N$ | Median Salary ($) | Test MAE ($) | Test RMSE ($) | Median AE ($) | Relative MAE (%) | Archetype $R^2$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Cluster 5 (`AI_ML`)** | $490$ | $\$187,250$ | **$\$27,001.58$** | $\$36,135.47$ | $\$21,244.38$ | **$14.42\%$** | $0.4651$ |
| **Cluster 4 (`DATA_BI`)** | $831$ | $\$170,000$ | **$\$31,985.12$** | $\$43,324.62$ | $\$23,319.47$ | **$18.81\%$** | $0.4516$ |
| **Cluster 1 (`DEVOPS_PLAT`)** | $441$ | $\$195,000$ | **$\$32,744.65$** | $\$44,106.48$ | $\$24,377.02$ | **$16.79\%$** | $0.3799$ |
| **Cluster 6 (`SYS_ENG`)** | $420$ | $\$190,000$ | **$\$34,651.44$** | $\$47,760.57$ | $\$27,487.73$ | **$18.24\%$** | $0.4797$ |
| **Cluster 2 (`WEB_FRONT`)** | $863$ | $\$165,650$ | **$\$35,096.50$** | $\$49,908.22$ | $\$26,042.08$ | **$21.19\%$** | $0.3849$ |
| **Cluster 0 (`FOUND_TECH`)** | $2,950$ | $\$170,000$ | **$\$37,663.98$** | $\$51,966.23$ | $\$28,027.32$ | **$22.16\%$** | $0.3930$ |
| **Cluster 3 (`CLOUD_ARCH`)** | $813$ | $\$220,000$ | **$\$46,098.35$** | $\$66,847.94$ | $\$33,333.22$ | **$20.95\%$** | $0.2818$ |

### Statistical Significance:
A non-parametric Kruskal-Wallis test on absolute prediction errors yields:
$$H = \mathbf{88.10}, \quad p = \mathbf{7.53 \times 10^{-17}} \quad (p < 0.001)$$
The null hypothesis of equal error distributions across archetypes is **firmly rejected**.

### Analytical Interpretation:
1. **Lowest Error (`AI_ML`):** Exhibits both the lowest absolute MAE ($\$27,002$) and lowest relative error ($14.42\%$). Highly specialized AI/ML skill requirements (PyTorch, deep learning, LLMs) tightly constrain candidate responsibilities, yielding more uniform market compensation.
2. **Highest Absolute Error (`CLOUD_ARCH`):** Displays the highest absolute MAE ($\$46,098$). However, its median salary is $\$220,000$ (highest across all clusters) and its salary variance is exceptionally wide ($\sigma > \$85\text{k}$). In relative terms ($20.95\%$), its error is comparable to Web Engineering ($21.19\%$), proving that absolute MAE is primarily driven by compensation scale.
3. **Highest Relative Error (`FOUND_TECH`):** Exhibits the highest relative error ($22.16\%$). The elevated relative error is consistent with the heterogeneous, broad nature of generic technical postings, which span entry-level IT support to senior generalist architects.

---

# 9. Research Question Findings (Synthesis)

### RQ1 Synthesis — Skills & Combinations vs. Salary
Triangulating tree split gain, test permutation importance, standardized Ridge coefficients, and observed salary distributions establishes clear empirical associations:
- **Individual Skills:** AI and deep learning competencies (`machine_learning`, `pytorch`, `deep_learning`), cloud platforms (`aws`, `kubernetes`), and compiled systems languages (`golang`, `c++`) display the strongest predictive associations with premium salaries.
- **Skill Profiles:** Postings specifying full specialized stacks command substantial observed differences over single-skill postings: Deep Learning stack (Python + ML + PyTorch) exhibits a median of $\$192.5\text{k}$ vs. $\$165\text{k}$ for general Python; Platform Engineering stack (AWS + Kubernetes + Terraform) exhibits a median of $\$198\text{k}$.
- **Structural Confounding:** Permutation importance proves that career seniority (`Lead / Principal / Executive` impact: $+\$4,374$) and Tier-1 geography (`San Francisco` impact: $+\$1,228$) account for more predictive variance than any single technical skill.

### RQ2 Synthesis — Latent Skill Archetypes
Technology job postings exhibit **recurring and reproducible skill-based structures with moderate separation and substantial overlap ($k = 7$)**:
- Six distinct specialized clusters capture established technology domains (DevOps, Frontend, Multi-Cloud, Data/BI, AI/ML, Systems Engineering).
- However, $49.47\%$ of the skill-bearing population resides in `FOUND_TECH`, a heterogeneous foundational cohort near the PCA origin. Archetypes represent overlapping market segments connected by universal bridge skills (`python`, `sql`), not discrete "natural classes."

### RQ3 Synthesis — Archetype Error Disaggregation
Salary prediction error **differs significantly across archetypes ($p < 0.001$)**:
- Absolute error is strongly influenced by cluster compensation scale and dispersion (Multi-Cloud MAE $\$46.1\text{k}$ vs. AI/ML MAE $\$27.0\text{k}$).
- Relative error reveals that generic, low-skill-count postings (`FOUND_TECH`) suffer from the greatest relative uncertainty ($22.16\%$) due to role ambiguity.

---

# 10. Bias, Variance & Generalization Analysis

Evaluating the winning tuned XGBoost regressor across training and test partitions confirms balanced learning dynamics:
- **Training Error:** $\text{MAE} = \$33,525.35$ | $R^2 = 0.4993$
- **Holdout Test Error:** $\text{MAE} = \$36,380.64$ | $R^2 = 0.4233$
- **Generalization Gaps:** $\Delta \text{MAE} = \mathbf{\$2,855.29}$ ($7.8\%$ relative gap), $\Delta R^2 = \mathbf{0.0760}$.
- **Learning Curves (`07_learning_curve.png`):** As training sample size scales from $5,400$ to $27,228$, validation $R^2$ steadily ascends from $0.37$ to $0.42$, while training $R^2$ descends toward $0.50$. The narrowing gap confirms that the observed train-test error gap is moderate and does not indicate severe overfitting.
- **Validation Curves (`09_validation_curve_xgboost.png`):** Testing tree depth across $[3, 7]$ confirms that validation MAE minimizes at `max_depth = 6`. Depths exceeding 7 induce mild overfitting.

---

# 11. Comprehensive Limitations

A rigorous scientific project must transparently communicate its empirical boundaries:
1. **Salary Disclosure Bias:** Postings with explicit salary ranges are heavily concentrated in US states with pay transparency mandates (California, New York, Washington, Colorado). Employers in transparency jurisdictions may structure salary disclosures differently from non-transparent markets.
2. **Missing Compensation Components:** Job descriptions record base annualized wage ranges, omitting annual equity grants (stock options/RSUs), performance bonuses, signing incentives, and health benefits, which comprise a large share of total compensation in senior engineering roles.
3. **Binary Skill Representation:** Technical skills are represented as binary presence/absence indicators, omitting depth of mastery, tool usage frequency, or required years of practical experience.
4. **Controlled Vocabulary Grain:** The curated 82-skill dictionary groups specialized tools under parent categories (e.g., PyTorch vs. specialized CUDA optimization), missing niche technical skills.
5. **Upper-Tail Scarcity:** Base salaries exceeding $\$400,000$ are empirically sparse in online postings ($< 1\%$), leading to modest underprediction in the extreme right tail.
6. **`FOUND_TECH` Heterogeneity:** The largest discovered cluster ($49.47\%$) is not a cohesive professional specialization but a residual cohort of postings with sparse skill mentions.
7. **PCA Information Loss:** 15 components capture $56.05\%$ of variance; $43.95\%$ of total feature variance remains outside the retained representation.
8. **Observational Confounding:** The study is strictly observational; associations between skills and salaries cannot be interpreted as causal treatment effects.
9. **Geographic Generalization:** Findings reflect the US technology labor market (2024–2026) and cannot be generalized directly to non-US economies or non-technology sectors.

---

# 12. Practical Implications

### For Job Seekers & Career Counselors:
- Specializing in modern artificial intelligence (`machine_learning`, `pytorch`), cloud platform orchestration (`aws`, `kubernetes`, `terraform`), or systems programming (`golang`, `c++`) is associated with premium salary bands.
- However, technical skills alone do not guarantee compensation increases; career leveling (advancing from Mid to Senior or Lead) and metropolitan location exert a larger structural influence on salary than acquiring single isolated tools.

### For Recruiters & Talent Acquisition:
- Skill-based archetypes provide an empirical basis for talent mapping and cross-skilling. Candidates in `DEVOPS_PLAT` and `CLOUD_ARCH` share substantial infrastructure overlap, facilitating cross-functional sourcing.
- Sourcing generalist candidates (`FOUND_TECH`) requires deeper behavioral screening, as low-skill postings display the highest compensation dispersion and role ambiguity.

### For Organizations & Compensation Teams:
- Prediction models achieve a typical percentage error of $\approx 21.7\%$ ($\text{MAE} \approx \$36.4\text{k}$). While valuable for macroeconomic benchmarking and range setting, algorithmic salary models should not be used as deterministic wage-setting engines.
- Subgroup error disaggregation demonstrates that compensation variance differs significantly across technical domains, motivating archetype-aware uncertainty intervals in compensation planning.

---

# 13. Final Conclusion

This investigation provides a rigorous, data-driven synthesis of skill taxonomy, latent archetypes, and compensation modeling in the US technology labor market:
1. Technology job competencies exhibit recurring, interpretable structural patterns that map cleanly onto six modern computing specializations and one foundational residual cohort.
2. Supervised machine learning reliably predicts salary midpoints ($R^2 = 0.4233$, $\text{MAE} = \$36,380.64$), achieving a $28.4\%$ error reduction over naive estimation.
3. Unsupervised archetypes provide powerful descriptive mental models for market navigation, but they provide no incremental predictive value beyond explicit skill vectors in supervised regression.
4. Prediction error is non-uniform across the labor market: specialized AI/ML roles are highly predictable, multi-cloud roles exhibit scale-driven dollar variance, and generic technical roles exhibit the highest relative dispersion.
5. The model captures meaningful labor-market structure, but substantial unexplained variance remains, emphasizing that human capital valuation depends heavily on unobserved factors beyond job posting text.

---

# 14. Reproducibility & Pipeline Integrity

- **Deterministic Seeds:** `random_state = 42` locked across train/test splitting, K-Fold cross-validation, PCA, K-Means, and tree-based regressors.
- **Environment:** Tested and certified under Python 3.13.9, Scikit-learn 1.7.2, XGBoost 3.2.0, Pandas 2.3.3, NumPy 2.2.6.
- **Headless Pipeline Execution:** All outputs, figures, and models can be reproduced from the command line:
  ```bash
  python src/rebuild_phase2_1.py
  python src/run_phase3_eda.py
  python src/run_phase4_1_archetype_correction.py
  python src/run_phase5_experiments.py
  ```
- **Executed Notebooks:** All notebooks (`03_eda.ipynb`, `04_1_archetype_correction.ipynb`, `05_salary_modeling.ipynb`) are fully executed and self-contained.

---

# 15. Future Work

1. **Multimodal NLP Integration:** Incorporating dense semantic text embeddings (e.g., RoBERTa or modern Transformer embeddings) directly from raw job descriptions to capture nuanced responsibilities and experience depth.
2. **Total Compensation Modeling:** Linking job posting disclosures with verified self-reported employee compensation datasets (e.g., equity, stock grants, bonus structures) to model total annual compensation packages.
3. **Longitudinal Market Tracking:** Tracking archetype shift and skill premiums over multi-year macroeconomic cycles to model technology adoption trajectories and automated skill obsolescence.
