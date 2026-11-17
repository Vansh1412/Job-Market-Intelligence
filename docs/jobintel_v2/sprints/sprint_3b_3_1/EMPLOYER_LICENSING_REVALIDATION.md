# JOBINTEL 2.0 — SPRINT 3B.3.1
# DELIVERABLE 3: EMPLOYER LICENSING REVALIDATION
## Forensic Legal, Intellectual Property & Data Rights Audit Across Five Jurisdictions

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.1 (Forensic Employer Source Validation & Evidence Qualification)  
**Audit Type:** Statutory & Contractual Rights Revalidation  
**Date:** November 2026  
**Auditor:** Principal Data Governance Auditor & Legal Compliance Specialist  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. DATA RIGHTS TAXONOMY & AUDIT FRAMEWORK

To prevent blanket assumptions regarding data usability, this audit evaluates every data source across ten distinct legal rights:
1. **Public Access:** Can a member of the public access or view the data without special credentials?
2. **Download Permission:** Is downloading the raw dataset authorized by the publisher?
3. **Storage Permission:** Can the downloaded data be stored on JobIntel servers/filesystems?
4. **Commercial Use:** Does the license or statutory framework permit commercial operation?
5. **Display Permission:** Can raw or lightly formatted fields be rendered to end users in the UI?
6. **Redistribution:** Can the data be served through JobIntel APIs to external parties?
7. **Derived-Data Creation:** Can transformations, models, and aggregations be generated and monetized?
8. **API Terms Compliance:** Do ingestion scripts adhere to documented API query caps and headers?
9. **Mandatory Attribution:** What specific legal citation must accompany displayed data?
10. **Retention & Deletion Mandates:** Does the source enforce a right-to-be-forgotten or mandatory cache purge?

---

## 2. JURISPRUDENCE & STATUTORY LEGAL CONTROLS AUDIT

### 2.1 The CFAA, *hiQ v. LinkedIn*, and *Meta v. Bright Data*
- **The Phase 0 Misconception:** Phase 0 asserted that *hiQ v. LinkedIn* legalized commercial scraping of public job postings.
- **Forensic Legal Reality:**
  1. **The Scope of *hiQ* Was Narrow:** In *hiQ Labs, Inc. v. LinkedIn Corp.*, 31 F.4th 1180 (9th Cir. 2022), the Ninth Circuit ruled strictly on preliminary injunction grounds regarding whether scraping publicly available information violates the Computer Fraud and Abuse Act (CFAA, 18 U.S.C. § 1030). The court held that public websites without authentication gates cannot invoke CFAA criminal "unauthorized access" provisions.
  2. **The Subsequent Disposition of *hiQ*:** In December 2022, following remand to the district court, hiQ entered into a **settlement and consent judgment**, permanently enjoining hiQ from scraping LinkedIn data, requiring hiQ to delete all scraped LinkedIn data, and entering a judgment in favor of LinkedIn on its breach of contract claims.
  3. **Breach of Contract Liability (*Meta v. Bright Data*):** In *Meta Platforms, Inc. v. Bright Data Ltd.* (N.D. Cal. 2024), while the court declined summary judgment on breach of contract for logged-out public scraping, platforms have aggressively updated their Terms of Service (ToS) to bind commercial scrapers via browsewrap/clickwrap agreements, state-law breach of contract, trespass to chattels, and tortious interference with contractual relations.
  4. **Job Board Aggregators (LinkedIn, Indeed, Naukri, Seek):** All major commercial job aggregators explicitly prohibit automated scraping, indexing, or harvesting in their Terms of Service.
- **Audit Finding:** **`LEGAL_REVIEW_REQUIRED` / SCRAPING PROHIBITED.** Citing *hiQ* as authorization to harvest commercial job platforms is legally defective. JOBINTEL 2.0 must maintain an absolute prohibition against unapproved scraping of commercial job boards.

### 2.2 European Union & United Kingdom Database Directive (96/9/EC)
- **Statutory Framework:** Directive 96/9/EC on the legal protection of databases, retained in UK law via the *Copyright and Rights in Databases Regulations 1997* (SI 1997/3032).
- **The *Sui Generis* Database Right:** Protects databases where there has been qualitatively or quantitatively a substantial investment in obtaining, verifying, or presenting the contents. Article 7 prohibits the "extraction" (permanent or temporary transfer) and/or "re-utilization" (making available to the public) of all or a substantial part of the contents.
- **Application to Job Boards:** Commercial UK job boards (e.g. Reed, Totaljobs, Indeed UK) qualify for *sui generis* database protection. Extracting substantial portions of their listings—even if publicly visible without a password—constitutes actionable database infringement under UK law.
- **Audit Finding:** **`LEGAL_REVIEW_REQUIRED` / COMMERCIAL HARVESTING BLOCKED.** Ingesting commercial UK job board databases without a formal commercial license exposes the platform to immediate UK High Court injunctive action.

