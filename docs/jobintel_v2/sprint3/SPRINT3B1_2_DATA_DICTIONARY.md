# JOBINTEL 2.0 — SALARY DATA DICTIONARY
## Cross-Market Salary Intelligence Schema, Entity Contracts & Semantic Rules

**Document Reference:** `JOBINTEL-DATA-DICT-3B.1.2-20261116`  
**Sprint:** 3B.1.2 (Salary Data Remediation and Evidence Closure)  
**Schema Implementation:** `src/backend/schemas/salary.py`  
**Data Directory:** `src/backend/data/salary/`  
**Compliance Standard:** Pydantic V2 / OpenAPI 3.1 Strict Typing

---

## 1. Schema Architecture Overview

The Salary Intelligence subsystem provides strongly-typed data contracts for:
1. **Salary Sources (`SalarySourceMeta`):** Institutional provenance, legal licensing, and survey methodology.
2. **Exchange Rates & PPP Factors (`PppFxRatesPayload`, `CurrencyRateInfo`):** Static annual reference FX and World Bank private consumption PPP conversion factors.
3. **Occupation Salary Profiles (`OccupationSalaryProfile`):** National salary distributions, percentiles (P10–P90), sample size, and RSE metrics.
4. **Comparability Engine Results (`CrossMarketSalaryComparisonResult`, `CrossMarketSalaryComparisonItem`):** Automated evaluation across 11 methodological dimensions.
5. **Data Governance Observations (`SalaryObservation`):** Immutable historical data collection records with decimal precision and timezone validation.

---

## 2. Entity Specifications

### 2.1 `SalarySourceMeta`
Metadata describing the primary statistical agency or benchmark authority for a jurisdiction.

| Field Name | Type | Nullable | Description & Constraints | Example |
| :--- | :--- | :---: | :--- | :--- |
| `source_id` | `str` | No | Unique identifier for the source release. | `"US_BLS_OEWS_2023"` |
| `market_id` | `str` | No | ISO-style market identifier (`US`, `UK`, `AU`, `SG`, `IN`). | `"US"` |
| `authority` | `str` | No | Name of statistical bureau or publishing body. | `"U.S. Bureau of Labor Statistics (BLS)"` |
| `publication_name` | `str` | No | Official survey title and edition. | `"OEWS Survey May 2023"` |
| `reference_period` | `str` | No | Period during which wages were observed. | `"May 2023"` |
| `release_date` | `str` | No | ISO date of publication release (`YYYY-MM-DD`). | `"2024-04-03"` |
| `license` | `str` | No | Legal terms of use / licensing. | `"Public Domain (U.S. Government Work)"` |
| `currency` | `str` | No | Standard ISO 4217 currency code. | `"USD"` |
| `pay_concept` | `str` | No | Definition of wage or compensation measured. | `"Gross annual straight-time wages..."` |
| `frequency` | `str` | No | Annualized collection frequency (`ANNUAL`). | `"ANNUAL"` |
| `sample_coverage` | `str` | No | Survey sample size and universe description. | `"1.2 million non-farm establishments"` |
| `source_url` | `str` | No | Stable URL to publication or national index. | `"https://www.bls.gov/oes/current/oes_nat.htm"` |
| `is_active` | `bool` | No | Operational flag (default: `true`). | `true` |
| `governance_gate` | `str \| None` | Yes | Active governance gate policy identifier. | `"GOVERNANCE_REVOCATION_GATE_ENFORCED"` |

---

### 2.2 `CurrencyRateInfo` & `PppFxRatesPayload`
Dual-conversion rates representing external currency value (FX) and domestic purchasing power (PPP).

