# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER SOURCE RESEARCH ACROSS FIVE GLOBAL MARKETS
### Authoritative Registries, Corporate Disclosures, Regulatory Headcount & Recruitment Feeds

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-SOURCE-RESEARCH`  
**Execution Phase:** Phase 0 (Read-Only Research Audit)  
**Date of Audit:** 2026-11-17  
**Scope:** Exhaustive evaluation of employer data sources across India (IN), United States (US), United Kingdom (UK), Australia (AU), and Singapore (SG).

---

## 1. RESEARCH METHODOLOGY & SOURCE CLASSIFICATION

Employer data sources fall into four distinct institutional categories:
1. **Statutory Corporate Registries:** Authoritative government bodies responsible for legal company formation, corporate identification numbers, legal names, and active status.
2. **Mandatory Corporate Disclosures & Filings:** Regulatory financial and ESG filings (e.g. SEC 10-K, WGEA Australia, BSE/NSE BRSR) that contain legally certified headcount and human capital disclosures.
3. **Primary Employer Career Portals & Applicant Tracking Systems (ATS):** Direct corporate recruitment endpoints (e.g. Greenhouse, Workday, Lever, SmartRecruiters) reflecting active recruitment marketing postings.
4. **Secondary Commercial Job Aggregators & Statistical Agencies:** Commercial platforms (Naukri, Indeed, LinkedIn) and official statistical bodies (BLS, ONS, ABS, MOM).

> [!CRITICAL]
> **Statutory Microdata Confidentiality Rule:**  
> Statistical agencies (US BLS, UK ONS, Australia ABS, Singapore MOM, India MoSPI) operate under strict non-disclosure statutes (e.g. US CIPSEA, UK Statistics of Trade Act 1947, Australian Census and Statistics Act 1905). **They legally cannot and do not disclose establishment-level vacancy or hiring counts for identifiable employers.**

---

## 2. DETAILED SOURCE AUDIT: UNITED STATES (US)

### Source US-1: SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval)
1. **Source Name:** SEC EDGAR Company Database & Submissions API
2. **Publisher or Owner:** U.S. Securities and Exchange Commission (SEC)
3. **Official URL:** `https://www.sec.gov/edgar/searchedgar/companysearch` | API: `https://data.sec.gov/`
4. **Geographic Coverage:** United States & Foreign Private Issuers listed on US exchanges.
5. **Employer Population Covered:** ~7,000+ publicly traded domestic and foreign corporations.
6. **Available Fields:** Central Index Key (CIK), Legal Entity Name, Standard Industrial Classification (SIC), IRS Employer Identification Number (EIN), State of Incorporation, Fiscal Year End, Business Address, Form 10-K Human Capital Disclosures (Item 1: total employees, full-time vs part-time, seasonal workers, geographical distribution, turnover metrics where disclosed).
7. **Update Frequency:** Annual (10-K), Quarterly (10-Q), Event-driven (8-K).
8. **Historical Coverage:** Complete digital archives from 1994 to present (30+ years).
9. **Access Method:** Direct REST API (`data.sec.gov/submissions/CIK{cik.zfill(10)}.json`), bulk archive downloads, and EDGAR full-text search.
10. **API or Download Availability:** Fully programmatic REST API returning JSON payloads, bulk zip archives of XBRL data.
11. **Authentication Requirements:** None. Mandatory requirement: Custom `User-Agent` header in format `Sample Company Name AdminContact@<sample company domain>.com`.
12. **Licensing and Redistribution Terms:** Public Domain (Work of the United States Government under 17 U.S.C. § 105).
13. **Commercial SaaS Reuse Restrictions:** Completely unrestricted for commercial SaaS ingestion and redistribution. Rate limited to a maximum of 10 requests per second.
14. **Attribution Requirements:** Citation recommended ("Source: U.S. Securities and Exchange Commission EDGAR System").
15. **Known Data Limitations:** Covers public companies only. Non-public private employers (over 90% of US firms) are completely absent. Human capital metrics in Item 1 are qualitative/semi-quantitative; companies have flexibility in how they report headcount categories.
16. **Company-Level Hiring Evidence:** **Supports Employment Stock and Change, NOT Real-Time Hiring Openings.** (Discloses annual total headcount and year-over-year delta).

---

