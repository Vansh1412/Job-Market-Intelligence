# SPRINT 3B.3.3: SECURITY AND GOVERNANCE AUDIT
## Pre-Release Security, Secret Detection, Data Governance & Corporate Identity Safeguards

**Sprint ID:** 3B.3.3  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Audit Date:** 2026-11-17  
**Auditor:** Principal Software Architect & Data Governance Specialist  
**Overall Security Verdict:** **PASS (ZERO VIOLATIONS / COMPLIANT)**

---

## 1. Executive Summary

This audit assesses the code, schema, and configuration changes introduced during Sprint 3B.3.3 against the security, privacy, and data governance standards of the JOBINTEL 2.0 platform.

The audit verified five major governance vectors:
1. **Secret & Credential Management:** Zero hardcoded secrets, API tokens, private keys, or `.env` credential leaks.
2. **Filesystem Path & Injection Safety:** Entity resolution operates purely in-memory with deterministic string normalization; zero filesystem traversal or arbitrary execution vectors.
3. **Data Governance & Source Verification:** UK demand publication gating (`UK_DEMAND_DATA_NOT_PUBLISHED`) is strictly preserved; zero unverified or scraped employer datasets committed.
4. **Corporate Identity & Legal Entity Safeguards:** Entity resolver enforces parent-subsidiary isolation and rejects automatic brand-based collapsing, preventing misleading corporate representations.
5. **Data Minimization & PII Protection:** Zero individual candidate records, employee PII, or confidential commercial contracts handled or stored.

---

## 2. Secret and Credential Audit

### 2.1 Repository and Diff Scanning
A scan was executed across all modified files and untracked sprint additions:
- `src/backend/services/india_service.py`
- `src/backend/services/usa_service.py`
- `src/backend/schemas/employer.py`
- `src/backend/employers/resolver.py`
- `src/backend/routers/v1.py`
- `tests/test_employer_resolver.py`
- `frontend/src/pages/PredictorPage.tsx`
- `frontend/src/pages/OccupationsPage.tsx`
- `frontend/src/pages/SkillsPage.tsx`
- `frontend/src/__tests__/prediction_display.test.ts`

**Findings:**
- **Zero API Keys:** No OpenAI, Anthropic, AWS, GCP, Vercel, or Render tokens detected.
- **Zero Database Passwords:** No connection strings or hardcoded credentials.
- **Zero Cryptographic Keys:** No private keys, certificates, or RSA blocks.
- **Environment Isolation:** Local `.env` files remain in `.gitignore` and are not staged.

---

## 3. Filesystem Safety & Injection Analysis

### 3.1 Employer Entity Resolver (`src/backend/employers/resolver.py`)
- **Memory-Only Processing:** The `EmployerEntityResolver` takes an in-memory dictionary of approved `EmployerProfile` entities and matches incoming `EmployerResolutionRequest` payloads purely through regex and string normalization.
- **No Path Traversal:** Does not read or write to the filesystem based on user input. No `open()`, `os.path.join()`, or dynamic imports based on query parameters.
- **No Eval / Exec:** String matching uses standard Python `re.sub` with fixed character class regexes (`[^a-z0-9 ]+`), eliminating code injection vulnerabilities.
- **Input Sanitization:** Input employer names are stripped, lowercased, and truncated safely.

### 3.2 Query Parameter Safety in Router (`src/backend/routers/v1.py`)
- The updated `/v1/employers` endpoint adds `limit` and `offset` with strict FastAPI/Pydantic validation:
  - `limit: Optional[int] = Query(None, ge=1, le=50)`
  - `offset: Optional[int] = Query(None, ge=0)`
- Negative numbers, non-integer types, and excessive limits (> 50) are rejected at the ASGI layer with HTTP 422 Unprocessable Entity.

---

## 4. Source Governance & Statutory Gate Enforcement

### 4.1 UK Demand Publication Gate Integrity
Sprint 3B.2 established the statutory publication gate requiring UK job posting counts to remain withheld (`null`) until accredited, representative official ONS / Adzuna series are certified.

- **Gate Verification:**
  - `src/backend/services/demand_service.py` was inspected and remains completely unmodified.
  - Test suite verification: `tests/test_demand_intelligence.py` executed 38 tests, including:
    - Verification that UK demand returns `postings_count: null`.
    - Verification that `reason: "UK_DEMAND_DATA_NOT_PUBLISHED"` is returned.
    - Verification that comparative demand charts exclude uncalibrated UK absolute indices.
- **Outcome:** **PRESERVED WITH ZERO REGRESSIONS**.

### 4.2 Machine Learning Model Binaries
- `models/india/final_model.pkl`: Hash unchanged; binary unmodified.
- `models/phase5/best_model.pkl`: Hash unchanged; binary unmodified.
- `models/india/scaler.pkl`: Hash unchanged; binary unmodified.
- Model weights were neither retrained nor retouched. All prediction changes are strictly presentational and metadata disclosures.

---

## 5. Corporate Identity & Anti-Collapsing Safeguards

### 5.1 Legal Entity Separation
In corporate data intelligence, automatically merging legally distinct entities (e.g., merging "Google India Private Limited" into "Alphabet Inc." or "Google LLC") misrepresents statutory employment liabilities, local wage structures, and compliance regimes.

- **Implementation Mechanism:**
  - The `EmployerEntityResolver` flags any candidate with known subsidiary suffixes (`private limited`, `pvt ltd`, `pty ltd`, `limited`, `gmbh`, `s.a.`, etc.) when matching against a parent entity.
  - Cross-market entity matches with differing sovereign jurisdictions (e.g., matching a US query against an IN statutory profile) are rejected from automatic exact matching.
  - Ambiguous matches return `status: EntityReviewStatus.MANUAL_REVIEW_REQUIRED`, preventing automated hallucination of corporate hierarchies.
- **Statutory Identifier Priority:**
  - Matches using authoritative government registries (SEC CIK, UK Companies House CRN, MCA CIN, ACRA UEN, ASIC ACN/ABN) receive `ResolutionMatchType.EXACT_STATUTORY_ID` and are classified as authoritative.

---

## 6. PII & Data Minimization Audit

- **Zero Individual Data:** No candidate names, resumes, email addresses, phone numbers, or individual salaries are collected, processed, or persisted.
- **Aggregated Cohorts Only:** Skill demand, occupation metrics, and wage models reflect statistical aggregates across thousands of public postings and official statistical surveys.
- **Stateless Execution:** The application maintains zero persistent user sessions or tracking cookies, preserving privacy-by-design.

---

## 7. Compliance Matrix

| Governance Requirement | Requirement Specification | Verification Evidence | Status |
| :--- | :--- | :--- | :--- |
| **SEC-01** | No secrets or credentials in codebase | Automated git diff & secret pattern scan | **PASS** |
| **SEC-02** | Input validation on pagination | FastAPI Query bounds (`ge=1, le=50, ge=0`) | **PASS** |
| **SEC-03** | Injection-safe entity resolver | Pure in-memory regex normalization | **PASS** |
| **GOV-01** | UK demand publication gating | `test_demand_intelligence.py` passing | **PASS** |
| **GOV-02** | Model binary immutability | SHA-256 hashes verified unchanged | **PASS** |
| **GOV-03** | Parent-subsidiary anti-collapsing | `test_employer_resolver.py` passing | **PASS** |
| **GOV-04** | PII and candidate data minimization | Clean codebase audit | **PASS** |

---

## 8. Conclusion

Sprint 3B.3.3 introduces zero security risks, leaks zero credentials, preserves all established data governance gates, and strengthens corporate identity safety across JOBINTEL 2.0.
