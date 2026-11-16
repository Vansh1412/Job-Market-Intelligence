# JOBINTEL 2.0 — SPRINT 3B.2.1
# AUDIT E: MARKET-BY-MARKET STATISTICAL VALIDATION AUDIT

**Audit Date:** 2026-11-16  
**Auditor:** Principal Data Governance Auditor & Statistical Methodology Reviewer  
**Execution Mode:** STRICT READ-ONLY INDEPENDENT AUDIT  
**Baseline Git Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Repository Branch:** `staging/sprint2c3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`

---

## 1. Overview and Assessment Standards

This audit evaluates each of the five target labour markets (United States, Australia, United Kingdom, Singapore, and India) against international statistical norms, occupational taxonomy accuracy, source data rights, and metric validity.

Every market is evaluated to ensure:
1. No non-comparable concepts are conflated (e.g. projecting decennial openings vs. measuring spot online advertisements).
2. Proper taxonomy versions are cited (US SOC 2018, AU OSCA 2024 / ANZSCO 2022, UK SOC 2020, SG SSOC 2024, IN NCO-2015).
3. Data boundaries, suppression rules, and legal licences are respected.

---

## 2. United States Market Audit

### 2.1 Statistical Framework & Methodology
- **Source Agencies:** U.S. Bureau of Labor Statistics (Employment Projections Program, EP) and National Center for O*NET Development.
- **Underlying Construct:** Projected **Annual Job Openings** over the 2023–2033 projection decade, calculated as the sum of net employment growth plus occupational separations (retirements, career changes).
- **Distinction Between Openings and Growth:** The BLS methodology separates net job growth (e.g., +17% for Software Developers) from total openings (140,100 per year), of which over 70% represent replacement needs.
- **Skills Grounding:** Skills are aligned to O*NET 28.0 Content Model knowledge/skills/abilities domains, which represent occupational worker requirements rather than transient keyword spikes from job boards.

### 2.2 U.S. Validation Table

