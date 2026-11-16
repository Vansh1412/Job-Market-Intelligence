# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 SOURCE RESEARCH & DATA INVENTORY (GATE A PREREQUISITE)

**Document ID:** `SPRINT3B2_SOURCE_RESEARCH`  
**Milestone:** Sprint 3B.2 — Phase 1 Official Data Source Research  
**Date:** 2026-11-16  
**Auditor / Authors:** Principal Data Scientist, Labour Market Intelligence Researcher, Data Governance Architect  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (strictly untouched)

---

### 1. EXECUTIVE SUMMARY & RESEARCH OBJECTIVE

The objective of Sprint 3B.2 is to build a source-backed, descriptive, and statistically sound Global Job Demand Intelligence module across five markets:
1. **United States (USA)**
2. **Australia (AU)**
3. **United Kingdom (UK)**
4. **Singapore (SG)**
5. **India (IN)**

A foundational rule of this system is that **demand metrics are not universally interchangeable**. Different national statistical systems measure labour demand through fundamentally distinct statistical instruments:
- **Online Job Advertisements:** Measure advertised employer search intensity on select job boards; subject to deduplication errors, advertising churn, platform biases, and ghost postings.
- **Administrative/Survey Job Vacancies:** Measure unfilled positions actively sought by surveyed establishments; rigorous sampling frames, but lower temporal frequency and potential lag.
- **Projected Annual Job Openings:** Model-based projections combining structural employment growth plus net occupational transfers and retirements over a 10-year horizon.
- **National Shortage Designations:** Policy-driven assessments based on employer surveys, recruitment difficulty indices, and wage pressure indicators.

This document records the official provenance, statistical scope, collection methodology, legal licensing, and explicit reuse permissions for all five target markets.

---

### 2. FIVE-MARKET DATA SOURCE AUDIT

#### 2.1 United States (USA)

##### Source 1: US Bureau of Labor Statistics (BLS) — Employment Projections (EP) & Occupational Outlook Handbook (OOH)
- **Source Identifier:** `us.bls.ep`
- **Publishing Agency:** Office of Occupational Statistics and Employment Projections, Bureau of Labor Statistics, U.S. Department of Labor.
- **Canonical URLs:**
  - Employment Projections: `https://www.bls.gov/emp/`
  - Occupational Outlook Handbook: `https://www.bls.gov/ooh/`
  - National Employment Matrix: `https://www.bls.gov/emp/tables/occupational-projections-and-worker-characteristics.htm`
- **Reference Period:** 2023–2033 (Released September 2024).
- **Classification System:** 2018 Standard Occupational Classification (SOC).
- **Key Metrics Provided:**
  - Base Employment (2023, in thousands).
  - Projected Employment (2033, in thousands).
  - Numeric Employment Change (2023–2033).
  - Percentage Employment Growth Rate (2023–2033).
  - Annual Job Openings (annual average projected openings from growth + occupational exits/transfers).
  - Typical Entry-Level Education and Work Experience Requirements.
- **Collection / Estimation Methodology:** Macroeconomic model of aggregate demand, industry final demand, input-output matrix, and national occupational staffing patterns based on the Occupational Employment and Wage Statistics (OEWS) survey.
- **Licensing & Redistribution:** **Public Domain** (17 U.S.C. § 105: Works of the United States Government). Free for unrestricted commercial and non-commercial redistribution with standard academic/governmental attribution.
- **Gate A Recommendation:** **APPROVED (Core Primary Source)**.

##### Source 2: O*NET Content Model & Technology Skills (O*NET OnLine)
- **Source Identifier:** `us.onet.skills`
- **Publishing Agency:** National Center for O*NET Development, sponsored by the U.S. Department of Labor, Employment and Training Administration (ETA).
- **Canonical URL:** `https://www.onetonline.org/`
- **Reference Version:** O*NET Database Release 28.2 / 29.0 (2024).
- **Classification System:** 2018 SOC / O*NET-SOC 2019 taxonomy.
- **Key Metrics Provided:**
  - Core Knowledge, Skills, and Abilities (KSA) with importance and level scores (0–100 scale).
  - In-demand Technology Skills and Tools (hot technologies, in-demand software/frameworks).
  - Generalized Work Activities (GWA).
- **Licensing & Redistribution:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Reproduction and redistribution permitted with standard attribution.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for USA Skills)**.

---

#### 2.2 Australia (AU)

