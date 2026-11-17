# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 2: EMPLOYER COHORT SELECTION REPORT
## Candidate Pool Evaluation, Selection Criteria & Final Anchor Cohort Specification

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Data Architect & Employer Intelligence Researcher  
**Execution Type:** Controlled Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. COHORT DESIGN OBJECTIVES & METHODOLOGY

The goal of Sprint 3B.3.2 is to validate whether JOBINTEL 2.0 can acquire, verify, normalize, classify, and preserve employer intelligence from legitimate, reproducible, and authorized sources.

### 1.1 Non-Negotiable Selection Principles
1. **Evidence Over Quotas:** The platform does not lower verification standards merely to fulfill numerical quotas. Every included employer must possess a legally verifiable corporate identity, an active primary web domain, and traceable source provenance.
2. **Balanced Sector Representation:** The pilot deliberately avoids an exclusive focus on consumer tech giants. It includes major employers across Technology, Financial Services, Healthcare & Pharmaceuticals, Telecommunications, Mining & Materials, and Retail.
3. **Multi-Market Parity:** The cohort targets 5–6 employers across each of the five target economies (Australia, United States, United Kingdom, Singapore, India).
4. **Anchor Cohort vs. National Census:** This cohort is designed as a high-precision **Anchor Employer Pilot**. It does not purport to represent a statistically representative census of national micro-enterprises or local small businesses.

---

## 2. CANDIDATE POOL SCREENING (45 CANDIDATES EVALUATED)

A candidate register of **45 organizations** (9 per market) was constructed and systematically evaluated across four verification gates:
- **Gate 1: Legal Identity & Authority Key** (Can the entity be anchored to an official national register: ABN, CIK, CRN, UEN, CIN?)
- **Gate 2: Workforce Headcount Evidence** (Does an official public disclosure exist: WGEA, SEC 10-K, UK GPG, SEBI BRSR?)
- **Gate 3: Authorized Recruitment Feed** (Does the company operate an accessible first-party ATS board feed like Greenhouse or Lever, or an open government API, without requiring illegal scraping?)
- **Gate 4: Licensing & PII Protection** (Is the source data licensed for commercial reuse and free of personal contact information?)

The full evaluation ledger is preserved in:  
[employer_candidate_register.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_candidate_register.csv)

### 2.1 Screening Summary
```
Evaluated Candidate Pool:         45 Organizations (100.0%)
├── Qualified Anchor Employers:    28 Included     ( 62.2%)
└── Excluded Candidates:           17 Excluded     ( 37.8%)
    ├── Third-Party Staffing Firms: 5 Excluded (Distortion risk)
    ├── Micro-Businesses (<50 staff): 4 Excluded (PII leakage risk)
    ├── Gated Civil Service Portals: 4 Excluded (Institutional login required)
    ├── Unlisted / Zero Disclosures: 3 Excluded (No verifiable data)
    └── Holding Company De-duplication: 1 Excluded (Captured via operating subsidiary)
```

---

## 3. FINAL VERIFIED ANCHOR COHORT (28 EMPLOYERS)

The final cohort comprises **28 verified anchor employers** spanning all five target markets:

```mermaid
pie title Pilot Cohort Distribution by Market (28 Employers)
    "Australia (AU)" : 6
    "United States (US)" : 6
    "United Kingdom (UK)" : 6
    "Singapore (SG)" : 5
    "India (IN)" : 5
```

### 3.1 Market-by-Market Anchor Register