### Source US-2: Bureau of Labor Statistics (BLS) Establishment Programs (OEWS / QCEW / MWR)
1. **Source Name:** BLS Occupational Employment and Wage Statistics (OEWS) & Quarterly Census of Employment and Wages (QCEW)
2. **Publisher or Owner:** U.S. Bureau of Labor Statistics / Department of Labor
3. **Official URL:** `https://www.bls.gov/oes/` | `https://www.bls.gov/cew/`
4. **Geographic Coverage:** United States nationwide, all 50 states, DC, Puerto Rico, Guam, Virgin Islands.
5. **Employer Population Covered:** ~1.1 million establishments surveyed annually (OEWS); ~11.5 million employer worksites reporting unemployment insurance taxes (QCEW).
6. **Available Fields:** Industry (NAICS), County/Metropolitan Area, Occupational employment counts, Wage percentiles (P10, P25, P50, P75, P90).
7. **Update Frequency:** Annual (OEWS), Quarterly (QCEW).
8. **Historical Coverage:** Comprehensive historical series from 1997 to present.
9. **Access Method:** Public Flat Files (Excel/CSV), LABSTAT Text Files, and BLS Public Data API v2.
10. **API or Download Availability:** Public download tables and REST API (`api.bls.gov`).
11. **Authentication Requirements:** API key optional (free registration grants 500 requests/day, 50 queries/request).
12. **Licensing and Redistribution Terms:** Public Domain (US Federal Government).
13. **Commercial SaaS Reuse Restrictions:** None.
14. **Attribution Requirements:** Mandatory citation ("U.S. Bureau of Labor Statistics").
15. **Known Data Limitations:** **CONFIDENTIALITY RESTRICTIONS (CIPSEA):** Under the Confidential Information Protection and Statistical Efficiency Act (44 U.S.C. § 3571-3572), individual employer establishment data is strictly confidential. Data is suppressed ($N < 3$ or dominance rule) and aggregated to industry-geographic cells.
16. **Company-Level Hiring Evidence:** **DOES NOT SUPPORT COMPANY-LEVEL HIRING.** Provides industry and occupation benchmarks only.

---

### Source US-3: State WARN Act Notice Repositories (Worker Adjustment and Retraining Notification)
1. **Source Name:** State Department of Labor WARN Act Disclosures
2. **Publisher or Owner:** Individual State Workforce Agencies (e.g., California EDD, New York State Department of Labor, Texas Workforce Commission).
3. **Official URL:** State-specific (e.g., `https://edd.ca.gov/en/jobs_and_training/Layoff_Services_WARN` / `https://dol.ny.gov/warn-notices`).
4. **Geographic Coverage:** United States, partitioned by state.
5. **Employer Population Covered:** Employers with 100+ full-time employees initiating mass layoffs (50+ employees) or plant closings.
6. **Available Fields:** Company Name, Worksite Address, City, County, Number of Affected Workers, Notice Date, Effective Layoff Date, Reason for Layoff, Union Representation.
7. **Update Frequency:** Semi-monthly or monthly.
8. **Historical Coverage:** Typically 5 to 10 years maintained on state workforce agency websites.
9. **Access Method:** Public CSV/Excel downloads and HTML web tables.
10. **API or Download Availability:** Direct file downloads on state portals.
11. **Authentication Requirements:** None.
12. **Licensing and Redistribution Terms:** Public record / public domain state administrative government data.
13. **Commercial SaaS Reuse Restrictions:** Permitted for factual redistribution.
14. **Attribution Requirements:** Citation to reporting state workforce agency.
15. **Known Data Limitations:** Negative hiring signal only (layoffs/restructuring); decentralized across 50 state formats; unstandardized company legal names.
16. **Company-Level Hiring Evidence:** **Provides Negative Employment Shocks (Workforce Reductions).**

---

### Source US-4: SAM.gov & USASpending.gov Federal Contractor Database
1. **Source Name:** SAM.gov Entity Management & USASpending.gov Award Search
2. **Publisher or Owner:** U.S. General Services Administration (GSA) / Bureau of the Fiscal Service
3. **Official URL:** `https://sam.gov/` | API: `https://api.usaspending.gov/`
4. **Geographic Coverage:** United States & international entities doing business with US federal government.
5. **Employer Population Covered:** ~500,000+ active federal contractors, grantees, and recipients.
6. **Available Fields:** Unique Entity Identifier (SAM UEI), CAGE Code, Legal Business Name, Doing Business As (DBA), Physical Address, Congressional District, NAICS Codes, PSC Codes, Federal Contract Obligations, Sub-awards, Parent UEI.
7. **Update Frequency:** Daily / Weekly.
8. **Historical Coverage:** Fiscal Year 2008 to present.
9. **Access Method:** Public REST API, monthly database snapshots, raw API endpoints.
10. **API or Download Availability:** Complete REST API with extensive filtering.
11. **Authentication Requirements:** None for public USASpending API; SAM.gov public API requires free GSA API key.
12. **Licensing and Redistribution Terms:** Public Domain (US Federal Government).
13. **Commercial SaaS Reuse Restrictions:** None.
14. **Attribution Requirements:** Citation recommended.
15. **Known Data Limitations:** Skewed toward defense, aerospace, IT services, healthcare, and federal research contractors; non-contracting commercial B2C/B2B tech firms are absent.
16. **Company-Level Hiring Evidence:** **Indirect Evidence (Contract expansions indicate workforce demand, but does not provide direct vacancy counts).**