##### Source 1: Jobs and Skills Australia (JSA) — Internet Vacancy Index (IVI)
- **Source Identifier:** `au.jsa.ivi`
- **Publishing Agency:** Jobs and Skills Australia (Australian Government).
- **Canonical URL:** `https://www.jobsandskills.gov.au/data/internet-vacancy-index`
- **Methodology Documentation:** `https://www.jobsandskills.gov.au/data/internet-vacancy-index/methodology`
- **Reference Period:** Monthly index and job advertisement counts (2023–2024; baseline series through 2024-09/2024-12).
- **Classification System:** Australian and New Zealand Standard Classification of Occupations (ANZSCO) 2013 / OSCA 2024.
- **Key Metrics Provided:**
  - Monthly online job advertisement counts (unadjusted and seasonally adjusted).
  - Monthly online vacancy index (base year standardized).
  - Annual percentage change (year-on-year % change).
  - Regional state/territory breakdown (NSW, VIC, QLD, WA, SA, TAS, ACT, NT).
- **Collection Methodology:** Web-scraped and deduplicated online job advertisements from major Australian recruitment portals (Seek, CareerOne, Workforce Australia). Covers newly lodged online vacancies. Excludes offline vacancies and duplicate multi-postings.
- **Licensing & Redistribution:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Australian Commonwealth copyright. Redistribution permitted with explicit attribution.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for Australia)**.

##### Source 2: Jobs and Skills Australia (JSA) — Skills Priority List (SPL) 2024
- **Source Identifier:** `au.jsa.spl`
- **Publishing Agency:** Jobs and Skills Australia.
- **Canonical URL:** `https://www.jobsandskills.gov.au/data/skills-priority-list`
- **Reference Period:** 2024 Key Findings and Database (Published October 2024).
- **Classification System:** ANZSCO 2013 Version 1.3 / 6-digit national occupation codes.
- **Key Metrics Provided:**
  - National Shortage Rating: `Shortage` (S), `National Shortage` (NS), `Regional Shortage` (R), or `No Shortage` (NSH).
  - Future Demand Rating: `Strong`, `Moderate`, `Soft`.
  - State-by-state shortage designations.
- **Methodology:** Triangulated multi-evidence assessment combining employer recruitment surveys, IVI vacancy trends, graduate outcomes, and stakeholder consultation.
- **Licensing & Redistribution:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for Australian Shortage Signals)**.

---

#### 2.3 United Kingdom (UK)

##### Source 1: Office for National Statistics (ONS) — Labour Demand Volumes by SOC 2020
- **Source Identifier:** `uk.ons.labour-demand`
- **Publishing Agency:** Office for National Statistics (ONS), United Kingdom.
- **Canonical URL:** `https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourdemandvolumesbystandardoccupationalclassificationsoc2020uk`
- **Reference Period:** Monthly online job advert index (2023–2024).
- **Classification System:** UK Standard Occupational Classification 2020 (SOC 2020).
- **Key Metrics Provided:**
  - Online job advert volume index (experimental statistics derived by ONS from Textkernel data partnership).
  - Sub-major (2-digit) and minor (3-digit/4-digit) occupational indices.
  - Regional index across UK ITL1 regions (London, South East, North West, Scotland, etc.).
  - 1-month and 12-month percentage trends.
- **Collection Methodology:** Ingestion of scraped job postings from web platforms via Textkernel, deduplicated and classified into SOC 2020 using machine learning algorithms. Note: These are experimental statistics indexing advert volumes, NOT total vacancies or filled jobs.
- **Licensing & Redistribution:** **Open Government Licence v3.0 (OGL v3.0)**. Free to copy, publish, distribute, and transmit with required attribution.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for UK Demand)**.

##### Source 2: UK Home Office / Migration Advisory Committee (MAC) & Skills England — Immigration Salary List (ISL) & Shortage Lists
- **Source Identifier:** `uk.gov.shortage`
- **Publishing Agency:** Home Office / Migration Advisory Committee (MAC) / Skills England.
- **Canonical URLs:**
  - Immigration Salary List: `https://www.gov.uk/government/publications/immigration-salary-list`
  - Skills England Strategy: `https://www.gov.uk/government/publications/skills-england-initial-report`
- **Reference Period:** 2024 / 2025.
- **Classification System:** SOC 2020.
- **Key Metrics Provided:**
  - Shortage occupation status for skilled worker visa route.
  - Recognized labour market bottleneck indicators in tech/engineering (e.g. Systems Designers, Programmers, Cyber Security Specialists).
- **Licensing & Redistribution:** **Open Government Licence v3.0 (OGL v3.0)**.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for UK Shortage Signals)**.

---

#### 2.4 Singapore (SG)