| Metric | Actual Source | Data Type | Classification System | Provenance | Verdict |
|---|---|---|---|---|---|
| Projected Annual Openings | U.S. BLS EP Table 1.7 | Annualized Projection | US SOC 2018 (6-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| 10-Yr Growth Rate (+17%) | U.S. BLS EP Table 1.7 | Structural Projection | US SOC 2018 (6-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| State Geographic Shares | U.S. BLS OEWS May 2023 | Proxy Distribution | US States (FIPS) | `OFFICIALLY_DERIVED` | **VALIDATED PROXY** |
| Skill Importance Weights | O*NET 28.0 Database | Taxonomy Scoring | O*NET-SOC 2018 | `OFFICIALLY_DERIVED` | **VALIDATED** |

---

## 3. Australia Market Audit

### 3.1 Statistical Framework & Methodology
- **Source Agency:** Jobs and Skills Australia (JSA), an Australian Government statutory agency.
- **Primary Survey / Series:** Internet Vacancy Index (IVI), measuring newly advertised job postings on major Australian job boards (SEEK, CareerOne, Workforce Australia), de-duplicated and seasonally adjusted.
- **Shortage Assessment:** JSA Skills Priority List (SPL 2024), providing official government shortage ratings (`S` = National Shortage, `NS` = No Shortage) based on employer surveys, vacancy fill rates, and stakeholder consultations.
- **Taxonomy Concordance:** JSA reports at ANZSCO 4-digit unit group level; JobIntel scales to 6-digit Australian Occupation Standard Classification (OSCA 2024) using empirical Australian labour force shares.

### 3.2 Australia Validation Table

| Metric | Actual Source | Data Type | Classification System | Provenance | Verdict |
|---|---|---|---|---|---|
| Monthly Online Adverts | JSA Internet Vacancy Index | Online Advert Count | AU OSCA 2024 / ANZSCO | `OFFICIALLY_DERIVED` | **VALIDATED** |
| National Shortage Status | JSA Skills Priority List (SPL 2024) | Statutory Classification | ANZSCO 2022 v1 | `OFFICIALLY_DERIVED` | **VALIDATED** |
| State Distribution (NSW, VIC) | JSA IVI Regional Series | Survey-Weighted Shares | Australian States/Territories | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Future Demand Rating | JSA SPL 5-Year Outlook | Categorical Assessment | ANZSCO 2022 v1 | `OFFICIALLY_DERIVED` | **VALIDATED** |

---

## 4. United Kingdom Market Audit

### 4.1 Statistical Framework & Methodology
- **Source Agency:** Office for National Statistics (ONS) in collaboration with Textkernel BV.
- **Primary Series:** Experimental Online Job Advert Volumes Index (Base 2019 = 100), tracking newly posted digital vacancies across the UK.
- **Statutory Shortage Reference:** Home Office Immigration Salary List (ISL 2024), advised by the independent Migration Advisory Committee (MAC).
- **Critical Distinction:** The ONS experimental series is an **index**, not an absolute count of vacancies. JobIntel correctly preserves the unit `Online Job Advert Index (Base=100)` rather than converting to fake raw job counts.
- **Fail-Closed Isolation:** The descriptive salary routes for the UK remain strictly disabled under HTTP 503 (`UK_DATA_NOT_PUBLISHED`). UK demand data is entirely segregated from salary data.

### 4.2 United Kingdom Validation Table

| Metric | Actual Source | Data Type | Classification System | Provenance | Verdict |
|---|---|---|---|---|---|
| Online Job Advert Index | ONS / Textkernel Labour Demand | Experimental Index | UK SOC 2020 (4-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Shortage Occupation Listing | MAC Immigration Salary List (2024) | Statutory List | UK SOC 2020 (4-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Historical Index Trend | ONS Experimental Series (2022–2024) | Quarterly Index Series | UK SOC 2020 (4-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Salary API Integrity Check | ASHE Ingestion Protection | Fail-Closed Check | UK SOC 2020 | `OFFICIAL_GOVERNANCE` | **PROTECTED (503)** |

---

## 5. Singapore Market Audit

### 5.1 Statistical Framework & Methodology
- **Source Agency:** Ministry of Manpower (MOM), Manpower Research and Statistics Department (MRSD).
- **Primary Survey:** MOM Job Vacancies Survey (Annual 2023/2024), covering private enterprises with at least 25 employees and the public sector.
- **Key Indicators:** Total job vacancies by occupation (Table 3: Commonly Sought After PMETs) and recruitment difficulty indicator (`percent_unfilled_over_6_months`).
- **Taxonomy Concordance:** Singapore Standard Occupational Classification (SSOC 2024/2020).
- **Data Completeness:** Singapore is the only market with official empirical survey measurements for long-term unfilled vacancy rates (e.g., 32.4% for Software Developers).

### 5.2 Singapore Validation Table

| Metric | Actual Source | Data Type | Classification System | Provenance | Verdict |
|---|---|---|---|---|---|
| Enterprise Job Vacancies | MOM Job Vacancies 2023/2024 Tab 3 | Official Enterprise Survey | SG SSOC 2024 (5-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| % Unfilled > 6 Months | MOM Job Vacancies 2023/2024 Tab 3 | Survey Hard-to-Fill % | SG SSOC 2024 (5-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Strategic Shortage Status | MOM / SSG Strategic Skills List | National Policy List | SG SSOC 2024 (5-digit) | `OFFICIALLY_DERIVED` | **VALIDATED** |
| Sub-National Breakdown | URA Planning Region Proxy | Geographic Proxy | Singapore Planning Regions | `OFFICIALLY_DERIVED` | **VALIDATED PROXY** |

---

## 6. India Market Audit

### 6.1 Statistical Framework & Methodology
- **Institutional Context:** The Ministry of Statistics and Programme Implementation (MoSPI) conducts the Periodic Labour Force Survey (PLFS), which measures employment stocks, activity status, and unemployment rates. India does **not** maintain a centralized official national enterprise job vacancy register equivalent to US JOLTS or Australian JSA IVI.
- **JobIntel Benchmark Ingestion:** To provide actionable demand signals for tech hub engineering roles, JobIntel ingests an empirical sample of 2023–2024 tech job postings across Tier-1 tech hubs (Bangalore, Hyderabad, NCR, Pune).
- **Classification & Integrity Standards:**
  - Standardized under National Classification of Occupations (NCO-2015).
  - Explicitly classified as `CALIBRATED_BENCHMARK` and `JOBINTEL_CURATED`.
  - Must never be represented as official MoSPI NSSO survey statistics.

### 6.2 India Validation Table

| Metric | Actual Source | Data Type | Classification System | Provenance | Verdict |
|---|---|---|---|---|---|
| Tech Job Postings Sample | JobIntel Empirical Tech Dataset | Empirical Sample Count | NCO-2015 (8-digit) | `JOBINTEL_CURATED` | **VALIDATED BENCHMARK** |
| Tech Hub Regional Shares | JobIntel Bangalore/Hyderabad Sample | Geographic Sample Share | Urban IT Hubs | `JOBINTEL_CURATED` | **VALIDATED BENCHMARK** |
| Labour Force Baseline Context | MoSPI PLFS Annual Report 2023-24 | Workforce Survey | NCO-2015 (1-digit/2-digit) | `OFFICIAL_STATISTICS` | **CONTEXTUAL ONLY** |
| Shortage Indicator | Tech Industry Demand Assessment | Empirical Tightness Rating | NCO-2015 (8-digit) | `JOBINTEL_CURATED` | **VALIDATED BENCHMARK** |

---

## 7. Comparative Market Validation Summary

```
   ┌─────────┬──────────────────────────┬─────────────────────────────┬──────────────────────────┐
   │ Market  │ Primary Demand Metric    │ Official Source Publisher   │ Data Release Readiness   │
   ├─────────┼──────────────────────────┼─────────────────────────────┼──────────────────────────┤
   │ USA     │ Projected Annual Openings│ U.S. BLS EP (Table 1.7)     │ Ready with Caveats (1)   │
   │ AU      │ Monthly Job Adverts (Raw)│ Jobs & Skills Australia IVI │ Ready with Caveats (2)   │
   │ UK      │ Job Advert Index (B=100) │ Office for National Stats   │ Ready with Caveats (3)   │
   │ SG      │ Enterprise Vacancy Count │ Ministry of Manpower (MRSD) │ Ready with Caveats (4)   │
   │ IN      │ Tech Postings Benchmark  │ JobIntel Research Labs      │ Calibrated Benchmark (5) │
   └─────────┴──────────────────────────┴─────────────────────────────┴──────────────────────────┘
```

**Caveats Required in Release Disclosures:**
1. **USA:** Values represent 10-year projected annual openings (including replacement needs), not current spot vacancies.
2. **AU:** Values represent monthly de-duplicated online job advertisements; 6-digit units are scaled from 4-digit ANZSCO.
3. **UK:** Values represent an index of online job adverts (Base 2019=100), not absolute vacancy headcounts.
4. **SG:** Enterprise vacancy figures reflect private firms with $\ge 25$ employees and public sector establishments.
5. **IN:** Values represent an empirical benchmark of tech job postings across Tier-1 tech clusters, not official government statistics.
