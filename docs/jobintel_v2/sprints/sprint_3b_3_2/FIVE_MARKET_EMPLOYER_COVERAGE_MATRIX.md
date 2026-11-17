# SPRINT 3B.3.2 — DELIVERABLE 14
# FIVE-MARKET EMPLOYER COVERAGE MATRIX
## Sovereign Legal Registries, Headcount Sources, ATS Ecosystems & Data Acquisition Strategies

---

## 1. CROSS-MARKET COMPARATIVE MATRIX

The table below presents a qualitative comparative analysis across the ten critical operational dimensions for the five target markets. Numerical scoring has been omitted in accordance with governance guidelines.

| Evaluation Dimension | Australia (AU) | United States (US) | United Kingdom (UK) | Singapore (SG) | India (IN) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Statutory Registry Availability** | **Open Data** (ABR bulk & API via data.gov.au) | **Open Data** (SEC EDGAR public access) | **Open Data** (Companies House REST API) | **Open Data** (ACRA via data.gov.sg bulk) | **Gated / Captcha** (MCA portal requires manual OTP/session) |
| **2. Headcount Data Availability** | **Statutory Bands** (WGEA mandatory public reporting) | **Statutory Exact** (SEC 10-K Item 1 / Item 101) | **Statutory Bands** (Gender Pay Gap Service) | **Aggregate Only** (MOM census; employer-level restricted) | **Statutory Exact** (SEBI BRSR for top 1,000 listed entities) |
| **3. Vacancy Data Availability** | **Government + ATS** (JSA IVI aggregates + Greenhouse) | **ATS Dominant** (Greenhouse, Lever, Workday) | **ATS Dominant** (Workday, Taleo; ONS withheld) | **Government + ATS** (MyCareersFuture + ATS feeds) | **Commercial Dominant** (Naukri; career sites custom) |
| **4. ATS Ecosystem Penetration** | **High** (Greenhouse, Lever, Workday widely used) | **Very High** (Standardized APIs across ~85% tech/corp) | **High** (Workday, Taleo, Greenhouse) | **Moderate to High** (Greenhouse, Lever, Workday) | **Moderate** (Mixed: Darwinbox, custom portals, Workday) |
| **5. Corporate Hierarchy Data** | **Partial** (ASIC extracts fee-gated; WGEA group data) | **High** (SEC 10-K Exhibit 21 list of subsidiaries) | **High** (Companies House PSC register) | **Partial** (ACRA corporate extract fee-based) | **High** (SEBI BRSR Section A corporate parentage) |
| **6. Industry Classification** | **ANZSIC 2006** (Standard in ABR & WGEA) | **NAICS 2022 / SIC** (Standard in SEC & BLS) | **UK SIC 2007** (Standard in Companies House) | **SSIC 2020** (Standard in ACRA) | **NIC 2008** (Standard in MCA & SEBI) |
| **7. Sovereign Entity Identifier** | **ABN** (11 digits, 100% resolvable) | **CIK / EIN** (10-digit CIK, 9-digit EIN) | **CRN** (8 digits, Companies House) | **UEN** (9–10 alphanumeric characters) | **CIN / LLPIN** (21 alphanumeric characters) |
| **8. Licensing Compatibility** | **CC-BY 3.0 / 4.0 AU** (Commercial reuse permitted) | **US Public Domain** (Federal government work) | **OGL v3.0** (Open Government Licence) | **Singapore Open Data** (Terms of Use compatible) | **Restricted / Public** (SEBI public disclosure) |
| **9. Acquisition Cost** | **Free** (ABR, data.gov.au, WGEA) | **Free** (SEC EDGAR public endpoints) | **Free** (Companies House API token) | **Free** (data.gov.sg datasets) | **Free for Listed** (SEBI/BSE); MCA requires manual work |
| **10. Update Frequency** | **Weekly (ABR) / Annual (WGEA)** | **Quarterly / Annual** (10-Q / 10-K) | **Real-time API** (Companies House) | **Monthly (ACRA bulk updates)** | **Annual** (BRSR filings post-audit) |

---

## 2. DETAILED SOVEREIGN MARKET PROFILES

### 2.1 Australia (AU)
- **Market Classification:** **`STRONG`**
- **Key Strengths:**
  - Complete, openly accessible business registry via the Australian Business Register (ABR) bulk data extract on data.gov.au under CC-BY 3.0 AU.
  - Unique statutory headcount reporting via the Workplace Gender Equality Agency (WGEA) covering all private employers with $\ge 100$ employees in structured size bands.
  - Established ATS API adoption (Greenhouse and Lever) across technology and financial firms.
- **Critical Gaps & Limitations:**
  - WGEA reports headcount in categorical bands (`"1000 to 4999"`), not exact headcounts.
  - Detailed ASIC company extracts (shareholding, directorships) are fee-gated ($10–$20 per extract).
- **Recommended Strategy for MVP:**
  - Ingest ABR bulk data for canonical legal entities and ABN validation.
  - Link WGEA public dataset for statutory headcount size bands.
  - Direct Greenhouse/Lever ingestion for tech cohort vacancies.
- **Scaling Path to 50–100 Employers:**
  - Scale through ASX 200 constituent filings and WGEA annual compliance reporting.

---

### 2.2 United States (US)
- **Market Classification:** **`STRONG`**
- **Key Strengths:**
  - Gold-standard corporate disclosure via the SEC EDGAR system (Forms 10-K and 10-Q) in public domain.
  - Exact global headcount disclosures published annually under Item 1 / Item 101.
  - Complete listing of significant subsidiaries provided under Form 10-K Exhibit 21.
  - Deepest penetration of public-facing ATS endpoints globally.
