# JOBINTEL 2.0 — SPRINT 3B.3.3.2.1
## DOCUMENT 03: EMPLOYER RESOLVER DUPLICATE IDENTIFIER & ARBITRARY SELECTION AUDIT

**Sprint:** 3B.3.3.2.1 — Independent Security, Statistical Contract & Release Audit  
**Auditor Role:** Principal Security Auditor & Backend Systems Architect  
**Audit Target:** Duplicate Registry Identifier Handling in `src/backend/employers/resolver.py`  
**Execution Mode:** STRICTLY READ-ONLY  
**Date:** 2026-11-17  
**Status:** CRITICAL DEFECT IDENTIFIED (ARBITRARY FIRST-RECORD RESOLUTION)  

---

### 1. Executive Summary & Defect Discovery

Section 4.A of the audit mandate requires an independent investigation of how `EmployerEntityResolver` handles duplicate statutory identifiers in the registry:
> *"Determine whether multiple distinct entities with the same authority, jurisdiction, and identifier can produce an automatic match.*  
> *Required safe behavior: Multiple conflicting records for the same identifier must not automatically select one. Duplicate or contradictory registry records must route to MANUAL_REVIEW_REQUIRED. No arbitrary primary-record selection."*

This forensic audit reveals that **`EmployerEntityResolver` contains an early-return design defect that produces arbitrary primary-record selection when duplicate registry identifiers exist.**

Furthermore, the existing regression test (`test_21_duplicate_registry_identifier_handling` in `tests/test_employer_resolver.py`) passed solely because it tested the first entity in the list, completely masking the vulnerability.

---

### 2. Code Inspection & Flaw Mechanism

#### 2.1 The Vulnerable Loop in `src/backend/employers/resolver.py`
In `EmployerEntityResolver.resolve()` (lines 243-326):
```python
for emp in self._employers:
    # ... compute similarity, check subsidiary markers ...
    if stat_match:
        if subsidiary_indicated or similarity < 0.60:
            candidates.append(...)
        else:
            candidate = EntityMatchCandidate(
                target_company_id=emp.company_id,
                target_company_name=emp.company_name,
                target_market_id=emp_market,
                match_type=ResolutionMatchType.EXACT_IDENTIFIER_MATCH,
                similarity_score=1.0,
                # ...
                review_status=EntityReviewStatus.AUTOMATICALLY_RESOLVED,
                requires_human_approval=False,
            )
            # CRITICAL DEFECT: EARLY RETURN ON FIRST MATCH
            return EmployerResolutionResponse(
                query_name=request.candidate_name,
                query_market_id=cand_market,
                resolution_match_type=ResolutionMatchType.EXACT_IDENTIFIER_MATCH,
                resolved_company_id=emp.company_id,
                review_status=EntityReviewStatus.AUTOMATICALLY_RESOLVED,
                candidates=(candidate,),
            )
```

#### 2.2 Mechanism of Failure
1. **Early Return Prematurity:**
   The resolver executes `return EmployerResolutionResponse(...)` on the **first employer in iteration order** where `stat_match` is True and `similarity >= 0.60`.
2. **Failure to Inspect Subsequent Records:**
   The resolver does not scan the remainder of `self._employers` to determine whether another registered employer shares the same statutory identifier.
3. **Arbitrary Primary Selection:**
   If entity $A$ and entity $B$ both carry SEC CIK `0001652044`, entity $A$ is *always* returned if it appears first in the list, regardless of which candidate was queried.

---

### 3. Adversarial Proof-of-Concept Execution

To confirm the vulnerability, an adversarial scenario was executed in an isolated runtime environment without modifying repository files:

#### Setup:
- Employer 1 (`emp-1`): `"Alpha One Corp"`, US, SEC CIK `0001652044`.
- Employer 2 (`emp-2`): `"Alpha Two Corp"`, US, SEC CIK `0001652044`.
- Registry order: `[emp-1, emp-2]`.

