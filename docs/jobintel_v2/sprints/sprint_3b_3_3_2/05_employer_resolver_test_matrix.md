# JOBINTEL 2.0 — SPRINT 3B.3.3.2
## DOCUMENT 05: EMPLOYER RESOLVER ADVERSARIAL TEST MATRIX

**Sprint:** 3B.3.3.2 — Critical Defect Remediation & Employer Resolver Hardening  
**Package:** WP-FIX-02  
**Author:** QA Lead & Security Test Engineer  
**Date:** 2026-11-17  
**Test File:** `tests/test_employer_resolver.py`  
**Status:** 27 / 27 TESTS PASSED (100%)  

---

### 1. Test Suite Summary

To verify the security, correctness, and governance compliance of the hardened employer entity resolver, an adversarial regression suite comprising 27 discrete tests was executed. All 27 tests passed cleanly in 40.70 seconds.

---

### 2. Detailed Test Matrix

| Test ID | Test Function Name | Category | Inputs / Scenarios | Expected Outcome | Execution Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `test_01_exact_valid_sec_cik_match` | Sovereign Registry Match | Alphabet Inc, US, `CIK0001652044`, `SEC` | `EXACT_IDENTIFIER_MATCH`, `resolved_company_id="alphabet-inc"`, `AUTOMATICALLY_RESOLVED` | **PASS** |
| **02** | `test_02_exact_valid_uk_crn_match` | Sovereign Registry Match | DeepMind Tech Ltd, UK, `07386357`, `Companies House` | `EXACT_IDENTIFIER_MATCH`, `resolved_company_id="deepmind-tech"`, `AUTOMATICALLY_RESOLVED` | **PASS** |
| **03** | `test_03_exact_valid_indian_cin_match` | Sovereign Registry Match | Infosys Limited, IN, `L72200KA1981PLC013115`, `MCA` | `EXACT_IDENTIFIER_MATCH`, `resolved_company_id="infosys-limited"`, `AUTOMATICALLY_RESOLVED` | **PASS** |
| **04** | `test_04_exact_valid_singapore_uen_match` | Sovereign Registry Match | Grab Holdings Ltd, SG, `201812345M`, `ACRA` | `EXACT_IDENTIFIER_MATCH`, `resolved_company_id="grab-holdings"`, `AUTOMATICALLY_RESOLVED` | **PASS** |
| **05** | `test_05_exact_valid_australian_abn_match` | Sovereign Registry Match | Atlassian Pty Ltd, AU, `53102443916`, `ASIC` | `EXACT_IDENTIFIER_MATCH`, `resolved_company_id="atlassian-pty-ltd"`, `AUTOMATICALLY_RESOLVED` | **PASS** |
| **06** | `test_06_partial_identifier_rejection` | Adversarial Infiltration | Candidate passes `0001` or `SEC` against CIK0001652044 | Must NOT match. `resolved_company_id is None` | **PASS** |
| **07** | `test_07_short_identifier_rejection` | Malformed Identifier | `12`, `SEC`, `1`, `   ` (< 4 chars) | `parse_statutory_token` returns `None` | **PASS** |
| **08** | `test_08_substring_collision_protection` | Substring Protection | Identifier in unrelated blog post URL (`item?id=07386357`) | Rejected. Must NOT match as a statutory reference | **PASS** |
| **09** | `test_09_wrong_statutory_authority_conflict` | Sovereign Authority Defense | Candidate passes `CIK0001652044` claiming authority `MCA` | Authority conflict suppresses exact statutory resolution | **PASS** |
| **10** | `test_10_wrong_jurisdiction_conflict` | Cross-Jurisdiction Defense | Candidate in `SG` passes US SEC CIK `CIK0001652044` | Suppresses match; `review_status = MANUAL_REVIEW_REQUIRED` | **PASS** |
| **11** | `test_11_missing_authority_safe_fallback` | Authority Fallback | Candidate passes CIK without authority in US vs UK | Resolves if US; suppresses if UK | **PASS** |
| **12** | `test_12_conflicting_authority_rejection` | Conflict Rejection | Candidate claims `UK Companies House` with SEC URL | Returns `None`; suppresses statutory match | **PASS** |
| **13** | `test_13_google_india_with_google_llc_cik` | Anti-Collapsing (Core) | Candidate `"Google India Private Limited"` with Google LLC CIK | `AMBIGUOUS_CANDIDATE`, `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED` | **PASS** |
| **14** | `test_14_subsidiary_candidate_with_parent_identifier` | Anti-Collapsing | `"Microsoft India R&D Pvt Ltd"` with MSFT US CIK | `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED`, `is_subsidiary = True` | **PASS** |
| **15** | `test_15_parent_candidate_with_subsidiary_identifier` | Cross-Entity Divergence | `"Alphabet Inc"` (US) with Indian subsidiary CIN | Suppresses match; `review_status = MANUAL_REVIEW_REQUIRED` | **PASS** |
| **16** | `test_16_same_brand_different_legal_entities_across_markets` | Cross-Market Brand | `"Amazon UK Services Ltd"` in UK vs `"Amazon.com Inc"` in US | `resolved_company_id = None`, `is_subsidiary = True`, `MANUAL_REVIEW_REQUIRED` | **PASS** |
| **17** | `test_17_foreign_subsidiary_vs_domestic_parent_entity` | Cross-Border Subsidiary | `"Apple Operations International Ltd"` (UK) vs `"Apple Inc"` (US) | `resolved_company_id = None`, `MANUAL_REVIEW_REQUIRED` | **PASS** |
| **18** | `test_18_conflicting_legal_names_and_identifiers` | Adversarial Spoofing | `"Acme Scam Corp"` passing Alphabet CIK `CIK0001652044` | Similarity < 0.60 blocks auto-resolution; `resolved_company_id = None` | **PASS** |
| **19** | `test_19_whitespace_only_or_missing_candidate_name` | Input Boundary | Candidate name `"   "` | `NO_MATCH`, `resolved_company_id = None`, `CONFIRMED_DISTINCT` | **PASS** |
| **20** | `test_20_malformed_statutory_identifier` | Robustness | `statutory_identifier="!@#$%^&*()_+="` | Gracefully handled without crash; `NO_MATCH` | **PASS** |
| **21** | `test_21_duplicate_registry_identifier_handling` | Integrity | Two registered employers sharing same identifier | Resolves primary without exception or crash | **PASS** |
| **22** | `test_22_ambiguous_fuzzy_candidate_routing` | Fuzzy Brand Collision | `"Alphabeta Technologies"` vs `"Alphabet Inc"` | Brand collision routed to `AMBIGUOUS_CANDIDATE`, `MANUAL_REVIEW_REQUIRED` | **PASS** |
| **23** | `test_23_manual_review_status_preservation` | Governance Gate | Ambiguous / subsidiary responses | All candidates require human approval: `requires_human_approval is True` | **PASS** |
| **24** | `test_24_no_match_distinct_entity` | Unrelated Entity | `"Bengaluru Artisan Bakery Ltd"` | `NO_MATCH`, `resolved_company_id = None`, `CONFIRMED_DISTINCT` | **PASS** |
| **25** | `test_25_malformed_request_error_handling` | HTTP Contract | POST `/api/v1/employers/resolve` with empty payload `{}` | FastAPI returns HTTP 422 Unprocessable Entity | **PASS** |
| **26** | `test_26_employer_pagination_endpoint` | HTTP Pagination | GET `/api/v1/employers` with limit, offset, bounds | Returns 200 for valid, 422 for limit>50, limit<1, offset<0 | **PASS** |
| **27** | `test_27_resolve_endpoint_via_http` | HTTP Integration | POST `/api/v1/employers/resolve` with Google India payload | Returns 200, governance caveat present, no auto-collapse | **PASS** |
