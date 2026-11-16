# JOBINTEL 2.0 — SPRINT 3B.1 IMPLEMENTATION REPORT
## Cross-Market Salary Intelligence: Source Provenance, Dual Metric Conversions, and Methodological Comparability

**Project:** JOBINTEL 2.0 — Global Career and Employer Intelligence Platform  
**Sprint:** 3B.1  
**Workstream:** Global Salary Intelligence Layer  
**Target Branch:** `staging/sprint2c3`  
**Production Baseline:** `master` at `198b79d` (completely untouched)  
**Execution Date:** November 16, 2026  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary & Objectives

Sprint 3B.1 establishes the descriptive, source-backed cross-market salary intelligence layer for JOBINTEL 2.0 across five major economic jurisdictions: **United States (US)**, **United Kingdom (UK)**, **Australia (AU)**, **Singapore (SG)**, and **India (IN)**.

Prior sprints established national taxonomy mappings and concordance crosswalks (Sprint 3A & 3B.0). Sprint 3B.1 implements the analytical and computational capabilities to benchmark occupational compensation across international borders while strictly adhering to data provenance, transparency of limitations, statistical comparability, and regulatory governance.

### Core Architectural Invariants Enforced
1. **Concordance Coverage vs. Salary Comparability Distinction:** Occupation concordance mapping coverage is never interpreted as proof of salary comparability. Occupational interchangeability and wage comparability are evaluated as distinct dimensions.
2. **Strict Separation of Nominal FX and Purchasing Power Parity (PPP):** Nominal currency conversion (market foreign exchange spot rate) and Purchasing Power Parity (World Bank ICP 2024 consumption price level factor) represent fundamentally different economic constructs. They are computed independently and presented side-by-side; they are never blended, averaged, or used interchangeably.
3. **No Synthetic Percentile Estimation:** No missing percentiles are fabricated or interpolated. Where an official survey publishes only medians or specific quartiles, only verified figures are returned.
4. **Preservation of UK ASHE Fail-Closed Governance:** UK ASHE salary endpoints strictly enforce the fail-closed HTTP 503 behavior governed by the JobIntel Revocation Registry and data catalog compliance rules until affirmative publication authorization is granted.
5. **Zero Model Retraining:** Frozen ML prediction models for India and the United States remain completely untouched with bitwise artifact integrity verified.

---

## 2. Baseline Reconciliation: Corrected Coverage Denominator

Sprint 3B.0 established 30 catalog occupation records. Sprint 3B.1 reconciles the reporting denominator to avoid conflating national jurisdictions with international reference frameworks:

| Metric | Prior Reporting | Reconciled Sprint 3B.1 Count | Rationale |
| :--- | :---: | :---: | :--- |
| **National Occupation Records** | 30 | **28** | Reconciled across 5 sovereign jurisdictions (`UK: 8`, `US: 7`, `AU: 4`, `SG: 6`, `IN: 3`). |
| **International Reference Records** | 0 | **2** | `INT_ISCO_08:2512` and `INT_ISCO_08:2511` serve as international taxonomy anchors, not sovereign labor markets. |
| **Total Catalog Occupations** | 30 | **30** | Sum of national jurisdictions and international reference standards. |
| **Mapped National Occupations** | 30 | **28** | 100% active concordance coverage across national occupations. |
| **Mapped International References**| 0 | **2** | 100% bidirectional crosswalk coverage to national codes. |
| **Total Concordance Mappings** | 62 | **62** | 4 Verified Official Crosswalks + 58 Expert-Reviewed Mappings. |
| **Canonical Concepts Activated** | 11 | **11** | 11 active concepts linked to national occupations; 1 concept (`CAN_OCC_DATA_ENGINEER`) explicitly held as idle. |

The updated schema in `src/backend/schemas/occupation.py` and service calculation in `src/backend/services/occupation_service.py` now expose `total_national_occupations: 28` and `total_international_references: 2`.

---

## 3. Authoritative Salary Sources & Metadata

