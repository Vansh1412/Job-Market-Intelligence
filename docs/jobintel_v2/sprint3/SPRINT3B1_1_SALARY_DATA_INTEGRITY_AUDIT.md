# JOBINTEL 2.0 — SPRINT 3B.1.1 INDEPENDENT AUDIT REPORT
## Independent Salary Data Integrity, Source Authenticity, and Methodology Audit

**Report Reference:** `JOBINTEL-AUDIT-3B.1.1-20261116`  
**Target Sprint:** Sprint 3B.1 (Cross-Market Salary Intelligence)  
**Audit Target Branch:** `staging/sprint2c3` (Commit `0d0b2ed`)  
**Production Baseline:** `master` at `198b79d` (Verified Untouched)  
**Audit Mode:** Independent Read-Only Empirical Inspection  
**Audit Date:** November 16, 2026  
**Auditor:** Principal Data Governance, Labour Market Statistics & Systems Audit Engineer  
**Overall Audit Verdict:** **CONDITIONAL PASS — VERIFIED WITH LIMITATIONS**  

---

## 1. Executive Summary & Audit Mandate

Sprint 3B.1 established a cross-market descriptive salary intelligence layer across five target economic jurisdictions: **United States (US)**, **United Kingdom (UK)**, **Australia (AU)**, **Singapore (SG)**, and **India (IN)**.

This independent audit (Sprint 3B.1.1) was commissioned to establish whether:
1. The **28 national salary observation records** and **140 claimed percentile values** (P10, P25, P50, P75, P90) are genuinely supported by their cited statistical sources.
2. The **World Bank ICP 2024 Purchasing Power Parity (PPP)** factors and **Nominal Foreign Exchange (FX)** rates adhere to sound statistical methodology and strict operational separation.
3. The **11-dimension comparability engine** and resulting verdicts accurately reflect methodological divergence rather than confusing occupational concordance with wage parity.
4. The **UK ASHE fail-closed governance gate (HTTP 503)** is completely preserved without data leakage.
5. Legacy production models, golden predictions, and master code remain bitwise identical and uncompromised.

### Key Audit Findings Summary
- **US BLS OEWS (7 occupations / 35 percentiles):** **VERIFIED**. Direct correspondence to official BLS May 2023 release under the standard 2,080-hour full-time annualization convention.
- **UK ONS ASHE (8 occupations / 40 percentiles):** **REQUIRES LEGAL REVIEW / SUPPRESSED**. The fail-closed HTTP 503 publication gate is strictly enforced. No unpublished UK wage figures are disclosed on public endpoints.
- **Australia ABS EEH / JSA (4 occupations / 20 percentiles):** **VERIFIED WITH LIMITATIONS**. P25, P50, and P75 are officially derived from weekly ordinary-time cash earnings (Cat. 6306.0); P10 and P90 are curated from broader unit-group distributions because 6-digit detailed codes do not publish official extreme tail percentiles.
- **Singapore MOM OWS (6 occupations / 30 percentiles):** **INCORRECT (AWS MULTIPLIER) & UNVERIFIED (P10/P90)**. 
  1. *AWS Assumption:* Sprint 3B.1 applied a 13-month multiplier (13x) to monthly gross wage assuming Annual Wage Supplement (AWS) inclusion. However, by MOM statutory definition, *Monthly Gross Wage explicitly excludes bonuses and AWS*.
  2. *Extreme Tail Non-Publication:* MOM OWS officially publishes only P25, P50, and P75. Claimed P10 and P90 figures are synthetic estimates (`JOBINTEL_CURATED`).
- **India JobIntel CTC (3 occupations / 15 percentiles):** **VERIFIED WITH LIMITATIONS (MODEL PREDICTIONS)**. MOSPI PLFS does not publish granular 4-digit IT wage percentiles. The figures represent validated statistical model distributions calibrated to tech metro postings (`JOBINTEL_MODEL_ESTIMATE`), not official government surveys.
- **World Bank PPP Methodology:** **VERIFIED WITH LIMITATIONS**. Figures for 2024 are World Bank model extrapolations from the ICP 2017/2021 benchmark rounds, not an independent "2024 ICP Benchmark". Private consumption PPP (`PA.NUS.PRVT.PP`) reflects household consumption living costs, not occupational labor cost PPP.
- **Nominal FX Multipliers:** **VERIFIED**. Rates are static 2024 annual reference averages. Direction of conversion and 6-decimal precision multipliers are mathematically sound.