### 2.3 Statutory Confidentiality Acts (National Statistical Agencies)
- **United States:** Confidential Information Protection and Statistical Efficiency Act (CIPSEA, 44 U.S.C. § 3572). Criminal penalties (fines up to $250,000 and imprisonment up to 5 years) for disclosing identifiable establishment data from BLS surveys (JOLTS, QCEW, CES).
- **United Kingdom:** Statistics of Trade Act 1947 (§ 9). Absolute prohibition against ONS disclosing individual undertaking returns from the Inter-Departmental Business Register (IDBR).
- **Australia:** Census and Statistics Act 1905 (§ 19). Criminal offense for ABS officers to disclose individual business survey information.
- **Singapore:** Statistics Act 1973 (§ 7). Statutory secrecy covering all Singapore establishment returns to the Department of Statistics and MOM.
- **India:** Collection of Statistics Act 2008 (§ 9 & § 11). Penalizes disclosure of individual industrial unit statistics.
- **Audit Finding:** **`VERIFIED` ABSOLUTE BAR.** No legal mechanism exists for JobIntel to obtain establishment-level vacancy or payroll microdata from official national statistical agencies.

---

## 3. COMPREHENSIVE SOURCE LICENSING AUDIT MATRIX

| Source & Jurisdiction | License Type / Legal Basis | Commercial Use | Redistribution Rights | Display Permission | API Terms & Constraints | Mandatory Attribution Notice |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **Australia: WGEA** | Creative Commons Attribution 4.0 (CC BY 4.0) | **Permitted** | **Permitted** | **Permitted** | Direct bulk CSV download; no query caps. | *"Source: Workplace Gender Equality Agency (WGEA), Commonwealth of Australia"* |
| **Australia: ABR** | data.gov.au Bulk License & ABN Lookup Terms | **Permitted** | **Conditional** | **Permitted** | Web service requires registered GUID; bulk CSV has no API caps. | *"Source: Australian Business Register (ABR)"* |
| **Australia: APSjobs** | CC BY 3.0 AU / Australian Public Service | **Permitted** | **Conditional** | **Permitted** | RSS/Portal feeds; civil service only. | *"Source: Australian Public Service Commission (APSC)"* |
| **UK: Companies House** | Open Government Licence v3.0 (OGL v3.0) | **Permitted** | **Permitted** | **Permitted** | REST API requires API key; 600 requests per 5 minutes per IP. | *"Contains public sector information licensed under the Open Government Licence v3.0"* |
| **UK: Gender Pay Gap** | Open Government Licence v3.0 (OGL v3.0) | **Permitted** | **Permitted** | **Permitted** | Direct CSV download; annual snapshots. | *"Contains public sector information licensed under the Open Government Licence v3.0"* |
| **UK: Home Office Sponsors** | Open Government Licence v3.0 (OGL v3.0) | **Permitted** | **Permitted** | **Permitted** | Direct CSV download; updated daily. | *"Source: UK Visas and Immigration (UKVI), Home Office"* |
| **US: SEC EDGAR** | U.S. Public Domain (17 U.S.C. § 105) | **Permitted** | **Permitted** | **Permitted** | Max 10 req/sec; mandatory custom User-Agent format. | *"Source: U.S. Securities and Exchange Commission (SEC) EDGAR System"* |
| **US: USAJOBS** | U.S. Public Domain / OPM Open Data | **Permitted** | **Permitted** | **Permitted** | REST API requires API key; federal positions only. | *"Source: U.S. Office of Personnel Management (OPM) USAJOBS"* |
| **US: State WARN Notices** | Public Records / State Freedom of Information | **Permitted** | **Permitted** | **Permitted** | Decentralized; PDF/Excel scraping required; negative flows only. | *"Source: State Workforce Agency WARN Filings"* |
| **Singapore: ACRA** | Singapore Open Data Licence (SODL v1.0) | **Permitted** | **Permitted** | **Permitted** | Data.gov.sg DataStore API / CSV download. | *"Contains information from ACRA Entities accessed on [Date] from Data.gov.sg"* |
| **Singapore: MOM Agencies** | Singapore Open Data Licence (SODL v1.0) | **Permitted** | **Permitted** | **Permitted** | Downloadable CSV via Data.gov.sg. | *"Source: Ministry of Manpower (MOM) Singapore"* |
| **Singapore: MCF** | Government Partner Agreement (Gated) | **Restricted** | **Prohibited** | **Conditional** | Requires SingPass / government partner onboarding. | **LEGAL_REVIEW_REQUIRED** |
| **India: SEBI BRSR** | Public Regulatory Filings (BSE / NSE) | **Permitted** | **Conditional** | **Permitted** | Corporate XBRL/PDF filings; manual/ingestion required. | *"Source: SEBI BRSR Disclosures, BSE/NSE Corporate Filings"* |
| **India: MCA21** | Government Data Portal (data.gov.in / NDSAP) | **Permitted** | **Conditional** | **Permitted** | Static CSV on data.gov.in; mca.gov.in portal has CAPTCHA. | *"Source: Ministry of Corporate Affairs, Government of India"* |
| **India: NCS** | MoLE Data Sharing Agreement (Gated) | **Restricted** | **Prohibited** | **Conditional** | Requires institutional MoLE clearance. | **LEGAL_REVIEW_REQUIRED** |
| **Global: Greenhouse API** | First-Party Board API Terms | **Permitted** | **Permitted** | **Permitted** | Public endpoint enabled by client; requires valid board token. | *"Source: Direct Employer Career Feed via Greenhouse"* |
| **Global: Lever API** | First-Party Board API Terms | **Permitted** | **Permitted** | **Permitted** | Public endpoint enabled by client; requires valid company token. | *"Source: Direct Employer Career Feed via Lever"* |
| **Global: Lightcast Skills** | Creative Commons Attribution 4.0 (CC BY 4.0) | **Permitted** | **Permitted** | **Permitted** | Open Skills taxonomy names/categories only; no analytics. | *"Source: Lightcast Open Skills Taxonomy (CC BY 4.0)"* |
| **Commercial Job Boards** | Proprietary Terms of Service (LinkedIn, Indeed) | **PROHIBITED** | **PROHIBITED** | **PROHIBITED** | Unapproved automated scraping is strictly barred by contract. | **DO NOT USE (CRITICAL LEGAL RISK)** |

