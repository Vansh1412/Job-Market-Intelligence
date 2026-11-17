# SPRINT 3B.3.2.1 — DELIVERABLE 11
# PUBLICATION GOVERNANCE DECISION
## Record-Level Publication Eligibility, Statutory Caveats & Permitted Display Channels

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Data Governance Specialist, Release Qualification Auditor  
**Scope:** All 82 entities in the pilot dataset (28 profiles, 32 hiring/headcount observations, 22 skill requirements)  
**Structured Matrix:** `docs/jobintel_v2/sprints/sprint_3b_3_2_1/EMPLOYER_PUBLICATION_ELIGIBILITY_MATRIX.csv`  

---

## 1. PUBLICATION ELIGIBILITY SUMMARY

Every individual entity and observation was evaluated against statutory source permissions, licensing boundaries, data quality, provenance completeness, privacy assessment, and publication purpose.

```
+----------------------------------------------------------------------------------------------------+
| PUBLICATION DECISION BREAKDOWN (82 TOTAL ENTITIES)                                                 |
+--------------------------+-----------------------+--------------------+----------------------------+
| Publication State        | Entity Count          | Share (%)          | Permitted Product Channel  |
+--------------------------+-----------------------+--------------------+----------------------------+
| PUBLISHABLE              | 43 entities           | 52.4%              | Public Directory & Profile |
| PUBLISHABLE_WITH_CAVEAT  | 38 entities           | 46.3%              | Profile with Mandatory Tag |
| WITHHELD                 | 1 entity              | 1.2%               | Serialized null / Drawer   |
| INTERNAL_RESEARCH_ONLY   | 0 entities            | 0.0%               | None                       |
| REVIEW_REQUIRED          | 0 entities            | 0.0%               | None                       |
| REVOKED                  | 0 entities            | 0.0%               | None                       |
| Total Entities Evaluated | 82 entities           | 100.0%             | 100% Traceable             |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 2. DETAILED GOVERNANCE CRITERIA FOR PUBLICATION STATES

### 2.1 State: `PUBLISHABLE` (43 Entities)
- **Applicability:**
  - 27 commercial enterprise profiles with sovereign registry verification (ABR, SEC EDGAR, Companies House, ACRA, SEBI).
  - 16 audited exact scalar headcount observations from SEC Form 10-K Item 1 filings and SEBI BRSR Principle 3 filings.
- **Permitted Channel:** Public Employer Directory (`/employers`), Employer Profile Pages (`/employers/[id]`), and statutory data drawers.
- **Mandatory Attribution:** Publisher name and statutory act citation must be visible in the Data Provenance Drawer.

### 2.2 State: `PUBLISHABLE_WITH_CAVEAT` (38 Entities)
- **Applicability:**
  - 1 public-sector agency profile (`comp_us_fed_va` — U.S. Department of Veterans Affairs).
  - 11 statutory establishment workforce size bands (6 WGEA Australia bands, 5 UK Gender Pay Gap bands).
  - 3 active vacancy counts from direct ATS feeds (Greenhouse, Lever).
  - 1 statutory dislocation notice from California EDD (Cisco WARN notice).
  - 22 posting-level skill requirements extracted from official career portal requisitions.
- **Mandatory Caveats Required in UI:**
  - *Size Bands:* `"Workforce size disclosed in statutory reporting brackets by [Publisher]; discrete headcount not published."`
  - *Public Sector Agency:* `"Sovereign federal agency governed via USAJOBS; not an SEC corporate registrant."`
  - *Vacancy Flow:* `"Advertised open vacancies from official careers portal; does not represent confirmed hires or net workforce expansion."`
  - *WARN Notices:* `"Statutory facility dislocation notification filed under Worker Adjustment and Retraining Notification Act."`
  - *Skill Requirements:* `"Skills requested in verified job postings for [Occupation] (Sample N = [count]); does not represent internal staff skills inventory."`

### 2.3 State: `WITHHELD` (1 Entity)
- **Applicability:** Observation `obs_uk_deepmind_vacancies` (UK employer open vacancies).
- **Governance Mandate:** In compliance with the platform UK publication gate, UK employer demand metrics are strictly withheld pending ONS/Adzuna source-use authorization.
- **Serialization:** Senders must serialize `observed_count = null` with `publication_gate_active: true` and the statutory disclaimer: *"UK vacancy flow data withheld pending source-use review."*

---

## 3. AUDITOR DIRECTIVE ON PERMITTED VS. PROHIBITED DERIVED METRICS

1. **PROHIBITED:** Synthetic "Employer Scores", "Hiring Momentum Scores", "Growth Indices", or competitive ranking tables.
2. **PROHIBITED:** Re-identifying recruiter names, hiring manager contacts, or executive home addresses.
3. **PROHIBITED:** Converting categorical size bands (e.g. `"1000 to 4999"`) into midpoints (e.g. `2,999.5`) or pseudo-exact floats.
4. **PERMITTED:** Pure factual side-by-side comparison of compatible attributes (e.g. comparing two ABN-registered entities on WGEA size band and industry sector).