All salary data are anchored in official statistical agency releases or clearly attributed benchmark models in `src/backend/data/salary/sources.json`:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   JOBINTEL 2.0 SALARY SOURCE PROVENANCE MATRIX                                  │
├───────────────┬────────────────────────────┬─────────────────────────────┬──────────────────────┬───────────────┤
│ Jurisdiction  │ Statistical Authority      │ Publication & Series        │ Compensation Concept │ License       │
├───────────────┼────────────────────────────┼─────────────────────────────┼──────────────────────┼───────────────┤
│ United States │ Bureau of Labor Statistics │ OEWS May 2023 Survey        │ Gross Annual Wages   │ Public Domain │
│ (US)          │ (BLS)                      │ (1.2M establishments)       │ (Straight-Time)      │ (US Gov)      │
├───────────────┼────────────────────────────┼─────────────────────────────┼──────────────────────┼───────────────┤
│ United Kingdom│ Office for National        │ ASHE Table 14/15 2024       │ Gross Annual Full-   │ Open Gov      │
│ (UK)          │ Statistics (ONS)           │ (1% PAYE HMRC sample)       │ Time Pay (Absence-0) │ Licence v3.0  │
├───────────────┼────────────────────────────┼─────────────────────────────┼──────────────────────┼───────────────┤
│ Australia     │ Australian Bureau of       │ EEH Cat. 6306.0 & JSA       │ Gross Annual Ordinary│ CC BY 4.0     │
│ (AU)          │ Statistics (ABS)           │ (8,000 employers)           │ Time Cash Earnings   │ International │
├───────────────┼────────────────────────────┼─────────────────────────────┼──────────────────────┼───────────────┤
│ Singapore     │ Ministry of Manpower (MOM) │ Occupational Wage Survey    │ Gross Monthly Wage   │ Singapore     │
│ (SG)          │ & SingStat                 │ (OWS) 2023 / AWS included   │ Annualized with AWS  │ Open Data     │
├───────────────┼────────────────────────────┼─────────────────────────────┼──────────────────────┼───────────────┤
│ India         │ JobIntel Intelligence      │ India Tech Benchmark 2024   │ Annual Cost to       │ JobIntel Open │
│ (IN)          │ Statistical Registry       │ & NCO-2015 Models           │ Company (CTC in LPA) │ Benchmark     │
└───────────────┴────────────────────────────┴─────────────────────────────┴──────────────────────┴───────────────┘
```

### Observation Inventory (`src/backend/data/salary/observations.json`)
Exactly 28 observation records are compiled, mapping 1:1 to every national occupation in the platform:
- **US (7 observations):** `15-1252` ($132,270), `15-2051` ($108,020), `15-1253` ($101,800), `15-1212` ($120,360), `15-1242` ($101,510), `15-1244` ($95,360), `15-1211` ($103,800).
- **UK (8 observations):** `2134` (£48,000), `2135` (£51,000), `2136` (£41,500), `2133` (£52,600), `2137` (£42,800), `2131` (£54,900), `3133` (£35,400), `3544` (£38,500). *(Withheld via HTTP 503 governance gate).*
- **AU (4 observations):** `261313` ($121,500 AUD), `224411` ($118,000 AUD), `262112` ($124,000 AUD), `261314` ($100,000 AUD).
- **SG (6 observations):** `25121` ($97,500 SGD), `25131` ($106,600 SGD), `25132` ($104,000 SGD), `25124` ($117,000 SGD), `25125` ($101,400 SGD), `25211` ($102,700 SGD).
- **IN (3 observations):** `2512.0100` (₹12,00,000 INR / 12.00 LPA), `2511.0100` (₹10,50,000 INR / 10.50 LPA), `2521.0100` (₹9,80,000 INR / 9.80 LPA).

---

## 4. Strict Separation of Nominal Foreign Exchange vs. Purchasing Power Parity (PPP)

A central requirement of Sprint 3B.1 is the formal decoupling of market exchange rates from purchasing power parity conversion factors.

### Reference Conversion Factors (`src/backend/data/salary/ppp_fx_rates.json`)

| Currency | Market | Nominal FX to USD (1 USD =) | Nominal USD Multiplier | World Bank ICP 2024 PPP Factor (1 Int$ =) | PPP USD Multiplier | PPP / FX Divergence Ratio |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **USD** | US | 1.0000 | 1.000000 | 1.0000 | 1.000000 | 1.00x |
| **GBP** | UK | 0.7850 | 1.273885 | 0.7100 | 1.408451 | 1.11x |
| **AUD** | AU | 1.5200 | 0.657895 | 1.4200 | 0.704225 | 1.07x |
| **SGD** | SG | 1.3450 | 0.743494 | 0.8400 | 1.190476 | 1.60x |
| **INR** | IN | 83.5000 | 0.011976 | 23.8000 | 0.042017 | **3.51x** |

### Mathematical and Analytical Demonstration
Consider an Indian Software Developer (`IN_NCO_2015:2512.0100`) earning a median salary of ₹12,00,000 INR (12.00 LPA):
- **Nominal USD Valuation:**
  $$\text{Nominal USD} = \frac{1,200,000 \text{ INR}}{83.50 \text{ INR/USD}} = \$14,371.20 \text{ USD}$$
- **Purchasing Power Parity Valuation:**
  $$\text{PPP USD (Int\$)} = \frac{1,200,000 \text{ INR}}{23.80 \text{ INR/Int\$}} = \$50,420.40 \text{ Int\$}$$

Comparing only nominal USD (\$14,371) to US Software Developers (\$132,270) implies a compensation ratio of 10.9%. However, evaluating the consumption purchasing power of that salary within India (\$50,420 Int$) reveals a living-standard equivalence of 38.1% of US median pay.

**Enforced System Rule:** The API and UI present both metrics concurrently and display the mandatory methodological disclaimer prohibiting arithmetic blending or substitution.

---

## 5. The 11 Methodological Dimensions of Comparability

The salary service (`src/backend/services/salary_service.py`) automatically evaluates cross-market comparisons across 11 discrete methodological checks:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   THE 11 METHODOLOGICAL DIMENSIONS OF SALARY COMPARABILITY             │
├────┬─────────────────────────────────┬─────────────────────────────────────────────────┤
│ #  │ Dimension                       │ Evaluated Criteria                              │
├────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│ 1  │ CURRENCY_MISMATCH               │ Dual FX / World Bank ICP 2024 PPP conversion.   │
│ 2  │ PAY_PERIOD_FREQUENCY            │ Annualized ordinary time vs monthly vs hourly.  │
│ 3  │ PAY_CONCEPT_DEFINITION          │ Straight-time wage vs Gross pay vs Cost to Co.  │
│ 4  │ SURVEY_POPULATION               │ Full-time non-managerial vs enterprise firms.   │
│ 5  │ OVERTIME_AND_BONUS_TREATMENT    │ Excluded (US) vs AWS included (SG) vs CTC (IN). │
│ 6  │ GEOGRAPHIC_COVERAGE             │ Nationwide multi-metro vs City-State vs Hubs.   │
│ 7  │ REFERENCE_YEAR_ALIGNMENT        │ 2023 release vs 2024 revised release.           │
│ 8  │ CLASSIFICATION_GRANULARITY      │ 4-digit unit group vs 6-digit detailed code.    │
│ 9  │ PERCENTILE_AVAILABILITY         │ Full p10-p90 spectrum vs median only.           │
│ 10 │ SOURCE_METHODOLOGY_TYPE         │ Official government census vs ML model/postings.│
│ 11 │ STATISTICAL_SUPPRESSION_AND_RSE │ Standard error, sample size, or governance gate.│
└────┴─────────────────────────────────┴─────────────────────────────────────────────────┘
```

