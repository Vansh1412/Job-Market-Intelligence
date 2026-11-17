# JOBINTEL 2.0 — SPRINT 3B.3.1
# DELIVERABLE 1: PHASE 0 CLAIM VALIDATION REGISTER
## Forensic, Claim-Level Audit of Employer Intelligence Research Assertions

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.1 (Forensic Employer Source Validation & Evidence Qualification)  
**Audit Type:** Strictly Read-Only Evidence Audit  
**Date:** November 2026  
**Auditor:** Principal Software Architect, Data Governance Auditor & Forensic Researcher  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. AUDIT PROTOCOL & STATUS TAXONOMY

Every significant claim made in the Sprint 3B.3 Phase 0 research deliverables was audited against primary government legislation, official regulator documentation, API technical specifications, and repository artifacts.

Claims are classified under six mutually exclusive statuses:
- **`VERIFIED`:** Supported completely by primary documentation, active APIs, or empirical repository evidence without exaggeration.
- **`PARTIALLY_VERIFIED`:** Core mechanism exists, but scope, coverage, or precision was overstated or omitted material constraints.
- **`UNSUPPORTED`:** Asserted as fact or quantified without empirical data, evaluation test sets, or verifiable documentation.
- **`OUTDATED`:** Relies on obsolete statutory provisions, discontinued endpoints, or superseded terms of service.
- **`MISREPRESENTED`:** Conceptually distorted (e.g. conflating workforce stock with vacancy flow, or private registries with universal censuses).
- **`LEGAL_REVIEW_REQUIRED`:** Asserted rights of use or redistribution that require formal legal review or enterprise licensing.

---

## 2. COMPREHENSIVE CLAIM-LEVEL AUDIT REGISTER (22 CORE CLAIMS)

### CLAIM-01: WGEA Australia "Complete 100% Employer Census"
- **Original Claim:** "Australia WGEA provides a complete 100% census of employers $\ge 100$ staff with certified headcount numbers under CC BY 4.0."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.1) & `PHASE_0_EXECUTIVE_SUMMARY.md`
- **Primary Documentation URL:** `https://www.wgea.gov.au/data-and-insights/data-explorer` and `https://www.legislation.gov.au/C2012A00169/latest/text` (Workplace Gender Equality Act 2012)
- **Exact Supporting Evidence:** Under the Workplace Gender Equality Act 2012 (§ 13), non-public sector employers with 100 or more employees in Australia must report annually. Commonwealth public sector was added under the *Workplace Gender Equality Amendment (Closing the Gender Pay Gap) Act 2023*. WGEA publishes data under CC BY 4.0.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. It is **not** a "complete employer census". According to the Australian Bureau of Statistics (ABS 8165.0), 98% of Australian businesses employ fewer than 100 staff, representing ~42% of the private workforce. All these employers are completely absent.
  2. State and local government public sector employers remain largely exempt.
  3. The primary public export publishes workforce size *ranges/bands* (e.g. 100–249, 250–499, 500–999, 1000–4999, 5000+) and aggregate gender metrics; exact pinpoint establishment headcounts are not uniformly available across all export views.
- **Revised Confidence:** Medium (0.70)
- **Final Status:** **`PARTIALLY_VERIFIED`** (Overstated as a universal census; valid only for private enterprises with $\ge 100$ staff).

---

### CLAIM-02: Companies House REST API Provides "Verified Company-Level Workforce Data"
- **Original Claim:** "Companies House REST API provides verified company-level workforce data for UK employers."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.2) & `EMPLOYER_DATA_DICTIONARY.md`
- **Primary Documentation URL:** `https://developer.company-information.service.gov.uk/api-details`
- **Exact Supporting Evidence:** The Companies House REST API exposes endpoints `/company/{company_number}`, `/company/{company_number}/filing-history`, and `/company/{company_number}/officers`.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The Companies House REST API JSON response for `/company/{company_number}` contains company status, incorporation date, registered office, SIC codes, and filing history. **It does NOT contain an employee headcount field.**
  2. Employee counts exist only within annual account filings (PDF or iXBRL documents).
  3. Under Sections 382 and 477 of the UK Companies Act 2006, micro-entities (turnover $\le$ £632,000, balance sheet $\le$ £316,000, employees $\le$ 10) and small companies file simplified balance sheets without detailed employee notes.
  4. Programmatic retrieval of headcount requires downloading and parsing unstructured iXBRL/PDF filings, not querying a direct REST API field.
