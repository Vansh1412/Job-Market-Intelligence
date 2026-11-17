# JOBINTEL 2.0 — SPRINT 3B.3.3.3.1
## DOCUMENT 03: EMPLOYER RESOLVER SECURITY AUDIT

**Sprint:** 3B.3.3.3.1 — Independent Remediation Verification & Release Gate Audit  
**Audit Target:** Audit C — Statutory Identifier Resolution, Collision Defense & Identity Attribution Safety  
**Component:** `src/backend/employers/resolver.py`  
**Status:** PASS — ARCHITECTURALLY SOUND & SECURE AGAINST MISATTRIBUTION  

---

### 1. Code-Level Inspection & Vulnerability Elimination

An exhaustive line-by-line inspection of `src/backend/employers/resolver.py` was conducted to verify that both critical defects identified in Sprint 3B.3.3.2.1 have been eliminated:

#### 1.1 Complete Scan & Elimination of First-Match Early Return
- **Verification:** Lines 244–322 iterate over `self._employers` in its entirety.
- **Evidence:** There are zero `return` statements within the `for emp in self._employers:` loop. All matches are gathered into `statutory_matches` and `fuzzy_candidates`.
- **Verdict:** First-match arbitrary attribution vulnerability is completely eradicated.

#### 1.2 Verification of Collision Detection (`distinct_stat_ids`)
- **Code:** Line 328:
  ```python
  distinct_stat_ids = {emp.company_id for emp, _, _ in statutory_matches}
  ```
- **Analysis:**
  - All records in `statutory_matches` have already been verified to share the candidate's normalized statutory token (`cand_token`) under compatible statutory authority and jurisdiction (lines 263–286).
  - The set comprehension `{emp.company_id for emp, _, _ in statutory_matches}` collects the unique company IDs associated with that statutory token.
  - **Case 1 (`len(distinct_stat_ids) > 1`):** Two or more distinct legal entities in the registry share the statutory identifier. Line 331 triggers:
    - `resolved_company_id = None`
    - `review_status = EntityReviewStatus.MANUAL_REVIEW_REQUIRED`
    - `resolution_match_type = ResolutionMatchType.AMBIGUOUS_CANDIDATE`
    - The resolver refuses to guess or pick an entity based on list order or lexical similarity.
  - **Case 2 (`len(distinct_stat_ids) == 1`):** Exactly one legal entity matches the statutory token. If multiple physical records exist representing the *same* legal entity (same `company_id`), `len(distinct_stat_ids) == 1` correctly prevents a false-positive collision and resolves safely.

#### 1.3 Elimination of Artificial Similarity Clamping
- **Inspection:** Line 376 previously executed `similarity_score = max(similarity, 0.75)`.
- **Verified Code:**
  ```python
  similarity_score = round(sim, 4)
  ```
- **Verdict:** True empirical similarity is reported. Spoof candidates or divergent entities (e.g. 12% similarity) are no longer masked with artificial 75% similarity.

---

### 2. Multi-Jurisdiction Adversarial Testing

Adversarial tests were executed across all five sovereign corporate registry authorities:

| Authority | Jurisdiction | Identifier Format | Colliding Entities Tested | Forward Order Result | Reverse Order Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SEC** | United States | CIK (10-digit) | `Alpha One Corp` vs `Alpha Two Corp` (CIK `0001652044`) | `None` / `MANUAL_REVIEW` | `None` / `MANUAL_REVIEW` | **PASS** |
| **Companies House** | United Kingdom | CRN (8-char) | `London Deep Tech Ltd` vs `Oxford Deep Systems Ltd` (CRN `07386357`) | `None` / `MANUAL_REVIEW` | `None` / `MANUAL_REVIEW` | **PASS** |
| **MCA** | India | CIN (21-char) | `Infosys Technologies Ltd` vs `Infotech Bangalore Pvt Ltd` (CIN `L72200KA1981PLC013115`) | `None` / `MANUAL_REVIEW` | `None` / `MANUAL_REVIEW` | **PASS** |
| **ACRA** | Singapore | UEN (9/10-char) | `Grab Mobility Pte Ltd` vs `Grab Financial Services Pte Ltd` (UEN `201812345M`) | `None` / `MANUAL_REVIEW` | `None` / `MANUAL_REVIEW` | **PASS** |
| **ASIC** | Australia | ABN (11-digit) | `Atlassian Operations Pty Ltd` vs `Atlassian Cloud Australia Pty Ltd` (ABN `53102443916`) | `None` / `MANUAL_REVIEW` | `None` / `MANUAL_REVIEW` | **PASS** |

#### Randomized Permutation Invariance (Monte Carlo Verification)
- 5 synthetic entities sharing CIK `0001999999` were shuffled across 10 random seeds.
- In every shuffle, and for every candidate query, `resolved_company_id` was strictly `None`, `review_status` was `MANUAL_REVIEW_REQUIRED`, and collision evidence cited exactly 5 colliding entities.

---

### 3. Downstream Consumer & Public Disclosure Review

1. **Downstream Callers:**
   - The sole consumer in the backend codebase is `src/backend/routers/v1.py` line 61 (`resolve_employer_endpoint`).
   - The route directly serializes the `EmployerResolutionResponse` Pydantic model.
   - When `resolved_company_id` is `None`, the response JSON contains `"resolved_company_id": null`. There is zero secondary fallback or automatic selection logic downstream.
2. **Public Information Disclosure:**
   - `evidence_summary` in collision responses states:
     ```
     Statutory identifier '...' is duplicated across 2 distinct registered employers. Automatic resolution prohibited; manual review required.
     ```
   - No private database fields, secrets, internal file paths, or credentials are leaked in the response payload.

---

### 4. Resolver Security Conclusion

The employer resolver remediation is robust, mathematically order-invariant, and enforces strict corporate identity boundaries across all 5 target markets.
