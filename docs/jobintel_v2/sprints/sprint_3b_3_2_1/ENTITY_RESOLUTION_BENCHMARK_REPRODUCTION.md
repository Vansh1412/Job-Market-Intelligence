# SPRINT 3B.3.2.1 — DELIVERABLE 6
# ENTITY RESOLUTION BENCHMARK REPRODUCTION
## Statistical Reproduction of Resolver V1 vs. V2, Confusion Matrices & Wilson Score Analysis

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Statistical Validation Engineer, Data Architect  
**Benchmark Dataset:** `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_entity_resolution_gold.json`  
**Structured Matrix:** `docs/jobintel_v2/sprints/sprint_3b_3_2_1/ENTITY_RESOLUTION_CONFUSION_MATRIX.csv`  

---

## 1. INDEPENDENT BENCHMARK REPRODUCTION RESULTS

An independent execution of the 100-pair entity resolution benchmark was conducted on Python 3 using the preserved gold standard dataset.

Two algorithmic configurations were reproduced:
- **Resolver V1 (Baseline):** 4-tier engine with naive domain matching.
- **Resolver V2 (Refined):** Enforces Sovereign Market Isolation, ATS Host Blacklisting, and routes domain matches with divergent normalized names or cross-border markets to a corporate hierarchy queue (`POSSIBLE_SUBSIDIARY_REVIEW`).

```
====================================================================================================
INDEPENDENT BENCHMARK REPRODUCTION SCORECARD (100 LABELLED PAIRS)
====================================================================================================
Metric                          Resolver V1 (Baseline)  Resolver V2 (Refined)   Definition / Formula
====================================================================================================
Total Benchmark Pairs (N)       100                     100                     Total sample size
True Positive Pairs (Actual +)  45                      45                      TP + FN in Gold Truth
True Negative Pairs (Actual -)  55                      55                      FP + TN in Gold Truth
Positive Predictions (Pred +)   42                      31                      TP + FP
Negative Predictions (Pred -)   58                      69                      TN + FN
True Positives (TP)             39                      31                      Correct match declarations
False Positives (FP)            3 (FALSE MERGES)        0 (ZERO FALSE MERGES)   Distinct entities merged
True Negatives (TN)             52                      55                      Correct distinct declarations
False Negatives (FN)            6                       14                      Matching entities split
Precision (PPV)                 92.86%                  100.00%                 TP / (TP + FP)
Recall (Sensitivity)            86.67%                  68.89%                  TP / (TP + FN)
Specificity (TNR)               94.55%                  100.00%                 TN / (TN + FP)
Pairwise False Positive Rate    5.45%                   0.00%                   FP / (TN + FP) [Type I Error]
False Discovery Rate (FDR)      7.14%                   0.00%                   FP / (TP + FP)
F1 Score                        0.8966                  0.8158                  2 * (P * R) / (P + R)
95% Wilson Score CI on FPR      [1.87% - 14.85%]        [0.00% - 6.53%]         Wilson Score Interval
====================================================================================================
```

---

## 2. CATEGORY-BY-CATEGORY ERROR ANALYSIS

The 100 pairs are divided across six challenge categories:

| Challenge Category | Pair Count | Ground Truth | Resolver V1 Outcome | Resolver V2 Outcome | Forensic Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Formatting & Suffix Variations** | 30 | MATCH | 30 TP, 0 FN | 30 TP, 0 FN | Legal suffix stripping (`Pty Ltd`, `Inc`, `PLC`) is 100% robust. |
| **Trade Name vs. Legal Name** | 15 | MATCH | 9 TP, 6 FN | 1 TP, 14 FN | Divergent names route to review queue (Recall reduced to preserve Precision). |
| **Parent vs. Subsidiary** | 15 | DISTINCT | 12 TN, **3 FP** | 15 TN, **0 FP** | V1 falsely merged parent/sub on domain; V2 routes to hierarchy queue. |
| **Name Collisions Across Markets** | 20 | DISTINCT | 20 TN, 0 FP | 20 TN, 0 FP | Market isolation successfully prevents all cross-market collisions. |
| **Recruitment Agency vs. Employer** | 10 | DISTINCT | 10 TN, 0 FP | 10 TN, 0 FP | Staffing keywords and missing registry IDs prevent false merges. |
| **Shared ATS Host Domain Traps** | 10 | DISTINCT | 10 TN, 0 FP | 10 TN, 0 FP | ATS domain blacklist (`greenhouse.io`, etc.) 100% effective. |
| **Total** | **100** | — | **39 TP, 3 FP** | **31 TP, 0 FP** | **Resolver V2 eliminates all fatal False Merges.** |

---

## 3. STATISTICAL POWER & THE MATHEMATICAL REALITY OF ZERO ERRORS

### 3.1 What Does Zero Observed Errors Establish?
In the 100-pair benchmark, Resolver V2 achieved **0 false positives among 55 true negative pairs** ($k = 0, n = 55$).
Applying the Wilson score confidence interval formula with continuity correction:
$$\text{Upper 95\% Bound} = \frac{z^2}{n + z^2} = \frac{1.96^2}{55 + 1.96^2} = \frac{3.8416}{58.8416} \approx \mathbf{6.53\%}$$

**What this establishes:**
We can assert with 95% statistical confidence that Resolver V2's true population false merge rate on this distribution of candidate pairs is **less than 6.53%**.

**What this does NOT establish:**
It does **NOT** prove that the false merge rate is $< 0.1\%$ ($< 0.001$).

### 3.2 Proof of Sample Size Required to Prove Error Rate $< 0.1\%$
Under the binomial distribution with zero observed errors, the one-sided upper $(1 - \alpha)$ confidence bound is given by the Rule of Three:
$$P(\text{No errors in } N \text{ trials}) = (1 - p)^N \ge \alpha \implies N \ln(1 - p) \ge \ln(\alpha)$$
Using the small-$p$ approximation $\ln(1 - p) \approx -p$:
$$-N p \approx \ln(\alpha) \implies N \ge \frac{-\ln(\alpha)}{p}$$
For a 95% confidence level ($\alpha = 0.05$) and target error rate $p = 0.001$ ($0.1\%$):
$$N \ge \frac{-\ln(0.05)}{0.001} = \frac{2.9957}{0.001} \approx \mathbf{3,000\text{ true negative pairs}}$$

**Statistical Verdict:**
Any claim that Resolver V2 has been "proven" to achieve $<0.1\%$ false merge rate is mathematically false given $N = 55$ true negatives. To statistically substantiate a $<0.1\%$ error rate, the benchmark suite must be expanded to at least **3,000 true negative candidate pairs**.

---

## 4. SOVEREIGN MARKET ISOLATION TRADEOFF ANALYSIS

Sovereign Market Isolation enforces that two records cannot be automatically merged unless their `market_id` matches.

- **Benefit:** Completely eliminates false merges where regional subsidiaries share a corporate domain with an overseas parent (e.g. `Microsoft India` vs. `Microsoft Corp`).
- **Limitation (The Recall Penalty):** In legitimate cross-border scenarios where a single sovereign entity operates in multiple jurisdictions without separate incorporation, Resolver V2 will refuse to merge them, yielding a False Negative.
- **Architectural Assessment:** For a labour market and employer intelligence platform, **Type I errors (false merges) are catastrophic** (corrupting sovereign payroll, headcount, and regulatory compliance data), whereas **Type II errors (false splits) are benign** (presenting regional entities as separate operating units). Resolver V2's trade-off of Precision (100.0%) over Recall (68.9%) is architecturally sound.