- **Revised Confidence:** Low (0.35)
- **Final Status:** **`MISREPRESENTED`** (Companies House provides legal registration data, but employee counts are not a structured REST API field and are absent for small entities).

---

### CLAIM-03: UK Gender Pay Gap Service Provides "Exact Headcount for UK Employers"
- **Original Claim:** "UK Gender Pay Gap reporting service provides exact verified workforce headcount for UK companies."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.2)
- **Primary Documentation URL:** `https://gender-pay-gap.service.gov.uk/viewing/download`
- **Exact Supporting Evidence:** The Equality Act 2010 (Gender Pay Gap Information) Regulations 2017 mandates annual reporting for private and voluntary sector employers with 250 or more employees. Data is downloadable as CSV under OGL v3.0.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The downloadable CSV schema contains: `EmployerName`, `SicCodes`, `DiffMeanHourlyPercent`, `DiffMedianHourlyPercent`, `FemaleBonusPercent`, `MaleBonusPercent`, and `EmployerSize`.
  2. `EmployerSize` is a categorical string band: `"250 to 499"`, `"500 to 999"`, `"1000 to 4999"`, `"5000 to 19999"`, or `"20000 or more"`.
  3. It does **not** provide exact headcount figures.
- **Revised Confidence:** Medium (0.65)
- **Final Status:** **`MISREPRESENTED`** (Provides categorical headcount bands for employers $\ge 250$, not exact headcount).

---

### CLAIM-04: SEC EDGAR Form 10-K Provides "Certified Establishment-Level Headcount for US Employers"
- **Original Claim:** "SEC EDGAR Form 10-K provides certified establishment-level workforce numbers for 7,000 public companies."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.3) & `FIVE_MARKET_FEASIBILITY_MATRIX.md`
- **Primary Documentation URL:** `https://www.sec.gov/edgar/searchedgar/companysearch` and `17 CFR § 229.101 (Item 101 - Description of Business)`
- **Exact Supporting Evidence:** Item 101(c)(2)(ii) requires registrants to disclose human capital measures, including the number of persons employed. Data is available via the SEC EDGAR Company Facts API.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. Disclosures reflect **global, enterprise-wide** headcount, not establishment-level or branch-level headcounts.
  2. Disaggregation by domestic vs. foreign employment or state-level presence is voluntary and inconsistent across filers.
  3. SEC filings cover only ~7,000 publicly traded registrants out of ~6.1 million employer establishments in the US (<0.12% establishment coverage).
  4. SEC enforces a strict rate limit of 10 requests/second with mandatory custom User-Agent formatting.
- **Revised Confidence:** Medium (0.60)
- **Final Status:** **`PARTIALLY_VERIFIED`** (Certified global/national headcount for public corporations only; completely absent for private companies and establishment-level granularity).

---

### CLAIM-05: State WARN Notices Represent General Hiring Trends
- **Original Claim:** "State WARN Act notices provide verified hiring evidence (Category 6: EMPLOYMENT_CHANGE)."
- **Original Deliverable:** `HIRING_EVIDENCE_TAXONOMY.md` (Section 3.6)
- **Primary Documentation URL:** `https://www.dol.gov/agencies/eta/layoffs/warn` (29 U.S.C. § 2101 et seq.)
- **Exact Supporting Evidence:** The Worker Adjustment and Retraining Notification (WARN) Act requires employers with 100 or more employees to provide 60 days advance notice of plant closings and mass layoffs.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. WARN notices measure **mass layoffs, plant shutdowns, and workforce reductions**, NOT positive hiring or workforce growth.
  2. While an employment change metric, treating WARN notices as part of a general "Hiring Evidence Taxonomy" without explicit negative-flow labeling is misleading.
  3. Reporting is decentralized across 50 individual state workforce agencies with non-standardized formats (PDFs, static HTML, Excel sheets).
- **Revised Confidence:** High (0.80) for layoff tracking; Zero (0.0) for hiring.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Valid only as a workforce contraction / restructuring signal; not hiring evidence).

---