- **Critical Gaps & Limitations:**
  - Federal business registration is fragmented across 50 state secretaries of state (e.g. Delaware, California, New York), making a single unified national private company registry unavailable.
  - EEO-1 establishment headcount reports remain confidential under Section 709(e) of Title VII.
- **Recommended Strategy for MVP:**
  - Utilize SEC EDGAR Company Facts API for public corporations (CIK, exact headcount, NAICS, subsidiaries).
  - Target public tech, financial, and industrial anchor corporations.
- **Scaling Path to 50–100 Employers:**
  - Expand ingestion to S&P 500 / Russell 1000 filings via automated EDGAR JSON endpoints.

---

### 2.3 United Kingdom (UK)
- **Market Classification:** **`MODERATE`** *(Demands Publication Gate Active)*
- **Key Strengths:**
  - World-class public registry API (Companies House) offering free, real-time REST queries for company status, registered office, and Persons with Significant Control (PSC).
  - Mandatory public headcount size reporting under the UK Gender Pay Gap reporting service for employers with $\ge 250$ staff.
- **Critical Gaps & Limitations:**
  - **Demand Publication Gate:** ONS vacancy and Adzuna job demand data remains withheld pending licensing and source-use review. Vacancy flow metrics cannot be displayed.
  - Micro and small business accounts file dormant or abbreviated balance sheets with zero headcount disclosure.
- **Recommended Strategy for MVP:**
  - Utilize Companies House API for legal entity verification and CRN resolution.
  - Utilize Gender Pay Gap public data for statutory establishment size bands.
  - Maintain the UK demand publication gate strictly active (`publication_gate_active: true`, `flow_vacancies = null`).
- **Scaling Path to 50–100 Employers:**
  - Expand across FTSE 100/250 constituents using Companies House and Gender Pay Gap data.

---

### 2.4 Singapore (SG)
- **Market Classification:** **`MODERATE`**
- **Key Strengths:**
  - Unified business registration via the Accounting and Corporate Regulatory Authority (ACRA) with authoritative Unique Entity Numbers (UEN).
  - High ATS adoption among regional multinational headquarters.
  - Official government job portal (MyCareersFuture) operates under open government terms.
- **Critical Gaps & Limitations:**
  - Ministry of Manpower (MOM) comprehensive employment surveys publish national/sectoral aggregate data; individual employer headcounts are treated as confidential statistical returns under the Statistics Act.
  - Detailed ACRA shareholder and financial statements require fee-based BizFile purchases.
- **Recommended Strategy for MVP:**
  - Ingest ACRA open entity directory from data.gov.sg for UEN verification.
  - Acquire vacancy data from official corporate career portals and public ATS endpoints.
  - Classify headcount into standard regional enterprise tiers based on statutory public releases.
- **Scaling Path to 50–100 Employers:**
  - Ingest Straits Times Index (STI) constituents and top regional technology employers.

---

### 2.5 India (IN)
- **Market Classification:** **`MODERATE`** *(Listed Sector Strong / Private Sector Gated)*
- **Key Strengths:**
  - Highly detailed Business Responsibility and Sustainability Reporting (BRSR) mandated by the Securities and Exchange Board of India (SEBI) for the top 1,000 listed companies.
  - BRSR Section A provides exact permanent and non-permanent employee headcounts, gender disaggregation, and corporate parentage.
- **Critical Gaps & Limitations:**
  - The Ministry of Corporate Affairs (MCA) MCA21 portal enforces interactive CAPTCHAs, preventing automated API ingestion for unlisted private entities.
  - National Career Service (NCS) API access is restricted to authorized institutional partners.
  - ATS landscape is fragmented between global platforms (Workday) and domestic systems (Darwinbox).
- **Recommended Strategy for MVP:**
  - Anchor India coverage strictly to Nifty 50 and Nifty Next 50 listed corporations with audited SEBI BRSR filings.
  - Ingest verified corporate websites and official ATS endpoints for tech/finance leaders.
  - Do NOT attempt to scrape MCA21 portal or bypass access controls.
- **Scaling Path to 50–100 Employers:**
  - Systematically ingest SEBI BRSR filings across the top 100 NSE/BSE listed corporations.

---

## 3. SUMMARY OF MARKET ADAPTABILITY FOR MVP

```
+----------------------------------------------------------------------------------------------------+
| FIVE-MARKET ACQUISITION ROADMAP FOR MVP (100 ANCHOR EMPLOYERS)                                     |
+--------+------------------+------------------------------+-----------------------------------------+
| Market | Planned Cohort   | Primary Statutory Source     | Vacancy Acquisition Channel             |
+--------+------------------+------------------------------+-----------------------------------------+
| AU     | 25 Employers     | ABR Bulk + WGEA Size Bands   | Greenhouse / Lever Public ATS APIs      |
| US     | 25 Employers     | SEC EDGAR 10-K Filings       | Greenhouse / Lever / Workday ATS APIs   |
| UK     | 20 Employers     | Companies House + GPG Portal | Careers Pages (Flow Withheld / Gated)   |
| SG     | 15 Employers     | ACRA Registry + BizFile Pub  | Regional Career Sites / Public ATS APIs |
| IN     | 15 Employers     | SEBI BRSR Annual Disclosures | Corporate Career Portals / Workday      |
+--------+------------------+------------------------------+-----------------------------------------+
| TOTAL  | 100 Employers    | 100% Authorized Statutory    | Zero Commercial Scraping                |
+--------+------------------+------------------------------+-----------------------------------------+
```