---

### Source US-5: Primary Employer Applicant Tracking System (ATS) Career Feeds
1. **Source Name:** Corporate Career Feeds (Greenhouse, Lever, Workday, SmartRecruiters)
2. **Publisher or Owner:** Direct Operating Employers via ATS vendors
3. **Official URL:** Company career subdomains (e.g., `boards.greenhouse.io/{company}`, `jobs.lever.co/{company}`)
4. **Geographic Coverage:** United States & global operating locations.
5. **Employer Population Covered:** Technology enterprises, high-growth startups, and mid-to-large corporates utilizing modern ATS platforms.
6. **Available Fields:** Requisition ID, Job Title, Department/Team, Office Location (City, State, Remote status), Job Description, Minimum Qualifications, Preferred Skills, Pay Transparency Compensation Ranges (where mandated by CA/CO/NY/WA laws), Publication Timestamp.
7. **Update Frequency:** Real-time / Daily.
8. **Historical Coverage:** Ephemeral (postings vanish when closed or filled).
9. **Access Method:** Public job board JSON APIs (e.g. Greenhouse public API: `api.greenhouse.io/v1/boards/{board_token}/jobs`), public RSS/XML feeds, or structured schema.org/JobPosting HTML.
10. **API or Download Availability:** Many ATS platforms provide standard, publicly open JSON endpoints designed for company websites.
11. **Authentication Requirements:** None for public job board endpoints.
12. **Licensing and Redistribution Terms:** Employer-owned recruitment announcements. Publicly available marketing collateral.
13. **Commercial SaaS Reuse Restrictions:** Terms of Service typically allow candidate discovery and search indexing, but prohibit unauthorized candidate application submission or commercial candidate fee extraction. Must respect `robots.txt` and rate limits.
14. **Attribution Requirements:** Must clearly display employer name, link to original job posting URL, and date observed.
15. **Known Data Limitations:** Reflects recruitment marketing postings, not confirmed hires; "ghost jobs" (evergreen postings with no active hiring manager allocation); variable structured data quality.
16. **Company-Level Hiring Evidence:** **Supports Direct Company-Level Recruitment Observations (JOB_ADVERTISEMENT).**

---

## 3. DETAILED SOURCE AUDIT: UNITED KINGDOM (UK)

### Source UK-1: Companies House Service
1. **Source Name:** Companies House Public Register API & Bulk Data Products
2. **Publisher or Owner:** Companies House (Executive agency of the Department for Business and Trade)
3. **Official URL:** `https://find-and-update.company-information.service.gov.uk/` | API: `https://developer.company-information.service.gov.uk/`
4. **Geographic Coverage:** United Kingdom (England, Wales, Scotland, Northern Ireland).
5. **Employer Population Covered:** ~5.2 million registered UK companies (active and dissolved).
6. **Available Fields:** Company Number (CRN), Legal Company Name, Company Status (Active, Dissolved, Liquidation), Company Type (Private Limited, PLC, LLP), Registered Office Address, Date of Creation, Nature of Business (UK Standard Industrial Classification - SIC 2007), Confirmation Statement filing dates, Accounts filing dates, Previous Company Names, Officer/Director listings, Disclosed Average Number of Employees (in Full Accounts filings).
7. **Update Frequency:** Real-time / Daily.
8. **Historical Coverage:** Complete corporate history since company incorporation (decades).
9. **Access Method:** REST API (`api.company-information.service.gov.uk`), Streaming API, and Monthly Free Bulk Data Downloads.
10. **API or Download Availability:** Free JSON REST API and full CSV database dumps.
11. **Authentication Requirements:** Requires free registered developer account and Basic Auth API Key.
12. **Licensing and Redistribution Terms:** **Open Government Licence v3.0 (OGL v3.0).**
13. **Commercial SaaS Reuse Restrictions:** Fully permitted for commercial reuse, adaptation, and SaaS publication under OGL v3.0 terms.
14. **Attribution Requirements:** Mandatory attribution statement: *"Contains public sector information licensed under the Open Government Licence v3.0."*
15. **Known Data Limitations:** Micro-entities and small companies are exempt from full accounts and only file balance sheets without employee counts; employee count is an annual average rather than point-in-time vacancies.
16. **Company-Level Hiring Evidence:** **Authoritative Entity Verification & Annual Headcount Disclosures.**

