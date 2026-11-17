# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## HIRING EVIDENCE TAXONOMY & STATISTICAL INTEGRITY RULES
### Seven-Tier Evidence Classification, Non-Collapsibility Mandates, Deduplication & Uncertainty Modeling

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-EVIDENCE-TAXONOMY`  
**Execution Phase:** Phase 0 (Research, Statistical Integrity & Classification Audit)  
**Date of Audit:** 2026-11-17  
**Core Standard:** Epistemological Separation of Observed Facts, Statutory Disclosures, and Inferred Estimates.

---

## 1. THE EPISTEMOLOGICAL PROBLEM OF EMPLOYER HIRING DATA

In commercial career platforms, "employer hiring" is frequently presented as a singular number (e.g. *"Google is hiring 1,500 people this month"* or an arbitrary "Hiring Activity Score: 88/100").

In labour economics and statistical science, **this representation is fundamentally indefensible**:
1. A digital job posting is a **recruitment marketing announcement**, not a transaction receipt for a hired worker.
2. A single open requisition may be used to hire 50 junior engineers, or it may be a "ghost job" used for talent pooling with zero active headcount budget.
3. Multiple third-party job boards scrape and duplicate identical postings across the web, artificially inflating apparent recruitment volume by 300% to 500%.
4. An annual increase in headcount discloses **net employee delta**, which reveals nothing about gross hiring unless company-wide attrition and turnover are accounted for.

To maintain scientific integrity, JOBINTEL 2.0 codifies an explicit **Seven-Tier Hiring Evidence Taxonomy**.

---

## 2. THE SEVEN-TIER HIRING EVIDENCE TAXONOMY

```
+-----------------------------------------------------------------------------------------+
| LEVEL 1: OFFICIAL_EMPLOYMENT_STATISTIC (Statutory Regulatory Filings)                   |
| -> Verified Headcount at Fiscal Close | Certified Legal Data | No Real-Time Vacancies   |
+-----------------------------------------------------------------------------------------+
| LEVEL 2: COMPANY_DISCLOSED_HIRING (Audited Annual Reports & Shareholder Disclosures)   |
| -> Certified Net Changes, Annual Gross Hires, Attrition Ratios | Retrospective          |
+-----------------------------------------------------------------------------------------+
| LEVEL 3: EXPLICIT_VACANCY_COUNT (Official Enterprise Vacancy Audits / Disclosed Slots)  |
| -> Point-in-time Unfilled Budgeted Slots | Extremely Rare at Employer Level             |
+-----------------------------------------------------------------------------------------+
| LEVEL 4: JOB_ADVERTISEMENT (Direct Employer ATS / Primary Career Portal Postings)       |
| -> Active Recruitment Intent | Ephemeral | 1 Post != 1 Hire | Null Openings Count       |
+-----------------------------------------------------------------------------------------+
| LEVEL 5: HISTORICAL_RECRUITMENT_OBSERVATION (Archived & Expired Job Requisitions)      |
| -> Past Skill Footprint | Closed Requisitions | Zero Current Vacancy Availability       |
+-----------------------------------------------------------------------------------------+
| LEVEL 6: EMPLOYMENT_CHANGE (Calculated Period-over-Period Net Delta)                    |
| -> Mathematical Derivative (Headcount_t2 - Headcount_t1) | Does Not Disclose Backfills  |
+-----------------------------------------------------------------------------------------+
| LEVEL 7: INFERRED_HIRING_ACTIVITY (Algorithmic / Heuristic Estimates)                   |
| -> Velocity Signals, Derived Projections | Statistical Model | Ground-Truth Unknown     |
+-----------------------------------------------------------------------------------------+
```

---

### Tier 1: `OFFICIAL_EMPLOYMENT_STATISTIC`
- **Definition:** Statutory corporate census data audited and submitted under legal mandate to national regulatory bodies (e.g., WGEA Australia public reports, SEC 10-K filings, Companies House annual accounts).
- **What It Establishes:** Legally verified total workforce headcount at the close of the reporting fiscal period; breakdown by statutory gender or occupation tiers where mandated.
- **What It DOES NOT Establish:** Real-time open requisitions, live talent demand, or skill requirements.
- **Epistemological Classification:** **Audited Regulatory Fact.**

---

### Tier 2: `COMPANY_DISCLOSED_HIRING`
- **Definition:** Formal retrospective human capital metrics published by corporate leadership in investor reports, annual reports (e.g. SEBI BRSR filings in India), or audited earnings statements.
- **What It Establishes:** Certified annual gross hiring figures (e.g., "TCS hired 45,000 fresh graduates in FY2024") and annualized corporate attrition percentages.
- **What It DOES NOT Establish:** Current month-to-month hiring velocity, individual office branch requirements, or verified daily vacancies.
- **Epistemological Classification:** **Corporate Disclosed Metric.**

---

### Tier 3: `EXPLICIT_VACANCY_COUNT`
- **Definition:** An authorized declaration by an employer stating the precise number of unfilled, budgeted, and actively recruited openings for a specific role (e.g., a civil service gazette or hospital authority stating "12 vacancies for Medical Officers").
- **What It Establishes:** The exact number of budgeted headcount positions authorized for recruitment at observation time $t$.
- **What It DOES NOT Establish:** The final number of candidates accepted, or the net change in total organizational headcount.
- **Epistemological Classification:** **Verified Budgeted Opening Fact.**

---

### Tier 4: `JOB_ADVERTISEMENT`
- **Definition:** A public digital posting collected directly from an employer career portal or authenticated Applicant Tracking System (ATS) requesting applicants for a job title.
- **What It Establishes:** Active recruitment marketing intent by the employer for that role and skill set on observation date $t$.
- **What It DOES NOT Establish:**
  1. It does NOT establish that 1 person was hired.
  2. It does NOT establish that 1 position was open (the employer may be hiring 20 people from 1 posting, or 0 people).
  3. It does NOT establish that the job is currently available once expired.
- **Data Rule:** `advertised_openings` is strictly serialized as `null` unless explicitly stated by the employer.
- **Epistemological Classification:** **Observed Public Announcement.**

---

### Tier 5: `HISTORICAL_RECRUITMENT_OBSERVATION`
- **Definition:** An archived job advertisement whose requisition has closed, expired, or been removed from the primary career portal.
- **What It Establishes:** The employer historically demanded those skills, qualifications, and titles during that past period.
- **What It DOES NOT Establish:** Current job availability or active recruitment.
- **Data Rule:** Mandatory visual flag: `REQUISITION_CLOSED` or `HISTORICAL_FOOTPRINT`. Must never be counted in active recruitment aggregates.
- **Epistemological Classification:** **Archived Historical Observation.**

---

### Tier 6: `EMPLOYMENT_CHANGE`
- **Definition:** The mathematical delta between two consecutive official reporting periods:
  $$\Delta E = E_{t_2} - E_{t_1}$$
- **What It Establishes:** Net headcount growth or contraction over interval $[t_1, t_2]$.
- **What It DOES NOT Establish:** Gross hiring. For example, if a firm of 100,000 employees has an attrition rate of 15% (15,000 departures) and reports a net increase of 5,000 employees, the gross hires were 20,000 employees, not 5,000.
- **Epistemological Classification:** **Derived Mathematical Statistic.**

---

### Tier 7: `INFERRED_HIRING_ACTIVITY`
- **Definition:** An algorithmic proxy derived from external signals (e.g., job posting cadence, team growth indicators, or economic modeling).
- **What It Establishes:** A directional momentum indicator indicating relative recruitment velocity.
- **What It DOES NOT Establish:** Ground-truth headcount or verified vacancies.
- **Data Rule:** Mandatory confidence intervals and transparent methodology disclaimers.
- **Epistemological Classification:** **Statistical Model Estimate.**

---

## 3. EPISTEMOLOGICAL SEPARATION MATRIX

Every data point exposed in JOBINTEL 2.0 must be classified into one of the following six distinct knowledge categories:

| Knowledge Category | Definition | Allowed Representation in UI | Prohibited Representation |
| :--- | :--- | :--- | :--- |
| **1. Observed Fact** | Verifiable empirical occurrence directly recorded from source. | *"Observed job posting on [date] for Senior Software Engineer."* | *"Company is expanding by 1 software engineer."* |
| **2. Official Published Statistic** | Statutory government or regulatory filing. | *"Headcount: 12,450 employees (as of 31 March 2024 per SEC 10-K filing)."* | *"Company currently employs 12,450 people today."* |
| **3. Company Disclosed Information** | Self-reported corporate announcement or annual report metric. | *"Company reported 14.2% attrition in FY24 Annual Report."* | Treating corporate press releases as statutory government audits. |
| **4. Derived Estimate** | Deterministic mathematical calculation from certified inputs. | *"Net Headcount Delta: +450 employees between FY22 and FY23."* | Conflating net headcount delta with gross hiring volume. |
| **5. Inferred Information** | Statistical or machine learning model output. | *"Inferred High Recruitment Velocity based on weekly posting cadence."* | Presenting an inferred score as ground-truth open jobs. |
| **6. Unknown Information** | Data that cannot be substantiated by authentic sources. | Explicit `null` or `"Not Disclosed by Employer"`. | Fabricating zero (`0`), filling averages, or hiding the absence. |

---

## 4. DEDUPLICATION & DATA QUALITY RISK CONTROLS

To prevent data contamination, all employer observations must undergo strict ingestion sanitization:

### 1. Cross-Platform Posting Deduplication
- **Risk:** An employer posts 1 requisition on their Workday ATS, which is automatically aggregated and republished across LinkedIn, Indeed, Glassdoor, and 15 niche job boards.
- **Deduplication Rule:** A posting is identified as a duplicate if:
  $$\text{Employer ID} = \text{Employer ID}_{\text{existing}}$$
  $$\text{Normalized Title} = \text{Normalized Title}_{\text{existing}}$$
  $$\text{City} = \text{City}_{\text{existing}}$$
  $$\text{Posting Date Delta} \le 7\text{ days}$$
- **Resolution:** Group duplicates under the primary canonical ATS observation; discard secondary aggregators.

### 2. The "Ghost Job" & Evergreen Posting Rule
- **Risk:** Certain enterprises maintain permanent, perpetual postings (e.g. "Software Engineer - All Levels") for continuous resume collection without immediate hiring budget.
- **Quality Rule:** Postings that remain open $> 120$ days without modification must be flagged as `EVERGREEN_TALENT_POOL` and excluded from short-term recruitment momentum calculations.

### 3. Missing Observation Dates
- Postings missing verifiable publication or ingestion dates must be rejected or tagged as `UNVERIFIED_CHRONOLOGY`.

### 4. Third-Party Staffing Agency Masking
- When a recruitment agency posts a job on behalf of a confidential client (e.g., "Top Tech Giant seeking Cloud Architect"), the posting **must never be assigned to the client company**. It must be attributed to the agency or classified as `UNRESOLVED_CLIENT_EMPLOYER`.

---

## 5. ABSOLUTE PROHIBITION: NO COMPOSITE EMPLOYER SCORE

JOBINTEL 2.0 strictly bans the computation or display of any composite:
$$\mathbf{Global\ Employer\ Hiring\ Score\ (PROHIBITED)}$$
$$\mathbf{Aggregate\ Employer\ Attractiveness\ Index\ (PROHIBITED)}$$

**Reasoning:** Combining a 2023 statutory headcount number, a 2024 digital job posting count, and an estimated wage model into a single 1-to-100 score destroys methodological validity, conceals missing data, and creates an illusion of precision that violates academic and research standards.

**Audit Status:** `PASS — HIRING EVIDENCE TAXONOMY FULLY SPECIFIED`
