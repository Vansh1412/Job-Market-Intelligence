# EMPLOYER RESOLUTION BENCHMARK AUDIT
## Independent Verification of `SYS_EMP_RESOLVER_V2` & The Rule of Three Analysis

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Benchmark Report: `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_BENCHMARK_EVALUATION.md`
- Audit Record: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/EMPLOYER_ENTITY_RESOLUTION_RELIABILITY_AUDIT.md`
- Reconciled Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/employer_resolution_confusion_matrix.csv`
- Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Executive Summary & Forensic Audit Finding

Sprint 3B.3.2 reported that `SYS_EMP_RESOLVER_V2` achieved a **0.00% false merge rate** and asserted that the resolver **"proved a false merge rate < 0.1%."**

This audit confirms that `SYS_EMP_RESOLVER_V2` did indeed achieve **zero false merges** across the test suite, exhibiting exceptional conservative precision. However, this audit determines that the statistical claim of having "proven an error rate < 0.1%" was mathematically invalid due to sample size constraints. The claim is formally retracted and replaced with exact confidence intervals in accordance with the **Rule of Three**.

---

## 2. Benchmark Confusion Matrix Analysis

The benchmark evaluated $N = 100$ gold candidate entity pairs across India, the United States, the United Kingdom, Singapore, and Australia.

### 2.1 Empirical 2x2 Contingency Matrix

```
                      +---------------------------------------+
                      |               ACTUAL                  |
                      |  Same Entity (45)  | Diff Entity (55) |
+---------------------+--------------------+------------------+
| PREDICTED | Match   | TP = 31            | FP = 0           |  Precision = 100.0%
|           | Distinct| FN = 14            | TN = 55          |  NPV = 79.71%
+---------------------+--------------------+------------------+
                        Recall = 68.89%      Specificity = 100%
```

### 2.2 Calculated Performance Metrics

| Metric | Formula | Value | 95% Wilson Score Interval | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Precision (PPV)** | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ | **100.00%** (31/31) | **[88.78% – 100.00%]** | Every proposed merge was an exact legal match. |
| **Recall (Sensitivity)** | $\frac{\text{TP}}{\text{TP} + \text{FN}}$ | **68.89%** (31/45) | **[54.33% – 80.47%]** | 14 difficult aliases were safely left unmerged. |
| **False Merge Rate (FPR)**| $\frac{\text{FP}}{\text{FP} + \text{TN}}$ | **0.00%** (0/55) | **[0.00% – 6.53%]** | Zero distinct entities were merged. |
| **F1 Score** | $\frac{2 \cdot P \cdot R}{P + R}$ | **0.8158** | N/A | High harmonic balance favoring precision over recall. |

---

## 3. Mathematical Proof: The Rule of Three ($N \ge 3,000$)

In statistical quality control and epidemiology (Hanley & Lippman-Hand, 1983), when an event has occurred zero times ($k = 0$) in $n$ independent trials, the upper bound of the 95% confidence interval for the true probability $p$ is approximated by:

$$p_{95\%} \approx \frac{3}{n}$$

More formally, using the exact binomial distribution:
$$P(\text{zero errors in } n \text{ trials}) = (1 - p)^n$$
Setting this probability equal to the significance level $\alpha = 0.05$:
$$(1 - p)^n = 0.05 \implies n \ln(1 - p) = \ln(0.05) \approx -2.99573$$
For small $p$, $\ln(1 - p) \approx -p$, yielding:
$$n \ge \frac{-\ln(0.05)}{p} \approx \frac{2.99573}{p}$$

### Application to `SYS_EMP_RESOLVER_V2`:
1. **Current Sample ($n = 55$ Negative Pairs):**
   $$p_{95\%} \approx \frac{3}{55} \approx 0.0545 \implies \mathbf{5.45\%} \quad (\text{Exact Wilson Upper Bound: } \mathbf{6.53\%})$$
   We can only be 95% confident that the true false merge rate is below **6.53%**, not 0.1%.
2. **Sample Required to Prove $p < 0.001$ (<0.1%):**
   $$n \ge \frac{2.99573}{0.001} = \mathbf{2,996} \approx \mathbf{3,000 \text{ true negative pairs}}$$

**Conclusion:**  
To scientifically prove that the false merge rate is strictly below 0.1%, JOBINTEL must evaluate at least 3,000 verified distinct entity pairs without a single false merge.

---

## 4. Production Readiness & Recommendation

Despite the sample size limitation for extreme claims, `SYS_EMP_RESOLVER_V2` demonstrates exceptional practical safety:
- It prioritizes **zero false merges** over high recall. Leaving an entity unmerged (FN = 14) causes minor deduplication redundancy, whereas merging distinct legal entities (FP) corrupts employer analytics, salary benchmarks, and headcount lineage.
- The system is cleared for controlled staging pilot usage.

### Reconciled Production Claim:
> *"SYS_EMP_RESOLVER_V2 achieved 0.00% false merges across 55 negative benchmark pairs (95% Wilson CI: [0.00%–6.53%]). High-confidence verification of error rates below 0.1% requires expanding benchmark coverage to N >= 3,000 negative pairs."*

---

## 5. Audit Verdict

- **Status:** **RECONCILED — CONDITIONAL GO**
- **Action:** Retract "<0.1%" claim, publish exact Wilson confidence interval `[0.00% - 6.53%]`.
