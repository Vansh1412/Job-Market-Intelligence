# Phase 5 Model Card: Tuned XGBoost Salary Regressor
**INT234 Predictive Analytics — Job Market Intelligence**  
*Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning*

---

## 1. Model Details
- **Model Name:** Extreme Gradient Boosting Regressor (`XGBRegressor`) — Tuned Architecture
- **Model Version:** 1.0.0 (Phase 5 Production-Frozen Baseline)
- **Model Family:** Gradient Boosted Decision Trees (Histogram-based partitioning, `tree_method='hist'`)
- **Task:** Supervised salary regression
- **Framework & Libraries:** `xgboost` (v3.2.0), `scikit-learn` (v1.7.2), `numpy` (v2.2.6), `pandas` (v2.3.3)
- **Developer:** Lead ML Research Engineer & Data Scientist (Antigravity)
- **Date:** October 2026
- **License / Governance:** Academic Task 2 Research Use; strictly governed holdout evaluation.

---

## 2. Intended Use
- **Primary Intended Use:** Academic and analytical salary estimation and labor-market research, predicting the expected market compensation midpoint (`salary_midpoint`, in USD) for technology sector job postings based on parsed technical skills, seniority tier, role family, metropolitan location, and remote work model.
- **Secondary Intended Use:** Benchmarking the incremental predictive contribution of skill-based job archetypes discovered through unsupervised learning (PCA + K-Means) relative to raw explicit skill indicators.
- **Target Audience:** Labor market analysts, compensation researchers, career counselors, and technical hiring managers seeking empirical salary benchmarks.

---

## 3. Not Intended For (Out-of-Scope Uses)
- **Employment Decisions & Automated Hiring:** This model must not be used to make employment decisions, screen candidates, or filter applicants.
- **Individual Compensation Setting:** This model must not be used to unilaterally determine, set, or cap compensation decisions affecting individuals or negotiate contracts without human oversight.
- **Individualized Salary Negotiation Guarantees:** Model outputs represent aggregate statistical midpoints, not guaranteed compensation for an individual.
- **Causal Policy Inference:** Feature weights, tree split gains, and permutation importance values reflect **correlational associations**, not causal wage premiums. Possessing a skill does not causally guarantee a salary increment of that exact magnitude.
- **Non-US / Non-Tech Labor Markets:** The model is trained on United States tech job postings ($30k–$600k USD). It is invalid for non-US currency markets, non-tech industries (e.g., healthcare, retail, construction), or executive C-suite equity compensation packages.

---

## 4. Target Variable Specification
- **Target Name:** `salary_midpoint`
- **Definition:** Continuous arithmetic midpoint of annualized salary boundaries:
  $$\text{salary\_midpoint} = \frac{\text{salary\_min} + \text{salary\_max}}{2}$$
- **Currency & Scale:** United States Dollars (USD), ranging between $\$30,000$ and $\$600,000$.
- **Target Distribution ($N = 34,036$):**
  - Minimum: $\$30,000.00$
  - 25th Percentile ($Q_1$): $\$143,900.00$
  - Median ($Q_2$): $\$180,412.50$
  - Mean ($\mu$): $\$187,030.73$
  - 75th Percentile ($Q_3$): $\$222,000.00$
  - Maximum: $\$600,000.00$
  - Standard Deviation ($\sigma$): $\$65,752.68$
  - Skewness: $+0.9436$ (mild right-tail skewness)
  - Kurtosis: $+2.5080$ (moderate leptokurtic distribution)

---

## 5. Training Data & Partitioning
- **Total Population:** $N = 34,036$ verified technology job postings derived from the audited Phase 2.1 pipeline.
- **Training Population:** $N_{\text{train}} = 27,228$ ($80.0\%$).
- **Holdout Test Population:** $N_{\text{test}} = 6,808$ ($20.0\%$).
- **Random Seed:** Locked at `random_state = 42`.
- **Holdout Isolation Protocol:** The holdout test set remained strictly uninspected during exploratory modeling, cross-validation, feature set selection, and hyperparameter tuning. Only **ONE final evaluation** was conducted on the frozen model.