---

## 2. Phase 0 — Repository Baseline & Cryptographic Integrity

### 2.1 Git State Verification
```
Target Branch:       staging/sprint2c3
Head Commit:         0d0b2ed feat(salary): implement cross-market salary intelligence, 
                             dual FX/PPP metrics, and 11-dimension comparability engine (Sprint 3B.1)
Origin Alignment:    Up to date with origin/staging/sprint2c3
Working Tree:        Clean (0 uncommitted changes, 0 untracked files)
Master Baseline:     198b79dcdff08a5be5f08847c4262d31a3ce261e (Verified UNTOUCHED)
```

### 2.2 SHA-256 Dataset and Code Hashes
Every critical dataset and service module was hashed using SHA-256 across both raw bytes and normalized LF bytes:

| File Path | Raw SHA-256 Hash | LF Normalized SHA-256 Hash |
| :--- | :---: | :---: |
| `src/backend/data/salary/sources.json` | `dbc8b0b6cf85e111d206c4380834d7e33fd321383b2df91ad14626d45855aa8a` | `dbc8b0b6cf85e111d206c4380834d7e33fd321383b2df91ad14626d45855aa8a` |
| `src/backend/data/salary/ppp_fx_rates.json` | `aef330bb54cfcd4c78ac62c50de718165806dbf4d65e7cdf22c47f03b87c75a3` | `aef330bb54cfcd4c78ac62c50de718165806dbf4d65e7cdf22c47f03b87c75a3` |
| `src/backend/data/salary/observations.json` | `1b7a131fb34a7283cccc40e85d52e8157ac04f0362e6a519590275830fa1d391` | `d078348b2ebec93d6037ad34c662c0d1139ae3329d63c864989bea511753e88e` |
| `src/backend/schemas/salary.py` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` | `148b58b5afc6384fc03437023280dff685e6d51b7507b992ad3a87844df2b52f` |
| `src/backend/services/salary_service.py` | `1dd59d1af58ed3f8fc9612e7b824ec7077e9ad4cd0341352e41ce170a8cc6c4e` | `1dd59d1af58ed3f8fc9612e7b824ec7077e9ad4cd0341352e41ce170a8cc6c4e` |
| `src/backend/routers/salary.py` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` | `687533418353dc5dd570450de8130a03832e710a3e3dc6488737f00c69f00a8c` |
| `src/backend/data/occupations/national_occupations.json` | `65482c468a3199133aad065f67355488fc75f8f5cfbd091912df3589b3c7a39b` | `5fabc96a73002271a12e4443f6411d06139023f36d7f7b0c62f327cac856074d` |
| `src/backend/data/occupations/mappings.json` | `b0c48378c8a9b90ad5b3ad804d108157d6acb99947bce1ed77301a6ee05ad176` | `79a2c1cd4adc8425c189fa658267877cf76e12b6bb68d41a8aab4fc6212da607` |
| `src/backend/data/occupations/canonical_occupations.json` | `a33cb726b8395e39e72818ddbbb12366fb7abb30b3b5eada2d05671bff78e040` | `a33cb726b8395e39e72818ddbbb12366fb7abb30b3b5eada2d05671bff78e040` |

---

## 3. Phase 1 — Comprehensive Audit of All 28 Observations & 140 Percentile Values

Every observation was audited against primary source releases, statutory definitions, and published tables.

### Provenance Classification Standards:
- **`OFFICIAL_PUBLISHED`**: Figure is published verbatim in an official government statistical release.
- **`OFFICIALLY_DERIVED`**: Figure is derived from official data using a documented, standardized arithmetic transformation (e.g. standard 2,080-hour or 52-week annualization).
- **`JOBINTEL_MODEL_ESTIMATE`**: Figure is produced by an internal calibrated statistical model or job posting wage index.
- **`JOBINTEL_CURATED`**: Figure is interpolated or synthesized from broader occupational groupings or heuristic adjustments.
- **`SUPPRESSED`**: Official figure exists in raw tables but is legally or procedurally withheld from disclosure.
- **`NOT_AVAILABLE`**: Figure is claimed in the platform but does not exist in the cited official publication.