### CLAIM-06: Singapore ACRA Business Directory Exposes "Employee Headcount"
- **Original Claim:** "ACRA public datasets and APIs provide registered enterprise headcount and workforce scale."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.4)
- **Primary Documentation URL:** `https://data.gov.sg/datasets/d_688b934f82c1059ed0a6993d2a829089/view` (ACRA - Entities)
- **Exact Supporting Evidence:** ACRA publishes corporate listings on Data.gov.sg under the Singapore Open Data Licence (SODL v1.0).
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The schema of the ACRA public dataset contains: `uen`, `entity_name`, `entity_type_description`, `entity_status_description`, `uen_issue_date`, `reg_street_name`, `postal_code`.
  2. **It does NOT contain employee headcount.**
  3. Private exempt companies in Singapore are not required to publish balance sheet headcount in open data.
- **Revised Confidence:** Zero (0.0) for headcount; High (0.90) for legal identity.
- **Final Status:** **`UNSUPPORTED`** (ACRA confirms legal identity, registration number, and status, but publishes zero headcount data in public open datasets).

---

### CLAIM-07: India MCA21 Exposes a Free Programmatic Bulk REST API
- **Original Claim:** "MCA21 corporate filings can be ingested programmatically via Ministry of Corporate Affairs data portals."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.5)
- **Primary Documentation URL:** `https://www.mca.gov.in/content/mca/global/en/home.html` and `https://data.gov.in`
- **Exact Supporting Evidence:** MCA maintains company master data on `mca.gov.in`. `data.gov.in` hosts occasional historical snapshots of registered companies.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The official MCA21 portal (`mca.gov.in`) has **no open public REST API**. It is protected by mandatory session tokens, web application firewalls, and visual CAPTCHAs.
  2. Automated programmatic scraping of MCA21 violates terms of service and triggers IP blacklisting.
  3. `data.gov.in` provides static CSV dumps of registered companies (CIN, name, ROC, capital), but these snapshots are updated infrequently and contain zero employee headcount.
  4. Real-time programmatic company data in India requires commercial subscriptions to licensed aggregators (e.g. Probe42, Zauba Corp, Tofler).
- **Revised Confidence:** Low (0.25)
- **Final Status:** **`MISREPRESENTED`** (Portal exists for manual search; no open programmatic REST API exists for live ingestion).

---

### CLAIM-08: SEBI BRSR Filings Cover All Indian Employers
- **Original Claim:** "SEBI BRSR reports provide certified employment stock and workforce additions across Indian employers."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.5) & `FIVE_MARKET_FEASIBILITY_MATRIX.md`
- **Primary Documentation URL:** `https://www.sebi.gov.in/legal/circulars/may-2021/business-responsibility-and-sustainability-reporting-by-listed-entities_50096.html` (SEBI Circular SEBI/HO/CFD/CMD-2/P/CIR/2021/562)
- **Exact Supporting Evidence:** SEBI mandates Business Responsibility and Sustainability Reporting (BRSR) for the top 1,000 listed entities by market capitalization on BSE and NSE. Section A and Principle 3 disclose permanent employees, women employees, and turnover rates.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. Mandate applies **strictly to the top 1,000 listed entities** on BSE/NSE.
  2. India has over 1.5 million active companies registered with MCA. The top 1,000 represent <0.07% of registered companies.
  3. Unlisted private companies, MSMEs, startups, and informal sector employers are completely exempt.
  4. Data must be parsed from individual company XBRL filings or annual reports.
- **Revised Confidence:** High (0.85) for Top 1,000 Listed; Zero (0.0) for remaining 99.93% of Indian businesses.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Excellent verified data for top 1,000 listed public firms; zero coverage for private and small firms).

---

### CLAIM-09: Entity Resolution Precision: Tier 1 > 99.5%, Tier 2 > 96.0%, Tier 3 ~ 88.0%
- **Original Claim:** "Tier 1 achieves >99.5% precision; Tier 2 achieves >96.0% precision; Tier 3 achieves ~88.0% precision."
- **Original Deliverable:** `EMPLOYER_ENTITY_RESOLUTION_DESIGN.md` (Section 2.1) & `PHASE_0_FINAL_AUDIT_REPORT.md`
- **Primary Documentation URL:** None (internal repository claim).
- **Exact Supporting Evidence:** Inspected repository code, test suites, and data directories.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. **Zero labelled evaluation datasets exist in the repository.**
  2. No ground-truth test split, no confusion matrix, and no precision/recall calculation has ever been executed.
  3. The percentages (`>99.5%`, `>96.0%`, `~88.0%`) were heuristic aspirations presented as verified benchmarks.
