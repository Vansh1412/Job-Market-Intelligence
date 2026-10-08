# Executive Summary: Job Market Intelligence
**Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning**  
**Course & Project:** INT234 Predictive Analytics — Academic Task 2  
**Author:** Lead ML Research Engineer, Data Scientist & Statistical Analyst  
**Date:** October 2026 | **Status:** Distinction-Ready Synthesis  

---

### What Was Studied?
This project investigates the latent structural organization of technology skills in online job postings and determines how accurately annualized salaries can be predicted from job characteristics. Specifically, it resolves three empirical research questions:
1. **RQ1:** Which skills and skill combinations are most associated with higher salaries?
2. **RQ2:** Do job postings naturally form meaningful, skill-based job archetypes?
3. **RQ3:** Does salary-prediction error differ systematically across skill-based archetypes?

Additionally, it tests a central machine learning hypothesis: **Does incorporating unsupervised archetype representations improve salary prediction over explicit skill and role features?**

---

### What Data Were Used?
- **Primary Source:** Dataset A (`Tech Job Postings with Parsed Salaries — ATS Direct`, package `jobs-tier1-L-2026-08-01`), selected over Dataset B for its 6.5× volume of technical annual USD salaries, controlled 101-competency vocabulary, and formal `DATASHEET.md` provenance.
- **Data Funnel:** Ingested $394,300$ raw postings $\to$ deduplicated to $335,995$ postings $\to$ filtered to $114,873$ technology-role postings.
- **Populations Analyzed:**
  - *Archetype Discovery Population ($N = 116,830$):* Technology postings containing $\ge 1$ parsed technical skill across 82 curated features. Postings with zero parsed skills ($N = 219,165$, $65.23\%$) were excluded from primary clustering to prevent non-technical distortion and preserved strictly as a diagnostic baseline.
  - *Supervised Modeling Cohort ($N = 34,036$):* Verified technology postings with complete role metadata and non-null annualized USD salaries within $[\$30,000, \$600,000]$ (mean: $\$187,031$, median: $\$180,413$, std: $\$65,753$). Partitioned into 80% Train ($N = 27,228$) and 20% Holdout Test ($N = 6,808$, isolated with `random_state = 42`).

---

### What Was Discovered About Skills and Salaries? (RQ1)
- **Top Salary-Associated Skills:** Machine learning and deep learning frameworks (`machine_learning`, `pytorch`, `deep_learning`), cloud infrastructure (`aws`, `kubernetes`, `terraform`), and compiled systems languages (`golang`, `c++`) display the strongest positive predictive associations with salary across tree split gain, test permutation importance, and standardized Ridge coefficients.
- **Observed Profile Differences:** Specialized skill profiles command substantial descriptive differences: a deep learning profile (Python + ML + PyTorch) exhibits an observed median salary of **$\$192,500$** vs. $\$165,000$ for postings specifying Python without specialized ML skills.
- **Structural Confounding:** Permutation importance demonstrates that career seniority (`Lead / Principal / Executive` impact: $+\$4,374$) and Tier-1 metropolitan markets (`San Francisco` impact: $+\$1,228$) are larger baseline determinants of compensation scale than any single technical skill token.

---

### What Archetypes Were Discovered? (RQ2)
Dimensionality reduction using 15-component Centered Covariance PCA ($56.05\%$ variance explained) and K-Means clustering ($k = 7$) identified **recurring and reproducible skill-based structures with moderate separation and substantial overlap** (stability: Mean $\text{ARI} = 0.7901$, Mean $\text{AMI} = 0.8030$; cross-cohort sensitivity match: $74.51\%$):
1. **`FOUND_TECH` (49.47%, $N = 57,791$, Median $\$170\text{k}$):** Broad, heterogeneous foundational cohort near the PCA origin dominated by sparse skill mentions ($67.56\%$ single-skill, $85.31\% \le 2$ skills).
2. **`DEVOPS_PLAT` (6.52%, $N = 7,614$, Median $\$195\text{k}$):** Cloud-native infrastructure, automated CI/CD, Kubernetes, and Terraform.
3. **`WEB_FRONT` (11.88%, $N = 13,878$, Median $\$165.7\text{k}$):** Modern web engineering, TypeScript, React, and full-stack JavaScript.
4. **`CLOUD_ARCH` (10.83%, $N = 12,657$, Median $\$220\text{k}$):** Enterprise multi-cloud architecture (Azure/AWS/GCP), distributed systems, and security.
5. **`DATA_BI` (10.31%, $N = 12,042$, Median $\$170\text{k}$):** Modern data platform, pipeline warehousing (Snowflake/Spark), and analytics.
6. **`AI_ML` (5.73%, $N = 6,699$, Median $\$187.3\text{k}$):** Deep learning, generative AI, LLM adaptation, and research engineering.
7. **`SYS_ENG` (5.26%, $N = 6,149$, Median $\$190\text{k}$):** Low-level compiled systems (C++/Linux), firmware/embedded, and high-throughput servers.

