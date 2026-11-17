# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## FIVE-MARKET EMPLOYER DATA FEASIBILITY MATRIX
### Cross-National Comparative Audit across Thirteen Statistical & Operational Dimensions

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-FEASIBILITY-MATRIX`  
**Execution Phase:** Phase 0 (Cross-Market Feasibility Audit)  
**Date of Audit:** 2026-11-17  
**Rating System:** Strictly Qualitative Evaluative Standard (`VERIFIED`, `PARTIALLY_VERIFIED`, `REVIEW_REQUIRED`, `UNAVAILABLE`, `UNKNOWN`).

---

## 1. EVALUATION CRITERIA & DEFINITIONS

To prevent arbitrary scoring, every dimension is evaluated using an explicit, defensible qualitative scale:

| Rating | Definition |
| :--- | :--- |
| **`VERIFIED`** | Source is active, officially documented, legally cleared for commercial SaaS integration, and exhibits programmatic data access with high reliability. |
| **`PARTIALLY_VERIFIED`** | Source provides authentic data for a subset of the market (e.g. public companies only, $\ge 100$ employee firms), or requires semi-automated transformation. |
| **`REVIEW_REQUIRED`** | Data exists but possesses unresolved intellectual property, Terms of Service ambiguities, or third-party licensing dependencies. |
| **`UNAVAILABLE`** | Data is legally confidential under national statistical protection statutes (CIPSEA, Statistics of Trade Act) or technically uncollectable without violating anti-scraping laws. |
| **`UNKNOWN`** | Insufficient empirical evidence available to substantiate data reliability or legal terms. |

---

## 2. THE FIVE-MARKET COMPARATIVE FEASIBILITY MATRIX

| Dimension # | Evaluation Dimension | United States (US) | United Kingdom (UK) | Australia (AU) | Singapore (SG) | India (IN) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Employer Identity Coverage** | `VERIFIED` (SEC CIK / State SOS) | `VERIFIED` (Companies House CRN) | `VERIFIED` (ABR / ABN Lookup) | `VERIFIED` (ACRA BizFile+ UEN) | `VERIFIED` (MCA21 CIN) |
| **2** | **Official Company Information** | `VERIFIED` (EDGAR 10-K) | `VERIFIED` (Accounts / SIC) | `VERIFIED` (ASIC / ANZSIC) | `VERIFIED` (SSIC Open Data) | `PARTIALLY_VERIFIED` (MCA Data.gov.in) |
| **3** | **Company Career Page Availability** | `VERIFIED` (Open ATS APIs) | `VERIFIED` (Open ATS APIs) | `PARTIALLY_VERIFIED` (Top 500 ATS) | `PARTIALLY_VERIFIED` (MNC ATS feeds) | `PARTIALLY_VERIFIED` (Tech enterprise ATS) |
| **4** | **Job Advertisement Availability** | `VERIFIED` (Public Boards / ATS) | `REVIEW_REQUIRED` (Textkernel Gate) | `PARTIALLY_VERIFIED` (Direct Portals) | `REVIEW_REQUIRED` (WSG Terms Gate) | `PARTIALLY_VERIFIED` (Tech Portals) |
| **5** | **Explicit Vacancy Count Availability** | `UNAVAILABLE` (BLS CIPSEA Confidential) | `UNAVAILABLE` (ONS Statutory Bar) | `UNAVAILABLE` (ABS Statutory Bar) | `UNAVAILABLE` (MOM Confidential) | `UNAVAILABLE` (MoSPI Confidential) |
| **6** | **Historical Hiring Evidence** | `PARTIALLY_VERIFIED` (10-K Headcount) | `PARTIALLY_VERIFIED` (Annual Accounts) | `VERIFIED` (WGEA 11-Yr Data) | `PARTIALLY_VERIFIED` (Annual Reports) | `PARTIALLY_VERIFIED` (BRSR Filings) |
| **7** | **Skill Requirements** | `VERIFIED` (Job Descriptions) | `PARTIALLY_VERIFIED` (Direct ATS only) | `PARTIALLY_VERIFIED` (Direct ATS only) | `PARTIALLY_VERIFIED` (Direct ATS only) | `VERIFIED` (IT/Tech Benchmarks) |
| **8** | **Qualification Requirements** | `VERIFIED` (O\*NET / ATS Specs) | `PARTIALLY_VERIFIED` (ATS Postings) | `PARTIALLY_VERIFIED` (ATS Postings) | `PARTIALLY_VERIFIED` (ATS Postings) | `PARTIALLY_VERIFIED` (ATS Postings) |
| **9** | **Geographic Resolution** | `VERIFIED` (State & MSA level) | `VERIFIED` (Local Authority level)| `VERIFIED` (State & Postcode) | `VERIFIED` (Planning Area level)| `PARTIALLY_VERIFIED` (Tier-1 Tech Metros) |
| **10** | **Update Frequency** | `VERIFIED` (Daily / Real-time) | `VERIFIED` (Daily API) | `VERIFIED` (Weekly ABR Dumps) | `PARTIALLY_VERIFIED` (Monthly Open Data)| `PARTIALLY_VERIFIED` (Periodic Dumps) |
| **11** | **Commercial Use Permission** | `VERIFIED` (US Public Domain) | `VERIFIED` (OGL v3.0 / Crown) | `VERIFIED` (CC BY 4.0 / CC BY 3.0)| `VERIFIED` (Singapore Open Data)| `PARTIALLY_VERIFIED` (NDSAP India) |
| **12** | **API Reliability** | `VERIFIED` (SEC JSON REST API) | `VERIFIED` (Companies House REST)| `VERIFIED` (ABR Web Services) | `VERIFIED` (Data.gov.sg REST) | `PARTIALLY_VERIFIED` (Data.gov.in / Custom) |
| **13** | **Data Acquisition Cost** | `VERIFIED` (100% Free / Open) | `VERIFIED` (100% Free / Open) | `VERIFIED` (100% Free / Open) | `VERIFIED` (100% Free / Open) | `VERIFIED` (Free Bulk Masters) |

---

## 3. MARKET-BY-MARKET FEASIBILITY SYNTHESIS

### 1. Australia (AU) — Readiness Rating: `VERY HIGH` (Benchmark Market)
- **Strengths:** Outstanding regulatory alignment between ABR (ABN registration) and WGEA (mandatory workforce reports under CC BY 4.0). Full coverage of employers with 100+ staff including verified occupational breakdowns, gender diversity, and headcount series over 11 years.
- **Constraints:** Micro-employers (<100 staff) do not report to WGEA. Real-time job vacancy microdata is unavailable from ABS due to confidentiality laws.
- **MVP Feasibility:** **100% READY.** Australia represents the most defensible market for launch.

### 2. United Kingdom (UK) — Readiness Rating: `HIGH` (Identity Robust, Volume Gated)
- **Strengths:** Companies House REST API provides complete, free, real-time corporate master data under OGL v3.0. Home Office licensed sponsor register provides verified skilled worker hiring status.
- **Constraints:** Proprietary job board feeds (e.g. Textkernel) remain withheld behind the UK publication gate (`UK_DEMAND_DATA_NOT_PUBLISHED`).
- **MVP Feasibility:** **READY WITH PUBLICATION GATE.** Launch directory, verified profiles, sponsor status, and corporate accounts while withholding unapproved third-party posting indices.

### 3. United States (US) — Readiness Rating: `HIGH` (Public Issuers Robust, Private Limited)
- **Strengths:** SEC EDGAR provides completely unrestricted programmatic access to public corporate filings under US Public Domain. Greenhouse and Lever open public APIs allow clean direct collection of tech job postings.
- **Constraints:** Private non-listed enterprises (over 90% of firms) have no federal corporate filing mandate; state registries are decentralized and often fee-gated.
- **MVP Feasibility:** **READY FOR S&P 500 & TECH ENTERPRISES.** Launch with public corporations, high-growth tech firms, and federal contractors.

### 4. Singapore (SG) — Readiness Rating: `MEDIUM-HIGH` (Registry Open, National Jobs Gated)
- **Strengths:** ACRA entity directory on Data.gov.sg provides reliable UEN and SSIC industry codes under Singapore Open Data Licence. MOM agency directory cleanly segregates staffing agencies.
- **Constraints:** MyCareersFuture terms of use legally prohibit commercial scraping. Direct employer ATS endpoints must be used for job advert collection.
- **MVP Feasibility:** **READY FOR DIRECT EMPLOYERS.** Launch ACRA-verified profiles with direct corporate ATS feeds.

### 5. India (IN) — Readiness Rating: `MEDIUM` (Listed Entities Strong, Startup/SME Fragmented)
- **Strengths:** SEBI BRSR filings mandate audited headcount, diversity, and turnover for the top 1,000 listed entities. High concentration of engineering postings across major tech metros (Bengaluru, Hyderabad, Pune, NCR).
- **Constraints:** MCA21 master data has no free public REST API (relies on periodic data.gov.in extracts); private startups and Global Capability Centers (GCCs) file non-public accounts.
- **MVP Feasibility:** **READY FOR TOP LISTED & TECH ENTERPRISES.** Launch top 1,000 listed firms and major tech employers using JobIntel curated benchmarks.

---

## 4. FEASIBILITY-DRIVEN SCOPE ALLOCATION

```
+---------------------------------------------------------------------------------------+
| APPROVED FOR PHASE 1 IMPLEMENTATION (MVP SCOPE):                                     |
| [X] Employer Directory: Search verified corporate entities by market & industry.      |
| [X] Employer Profile: Headquarters, industry, size tier, canonical website, and CRN/CIK.|
| [X] Regulatory Headcount: WGEA (AU), SEC 10-K (US), Companies House (UK), BRSR (IN).   |
| [X] Direct ATS Recruitment Observations: Permissive Greenhouse/Lever job adverts.     |
| [X] Skill Requirements: Canonical skills extracted from active job descriptions.       |
| [X] Multi-Employer Side-by-Side Comparison: Headcount, locations, and required skills. |
+---------------------------------------------------------------------------------------+
| PROHIBITED / DEFERRED BEYOND PHASE 1:                                                 |
| [!] Unapproved Web Scraping of Commercial Aggregators (LinkedIn, Indeed, Naukri).    |
| [!] Single Composite "Employer Hiring Score" (Banned for methodological invalidity).  |
| [!] Speculative Vacancy Estimation from BLS/ONS/ABS (Statutory confidentiality bar).  |
| [!] Street-Level Residential Address Mapping (Strict PII violation).                  |
| [!] Automated Unreviewed Fuzzy Merging of Disputed Legal Entities.                   |
+---------------------------------------------------------------------------------------+
```

**Audit Status:** `PASS — FIVE-MARKET FEASIBILITY MATRIX AUDITED`
