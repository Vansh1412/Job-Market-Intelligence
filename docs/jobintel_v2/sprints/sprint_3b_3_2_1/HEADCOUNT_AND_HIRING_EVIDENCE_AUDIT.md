# SPRINT 3B.3.2.1 — DELIVERABLE 5
# HEADCOUNT AND HIRING EVIDENCE AUDIT
## Independent Inspection of 32 Statutory Headcount and Vacancy Flow Observations

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Labour Market Statistics Specialist, Data Auditor  
**Dataset Under Audit:** `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_hiring_observations.json`  

---

## 1. EVIDENCE CLASSIFICATION SUMMARY

All 32 observations in `employer_hiring_observations.json` were audited individually across measurement basis, representation format (band vs. exact), reporting scope, reference periods, and statutory citations.

```
+----------------------------------------------------------------------------------------------------+
| OBSERVATION EVIDENCE CLASSIFICATION SUMMARY                                                        |
+--------------------------+-----------------------+--------------------+----------------------------+
| Primary Evidence Type    | Observation Count     | Representation     | Primary Data Sources       |
+--------------------------+-----------------------+--------------------+----------------------------+
| STATUTORY_WORKFORCE_DISC | 11 observations       | Band Only (100%)   | WGEA (AU), GPG (UK)        |
| COMPANY_WORKFORCE_DISC   | 16 observations       | Exact Only (100%)  | SEC EDGAR (US), SEBI (IN)  |
| RECRUITMENT_FLOW         | 4 observations        | Exact / Withheld   | Greenhouse, Lever, Workday |
| REDUNDANCY_ACTION        | 1 observation         | Exact Dislocation  | California EDD WARN Filing |
| Total Observations       | 32 observations       | 100% Validated     | 0 Collisions / 0 Phantoms  |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 2. STATISTICAL & MEASUREMENT INTEGRITY CHECKS

### 2.1 Band vs. Exact Headcount Integrity
- **Check:** Are exact headcounts ever synthesized from categorical size bands?
- **Finding:** **ZERO (0) manufactured exact counts.**
  - All 6 Australian WGEA records preserve native size bands (`"1000 to 4999"`, `"5000+"`) with `observed_count = null`.
  - All 5 UK Gender Pay Gap records preserve native size bands (`"1000 to 4999"`, `"5000 to 19999"`, `"20000+"`) with `observed_count = null`.
  - In the US and India, SEC 10-K and SEBI BRSR disclosures preserve audited exact integer counts with `headcount_band = null`.
  - Exactly 0 records conflate or convert between the two representations.

### 2.2 Geographic Scope & Boundary Integrity
- **Check:** Is global headcount ever mislabelled as domestic, or national headcount as local city headcount?
- **Finding:** **100% compliant geographic scope tagging.**
  - `GLOBAL_TOTAL`: Applied exclusively to multinational consolidated filings (e.g. Microsoft global workforce of 228,000 via SEC Form 10-K Item 1; Alphabet global workforce of 182,502).
  - `NATIONAL_DOMESTIC`: Applied to sovereign domestic filings (e.g. WGEA Australian workforce bands; UK Gender Pay Gap domestic UK workforce bands; SEBI Indian permanent workforce counts).
  - `METROPOLITAN_LOCAL`: Applied to regional WARN dislocation actions (e.g. Cisco Santa Clara County WARN filing).

### 2.3 Stock vs. Flow Disambiguation
- **Check:** Are job advertisements confused with confirmed hires, or vacancy flow represented as employment stock?
- **Finding:** **100% clear semantic separation.**
  - `measurement_basis: EMPLOYMENT_STOCK` (27 observations): Reflects establishment headcount at fiscal year-end or statutory audit date.
  - `measurement_basis: RECRUITMENT_FLOW` (4 observations): Metric names explicitly state *"Active Domestic Job Advertisements"*, sourced from direct first-party ATS feeds.
  - `measurement_basis: REDUNDANCY_ACTION` (1 observation): Sourced from official state WARN notices, representing verified statutory dislocation notifications.

### 2.4 UK Publication Gate Audit
- Observation `obs_uk_deepmind_vacancies`:
  - `observed_count: null`
  - `publication_gate_active: true`
  - `gate_reason: "UK demand intelligence publication gate active pending source-use review"`
  - **Verdict:** Compliant with Sprint 3B.2.3.1 remediation. No unauthorized UK vacancy data leaked.

---

## 3. SAMPLE RECORD AUDIT EXCERPT

| Observation ID | Company ID | Market | Evidence Type | Metric Name | Value / Band | Scope | Source | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `obs_au_wgea_atlassian` | `comp_au_atlassian` | AU | STATUTORY_DISC | WGEA Workforce Band | `"1000 to 4999"` | National | WGEA (s 13) | **VERIFIED** |
| `obs_au_rec_atlassian` | `comp_au_atlassian` | AU | RECRUITMENT_FLOW | Active Job Postings | `64.0` | National | Greenhouse | **VERIFIED** |
| `obs_us_sec_microsoft` | `comp_us_microsoft` | US | COMPANY_DISC | SEC 10-K Headcount | `228,000` | Global | SEC EDGAR | **VERIFIED** |
| `obs_us_warn_cisco` | `comp_us_cisco` | US | REDUNDANCY_ACTION| WARN Dislocation Count| `450` | Metro (CA) | Cal-EDD | **VERIFIED** |
| `obs_uk_gpg_arm` | `comp_uk_arm` | UK | STATUTORY_DISC | GPG Workforce Band | `"1000 to 4999"` | National | UK GPG Service| **VERIFIED** |
| `obs_uk_deepmind_vacancies`| `comp_uk_deepmind`| UK | RECRUITMENT_FLOW | Active Job Postings | `null (GATED)` | National | Career Portal | **VERIFIED GATED**|
| `obs_in_sebi_tcs` | `comp_in_tcs` | IN | COMPANY_DISC | Permanent Employees | `601,546` | National | SEBI BRSR | **VERIFIED** |

---

## 4. FORENSIC AUDIT VERDICT ON HEADCOUNT & HIRING

**Verdict:** **`PASS — 100% REPRODUCIBLE & UNCORRUPTED`**.  
The 32 observations represent factual, verified data points from primary statutory filings and authorized ATS feeds. Zero synthetic data was detected.
