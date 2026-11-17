# SIX CRITICAL CLAIMS RECONCILIATION
## Forensic Verification of Preceding Sprint Assertions

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Sprint 3B.3.2 Documentation: `docs/jobintel_v2/sprints/sprint_3b_3_2/`
- Sprint 3B.3.2.2 Claims Register: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/prediction_claims.csv`
- Reconciled Claims Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/claims_reconciliation.csv`
- Evaluation Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Executive Reconciliation Summary

In accordance with Section 14 of the sprint mandate, this audit performs an exhaustive, evidence-based forensic re-evaluation of the six critical claims flagged during Sprint 3B.3.2.2.

Every claim is audited against source code, raw data objects, mathematical principles, and runtime infrastructure realities. No claim is accepted on authority.

```
+-------------------------------------------------------------------------------+
|                       SIX CRITICAL CLAIMS SUMMARY AUDIT                       |
+---------+----------------------------------------+----------------------------+
| Claim ID| Description                            | Reconciled Verdict         |
+---------+----------------------------------------+----------------------------+
| CLM-001 | Resolver V2 Error Rate < 0.1%          | UNSUPPORTED (Overstated)   |
| CLM-002 | Evidence Ledger Complete Provenance    | VERIFIED_WITH_LIMITATIONS  |
| CLM-003 | Render Free Tier Zero OOM Risk         | MISLEADING (Unbounded Risk)|
| CLM-004 | 100% Empirical Lineage Guarantee       | VERIFIED_WITH_LIMITATIONS  |
| CLM-005 | 100% Skill Extraction Precision        | VERIFIED_WITH_LIMITATIONS  |
| CLM-006 | Title Mapping 95% Probability          | UNSUPPORTED (Uncalibrated) |
+---------+----------------------------------------+----------------------------+
```

---

## 2. Deep-Dive Forensic Audit of Each Claim

### Claim CLM-001: Entity Resolver V2 Error Rate < 0.1%
- **Original Claim Text:** *"Resolver V2 achieved 0.00% false merge rate and proved false merge rate < 0.1%."* (Sprint 3B.3.2 Final Report, Line 150)
- **Source Inspection:** Evaluated against `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_BENCHMARK_EVALUATION.md`. The benchmark examined 100 entity pairs, of which 55 were true negative pairs (distinct legal entities).
- **Statistical Truth:** Across 55 negative trials, 0 false merges were observed. The 95% Wilson score confidence interval is `[0.00% - 6.53%]`.
- **Mathematical Reality:** Under the Rule of Three, proving an error rate strictly below 0.1% ($p < 0.001$) at 95% confidence requires observing 0 errors across at least **3,000 true negative pairs** ($N \ge -\ln(0.05) / 0.001 \approx 2,996$).
- **Reconciled Verdict:** **UNSUPPORTED**.
- **Mandatory Replacement:** *"Resolver V2 achieved 0.00% false merges across 55 negative benchmark pairs (95% Wilson CI: [0.00% - 6.53%]). High-confidence verification of error rates below 0.1% requires benchmark expansion to N >= 3,000 negative pairs."*

---

### Claim CLM-002: Cryptographic SHA-256 Evidence Ledger Scope
- **Original Claim Text:** *"Cryptographic SHA-256 evidence ledger verifies complete provenance across all 28 anchor employers and observations."* (Sprint 3B.3.2 Employer Provenance Audit, Line 45)
- **Source Inspection:** Evaluated against `docs/jobintel_v2/sprints/sprint_3b_3_2/evidence_ledger.json`. The ledger records SHA-256 hashes of primary regulatory filings, source PDFs, and raw JSON/HTML snapshots.
- **Statistical Truth:** The ledger successfully guarantees the bit-level immutability of the ingested *source documents*. However, granular row-level entity observation hashing (linking each normalized employer record back to its specific byte-range or parsed entry) is scheduled for Sprint 3B.3.3.
- **Reconciled Verdict:** **VERIFIED_WITH_LIMITATIONS**.
- **Mandatory Replacement:** *"Cryptographic SHA-256 ledger verifies immutability of primary source documents and bulk raw JSON/HTML snapshots. Row-level observation hashing will be introduced in Sprint 3B.3.3."*

---

