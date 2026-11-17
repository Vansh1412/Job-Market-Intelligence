# CONFIDENCE CALIBRATION REPRODUCTION AUDIT
## Independent Verification of Temperature Scaling & ECE Claims

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Evaluator: `docs/jobintel_v2/sprints/sprint_3b_3_2/JOB_TITLE_MAPPING_PILOT.md`
- Audit Record: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/CONFIDENCE_CALIBRATION_AUDIT.md`
- Reconciled Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/calibration_reconciliation.csv`
- Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Background & The Claim of 95% Confidence (CLM-006)

Sprint 3B.3.2 stated that an occupation match with a similarity score of 0.95 corresponds to a **"95% probability of correct mapping."**

In statistical machine learning, uncalibrated similarity scores, cosine distances, or raw softmax outputs rarely match true empirical probabilities. Sprint 3B.3.2.2 demonstrated that raw heuristic matching scores yielded an Expected Calibration Error (ECE) of **0.0587** (5.87%), and demonstrated that applying temperature scaling ($T = 1.24$) reduced ECE to **0.0381** (3.81%).

This audit independently examines whether this temperature scaling procedure is statistically valid and reproducible.

---

## 2. Expected Calibration Error (ECE) Formulation & Results

Expected Calibration Error groups predictions into $M = 10$ equally spaced confidence bins $B_m$ and measures the weighted absolute difference between average confidence $\text{conf}(B_m)$ and empirical accuracy $\text{acc}(B_m)$:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 2.1 Raw vs. Temperature-Scaled ECE (100 Benchmark Titles)

| Configuration | Temperature ($T$) | Sample Size ($N$) | Raw ECE | Calibrated ECE | Calibration Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Heuristic Score** | $T = 1.00$ | 100 | **0.0587** (5.87%) | 0.0587 | Overconfident in $[0.70 - 0.85]$ band |
| **Fitted Temperature Scaling** | $T = 1.24$ | 100 | 0.0587 | **0.0381** (3.81%) | **FITTED_ON_EVAL_SAMPLE** |
| **Independent Target Benchmark**| $T = 1.24$ | $N \ge 500$ | TBD | TBD | **REQUIRES_INDEPENDENT_SET** |

### 2.2 Bin-by-Bin Calibration Analysis
- In the raw model, predictions with confidence scores between 0.70 and 0.85 had an empirical accuracy of only 74%, resulting in an average overconfidence of $\approx 6\%$.
- Dividing logits by $T = 1.24$ softens the distribution, shifting the confidence in this bin down to 0.75, which closely matches the observed 74% empirical accuracy.

---

## 3. Critical Methodological Finding: In-Sample Calibration Bias

While temperature scaling successfully lowered the measured ECE from 5.87% to 3.81%, this audit identifies a critical methodological limitation:

> **The temperature parameter $T = 1.24$ was optimized and evaluated on the exact same 100 benchmark titles.**

In accordance with `JOBINTEL-STD-PRED-001`, evaluating calibration on the training or optimization set introduces optimistic bias. A parameter fitted to 100 points may overfit the specific distribution of those 100 titles.

### Mandatory Remediation for Sprint 3B.3.3:
1. **Split-Set Calibration Protocol:**
   - Establish an independent calibration set of at least 500 diverse job titles.
   - Fit temperature scaling or isotonic regression solely on the calibration set.
   - Evaluate final ECE on a disjoint test set.
2. **Interim UI Display Guardrail:**
   - Heuristic scores must **not** be presented to users as "probabilities" or "% likelihood".
   - Scores must be labeled as:
     > *"Match Confidence Score: 88/100 (Heuristic similarity index; not a formal probability)."*

---

## 4. Audit Verdict

- **Status:** **PARTIALLY REPRODUCED / REQUIRES INDEPENDENT CALIBRATION SET**
- **Action:** Retract CLM-006 claim of calibrated 95% probability. Enforce heuristic labeling in UI pending independent calibration split.
