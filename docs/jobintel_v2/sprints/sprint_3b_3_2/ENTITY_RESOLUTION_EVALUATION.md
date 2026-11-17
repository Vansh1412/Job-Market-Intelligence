# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 7: ENTITY RESOLUTION EVALUATION REPORT
## Empirical Benchmark Execution, Confusion Matrices, False Merge Analysis & Statistical Power Bounds

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Machine Learning Engineer & Statistical QA Lead  
**Execution Type:** Controlled Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. EMPIRICAL BENCHMARK EXECUTION RESULTS

The 4-tier entity resolution engine was tested against the gold-standard evaluation dataset of **100 real-world candidate pairs** ([employer_entity_resolution_gold.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_entity_resolution_gold.json)).

Two algorithmic configurations were evaluated:
- **Resolver V1 (Baseline):** Naive 4-tier resolver matching registration IDs, cross-border web domains, and normalized names.
- **Resolver V2 (Jurisdiction-Aware):** Constrains domain matching to the same sovereign market and routes parent-subsidiary cross-border domain overlaps to an explicit corporate hierarchy review queue.

```
========================================================================================
EMPIRICAL RESOLUTION BENCHMARK RESULTS (100 LABELLED PAIRS)
========================================================================================
Configuration             TP    FP    TN    FN    Precision    Recall    F1-Score  False Merge (Type I)
Resolver V1 (Baseline)    39     3    52     6      92.86%     86.67%     0.8966    5.45% [1.87% - 14.85%]
Resolver V2 (Refined)     31     0    55    14     100.00%     68.89%     0.8158    0.00% [0.00% -  6.47%]
========================================================================================
```

---

## 2. DETAILED CONFUSION MATRIX & ERROR BREAKDOWN

### 2.1 Category-Level Performance (Resolver V1 vs V2)

| Challenge Category | Pair Count | Ground Truth | V1 Outcome | V2 Outcome | Key Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Formatting & Suffix Variations** | 30 | MATCH | 30 TP, 0 FN | 30 TP, 0 FN | 100% precision and recall; suffix regexes are robust |
| **Trade Name vs. Legal Name** | 15 | MATCH | 9 TP, 6 FN | 1 TP, 14 FN | Trade aliases require dedicated dictionary lookup |
| **Parent vs. Subsidiary** | 15 | DISTINCT | 12 TN, **3 FP** | 15 TN, **0 FP** | V1 falsely merged parent/subsidiary sharing domains |
| **Name Collisions Across Markets** | 20 | DISTINCT | 20 TN, 0 FP | 20 TN, 0 FP | Jurisdiction filtering successfully prevented all collisions |
| **Recruitment Agency vs. Employer** | 10 | DISTINCT | 10 TN, 0 FP | 10 TN, 0 FP | Staffing agency exclusions are 100% effective |
| **Shared ATS Host Domain Traps** | 10 | DISTINCT | 10 TN, 0 FP | 10 TN, 0 FP | ATS domain blacklist (`greenhouse.io`, etc.) 100% effective |
| **Total Benchmark Pairs** | **100** | — | **39 TP, 3 FP** | **31 TP, 0 FP** | **V2 completely eliminates fatal False Merges** |

### 2.2 Forensic Root Cause Analysis of Resolver V1 False Merges (3 FPs)
In Resolver V1, three parent-subsidiary pairs were incorrectly merged as identical entities:
1. `pair_052`: *Microsoft India (R&D) Private Limited* (IN) merged with *Microsoft Corporation* (US) because both use root domain `microsoft.com`.
2. `pair_053`: *Cisco Systems Capital Corporation* (US) merged with *Cisco Systems, Inc.* (US) due to shared domain `cisco.com`.
3. `pair_059`: *GrabTaxi Pte. Ltd.* (SG) merged with *Grab Holdings Inc.* (SG) due to shared domain `grab.com`.

**Impact of Error:** Merging an operating subsidiary into its corporate parent corrupts national workforce data, attributing global revenues and headcounts to a regional development center.

**The Resolver V2 Fix:** Constrained Tier 2 domain matching so that domain matches with divergent normalized names or cross-border market IDs are classified as `POSSIBLE_SUBSIDIARY_REVIEW` rather than auto-merged. This drove False Merges to **exactly zero (0 FP)**.

---

## 3. STATISTICAL POWER ANALYSIS & THE $< 0.1\%$ TARGET

In Sprint 3B.3 Phase 0, the research proposed:
$$\text{False Merge Rate Target: } < 0.1\% \quad (1 \text{ false merge per } 1,000 \text{ pairs})$$

### 3.1 Can a 100-Pair Sample Prove a $< 0.1\%$ False Merge Rate?
**Mathematically, NO.**
- On our benchmark of 100 pairs, there are $N_{neg} = 55$ true negative pairs.
- Resolver V2 observed $FP = 0$ false merges ($0.00\%$).
- Under the **Wilson Score Interval** at 95% confidence:
  $$\text{Upper 95\% Bound} = \frac{0 + \frac{1.96^2}{2 \times 55} + 1.96 \sqrt{\frac{1.96^2}{4 \times 55^2}}}{1 + \frac{1.96^2}{55}} = \mathbf{6.47\%}$$
- Under the **Rule of Three**, when zero events are observed in $N$ trials, the 95% upper bound is approximately:
  $$\text{Upper Bound} \approx \frac{3}{N} = \frac{3}{55} = \mathbf{5.45\%}$$

### 3.2 Scientific Conclusion
Claiming that the $<0.1\%$ target is "achieved" based on a 100-pair sample is statistically invalid.
- To mathematically prove a False Merge Rate $< 0.1\%$ at 95% confidence with zero observed errors requires a minimum sample of:
  $$N_{required} \ge \frac{3}{0.001} = \mathbf{3,000\text{ true negative pairs}}$$
- **Governance Finding:** Resolver V2 achieves an **empirically observed 0.00% false merge rate on the 100-pair pilot benchmark** with a 95% confidence interval of $[0.00\%, 6.47\%]$. Scaling to larger cohorts in Phase 1 will expand the gold standard toward the 3,000-pair statistical power requirement.

---

## 4. FALSE SPLIT RATE & THE RECALL TRADE-OFF

In Resolver V2, eliminating all false merges increased False Splits from 6 to 14 ($FN = 14$, Recall = 68.89%).

### Why Did False Splits Occur?
All 14 false splits occurred in the `TRADE_VS_LEGAL` category:
- Trade name *CommBank* failed to match legal name *Commonwealth Bank of Australia*.
- Trade name *Jio Platforms* failed to match legal entity *Reliance Industries Limited*.
- Trade name *Chase* failed to match *JPMorgan Chase & Co.*.

### Methodological Policy: Prefer False Splits over False Merges
- A **False Split** (Type II Error) keeps one company represented under two separate profiles. This is an inconvenience that can be resolved via an administrative alias table.
- A **False Merge** (Type I Error) merges two distinct companies, corrupting legal liabilities, financial metrics, and layoffs. This destroys platform credibility.
- **Decision:** JobIntel 2.0 permanently prioritizes minimizing False Merges over False Splits. An administrative trade alias table (`data/governance/trade_aliases.json`) will be introduced in Phase 1 to recover recall without compromising precision.
