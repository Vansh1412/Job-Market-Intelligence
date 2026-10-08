# Phase 5 Executive Summary: Salary Prediction & Comparative ML
**INT234 Predictive Analytics — Job Market Intelligence**  
*Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning*

---

### 1. Problem Statement
Can observed job-market technical skills and posting metadata explain salary variation, and does incorporating unsupervised skill-based job archetypes improve predictive accuracy?

---

### 2. Dataset & Population
- **Cohort Source:** Verified technology job postings from the audited Phase 2.1 pipeline (`modeling_dataset.parquet`).
- **Sample Size:** $N = 34,036$ postings with non-null USD annualized compensation boundaries within $[\$30,000, \$600,000]$.
- **Data Partitions:** Strict 80% Training ($N_{\text{train}} = 27,228$) vs. 20% Holdout Test ($N_{\text{test}} = 6,808$, isolated with `random_state = 42`).
- **Target Variable:** `salary_midpoint` (Mean: $\$187,031$, Median: $\$180,413$, Standard Deviation: $\$65,753$).

---

### 3. Best Model & Hyperparameters
- **Winning Algorithm:** Extreme Gradient Boosting Regressor (`XGBRegressor`) with histogram-based tree splitting (`tree_method='hist'`).
- **Selected Hyperparameters:** `max_depth = 6`, `learning_rate = 0.10`, `n_estimators = 150`, `subsample = 0.80`, `colsample_bytree = 0.80`.

---

### 4. Best Feature Set
- **Selected Feature Representation:** **Feature Set A** (123 explicit predictors: role metadata, seniority tiers, metropolitan geography, remote work flag, and 82 standardized binary technical skill indicators).

---

### 5. Quantitative Performance Summary
- **5-Fold Cross-Validation (Training Partition):**
  - CV MAE: **$\$36,072 \pm \$185$**
  - CV RMSE: **$\$49,886 \pm \$412$**
  - CV $R^2$: **$0.4192 \pm 0.0071$**
  - CV MAPE: **$22.12\%$**
- **Holdout Test Set ($N_{\text{test}} = 6,808$, Evaluated ONCE):**
  - Test MAE: **$\$36,380.64$** (a **$28.4\%$ error reduction** over naive median baseline of $\$50,805.56$)
  - Test RMSE: **$\$51,082.06$** (a **$24.5\%$ error reduction** over naive median baseline of $\$67,659.87$)
  - Test $R^2$: **$0.4233$**
  - Test MAPE: **$21.71\%$**
  - Test Median Absolute Error: **$\$26,384.22$**

---

### 6. Key Discovery: Archetype Incremental Value
- **Scientific Finding:** **Feature Set C provides no practically meaningful improvement over Feature Set A.**
- **Empirical Evidence:** Incorporating the 7 fold-safe K-Means archetype indicators (Feature Set C) yields a holdout test MAE of **$\$36,424.84$** vs. **$\$36,380.64$** for Feature Set A ($\Delta \text{MAE} = +\$44.20$, or $0.12\%$).
- **Methodological Synthesis:** Unsupervised archetypes provide valuable descriptive taxonomy and market segmentation, but explicit high-resolution skill indicators already supply the principal predictive signal available from observed posting metadata.

---

### 7. RQ1 — Skill-Salary Associations
- **Top Salary-Associated Skills:** Specialized technical skills such as machine learning (`machine_learning`), deep learning (`pytorch`, `deep_learning`), cloud infrastructure (`aws`, `kubernetes`, `terraform`), and systems languages (`golang`, `c++`) show meaningful observed and model-derived associations with higher salaries.
- **Skill Profiles:** Postings with specialized profiles (e.g., Python + PyTorch + ML at $\$192.5\text{k}$ median vs. $\$165\text{k}$ for general Python roles) display substantial observed salary differences.
- **Macroeconomic Controls:** Non-skill variables remain the largest baseline determinants of compensation scale: `Lead / Principal / Executive` seniority ($+\$4,374$ permutation impact) and Tier-1 tech hubs (`San Francisco`, `New York`, `Seattle`).

---

### 8. RQ2 — Skill-Based Archetypes Context
- Job postings exhibit recurring and reproducible skill-based structures with moderate separation and substantial overlap ($k = 7$ clusters), serving as an effective descriptive taxonomy.

---

### 9. RQ3 — Archetype Error Differences
- **Statistical Significance:** Prediction-error distributions differ significantly across the identified archetypes (Kruskal-Wallis $H = 88.10$, $p = 7.53 \times 10^{-17}$, $p < 0.001$).
- **Lowest-Error Archetype:** **`AI_ML (AI / Machine Learning)`** (Cluster 5, $N = 490$) displays both the lowest absolute error ($\text{MAE} = \mathbf{\$27,002}$) and lowest relative error ($\mathbf{14.42\%}$), consistent with tightly constrained, specialized market compensation bands.
- **Highest Absolute Error Archetype:** **`CLOUD_ARCH (Multi-Cloud)`** (Cluster 3, $N = 813$) exhibits the highest absolute error ($\text{MAE} = \mathbf{\$46,098}$), primarily driven by elevated compensation scale (median $\$220\text{k}$) and wider market dispersion ($\sigma > \$85\text{k}$). Its relative error ($20.95\%$) is standard.
- **Highest Relative Error Archetype:** **`FOUND_TECH (Foundational & Broad)`** (Cluster 0, $N = 2,950$) exhibits the highest relative error ($\mathbf{22.16\%}$), consistent with the heterogeneous, broad nature of generic technical postings.

---

### 10. Major Limitations
1. **Unexplained Variance:** The model explains approximately $42.3\%$ of salary variance ($R^2 \approx 0.423$, $\text{MAE} \approx \$36.4\text{k}$); individual predictions can deviate substantially from actual compensation because unobserved factors (candidate experience, equity grants, funding stage, negotiation) are not captured in job postings.
2. **Text Parsing Resolution:** Binary skill indicators indicate presence but cannot quantify depth of mastery or years of hands-on experience.
3. **Upper-Tail Scarcity:** Extreme compensation observations above $\$400,000$ are empirically sparse, leading to modest underprediction in the extreme right tail.