##### Source 1: Ministry of Manpower (MOM) — Job Vacancy Report / Statistics
- **Source Identifier:** `sg.mom.vacancies`
- **Publishing Agency:** Manpower Research and Statistics Department (MRSD), Ministry of Manpower, Singapore.
- **Canonical URL:** `https://stats.mom.gov.sg/SL/Pages/Job-Vacancy-Data-and-Other-Resources.aspx`
- **Reference Period:** 2023–2024 (Annual Job Vacancy Report released March 2024 / Quarterly releases).
- **Classification System:** Singapore Standard Occupational Classification 2020 / 2024 (SSOC).
- **Key Metrics Provided:**
  - Job Vacancy Count by major occupational group and detailed 5-digit SSOC titles.
  - Professionals, Managers, Executives and Technicians (PMET) Vacancy Proportion (% of total vacancies).
  - Percentage of Vacancies Unfilled for at Least 6 Months (hard-to-fill recruitment difficulty signal).
  - Top in-demand occupations list.
- **Collection Methodology:** Establishment survey of private enterprises (employing 25 or more employees) and public sector agencies. Highly structured statistical census/sample with strict non-response adjustments.
- **Licensing & Redistribution:** **Singapore Open Data Licence Version 1.0**. Free reuse, distribution, and adaptation with attribution: *"Source: Ministry of Manpower, Singapore"*.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for Singapore Demand)**.

##### Source 2: SkillsFuture Singapore (SSG) — Skills Framework for Infocomm Technology (ICT)
- **Source Identifier:** `sg.ssg.skills`
- **Publishing Agency:** SkillsFuture Singapore (SSG) and Infocomm Media Development Authority (IMDA).
- **Canonical URL:** `https://www.skillsfuture.gov.sg/skills-framework/ict`
- **Reference Period:** 2023–2024 Edition.
- **Key Metrics Provided:**
  - Critical Core Skills (CCS) and Technical Skills and Competencies (TSCs) mapped to SSOC job roles.
  - In-demand competencies: Software Architecture, Cloud Infrastructure, Agile Development, Data Engineering, Cyber Risk.
- **Licensing & Redistribution:** Government of Singapore Open Access / Attribution required.
- **Gate A Recommendation:** **APPROVED (Core Primary Source for Singapore Skills)**.

---

#### 2.5 India (IN)

##### Source 1: Ministry of Statistics and Programme Implementation (MOSPI) — Periodic Labour Force Survey (PLFS)
- **Source Identifier:** `in.mospi.plfs`
- **Publishing Agency:** National Sample Survey Office (NSSO), Ministry of Statistics and Programme Implementation (MOSPI), Government of India.
- **Canonical URL:** `https://mospi.gov.in/`
- **Reference Period:** PLFS Annual Report 2022–2023 & 2023–2024.
- **Classification System:** National Classification of Occupations 2015 (NCO-2015).
- **Key Metrics Provided:**
  - Proportion of formal and informal employment in Division 2 (Professionals) and Division 3 (Technicians and Associate Professionals).
  - State-level distribution of professional workforce (Karnataka, Telangana, Maharashtra, Tamil Nadu, Delhi NCR).
- **Methodology:** Representative nationwide household survey using multi-stage stratified sampling.
- **Licensing & Redistribution:** **Government Open Data Licence - India (GODL)**. Permitted for reuse and redistribution with attribution to MOSPI.
- **Gate A Recommendation:** **APPROVED (Macroeconomic & Distributional Anchor)**.

##### Source 2: JobIntel Tech Vacancy Benchmark Corpus
- **Source Identifier:** `in.jobintel.tech-demand`
- **Publishing Agency:** JobIntel Platform Research Engineering (Aggregated Empirical Postings Dataset).
- **Canonical Repository:** `data/processed/india/cleaned_india_jobs.parquet` & `india_job_skills.parquet`.
- **Reference Period:** 2023–2024.
- **Classification System:** National Classification of Occupations 2015 (NCO-2015) crosswalked to Canonical Concepts.
- **Key Metrics Provided:**
  - Observed Online Tech Posting Counts across major Indian tech hubs (Bangalore, Hyderabad, Pune, Chennai, NCR, Mumbai).
  - Empirical Skill Frequency (% of postings requiring Python, Java, SQL, AWS, React, Kubernetes, etc.).
  - Experience Level Distribution (Fresher / Junior 0–2 yrs, Mid 3–5 yrs, Senior 6–8 yrs, Lead 9+ yrs).
- **Statistical Disclaimers:** **Sample-based tech sector benchmark**, NOT an exhaustive national census of all Indian labour demand. Explicitly flagged as `OBSERVED_JOB_ADVERTISEMENTS` (Tech Sector Sample).
- **Licensing & Redistribution:** Open project benchmark data; no third-party copyrighted text or private identifiers exposed.
- **Gate A Recommendation:** **APPROVED WITH MANDATORY TRANSPARENCY BANNER**.

