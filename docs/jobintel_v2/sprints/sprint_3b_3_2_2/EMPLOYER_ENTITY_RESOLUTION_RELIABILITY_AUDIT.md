# JOBINTEL 2.0 — EMPLOYER ENTITY RESOLUTION RELIABILITY AUDIT
## Independent Statistical Audit of Entity Matching, Operational Decision States & False Merge Error Costs

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Data Governance Auditor  
**System Audited:** `SYS_EMP_RESOLVER_V2` (Employer Entity Resolution Engine V2)  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/ENTITY_RESOLUTION_CONFUSION_MATRIX.csv`  

---

## 1. ASYMMETRIC ERROR-COST DYNAMICS IN ENTITY MATCHING

In employer intelligence, **Type I errors (False Merges) and Type II errors (False Splits) have fundamentally unequal operational costs**:

```
====================================================================================================
ERROR-COST MATRIX IN EMPLOYER ENTITY RESOLUTION
====================================================================================================
Error Type      Failure Mode                                    Business & Legal Consequence
----------------------------------------------------------------------------------------------------
False Merge     Two distinct sovereign entities incorrectly    CATASTROPHIC:
(Type I Error)  collapsed into one unified record               - Corrupts statutory headcount disclosures.
                (e.g., merging Microsoft India into Microsoft   - Confounds local regulatory compliance.
                Corporation US).                                - Destroys sovereign payroll analytics.
                                                                - Creates misleading executive profiles.
----------------------------------------------------------------------------------------------------
False Split     A single company's regional profile left as a   BENIGN & RECOVERABLE:
(Type II Error) distinct record rather than merged with parent  - Retains regional entity integrity.
                (e.g., treating GrabTaxi SG as separate entity).- User sees distinct local profile.
                                                                - Can be manually reconciled in review.
====================================================================================================
```

Because False Merges represent a catastrophic data governance failure, the resolver architecture must prioritize **Precision and Zero False Merges above raw Recall**.

---

## 2. THREE OPERATIONAL OUTCOMES (THE DECISION TRIAGE ENGINE)

The platform rejects naive binary thresholding. Entity resolution evaluates pairs into three distinct operational states:

1. **`AUTO_MATCH` (Automated Identity Union):**
   - **Criteria:** Exact match on sovereign registration identifier (ABN, CIK, CRN, UEN, CIN) OR exact verified domain match with identical normalized legal names within the *same sovereign market*.
   - **Operational Action:** Automatically merges profiles into an authoritative unified entity.
2. **`MANUAL_REVIEW` (Human-in-the-Loop Corporate Hierarchy Triage):**
   - **Criteria:** Shared root domain across different sovereign markets (`mkt_a != mkt_b`) OR shared root domain with divergent legal names (e.g. `cisco.com` between Cisco Systems Inc and Cisco Systems Capital Corp) OR high phonetic similarity without matching registration IDs.
   - **Operational Action:** Profiles remain separate; linked via `RELATION_PARENT_SUBSIDIARY` or `POSSIBLE_DUPLICATE` review queues.
3. **`NO_MATCH` (Distinct Entities):**
   - **Criteria:** Distinct registration identifiers, distinct primary domains, or presence on the ATS Host Blacklist (`greenhouse.io`, `lever.co`).
   - **Operational Action:** Maintained as completely separate, independent corporate entities.

---

## 3. INDEPENDENT BENCHMARK REPRODUCTION & METRIC DISCIPLINE

Resolver V2 was evaluated on the 100-pair adversarial gold benchmark ([employer_entity_resolution_gold.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_entity_resolution_gold.json)):

```
+----------------------------------------------------------------------------------------------------+
| RESOLVER V2 INDEPENDENT REPRODUCTION SCORECARD                                                     |
+--------------------------+-----------------------+--------------------+----------------------------+
| Metric Parameter         | Measured Value        | 95% Wilson CI      | Operational Assessment     |
+--------------------------+-----------------------+--------------------+----------------------------+
| Benchmark Sample Size    | 100 candidate pairs   | Exact sample       | N = 100                    |
| True Positives (TP)      | 31 pairs              | N/A                | Correctly resolved matches |
| False Positives (FP)     | 0 pairs (ZERO MERGES) | N/A                | 0 false merges achieved    |
| True Negatives (TN)      | 55 pairs              | N/A                | Correctly isolated distinct|
| False Negatives (FN)     | 14 pairs              | N/A                | Routed to Manual Review    |
| Pairwise Precision (PPV) | 100.00%               | [88.78% - 100.00%] | High confidence matches    |
| Pairwise Recall (Sens)   | 68.89%                | [54.33% - 80.47%]  | Conservative tradeoff      |
| False Merge Rate (FPR)   | 0.00%                 | [0.00% - 6.53%]    | Type I Error = 0 / 55      |
| F1 Score                 | 0.8158                | N/A                | Balanced safety score      |
+--------------------------+-----------------------+--------------------+----------------------------+
```

### 3.1 Auditor Correction on Sample Size and "0.1% Error Claims"
- In Sprint 3B.3.2, narrative text claimed that Resolver V2 had *"proved a false merge rate < 0.1%"*.
- **The Statistical Reality:** Proving that an error rate $p < 0.001$ with 95% confidence when observing zero errors requires at least **$N \ge 3,000$ true negative pairs** under the binomial Rule of Three ($N \ge -\ln(0.05) / 0.001 \approx 2,996$).
- On the current sample of $N = 55$ true negatives, the Wilson score interval establishes an upper bound of **$< 6.53\%$**, not $< 0.1\%$.
- **Mandated Standard:** Sprint 3B.3.3 must not claim population error rates below 0.1% until a formal 3,000-pair benchmark has been executed and verified.