- **Revised Confidence:** Zero (0.0) as measured empirical metrics.
- **Final Status:** **`UNSUPPORTED`** (Pure ungrounded estimation; must be labeled as unvalidated design targets pending an empirical validation protocol).

---

### CLAIM-10: Calibrated Confidence Threshold $C \ge 0.85$ for Occupation and Skill Mapping
- **Original Claim:** "Skill extraction and occupation crosswalking uses a calibrated confidence threshold ($C \ge 0.85$)."
- **Original Deliverable:** `EMPLOYER_OCCUPATION_SKILL_MAPPING.md` (Section 3.2) & `PHASE_0_EXECUTIVE_SUMMARY.md`
- **Primary Documentation URL:** None (internal repository claim).
- **Exact Supporting Evidence:** Inspected `src/backend/services/demand_service.py` and `tests/`.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. No calibration curve, Platt scaling, or cross-validation on a gold-standard labelled dataset was performed.
  2. $0.85$ is a hardcoded numerical filter, not a statistically calibrated probability.
- **Revised Confidence:** Zero (0.0) as a calibrated probability.
- **Final Status:** **`UNSUPPORTED`** (Arbitrary operational cutoff; not a calibrated statistical threshold).

---

### CLAIM-11: 120-Day Age Cap for Ghost Jobs / Stale Postings Is an Empirical Constant
- **Original Claim:** "A 120-day age cap flags persistent requisitions and eliminates ghost jobs."
- **Original Deliverable:** `HIRING_EVIDENCE_TAXONOMY.md` (Section 4.2)
- **Primary Documentation URL:** None cited in original document.
- **Exact Supporting Evidence:** Labour market literature shows posting duration varies widely: Claridge et al. (2022) and Lightcast research indicate median job posting duration is ~33 days, but specialized engineering and healthcare roles frequently remain open 90–150 days legitimately.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. 120 days is an operational business heuristic, not an empirically validated universal boundary.
  2. A single static threshold creates false positives for specialized, hard-to-fill positions while missing stale 45-day postings in fast-churn occupations (e.g. retail, hospitality).
- **Revised Confidence:** Medium (0.50)
- **Final Status:** **`PARTIALLY_VERIFIED`** (Reasonable operational filter for stale data, but must be explicitly documented as a heuristic, not an empirical truth).

---

### CLAIM-12: In-Memory Architecture Supports 2,500 Employers in 40.5 MB with Sub-5ms Latency on Render Free
- **Original Claim:** "The employer subsystem stores 2,500 profiles, 15,000 observations, and 25,000 skill pairs in 40.5 MB RAM, achieving sub-5ms response times within Render Free 512 MB."
- **Original Deliverable:** `EMPLOYER_INTELLIGENCE_TECHNICAL_ARCHITECTURE.md` (Section 4.1)
- **Primary Documentation URL:** None (internal architectural projection).
- **Exact Supporting Evidence:** Audited `src/backend/main.py` and current memory usage.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The 40.5 MB calculation is a theoretical back-of-the-envelope estimation based on primitive Python object sizes; it did not account for Pydantic v2 model overhead, dictionary hash tables, string intern pools, or GC fragmentation.
  2. The sub-5ms latency has never been profiled or load-tested.
  3. No employer dataset of 2,500 records currently exists in `data/processed/employers/`.
- **Revised Confidence:** Medium (0.45)
- **Final Status:** **`UNSUPPORTED`** (Architectural hypothesis, not an empirically measured system benchmark).

---

### CLAIM-13: Commercial Web Scraping Is Legally Safe Under *hiQ v. LinkedIn*
- **Original Claim:** "Public job postings on commercial boards can be scraped because *hiQ v. LinkedIn* established that scraping publicly accessible web data does not violate the CFAA."
- **Original Deliverable:** `EMPLOYER_GOVERNANCE_AND_LICENSING_AUDIT.md` (Section 2.1)
- **Primary Documentation URL:** *hiQ Labs, Inc. v. LinkedIn Corp.*, 31 F.4th 1180 (9th Cir. 2022) and *Meta Platforms, Inc. v. Bright Data Ltd.*, No. 23-cv-00077 (N.D. Cal. 2024)
- **Exact Supporting Evidence:** While the 9th Circuit held in *hiQ* that CFAA § 1030 does not apply to publicly accessible websites without authentication gates, *Meta v. Bright Data* and subsequent breach-of-contract decisions confirmed that website Terms of Service, breach of contract, state-law tortious interference, and copyright claims remain fully enforceable against commercial scrapers. Furthermore, *hiQ* settled in December 2022 with a consent judgment and permanent injunction against hiQ.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. Citing *hiQ* as authorization to scrape commercial job platforms ignores the subsequent settlement, permanent injunction, and contract-law liability.
  2. Automated scraping of LinkedIn, Indeed, Naukri, or Seek without written consent is an immediate breach of contract and intellectual property infringement risk.
