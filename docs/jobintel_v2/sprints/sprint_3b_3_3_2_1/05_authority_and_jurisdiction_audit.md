# JOBINTEL 2.0 — SPRINT 3B.3.3.2.1
## DOCUMENT 05: STATUTORY REGISTRY AUTHORITY & JURISDICTION INTEGRITY AUDIT

**Sprint:** 3B.3.3.2.1 — Independent Security, Statistical Contract & Release Audit  
**Auditor Role:** Independent Security Auditor & Corporate Registry Specialist  
**Audit Target:** Deterministic Statutory Token Parsing & Sovereign Jurisdiction Boundaries  
**Execution Mode:** STRICTLY READ-ONLY  
**Date:** 2026-11-17  
**Status:** VERIFIED  

---

### 1. Executive Summary

This audit independently assesses the sovereign registry architecture and adversarial resilience of `parse_statutory_token()` and the `AUTHORITY_MAP` in `src/backend/employers/resolver.py`.

The audit evaluated all five supported sovereign corporate registries:
1. United States: Securities and Exchange Commission (SEC EDGAR).
2. United Kingdom: Companies House.
3. India: Ministry of Corporate Affairs (MCA / ROC).
4. Singapore: Accounting and Corporate Regulatory Authority (ACRA).
5. Australia: Australian Securities and Investments Commission (ASIC / ABR).

---

### 2. Sovereign Authority & Token Parsing Verification

#### 2.1 US SEC EDGAR Specification
- **Canonical Format:** 10-digit zero-padded integer (e.g. `0001652044`).
- **Parsing Logic:**
  - Matches `CIK` prefix or `sec.gov` URL path.
  - Pads extracted digits to 10 characters: `f"{int(digits):010d}"`.
- **Authority Validation:** Rejects input if `authority_hint` conflicts with `"SEC"`.
- **Test Results:**
  - `Alphabet Inc` with `CIK0001652044` parses to `('SEC', '0001652044')` (**VERIFIED**).
  - Standalone `0001` evaluated without market/authority context evaluates to `None` (**VERIFIED**).

#### 2.2 UK Companies House CRN Specification
- **Canonical Format:** 8 characters (either 8 digits or 2 letters + 6 digits).
- **Parsing Logic:**
  - Matches `CRN` prefix, `company-information.service.gov.uk` URL, or standalone 8-character string with UK context.
- **Authority Validation:** Rejects input if authority hint conflicts with `"COMPANIES_HOUSE"`.
- **Test Results:**
  - `DeepMind Technologies Limited` with `07386357` parses to `('COMPANIES_HOUSE', '07386357')` (**VERIFIED**).
  - Scottish company number `SC123456` parses cleanly (**VERIFIED**).

#### 2.3 India MCA CIN Specification
- **Canonical Format:** 21 characters: `[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}`.
- **Structure Breakdown:** Listing status (1) + Industry code (5) + State (2) + Incorporation year (4) + Ownership structure (3) + Sequential registration number (6).
- **Parsing Logic:** Strict regex matching against the 21-character alphanumeric specification.
- **Test Results:**
  - `Infosys Limited` with `L72200KA1981PLC013115` parses to `('MCA', 'L72200KA1981PLC013115')` (**VERIFIED**).

#### 2.4 Singapore ACRA UEN Specification
- **Canonical Format:** 9 or 10 characters (e.g., `201812345M` or `T12LL1234A`).
- **Structure Breakdown:** Standard business format or new entity format with prefix/year/entity type.
- **Parsing Logic:** Regex matching against 8-9 digits + check letter, or 9-character entity token.
- **Test Results:**
  - `Grab Holdings Ltd` with `201812345M` parses to `('ACRA', '201812345M')` (**VERIFIED**).

#### 2.5 Australia ASIC / ABR Specification
- **Canonical Format:** Australian Business Number (ABN, 11 digits) or Australian Company Number (ACN, 9 digits).
- **Parsing Logic:** Matches `ABN` prefix, `abr.business.gov.au` URL parameter, or 11/9 standalone digits with AU context.
- **Test Results:**
  - `Atlassian Pty Ltd` with `53102443916` parses to `('ASIC', '53102443916')` (**VERIFIED**).

---

### 3. Adversarial Robustness Matrix

| Adversarial Attack / Vector | Input Scenario | Expected Defense | Observed Behavior | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Partial Token Infiltration** | Candidate passes `0001` against CIK `0001652044` | Reject token or fail exact match | Evaluates to `None` or fails token equality; `resolved_company_id = None` | **VERIFIED** |
| **Arbitrary String / Substring** | Candidate passes `"SEC"` | Reject as $< 4$ characters | Evaluates to `None`; no statutory match | **VERIFIED** |
| **Short Tokens** | Candidate passes `"12"`, `"1"`, `"   "` | Reject input | Evaluates to `None`; `NO_MATCH` | **VERIFIED** |
| **URL Substring Collision** | Identifier in non-statutory blog URL (`item?id=07386357`) | Reject non-registry source URL | Evaluates to `None`; no false statutory match | **VERIFIED** |
| **Authority Spoofing** | Candidate passes SEC CIK format with `statutory_authority="MCA"` | Flag authority conflict | Conflict detected; statutory matching suppressed | **VERIFIED** |
| **Jurisdiction Mismatch** | Candidate in `SG` passes US SEC CIK | Flag cross-jurisdiction divergence | Cross-jurisdiction match suppressed; manual review enforced | **VERIFIED** |
| **Conflicting Claims** | Candidate claims `UK Companies House` with SEC URL | Reject conflicting authority | Returns `None`; suppresses statutory match | **VERIFIED** |
| **Malformed Characters** | Candidate passes `!@#$%^&*()_+=` | Clean rejection without exception | Gracefully returns `None` and `NO_MATCH` | **VERIFIED** |

---

### 4. Findings Summary & Action Items

- **Claim:** All five sovereign registries are supported with deterministic token parsing, authority mapping, and adversarial defenses.
- **Evidence:** Code analysis of `src/backend/employers/resolver.py` and test execution of tests 01 through 12, 19, 20, 24, 25 in `tests/test_employer_resolver.py`.
- **Risk:** Minor edge cases in generic token fallback for unlisted foreign registries.
- **Required Action:** For Sprint 4.0, implement Luhn algorithm check-digit validation for Australian ABN and checksum validation for Singapore UEN.
- **Status:** **VERIFIED**.