---

### Source UK-2: Home Office Register of Licensed Sponsors (Worker and Temporary Worker)
1. **Source Name:** Register of Licensed Sponsors: Worker & Temporary Worker
2. **Publisher or Owner:** UK Home Office / UK Visas and Immigration (UKVI)
3. **Official URL:** `https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers`
4. **Geographic Coverage:** United Kingdom nationwide.
5. **Employer Population Covered:** ~100,000+ UK registered businesses holding active Tier 2 / Skilled Worker sponsor licences.
6. **Available Fields:** Organisation Name, Town/City, County, Type & Rating (Worker - Skilled Worker, Global Business Mobility, Scale-up, Temporary Worker), Route Tier.
7. **Update Frequency:** Daily / Weekly.
8. **Historical Coverage:** Point-in-time daily active register snapshots.
9. **Access Method:** Direct CSV download from `gov.uk`.
10. **API or Download Availability:** Publicly accessible direct CSV download URL.
11. **Authentication Requirements:** None.
12. **Licensing and Redistribution Terms:** **Open Government Licence v3.0 (OGL v3.0).**
13. **Commercial SaaS Reuse Restrictions:** Completely permitted for commercial integration and analysis.
14. **Attribution Requirements:** Mandatory OGL v3.0 acknowledgement.
15. **Known Data Limitations:** Indicates legal authorization to sponsor overseas workers, not specific live vacancies; does not provide total company employee counts.
16. **Company-Level Hiring Evidence:** **Verified International Hiring Authorization & Operational Locations.**

---

### Source UK-3: ONS Inter-Departmental Business Register (IDBR) / Business Demography
1. **Source Name:** ONS Business Demography & UK Business: Activity, Size and Location
2. **Publisher or Owner:** Office for National Statistics (ONS)
3. **Official URL:** `https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation`
4. **Geographic Coverage:** United Kingdom.
5. **Employer Population Covered:** ~2.7 million VAT and/or PAYE registered businesses.
6. **Available Fields:** Aggregate counts of enterprises by employment size band (micro: 0-9, small: 10-49, medium: 50-249, large: 250+), 4-digit SIC 2007 industry classification, and administrative geography (Local Authority, Region).
7. **Update Frequency:** Annual.
8. **Historical Coverage:** Comprehensive annual series from 2000 to present.
9. **Access Method:** Excel/CSV data tables via ONS website and Nomis portal.
10. **API or Download Availability:** Nomis API (`nomisweb.co.uk`) and ONS Open Data API.
11. **Authentication Requirements:** None for public data.
12. **Licensing and Redistribution Terms:** Open Government Licence v3.0 (OGL v3.0).
13. **Commercial SaaS Reuse Restrictions:** Permitted with attribution.
14. **Attribution Requirements:** Mandatory OGL attribution ("Source: Office for National Statistics").
15. **Known Data Limitations:** **CONFIDENTIALITY RESTRICTIONS:** Under the Statistics of Trade Act 1947, identifiable business microdata is strictly confidential. No individual company name or individual vacancy count is disclosed.
16. **Company-Level Hiring Evidence:** **DOES NOT SUPPORT COMPANY-LEVEL HIRING.** Benchmark use only.

---

## 4. DETAILED SOURCE AUDIT: AUSTRALIA (AU)

