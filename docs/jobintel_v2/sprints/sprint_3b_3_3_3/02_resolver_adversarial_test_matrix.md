# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 02: RESOLVER ADVERSARIAL TEST MATRIX & ORDER-INVARIANCE EVIDENCE

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Test Suite:** `tests/test_employer_resolver.py`  
**Total Tests:** 32 (expanded from 27)  
**Pass Rate:** 100% (32/32 PASS)  
**Execution Runtime:** 2.16s  

---

### 1. Test Suite Architecture

The test suite enforces mathematical order invariance, multi-jurisdiction collision rejection, spoofing defense, and strict Pydantic contract compliance.

| Category | Test IDs | Objective & Verification Target |
| :--- | :--- | :--- |
| **Statutory Exact Matching** | `test_01` – `test_05` | Exact match for SEC (CIK), Companies House (CRN), MCA (CIN), ACRA (UEN), ASIC (ABN). |
| **Identifier Malformation & Truncation** | `test_06` – `test_08`, `test_20` | Rejection of truncated CIKs, short tokens, substring collisions, and regex-invalid tokens. |
| **Jurisdictional & Authority Conflicts** | `test_09` – `test_12` | Rejection of cross-authority mismatches (e.g. SEC identifier submitted with ACRA authority). |
| **Cross-Border & Subsidiary Divergence** | `test_13` – `test_18` | Detection of legal-boundary mismatches (e.g. Google India vs Google LLC CIK, foreign subs vs domestic parents). |
| **Input Sanitization** | `test_19`, `test_25` | Whitespace-only names, empty strings, malformed schemas return 422 or fail-closed `NO_MATCH`. |
| **Duplicate Collision & Order Invariance** | `test_21`, `test_21b` – `test_21f` | Multi-jurisdiction duplicate statutory identifier collision handling with order invariance. |
| **Fuzzy Matching & Manual Review** | `test_22` – `test_24` | Routing of low-confidence or ambiguous matches to `MANUAL_REVIEW_REQUIRED`. |
| **API Endpoints & Pagination** | `test_26` – `test_27` | HTTP `/api/v1/employers` pagination and `/api/v1/employers/resolve` integration. |

---

### 2. Deep Dive: Adversarial Collision Test Suite (`test_21` series)

#### Test 21: SEC CIK Duplicate Collision & List Reversal
- **Setup:** Two records `emp-1` ("Alpha One Corp") and `emp-2` ("Alpha Two Corp") both carrying CIK `0001652044`.
- **Forward List `[emp-1, emp-2]`:**
  - Query "Alpha One Corp": `resolved_company_id is None`, `review_status == MANUAL_REVIEW_REQUIRED`, `resolution_match_type == AMBIGUOUS_CANDIDATE`.
  - Query "Alpha Two Corp": `resolved_company_id is None`, `review_status == MANUAL_REVIEW_REQUIRED`, `resolution_match_type == AMBIGUOUS_CANDIDATE`.
- **Reversed List `[emp-2, emp-1]`:**
  - Query "Alpha One Corp": identically returns `None` and `MANUAL_REVIEW_REQUIRED`.
  - Query "Alpha Two Corp": identically returns `None` and `MANUAL_REVIEW_REQUIRED`.
- **Result:** Complete order invariance. No arbitrary first-match bias.

#### Test 21b: UK Companies House CRN Duplicate Collision
- **Setup:** `London Deep Tech Ltd` and `Oxford Deep Systems Ltd` sharing CRN `07386357`.
- **Result:** Fail closed to `MANUAL_REVIEW_REQUIRED`, `resolved_company_id = None`, collision evidence attached.

#### Test 21c: Indian MCA CIN Duplicate Collision
- **Setup:** `Infosys Technologies Ltd` and `Infotech Bangalore Pvt Ltd` sharing CIN `L72200KA1981PLC013115`.
- **Result:** Fail closed to `MANUAL_REVIEW_REQUIRED`, `resolved_company_id = None`, collision evidence attached.

#### Test 21d: Singapore ACRA UEN Duplicate Collision
- **Setup:** `Grab Mobility Pte Ltd` and `Grab Financial Services Pte Ltd` sharing UEN `201812345M`.
- **Result:** Fail closed to `MANUAL_REVIEW_REQUIRED`, `resolved_company_id = None`, collision evidence attached.

