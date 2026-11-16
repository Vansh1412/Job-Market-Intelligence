# JOBINTEL 2.0 — SPRINT 3B.2.3 PROVENANCE AUDIT REPORT
## Record-Level Provenance, Transformation Lineage & Statistical Authenticity

**Audit Date:** November 16, 2026  
**Auditor:** Independent Principal Data Governance Auditor  
**Audit Scope:** Independent inspection of `src/backend/schemas/demand.py`, `src/backend/data/demand/observations.json`, `sources.json`, and `metrics.json`.

---

### 1. PROVENANCE TAXONOMY ARCHITECTURE

The audit inspected `src/backend/schemas/demand.py` to verify the semantic categorization of observation provenance:

```python
class DemandProvenance(StrEnum):
    OFFICIAL_PUBLISHED = "OFFICIAL_PUBLISHED"
    OFFICIALLY_DERIVED = "OFFICIALLY_DERIVED"
    JOBINTEL_CURATED = "JOBINTEL_CURATED"
    JOBINTEL_MODEL_ESTIMATE = "JOBINTEL_MODEL_ESTIMATE"
    SYNTHETIC_TEST_FIXTURE = "SYNTHETIC_TEST_FIXTURE"
    UNVERIFIED = "UNVERIFIED"
```

All 6 required categories are formally defined with semantic descriptions in `PROVENANCE_METADATA`:
- `OFFICIAL_PUBLISHED`: Directly extracted from official statistical agency releases or statutory censuses with no computational transformation.
- `OFFICIALLY_DERIVED`: Produced through reproducible calculation, annualization, employment-weighting, or taxonomy concordance from verified official input statistics.
- `JOBINTEL_CURATED`: Curated research benchmark compiled and validated by JobIntel Research Labs from empirical industry posting samples.
- `JOBINTEL_MODEL_ESTIMATE`: Econometric or machine learning model estimate based on multi-source feature modeling.
- `SYNTHETIC_TEST_FIXTURE`: Synthetically generated data points for testing.
- `UNVERIFIED`: Data with unconfirmed provenance.

---

### 2. AUDIT SUMMARY BY PROVENANCE CATEGORY

The audit performed an independent enumeration of all 28 records in `src/backend/data/demand/observations.json`:

| Category | Observation Count | Percentage | Markets Covered | Audit Findings |
|---|---|---|---|---|
| `OFFICIAL_PUBLISHED` | **0** | 0.0% | None | Zero observations are tagged `OFFICIAL_PUBLISHED`. All official records bundle derived sub-national distributions. |
| `OFFICIALLY_DERIVED` | **25** | 89.3% | US (7), AU (4), UK (8), SG (6) | All 25 observations derive from official statistical authorities (BLS, JSA, ONS, MOM) with computational scaling or regional allocation. |
| `JOBINTEL_CURATED` | **3** | 10.7% | IN (3) | All 3 Indian observations represent calibrated empirical tech posting samples across Bangalore, Hyderabad, NCR, and Pune. |
| `JOBINTEL_MODEL_ESTIMATE`| **0** | 0.0% | None | No econometric model estimates are deployed in the demand observation registry. |
| `SYNTHETIC_TEST_FIXTURE`| **0** | 0.0% | None | No test fixtures exist in the active data registry. |
| `UNVERIFIED` | **0** | 0.0% | None | All observations have verified source links and transformations. |
| **TOTAL** | **28** | **100.0%** | **5 Markets** | **All 28 records classified.** |

#### Critical Finding: Distinction Between `OFFICIAL_PUBLISHED` and `OFFICIALLY_DERIVED`
The previous sprint reported "25 official, 3 curated". The independent audit confirms that **none of the 25 official observations are pure `OFFICIAL_PUBLISHED`** in their entirety. Because each observation object in `DemandObservation` bundles both the national aggregate and regional distributions:
1. **US (7 records):** National openings are official BLS projections (Table 1.7), but state distributions are derived via OEWS employment weights.
2. **AU (4 records):** 6-digit OSCA occupations inherit values scaled from 4-digit ANZSCO 2613 group data.
3. **UK (8 records):** Indices are experimental series constructed by ONS combining digital job board feeds from Textkernel.
4. **SG (6 records):** National PMET vacancies are official MOM survey counts, but regional breakdowns are synthetic planning area proxies.

Classifying all 25 as `OFFICIALLY_DERIVED` rather than `OFFICIAL_PUBLISHED` is a **methodologically conservative and defensible decision** that prevents misleading users into believing derived state distributions are official census statistics.

---

### 3. EXHAUSTIVE RECORD-BY-RECORD AUDIT (28 OBSERVATIONS)