### The 5 Comparability Verdicts
1. `DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS`: Identical jurisdictions, sources, and pay concepts.
2. `COMPARABLE_WITH_ADJUSTMENTS`: Both official statistical surveys, identical or close concordance, adjusted for frequency, bonuses, or inflation.
3. `COMPARABLE_WITH_MAJOR_CAVEATS`: Official survey compared against an ML model prediction (e.g. US/SG/AU vs IN), or asymmetrical classification scopes (`BROADER_THAN`/`NARROWER_THAN`).
4. `NOT_COMPARABLE`: Divergent occupational profiles or confidence scores below 0.50.
5. `INSUFFICIENT_DATA`: Data withheld due to statistical suppression or active governance publication gate.

---

## 6. UK ASHE Fail-Closed Governance Invariant

The UK Annual Survey of Hours and Earnings (ASHE) Table 14/15 dataset is governed by strict compliance policies. Under Sprint 2C.1 and 2C.2 rules:
- Direct queries for UK occupation salary profiles (`GET /v1/salary/occupations/UK_SOC_2020:2134`) or comparisons originating from a UK occupation return **HTTP 503 Service Unavailable** with error code `UK_DATA_NOT_PUBLISHED`.
- When non-UK occupations (e.g. US Software Developers) request cross-market comparisons, UK appears as a comparator row with:
  - `is_suppressed: true`
  - `original_median: null`
  - `nominal_usd_median: null`
  - `ppp_usd_median: null`
  - `comparability_verdict: INSUFFICIENT_DATA`
  - `comparability_caveats: ["UK ASHE salary publication is withheld by governance policy gate (fail-closed HTTP 503 policy)."]`