#### Test 21e: Australian ASIC ABN Duplicate Collision
- **Setup:** `Atlassian Operations Pty Ltd` and `Atlassian Cloud Australia Pty Ltd` sharing ABN `53102443916`.
- **Result:** Fail closed to `MANUAL_REVIEW_REQUIRED`, `resolved_company_id = None`, collision evidence attached.

#### Test 21f: Randomized Registry Order Invariance (Monte Carlo Permutation)
- **Setup:** 5 synthetic companies sharing CIK `0001999999`.
- **Permutation:** 10 random seeds shuffle the registry order.
- **Verification:** Across all 10 shuffles and across all 5 candidate queries, every single resolution returns:
  - `resolved_company_id == None`
  - `review_status == MANUAL_REVIEW_REQUIRED`
  - `resolution_match_type == AMBIGUOUS_CANDIDATE`
  - Collision trail citing exactly 5 conflicting entities.

---

### 3. Pytest Execution Transcript

```
tests/test_employer_resolver.py::test_01_exact_valid_sec_cik_match PASSED [  3%]
tests/test_employer_resolver.py::test_02_exact_valid_uk_crn_match PASSED [  6%]
tests/test_employer_resolver.py::test_03_exact_valid_indian_cin_match PASSED [  9%]
tests/test_employer_resolver.py::test_04_exact_valid_singapore_uen_match PASSED [ 12%]
tests/test_employer_resolver.py::test_05_exact_valid_australian_abn_match PASSED [ 15%]
tests/test_employer_resolver.py::test_06_partial_identifier_rejection PASSED [ 18%]
tests/test_employer_resolver.py::test_07_short_identifier_rejection PASSED [ 21%]
tests/test_employer_resolver.py::test_08_substring_collision_protection PASSED [ 25%]
tests/test_employer_resolver.py::test_09_wrong_statutory_authority_conflict PASSED [ 28%]
tests/test_employer_resolver.py::test_10_wrong_jurisdiction_conflict PASSED [ 31%]
tests/test_employer_resolver.py::test_11_missing_authority_safe_fallback PASSED [ 34%]
tests/test_employer_resolver.py::test_12_conflicting_authority_rejection PASSED [ 37%]
tests/test_employer_resolver.py::test_13_google_india_with_google_llc_cik PASSED [ 40%]
tests/test_employer_resolver.py::test_14_subsidiary_candidate_with_parent_identifier PASSED [ 43%]
tests/test_employer_resolver.py::test_15_parent_candidate_with_subsidiary_identifier PASSED [ 46%]
tests/test_employer_resolver.py::test_16_same_brand_different_legal_entities_across_markets PASSED [ 50%]
tests/test_employer_resolver.py::test_17_foreign_subsidiary_vs_domestic_parent_entity PASSED [ 53%]
tests/test_employer_resolver.py::test_18_conflicting_legal_names_and_identifiers PASSED [ 56%]
tests/test_employer_resolver.py::test_19_whitespace_only_or_missing_candidate_name PASSED [ 59%]
tests/test_employer_resolver.py::test_20_malformed_statutory_identifier PASSED [ 62%]
tests/test_employer_resolver.py::test_21_duplicate_registry_identifier_handling PASSED [ 65%]
tests/test_employer_resolver.py::test_21b_duplicate_uk_crn_collision PASSED [ 68%]
tests/test_employer_resolver.py::test_21c_duplicate_indian_cin_collision PASSED [ 71%]
tests/test_employer_resolver.py::test_21d_duplicate_singapore_uen_collision PASSED [ 75%]
tests/test_employer_resolver.py::test_21e_duplicate_australia_abn_collision PASSED [ 78%]
tests/test_employer_resolver.py::test_21f_randomized_registry_order_invariance PASSED [ 81%]
tests/test_employer_resolver.py::test_22_ambiguous_fuzzy_candidate_routing PASSED [ 84%]
tests/test_employer_resolver.py::test_23_manual_review_status_preservation PASSED [ 87%]
tests/test_employer_resolver.py::test_24_no_match_distinct_entity PASSED [ 90%]
tests/test_employer_resolver.py::test_25_malformed_request_error_handling PASSED [ 93%]
tests/test_employer_resolver.py::test_26_employer_pagination_endpoint PASSED [ 96%]
tests/test_employer_resolver.py::test_27_resolve_endpoint_via_http PASSED [100%]

============================= 32 passed in 2.16s ==============================
```
