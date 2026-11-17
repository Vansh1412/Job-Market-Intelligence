# SPRINT 3B.3.3.1: EMPLOYER ENTITY RESOLVER & SUBSIDIARY PROTECTION AUDIT
## Critical Forensic Code & Security Audit: Vulnerability Analysis, Substring Matching & Test Coverage

**Sprint ID:** 3B.3.3.1  
**Audit Target:** `src/backend/employers/resolver.py`, `src/backend/schemas/employer.py`, `src/backend/routers/v1.py`  
**Auditor:** Independent Principal Engineer & Data Governance Specialist  
**Audit Date:** 2026-11-17  
**Finding Verdict:** **CRITICAL DEFECT DETECTED (SECURITY & GOVERNANCE VULNERABILITY)**

---

## 1. Executive Summary

This forensic code review audited the `EmployerEntityResolver` implementation and its API endpoints.

**Critical Finding:**  
The resolver contains a severe architectural vulnerability in its statutory identifier resolution logic:
1. **Statutory Override of Contradictory Names:** When `request.statutory_identifier` is provided and matches via substring, the resolver immediately returns `AUTOMATICALLY_RESOLVED` and assigns the target `company_id` without validating whether `request.candidate_name` matches or contradicts the entity name!
   - Example Exploit: Querying `candidate_name="Google India Private Limited"` with Alphabet's US CIK (`0001652044`) without `market_id` automatically resolves to `google-llc` (US parent), **completely bypassing the subsidiary anti-collapsing protection**!
   - Example Exploit: Querying `candidate_name="Malicious Phishing Shell Entity"` with an authentic SEC CIK automatically resolves to the authentic corporation!
2. **Insecure Substring Matching:** Statutory identifier matching uses `request.statutory_identifier.lower() in str(src.source_reference).lower()`.
   - Short strings (e.g. `"0001"`, `"SEC"`, `"1"`) match any source reference containing those characters, producing widespread false-positive corporate hijackings.
3. **Ignored Statutory Authority:** The request parameter `statutory_authority` is accepted by the Pydantic schema but **completely ignored** in the resolver logic.

---

## 2. In-Depth Component Analysis

### 2.1 Statutory Identifier Normalization & Precedence
- **Current Logic:** The resolver checks statutory identifier first:
  ```python
  if request.statutory_identifier:
      stat_match = any(
          request.statutory_identifier.lower() in str(src.source_reference).lower()
          for src in emp.source_references
      )
      if stat_match and (not cand_market or cand_market == emp_market):
          # Immediately returns AUTOMATICALLY_RESOLVED!
  ```
- **Flaws Identified:**
  - Uses `in` (substring containment) rather than exact identifier token extraction.
  - Does not normalize or strip registry prefixes (e.g., `"CIK0001652044"` vs `"0001652044"`).
  - Returns on the first iteration without checking for duplicate or conflicting identifiers across other registered employers.

### 2.2 Country & Market Isolation
- If `market_id` is supplied in the request, it checks `cand_market == emp_market`.
- If `market_id` is omitted (`None`), country isolation is completely disabled: an overseas candidate can match a domestic entity's identifier without any jurisdictional check.

### 2.3 Parent/Subsidiary & Foreign Subsidiary Handling
- For string-based queries (without statutory ID), the resolver correctly flags subsidiary markers (`"india"`, `"pvt ltd"`, `"pty ltd"`, `"technologies"`, etc.) and routes them to `MANUAL_REVIEW_REQUIRED`.
- However, as proved above, this protection is **completely overridden** if any statutory ID is present in the request.

### 2.4 Input Validation & Malformed Payloads
- `EmployerResolutionRequest`:
  - `candidate_name: str = Field(min_length=1, max_length=200)`
  - Whitespace-only strings (e.g. `"   "`) pass Pydantic validation (length 3), but `normalize_entity_name("   ")` collapses to `""`, causing empty brand matching.
  - Special characters are stripped via `re.sub(r"[^\w\s]", " ", cleaned)`, which safely prevents regex injection.
- API validation at the ASGI boundary enforces HTTP 422 for missing required fields.

---

## 3. Test Coverage Matrix

### 3.1 Existing Automated Tests (`tests/test_employer_resolver.py`)

| Test Function | Coverage Scope | Status |
| :--- | :--- | :--- |
| `test_employer_pagination_endpoint` | Verifies default list, limit/offset bounds, and HTTP 422 error trapping. | **PASS** |
| `test_resolver_exact_statutory_identifier_match` | Verifies happy-path exact CIK match in same market. | **PASS** |
| `test_resolver_prevents_automatic_subsidiary_collapse` | Verifies subsidiary name without statutory ID routes to manual review. | **PASS** |
| `test_resolver_no_match_for_distinct_entity` | Verifies unrelated employer returns `NO_MATCH` and `CONFIRMED_DISTINCT`. | **PASS** |
| `test_resolve_endpoint_via_http` | Verifies POST `/api/v1/employers/resolve` HTTP 200 payload. | **PASS** |

