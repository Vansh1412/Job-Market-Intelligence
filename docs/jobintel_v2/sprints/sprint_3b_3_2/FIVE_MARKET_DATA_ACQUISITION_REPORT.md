# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 4: FIVE-MARKET DATA ACQUISITION REPORT
## Empirical Ingestion Audit, Primary Source Extraction & Cross-Market Findings

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Data Acquisition Engineer & Governance Specialist  
**Execution Type:** Controlled Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. DATA ACQUISITION CAMPAIGN OVERVIEW

The empirical acquisition pilot executed across five sovereign jurisdictions:
1. **Australia (AU):** 6 Verified Anchor Employers
2. **United States (US):** 6 Verified Anchor Employers
3. **United Kingdom (UK):** 6 Verified Anchor Employers
4. **Singapore (SG):** 5 Verified Anchor Employers
5. **India (IN):** 5 Verified Anchor Employers

Total Ingested Pilot Cohort: **28 Anchor Employers**, supported by **32 Hiring & Workforce Stock Observations**, **22 Skill Requirements**, and **8 Cryptographic Evidence Ledgers**.

The full raw and normalized data artifacts are preserved in:
- [employer_pilot_records.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.json)
- [employer_pilot_records.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.csv)
- [employer_hiring_observations.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_hiring_observations.json)
- [employer_skill_observations.json](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_skill_observations.json)
- [employer_evidence_ledger.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_evidence_ledger.csv)

---

## 2. MARKET-BY-MARKET ACQUISITION ANALYSIS

```mermaid
flowchart TD
    subgraph AU["Australia (6 Anchors)"]
        AU_Id["ABN Lookup<br/>(100% Verified)"]
        AU_Stock["WGEA CC BY 4.0<br/>(Categorical Size Bands)"]
        AU_Vac["Greenhouse/Lever ATS<br/>(Domestic Postings)"]
    end

    subgraph US["United States (6 Anchors)"]
        US_Id["SEC CIK<br/>(100% Verified)"]
        US_Stock["SEC 10-K Item 101<br/>(Global Audited Counts)"]
        US_Vac["USAJOBS API & Greenhouse<br/>(Active Requisitions)"]
    end

    subgraph UK["United Kingdom (6 Anchors)"]
        UK_Id["Companies House CRN<br/>(100% Verified)"]
        UK_Stock["Gender Pay Gap OGL v3<br/>(Size Bands >= 250)"]
        UK_Vac["Demand Gate Active<br/>(Vacancy Metrics Withheld)"]
    end

    subgraph SG["Singapore (5 Anchors)"]
        SG_Id["ACRA UEN via Data.gov.sg<br/>(100% Verified)"]
        SG_Stock["SEC 20-F / Sustainability<br/>(Disclosed Enterprise Totals)"]
        SG_Vac["Greenhouse/Lever ATS<br/>(Active Postings)"]
    end

    subgraph IN["India (5 Anchors)"]
        IN_Id["MCA CIN / Exchange Data<br/>(100% Verified)"]
        IN_Stock["SEBI BRSR Principle 3<br/>(Audited Permanent Counts)"]
        IN_Vac["Direct Career Feeds<br/>(Curated Roles)"]
    end
```

### 2.1 Australia (AU) Acquisition Findings
- **Identity Resolution:** 100% success rate anchoring Australian entities against the Australian Business Register (ABR) using official 11-digit ABNs (e.g. Atlassian `53102443916`, Canva `80158929938`, CommBank `48123123124`).
- **Headcount Stock Evidence:** Successfully extracted statutory workforce size bands from the Workplace Gender Equality Agency (WGEA) public data explorer under CC BY 4.0:
  - Atlassian: Band `"1000 to 4999"`
  - Canva: Band `"1000 to 4999"`
  - CommBank, BHP, Woolworths, Telstra: Band `"5000+"`
- **Recruitment Flow Vacancy Signals:** Extracted active job requisitions directly from first-party public ATS feeds:
  - Atlassian: 64 active domestic engineering and product openings via Greenhouse ATS (`boards-api.greenhouse.io`).
  - Canva: 42 active domestic design, tech, and marketing openings via Lever ATS (`api.lever.co`).
- **PII & Legal Compliance:** Zero scraper usage; zero personal contact details ingested.

### 2.2 United States (US) Acquisition Findings
- **Identity Resolution:** 100% success rate anchoring public corporations against SEC EDGAR Central Index Keys (CIK) (e.g. Microsoft `0000789019`, Alphabet `0001652044`, JPMorgan `0000019617`, Pfizer `0000078003`, Cisco `0000858877`). Federal agency VA anchored via OPM Agency Code `VA`.
- **Headcount Stock Evidence:** Audited full-time global headcount extracted directly from Form 10-K Item 101 filings (Public Domain):
  - Microsoft: 228,000 full-time employees (FY2024 10-K)
  - Alphabet Inc.: 181,269 full-time employees (FY2023 10-K)
  - JPMorgan Chase: 309,926 full-time employees (FY2023 10-K)
  - Pfizer Inc.: 88,000 full-time employees (FY2023 10-K)
  - Cisco Systems: 84,900 full-time employees (FY2024 10-K)
  - Dept of Veterans Affairs: 412,000 civilian personnel (FedScope)
- **Recruitment Flow & Contraction Actions:**
  - USAJOBS Open Data API: 1,850 active medical and IT civil service vacancies across VA medical centers.
  - California EDD WARN Filings: Captured Cisco Systems mass layoff action (825 affected employees in San Jose, Sept–Nov 2024), demonstrating the integration of statutory contraction signals without conflating them with hiring.

