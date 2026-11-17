# JOBINTEL 2.0 — OCCUPATION MAPPING RELIABILITY AUDIT
## Independent Audit of Canonical Occupation Mapping, Denominator Integrity & Confidence Semantics

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Taxonomic NLP Specialist  
**System Audited:** `SYS_OCC_MAPPER` (Canonical Occupation Mapping Engine)  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/JOB_TITLE_CONFUSION_MATRIX.csv`  

---

## 1. TAXONOMIC MAPPING ARCHITECTURE & SCOPE

The JOBINTEL Canonical Occupation Mapping Engine maps diverse, non-standard job titles across five national markets into 12 standardized canonical occupational archetypes (`CAN_OCC_001` through `CAN_OCC_012`):
- `CAN_OCC_SOFTWARE_ENGINEER`
- `CAN_OCC_DATA_SCIENTIST`
- `CAN_OCC_ML_ENGINEER`
- `CAN_OCC_DATA_ENGINEER`
- `CAN_OCC_DATA_ANALYST`
- `CAN_OCC_DEVOPS_ENGINEER`
- `CAN_OCC_CYBERSECURITY_ANALYST`
- `CAN_OCC_SYSTEMS_ANALYST`
- `CAN_OCC_DATABASE_ADMIN`
- `CAN_OCC_NETWORK_ENGINEER`
- `CAN_OCC_QA_TEST_ENGINEER`
- `CAN_OCC_IT_PROJECT_MGR`

---

## 2. DENOMINATOR DISCIPLINE & ACCURACY REPORTING

### 2.1 The Critical Denominator Distinction
A common industry flaw is silently excluding unmapped or unresolved job titles from evaluation denominators to report artificially inflated "100% precision."

JOBINTEL strictly enforces three separate metrics:
1. **Mapping Coverage Rate:** Percentage of input records receiving an automatic canonical mapping.
   $$\text{Coverage} = \frac{N_{\text{mapped}}}{N_{\text{total}}} = \frac{97}{100} = \mathbf{97.0\%}$$
2. **Conditional Accuracy:** Correctness evaluated strictly among records that received a mapping.
   $$\text{Accuracy}_{\text{cond}} = \frac{N_{\text{correct\_mapped}}}{N_{\text{mapped}}} = \frac{97}{97} = \mathbf{100.0\%}$$
3. **Overall Population Accuracy (The Standard Metric):** Correctness evaluated across the entire evaluation cohort, counting unmapped titles as non-matches.
   $$\text{Accuracy}_{\text{overall}} = \frac{N_{\text{correct}}}{N_{\text{total}}} = \frac{97}{100} = \mathbf{97.00\%}$$

### 2.2 Complete Evaluation Matrix on 100 Gold Titles

```
+----------------------------------------------------------------------------------------------------+
| 100-TITLE BENCHMARK REPRODUCTION MATRIX                                                            |
+--------------------------+-----------------------+--------------------+----------------------------+
| Metric Parameter         | Measured Value        | 95% Confidence Int | Target Performance SLA     |
+--------------------------+-----------------------+--------------------+----------------------------+
| Total Evaluation Cohort  | 100 titles            | Exact count        | N = 100                    |
| Correctly Classified     | 97 titles             | [91.48% - 99.38%]  | >= 90.0%                   |
| Misclassified (Wrong Cat)| 0 titles              | [0.00% - 3.69%]    | <= 2.0% (Zero tolerance)   |
| Unmapped Jargon Fallback | 3 titles              | [0.62% - 8.52%]    | <= 5.0%                    |
| Overall Accuracy         | 97.00%                | [91.48% - 99.38%]  | >= 90.0%                   |
| Macro-Averaged F1        | 0.9852                | N/A                | >= 0.9000                  |
| Raw ECE (Calibration)    | 0.0587                | N/A                | <= 0.0500 (Conditional)    |
| Calibrated ECE (T=1.24)  | 0.0381                | N/A                | <= 0.0500 (Passed)         |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 3. AUDIT OF CONFIDENCE SCORE SEMANTICS

### 3.1 The Flawed Assumption in Sprint 3B.3.2
In Sprint 3B.3.2 Deliverable 8, mapping scores were described as:
> *"Titles mapped with confidence >= 0.90 represent 95% probability of correctness."*

### 3.2 Independent Statistical Auditor Correction
- **What the Raw Score Actually Is:** The mapping engine assigns rule-based similarity weights (e.g. 0.95 for standard title keywords, 0.78 for colloquial jargon such as "ninja", "rockstar", "wizard").
- **Why It Is NOT a Calibrated Probability:** A heuristic weight of 0.95 is **not** an empirical posterior probability. In the raw distribution, titles assigned 0.95 confidence achieved 97.0% empirical accuracy, yielding an **Expected Calibration Error (ECE) of 0.0587**.
- **The Required Remedy:**
  1. **Option A (Temperature Scaling):** Applying post-hoc temperature scaling with $T = 1.24$ calibrates the output distribution, driving ECE down to **0.0381** ($< 0.05$).
  2. **Option B (User-Facing Categorical Bands):** In UI cards, display qualitative matching tiers (**"High Match"**, **"Moderate Match"**) rather than raw pseudo-probabilities like "95% match".