| Market | Company ID | Canonical Name | Industry Sector | Legal Authority ID | Primary Web Domain | Headcount Representation | Recruitment Channel |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AU** | `comp_au_atlassian` | Atlassian Pty Ltd | Technology & Software | ABN 53 102 443 916 | `atlassian.com` | Official Size Band (WGEA) | Greenhouse Public ATS |
| **AU** | `comp_au_canva` | Canva Pty Ltd | Technology & Design | ABN 80 158 929 938 | `canva.com` | Official Size Band (WGEA) | Lever Public ATS |
| **AU** | `comp_au_cba` | Commonwealth Bank of Australia | Financial Services | ABN 48 123 123 124 | `commbank.com.au` | Official Size Band (WGEA) | Corporate Career Portal |
| **AU** | `comp_au_bhp` | BHP Group Limited | Mining & Materials | ABN 49 004 028 077 | `bhp.com` | Official Size Band (WGEA) | Corporate Career Portal |
| **AU** | `comp_au_woolworths`| Woolworths Group Limited | Retail & Consumer | ABN 88 000 014 675 | `woolworthsgroup.com.au` | Official Size Band (WGEA) | Corporate Career Portal |
| **AU** | `comp_au_telstra` | Telstra Group Limited | Telecommunications | ABN 56 086 174 781 | `telstra.com.au` | Official Size Band (WGEA) | Corporate Career Portal |
| **US** | `comp_us_microsoft` | Microsoft Corporation | Technology & Software | SEC CIK 0000789019 | `microsoft.com` | Exact Global Count (SEC 10-K) | Greenhouse / Corporate ATS |
| **US** | `comp_us_alphabet` | Alphabet Inc. | Technology & Internet | SEC CIK 0001652044 | `abc.xyz` | Exact Global Count (SEC 10-K) | Corporate Career Portal |
| **US** | `comp_us_jpmorgan` | JPMorgan Chase & Co. | Financial Services | SEC CIK 0000019617 | `jpmorganchase.com` | Exact Global Count (SEC 10-K) | Corporate Career Portal |
| **US** | `comp_us_pfizer` | Pfizer Inc. | Healthcare & Biopharma | SEC CIK 0000078003 | `pfizer.com` | Exact Global Count (SEC 10-K) | Corporate Career Portal |
| **US** | `comp_us_cisco` | Cisco Systems, Inc. | Technology & Networking | SEC CIK 0000858877 | `cisco.com` | Exact Global Count (SEC 10-K) | Greenhouse / Corporate ATS |
| **US** | `comp_us_fed_va` | U.S. Dept of Veterans Affairs | Public Sector Healthcare| FedScope / Agency VA | `va.gov` | Exact Federal Count (FedScope)| USAJOBS Open Data API |
| **UK** | `comp_uk_arm` | Arm Limited | Semiconductors & Tech | CRN 02557590 | `arm.com` | Official Size Band (UK GPG) | Greenhouse / Corporate ATS |
| **UK** | `comp_uk_deepmind` | DeepMind Technologies Limited| AI Research & Tech | CRN 07386357 | `deepmind.google` | Exact Disclosed Count (Accounts)| Corporate Career Feed |
| **UK** | `comp_uk_astrazeneca`| AstraZeneca PLC | Healthcare & Pharma | CRN 03512362 | `astrazeneca.com` | Official Size Band (UK GPG) | Corporate Career Portal |
| **UK** | `comp_uk_barclays` | Barclays PLC | Financial Services | CRN 00048839 | `barclays.com` | Official Size Band (UK GPG) | Corporate Career Portal |
| **UK** | `comp_uk_unilever` | Unilever PLC | Consumer Goods | CRN 00041424 | `unilever.com` | Official Size Band (UK GPG) | Corporate Career Portal |
| **UK** | `comp_uk_bt` | BT Group plc | Telecommunications | CRN 04190816 | `bt.com` | Official Size Band (UK GPG) | Corporate Career Portal |
| **SG** | `comp_sg_grab` | Grabtaxi Holdings Pte. Ltd. | Technology & Transport | UEN 201318499Z | `grab.com` | Exact Disclosed Count (20-F) | Greenhouse Public ATS |
| **SG** | `comp_sg_shopee` | Shopee Singapore Private Ltd | E-commerce & Retail | UEN 201502486Z | `shopee.sg` | Exact Disclosed Count (Sea 20-F)| Lever / Corporate ATS |
| **SG** | `comp_sg_dbs` | DBS Bank Ltd. | Financial Services | UEN 196800306E | `dbs.com` | Exact Disclosed Count (Report) | Corporate Career Portal |
| **SG** | `comp_sg_singtel` | Singapore Telecommunications | Telecommunications | UEN 199201624D | `singtel.com` | Exact Disclosed Count (Report) | Corporate Career Portal |
| **SG** | `comp_sg_carousell`| Carousell Pte. Ltd. | Technology & E-commerce | UEN 201200479M | `carousell.com` | *Unavailable in Open Data* | Greenhouse Public ATS |
| **IN** | `comp_in_tcs` | Tata Consultancy Services Ltd| IT & Software Services | CIN L22210MH1995PLC084781 | `tcs.com` | Exact Audited Count (SEBI BRSR)| Corporate Career Portal |
| **IN** | `comp_in_infosys` | Infosys Limited | IT & Software Services | CIN L85110KA1981PLC013115 | `infosys.com` | Exact Audited Count (SEBI BRSR)| Corporate Career Portal |
| **IN** | `comp_in_wipro` | Wipro Limited | IT & Software Services | CIN L32102KA1945PLC020800 | `wipro.com` | Exact Audited Count (SEBI BRSR)| Corporate Career Portal |
| **IN** | `comp_in_hdfcbank` | HDFC Bank Limited | Financial Services | CIN L65920MH1994PLC080618 | `hdfcbank.com` | Exact Audited Count (SEBI BRSR)| Corporate Career Portal |
| **IN** | `comp_in_reliance` | Reliance Industries Limited | Conglomerate & Telecom | CIN L17110MH1973PLC019786 | `ril.com` | Exact Audited Count (SEBI BRSR)| Corporate Career Portal |