### Source AU-1: Australian Business Register (ABR) / ABN Lookup
1. **Source Name:** ABN Lookup & Australian Business Register Bulk Data
2. **Publisher or Owner:** Australian Taxation Office (ATO) on behalf of the Registrar of the Australian Business Register
3. **Official URL:** `https://abr.business.gov.au/` | `https://data.gov.au/data/dataset/abn-bulk-extract`
4. **Geographic Coverage:** Australia nationwide (all states and territories).
5. **Employer Population Covered:** ~8 million active and inactive Australian Business Numbers (ABNs).
6. **Available Fields:** Australian Business Number (ABN), Australian Company Number (ACN), Entity Legal Name, Business Trading Names, Entity Type (Australian Private Company, Public Company, Partnership, Sole Trader), Registration Status (Active/Cancelled), Effective Registration Dates, Australian Postcode, State/Territory, Goods and Services Tax (GST) registration status, Deductible Gift Recipient (DGR) status.
7. **Update Frequency:** Daily online lookup; weekly XML bulk database extract.
8. **Historical Coverage:** Inception of ABN system (2000) to present.
9. **Access Method:** ABR Web Services (SOAP/XML API), public web lookup, and weekly bulk extract on `data.gov.au`.
10. **API or Download Availability:** Free programmatic web service API and complete bulk XML extract.
11. **Authentication Requirements:** Web services require free ABR GUID registration.
12. **Licensing and Redistribution Terms:** **Data.gov.au Terms / Australian Government Open Access.** Bulk extract is provided for public reference and commercial validation.
13. **Commercial SaaS Reuse Restrictions:** Permitted for entity validation and business identification; marketing or direct mail solicitation using registry data is restricted under Privacy Act 1988 guidelines.
14. **Attribution Requirements:** Must state: *"Data sourced from the Australian Business Register."*
15. **Known Data Limitations:** Does not include employee counts, industry codes in public free extract, or hiring indicators.
16. **Company-Level Hiring Evidence:** **Authoritative Entity Verification & Australian Corporate Primary Key.**

---

### Source AU-2: Workplace Gender Equality Agency (WGEA) Employer Data
1. **Source Name:** WGEA Public Reporting Employer Data & Gender Pay Gap Register
2. **Publisher or Owner:** Workplace Gender Equality Agency (Australian Statutory Agency)
3. **Official URL:** `https://www.wgea.gov.au/data-and-insights/employer-data` | `https://data.gov.au/`
4. **Geographic Coverage:** Australia nationwide.
5. **Employer Population Covered:** All non-public sector employers with 100 or more employees in Australia (~5,000+ major employers).
6. **Available Fields:** ABN, Legal Organisation Name, Trading Name, ANZSIC 4-digit Industry, Total Employee Headcount, Headcount breakdown by gender (male, female, non-binary), Employment Status (Full-time, Part-time, Casual), Occupational Category breakdown (Managers, Professionals, Technicians & Trades, Community & Personal Service, Clerical & Admin, Sales, Machinery Operators, Labourers), Governing Body composition, Employer Gender Pay Gap statistics.
7. **Update Frequency:** Annual (reporting year May to April).
8. **Historical Coverage:** Annual public datasets from 2013-14 to present (11 years).
9. **Access Method:** Direct CSV/Excel downloads via WGEA Data Explorer and `data.gov.au`.
10. **API or Download Availability:** Bulk structured tabular CSV downloads.
11. **Authentication Requirements:** None.
12. **Licensing and Redistribution Terms:** **Creative Commons Attribution 4.0 International (CC BY 4.0).**
13. **Commercial SaaS Reuse Restrictions:** Fully permitted for commercial reuse, data enrichment, and redistribution under CC BY 4.0 terms.
14. **Attribution Requirements:** Mandatory attribution: *"Source: Workplace Gender Equality Agency (WGEA), Commonwealth of Australia, licensed under CC BY 4.0."*
15. **Known Data Limitations:** Covers employers with $\ge 100$ staff only; reporting is annual retrospective; does not report real-time live open job postings.
16. **Company-Level Hiring Evidence:** **Authoritative Ground-Truth Workforce Size & Occupational Employment Structure.**

---

### Source AU-3: Australian Securities and Investments Commission (ASIC) Registers
1. **Source Name:** ASIC Company and Business Names Register
2. **Publisher or Owner:** Australian Securities and Investments Commission (ASIC)
3. **Official URL:** `https://asic.gov.au/online-services/search-asic-registers/` | `https://data.gov.au/`
4. **Geographic Coverage:** Australia.
5. **Employer Population Covered:** All incorporated companies and registered business names in Australia.
6. **Available Fields:** Company Name, ACN, Type, Class, Sub-class, Status, Date of Registration, Previous State of Registration.
7. **Update Frequency:** Monthly snapshots on `data.gov.au`.
8. **Historical Coverage:** Comprehensive corporate records from 1991 to present.
9. **Access Method:** Public CSV datasets on `data.gov.au` and ASIC Connect online portal.
10. **API or Download Availability:** Free monthly CSV datasets for basic company and business name listings. Detailed corporate extracts require paid search fees.
11. **Authentication Requirements:** None for public data.gov.au datasets.
12. **Licensing and Redistribution Terms:** Creative Commons Attribution 3.0 Australia (CC BY 3.0 AU).
13. **Commercial SaaS Reuse Restrictions:** Permitted with attribution for basic company master data.
14. **Attribution Requirements:** Citation to ASIC.
15. **Known Data Limitations:** Free datasets contain basic corporate metadata only; shareholdings, director identities, and financial accounts require paid commercial searches.
16. **Company-Level Hiring Evidence:** **Corporate Registration Verification Only.**

