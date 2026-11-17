# JOBINTEL 2.0 — PROPOSED EVALUATION TARGETS & BENCHMARK MATRIX
## Forward-Looking Reliability Targets, Task-Specific Objectives & Validation Framework

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Quantitative Evaluation Lead  
**Scope:** Planning & Target Architecture for Future Model Cycles (Sprint 3B.3.3+)  

---

## 1. EVALUATION TARGET MATRIX (PLANNING TARGETS ONLY)

The following targets are **forward-looking planning targets**, NOT historical measured numbers. They define the statistical thresholds required before a model or heuristic pipeline can be upgraded to production tier status.

```
+----------------------------------------------------------------------------------------------------+
| JOBINTEL PROPOSED EVALUATION TARGET MATRIX                                                         |
+--------------------------+-----------------------+--------------------+----------------------------+
| Intelligence Task        | Primary Metric Target | Secondary Target   | Mandatory Evaluation Guard |
+--------------------------+-----------------------+--------------------+----------------------------+
| Occupation Classification| 85% – 95% Overall Acc | Macro F1 >= 0.90   | Denominator includes       |
| (Taxonomy Mapping)       |                       |                    | unmapped fallback cases.   |
| Employer Entity          | Precision >= 98.0%    | False Merge Rate   | Asymmetric cost function:  |
| Resolution               | (Recall >= 65.0%)     | FPR <= 1.0% (N=3k) | Type I error minimization. |
| Contextual Skill         | 85% – 90% F1 Score    | Specificity >= 95% | Adversarial short-token    |
| Extraction               | (Aspirational target) | on colloquial text | co-occurrence guard.       |
| Salary Compensation      | No universal accuracy | Median AE < 15%    | Residual prediction band;  |
| Regression               | (MAE < ₹3.5 LPA / $35k| R2 >= 0.50         | no fake single-point quotes|
| Demand Intelligence      | 100% Provenance Trace | Gated Releases     | UK publication gate active;|
| Observations             | (Statutory filings)   | (Zero leakage)     | zero synthetic momentum.   |
| Probability Confidence   | Expected Calib Error  | Brier Score <= 0.05| Temperature / Platt scaling|
| Calibration              | ECE <= 0.0500         | on binary tasks    | on independent holdout.    |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 2. TASK-SPECIFIC TARGET RATIONALES & DEFICIENCIES

### 2.1 Occupation Classification (`SYS_OCC_MAPPER`)
- **Proposed Target:** 85% – 95% Overall Accuracy across diverse, uncurated job titles.
- **Current Measured Reality:** Achieves **97.00% accuracy** on the 100-title gold benchmark with **0.0% misclassification** and **3.0% unmapped fallback**.
- **Assessment:** Exceeds the proposed aspiration. The system is production-ready for the 12 canonical occupations.

### 2.2 Employer Entity Resolution (`SYS_EMP_RESOLVER_V2`)
- **Proposed Target:** Precision $\ge 98.0\%$ with False Merge Rate (FPR) $\le 1.0\%$ verified on $N \ge 3,000$ pairs.
- **Current Measured Reality:** Achieves **100.0% precision** and **0.0% false merges** on $N = 100$ pairs (95% Wilson CI: `[0.00% - 6.53%]`).
- **Deficiency / Gap:** The sample size ($N = 55$ true negatives) is statistically insufficient to prove that the population FPR is $\le 1.0\%$ or $< 0.1\%$.
- **Action Plan:** Expand the gold resolution benchmark to 3,000 true negative pairs during Sprint 3B.3.3.

### 2.3 Contextual Skill Extraction (`SYS_SKILL_EXTRACTOR`)
- **Proposed Target:** 85% – 90% F1 score across unstructured job descriptions.
- **Current Measured Reality:** Achieved **100.0% accuracy** on 20 hand-crafted adversarial test phrases.
- **Deficiency / Gap:** The 20-phrase test proves rule correctness on tested patterns, but does not measure real-world recall across messy recruiter jargon.
- **Action Plan:** Construct an independent, human-annotated 500-posting corpus to establish true production F1.

### 2.4 Salary Compensation Regression (`MOD_IN_SALARY_HGBR`, `MOD_US_SALARY_XGB`)
- **Proposed Target:** Median Absolute Error $< 15\%$ of median salary, with $R^2 \ge 0.50$.
- **Current Measured Reality:**
  - India: Median AE is ₹2.08 LPA (~17% of median salary), $R^2 = 0.5798$ (Passes variance target).
  - USA: MAE is $36,380, $R^2 = 0.4233$ (Slightly below $R^2 = 0.50$ aspiration).
- **Usability Verdict:** Usable with restrictions. Because base salary in the USA has immense unobserved variance (company tier, specific startup equity trade-offs), an $R^2$ of 0.42 is typical for job board data. The model is fully authorized for benchmark ranges with appropriate disclaimer banners.

---

## 3. GOVERNANCE PROTOCOL FOR UNDER-PERFORMING MODELS

If a predictive model falls below its proposed target:
1. **Never alter or massage the test metrics** to artificially meet the target.
2. **Document the performance gap** in the model card, detailing the specific archetype or geographic segments driving error.
3. **Attach user-facing caveat tags** and widen the displayed prediction interval.
4. **Implement an automated fallback** routing low-confidence instances to human-in-the-loop review.