---

## 4. PRIVACY, PERSONAL DATA & RETENTION REGULATIONS

### 4.1 General Data Protection Regulation (GDPR) & UK Data Protection Act 2018
- **Scope:** Protects identified or identifiable natural persons within the UK and European Economic Area.
- **Application to Employer Intelligence:**
  1. Corporate legal entities (e.g. "Acme Corp Ltd") do **not** have GDPR privacy rights.
  2. However, sole proprietorships, partnerships, and micro-businesses often use the personal names and residential addresses of founders as their registered corporate address.
  3. Job postings frequently contain recruiter names, personal cell phone numbers, and direct email addresses (`john.doe@company.com`).
- **Mandatory Compliance Controls:**
  - **No Sole Proprietors:** Exclude sole traders, unincorporated entities, and companies with <50 employees.
  - **Address Truncation:** Strip street numbers, building names, and apartment numbers; store only City, State/Region, and Country.
  - **PII Regex Filter:** Scrub all personal names, phone numbers, and individual email addresses during text ingestion. Only generic corporate inboxes (`careers@company.com`) may be retained.

### 4.2 California Consumer Privacy Act (CCPA / CPRA)
- Personal information of California residents appearing in public-record job postings must adhere to statutory exemptions (publicly available government records are exempt under Cal. Civ. Code § 1798.140(v)(2)). However, commercial contact details gathered from job boards do not automatically enjoy blanket exemption.
- Enforce the same PII scrubbing pipeline across all US job postings.

### 4.3 India Digital Personal Data Protection Act, 2023 (DPDP Act)
- Section 4 mandates that digital personal data may only be processed for a lawful purpose with consent or for certain legitimate uses.
- Company registration numbers (CIN) and corporate BRSR filings are public statutory filings, but personal Director Identification Numbers (DIN), personal residential addresses of directors, and recruiter contact info must be excised from all Indian datasets.

---

## 5. FORMAL LICENSING RE-QUALIFICATION VERDICT

1. **Fully Approved for Commercial Ingestion & Display:**
   - **WGEA Australia (CC BY 4.0):** 100% legally clear for enterprise headcount bands and gender profiles.
   - **Companies House (OGL v3.0):** 100% legally clear for corporate identity, CRN, status, and SIC codes.
   - **UK Gender Pay Gap (OGL v3.0):** 100% legally clear for workforce size bands (250+ employees).
   - **SEC EDGAR (Public Domain):** 100% legally clear for corporate global headcount, subject to the 10 req/sec User-Agent rate limit.
   - **ACRA Singapore via Data.gov.sg (SODL v1.0):** 100% legally clear for corporate UEN identity resolution.
   - **Lightcast Open Skills (CC BY 4.0):** 100% legally clear for skill taxonomy terminology.
   - **First-Party Greenhouse / Lever Feeds:** 100% legally clear for public job postings explicitly exposed by participating employers.
2. **Strictly Prohibited & Blocked:**
   - **Commercial Aggregator Scraping (LinkedIn, Indeed, Naukri, Seek):** Formally prohibited. Poses unacceptable breach-of-contract and CFAA litigation exposure.
3. **Classified as `LEGAL_REVIEW_REQUIRED` (Withheld from Staging Execution):**
   - **MyCareersFuture Singapore:** Requires formal developer partner agreement with Workforce Singapore.
   - **National Career Service India:** Requires formal institutional registration with MoLE.
   - **Automated MCA21 Ingestion:** Web portal scraping violates ToS; commercial aggregator licensing required for live Indian private company feeds.