#### Query:
Candidate name: `"Alpha Two Corp"`, market: `"US"`, statutory identifier: `"CIK0001652044"`.

#### Empirical Output:
```text
Query Alpha Two Corp -> resolved_company_id: emp-1
Review status: AUTOMATICALLY_RESOLVED
Candidates: [('emp-1', 'Alpha One Corp', 1.0)]
```

#### Analysis:
1. Candidate `"Alpha Two Corp"` matched `emp-1`'s CIK.
2. Normalized similarity between `"alpha two"` and `"alpha one"` is $\frac{2 \times 7}{9 + 9} = 0.777 \ge 0.60$.
3. The resolver immediately returned `emp-1` (`"Alpha One Corp"`) as **`AUTOMATICALLY_RESOLVED`**!
4. **Result:** A query explicitly seeking `Alpha Two Corp` was mis-resolved to `Alpha One Corp` because `Alpha One Corp` occurred earlier in the registry list.
5. `emp-2` was never inspected.

---

### 4. Forensic Evaluation of `test_21_duplicate_registry_identifier_handling`

In `tests/test_employer_resolver.py`:
```python
def test_21_duplicate_registry_identifier_handling():
    url = "https://www.sec.gov/edgar/CIK0001652044"
    e1 = make_mock_employer("emp-1", "Alpha One", "US", "SEC", "US SEC", url)
    e2 = make_mock_employer("emp-2", "Alpha Two", "US", "SEC", "US SEC", url)
    resolver = EmployerEntityResolver([e1, e2])
    req = EmployerResolutionRequest(
        candidate_name="Alpha One",
        market_id="US",
        statutory_identifier="CIK0001652044",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id == "emp-1"
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
```

#### Audit Assessment:
- The test passed, but it evaluated only the tautological case where the queried entity (`Alpha One`) happened to be `e1` (index 0).
- The test did NOT check what happened when `Alpha Two` was queried.
- The test failed to verify the required governance invariant: **duplicate statutory records must NOT automatically resolve; they must route to `MANUAL_REVIEW_REQUIRED`**.

---

### 5. Architectural Specification for Remediation

To eliminate arbitrary primary-record selection and comply with Section 4.A:
1. **Eliminate Early Return:**
   The resolver must iterate through the entire employer registry, collecting all matching candidates.
2. **Duplicate Detection Gate:**
   If multiple distinct employers ($K \ge 2$) in the registry match the candidate's statutory token:
   - Automatic resolution is **strictly prohibited**.
   - The resolver must set:
     ```python
     resolution_match_type = ResolutionMatchType.AMBIGUOUS_CANDIDATE
     resolved_company_id = None
     review_status = EntityReviewStatus.MANUAL_REVIEW_REQUIRED
     requires_human_approval = True
     ```
   - An explicit caveat must be attached: `"Multiple distinct registered employers claim this statutory identifier. Automatic resolution prohibited; manual review required."`
3. **Unique Match Requirement:**
   Only when *exactly one* registered employer matches the canonical statutory token, AND the legal identity check passes ($\text{similarity} \ge 0.60$ and no subsidiary indicator), may the resolver return `AUTOMATICALLY_RESOLVED`.

---

### 6. Audit Verdict

- **Claim:** Duplicate registry identifiers are handled safely without arbitrary selection.
- **Evidence:** Runtime proof proves querying `Alpha Two Corp` automatically resolves to `emp-1` (`Alpha One Corp`).
- **Risk:** High severity data governance and corporate identity violation. An organization could be misattributed or merged with an unrelated entity sharing a duplicate registry reference.
- **Required Action:** Refactor `EmployerEntityResolver.resolve()` to eliminate early return, collect all matches, and enforce `MANUAL_REVIEW_REQUIRED` whenever duplicates are detected.
- **Status:** **CRITICAL DEFECT IDENTIFIED (BLOCKING STAGING RELEASE)**.