---

### How Well Could Salaries Be Predicted?
- **Winning Model:** Tuned Extreme Gradient Boosting (`XGBRegressor`, `max_depth = 6`, `learning_rate = 0.10`, `n_estimators = 150`, `subsample = 0.80`, `colsample_bytree = 0.80`, `tree_method = 'hist'`).
- **Holdout Test Set Performance ($N_{\text{test}} = 6,808$, Evaluated ONCE):**
  - **Mean Absolute Error (MAE):** **$\$36,380.64$** (a **$28.4\%$ error reduction** over naive median baseline of $\$50,805.56$)
  - **Root Mean Squared Error (RMSE):** **$\$51,082.06$** (a **$24.5\%$ error reduction** over naive median baseline of $\$67,659.87$)
  - **Coefficient of Determination ($R^2$):** **$0.4233$**
  - **Mean Absolute Percentage Error (MAPE):** **$21.71\%$**
  - **Median Absolute Error:** **$\$26,384.22$**
- **Generalization:** Train MAE ($\$33,525$) vs. Test MAE ($\$36,381$) yields a tight gap of $\Delta = \$2,855$ ($7.8\%$), confirming controlled generalization error with no evidence of severe overfitting.

---

### Does Archetype Membership Improve Prediction?
- **Finding:** **Feature Set C provides no practically meaningful improvement over Feature Set A.**
  - Feature Set A (Explicit Skills, 123 features): Test MAE = **$\$36,380.64$** | Test $R^2 = 0.4233$
  - Feature Set C (Explicit Skills + 7 Archetypes, 130 features): Test MAE = **$\$36,424.84$** | Test $R^2 = 0.4255$
  - Difference: **$+\$44.20$** ($0.12\%$ difference; practically indistinguishable).
- **Takeaway:** Explicit skill vectors and role metadata already supply the principal predictive signal available from observed posting text. Archetypes provide valuable descriptive taxonomy, but redundant predictive information.

---

### Does Prediction Error Differ by Archetype? (RQ3)
- **Statistical Significance:** A Kruskal-Wallis test on absolute prediction errors firmly rejects equal error distributions:
  $$H = \mathbf{88.10}, \quad p = \mathbf{7.53 \times 10^{-17}} \quad (p < 0.001)$$
- **Lowest Error:** **`AI_ML`** displays both the lowest absolute MAE (**$\$27,002$**) and lowest relative error (**$14.42\%$**), consistent with tightly constrained, specialized market compensation.
- **Highest Absolute Error:** **`CLOUD_ARCH`** displays the highest absolute MAE (**$\$46,098$**), primarily driven by elevated compensation scale (median $\$220\text{k}$) and wide market dispersion ($\sigma > \$85\text{k}$). Its relative error ($20.95\%$) is standard.
- **Highest Relative Error:** **`FOUND_TECH`** exhibits the highest relative error (**$22.16\%$**), consistent with role heterogeneity among generic technical postings.

---

### What Are the Major Limitations?
1. **Unexplained Variance:** $R^2 \approx 0.423$ and $\text{MAE} \approx \$36.4\text{k}$ indicate that individual predictions can deviate substantially from actual salaries; unobserved factors (candidate experience, equity grants, negotiation, company prestige) remain uncaptured.
2. **Missing Compensation Components:** Job postings record base salaries, omitting equity packages (RSUs/stock options) and annual bonuses that constitute a major share of senior tech compensation.
3. **Binary Skill Representation:** Indicates skill presence but cannot measure depth of mastery or practical years of experience.
4. **Upper-Tail Scarcity:** Base salaries exceeding $\$400,000$ are empirically sparse, leading to modest right-tail underprediction.

---

### What Are the Practical Implications?
- **For Job Seekers:** Specializing in AI/ML, cloud platform engineering, or systems languages is associated with premium salary bands, but career leveling (Mid $\to$ Senior $\to$ Lead) and geography remain the primary structural drivers of compensation scale.
- **For Recruiters:** Archetypes offer an empirical framework for talent mapping and cross-skilling across related infrastructure stacks, while generalist roles (`FOUND_TECH`) require deeper candidate vetting due to wide compensation dispersion.
- **For Organizations:** Algorithmic salary modeling is valuable for market benchmarking and range setting, but should not be used as a deterministic wage-setting engine. Segment-aware uncertainty intervals should be reported.

---

### What Is the Final Conclusion?
Technical skills strongly structure the technology labor market into six modern engineering specializations and one large foundational residual cohort. Supervised machine learning reliably captures meaningful wage structure ($28.4\%$ error reduction over baseline), but archetype memberships do not improve prediction beyond explicit skill indicators. Prediction errors differ significantly across archetypes, demonstrating that algorithmic compensation modeling encounters varied uncertainty depending on technical specialization and role ambiguity.