| # | Observation ID | Market | Occupation ID | Metric Type | Value & Unit | Provenance | Source ID & Publisher | Transformation Method | Verification Result |
|---|---|---|---|---|---|---|---|---|---|
| 01 | `dmd-us-15-1252-2024` | US | `15-1252` | `ANNUAL_JOB_OPENINGS` | 140,100 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 02 | `dmd-us-15-2051-2024` | US | `15-2051` | `ANNUAL_JOB_OPENINGS` | 20,800 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 03 | `dmd-us-15-1212-2024` | US | `15-1212` | `ANNUAL_JOB_OPENINGS` | 16,800 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 04 | `dmd-us-15-1253-2024` | US | `15-1253` | `ANNUAL_JOB_OPENINGS` | 15,300 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 05 | `dmd-us-15-1242-2024` | US | `15-1242` | `ANNUAL_JOB_OPENINGS` | 10,200 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 06 | `dmd-us-15-1211-2024` | US | `15-1211` | `ANNUAL_JOB_OPENINGS` | 38,000 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 07 | `dmd-us-15-1244-2024` | US | `15-1244` | `ANNUAL_JOB_OPENINGS` | 18,900 Annual Openings | `OFFICIALLY_DERIVED` | `us.bls.ep` (BLS) | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **PASS** |
| 08 | `dmd-au-261313-2024` | AU | `261313` | `OBSERVED_JOB_ADVERTISEMENTS` | 4,820 Monthly Adverts | `OFFICIALLY_DERIVED` | `au.jsa.ivi` (JSA) | `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING` | **PASS** |
| 09 | `dmd-au-224411-2024` | AU | `224411` | `OBSERVED_JOB_ADVERTISEMENTS` | 1,340 Monthly Adverts | `OFFICIALLY_DERIVED` | `au.jsa.ivi` (JSA) | `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING` | **PASS** |
| 10 | `dmd-au-262112-2024` | AU | `262112` | `OBSERVED_JOB_ADVERTISEMENTS` | 1,180 Monthly Adverts | `OFFICIALLY_DERIVED` | `au.jsa.ivi` (JSA) | `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING` | **PASS** |
| 11 | `dmd-au-261314-2024` | AU | `261314` | `OBSERVED_JOB_ADVERTISEMENTS` | 890 Monthly Adverts | `OFFICIALLY_DERIVED` | `au.jsa.ivi` (JSA) | `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING` | **PASS** |
| 12 | `dmd-uk-2134-2024` | UK | `2134` | `OBSERVED_JOB_ADVERTISEMENTS` | 112.5 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 13 | `dmd-uk-2135-2024` | UK | `2135` | `OBSERVED_JOB_ADVERTISEMENTS` | 119.8 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 14 | `dmd-uk-2136-2024` | UK | `2136` | `OBSERVED_JOB_ADVERTISEMENTS` | 96.2 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 15 | `dmd-uk-2133-2024` | UK | `2133` | `OBSERVED_JOB_ADVERTISEMENTS` | 108.4 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 16 | `dmd-uk-2137-2024` | UK | `2137` | `OBSERVED_JOB_ADVERTISEMENTS` | 94.0 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 17 | `dmd-uk-2131-2024` | UK | `2131` | `OBSERVED_JOB_ADVERTISEMENTS` | 104.2 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 18 | `dmd-uk-3133-2024` | UK | `3133` | `OBSERVED_JOB_ADVERTISEMENTS` | 98.0 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 19 | `dmd-uk-3544-2024` | UK | `3544` | `OBSERVED_JOB_ADVERTISEMENTS` | 115.0 Advert Index | `OFFICIALLY_DERIVED` | `uk.ons.labour-demand` (ONS/Textkernel) | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **PASS (GATED)** |
| 20 | `dmd-sg-25121-2024` | SG | `25121` | `OBSERVED_VACANCIES` | 3,420 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 21 | `dmd-sg-25131-2024` | SG | `25131` | `OBSERVED_VACANCIES` | 860 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 22 | `dmd-sg-25132-2024` | SG | `25132` | `OBSERVED_VACANCIES` | 1,120 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 23 | `dmd-sg-25124-2024` | SG | `25124` | `OBSERVED_VACANCIES` | 940 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 24 | `dmd-sg-25125-2024` | SG | `25125` | `OBSERVED_VACANCIES` | 1,280 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 25 | `dmd-sg-25211-2024` | SG | `25211` | `OBSERVED_VACANCIES` | 1,050 Vacancies | `OFFICIALLY_DERIVED` | `sg.mom.vacancies` (MOM) | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **PASS** |
| 26 | `dmd-in-2512.0100-2024` | IN | `2512.0100` | `OBSERVED_JOB_ADVERTISEMENTS` | 24,500 Postings | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` (JobIntel) | `JOBINTEL_EMPIRICAL_TECH_HUB_POSTINGS_BENCHMARK` | **PASS** |
| 27 | `dmd-in-2511.0100-2024` | IN | `2511.0100` | `OBSERVED_JOB_ADVERTISEMENTS` | 3,800 Postings | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` (JobIntel) | `JOBINTEL_EMPIRICAL_TECH_HUB_POSTINGS_BENCHMARK` | **PASS** |
| 28 | `dmd-in-2521.0100-2024` | IN | `2521.0100` | `OBSERVED_JOB_ADVERTISEMENTS` | 2,600 Postings | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` (JobIntel) | `JOBINTEL_EMPIRICAL_TECH_HUB_POSTINGS_BENCHMARK` | **PASS** |

---

### 4. DATA INTEGRITY & REFERENTIAL CHECKS

1. **Foreign Key Integrity:**
   - 28/28 source IDs resolve to registered entries in `src/backend/data/demand/sources.json`.
   - 28/28 metric types resolve to definitions in `src/backend/data/demand/metrics.json`.
2. **Duplicate Observations:**
   - Exactly 0 duplicate `observation_id` values found.
3. **Classification System Consistency:**
   - US: All 7 observations map to 2018 SOC 6-digit codes.
   - AU: All 4 observations map to 2024 OSCA / ANZSCO v1.3 6-digit codes.
   - UK: All 8 observations map to SOC 2020 4-digit codes.
   - SG: All 6 observations map to SSOC 2020 5-digit PMET codes.
   - IN: All 3 observations map to NCO-2015 8-digit codes.
4. **Transformation Completeness:**
   - 28/28 observations contain non-null `transformation_method` strings.
   - 28/28 observations contain non-null `derivation_summary` strings detailing lineage.

---

### 5. AUDIT VERDICT

```text
PROVENANCE AUDIT VERDICT: VERIFIED CLOSED
Status: PASS
Exact Counts: OFFICIALLY_DERIVED: 25, JOBINTEL_CURATED: 3, OFFICIAL_PUBLISHED: 0.
Referential Integrity: 100% valid.
Transformation Lineage: 100% documented.
```
