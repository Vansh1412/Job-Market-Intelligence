# JOBINTEL 2.0 — SALARY METHODOLOGY NOTES
## Methodological Framework, Economic Concepts & Statistical Governance

**Document Reference:** `JOBINTEL-METHODOLOGY-NOTES-3B.1.2-20261116`  
**Sprint:** 3B.1.2 (Salary Data Remediation and Evidence Closure)  
**Date:** November 16, 2026  
**Target Branch:** `staging/sprint2c3`  
**Mandate:** Economically rigorous documentation of cross-market salary benchmarking, compensation definitions, currency conversions, and governance protections.

---

## 1. The Strict Separation Invariant: Nominal FX vs. Purchasing Power Parity (PPP)

A fundamental principle of the JOBINTEL 2.0 salary intelligence architecture is the **strict conceptual and mathematical decoupling of Nominal Foreign Exchange (FX) and Purchasing Power Parity (PPP)**.

### 1.1 Conceptual Foundations
- **Nominal Foreign Exchange (FX):**
  - Measures the relative price of two national fiat currencies in global financial markets.
  - Dictated by international capital flows, interest rate differentials, trade balances, and central bank foreign reserve interventions.
  - **Analytical Purpose:** Evaluates international financial transfer value, cross-border corporate labor budgeting, and international hiring cost parity.
  - **Data Source in Platform:** Static 2024 Reference Annual Average Exchange Rates compiled from central bank benchmark fixings (Federal Reserve H.10, Bank of England, Reserve Bank of Australia, Monetary Authority of Singapore, Reserve Bank of India) and IMF International Financial Statistics (IFS).
- **Purchasing Power Parity (PPP):**
  - Measures the rate of currency conversion that equalizes the purchasing power of different currencies by eliminating the differences in price levels between countries.
  - **Analytical Purpose:** Evaluates relative domestic living standards and consumer purchasing power within the local economy.
  - **Data Source in Platform:** World Bank World Development Indicators (WDI) series `PA.NUS.PRVT.PP` (PPP conversion factor, private consumption, LCU per international $).