---

## 6. Feature Set & Input Representation
The model utilizes **Feature Set A** (123 input features), combining explicit role metadata and technical skills:
1. **Seniority Tier (5 one-hot indicators):** Intern, Junior / Entry, Mid / Unspecified, Senior, Lead / Principal / Executive.
2. **Role Family (18 one-hot indicators):** Backend Developer, Data / BI Analyst, Data Engineer, Data Scientist, DevOps / Cloud / Platform, Embedded & Hardware, Engineering Management, Frontend Developer, Full-Stack Developer, ML / AI Engineer, Mobile Engineer, Other Tech, QA / SDET, Security Engineer, Software Engineer, Solutions & Architecture, Systems & Network Engineer, Technical Product & PM.
3. **Geographic City (16 one-hot indicators):** Boston, Chicago, Costa Mesa, Denver, Hawthorne, Long Beach, Los Angeles, Mountain View, New York, New York City, Other, San Francisco, San Jose, Seattle, Toronto, Washington.
4. **Work Arrangement (1 binary indicator):** `is_remote` (True/False).
5. **Skill Breadth (1 continuous indicator):** `num_skills` (Total parsed technical skills).
6. **Technical Skills (82 binary indicators):** Standardized Taxonomy D skills (e.g., `skill_python`, `skill_aws`, `skill_machine_learning`, `skill_kubernetes`, `skill_sql`, `skill_pytorch`, etc.).

---

## 7. Preprocessing & Leakage Safeguards
- **Strict Fold-Safe Transformations:** The implemented pipeline contains no identified target or archetype leakage: learned transformations are fitted within training folds, and the holdout test set is isolated until final evaluation.
- **Target Quarantine:** Columns such as `salary_min`, `salary_max`, `salary_band`, `log_salary`, and `job_id` are strictly quarantined from the predictor matrix.
- **Exploratory Archetype Isolation:** The precomputed unsupervised cluster labels from Phase 4 were **never joined** into the predictive dataset. In Feature Set C benchmarking, PCA and K-Means ($k=7$) were refit inside each fold, and validation/test instances were assigned using training centroids only.

---

## 8. Cross-Validation & Hyperparameter Tuning
- **Validation Scheme:** 5-Fold Cross-Validation on the training partition ($N_{\text{train}} = 27,228$).
- **Optimal Hyperparameters (Selected via Controlled Search):**
  - `n_estimators`: 150
  - `max_depth`: 6
  - `learning_rate`: 0.10
  - `subsample`: 0.80
  - `colsample_bytree`: 0.80
  - `tree_method`: `hist` (Histogram-based optimization)
  - `random_state`: 42
  - `n_jobs`: -1
- **Cross-Validation Performance:**
  - Mean CV MAE: **$\$36,072 \pm \$185$**
  - Mean CV RMSE: **$\$49,886 \pm \$412$**
  - Mean CV $R^2$: **$0.4192 \pm 0.0071$**
  - Mean CV MAPE: **$22.12\%$**

---

## 9. Final Holdout Test Performance ($N_{\text{test}} = 6,808$)
The final model was fitted on the full 80% training partition and evaluated once on the isolated test set:
- **Mean Absolute Error (MAE):** **$\$36,380.64$** (28.4% improvement over naive median baseline of $\$50,805.56$)
- **Root Mean Squared Error (RMSE):** **$\$51,082.06$** (24.5% improvement over naive median baseline of $\$67,659.87$)
- **Coefficient of Determination ($R^2$):** **$0.4233$**
- **Mean Absolute Percentage Error (MAPE):** **$21.71\%$**
- **Median Absolute Error:** **$\$26,384.22$**

---

## 10. Bias-Variance & Generalization Diagnostics
- **Training Partition Error:** MAE = $\$33,525.35$, RMSE = $\$46,309.53$, $R^2 = 0.4993$.
- **Holdout Test Partition Error:** MAE = $\$36,380.64$, RMSE = $\$51,082.06$, $R^2 = 0.4233$.
- **Generalization Gaps:**
  - $\Delta \text{MAE} = \$2,855.29$ ($7.8\%$ relative gap)
  - $\Delta R^2 = 0.0760$