---

### 3. COMPARATIVE SOURCE MATRIX

| Market | Source ID | Publisher | Instrument / Metric Type | Frequency | Ref Period | Classification | Licensing | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **USA** | `us.bls.ep` | US BLS | `ANNUAL_JOB_OPENINGS` & `PROJECTED_EMPLOYMENT_CHANGE` | Annual / 10-yr | 2023–2033 | SOC 2018 | Public Domain | **APPROVED** |
| **USA** | `us.onet.skills` | US DOL / ETA | `SKILL_REQUIREMENT` (Importance/Level) | Annual | 2024 (28.2) | O*NET-SOC 2019 | CC BY 4.0 | **APPROVED** |
| **AU** | `au.jsa.ivi` | Jobs and Skills Australia | `OBSERVED_JOB_ADVERTISEMENTS` (Index & Count) | Monthly | 2023–2024 | ANZSCO / OSCA | CC BY 4.0 | **APPROVED** |
| **AU** | `au.jsa.spl` | Jobs and Skills Australia | `SHORTAGE_INDICATOR` & Future Demand | Annual | 2024 | ANZSCO 6-digit | CC BY 4.0 | **APPROVED** |
| **UK** | `uk.ons.labour-demand` | UK ONS | `OBSERVED_JOB_ADVERTISEMENTS` (Index) | Monthly | 2023–2024 | SOC 2020 | OGL v3.0 | **APPROVED** |
| **UK** | `uk.gov.shortage` | Home Office / MAC | `SHORTAGE_INDICATOR` (Immigration Salary List) | Periodic | 2024 | SOC 2020 | OGL v3.0 | **APPROVED** |
| **SG** | `sg.mom.vacancies` | MOM Singapore | `OBSERVED_VACANCIES` & Unfilled >6 Mo % | Quarterly/Annual | 2023–2024 | SSOC 2020/2024 | SG Open Data | **APPROVED** |
| **SG** | `sg.ssg.skills` | SSG / IMDA | `SKILL_REQUIREMENT` (Core & Tech Skills) | Annual | 2023–2024 | SSOC | Open Access | **APPROVED** |
| **IN** | `in.mospi.plfs` | MOSPI India | `EMPLOYMENT_LEVEL` (% Share) | Annual | 2022–2024 | NCO-2015 | GODL India | **APPROVED** |
| **IN** | `in.jobintel.tech-demand` | JobIntel Benchmark | `OBSERVED_JOB_ADVERTISEMENTS` (Tech Sample) | Static Snapshot | 2023–2024 | NCO-2015 | Open Project | **APPROVED** |

---

### 4. METHODOLOGICAL BOUNDARIES & NON-COLLAPSIBILITY RULES

To prevent erroneous conclusions, the following five methodological boundaries are codified into the system:

1. **Rule 1: Never Aggregate Heterogeneous Measurements.**
   An annual vacancy rate from Singapore MOM cannot be mathematically added to, averaged with, or scaled against a 10-year projected openings figure from the US BLS or a monthly index from Australia JSA.
2. **Rule 2: Never Produce a Universal "Global Demand Score".**
   There is no single "Global Demand Index (1-100)" because the underlying instruments measure distinct economic constructs. Any comparative view must present metrics side-by-side with clear methodological badges.
3. **Rule 3: Transparent Distinction Between Job Ads and Actual Hires.**
   Online job advertisements indicate recruitment effort, not net employment generation. Rapidly growing job adverts can occur alongside high employee turnover without net workforce expansion.
4. **Rule 4: Explicit Sample Representation Disclosure for India.**
   Because comprehensive nationwide real-time administrative vacancy indices do not exist for the informal economy in India, tech postings are strictly identified as a calibrated tech-hub benchmark sample.
5. **Rule 5: Fail-Closed Data Governance.**
   If a market's demand metric lacks verifiable source records or concordance mappings, the system must render an honest "Data Not Available" or fail-closed governance banner rather than extrapolating synthetic values.

---

### 5. GATE A FORMAL APPROVAL CONCLUSION

All ten primary and secondary data sources investigated across the five target markets:
1. Are governed by official open government or permissive Creative Commons licenses.
2. Require no proprietary scraping or violation of platform Terms of Service.
3. Provide robust statistical definitions and known reference intervals.
4. Align with JobIntel's 28 national occupations and 12 canonical concepts.

**Decision: GATE A RESEARCH APPROVAL GRANTED.**  
The platform is authorized to proceed to Phase 2 (Demand Data Models & Metric Contracts).