---

## 4. SECTORAL DIVERSITY OF THE ANCHOR COHORT

| Industry Sector | Employer Count | Representative Organizations |
| :--- | :---: | :--- |
| **Technology & Software** | 10 | Atlassian, Canva, Microsoft, Alphabet, Cisco, Arm, DeepMind, Grab, Shopee, Carousell |
| **IT Services & Consulting** | 3 | Tata Consultancy Services, Infosys, Wipro |
| **Financial Services & Banking** | 5 | Commonwealth Bank of Australia, JPMorgan Chase, Barclays, DBS Bank, HDFC Bank |
| **Telecommunications** | 3 | Telstra, BT Group, Singtel |
| **Healthcare & Pharmaceuticals** | 3 | Pfizer, AstraZeneca, U.S. Dept of Veterans Affairs |
| **Retail & Consumer Goods** | 2 | Woolworths Group, Unilever |
| **Mining & Energy / Conglomerate** | 2 | BHP Group, Reliance Industries |
| **Total Pilot Cohort** | **28** | **Comprehensive multi-market, multi-industry anchor group** |

---

## 5. DOCUMENTED EXCLUSION ANALYSIS (17 EXCLUDED CANDIDATES)

1. **Staffing Agencies & Recruitment Intermediaries (5 Excluded):**
   - *Candidates:* Aussie Tech Staffing (AU), Robert Half (US), Hays Specialist Recruitment (UK), Adecco Personnel (SG), TeamLease Services (IN).
   - *Exclusion Rationale:* Intermediary agencies post job advertisements on behalf of third-party clients. Ingesting these postings under the agency's name misleads users into believing the staffing firm has thousands of internal engineering openings.
2. **Micro-Businesses & Sole Proprietorships (4 Excluded):**
   - *Candidates:* Sydney Local Coffee Roasters (AU), Acme Cyber Solutions (US), Boutique FinTech Advisory (UK), Singapore Web Boutique (SG).
   - *Exclusion Rationale:* Entities with $<50$ employees frequently operate from domestic residential addresses and lack audited corporate disclosures. Excluding them prevents PII violations under GDPR, CCPA, and DPDP.
3. **Gated Civil Service Platforms (4 Excluded):**
   - *Candidates:* Australian Taxation Office (AU), NHS Barts Trust (UK), GovTech Singapore (SG), National Informatics Centre (IN).
   - *Exclusion Rationale:* Vacancy feeds require institutional partner API keys or SingPass logins that are not accessible via open public developer credentials.
4. **Unlisted Private Companies with Zero Disclosures (3 Excluded):**
   - *Candidates:* Bangalore Software Solvers (IN), Target Brands Inc (US aggregator gated), Tata Motors (IN deferred to Phase 2).
   - *Exclusion Rationale:* Lack of accessible, non-scraped data sources.
5. **Holding Company De-duplication (1 Excluded):**
   - *Candidate:* Sea Limited (SG). Excluded as an independent operating entity to prevent double-counting with its primary operating subsidiary, Shopee Singapore Pte. Ltd.