### Full Inventory Audit Table (28 Observations / 140 Claimed Percentiles)

| # | Market | Occupation ID & Title | Currency & Period | P10 | P25 | P50 (Median) | P75 | P90 | Primary Source Cited | Audit Classification |
| :-: | :---: | :--- | :---: | :-: | :-: | :-: | :-: | :-: | :--- | :--- |
| **1** | US | `US_SOC_2018:15-1252`<br>Software Developers | USD / Annual | \$77,020 | \$101,370 | \$132,270 | \$168,050 | \$208,620 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **2** | US | `US_SOC_2018:15-2051`<br>Data Scientists | USD / Annual | \$61,070 | \$81,720 | \$108,020 | \$146,800 | \$184,090 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **3** | US | `US_SOC_2018:15-1253`<br>Software QA Analysts/Testers | USD / Annual | \$55,200 | \$75,310 | \$101,800 | \$130,940 | \$161,020 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **4** | US | `US_SOC_2018:15-1212`<br>Info Security Analysts | USD / Annual | \$69,210 | \$90,870 | \$120,360 | \$153,600 | \$182,370 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **5** | US | `US_SOC_2018:15-1242`<br>Database Administrators | USD / Annual | \$54,920 | \$74,440 | \$101,510 | \$131,730 | \$161,280 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **6** | US | `US_SOC_2018:15-1244`<br>Network & Systems Admins | USD / Annual | \$55,540 | \$71,960 | \$95,360 | \$122,220 | \$147,700 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **7** | US | `US_SOC_2018:15-1211`<br>Computer Systems Analysts | USD / Annual | \$61,990 | \$80,520 | \$103,800 | \$131,840 | \$161,900 | BLS OEWS May 2023 | **OFFICIAL_PUBLISHED** |
| **8** | UK | `UK_SOC_2020:2134`<br>Programmers & Devs | GBP / Annual | £28,100 | £36,926 | £48,000 | £62,500 | £78,000 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **9** | UK | `UK_SOC_2020:2135`<br>Cyber Security Professionals | GBP / Annual | £31,500 | £39,800 | £51,000 | £64,200 | £79,500 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **10**| UK | `UK_SOC_2020:2136`<br>IT Quality & Testing | GBP / Annual | £25,200 | £32,400 | £41,500 | £53,000 | £66,200 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **11**| UK | `UK_SOC_2020:2133`<br>IT Business Analysts & Arch. | GBP / Annual | £32,000 | £41,200 | £52,600 | £67,500 | £84,000 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **12**| UK | `UK_SOC_2020:2137`<br>IT Network Professionals | GBP / Annual | £26,000 | £33,500 | £42,800 | £55,100 | £69,400 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **13**| UK | `UK_SOC_2020:2131`<br>IT Project Managers | GBP / Annual | £33,400 | £42,600 | £54,900 | £69,800 | £87,200 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **14**| UK | `UK_SOC_2020:3133`<br>Database Admins & Techs | GBP / Annual | £22,100 | £27,800 | £35,400 | £44,900 | £56,100 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **15**| UK | `UK_SOC_2020:3544`<br>Data Analysts | GBP / Annual | £24,000 | £30,500 | £38,500 | £49,200 | £62,000 | ONS ASHE 2024 Table 14 | **SUPPRESSED (HTTP 503)** |
| **16**| AU | `AU_OSCA_2024:261313`<br>Software Engineer | AUD / Annual | \$78,000 | \$96,200 | \$121,500 | \$152,000 | \$185,000 | ABS EEH 6306.0 / JSA | **VERIFIED WITH LIMITATIONS**<br>(P25-P75: Derived; P10/P90: Curated) |
| **17**| AU | `AU_OSCA_2024:224411`<br>Data Scientist | AUD / Annual | \$75,000 | \$92,000 | \$118,000 | \$148,000 | \$178,000 | ABS EEH 6306.0 / JSA | **VERIFIED WITH LIMITATIONS**<br>(P25-P75: Derived; P10/P90: Curated) |
| **18**| AU | `AU_OSCA_2024:262112`<br>ICT Security Specialist | AUD / Annual | \$80,000 | \$98,500 | \$124,000 | \$155,000 | \$188,000 | ABS EEH 6306.0 / JSA | **VERIFIED WITH LIMITATIONS**<br>(P25-P75: Derived; P10/P90: Curated) |
| **19**| AU | `AU_OSCA_2024:261314`<br>Software Tester | AUD / Annual | \$66,000 | \$80,500 | \$100,000 | \$124,500 | \$148,000 | ABS EEH 6306.0 / JSA | **VERIFIED WITH LIMITATIONS**<br>(P25-P75: Derived; P10/P90: Curated) |
| **20**| SG | `SG_SSOC_2024:25121`<br>Software Developer | SGD / Annual | \$54,600 | \$72,800 | \$97,500 | \$132,600 | \$175,500 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **21**| SG | `SG_SSOC_2024:25131`<br>AI / ML Engineer | SGD / Annual | \$62,400 | \$80,600 | \$106,600 | \$149,500 | \$195,000 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **22**| SG | `SG_SSOC_2024:25132`<br>Data Scientist | SGD / Annual | \$58,500 | \$78,000 | \$104,000 | \$143,000 | \$188,500 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **23**| SG | `SG_SSOC_2024:25124`<br>Cloud Architect | SGD / Annual | \$70,200 | \$91,000 | \$117,000 | \$162,500 | \$208,000 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **24**| SG | `SG_SSOC_2024:25125`<br>DevOps Engineer | SGD / Annual | \$58,500 | \$75,400 | \$101,400 | \$140,400 | \$182,000 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **25**| SG | `SG_SSOC_2024:25211`<br>Cybersecurity Specialist | SGD / Annual | \$59,800 | \$76,700 | \$102,700 | \$143,000 | \$184,600 | MOM OWS 2023 | **INCORRECT (AWS) / UNVERIFIED (P10/P90)** |
| **26**| IN | `IN_NCO_2015:2512.0100`<br>Software Developer | INR / Annual (CTC) | ₹4,50,000 | ₹7,50,000 | ₹12,00,000 | ₹18,00,000 | ₹26,00,000 | JobIntel ML Models 2024 | **JOBINTEL_MODEL_ESTIMATE** |
| **27**| IN | `IN_NCO_2015:2511.0100`<br>Systems Analyst | INR / Annual (CTC) | ₹4,20,000 | ₹6,80,000 | ₹10,50,000 | ₹15,50,000 | ₹22,50,000 | JobIntel ML Models 2024 | **JOBINTEL_MODEL_ESTIMATE** |
| **28**| IN | `IN_NCO_2015:2521.0100`<br>Database Administrator | INR / Annual (CTC) | ₹4,00,000 | ₹6,50,000 | ₹9,80,000 | ₹14,50,000 | ₹21,00,000 | JobIntel ML Models 2024 | **JOBINTEL_MODEL_ESTIMATE** |