---

## 7. Backend API Architecture & Routing Contracts

The router `src/backend/routers/salary.py` exposes the new cross-market salary intelligence layer under `/v1/salary` and `/api/v1/salary`, while preserving all legacy endpoints (`/api/salary/*`):

| Endpoint | Method | Response Model | Description |
| :--- | :---: | :--- | :--- |
| `/v1/salary/sources` | GET | `list[SalarySourceMeta]` | Lists all 5 authoritative sources and licensing metadata. |
| `/v1/salary/sources/{source_id}` | GET | `SalarySourceMeta` | Retrieves single source details. |
| `/v1/salary/rates` | GET | `PppFxRatesPayload` | Returns spot FX rates and World Bank ICP 2024 PPP factors. |
| `/v1/salary/observations` | GET | `list[OccupationSalaryProfile]` | Lists observations across all 28 national occupations. |
| `/v1/salary/occupations/{id}` | GET | `OccupationSalaryProfile` | Detailed profile with percentiles (fails closed with 503 for UK). |
| `/v1/salary/compare` | GET | `CrossMarketSalaryComparisonResult` | Full cross-market comparison with automated comparability verdict. |
| `/v1/salary/convert` | GET | `SalaryConversionResult` | Live converter computing Nominal USD and PPP USD for any amount. |

---

## 8. Frontend Implementation: Tab 4 in Occupations Explorer

The frontend in `frontend/src/pages/OccupationsPage.tsx` incorporates a dedicated tab: **"Cross-Market Salary Intelligence"**:

1. **Benchmark Quick Selectors:** Instant switching between US Software Developers, US Data Scientists, AU Software Engineers, SG Software Developers, IN Software Developers, and UK Software Developers (with governance notice).
2. **Catalog Dropdown:** Direct selection across all 28 national occupations grouped by jurisdiction.
3. **Dual Metric Hero Cards:** Displays Original Median, Nominal USD Median (Market FX), and PPP USD Median (World Bank ICP 2024) side-by-side.
4. **Wage Distribution Strip:** Renders the 5 core percentiles (p10, p25, p50, p75, p90) with median highlight.
5. **Methodological Alert Callout:** Explicit banner explaining the difference between nominal exchange rate value and domestic purchasing power parity.
6. **Cross-Market Comparison Grid:** Displays cards for each matched jurisdiction with flag, title, relationship badge, comparability verdict badge (color-coded), side-by-side dual metrics, and detailed caveat explanations.
7. **Interactive FX vs. PPP Multiplier Calculator:** Allows users to test any salary amount in INR, GBP, AUD, SGD, or USD, showing immediate conversions and the domestic purchasing power multiplier.

---

## 9. Test Results & Verification

### Backend Tests
```
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

### Frontend Verification
- **Unit Tests:** `vitest run` passed (3 test files, 9 passed).
- **TypeScript & Vite Build:** `tsc -b && vite build` passed cleanly (**2,892 modules transformed**, 0 errors, built in 412ms).

---

## 10. Repository State & Deployment Readiness

- **Current Branch:** `staging/sprint2c3`
- **Current HEAD:** Verified
- **Master Baseline:** `198b79d` (completely untouched)
- **Deployment Safety:** No model artifacts were modified; frozen serialized models remain verified.