#### `CurrencyRateInfo`
| Field Name | Type | Nullable | Description & Constraints | Example |
| :--- | :--- | :---: | :--- | :--- |
| `currency` | `str` | No | ISO 4217 currency code (`USD`, `GBP`, `AUD`, `SGD`, `INR`). | `"INR"` |
| `market_id` | `str` | No | Target market jurisdiction code. | `"IN"` |
| `nominal_fx_to_usd` | `float` | No | Local currency units per 1 USD (Static 2024 average). | `83.50` |
| `nominal_usd_multiplier` | `float` | No | Multiplier to convert local currency to USD ($1 / \text{FX}$). | `0.011976` |
| `ppp_conversion_factor_to_usd` | `float` | No | World Bank WDI private consumption factor (`PA.NUS.PRVT.PP`). | `23.80` |
| `ppp_usd_multiplier` | `float` | No | Multiplier to convert local currency to Int\$ ($1 / \text{PPP}$). | `0.042017` |
| `fx_source` | `str` | No | Primary central bank or IMF data source. | `"Reserve Bank of India 2024 Reference Average"` |
| `ppp_source` | `str` | No | Specific World Bank WDI indicator and methodology. | `"World Bank WDI (PA.NUS.PRVT.PP) 2024 Extrapolation"` |

---

### 2.3 `SalaryPercentiles`
Distributional wage percentiles. **Strict Non-Fabrication Rule:** Where statistical agencies do not compile or publish a specific percentile, the value **MUST be `null`** (Python `None`).

| Field Name | Type | Nullable | Description & Constraints | Supported by Jurisdiction |
| :--- | :--- | :---: | :--- | :--- |
| `p10` | `float \| None` | Yes | 10th Percentile (Bottom 10% earned less than this amount). | US, UK, IN (AU: `null`, SG: `null`) |
| `p25` | `float \| None` | Yes | 25th Percentile (First quartile). | US, UK, AU, SG, IN |
| `p50` | `float \| None` | Yes | 50th Percentile / Median (Core comparison benchmark). | US, UK, AU, SG, IN |
| `p75` | `float \| None` | Yes | 75th Percentile (Third quartile). | US, UK, AU, SG, IN |
| `p90` | `float \| None` | Yes | 90th Percentile (Top 10% earned more than this amount). | US, UK, IN (AU: `null`, SG: `null`) |

---

### 2.4 `OccupationSalaryProfile`
Published profile of an occupation within a single jurisdiction.

| Field Name | Type | Nullable | Description & Constraints | Example |
| :--- | :--- | :---: | :--- | :--- |
| `observation_id` | `str` | No | Unique observation identifier. | `"sal_obs_us_151252_2023"` |
| `occupation_id` | `str` | No | Prefixed national occupation code. | `"US_SOC_2018:15-1252"` |
| `occupation_title` | `str` | No | Standardized occupational title. | `"Software Developers"` |
| `market_id` | `str` | No | Country / Market jurisdiction. | `"US"` |
| `source_id` | `str` | No | Foreign key linking to `SalarySourceMeta`. | `"US_BLS_OEWS_2023"` |
| `currency` | `str` | No | Native survey currency. | `"USD"` |
| `period_type` | `str` | No | Collection frequency (default: `"ANNUAL"`). | `"ANNUAL"` |
| `mean` | `float \| None` | Yes | Arithmetic mean wage if published. | `138110.0` |
| `percentiles` | `SalaryPercentiles`| No | Distribution percentiles (P10–P90). | `{p10: 77020, ..., p90: 208620}` |
| `nominal_usd_median` | `float \| None` | Yes | Median converted via Nominal FX. | `132270.0` |
| `ppp_usd_median` | `float \| None` | Yes | Median converted via World Bank PPP. | `132270.0` |
| `sample_size` | `int \| None` | Yes | Reported employment or respondent count. | `1632300` |
| `standard_error` | `float \| None` | Yes | Relative standard error (RSE %) of mean. | `0.6` |
| `is_suppressed` | `bool` | No | Suppression / withholding flag. | `false` |
| `quality_flag` | `str` | No | Provenance classification (`OFFICIAL_STATISTICAL_RELEASE`, `OFFICIALLY_DERIVED`, `MODEL_PREDICTION`, `GOVERNANCE_WITHHELD`). | `"OFFICIAL_STATISTICAL_RELEASE"` |
| `source_meta` | `SalarySourceMeta \| None` | Yes | Hydrated source metadata. | Object |
| `notes` | `str` | No | Methodological notes and caveats. | `"BLS OEWS straight-time gross..."` |

---

