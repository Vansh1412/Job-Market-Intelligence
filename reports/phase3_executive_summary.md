# Phase 3: Executive Summary — Exploratory Data Analysis & Statistical Profiling
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Supervised Modeling Cohort:** $N = 34,036$ observations $\times$ 102 variables  
**Date:** October 5, 2026  
**Status:** Complete & Signed Off — Phase 4 Ready  

---

### 1. Dataset Dimensions & Population Scope
- **Final Modeling Cohort:** **34,036 job postings** with dual-bound annual USD salaries and verified technical skills.
- **Variables:** **102 columns** (8 metadata predictors, 91 multi-hot skill indicators, 3 strictly isolated salary targets).
- **Population Definition:** Full-time technology positions posted across major enterprise ATS engines with explicit compensation ranges within the defensible boundary of $[\$30,000, \$600,000]$.
- **Data Completeness:** 100% complete across all 99 predictor features and target variables in the modeling dataset. Zero imputation was performed.

---

### 2. Salary Distribution & Transformation
- **Median Annual Salary:** **\$180,372.50**
- **Mean Annual Salary:** **\$187,020.55**
- **Standard Deviation:** **\$65,817.80**
- **Interquartile Range (IQR):** **\$78,130.00** ($Q_1 = \$143,870, Q_3 = \$222,000$)
- **Distributional Skewness:**
  - Raw Midpoint Skewness: **+0.944** (moderate right skewness).
  - Log Midpoint Skewness ($\ln(y)$): **-0.503** (symmetric, near-normal target distribution).
  - *Methodological Note:* Log transformation stabilizes target variance, but residual normality will be formally evaluated post-fitting in Phase 5.

---

### 3. Role Family & Seniority Patterns
- **Dominant Role Families:**
  - *Software Engineer (General):* 19.13% ($N = 6,511$, Median = \$192,775)
  - *ML / AI Engineer:* 17.52% ($N = 5,963$, Median = \$190,000)
  - *Technical Product & PM:* 7.33% ($N = 2,494$, Median = \$194,525)
  - *Data Scientist:* 5.74% ($N = 1,954$, Median = \$175,000)
  - *DevOps / Cloud / Platform:* 4.93% ($N = 1,677$, Median = \$176,250)
  - *Other Tech:* 20.35% ($N = 6,928$, Median = \$152,250) — *retained for specialized long-tail titles*.
- **Top Paying Role Families:**
  - *Engineering Management:* **\$242,500** median ($N = 827$)
  - *Mobile Engineer:* **\$200,000** median ($N = 309$)
  - *Backend Developer:* **\$195,000** median ($N = 684$)
  - *Security Engineer:* **\$195,000** median ($N = 692$)
- **Career Seniority Progression:**
  - Monotonic median climb: *Junior/Entry* (\$105k) $\rightarrow$ *Mid* (\$155k) $\rightarrow$ *Senior* (\$180k) $\rightarrow$ *Lead/Principal/Exec* (\$220k).
  - Seniority accounts for 21.2% of rank variance in compensation ($\epsilon^2 = 0.2120$).

---

### 4. Technical Skill Landscape (RQ1 Evidence)
- **Top 5 Most Frequent Technical Skills:**
  1. `python`: 34.06% prevalence ($N = 11,593$)
  2. `sql`: 19.87% prevalence ($N = 6,764$)
  3. `machine-learning`: 18.42% prevalence ($N = 6,270$)
  4. `aws`: 18.19% prevalence ($N = 6,191$)
  5. `llm`: 15.98% prevalence ($N = 5,439$)
- **Top 5 Salary-Associated Skills (Min Support $N \ge 100$):**
  1. `pytorch`: **\$220,563** median (+22.28% premium over cohort median, $p < 10^{-100}$)
  2. `deep-learning`: **\$215,000** median (+19.20% premium, $p < 10^{-70}$)
  3. `tensorflow`: **\$211,000** median (+16.98% premium, $p < 10^{-35}$)
  4. `scala`: **\$209,750** median (+16.29% premium, $p < 10^{-15}$)
  5. `machine-learning`: **\$207,500** median (+15.04% premium, $p < 10^{-300}$)
- **Top Exploratory Combination Premiums (Pairwise Associations):**
  - `machine-learning + rust`: **\$222,000** median (+23.1% premium, exploratory premium = +\$14,500 over individual medians)
  - `machine-learning + c++`: **\$221,000** median (+22.5% premium, exploratory premium = +\$13,500)
  - `data-engineering + rust`: **\$220,000** median (+22.0% premium, exploratory premium = +\$14,498)
  *(Note: These pairwise salary differences are descriptive associations and should not be interpreted as causal interaction effects because role, seniority, geography, and other confounders have not yet been controlled.)*

---

### 5. Market & Geographic Insights
- **Top Compensating Tech Hubs:**
  - Mountain View, CA: **\$220,000** median ($N = 610$)
  - San Francisco, CA: **\$218,000** median ($N = 4,460$)
  - New York City, NY: **\$200,000** median ($N = 1,146$)
  - San Jose, CA: **\$200,000** median ($N = 412$)
  - Seattle, WA: **\$189,950** median ($N = 570$)
- **Remote Work Model:**
  - Remote Postings: **\$180,000** median ($N = 10,778$, 31.67%)
  - Onsite / Hybrid Postings: **\$180,500** median ($N = 23,258$, 68.33%)
  - Mann-Whitney test: $p = 0.0531$. No statistically significant salary difference was detected at $\alpha = 0.05$.

---

### 6. Research Questions Status

| Research Question | Phase 3 Status | Core Discovery / Evidence |
|---|---|---|
| **RQ1: Skills & Combinations vs Salary** | **Partially Investigated** | Empirical premiums documented for AI/ML frameworks (+17% to +22%) and compiled systems languages (+14% to +16%). Exploratory pairwise combination associations identified. Causal claims avoided pending controlled regression in Phase 5. |
| **RQ2: Skill-Based Archetypes** | **Prepared, Not Answered** | High matrix sparsity (94.88%) and pairwise Jaccard similarity structure show visually distinguishable co-occurrence patterns that motivate formal archetype discovery using PCA and K-Means in Phase 4. Zero clustering algorithms were executed. |
| **RQ3: Error across Archetypes** | **Not Yet Evaluated** | Baseline compensation variance and subgroup distributions established. Rank-based effect sizes calculated (seniority $\epsilon^2 = 0.212$, role family $\epsilon^2 = 0.096$). Cannot be evaluated until predictive models and archetype assignments are completed in Phases 4 & 5. |

---

### 7. Explicit Limitations
1. **Salary Disclosure Bias:** Skewed toward US transparency law jurisdictions (California, New York, Washington).
2. **Confounding in Unadjusted Premiums:** High-paying skills (PyTorch, Rust) are correlated with senior career levels and tier-1 tech metros.
3. **Controlled Tag Grain:** Emerging sub-frameworks default to parent tags in the ATS dictionary.

*Phase 3 is complete. Ready for Phase 4 Archetype Discovery.*