---

## 5. DETAILED SOURCE AUDIT: SINGAPORE (SG)

### Source SG-1: ACRA Entity Information (Accounting and Corporate Regulatory Authority)
1. **Source Name:** ACRA Directory of Registered Entities & BizFile+ Open Data
2. **Publisher or Owner:** Accounting and Corporate Regulatory Authority (ACRA), Singapore Government
3. **Official URL:** `https://www.bizfile.gov.sg/` | `https://data.gov.sg/datasets/d_012e1a37c95781a74d28f09d849a9a3d`
4. **Geographic Coverage:** Singapore.
5. **Employer Population Covered:** ~600,000+ registered business entities, companies, and LLPs.
6. **Available Fields:** Unique Entity Number (UEN), Entity Name, Entity Type Description, Entity Status (Live Company, Struck Off, Dissolved), SSIC 2020 Primary Code & Description, SSIC Secondary Code & Description, Incorporation / Registration Date, Registered Office Address (Street Name, Postal Code).
7. **Update Frequency:** Monthly dataset refresh on Data.gov.sg; real-time on BizFile+.
8. **Historical Coverage:** Inception of corporate registrations to present.
9. **Access Method:** API / CSV download on Data.gov.sg; web lookup on BizFile+.
10. **API or Download Availability:** Free CSV download and REST API on Data.gov.sg.
11. **Authentication Requirements:** None for public Data.gov.sg datasets.
12. **Licensing and Redistribution Terms:** **Singapore Open Data Licence (Version 1.0).**
13. **Commercial SaaS Reuse Restrictions:** Permitted for commercial reuse and application development under Singapore Open Data Licence terms.
14. **Attribution Requirements:** Must cite: *"Source: ACRA. Data accessed from Data.gov.sg."*
15. **Known Data Limitations:** Does not include employee counts or job vacancy counts; paid ACRA BizExtract profiles ($5.50 SGD per extract) required for full financial statements and officer listings.
16. **Company-Level Hiring Evidence:** **Authoritative Singapore Corporate Identity & SSIC Industry Classification.**

---

### Source SG-2: MOM Employment Agencies & Foreign Worker Quota Information
1. **Source Name:** MOM Employment Agency Directory & Licences Register
2. **Publisher or Owner:** Ministry of Manpower (MOM), Singapore Government
3. **Official URL:** `https://www.mom.gov.sg/employment-agencies` | `https://data.gov.sg/`
4. **Geographic Coverage:** Singapore.
5. **Employer Population Covered:** All licensed employment agencies and recruitment intermediaries operating in Singapore (~4,000+ agencies).
6. **Available Fields:** Agency Licence Number, Agency Name, Employment Agency Personnel Name, Licence Status (Valid, Suspended, Revoked), Demerit Points.
7. **Update Frequency:** Monthly.
8. **Historical Coverage:** Current active licensing register.
9. **Access Method:** Direct CSV download and MOM portal lookup.
10. **API or Download Availability:** CSV dataset on Data.gov.sg.
11. **Authentication Requirements:** None.
12. **Licensing and Redistribution Terms:** Singapore Open Data Licence.
13. **Commercial SaaS Reuse Restrictions:** Permitted with attribution.
14. **Attribution Requirements:** Citation to Ministry of Manpower.
15. **Known Data Limitations:** Identifies recruitment agencies only; critical for distinguishing direct employers from third-party staffing intermediaries.
16. **Company-Level Hiring Evidence:** **Entity Resolution Filter (Distinguishes Agencies from Direct Employers).**

---

### Source SG-3: MyCareersFuture Job Portal (Workforce Singapore)
1. **Source Name:** MyCareersFuture National Jobs Portal
2. **Publisher or Owner:** Workforce Singapore (WSG) / Government of Singapore
3. **Official URL:** `https://www.mycareersfuture.gov.sg/`
4. **Geographic Coverage:** Singapore nationwide.
5. **Employer Population Covered:** Singapore registered employers advertising vacancies under the Fair Consideration Framework (FCF).
6. **Available Fields:** Job ID, Job Title, Company Name, UEN, SSIC Industry, Job Category, Employment Type, Position Level, Salary Range (Min/Max SGD), Required Skills, Minimum Experience Years, Posting Date, Expiry Date.
7. **Update Frequency:** Real-time / Daily.
8. **Historical Coverage:** Active postings only (~30 to 60 days).
9. **Access Method:** Web portal; internal backend API (`api.mycareersfuture.gov.sg/v2/jobs`).
10. **API or Download Availability:** No public commercial API. Internal API requires session tokens.
11. **Authentication Requirements:** SingPass authentication for applicant interaction; no open public developer key.
12. **Licensing and Redistribution Terms:** **RESTRICTED.** Terms of Use explicitly prohibit automated scraping, indexing, or commercial redistribution without prior written consent of WSG.
13. **Commercial SaaS Reuse Restrictions:** **HIGH LEGAL RISK.** Automated ingestion is prohibited under platform Terms of Service.
14. **Attribution Requirements:** N/A (prohibited from unapproved redistribution).
15. **Known Data Limitations:** Government portal with mandatory 14-day advertising rule for Employment Pass eligibility; legal restrictions prevent bulk harvesting.
16. **Company-Level Hiring Evidence:** **High quality government hiring data, but BLOCKED by Terms of Use.**

