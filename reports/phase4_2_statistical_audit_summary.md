# Phase 4.2: Statistical Audit Summary & Quality Sign-Off
**Project:** INT234 Predictive Analytics — Job Market Intelligence  
**Author:** Lead ML Research Engineer, Statistical Reviewer & Reproducibility Auditor  
**Date:** October 2026  
**Status:** Certified & Frozen  

---

## 1. Executive Summary

Phase 4.2 completed an adversarial statistical and methodological audit of the Phase 4.1 archetype discovery pipeline. Rather than generating new analyses or models, Phase 4.2 audited computed evidence, verified blueprint compliance, calibrated reporting terminology, audited cross-cohort sensitivity, evaluated structural heterogeneity in the largest cluster, and established strict data-leakage controls for Phase 5.

The overall methodology is confirmed to be **statistically defensible, empirically sound, and fully reproducible**.

---

## 2. Audit Findings: What Was Correct vs. What Was Corrected

### What Was Correct
1. **Population Filtering:** Restricting archetype discovery to postings with $\ge 1$ qualifying technical skill ($N = 116,830$) successfully eliminated the artificial zero-skill cluster that dominated the unconstrained corpus.
2. **Covariance PCA Pre-processing:** Centered Covariance PCA (`StandardScaler(with_mean=True, with_std=False)`) correctly preserves empirical skill volume and avoids rare-skill variance distortion inherent in correlation PCA on sparse binary data.
3. **Partition Robustness:** Multi-seed evaluations confirm that K-Means initialization converges reliably to the same geometric centroids (mean $\text{ARI} = 0.7901$, mean $\text{AMI} = 0.8030$).
4. **Data Isolation:** Exploratory cluster assignments remain strictly segregated in `job_archetype_assignments.parquet`; no cluster labels leaked into the supervised modeling dataset.
5. **Artifact Integrity:** All 14 tables, 14 figures, 3 model artifacts, and 2 assignments parquet files match reported metrics exactly.

### What Was Corrected
1. **Eliminated "Optimal k=7" Claims:** Acknowledged that $k=2$ maximizes silhouette (0.3449) and $k=10$ minimizes Davies-Bouldin (1.6054). Re-framed $k=7$ as a **defensible multi-criteria compromise** balancing granular specialization, structural separation, and stability.
2. **Replaced Exaggerated Stability Terminology:** Replaced "highly stable" and "refutes null hypothesis" with **"good-to-strong partition stability across random initializations."**
3. **Calibrated Cross-Cohort Sensitivity Claims:** Struck claims that "identical 7 archetypes replicate cleanly." Replaced with formal empirical metrics: a **74.51% Hungarian matching rate** and **0.8708 mean centroid cosine similarity**.
4. **Corrected Sampling Description:** Replaced "stratified sample" with **"fixed random sample of 25,000 observations without replacement (`random_state=42`)."**
5. **Disclosed FOUND_TECH Heterogeneity:** Formally documented that Cluster 0 (`FOUND_TECH`, 49.5%) is a **foundational residual bucket** where 67.56% of postings have exactly 1 skill and 85.31% have $\le 2$ skills (mean = 1.61).
6. **Refined Zero-Skill Phrasing:** Replaced "65.23% are non-technical jobs" with **"postings with no parsed qualifying technical skills"** to acknowledge unparsed descriptions.
7. **Framed Salary Differences as Descriptive Associations:** Strictly prohibited claiming that clusters "discovered salary tiers" or that cluster membership caused salary differences.
8. **Calibrated RQ2 Language:** Avoided claims of "natural classes," concluding that the data exhibit **recurring and reproducible skill-based structures with moderate separation and substantial overlap**.

---

## 3. Key Methodological Compromises & Limitations

| Analytical Component | Observed Trade-off | Methodological Justification |
|---|---|---|
| **$k=7$ Selection vs. $k=2$** | $k=2$ achieves higher silhouette (0.3449) but clumps 80.6% of jobs into one uninterpretable blob. | $k=7$ is retained to uncover substantive, actionable technology skill specializations. |
| **Retained PCA Components (15 PCs)** | 15 PCs explain 56.05% of variance, leaving 43.95% unrepresented. | Retains major co-occurrence directions ($\lambda \ge 1.0$) while reducing 82 dimensions by 81.7%. |
| **Cluster 0 (`FOUND_TECH`) Dominance** | Cluster 0 contains 49.47% of postings and has high internal diversity. | Reflects real-world ATS postings that specify only 1 or 2 isolated skill tags near the PCA origin. |
| **Silhouette Magnitude (0.2379)** | Lower than the artificial 0.68 from Phase 4. | Reflects authentic overlapping skill bridges (`python`, `sql`, `linux`) in contemporary software engineering. |

---

## 4. Phase 4.2 Quality Gate Summary

- **Population Definition:** PASS
- **Zero-Skill Handling:** PASS
- **PCA Scaling:** PASS (Covariance PCA empirically justified over Correlation PCA)
- **PCA Components:** PASS (15 components, 56.05% variance)
- **K Selection:** PASS (Multi-criteria compromise)
- **k=2 Evaluation:** PASS (Rejected due to severe thematic collapse)
- **Stability:** PASS (Mean ARI = 0.7901, Mean AMI = 0.8030)
- **Silhouette Sampling:** PASS (Fixed random sample, $N=25,000$, seed=42)
- **Cluster Balance:** PASS (Documented and defensible)
- **FOUND_TECH Heterogeneity:** PASS (Formally disclosed as limitation)
- **Salary Sensitivity:** PASS (Formal Hungarian match = 74.51%, centroid cosine = 0.8708)
- **Data Leakage Governance:** PASS (Exploratory labels isolated)
- **Reproducibility:** PASS (100% deterministic)
- **RQ2 Conclusion:** PASS (Calibrated: Supported with moderate separation & substantial overlap)

---

## 5. Official Phase 4.2 Sign-Off

### Phase 4.2 Verdict:
**GREEN — STATISTICALLY AND METHODOLOGICALLY DEFENSIBLE**

### RQ2 Final Answer:
**SUPPORTED, with moderate separation and substantial overlap.**

### Phase 5 Readiness:
**YES — Ready for supervised predictive modeling upon explicit user command.**

### Leakage Protocol Status:
**PASS — Strict cross-validation fold-specific pipeline rules established.**
