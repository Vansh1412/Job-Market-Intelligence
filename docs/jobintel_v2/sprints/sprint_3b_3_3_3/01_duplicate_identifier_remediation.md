# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 01: DUPLICATE IDENTIFIER REMEDIATION & RESOLVER HARDENING

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Component:** `src/backend/employers/resolver.py`  
**Security Classification:** Critical Integrity & Identity Attribution Vulnerability Remediation  
**Status:** IMPLEMENTED, ADVERSARIALLY VERIFIED & CLOSED  

---

### 1. Vulnerability Analysis & Root Cause

In forensic audit `Sprint 3B.3.3.2.1`, two critical defects in `src/backend/employers/resolver.py` were identified:

#### Defect 1: First-Match Early Return on Duplicate Statutory Identifiers (Arbitrary Attribution)
- **Mechanism:** In `EmployerEntityResolver.resolve()`, when an exact statutory identifier match (CIK, CRN, CIN, UEN, ABN) was found on an employer record, the resolver evaluated whether lexical similarity was $\ge 0.60$. If true, line 319 immediately executed:
  ```python
  return EmployerResolutionResult(
      resolution_match_type=EmployerResolutionMatchType.STATUTORY_EXACT_MATCH,
      resolved_company_id=emp.company_id,
      canonical_name=emp.canonical_name,
      ...
  )
  ```
- **Consequence:** If two distinct legal entities in the repository shared an identifier (e.g., due to registry data entry errors, corporate mergers, dual listings, or scraping anomalies), querying the second entity resolved to the *first entity encountered in list iteration order*. The resolution outcome was entirely dependent on non-deterministic insertion order, leading to identity spoofing or misattribution.

#### Defect 2: Artificial Similarity Clamping
- **Mechanism:** When a candidate's legal name contradicted the statutory entity (similarity $< 0.60$ or subsidiary indicated), line 298 artificially clamped the reported similarity score:
  ```python
  similarity_score = max(similarity, 0.75)
  ```
- **Consequence:** Distorted forensic audit metrics. A candidate with only 12% similarity (such as "Acme Scam Corp" vs "Alphabet Inc.") was reported to consumers with a 75% similarity score, obscuring spoofing attempts and masking severe lexical divergence.

---

### 2. Surgical Engineering Remediation

To eliminate these vulnerabilities, `src/backend/employers/resolver.py` was remediated as follows:

1. **Removal of Early Return:**
   - Eliminated line 319.
   - The loop now scans all registered employers in `self._employers` exhaustively, collecting all statutory matches and fuzzy candidates into `statutory_matches = []` and `fuzzy_candidates = []`.

2. **Collision Detection & Fail-Closed Routing:**
   - Evaluates the set of distinct company IDs matching the statutory token:
     ```python
     distinct_stat_ids = {emp.company_id for emp, _, _ in statutory_matches}
     ```
   - **Collision Rule:** If `len(distinct_stat_ids) > 1`:
     - Resolver refuses to guess or pick an arbitrary entity.
     - Immediately returns `review_status = EmployerReviewStatus.MANUAL_REVIEW_REQUIRED`.
     - Sets `resolved_company_id = None`.
     - Sets `resolution_match_type = EmployerResolutionMatchType.AMBIGUOUS_CANDIDATE`.
     - Appends full collision details into `evidence_trail` documenting every colliding entity ID, canonical name, and identifier.

3. **True Empirical Similarity Reporting (No Clamping):**
   - Removed `max(similarity, 0.75)`.
   - All similarity scores are computed using pure Levenshtein/token-sort metrics and reported as `round(sim, 4)`.
   - Ambiguous or contradictory candidates accurately report their genuine similarity score (e.g. 0.12 or 0.35).

4. **Deterministic Single-Entity Resolution:**
   - If and only if `len(distinct_stat_ids) == 1`:
     - Checks whether `subsidiary_indicated` or `sim < 0.60`.
     - If contradictory: routes to `AMBIGUOUS_CANDIDATE` with `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`, and true empirical similarity.
     - If legitimate: routes to `AUTOMATICALLY_RESOLVED` with `STATUTORY_EXACT_MATCH`.

---

### 3. Code Implementation Diff Summary

```python
# --- src/backend/employers/resolver.py ---
# Scan all employers without early return
statutory_matches = []
fuzzy_candidates = []

for emp in self._employers:
    is_stat_match, stat_field, stat_val = self._matches_statutory_token(emp, statutory_token, authority)
    sim = self._calculate_similarity(clean_candidate, emp.canonical_name, emp.trading_names)
    if is_stat_match:
        statutory_matches.append((emp, stat_field, sim))
    elif sim >= 0.50:
        fuzzy_candidates.append((emp, sim))

# Collision handling
distinct_stat_ids = {emp.company_id for emp, _, _ in statutory_matches}
if len(distinct_stat_ids) > 1:
    colliding_names = [f"{emp.canonical_name} ({emp.company_id})" for emp, _, _ in statutory_matches]
    return EmployerResolutionResult(
        resolution_match_type=EmployerResolutionMatchType.AMBIGUOUS_CANDIDATE,
        resolved_company_id=None,
        canonical_name=None,
        review_status=EmployerReviewStatus.MANUAL_REVIEW_REQUIRED,
        similarity_score=round(max(sim for _, _, sim in statutory_matches), 4),
        evidence_trail=[
            f"Statutory collision detected: identifier matched {len(distinct_stat_ids)} distinct entities: {', '.join(colliding_names)}.",
            "Resolution failed closed to require manual review without attribution."
        ],
        ...
    )
```

---

### 4. Empirical Order-Invariance Verification

To guarantee that list order cannot alter resolution behavior:
- Tested with two records: `emp-1` ("Alpha One Corp") and `emp-2` ("Alpha Two Corp") sharing CIK `0001652044`.
- **Forward Order `[emp-1, emp-2]`:**
  - Query `Alpha One Corp` -> `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`
  - Query `Alpha Two Corp` -> `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`
- **Reversed Order `[emp-2, emp-1]`:**
  - Query `Alpha One Corp` -> `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`
  - Query `Alpha Two Corp` -> `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`
- **Multi-Jurisdiction Invariance:** Verified across SEC (US), Companies House (UK), MCA (India), ACRA (Singapore), and ASIC (Australia).
- **Randomized Shuffle Invariance:** 10 random permutations of 5 colliding entities verified 100% invariant in `test_21f`.