---

## 6. DETAILED SOURCE AUDIT: INDIA (IN)

### Source IN-1: Ministry of Corporate Affairs (MCA / MCA21)
1. **Source Name:** MCA21 Master Data Repository
2. **Publisher or Owner:** Ministry of Corporate Affairs (MCA), Government of India
3. **Official URL:** `https://www.mca.gov.in/content/mca/global/en/home.html`
4. **Geographic Coverage:** India nationwide (all states and union territories).
5. **Employer Population Covered:** ~2.5 million registered companies and LLPs.
6. **Available Fields:** Corporate Identification Number (CIN), Company Legal Name, ROC Code, Registration Number, Company Category, Company Subcategory, Class of Company (Public/Private), Authorized Capital, Paid-up Capital, Date of Incorporation, Registered Office Address, Listing Status (Listed/Unlisted), Company Status (Active/Struck Off/Under Liquidation).
7. **Update Frequency:** Event-driven / Daily portal updates.
8. **Historical Coverage:** Inception of corporate registrations under Companies Act 1956/2013 to present.
9. **Access Method:** MCA portal "View Company/LLP Master Data" web form; commercial API vendors (Signzy, Karza, Surepass).
10. **API or Download Availability:** No free public REST API provided by MCA. Bulk master data zip files are periodically released on `data.gov.in`.
11. **Authentication Requirements:** Web portal uses CAPTCHA gates; commercial aggregators require enterprise API subscriptions.
12. **Licensing and Redistribution Terms:** National Data Sharing and Accessibility Policy (NDSAP) applies to data published on `data.gov.in`. MCA portal web data is public record, but automated harvesting is subject to Terms of Service restrictions.
13. **Commercial SaaS Reuse Restrictions:** Public master data from `data.gov.in` is open for reuse with attribution; commercial APIs require private vendor contracts.
14. **Attribution Requirements:** Citation to Ministry of Corporate Affairs / data.gov.in.
15. **Known Data Limitations:** Free bulk datasets on `data.gov.in` are refreshed infrequently (often 6-12 month lag); employee headcount is not recorded in master data.
16. **Company-Level Hiring Evidence:** **Authoritative Primary Key (CIN) & Corporate Status Verification.**

---

### Source IN-2: BSE & NSE Corporate Disclosures & BRSR (Business Responsibility and Sustainability Reporting)
1. **Source Name:** Stock Exchange Filings & Annual Reports (BRSR Submissions)
2. **Publisher or Owner:** Securities and Exchange Board of India (SEBI) / BSE Ltd / National Stock Exchange of India (NSE)
3. **Official URL:** `https://www.bseindia.com/` | `https://www.nseindia.com/`
4. **Geographic Coverage:** India.
5. **Employer Population Covered:** Top 1,000 listed entities by market capitalization (mandatory BRSR); all ~5,000+ listed companies (annual reports).
6. **Available Fields:** Company Name, Scrip Code, ISIN, Sector, Total Permanent Employees, Total Other-than-Permanent Employees, Gender Diversity Ratios, Attrition Rate, Employee Turnover, Training Hours, Employee Health & Safety, Total Employee Benefit Expenses.
7. **Update Frequency:** Annual (BRSR and Annual Accounts); Quarterly (Financial Results).
8. **Historical Coverage:** Mandatory BRSR reporting from Fiscal Year 2022-23 to present; annual reports for 20+ years.
9. **Access Method:** Corporate filings search on BSE/NSE websites, PDF/XBRL filings downloads.
10. **API or Download Availability:** Structured XBRL filings available for programmatic extraction on BSE/NSE portals.
11. **Authentication Requirements:** None for public web downloads; bulk exchange feeds require licensed financial data agreements.
12. **Licensing and Redistribution Terms:** Public regulatory filings mandated by SEBI LODR Regulations 2015. Factual financial and human capital data is freely readable.
13. **Commercial SaaS Reuse Restrictions:** Permitted for factual analysis and corporate benchmarking; raw exchange redistribution may require exchange vendor agreements.
14. **Attribution Requirements:** Must cite: *"Source: Regulatory filings with BSE/NSE under SEBI (LODR) Regulations."*
15. **Known Data Limitations:** Covers top 1,000 listed Indian corporations; private limited tech startups and foreign GCCs (Global Capability Centers) operating as private subsidiaries are not covered under listed BRSR mandates.
16. **Company-Level Hiring Evidence:** **Certified Annual Headcount, Attrition, and Gender Diversity Statistics.**