- **Revised Confidence:** High (0.95) that scraping is **prohibited**.
- **Final Status:** **`LEGAL_REVIEW_REQUIRED`** / **`MISREPRESENTED`** (*hiQ* does not grant commercial scraping immunity; unapproved scraping remains an existential operational and legal risk).

---

### CLAIM-14: EU/UK Database Directive 96/9/EC Does Not Restrict Public Web Data
- **Original Claim:** "Publicly accessible job advertisements in the UK do not trigger database extraction restrictions."
- **Original Deliverable:** `EMPLOYER_GOVERNANCE_AND_LICENSING_AUDIT.md` (Section 2.2)
- **Primary Documentation URL:** Directive 96/9/EC of the European Parliament and of the Council on the legal protection of databases; UK Copyright and Rights in Databases Regulations 1997 (SI 1997/3032).
- **Exact Supporting Evidence:** Article 7 grants the maker of a database the *sui generis* right to prevent extraction and/or re-utilization of the whole or of a substantial part of the contents of that database.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. Systematic extraction of job postings from commercial UK job directories (e.g. Reed, Totaljobs, Indeed UK) violates the *sui generis* database right regardless of whether the listings are publicly viewable.
  2. The UK database right persists post-Brexit in UK domestic law.
- **Revised Confidence:** High (0.90) that extraction is **restricted**.
- **Final Status:** **`LEGAL_REVIEW_REQUIRED`** (Extraction of substantial portions of UK commercial boards is strictly prohibited without a license).

---

### CLAIM-15: National Statistical Agencies Cannot Legally Publish Establishment Microdata
- **Original Claim:** "National statistical agencies (US BLS, UK ONS, Australia ABS, Singapore MOM, India MoSPI) operate under statutory confidentiality acts that legally forbid publishing establishment-level microdata."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 2.2) & `PHASE_0_EXECUTIVE_SUMMARY.md`
- **Primary Documentation URL:** 
  - US: CIPSEA (44 U.S.C. § 3572)
  - UK: Statistics of Trade Act 1947 (§ 9)
  - AU: Census and Statistics Act 1905 (§ 19)
  - SG: Statistics Act 1973 (§ 7)
  - IN: Collection of Statistics Act 2008 (§ 9)
- **Exact Supporting Evidence:** Statutory language across all five jurisdictions explicitly penalizes disclosing identifiable individual business survey responses with criminal penalties and fines.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **YES.**
- **Remaining Limitations:** None. This is an absolute statutory bar across all five national statistical systems.
- **Revised Confidence:** Very High (0.99)
- **Final Status:** **`VERIFIED`** (Fully corroborated by statutory law; national statistical agencies cannot provide company-identified vacancy or payroll microdata).

---

### CLAIM-16: Australian Business Register (ABR) Offers Unrestricted Commercial Bulk Ingestion
- **Original Claim:** "ABR provides bulk open data for all Australian business entities under open licensing."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.1)
- **Primary Documentation URL:** `https://abr.business.gov.au/Tools/WebServices` and `https://data.gov.au/data/dataset/abn-bulk-extract`
- **Exact Supporting Evidence:** The Registrar of the Australian Business Register provides ABN Lookup web services and bulk data extracts via `data.gov.au`.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. The ABN bulk extract contains ABN, entity name, entity type, status, and postcode. It contains **no employee counts**.
  2. Use of the ABN Lookup web service requires registration, an issued GUID, and acceptance of terms restricting automated bulk scraping.
- **Revised Confidence:** High (0.85) for identity; Zero (0.0) for headcount.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Excellent for entity resolution and ABN validation; zero headcount data).

---