### Breakdown of the 140 Claimed Percentiles:
- **`OFFICIAL_PUBLISHED`:** 35 values (US: 35).
- **`OFFICIALLY_DERIVED`:** 12 values (AU P25, P50, P75: 12).
- **`JOBINTEL_MODEL_ESTIMATE`:** 15 values (IN: 15).
- **`SUPPRESSED (Active Gate)`:** 40 values (UK: 40).
- **`JOBINTEL_CURATED (Interpolated)`:** 8 values (AU P10, P90: 8).
- **`INCORRECT_TRANSFORMATION / NOT_AVAILABLE`:** 30 values (SG: 30 — 18 values distorted by unauthorized AWS 13-month inflation + 12 synthetic P10/P90 tail values).

---

## 4. Phase 2 — Market-Specific Audit Findings

### 4.1 United States: BLS OEWS (May 2023)
- **Status:** **VERIFIED**
- **Classification System:** US SOC 2018 (6-digit detailed occupations).
- **Sample Universe:** 1.2 million business establishments over 6 semi-annual survey panels (May 2020 through May 2023). Covers non-farm wage and salary civilian employment.
- **Exclusion Audit:** Verified that self-employed individuals, unincorporated business owners, and household workers are excluded.
- **Annualization Convention:** Verified that annual wages are calculated as $\text{Hourly Rate} \times 2,080 \text{ hours}$. For tech professionals who are salaried exempt, BLS directly collects annual salaries where reported.
- **Discrepancy Noted in Metadata:** In `sources.json`, `source_url` is statically set to `https://www.bls.gov/oes/current/oes151252.htm` (Software Developers) for all 7 US occupations rather than linking to the parent index `https://www.bls.gov/oes/current/oes_nat.htm` or specific detailed codes.

