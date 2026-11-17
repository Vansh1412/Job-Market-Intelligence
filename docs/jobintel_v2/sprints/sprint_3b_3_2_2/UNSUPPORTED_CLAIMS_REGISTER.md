# JOBINTEL 2.0 — UNSUPPORTED CLAIMS REGISTER
## Formal Register of Overstated Claims, Certainty Language & Remediation Directives

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Product Integrity Lead  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/prediction_claims.csv`  

---

## 1. CLAIMS AUDIT OVERVIEW

A comprehensive audit of documentation, codebases, and interface strings identified six primary instances of unsupported certainty, statistical overstatement, or misleading performance claims.

```
+----------------------------------------------------------------------------------------------------+
| UNSUPPORTED CLAIMS REGISTER SUMMARY                                                                |
+---------+---------------------------+------------------------+------------+------------------------+
| Claim ID| Originating File          | Category               | Risk Level | Audit Verdict          |
+---------+---------------------------+------------------------+------------+------------------------+
| CLM-001 | SPRINT_3B3_2_FINAL_REPORT | Model Performance Claim| HIGH       | UNSUPPORTED            |
| CLM-002 | EMPLOYER_PROVENANCE_AUDIT | Provenance Scope Claim | MEDIUM     | VERIFIED_W_LIMITATIONS |
| CLM-003 | STORAGE_BENCHMARK_REPORT  | Infrastructure Safety  | HIGH       | MISLEADING             |
| CLM-004 | market_service.py         | Lineage Guarantee      | LOW        | VERIFIED_W_LIMITATIONS |
| CLM-005 | SKILL_EXTRACTION_REPORT   | NLP Precision Claim    | MEDIUM     | VERIFIED_W_LIMITATIONS |
| CLM-006 | JOB_TITLE_MAPPING_PILOT   | Confidence Semantics   | HIGH       | UNSUPPORTED            |
+---------+---------------------------+------------------------+------------+------------------------+
```

---

## 2. DETAILED CLAIM-BY-CLAIM REMEDIATION DOSSIER

### 2.1 Claim CLM-001: Entity Resolution Population Error Rate
- **Location:** `docs/jobintel_v2/sprints/sprint_3b_3_2/SPRINT_3B3_2_FINAL_AUDIT_REPORT.md` (Line 150)
- **Original Claim:** *"Resolver V2 achieved 0.00% false merge rate and proved false merge rate < 0.1%"*
- **Supporting Evidence:** 100-pair benchmark contained 55 true negative pairs; 0 false merges were observed.
- **Audit Risk:** High. Stating that an error rate is "proven to be $<0.1\%$" on a sample of 55 instances is mathematically false ($N \ge 3,000$ required).
- **Mandated Replacement:** *"Resolver V2 achieved 0.00% false merges across 55 negative pairs in the benchmark (95% Wilson CI: [0.00% - 6.53%]). Proving error rate < 0.1% requires N >= 3,000 true negative pairs."*
- **Code Change Required:** No (Documentation only).

### 2.2 Claim CLM-002: Cryptographic Evidence Ledger Scope
- **Location:** `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_PROVENANCE_AUDIT.md` (Line 45)
- **Original Claim:** *"Cryptographic SHA-256 evidence ledger verifies complete provenance across all 28 anchor employers and observations."*
- **Supporting Evidence:** `employer_evidence_ledger.csv` contains 8 SHA-256 hashes for raw bulk snapshots and 4 single corporate filings.
- **Audit Risk:** Medium. Creates the impression that every individual profile row has an immutable cryptographic hash.
- **Mandated Replacement:** *"Evidence ledger verifies cryptographic integrity for primary statutory source documents and bulk snapshots; individual row-level entity hashing will be introduced in Sprint 3B.3.3."*
- **Code Change Required:** No (Documentation only; feature scheduled for Sprint 3B.3.3).

### 2.3 Claim CLM-003: Render Free Tier OOM Immunity
- **Location:** `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_STORAGE_MEMORY_BENCHMARK.md` (Line 80)
- **Original Claim:** *"In-memory storage on Render Free tier operates with zero OOM risk."*
- **Supporting Evidence:** 28 employers consume 241 KB heap; 100 employers extrapolate to 0.84 MB.
- **Audit Risk:** High. Ignores request concurrency, response JSON serialization buffers, and memory fragmentation on a 512 MB container.
- **Mandated Replacement:** *"In-memory dataset heap (~0.84 MB for 100 employers) presents low baseline risk, but large unpaginated JSON serialization responses and concurrent query spikes present operational risk without pagination."*
- **Code Change Required:** Yes (Mandate pagination parameters `limit`/`offset` on endpoints in Sprint 3B.3.3).

### 2.4 Claim CLM-004: 100% Empirical Data Lineage Guarantee
- **Location:** `src/backend/services/market_service.py` (Line 9)
- **Original Claim:** *"Guarantees 100% empirical data lineage with zero synthetic fallback data."*
- **Supporting Evidence:** Data pipeline enforces strict null-checks and statutory source verification.
- **Audit Risk:** Low. "Guarantees" is absolute legal terminology that should be avoided in technical comments.
- **Mandated Replacement:** *"Enforces strict empirical data lineage from primary government sources; requests with missing data return null/withheld status."*
- **Code Change Required:** Code comment cleanup scheduled for Sprint 3B.3.3.

### 2.5 Claim CLM-005: 100% Skill Extraction Precision
- **Location:** `docs/jobintel_v2/sprints/sprint_3b_3_2/SKILL_EXTRACTION_EVALUATION.md` (Line 60)
- **Original Claim:** *"5-token contextual co-occurrence window achieves 100% precision on skill extraction."*
- **Supporting Evidence:** Evaluated on 20 hand-crafted adversarial test cases.
- **Audit Risk:** Medium. Generalizes a 20-case test suite to all English vacancy text.
- **Mandated Replacement:** *"Contextual co-occurrence filter achieved 100% accuracy on the 20 adversarial benchmark test cases. Production vacancy text requires ongoing sample size reporting."*
- **Code Change Required:** No (Documentation only).

### 2.6 Claim CLM-006: Title Mapping Heuristic Confidence as Probability
- **Location:** `docs/jobintel_v2/sprints/sprint_3b_3_2/JOB_TITLE_MAPPING_PILOT.md` (Line 35)
- **Original Claim:** *"Confidence scores of 0.95 represent 95% mapping probability."*
- **Supporting Evidence:** Rule weights assign 0.95 to primary pattern matches.
- **Audit Risk:** High. Heuristic weights are not posterior probabilities (Raw ECE = 0.0587).
- **Mandated Replacement:** *"Heuristic mapping confidence is an uncalibrated similarity indicator. Calibrated probability requires post-hoc Platt / temperature scaling."*
- **Code Change Required:** No (Addressed via temperature calibration in Sprint 3B.3.3).