### 1.2 Critical Methodological Invariant & Prohibition
```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CRITICAL METHODOLOGICAL INVARIANT                                  │
│                                                                                                        │
│ Nominal Foreign Exchange rates and Purchasing Power Parity conversion factors serve fundamentally      │
│ distinct economic functions.                                                                           │
│                                                                                                        │
│ 1. Under NO circumstances shall Nominal FX and PPP be averaged, blended, or linearly combined into     │
│    a single "composite" salary figure.                                                                 │
│ 2. The platform MUST always report both figures side-by-side with clear methodological labels:         │
│    - "Nominal USD Median (Market FX)"                                                                  │
│    - "PPP Int$ Median (World Bank WDI PPP)"                                                            │
│ 3. Users MUST be warned that a high PPP wage does not imply international cash transferability.        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Technical Clarification on World Bank 2024 PPP Extrapolations
- The International Comparison Program (ICP), coordinated by the World Bank, conducts global benchmark price collection surveys at multi-year intervals (recent benchmark rounds: **ICP 2011**, **ICP 2017**, and **ICP 2021**).
- **There is no primary "ICP 2024 Benchmark Survey".** Figures published for calendar year 2024 represent **World Bank model-based extrapolations** that adjust the ICP 2021 benchmark price levels using national Consumer Price Index (CPI) movements relative to the United States.
- Furthermore, private consumption PPP (`PA.NUS.PRVT.PP`) reflects a representative household basket of final consumption goods and services (food, shelter, utilities, transport). It is an **illustrative price-level adjustment for living standards**, not an occupational employer labor-cost parity index.

---

## 2. Compensation Concept Divergence Across Jurisdictions

Cross-market occupational salary comparisons frequently collapse because practitioners compare incompatible compensation concepts without standardization. JOBINTEL 2.0 explicitly accounts for these structural differences.

### 2.1 Gross Cash Earnings vs. Cost to Company (CTC)
The five jurisdictions in JOBINTEL 2.0 measure three distinct economic concepts of compensation:

| Market | Authority & Survey | Pay Concept Measured | Major Inclusions | Major Exclusions |
| :--- | :--- | :--- | :--- | :--- |
| **United States** | BLS OEWS | **Straight-Time Gross Wages** | Base hourly wages, guaranteed cost-of-living allowances. | Overtime pay, shift differentials, non-production bonuses, employer health/pension contributions. |
| **United Kingdom** | ONS ASHE | **Gross Annual Pay** | Base pay, incentive pay, shift premium pay, paid absence. | Employer National Insurance (NIC), employer pension contributions, non-taxable perks. |
| **Australia** | ABS EEH | **Ordinary-Time Cash Earnings** | Base ordinary time wages, regular cash allowances. | Overtime pay, irregular annual bonuses, employer Superannuation Guarantee (11.5%). |
| **Singapore** | MOM OWS | **Gross Monthly Wage (x12)** | Basic wage, overtime pay, commissions, allowances, 1/12 variable pay. | Employer Central Provident Fund (CPF, 17%), discretionary bonuses, Annual Wage Supplement (AWS). |
| **India** | JobIntel Benchmark | **Annual Cost to Company (CTC)** | Basic pay, HRA, special allowances, employer PF (12%), gratuity (4.81%), performative bonus. | Income tax withheld, personal employee deductions. |

### 2.2 Deep Dive: India's Cost to Company (CTC) Metric
In the Indian formal technology sector, salaries are uniformly contracted as **Cost to Company (CTC)** rather than gross take-home pay. CTC represents the total financial outflow incurred by the employer:
$$\text{CTC} = \text{Gross Salary} + \text{Statutory Employer Contributions} + \text{Perquisites/Benefits}$$

Key components included in Indian CTC estimates:
1. **Basic Salary:** Typically 40%–50% of gross pay.
2. **House Rent Allowance (HRA):** Tax-advantaged living allowance (40%–50% of basic).
3. **Employer Provident Fund (PF):** Statutory 12% contribution matching under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952.
4. **Gratuity Provision:** Statutory provision of 4.81% of basic pay under the Payment of Gratuity Act, 1972 ($15 \text{ days' basic wage} / 26 \text{ working days per year} \approx 4.81\%$).
5. **Medical Insurance & Group Cover:** Employer-funded health premiums.

**Comparability Impact:** Indian CTC figures appear larger than gross cash wages because they include mandatory employer overhead. Comparing ₹12.00 LPA CTC ($14,371 USD nominal / $50,420 Int$ PPP) to US $132,270 USD straight-time wages compares an employer labor-cost metric against an employee gross cash metric. The comparability engine explicitly flags this under `PAY_CONCEPT_DEFINITION`.

---

## 3. Jurisdiction-Specific Remediation Notes (Sprint 3B.1.2)

### 3.1 Singapore MOM OWS Remediation (`C-01` & `C-02`)
- **Annualization Multiplier:**
  - In Sprint 3B.1, Singapore monthly gross wages were annualized as $\text{Monthly Gross} \times 13$, assuming the inclusion of a 13th-month Annual Wage Supplement (AWS).
  - MOM statutory guidance explicitly states that Monthly Gross Wage *excludes bonuses and AWS*.
  - Under Sprint 3B.1.2, all 6 Singapore occupations were remediated to the official statutory annualization convention:
    $$\text{Annualized Gross Wage} = \text{Monthly Gross Wage} \times 12$$
- **Percentile Truncation:**
  - MOM OWS Table T1 compiles and publishes **only P25, Median (P50), and P75**.
  - MOM OWS does not compile or publish P10 and P90 tail values.
  - Synthetic P10 and P90 figures were completely purged and replaced with `null` across all 6 observations.

### 3.2 Australia ABS EEH Remediation (`C-03`)
- **Survey Methodology:**
  - ABS Cat. 6306.0 collects employee earnings for a May reference period.
  - Wages are published as **Weekly Ordinary-Time Cash Earnings** for full-time adult non-managerial employees.
  - Annualization formula: $\text{Weekly Earnings} \times 52$.
- **Percentile Provenance:**
  - ABS Cat. 6306.0 publishes P25, P50, and P75 for 4-digit ANZSCO unit groups (e.g. 2613 Software and Applications Programmers).
  - Extreme tail percentiles (P10 and P90) are not officially published at the 6-digit detailed OSCA level.
  - Under Sprint 3B.1.2, P10 and P90 were nullified (`p10: null`, `p90: null`) to prevent false precision.

### 3.3 United States BLS OEWS Convention (`C-04`)
- **Full-Time Annualization Convention:**
  - BLS collects straight-time hourly and annual wages from 1.2 million non-farm establishments.
  - Published annual wages reflect a standard **2,080 annual work hours convention** ($40 \text{ hours/week} \times 52 \text{ weeks/year}$).
  - All 5 percentiles (P10, P25, P50, P75, P90) are officially compiled and published verbatim by BLS.
- **Citation Stability:**
  - Base source URL in `sources.json` points to the national parent index (`https://www.bls.gov/oes/current/oes_nat.htm`), while individual code pages (`oes151252.htm`, etc.) are documented in the Evidence Matrix.

### 3.4 United Kingdom ASHE Fail-Closed Architecture & SOC Reconciliation (`C-08`)
- **Governance Gate Enforcement:**
  - UK salary data is governed by the automated fail-closed gate in `src/backend/routers/uk_salary.py`.
  - When `require_uk_publication()` evaluates to false, all endpoints accessing UK salary profiles or UK comparisons return **HTTP 503 Service Unavailable** (`UK_DATA_NOT_PUBLISHED`).
  - When non-UK roles query cross-market benchmarks, UK comparator records return `is_suppressed: true` with all wage figures set to `null`.
- **Classification Concordance Requirement for Future Unblocking:**
  - The legacy data ingestion pipeline `ingestion/ashe2025.py` processes ASHE Table 15 based on **UK SOC 2010** classification codes.
  - The platform's occupation taxonomy and salary observation registry are standardized on **UK SOC 2020** (e.g. `2134` Programmers and software development professionals).
  - Before the UK fail-closed governance gate can be legally and technically lifted, a verified bidirectional crosswalk between UK SOC 2010 and UK SOC 2020 must be integrated to prevent classification drift between historical time-series and current registers.