### 4.2 United Kingdom: ONS ASHE (2024 Revised)
- **Status:** **REQUIRES LEGAL REVIEW / FAIL-CLOSED PRESERVED**
- **Classification System:** UK SOC 2020 (4-digit unit groups).
- **Sample Universe:** 1% random sample of employee jobs drawn from HMRC PAYE records. Full-time adult employees on adult rates whose pay was unaffected by absence.
- **Governance Gate Enforcement:** Verified that `GET /v1/salary/occupations/UK_SOC_2020:2134` and `/v1/salary/compare?occupation_id=UK_SOC_2020:2134` return **HTTP 503 Service Unavailable** (`UK_DATA_NOT_PUBLISHED`).
- **Data Leakage Check:** When non-UK occupations request cross-market comparisons, UK is reported as `is_suppressed: true` and all percentiles/medians return `null`. Zero unauthorized wage leakage was detected.
- **SOC Vintage Inconsistency:** The legacy pipeline `ashe2025.py` processes ASHE Table 15 in **SOC 2010**, whereas `national_occupations.json` and `observations.json` register UK occupations under **SOC 2020**.

### 4.3 Australia: ABS EEH / JSA (May 2023)
- **Status:** **VERIFIED WITH LIMITATIONS**
- **Classification System:** ANZSCO 2022 / OSCA 2024.
- **Measure Definition:** Gross ordinary-time cash earnings for full-time non-managerial adult employees. Excludes overtime premiums.
- **Percentile Non-Availability:** ABS EEH (Cat. 6306.0) publishes median, 25th percentile, and 75th percentile for 4-digit unit groups (e.g. 2613). 
- **Audit Finding:** The published figures in `observations.json` for 261313 (\$121,500) and 261314 (\$100,000) are annualized from weekly ordinary earnings ($\text{Weekly} \times 52$). P10 (\$78,000) and P90 (\$185,000) are not published at the 6-digit detailed occupation level by ABS and represent calibrated estimations.

### 4.4 Singapore: MOM OWS (2023)
- **Status:** **INCORRECT (AWS MULTIPLIER) & UNVERIFIED (P10/P90)**
- **Audit Finding 1: Distortion via AWS 13th Month Multiplier:**
  - MOM defines **Monthly Gross Wage** as: *"Basic wage, overtime payments, commissions, tips, other allowances and 1/12 of annual variable payment. It EXCLUDES employer CPF contributions, bonuses, and annual wage supplements (AWS)."*
  - Sprint 3B.1 derived annual figures by multiplying monthly figures by 13 (assuming an unverified 13th month AWS bonus). For 25121 Software Developers, the published MOM OWS median monthly gross wage is **\$7,500 SGD/month**. Multiplying by 13 yielded \$97,500 SGD.
  - Standard MOM annualization without speculative bonus addition is $\$7,500 \times 12 = \$90,000 \text{ SGD}$. The AWS inflation was added without an independent empirical basis.
- **Audit Finding 2: Non-Publication of P10 and P90:**
  - Official MOM OWS tables publish **only P25, Median (P50), and P75**.
  - MOM OWS *does not publish P10 and P90*.
  - The claimed values for SG P10 and P90 (e.g. \$54,600 and \$175,500) are synthetic figures generated by the authoring engineer, violating the rule: *"Never estimate unavailable percentiles."*

### 4.5 India: JobIntel CTC Benchmark Models
- **Status:** **VERIFIED WITH LIMITATIONS (MODEL PREDICTIONS)**
- **Source Nature:** The three Indian figures are **NOT** government census survey observations. The Periodic Labour Force Survey (PLFS) published by MOSPI does not collect or publish fine-grained 4-digit NCO-2015 private-sector IT wage distributions.
- **Methodology & Concept:** Figures represent calibrated distributions from JobIntel's predictive model registry and job posting wage scrapers across Bengaluru, Hyderabad, Pune, and NCR.
- **Compensation Concept Disparity:** India figures represent **Annual Cost to Company (CTC)**, which includes mandatory employer Provident Fund contributions (12%), gratuity provisions (4.81%), and employer insurance. CTC is an employer labor cost metric, structurally distinct from gross wages.
- **Tagging Compliance:** The platform correctly tags India observations as `quality_flag: MODEL_PREDICTION` and assigns `ComparabilityVerdict.COMPARABLE_WITH_MAJOR_CAVEATS`.

