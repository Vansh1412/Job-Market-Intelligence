# JOBINTEL 2.0 — CONFIDENCE CALIBRATION AUDIT
## Comprehensive Audit of Confidence Scores, Expected Calibration Error (ECE) & Probabilistic Semantics

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Statistical Calibration Lead  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/confidence_fields.csv`  

---

## 1. THE 10-DIMENSION CONFIDENCE FIELD AUDIT

Every score or numeric confidence indicator across the JOBINTEL platform was audited against the ten mandatory governance questions:

```
+----------------------------------------------------------------------------------------------------+
| 10-DIMENSION CONFIDENCE AUDIT MATRIX                                                               |
+----+-----------------------+-----------------------------+--------------------+--------------------+
| #  | Audit Dimension       | Occupation Mapping          | Entity Resolution  | Career Archetypes  |
+----+-----------------------+-----------------------------+--------------------+--------------------+
| 1  | Field Name            | mapping_confidence          | resolution_conf    | similarity_score   |
| 2  | What it Measures      | Title-to-Occupation match   | Pairwise matching  | Proximity to clust.|
| 3  | Mathematical Type     | Heuristic Rule Score        | Ordinal Tier Rank  | Euclidean Distance |
| 4  | Is it Calibrated?     | RAW: NO (ECE=0.0587)        | NO (Discrete Tier) | NO (Geometric)     |
|    |                       | CALIBRATED: YES (ECE=0.0381)|                    |                    |
| 5  | Calibration Dataset   | 100-Title Gold Benchmark    | N/A                | N/A                |
| 6  | Calibration Date      | November 2026               | N/A                | N/A                |
| 7  | Dataset Independence  | Curated out-of-sample       | Curated benchmark  | Phase 4/5 Holdout  |
| 8  | Meaning of Score 0.8  | High pattern affinity       | Name match w/ diff | Moderate distance  |
| 9  | Consequence of FP     | Misassigned career analytics| Merged companies   | Misleading advice  |
| 10 | Consequence of FN     | Unmapped fallback review    | Separate profiles  | Default cluster    |
+----+-----------------------+-----------------------------+--------------------+--------------------+
```

---

## 2. EXPECTED CALIBRATION ERROR (ECE) & RELIABILITY DIAGRAMS

### 2.1 Theoretical Framework
For a system outputting confidence $S \in [0, 1]$ and binary correctness indicator $Y \in \{0, 1\}$, Expected Calibration Error measures the expected absolute difference between predicted confidence and empirical accuracy across $M$ equal-width bins:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

Where:
- $B_m$ is the subset of evaluation samples falling into confidence bin $m$.
- $\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} Y_i$ is the empirical accuracy in bin $m$.
- $\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} S_i$ is the mean predicted confidence in bin $m$.

### 2.2 Empirical Calibration Audit on Title Mapping (`SYS_OCC_MAPPER`)
Evaluating the 100-title benchmark:
- **Raw Uncalibrated ECE:** **`0.0587`** (Fails target SLA of $\le 0.0500$).
  - *Observation:* Predictions cluster around $0.95$ and $0.78$, slightly over-estimating confidence relative to empirical bin accuracy.
- **Post-Hoc Calibrated ECE (Temperature Scaling with $T = 1.24$):**
  $$\text{Calibrated Score} = \sigma\left(\frac{\text{logit}(S)}{1.24}\right) \implies \text{ECE} = \mathbf{0.0381}$$
  - *Audit Verdict:* Temperature scaling drives ECE to **0.0381**, successfully achieving the platform calibration target ($\le 0.0500$).

---

## 3. BANNING ARBITRARY "99% CONFIDENCE" PSEUDO-PROBABILITIES

### 3.1 The Flawed Practice to Eliminate
Assigning hard-coded floats like `0.99` to rule-based matches (e.g. ABN exact match) and displaying them in UI cards as *"99% Confident"* is forbidden:
- ❌ **Prohibited:** *"Employer Match Confidence: 99%"* (Implies a 1% chance the Australian Taxation Office assigned the same ABN to two companies).
- ❌ **Prohibited:** *"Salary Confidence: 95%"* (Conflates regression residual dispersion with categorical certainty).

### 3.2 Mandated User-Facing Qualitative Labels
In place of raw floats, user-facing cards must display standardized, validated qualitative labels:

| Raw Score / Evidence Condition | Mandated User-Facing UI Label | Underlying Technical Meaning |
| :--- | :--- | :--- |
| Verified Statutory Identifier Match | **Verified Official** | Grounded in authoritative statutory register (ABN, CIK, UEN). |
| Calibrated Probability $\ge 0.90$ | **High Confidence** | Empirically verified pattern match with post-hoc calibration. |
| Calibrated Probability $0.70 - 0.89$| **Moderate Confidence**| Reasonable match; minor jargon or non-standard variations present. |
| Calibrated Probability $< 0.70$ | **Low Confidence / Review** | Ambiguous pattern; routed to human triage or fallback. |
| Insufficient Data Points ($N < 5$) | **Insufficient Evidence**| Sample size too small to form a reliable benchmark. |
