# SPRINT 3B.3.3.2: DEFECT REMEDIATION PLAN
## Detailed Technical Architecture, Implementation Strategy & Guardrails

**Sprint ID:** 3B.3.3.2  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Author:** Principal Backend Engineer & Security Architect  
**Date:** 2026-11-17  

---

## 1. Technical Strategy for Defect 1: Skill Denominator Alignment

### 1.1 The Underlying Semantic Disconnect
In the previous sprint, `frontend/src/pages/SkillsPage.tsx` displayed:
`{detailPostings.toLocaleString()} postings (Cohort N = {isUSA ? '34,036' : '5,859'})`
- **USA:** `detailPostings` for Python is `31,676`, and prevalence is `9.4%`. $31,676 / 34,036 = 93.1\%$, which contradicts $9.4\%$.
- **India:** Top skills show counts such as $723$ postings with $13.6\%$ prevalence. $723 / 5,859 = 12.3\%$, whereas $723 / 5,316 = 13.60\%$. The active skill-bearing denominator was $\sim 5,316$.

### 1.2 Remediation Architecture
1. **Backend Payload Enrichment (`src/backend/routers/skills.py` & `india_service.py`):**
   - For USA (`GET /skills/detail/{skill_name}`):
     Return structured population metadata:
     ```python
     "population_size": 335995,
     "population_type": "Deduplicated Tech & General Job Postings Corpus",
     "postings": postings,  # e.g. 31676
     "prevalence_pct": prev,  # e.g. 9.43%
     "observation_period": "2023-2024",
     ```
   - For India (`GET /india/skills/{skill_name}`):
     Read the exact population from `reports/tables/india/india_skill_analytics.json`:
     `total_active_postings: 5316` (or exact denominator matching $13.6\%$ from 723 postings).
     Return:
     ```python
     "population_size": 5316,
     "population_type": "Verified Tech Requisitions with Curated Skill Profiles",
     "posting_count": 723,
     "demand_percentage": 13.6,
     "observation_period": "2024-2025",
     ```
2. **Frontend Dynamic Rendering (`SkillsPage.tsx`):**
   - Remove hardcoded `34,036` and `5,859`.
   - Read `population_size` and `population_type` dynamically from the API response (`skillDetail?.population_size`).
   - If `population_size` is present, display:
     `{detailPostings.toLocaleString()} postings (Corpus N = {detailPopulation.toLocaleString()})`
   - Ensure the quotient $\frac{\text{detailPostings}}{\text{detailPopulation}}$ mathematically rounds to the displayed `detailDemandPct`.

---

## 2. Technical Strategy for Defect 2: Employer Resolver Security Hardening