---

## 5. Phase 3 & 4 — PPP and Nominal Foreign Exchange Audit

### 5.1 Purchasing Power Parity (PPP) Factor Audit
- **Series Code:** World Bank World Development Indicators (WDI) series code `PA.NUS.PRVT.PP` (PPP conversion factor, private consumption, LCU per international \$).
- **ICP Benchmark Round Reality:** 
  - The International Comparison Program (ICP) conducted benchmark global price surveys in **ICP 2011**, **ICP 2017**, and **ICP 2021** (released in 2024).
  - **There is no "ICP 2024 Benchmark Round".** Figures labeled 2024 are model-based CPI extrapolations from the ICP 2021 benchmark. Describing 2024 as an "ICP revision round" is technically imprecise.
- **Application to Occupational Wages:** 
  - Private consumption PPP is designed to adjust household final consumption expenditure baskets (groceries, housing, utilities).
  - Its application to occupational gross compensation is an **illustrative price-level adjustment**, not an official labor-cost parity index.

### 5.2 Nominal Foreign Exchange Rate Audit
- **Provider & Reference Period:** Federal Reserve H.10, IMF IFS, and MAS annual averages for calendar year 2024.
- **Direction & Multiplier Accuracy:**
  - USD $\to$ INR: Base 83.5000 | Multiplier 0.011976 | Re-calculated: $1 / 83.5 = 0.011976047$. Precision error: $< 0.0004\%$.
  - USD $\to$ GBP: Base 0.7850 | Multiplier 1.273885 | Re-calculated: $1 / 0.785 = 1.27388535$. Precision error: $< 0.0003\%$.
  - USD $\to$ AUD: Base 1.5200 | Multiplier 0.657895 | Re-calculated: $1 / 1.52 = 0.65789473$. Precision error: $< 0.0004\%$.
  - USD $\to$ SGD: Base 1.3450 | Multiplier 0.743494 | Re-calculated: $1 / 1.345 = 0.74349442$. Precision error: $< 0.0004\%$.
- **Finding:** Rates are fixed 2024 annual benchmarks, not dynamic live streaming quotes. The label `fx_description` in `ppp_fx_rates.json` states "annual market spot conversion values". It must be explicitly qualified as a **static annual benchmark exchange rate**.

---

## 6. Phase 5 — Comparability Engine Audit

The comparability engine in `src/backend/services/salary_service.py` evaluates 11 explicit methodological dimensions.

### Dimensions Verified:
1. `CURRENCY_MISMATCH`: Dual FX and World Bank PPP conversions applied with explicit caveats.
2. `PAY_PERIOD_FREQUENCY`: Annualized ordinary time vs. monthly/weekly.
3. `PAY_CONCEPT_DEFINITION`: CTC (with statutory employer benefits) vs. gross cash vs. straight-time wages.
4. `SURVEY_POPULATION`: Full-time non-managerial adults vs. enterprise establishments $\ge 10$.
5. `OVERTIME_AND_BONUS_TREATMENT`: Overtime excluded vs. AWS bonuses included.
6. `GEOGRAPHIC_COVERAGE`: Nationwide multi-metro vs. city-state vs. regional hubs.
7. `REFERENCE_YEAR_ALIGNMENT`: 2023 survey releases vs. 2024 model benchmarks.
8. `CLASSIFICATION_GRANULARITY`: 4-digit SOC unit groups vs. 6-digit detailed occupations.
9. `PERCENTILE_AVAILABILITY`: Complete spectrum vs. partial percentiles.
10. `SOURCE_METHODOLOGY_TYPE`: Government statistical census vs. ML model predictions.
11. `STATISTICAL_SUPPRESSION_AND_RSE`: Governance withholding and relative standard error checks.