### 2.5 `ComparabilityVerdict` Enum & Evaluation Hierarchy
Automated evaluation of comparability between two occupational wage observations across 11 dimensions.

```
                                [Evaluate Comparability]
                                           │
                ┌──────────────────────────┴──────────────────────────┐
                ▼                                                     ▼
     [Target/Source Suppressed                                [Unmapped OR
        OR Median is null]                               Confidence < 0.50]
                │                                                     │
                ▼                                                     ▼
    INSUFFICIENT_DATA                                          NOT_COMPARABLE
                                                                      │
                                ┌─────────────────────────────────────┴─────────────────────────────────────┐
                                ▼                                                                           ▼
                    [Model Prediction OR                                                           [Currency Mismatch
               Relationship Broader/Narrower                                                               OR
                    OR Confidence < 0.88]                                                       Reference Year Mismatch]
                                │                                                                           │
                                ▼                                                                           ▼
                  COMPARABLE_WITH_MAJOR_CAVEATS                                                COMPARABLE_WITH_ADJUSTMENTS
                                                                                                            │
                                                                                                            ▼
                                                                                              DIRECTLY_COMPARABLE_WITHIN_
                                                                                                  SOURCE_LIMITATIONS
```

| Enum Member | Evaluation Condition | Meaning |
| :--- | :--- | :--- |
| **`INSUFFICIENT_DATA`** | Source or target observation is suppressed (e.g. UK fail-closed HTTP 503) or median is `null`. | Comparison cannot be performed due to data withholding or missing values. |
| **`NOT_COMPARABLE`** | `relationship_type == "NO_SUPPORTED_MAPPING"` OR `confidence_score < 0.50`. | Concordance mapping is absent or insufficient to justify wage benchmarking. |
| **`COMPARABLE_WITH_MAJOR_CAVEATS`** | Quality flag is `MODEL_PREDICTION`, OR relationship is `BROADER_THAN`/`NARROWER_THAN`, OR `confidence_score < 0.88`. | Substantial structural differences in data source (e.g., ML vacancy model vs. census survey) or job task scope. |
| **`COMPARABLE_WITH_ADJUSTMENTS`** | Different currencies requiring dual FX/PPP conversions, OR differing reference survey years (e.g., 2023 vs 2024). | Methodologically comparable official surveys requiring economic conversion adjustments. |
| **`DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS`** | Identical currency, same survey reference period, same pay concept, and high-confidence mapping ($\ge 0.88$). | Direct statistical comparability subject only to standard survey sampling error. |

---

## 3. Comparability Dimensions Reference

Every cross-market comparison explicitly reports on 11 standardized dimensions:
1. `CURRENCY_MISMATCH`: Local currencies converted via both Nominal FX and World Bank PPP.
2. `PAY_PERIOD_FREQUENCY`: Standardized annualization factors ($2,080 \text{ hours}$, $52 \text{ weeks}$, $12 \text{ months}$).
3. `PAY_CONCEPT_DEFINITION`: Gross cash wages vs. straight-time earnings vs. Total Cost to Company (CTC).
4. `SURVEY_POPULATION`: Non-farm business establishments vs. PAYE employee records vs. tech metro postings.
5. `OVERTIME_AND_BONUS_TREATMENT`: Treatment of overtime premiums and annual bonuses.
6. `GEOGRAPHIC_COVERAGE`: Nationwide multi-state vs. city-state vs. concentrated tech metros.
7. `REFERENCE_YEAR_ALIGNMENT`: Temporal alignment (e.g., May 2023 vs. 2024 benchmark).
8. `CLASSIFICATION_GRANULARITY`: 4-digit unit groups (e.g., SOC 2134) vs. 6-digit detailed occupations (e.g., SOC 15-1252).
9. `PERCENTILE_AVAILABILITY`: Complete 5-point spectrum vs. 3-point quartile reporting (null P10/P90).
10. `SOURCE_METHODOLOGY_TYPE`: Government statutory probability survey vs. calibrated vacancy model.
11. `STATISTICAL_SUPPRESSION_AND_RSE`: Active governance withholding and relative standard error limits.
