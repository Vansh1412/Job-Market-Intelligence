# JobIntel: Future Research & Experimental Roadmap

**Document:** `reports/future_experiments.md`  
**Phase:** Phase 7 Final Production Hardening & Distinction Audit  
**Status:** Frozen Research Log — No Live Modification Permitted  

---

## 1. Governance & Freeze Compliance Notice

In strict adherence to the project charter:
> *"The objective of Phase 7 is NOT to improve machine-learning models... Retraining, refitting, hyperparameter tuning, feature modification, or replacing frozen models is strictly prohibited. If you identify a potentially better ML approach: DO NOT IMPLEMENT IT. Record it in `reports/future_experiments.md`."*

The research hypotheses and architectural enhancements documented below represent candidate future investigations conceived during model validation, error analysis, and cross-market synthesis.

---

## 2. Candidate Experimental Hypotheses

### Experiment 1: Two-Stage Hurdle Regressor for Upper-Tail Compensation
* **Current Limitation:** Single `HistGradientBoostingRegressor` predicts `salary_midpoint_inr` via $\log(1+y)$ across all tiers. Holdout error scales sharply at higher compensation:
  * Overall: $\text{MAE} = ₹3.71\text{ LPA}$
  * Subgroup $\ge 20\text{ LPA}$: $\text{MAE} \approx ₹8.06\text{ LPA}$ ($N=335$ cohort postings)
  * Subgroup $\ge 40\text{ LPA}$: $\text{MAE} \approx ₹31.12\text{ LPA}$ ($N=54$ cohort postings)
* **Proposed Architecture:** A two-stage hurdle/compound model:
  * *Stage 1:* Calibrated binary classifier predicting $\mathbb{P}(\text{Salary} \ge 20\text{ LPA} \mid X)$.
  * *Stage 2:* Specialized extreme-value regressor or Pareto tail quantile regressor trained specifically on upper-quartile senior postings.
* **Expected Benefit:** Mitigates the regression-to-the-mean shrinkage effect without distorting entry/mid-level predictions.

---

### Experiment 2: Dense Semantic Embedding Representations (Sentence-BERT / GTE)
* **Current Limitation:** Both USA ($M=82$) and India ($M=284$) utilize binary one-hot / tokenized skill presence indicators. This ignores linguistic context, domain depth, seniority qualifiers within text, and synonym overlap.
* **Proposed Architecture:** Ingest raw job title and description text into pre-trained transformers (e.g., `sentence-transformers/all-mpnet-base-v2` or `gte-large`), yielding 768-dimensional dense semantic vectors. Concatenate dense text embeddings with structured metadata (city, experience).
* **Expected Benefit:** Captures latent technical seniority and holistic role requirements beyond exact dictionary matches.

---

### Experiment 3: Probabilistic / Soft Archetype Assignment via Gaussian Mixture Models
* **Current Limitation:** Hard assignment via spherical K-Means ($k=7$ USA, $k=6$ India). Real-world candidates often possess hybrid skill sets spanning multiple disciplines (e.g. 50% Full-Stack, 50% Cloud/DevOps).
* **Proposed Architecture:** Fit Gaussian Mixture Models (GMM) with full or tied covariance matrices in the PCA feature space. Emit soft posterior probabilities:
  $$\gamma_{ik} = \mathbb{P}(Z_i = k \mid X_i)$$
* **Expected Benefit:** Enables multi-archetype affinity scoring, continuous transition modeling, and better uncertainty quantification for interdisciplinary professionals.

---

### Experiment 4: Tech-Specific Purchasing Power Parity (PPP) Hedonic Deflators
* **Current Limitation:** Cross-market analysis intentionally preserves currency isolation (USD vs INR) to prevent misleading conclusions from naive nominal exchange rates.
* **Proposed Architecture:** Formulate an empirical hedonic price index calibrated to software engineering consumption baskets (housing in tech hubs like SF Bay Area vs Bengaluru, tech hardware, private healthcare, taxes).
* **Expected Benefit:** Permits academically sound purchasing-power comparisons without crude macroeconomic FX conversions.

---

### Experiment 5: Explainable Boosting Machines (EBMs) / Neural Additive Models (NAMs)
* **Current Limitation:** XGBoost and HistGB require post-hoc TreeSHAP calculations for local feature attributions, adding inference overhead.
* **Proposed Architecture:** Train InterpretML Explainable Boosting Machines (EBM) with exact generalized additive formulas:
  $$g(\mathbb{E}[y]) = \beta_0 + \sum f_i(x_i) + \sum f_{ij}(x_i, x_j)$$
* **Expected Benefit:** Delivers glass-box interpretability with zero TreeSHAP runtime latency and exact pairwise interaction discovery.

---

## 3. Summary Table

| ID | Proposed Experiment | Targeted Limitation | Estimated Complexity | Justification for Deferral |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | Two-Stage Hurdle Regressor | Upper-tail MAE scaling ($\ge 20$ LPA) | Medium | Requires refitting and altering frozen production pipeline. |
| **EXP-02** | Dense S-BERT Embeddings | Binary skill sparsity | High | Requires re-processing gigabytes of raw unstructured text descriptions. |
| **EXP-03** | GMM Soft Archetypes | Hard boundary K-Means assignment | Low-Medium | Alters validated $k=7$ and $k=6$ cluster schema. |
| **EXP-04** | Tech-Calibrated PPP Index | FX vs purchasing power divergence | Medium | External macroeconomic dataset integration required. |
| **EXP-05** | Explainable Boosting Machines | Post-hoc SHAP computational overhead | Medium | Preserves validated XGBoost & HistGB baseline superiority. |

---

*This document is certified frozen. All suggestions must remain in this backlog until post-submission production iterations.*