### Logic & Rule Gap Discovered:
- In `evaluate_comparability()`:
  - If target or source is suppressed or missing median: assigns `INSUFFICIENT_DATA` (**Verified**).
  - If either is `MODEL_PREDICTION`, or relationship is `BROADER_THAN`/`NARROWER_THAN`, or confidence $< 0.88$: assigns `COMPARABLE_WITH_MAJOR_CAVEATS` (**Verified**).
  - If currency differs or AWS bonus included: assigns `COMPARABLE_WITH_ADJUSTMENTS` (**Verified**).
  - If identical: assigns `DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS` (**Verified**).
- **Audit Defect:** The enum defines `NOT_COMPARABLE`, but the rule branch assigning `NOT_COMPARABLE` (for confidence $< 0.50$ or `NO_SUPPORTED_MAPPING`) is eclipsed by line 339, which assigns `COMPARABLE_WITH_MAJOR_CAVEATS`. Low-confidence or unmapped roles should return `NOT_COMPARABLE`.

---

## 7. Phase 6 — API and Frontend Verification

### 7.1 API Contracts Verification
All 7 endpoints were probed using FastAPI TestClient:
- `GET /v1/salary/sources`: HTTP 200 (5 sources returned).
- `GET /v1/salary/sources/US_BLS_OEWS_2023`: HTTP 200. Unknown ID returns HTTP 404.
- `GET /v1/salary/rates`: HTTP 200 (contains strict separation warning).
- `GET /v1/salary/observations`: HTTP 200 (28 observations; market filter works).
- `GET /v1/salary/occupations/{id}`: HTTP 200 for US, AU, SG, IN. **HTTP 503 for UK**.
- `GET /v1/salary/compare?occupation_id=...`: HTTP 200 for US, AU, SG, IN. **HTTP 503 for UK**.
- `GET /v1/salary/convert`: HTTP 200 (dual nominal USD and PPP USD calculated).

### 7.2 Frontend Implementation Verification
- Tab 4 in `OccupationsPage.tsx` successfully renders:
  1. Source occupation hero card with flag, code, and authority metadata.
  2. Side-by-side Dual Metric callouts (Nominal USD vs. PPP USD).
  3. Wage percentile distribution strip (P10 to P90).
  4. Methodological separation alert callout highlighting the difference between nominal exchange value and domestic purchasing power.
  5. Cross-market comparative cards with color-coded comparability verdicts and structured caveats.
  6. UK fail-closed governance banner when UK is queried or listed as a comparator.
  7. Interactive live currency and PPP multiplier calculator.

---

## 8. Phase 7 — Regression Verification & Golden Parity Evidence

### 8.1 Backend Test Results
```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 330 items

tests\test_archetype_parity.py ...............                           [  4%]
tests\test_ashe_ingestion.py ...........................                 [ 12%]
tests\test_chart_contracts.py ........                                   [ 15%]
tests\test_cloud_contracts.py ......                                     [ 16%]
tests\test_end_to_end_integration.py ................                    [ 21%]
tests\test_global_foundation.py ..........................               [ 29%]
tests\test_golden_predictions.py ..                                      [ 30%]
tests\test_governance_engine.py ......................................   [ 41%]
tests\test_input_validation.py ........................                  [ 49%]
tests\test_market_analytics.py .....                                     [ 50%]
tests\test_occupation_intelligence.py ...................                [ 56%]
tests\test_prediction_parity.py .............                            [ 60%]
tests\test_routing_contracts.py ....                                     [ 61%]
tests\test_salary_intelligence.py ..............                         [ 65%]
tests\test_schema_contracts.py .......                                   [ 67%]
tests\test_skill_integrity.py ............                               [ 71%]
tests\test_uk_salary_api.py ...................................          [ 82%]
tests\test_uk_salary_service.py ........................................ [ 94%]
tests\test_zero_storage_deployment.py ..........                         [100%]

============================ 330 passed in 28.97s =============================
```

### 8.2 Frontend Tests & Production Build
- **Vitest Suite:** `vitest run --run` passed (**3 test files, 9 tests passed in 1.18s**).
- **Vite Production Build:** `tsc -b && vite build` passed cleanly (**2,892 modules transformed in 405ms**).
- **Golden Prediction Parity:** Verified bitwise identical for India and USA models.

---

## 9. Corrective Action Register

Before promoting to production or executing subsequent sprints, the following remediation tasks must be tracked:

| ID | Severity | Component | Finding | Required Remediation |
| :---: | :---: | :--- | :--- | :--- |
| **C-01** | **HIGH** | `observations.json` | Singapore MOM OWS Monthly Gross Wage multiplied by 13 (AWS assumption). | Revert SG annualized wage to 12x monthly gross wage (\$90,000 for Software Dev), or establish a distinct "Total Cash with AWS" metric with separate citations. |
| **C-02** | **HIGH** | `observations.json` | Singapore MOM OWS P10 and P90 claimed values are synthetic. | Set SG P10 and P90 to `null` in `observations.json` to reflect official MOM non-publication. |
| **C-03** | **MEDIUM** | `observations.json` | Australia ABS EEH P10 and P90 are unit-group interpolations. | Tag AU P10 and P90 as `JOBINTEL_CURATED` or set to `null` if strict 6-digit official publication is required. |
| **C-04** | **MEDIUM** | `sources.json` | US BLS OEWS URL points to single occupation (`oes151252.htm`) for all 7 records. | Update `sources.json` or add per-observation `source_url` pointing to specific BLS code pages. |
| **C-05** | **MEDIUM** | `salary_service.py` | Comparability engine never assigns `NOT_COMPARABLE` for low confidence. | Add explicit condition in `evaluate_comparability()` returning `NOT_COMPARABLE` when confidence $< 0.50$ or unmapped. |
| **C-06** | **LOW** | `ppp_fx_rates.json` | Reference to "ICP 2024 Revision" implies 2024 was an ICP benchmark survey. | Clarify metadata to state "World Bank 2024 extrapolation from ICP 2017/2021 benchmark rounds". |
| **C-07** | **LOW** | `ppp_fx_rates.json` | Nominal FX described as "spot conversion values". | Update metadata description to "2024 Reference Annual Average Exchange Rates". |
| **C-08** | **MEDIUM** | `ingestion/ashe2025.py` | UK ASHE ingestion script uses SOC 2010; salary registry uses SOC 2020. | Reconcile UK SOC editions before lifting UK ASHE publication gate. |

---

## 10. Final Readiness Decision & Verifiable Audit Verdicts

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FINAL AUDIT VERDICT MATRIX (SPRINT 3B.1.1)                            │
├──────────────────────────────────┬─────────────────────────────┬──────────────────────────────────────┤
│ Audit Domain                     │ Verdict                     │ Primary Rationale                    │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 1. Git & Cryptographic Baseline  │ VERIFIED                    │ Master untouched; HEAD 0d0b2ed clean.│
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 2. United States BLS OEWS        │ VERIFIED                    │ Verbatim correspondence to May 2023. │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 3. United Kingdom ONS ASHE       │ REQUIRES LEGAL REVIEW       │ HTTP 503 fail-closed gate enforced.  │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 4. Australia ABS EEH / JSA       │ VERIFIED WITH LIMITATIONS   │ P25-P75 derived; P10/P90 curated.    │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 5. Singapore MOM OWS             │ INCORRECT (AWS) /           │ 13x AWS multiplier unjustified;      │
│                                  │ UNVERIFIED (P10/P90)        │ P10 and P90 not published by MOM.    │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 6. India JobIntel CTC Models     │ VERIFIED WITH LIMITATIONS   │ Statistical model, not census survey.│
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 7. PPP & Nominal FX Engine       │ VERIFIED WITH LIMITATIONS   │ Decoupling verified; 2024 is extrap. │
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 8. Comparability Engine          │ VERIFIED WITH LIMITATIONS   │ 11 dimensions active; C-05 gap noted.│
├──────────────────────────────────┼─────────────────────────────┼──────────────────────────────────────┤
│ 9. Full Regression & Build       │ VERIFIED                    │ 330/330 pytest, 9/9 vitest, build ok.│
└──────────────────────────────────┴─────────────────────────────┴──────────────────────────────────────┘
```

**OVERALL AUDIT DETERMINATION:** **CONDITIONAL PASS — VERIFIED WITH LIMITATIONS**

The Sprint 3B.1 salary intelligence implementation is mathematically sound, cleanly separated from frozen ML models, completely protected by UK fail-closed governance, and passes all 330 automated tests. Staging deployment is approved subject to registering the Corrective Action Register items (C-01 through C-08) prior to production release.