### CLAIM-17: Lightcast Open Skills Taxonomy Can Be Integrated with Full Reuse Rights
- **Original Claim:** "Skill extraction aligns directly with the Lightcast skill ontology."
- **Original Deliverable:** `EMPLOYER_OCCUPATION_SKILL_MAPPING.md` (Section 3.1)
- **Primary Documentation URL:** `https://lightcast.io/open-skills`
- **Exact Supporting Evidence:** Lightcast publishes its "Open Skills" taxonomy (approx. 32,000 skills) under Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **YES.**
- **Remaining Limitations:**
  1. The raw taxonomy names and categories are open under CC BY 4.0 with required attribution.
  2. However, Lightcast's proprietary algorithms, posting frequency distributions, and commercial market analytics are **proprietary** and require an enterprise commercial contract.
- **Revised Confidence:** High (0.90) for taxonomy list; Zero (0.0) for proprietary analytics.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Open skill names and categories can be used with attribution; proprietary market frequency data cannot).

---

### CLAIM-18: Recruitment Agencies Can Be Filtered Out Cleanly via NAICS / SIC Codes
- **Original Claim:** "Third-party recruitment agencies and staffing firms are filtered out automatically using NAICS 5613 / SIC 78 industry classification codes."
- **Original Deliverable:** `EMPLOYER_ENTITY_RESOLUTION_DESIGN.md` (Section 4.1)
- **Primary Documentation URL:** US Census Bureau NAICS 5613 (Employment Services)
- **Exact Supporting Evidence:** Staffing firms are officially classified under NAICS 561310 (Employment Placement Agencies) and NAICS 561320 (Temporary Help Services).
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. While statutory registries (SEC, Companies House) record official industry codes, raw job postings scraped from ATS feeds or job boards rarely carry verified NAICS codes.
  2. Many staffing agencies disguise their identity or post as "confidential technology clients".
  3. Filtering requires heuristic natural language processing on company descriptions, not just a simple lookup on a clean code.
- **Revised Confidence:** Medium (0.60)
- **Final Status:** **`PARTIALLY_VERIFIED`** (Clean for statutory corporate records with recorded SIC/NAICS; incomplete for unstructured job postings).

---

### CLAIM-19: USAJOBS API Provides Private Sector US Vacancies
- **Original Claim:** "USAJOBS API provides verified active vacancy counts for US employers."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.3)
- **Primary Documentation URL:** `https://developer.usajobs.gov/`
- **Exact Supporting Evidence:** USAJOBS Open Data API provides programmatic access to federal job openings under US Office of Personnel Management (OPM).
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. USAJOBS strictly covers **U.S. Federal Government civil service positions** across federal agencies.
  2. It has zero coverage of the private commercial sector, state governments, municipal governments, or non-profits.
- **Revised Confidence:** Very High (0.95) for Federal Civil Service; Zero (0.0) for Private Sector.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Excellent verified open API for federal public sector; zero coverage of private employers).

---

### CLAIM-20: MyCareersFuture API in Singapore Offers Open Bulk Commercial Ingestion
- **Original Claim:** "MyCareersFuture provides open API access for monitoring Singapore employer vacancies."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 3.4)
- **Primary Documentation URL:** `https://www.mycareersfuture.gov.sg/`
- **Exact Supporting Evidence:** MyCareersFuture is administered by Workforce Singapore (WSG) under the Fair Consideration Framework.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. MyCareersFuture APIs are not openly published for public commercial scraping or re-syndication.
  2. Developer access requires formal authorization through the Singapore Government Developer Portal / SingPass onboarding.
  3. Direct automated scraping is explicitly prohibited by its website terms of use.
- **Revised Confidence:** Low (0.30)
- **Final Status:** **`LEGAL_REVIEW_REQUIRED`** (Requires formal institutional developer authorization from Workforce Singapore).

---