### 2.1 The Vulnerability Mechanics
In the previous implementation:
1. Substring containment (`request.statutory_identifier.lower() in str(src.source_reference).lower()`) matched partial strings (e.g. `"0001"`, `"SEC"`, `"1"`).
2. Any statutory match immediately triggered `review_status = AUTOMATICALLY_RESOLVED` and returned `resolved_company_id = emp.company_id` without checking if `candidate_name` contradicted `company_name` (e.g. "Google India Private Limited" matching Alphabet's CIK).
3. `statutory_authority` was accepted in the Pydantic schema but ignored.

### 2.2 Hardening Architecture (`src/backend/employers/resolver.py`)

#### Step A: Exact Statutory Token Extraction & Matching
- Do NOT use substring containment.
- Implement structured identifier parsing:
  - For SEC CIK: extract the exact 10-digit or trimmed numeric CIK (e.g. `"0001652044"` or `"1652044"`).
  - For UK CRN: extract 8-character Companies House alphanumeric code (e.g. `"03977902"`).
  - For India CIN: extract 21-character alphanumeric MCA Corporate Identity Number.
  - For Singapore UEN: extract 9-10 character ACRA Unique Entity Number.
  - For Australia ABN/ACN: extract 11-digit ABN or 9-digit ACN.
- Compare candidate identifier against extracted structured identifiers using strict normalized token equality.

#### Step B: Statutory Authority & Jurisdiction Validation
- Define supported statutory authorities per jurisdiction:
  - US: `US SEC`, `SEC`, `EDGAR`, `SEC EDGAR`
  - UK: `UK Companies House`, `Companies House`, `CRN`
  - IN: `Ministry of Corporate Affairs`, `MCA`, `ROC`
  - SG: `ACRA`, `Accounting and Corporate Regulatory Authority`
  - AU: `ASIC`, `Australian Securities and Investments Commission`, `ABR`
- If `request.statutory_authority` is provided:
  - Must be compatible with the candidate market and the matched employer's registration authority.
  - If contradictory (e.g. `statutory_authority="MCA"` with an SEC CIK), reject automatic resolution and route to `MANUAL_REVIEW_REQUIRED` (or `NO_MATCH`).

#### Step C: Legal Entity Contradiction & Subsidiary Anti-Collapsing Check
- Even if the statutory identifier matches:
  - Extract normalized legal tokens and subsidiary markers from `candidate_name` and `target_company_name`.
  - If `candidate_name` contains subsidiary markers (`"india"`, `"uk"`, `"private limited"`, `"pvt ltd"`, `"pty ltd"`, `"services"`, `"technologies"`, etc.) that are NOT in `target_company_name`:
    $$\mathbf{RULE:} \quad \text{DO NOT AUTOMATICALLY RESOLVE.}$$
    Assign:
    - `review_status = EntityReviewStatus.MANUAL_REVIEW_REQUIRED`
    - `is_subsidiary_relationship = True`
    - `resolved_company_id = None`
    - `evidence_summary = "Candidate name indicates distinct legal subsidiary. Automatic collapsing into parent prohibited by JOBINTEL governance."`
  - If candidate market differs from registered entity headquarters without verified multinational operating rights, force manual review.

#### Step D: Conservative Decision Hierarchy
1. **EXACT_STATUTORY_MATCH (Authoritative):**
   - Exact identifier token match.
   - Compatible statutory authority.
   - Compatible jurisdiction.
   - Zero legal-entity / subsidiary contradictions.
   - $\rightarrow$ `AUTOMATICALLY_RESOLVED`.
2. **STATUTORY_IDENTIFIER_SUBSIDIARY_FLAG (Manual Review):**
   - Statutory ID matches parent, but candidate name has subsidiary marker or distinct jurisdiction.
   - $\rightarrow$ `MANUAL_REVIEW_REQUIRED` (`resolved_company_id = None`).
3. **STRONG_LEXICAL_CANDIDATE (Manual Review):**
   - Normalized similarity $\ge 0.98$, same jurisdiction, zero subsidiary markers.
   - $\rightarrow$ `MANUAL_REVIEW_REQUIRED`.
4. **AMBIGUOUS_CANDIDATE (Manual Review):**
   - Shared core brand, cross-market distinction, or subsidiary markers.
   - $\rightarrow$ `MANUAL_REVIEW_REQUIRED`.
5. **NO_MATCH (Distinct):**
   - No identifier match, similarity $< 0.70$, no shared brand.
   - $\rightarrow$ `CONFIRMED_DISTINCT` (`resolved_company_id = None`).

---

## 3. Implementation Steps & Verification Flow

```
1. Write 00_baseline_and_scope.md & 01_defect_remediation_plan.md
2. Implement WP-FIX-01:
   - Enrich backend skills endpoints with population metadata.
   - Update frontend SkillsPage.tsx to dynamically render verified population.
   - Author test_skill_denominator_integrity.py.
3. Implement WP-FIX-02:
   - Rewrite statutory token parsing & validation in resolver.py.
   - Add candidate name legal contradiction check.
   - Expand tests/test_employer_resolver.py with 25+ adversarial test cases.
4. Execute WP-FIX-03 & WP-FIX-04:
   - Document USA Median AE forensic reconciliation.
   - Document salary interval API contract deprecation plan.
5. Execute WP-FIX-05:
   - Document employer pagination capacity & migration roadmap.
6. Run full regression suite (376+ backend, 20+ frontend, Vite build).
7. Review as independent auditor & create documentation suite (02 through 11).
```
