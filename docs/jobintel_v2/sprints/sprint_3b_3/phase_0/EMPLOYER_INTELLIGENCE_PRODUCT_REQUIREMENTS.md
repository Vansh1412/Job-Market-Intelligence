# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER INTELLIGENCE PRODUCT REQUIREMENTS DOCUMENT (PRD)
### Functional Specifications, Module Requirements, User Problem Statements & Evidence Guardrails

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-PRD`  
**Execution Phase:** Phase 0 (Product Design & Requirements Audit)  
**Date of Audit:** 2026-11-17  
**Guiding Directive:** Define user-centric, academically defensible experiences with strict evidence guardrails. Zero UI implementation during Phase 0.

---

## 1. PRODUCT VISION & CORE PERSONAS

### Strategic Product Statement
JOBINTEL 2.0 Global Employer Intelligence provides transparent, evidence-backed intelligence on employers across the United States, United Kingdom, Australia, Singapore, and India. Unlike commercial review sites that rely on unverified anonymous sentiment or black-box rankings, JobIntel links corporate identities directly to **statutory government registers, certified human capital disclosures, and authentic primary recruitment postings**.

### Core Target Personas:
1. **The Global Career Transitioner / Job Seeker:** Needs to evaluate target employers, verify whether international hiring/sponsorship is active, understand required skill sets, and inspect confirmed regional office locations.
2. **The Labour Market & Policy Researcher:** Requires audited enterprise headcount trends, gender diversity statistics, and skill demand distributions across corporate sectors without proprietary aggregation bias.
3. **The Academic & Technical Auditor:** Demands transparent data provenance, clear statutory citations, and an epistemological separation of recruitment marketing from realized employment.

---

## 2. MODULE A: EMPLOYER DIRECTORY

### 1. User Problem Solved
Users need a trustworthy index to search and discover operating employers across five national markets without being misled by fictitious shell entities, duplicated recruitment agency listings, or pay-to-play featured company rankings.

### 2. Functional Requirements
- **Multi-Market Search Bar:** Real-time search across `legal_name`, `trading_names`, and `registration_id` (CIK, CRN, ABN, UEN, CIN).
- **Faceted Governance Filters:**
  - Market / Country of Registration (`US`, `UK`, `AU`, `SG`, `IN`).
  - Standard Industry Classification (Technology & Information, Financial Services, Healthcare, Manufacturing, etc.).
  - Enterprise Size Tier (`MICRO`, `SMALL`, `MEDIUM`, `LARGE`, `ENTERPRISE`).
  - Identity Verification Tier (`VERIFIED` only by default; toggle for `REVIEW_REQUIRED`).
- **Entity Card Display:** Company legal name, commercial trading brand, country flag, primary headquarters city, industry badge, and statutory registration key.

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `HIGH` (Available via Companies House, SEC EDGAR, ABR, ACRA, MCA master data).
- **Implementation Complexity:** `LOW-MEDIUM`.
- **Primary Risk:** Fragmented search results when users type informal abbreviations (e.g., "IBM" vs "International Business Machines Corp"). Mitigated via `trading_names` index.

---

## 3. MODULE B: EMPLOYER PROFILE

### 1. User Problem Solved
Users need a verified single-source-of-truth overview of an enterprise's corporate structure, operating locations, official website, and legal registration status.

### 2. Functional Requirements
- **Corporate Metadata Banner:** Verified legal entity name, corporate category, canonical domain, headquarters address, and official registration key with a direct deep-link to the national registry portal (e.g. link to Companies House or SEC search).
- **Corporate Structure & Hierarchy Card:** Display parent company (if subsidiary) and verified operating subsidiaries.
- **Statutory Headcount & Size Card:** Display official employee headcount certified from statutory filings (WGEA Australia, SEC 10-K, Companies House, or SEBI BRSR) with exact reporting date and source link.
- **Audited Office Locations:** List of verified corporate offices (HQ, Regional HQ, R&D centers) with geographic coordinates restricted to city/region level.

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `HIGH` for listed/large enterprises; `MEDIUM` for mid-market firms.
- **Implementation Complexity:** `MEDIUM`.
- **Primary Risk:** Outdated headcount figures if the latest annual accounts are not yet published. Mitigated via prominent "Observation Period: [Date]" timestamps.

---

## 4. MODULE C: HIRING INTELLIGENCE

### 1. User Problem Solved
Users need to understand an employer's actual recruitment activity without assuming that a high posting volume automatically means rapid expansion.

### 2. Functional Requirements
- **Observed Job Postings Explorer:** Table of active recruitment advertisements collected from direct employer career portals.
- **Filtering Capabilities:** Filter postings by Canonical Occupation (`CAN_OCC_*`), Seniority Level, Workplace Model (`Remote`, `Hybrid`, `Onsite`), and Location.
- **Epistemological Disclaimer Banner:** Mandatory callout:  
  *"Observed job postings represent recruitment marketing announcements and talent churn. They do not represent verified net headcount growth or individual confirmed hires."*
- **Historical Recruitment Footprint:** Visual timeline showing when the company historically advertised for specific job families over the past 12 months.
- **UK Gating Enforcement:** For UK entities, withhold proprietary commercial posting volumes behind the `UK_DEMAND_DATA_NOT_PUBLISHED` banner.

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `MEDIUM-HIGH` via direct ATS integrations.
- **Implementation Complexity:** `MEDIUM`.
- **Primary Risk:** Evergreen "ghost jobs" skewing volume. Mitigated via 120-day age-capping and `EVERGREEN_TALENT_POOL` tags.

---

## 5. MODULE D: SKILLS & QUALIFICATION ARCHITECTURE

### 1. User Problem Solved
Job candidates need to know which specific technical tools, programming languages, and credentials an employer genuinely expects for a target occupation, rather than guessing from vague job specs.

### 2. Functional Requirements
- **Top In-Demand Skills Table:** Ranked list of technical competencies extracted from employer job descriptions for a selected occupation.
- **Requirement Rigor Breakdown:** Distinct visual badges for:
  - `MANDATORY_REQUIRED` (stated as essential requirements).
  - `PREFERRED_BONUS` (stated as nice-to-have).
- **Skill Frequency Metrics:** Display percentage of employer postings in that job family demanding the skill:
  $$\text{Frequency} = \left(\frac{N_{\text{postings with skill}}}{N_{\text{total postings in occupation}}}\right) \times 100$$
- **Qualification Requirements Card:** Disclose stated minimum educational degrees (e.g. Bachelor's in CS), industry certifications (e.g. AWS, CISA, PMP), and minimum years of experience.

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `HIGH` for technology, data science, and engineering roles.
- **Implementation Complexity:** `MEDIUM-HIGH` (requires NLP parsing and skill taxonomy alignment).
- **Primary Risk:** False extraction of generic words as skills (e.g. "Go" or "Excel"). Mitigated via boundary token rules and JobIntel canonical skill tokens.

---

## 6. MODULE E: MULTI-EMPLOYER SIDE-BY-SIDE COMPARISON

### 1. User Problem Solved
Users need to objectively compare two prospective employers on compensation policy transparency, skill requirements, workforce scale, and geographic presence.

### 2. Functional Requirements
- **Side-by-Side Comparator:** Dual-column view comparing `Employer A` vs `Employer B`.
- **Harmonized Comparison Dimensions:**
  - Certified Workforce Size (WGEA, SEC, Companies House, BRSR).
  - Geographic Operating Hubs.
  - Workplace Flexibility (% Remote vs Hybrid vs Onsite).
  - Common Core Skills demanded for Software Engineers / Data Scientists.
  - Stated Experience Requirements.
- **Strict Anti-Ranking Rule:** **Zero artificial competitive rankings.** The interface must never proclaim "Employer A ranks higher than Employer B". It presents objective harmonized facts side-by-side.
- **Missing Data Disclosure:** If Employer B does not disclose an attribute, render an explicit `"Data Not Disclosed by Employer"` warning banner.

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `MEDIUM`.
- **Implementation Complexity:** `MEDIUM`.
- **Primary Risk:** Comparing companies across different reporting years or differing pay concepts (e.g. US Base vs India CTC). Mitigated via contextual comparability footnotes.

---

## 7. MODULE F: EMPLOYER GEOGRAPHIC MAP

### 1. User Problem Solved
Users want an interactive geographical map to visualize where an employer operates development centers, regional offices, and corporate headquarters.

### 2. Functional Requirements
- **Regional Facility Markers:** Plot verified office establishments at the city/metro centroid level.
- **Office Classification Pin Badges:** Visual differentiation between Global HQ (purple pin), Regional HQ (blue pin), and R&D Development Center (cyan pin).
- **Strict Privacy Safeguard:** **Absolute ban on plotting residential addresses or street-level coordinates.**

### 3. Feasibility, Complexity & Risk Assessment
- **Data Availability:** `MEDIUM-HIGH`.
- **Implementation Complexity:** `LOW-MEDIUM` (using lightweight SVG or canvas map rendering).
- **Primary Risk:** Confusing an individual remote employee's home city with a corporate operating office. Mitigated by plotting only verified corporate facilities.

---

## 8. SUMMARY PRODUCT ROADMAP & PHASE GATING

| Module | Phase 1 (MVP) Scope | Phase 2 Scope | Post-Phase 2 / Deferred |
| :--- | :--- | :--- | :--- |
| **Directory** | Top 250 enterprise employers across 5 markets. | Full corporate registry search index. | Automated scraping of micro-firms. |
| **Profile** | Statutory keys, verified locations, official headcount. | Subsidiary DAG visualization. | Unverified financial estimates. |
| **Hiring Intelligence** | Direct ATS postings with strict disclaimers. | Historical recruitment footprint series. | Commercial aggregator scraping. |
| **Skills & Qualifications** | Canonical skill frequency for tech roles. | Experience requirement distributions. | Soft skills / unmeasurable traits. |
| **Comparison** | Side-by-side factual comparisons. | Multi-company skill overlap matrices. | Black-box "Employer Scores". |
| **Geographic Map** | City-level office plots for verified HQ/R&D. | Regional hiring intensity heatmaps. | Street-level address geocoding. |

**Audit Status:** `PASS — PRD SPECIFIED WITH EVIDENCE-BASED GUARDRAILS`