### Claim CLM-003: Render Free Tier Zero OOM Risk
- **Original Claim Text:** *"In-memory storage on Render Free tier operates with zero OOM risk."* (Sprint 3B.3.2 Employer Storage Benchmark, Line 80)
- **Source Inspection:** Evaluated against `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_STORAGE_MEMORY_BENCHMARK.md` and `render.yaml`. Render free instances provide 512 MB of RAM. The baseline python process with 100 in-memory employer profiles consumes ~68 MB RSS (~0.84 MB dataset heap).
- **Runtime Reality:** While static heap consumption is negligible, returning an unpaginated JSON payload across multiple concurrent API requests causes significant transient memory spikes during serialization and buffer allocation. Under concurrent traffic spikes, memory can exceed 512 MB, triggering OS `SIGKILL` (OOM).
- **Reconciled Verdict:** **MISLEADING**.
- **Mandatory Replacement:** *"In-memory dataset heap (~0.84 MB for 100 employers) presents low baseline RAM usage, but unbounded JSON responses and concurrent query spikes present operational OOM risks on Render Free tier (512 MB RAM). Mandatory pagination (default 25, max 50) is required."*

---

### Claim CLM-004: 100% Empirical Data Lineage Guarantee
- **Original Claim Text:** *"Guarantees 100% empirical data lineage with zero synthetic fallback data."* (`src/backend/services/market_service.py`, Line 9)
- **Source Inspection:** Inspected backend routing logic in `src/backend/services/market_service.py` and `src/backend/routers/market.py`.
- **System Reality:** The system code strictly enforces a gating rule: when statutory data for a jurisdiction (e.g., UK vacancy flow) is unverified or licensing is ambiguous, the backend returns `null` or explicit `withheld` status rather than synthetic approximations.
- **Reconciled Verdict:** **VERIFIED_WITH_LIMITATIONS**.
- **Mandatory Replacement:** *"Enforces strict rejection of synthetic fallbacks for statutory demand metrics; missing or unverified data returns explicit null/withheld status in compliance with sovereign data governance policies."*

---

### Claim CLM-005: 100% Precision on Skill Extraction
- **Original Claim Text:** *"5-token contextual co-occurrence window achieves 100% precision on skill extraction."* (Sprint 3B.3.2 Skill Extraction Evaluation, Line 60)
- **Source Inspection:** Inspected `docs/jobintel_v2/sprints/sprint_3b_3_2/skill_extraction_benchmark.csv`.
- **Statistical Truth:** The 5-token contextual guard achieved 100% accuracy (20/20) on the *adversarial unit test suite*. Generalizing this to all production job postings ignores wide 95% Wilson confidence intervals (`[83.89% - 100.00%]`) and real-world natural language anomalies.
- **Reconciled Verdict:** **VERIFIED_WITH_LIMITATIONS**.
- **Mandatory Replacement:** *"Contextual co-occurrence filter achieved 100% accuracy on the 20 adversarial benchmark test cases. Production vacancy text requires sample size reporting (N) on all skill frequency charts."*

---

### Claim CLM-006: Title Mapping 95% Confidence Equals 95% Probability
- **Original Claim Text:** *"Confidence scores of 0.95 represent 95% mapping probability."* (Sprint 3B.3.2 Job Title Mapping Pilot, Line 35)
- **Source Inspection:** Inspected similarity matching calculation in `SYS_OCC_MAPPER`.
- **Statistical Truth:** Heuristic match scores represent monotonic token/Levenshtein similarity, not true posterior probabilities. Raw scores exhibit an ECE of 5.87% and overconfidence in the 0.70–0.85 band.
- **Reconciled Verdict:** **UNSUPPORTED**.
- **Mandatory Replacement:** *"Heuristic mapping confidence is an uncalibrated similarity indicator. Display scores as heuristic match indices until independent temperature scaling is implemented."*

---

## 3. Governance Conclusion

Every identified claim has been reconciled with exact empirical evidence. Claims CLM-001 and CLM-006 are formally retracted from platform documentation and replaced with statistically sound descriptions. Claims CLM-002, CLM-004, and CLM-005 are preserved with precise bounding disclosures, and CLM-003 is mitigated via mandatory pagination specifications.