---

### Source IN-3: National Career Service (NCS)
1. **Source Name:** National Career Service Portal
2. **Publisher or Owner:** Ministry of Labour & Employment (MoLE), Government of India
3. **Official URL:** `https://www.ncs.gov.in/`
4. **Geographic Coverage:** India nationwide.
5. **Employer Population Covered:** ~3.5 million registered employers and recruitment institutions.
6. **Available Fields:** Employer Name, Industry, Job Title, Functional Area, Number of Vacancies, Qualification, Minimum Experience, State, District, Wage/Salary Offered.
7. **Update Frequency:** Daily / Weekly.
8. **Historical Coverage:** Operational since 2015.
9. **Access Method:** Web portal; select API partnerships.
10. **API or Download Availability:** No public open REST API for third-party commercial platforms without formal government Memorandum of Understanding (MoU).
11. **Authentication Requirements:** Registered employer/jobseeker logins.
12. **Licensing and Redistribution Terms:** **RESTRICTED.** NCS Terms and Conditions prohibit automated scraping or unauthorized harvesting of candidate and employer profiles.
13. **Commercial SaaS Reuse Restrictions:** High compliance hurdle without an authorized MoLE data sharing agreement.
14. **Attribution Requirements:** N/A (unauthorized scraping prohibited).
15. **Known Data Limitations:** Skewed heavily toward manufacturing, vocational, micro-enterprise, and entry-level state roles; modern Indian software engineering and digital economy roles are underrepresented compared to private tech platforms.
16. **Company-Level Hiring Evidence:** **Official Vacancy Records, but GATED by Government Partnership Requirements.**

---

## 7. COMPARATIVE SUMMARY ACROSS ALL FIVE MARKETS

| Country | Primary Corporate Registry | Statutory Corporate Key | Official Headcount Source | Real-Time Hiring Observation Source | Legal Gating / SaaS Redistribution Status |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **United States (US)** | SEC EDGAR & State SOS | **CIK / EIN** | SEC 10-K Human Capital Disclosures | Public ATS endpoints (Greenhouse, Lever, Workday) | **APPROVED (Public Domain / Permissive APIs)** |
| **United Kingdom (UK)** | Companies House | **CRN (8 digits)** | Companies House Annual Accounts | Home Office Sponsor Register / Permitted ATS | **APPROVED (Open Government Licence v3.0)** |
| **Australia (AU)** | Australian Business Register (ABR) | **ABN (11 digits)** | WGEA Employer Reports (100+ staff) | Direct Corporate Portals / ABR extracts | **APPROVED (CC BY 4.0 / Open Government)** |
| **Singapore (SG)** | ACRA / BizFile+ | **UEN (9-10 chars)** | Listed Annual Reports / MOM Aggregates | Direct Public ATS feeds (MyCareersFuture gated) | **APPROVED (Singapore Open Data Licence)** |
| **India (IN)** | Ministry of Corporate Affairs (MCA) | **CIN (21 chars)** | SEBI BRSR Filings (Top 1,000 listed) | Direct Corporate Portals / Curated Benchmarks | **CONDITIONAL (Open Master Data + Direct Feeds)** |

---

## 8. STRATEGIC RESEARCH CONCLUSION

The research proves that an authentic Global Employer Intelligence module **is legally and technically feasible across all five markets** by combining:
1. **Government Open Master Data** for corporate identity and legal entity resolution.
2. **Statutory Corporate Headcount Filings** (WGEA AU, SEC 10-K US, Companies House UK, BRSR IN) for verified workforce size.
3. **Direct Employer Career Portal / Open ATS Feeds** for observed job postings, with explicit disclaimers separating digital recruitment marketing from net headcount growth.

**Audit Status:** `PASS — FIVE-MARKET SOURCE INVENTORY COMPLETE`