### 3.2 Missing & Uncovered Test Scenarios (Identified Gaps)

> [!WARNING]
> In accordance with read-only audit instructions, the following tests are documented but **MUST NOT** be added to the codebase during this audit sprint.

1. **Test Gap 01 — Contradictory Legal Entity Name with Statutory ID:**
   - Candidate passes `candidate_name="Google India Private Limited"` and `statutory_identifier="CIK0001652044"` (US parent CIK).
   - Expected Behavior: Must detect name-entity contradiction and route to `MANUAL_REVIEW_REQUIRED`.
   - Current Flaw: Resolver resolves to `google-llc` with `AUTOMATICALLY_RESOLVED`.
2. **Test Gap 02 — Substring False-Positive Identifier Match:**
   - Candidate passes `statutory_identifier="SEC"` or `"0001"`.
   - Current Flaw: Matches any registered employer having that substring in `source_reference`.
3. **Test Gap 03 — Ignored Statutory Authority:**
   - Candidate passes `statutory_authority="MCA"` (India) with an SEC CIK.
   - Current Flaw: Resolver ignores authority and resolves to US company.
4. **Test Gap 04 — Whitespace-Only Candidate Name:**
   - Candidate passes `candidate_name="   "`.
   - Current Flaw: Passes Pydantic validation; produces empty normalized string.
5. **Test Gap 05 — Conflicting Statutory Identifiers in Registry:**
   - Multiple registered employers containing overlapping source references.
6. **Test Gap 06 — Cross-Border Identifier Conflict:**
   - Candidate passes `market_id="SG"` with a US statutory ID.

---

## 4. Findings Matrix

### Finding RES-01: Statutory Match Overrides Contradictory Entity Identity
- **Claim:** The resolver strictly enforces JOBINTEL anti-collapsing rules and never collapses subsidiaries or misrepresents corporate identity.
- **Actual Implementation:** The statutory identifier block (lines 76–103) executes before any lexical similarity or subsidiary marker checks. If an identifier matches, it returns `AUTOMATICALLY_RESOLVED` unconditionally, regardless of how divergent or contradictory `candidate_name` is.
- **Evidence:** `src/backend/employers/resolver.py` lines 82–102.
- **Verification Method:** Forensic code trace and symbolic execution.
- **Risk:** **CRITICAL**. A malicious actor, scraper error, or data entry mistake could bind an Indian subsidiary, offshore entity, or unrelated business to a parent company profile, creating severe legal misrepresentation.
- **Required Action:**
  - Before automatically resolving a statutory match, verify that `candidate_name` does not contain subsidiary markers (`SUBSIDIARY_MARKERS`) and has high lexical compatibility with `emp.company_name`.
  - If a subsidiary marker is present in `candidate_name` while matching a parent statutory ID, route to `MANUAL_REVIEW_REQUIRED` with `is_subsidiary_relationship=True`.
- **Status:** **`INCORRECT / SECURITY DEFECT`**

### Finding RES-02: Substring Containment for Statutory Identifiers
- **Claim:** Statutory identifier matching is exact.
- **Actual Implementation:** Uses Python `in` operator on the string representation of `source_reference`:
  `request.statutory_identifier.lower() in str(src.source_reference).lower()`.
- **Evidence:** `src/backend/employers/resolver.py` line 79.
- **Verification Method:** Code inspection.
- **Risk:** **HIGH**. Fragile substring matching allows partial strings to trigger matches.
- **Required Action:**
  - Extract structured identifier fields (`statutory_id`, `statutory_type`) in `EmployerSourceReference`.
  - Require exact, normalized string equality on the identifier token.
- **Status:** **`INCORRECT`**

### Finding RES-03: Statutory Authority Parameter Ignored
- **Claim:** `statutory_authority` is accepted to disambiguate corporate registries.
- **Actual Implementation:** Parameter is accepted by `EmployerResolutionRequest` but never evaluated in `resolver.py`.
- **Evidence:** `src/backend/employers/resolver.py` lines 64–103.
- **Verification Method:** Variable usage analysis.
- **Risk:** Low operational risk, but misleading API contract.
- **Required Action:** Filter candidate employer source references by `src.source_organization == request.statutory_authority`.
- **Status:** **`NOT VERIFIED (DEAD CODE / CONTRACT MISMATCH)`**

---

## 5. Conclusion

While the string-based heuristic resolution correctly detects subsidiary markers, the statutory identifier branch contains critical security and governance flaws: it allows partial substring matching and unconditionally overrides contradictory legal entity names. This defect blocks production and staging release.