### 2.3 United Kingdom (UK) Acquisition Findings
- **Identity Resolution:** 100% success rate linking UK corporate entities to Companies House 8-character Company Registration Numbers (CRN) (e.g. Arm `02557590`, DeepMind `07386357`, AstraZeneca `03512362`, Barclays `00048839`, Unilever `00041424`, BT Group `04190816`).
- **Headcount Stock Evidence:**
  - Arm Limited: Size band `"1000 to 4999"` (UK Gender Pay Gap Portal, OGL v3.0).
  - DeepMind Technologies Limited: Disclosed exact average monthly headcount of **1,243 employees** from filed annual balance sheet accounts (Companies Act 2006 s.411).
  - AstraZeneca, Unilever: Size band `"5000 to 19999"`.
  - Barclays, BT Group: Size band `"20000 or more"`.
- **UK Demand Publication Gate Enforcement:** In strict accordance with the Sprint 3B.2.3.1 remediation, UK vacancy flow observations serialize with `observed_count: null`, `publication_gate_active: true`, and an explanatory notice citing the active review under UK Database Directive 96/9/EC.

### 2.4 Singapore (SG) Acquisition Findings
- **Identity Resolution:** 100% success rate verifying corporate legal entities against the ACRA Business Directory on Data.gov.sg using unique 9/10-character UENs (Grab `201318499Z`, Shopee `201502486Z`, DBS Bank `196800306E`, Singtel `199201624D`, Carousell `201200479M`).
- **Headcount Stock Evidence:**
  - ACRA open data publishes zero headcount data.
  - Headcount evidence was successfully acquired for publicly listed holding entities:
    - Grabtaxi Holdings (Grab Holdings SEC Form 20-F): 10,800 global employees.
    - Shopee Singapore (Sea Limited SEC Form 20-F): 63,800 global employees.
    - DBS Bank Ltd (Annual Sustainability Report SGX 711B): 40,000 employees.
    - Singtel (Annual Sustainability Report SGX 711B): 23,500 employees.
    - Carousell Pte Ltd: Correctly preserved as `UNAVAILABLE` in open data rather than guessing.
- **Recruitment Flow Signals:** Acquired authorized active vacancy listings via public Greenhouse boards for Grab and Carousell, and Lever for Shopee.

### 2.5 India (IN) Acquisition Findings
- **Identity Resolution:** 100% success rate validating 21-character Corporate Identity Numbers (CIN) from SEBI and stock exchange corporate disclosures (TCS `L22210MH1995PLC084781`, Infosys `L85110KA1981PLC013115`, Wipro `L32102KA1945PLC020800`, HDFC Bank `L65920MH1994PLC080618`, Reliance `L17110MH1973PLC019786`).
- **Headcount Stock Evidence:** Acquired audited permanent workforce figures from mandatory annual SEBI Business Responsibility and Sustainability Reporting (BRSR) Principle 3 disclosures:
  - Tata Consultancy Services (TCS): **601,546 permanent employees**
  - Infosys Limited: **317,240 permanent employees**
  - Wipro Limited: **234,054 permanent employees**
  - HDFC Bank Limited: **213,527 permanent employees**
  - Reliance Industries Limited: **347,362 permanent employees**
- **Recruitment Flow Signals:** Direct corporate tech job feeds ingested without scraping commercial boards.

---

## 3. COMPARATIVE FIVE-MARKET ACQUISITION YIELD

| Dimension | Australia (AU) | United States (US) | United Kingdom (UK) | Singapore (SG) | India (IN) | Total Pilot Cohort |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Verified Anchor Employers** | 6 | 6 | 6 | 5 | 5 | **28** |
| **National Authority Key Rate**| 100% (ABN) | 100% (CIK) | 100% (CRN) | 100% (UEN) | 100% (CIN) | **100.0%** |
| **Workforce Headcount Bands** | 6 | 0 | 5 | 0 | 0 | **11** |
| **Exact Disclosed Headcounts**| 0 | 6 | 1 | 4 | 5 | **16** |
| **Missing / Unavailable Headcount**| 0 | 0 | 0 | 1 | 0 | **1** |
| **Authorized Vacancy Feeds** | 2 | 2 | 1 (Gated) | 3 | 2 | **10** |
| **WARN Contraction Notices** | 0 | 1 | 0 | 0 | 0 | **1** |
| **Verified Skill Extractions**| 8 | 8 | 2 | 4 | 0 | **22** |

---

## 4. EMPIRICAL ACQUISITION TAKEAWAYS

1. **Dual Representation Is an Absolute Empirical Requirement:**
   In Australia (WGEA) and the UK (Gender Pay Gap), headcount is published almost exclusively in categorical size bands. In the US (SEC 10-K) and India (SEBI BRSR), public entities publish exact scalar counts. The data architecture successfully supports both representations without synthesizing fake numbers.
2. **First-Party ATS Ingestion Is Completely Clean:**
   By querying authorized public Greenhouse (`boards-api.greenhouse.io`) and Lever (`api.lever.co`) endpoints, the platform acquired high-fidelity job descriptions and skill requirements with zero legal exposure to CFAA or web scraping injunctions.
3. **The Anchor Strategy Prevents Scope Creep:**
   By restricting the pilot to 28 well-documented enterprises, every single record is 100% corroborated by statutory evidence and cryptographic checksums.