- **Diagnostic Conclusion:** The relatively small train-to-test error gap indicates controlled generalization error and no evidence of severe overfitting. Learning curves demonstrate asymptotic convergence between training and validation scores as sample size scales.

---

## 11. Subgroup & Archetype Performance (RQ3)
Prediction accuracy was disaggregated across the seven skill-based archetypes assigned via training centroids:
1. **Cluster 5 (AI / Machine Learning):** $N = 490$ | MAE = **$\$27,002$** | RMSE = $\$36,135$ | Rel MAE = **$14.42\%$** | $R^2 = 0.4651$
2. **Cluster 4 (Data & Analytics):** $N = 831$ | MAE = **$\$31,985$** | RMSE = $\$43,325$ | Rel MAE = **$18.81\%$** | $R^2 = 0.4516$
3. **Cluster 1 (DevOps & Cloud):** $N = 441$ | MAE = **$\$32,745$** | RMSE = $\$44,106$ | Rel MAE = **$16.79\%$** | $R^2 = 0.3799$
4. **Cluster 6 (Systems & Backend):** $N = 420$ | MAE = **$\$34,651$** | RMSE = $\$47,761$ | Rel MAE = **$18.24\%$** | $R^2 = 0.4797$
5. **Cluster 2 (Frontend & Web):** $N = 863$ | MAE = **$\$35,096$** | RMSE = $\$49,908$ | Rel MAE = **$21.19\%$** | $R^2 = 0.3849$
6. **Cluster 0 (Foundational & Broad):** $N = 2,950$ | MAE = **$\$37,664$** | RMSE = $\$51,966$ | Rel MAE = **$22.16\%$** | $R^2 = 0.3930$
7. **Cluster 3 (Multi-Cloud):** $N = 813$ | MAE = **$\$46,098$** | RMSE = $\$66,848$ | Rel MAE = **$20.95\%$** | $R^2 = 0.2818$

**Statistical Comparison:** A Kruskal-Wallis test on absolute prediction errors yields $H = 88.10$, $p = 7.53 \times 10^{-17}$ ($p < 0.001$). Prediction-error distributions differ significantly across archetypes. `CLOUD_ARCH`'s higher absolute MAE is primarily consistent with higher salary scale and dispersion (median $\$220\text{k}$), whereas `FOUND_TECH` displays higher relative error consistent with role heterogeneity.

---

## 12. Methodological Strengths & Limitations

### Strengths:
1. **High Interpretability:** Combines non-linear gradient boosting with comprehensive permutation importance and tree split gain metrics.
2. **Methodological Rigor:** The pipeline contains no identified target or archetype leakage across cross-validation folds and holdout sets.
3. **Empirical Robustness:** Achieves direct dollar precision ($\sim 21.7\%$ typical percentage error) across diverse tech disciplines.

### Limitations:
1. **Salary Disclosure Bias:** Postings with transparent salary ranges may differ systematically from postings without disclosed compensation.
2. **Missing Equity/Bonus Compensation:** Job postings omit equity packages (stock options/RSUs), performance bonuses, and sign-on incentives, which comprise a large portion of senior tech compensation.
3. **Binary Skill Representation:** Technical skills are represented as binary indicators (present/absent), omitting depth of mastery or tool usage frequency.
4. **No Direct Measurement of Years/Depth of Experience:** Postings specify required experience in text, but individual applicant tenure and candidate capability remain unobserved.
5. **Geographic and Company Confounding:** High-paying tech hubs (San Francisco, New York) and well-funded tech firms account for substantial variation not explained by skill tokens alone.
6. **Upper-Tail Scarcity:** Observations with compensation above $\$400,000$ are empirically sparse, leading to modest underprediction in the extreme right tail.
7. **Imperfect Role Taxonomy:** Broad role family buckets can encompass heterogeneous job functions.
8. **Substantial Prediction Error:** An MAE of approximately $\$36\text{k}$ means that individual salary predictions can still deviate substantially from observed ground truth.