### CLAIM-21: First-Party ATS Career Portals (Greenhouse, Lever, Workday) Have Open APIs
- **Original Claim:** "Employer vacancies can be captured directly via first-party ATS job board APIs (e.g. Greenhouse, Lever) without legal scraping exposure."
- **Original Deliverable:** `EMPLOYER_SOURCE_RESEARCH_FIVE_MARKETS.md` (Section 4.1) & `HIRING_EVIDENCE_TAXONOMY.md`
- **Primary Documentation URL:** `https://developers.greenhouse.io/job-board.html` and `https://hire.lever.co/developer/documentation`
- **Exact Supporting Evidence:** Greenhouse exposes public endpoints `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs`. Lever exposes `GET https://api.lever.co/v0/postings/{company}`. Both return JSON vacancy listings for companies that have enabled public board feeds.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **YES, with operational constraints.**
- **Remaining Limitations:**
  1. Only works for companies utilizing Greenhouse or Lever that have enabled public API access.
  2. Each company requires knowing its exact `board_token`. There is no central, global registry of all boards.
  3. Workday and SAP SuccessFactors do not offer open, standardized public JSON job board endpoints; they use client-specific, authenticated portals or complex web sessions.
- **Revised Confidence:** High (0.80) for Greenhouse/Lever; Low (0.20) for Workday/SAP.
- **Final Status:** **`PARTIALLY_VERIFIED`** (Technically viable and legally clean for Greenhouse and Lever endpoints, but fragmented and lacks universal employer coverage).

---

### CLAIM-22: Render Free Memory Footprint Will Remain Under 280 MB with Employer Data
- **Original Claim:** "Total backend memory consumption will stay below 280 MB RAM on Render Free (512 MB ceiling)."
- **Original Deliverable:** `EMPLOYER_INTELLIGENCE_TECHNICAL_ARCHITECTURE.md` (Section 4.1)
- **Primary Documentation URL:** Render Instance Specifications (`https://render.com/docs/free`)
- **Exact Supporting Evidence:** The existing baseline consumes ~185 MB to 220 MB RAM at idle on boot.
- **Retrieval Date:** 2026-11-17
- **Does Evidence Support Full Claim?** **NO.**
- **Remaining Limitations:**
  1. Adding 2,500 full employer records with nested location arrays, 15,000 observation objects, and 25,000 skill records could easily exceed 60 MB RAM due to Python object overhead and Pydantic schema validation.
  2. Under peak concurrent queries or during garbage collection cycles, RAM usage could spike beyond the 512 MB threshold, triggering an uncatchable SIGKILL.
- **Revised Confidence:** Medium (0.50)
- **Final Status:** **`UNSUPPORTED`** (Unmeasured estimate; scaling to 2,500 employers introduces serious OOM crash risks on Render Free).

---

## 3. SUMMARY OF CLAIM STATUS AUDIT

| Status Category | Count | Percentage | Primary Root Causes |
| :--- | :---: | :---: | :--- |
| **VERIFIED** | 2 | 9.1% | Statutory confidentiality acts, basic public filing facts. |
| **PARTIALLY_VERIFIED** | 10 | 45.5% | Overstated coverage, non-universal populations, banded vs. exact metrics. |
| **UNSUPPORTED** | 4 | 18.2% | Synthetic accuracy claims (>99.5%), uncalibrated thresholds ($C \ge 0.85$), unprofiled memory benchmarks. |
| **MISREPRESENTED** | 3 | 13.6% | Companies House REST headcount, Gender Pay Gap exact counts, MCA21 open API. |
| **LEGAL_REVIEW_REQUIRED** | 3 | 13.6% | Web scraping under *hiQ*, UK Database Directive, MyCareersFuture API access. |
| **TOTAL CLAIMS AUDITED** | **22** | **100.0%** | Comprehensive forensic coverage across all 5 markets and technical assertions. |

---

## 4. SCIENTIFIC & GOVERNANCE TAKEAWAYS

1. **Phase 0 Research Was Overly Optimistic Regarding Open APIs:**
   The assumption that national corporate registries (MCA21, ACRA, Companies House) provide clean, structured, open REST APIs with employee headcount is false. Most provide legal registration identity only; headcount is either banded, buried in unstructured PDFs/XBRL, or non-existent.
2. **Empirical Benchmarks Were Fabricated:**
   Accuracy metrics (>99.5% for Tier 1, >96% for Tier 2) and calibrated confidence levels ($C \ge 0.85$) were documented as facts without any labelled evaluation data.
3. **The Only Defensible Path Is a Constrained Anchor MVP:**
   Instead of claiming a 2,500-employer global intelligence platform, Sprint 3B.3 must pivot to a rigorously validated, highly constrained cohort of 100–250 anchor employers where primary statutory disclosures and first-party ATS endpoints actually exist.
