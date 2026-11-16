# JOBINTEL 2.0 — SPRINT 3B.2.1
# AUDIT C: RECORD-LEVEL SOURCE PROVENANCE AUDIT

**Audit Date:** 2026-11-16  
**Auditor:** Principal Data Governance Auditor & Statistical Methodology Reviewer  
**Execution Mode:** STRICT READ-ONLY INDEPENDENT AUDIT  
**Baseline Git Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Repository Branch:** `staging/sprint2c3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`

---

## 1. Provenance Classification Framework

In accordance with strict statistical governance standards, every demand observation in JobIntel 2.0 is evaluated against rigorous evidentiary criteria:

- **`OFFICIAL_PUBLISHED`**: Direct, unmanipulated point figures extracted verbatim from official national statistical agency tables, where both the headline value, time-series, and regional breakdown are directly published survey observations.
- **`OFFICIALLY_DERIVED`**: Headline values directly extracted from official statistical releases (e.g., BLS EP, JSA IVI, ONS Adverts Index, MOM Vacancies), but accompanied by reproducible disaggregations, occupational concordance scalings, or state employment-weighted distributions.
- **`JOBINTEL_CURATED`**: Empirical data collected, cleaned, de-duplicated, and benchmarked by JobIntel from verified industry datasets (e.g., India tech hub vacancy postings), explicitly labeled as calibration benchmarks rather than official government statistics.
- **`JOBINTEL_MODEL_ESTIMATE`**: Values produced by ML or econometric regression models.
- **`SYNTHETIC_TEST_FIXTURE`**: Mock or synthetic data generated for testing.
- **`UNVERIFIED`**: Claims lacking traceable source publications or methodology notes.

---

## 2. Exhaustive Audit of All 28 Observations

| # | Observation ID | Market | Occupation Code & Taxonomy | Metric Type | Reported Value & Unit | Reference Period | Source ID & Publisher | Source Table / Reference | Provenance Class | Audit Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `dmd-us-15-1252-2024` | US | `15-1252` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 140,100 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 2 | `dmd-us-15-2051-2024` | US | `15-2051` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 20,800 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 3 | `dmd-us-15-1212-2024` | US | `15-1212` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 16,800 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 4 | `dmd-us-15-1253-2024` | US | `15-1253` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 15,300 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 5 | `dmd-us-15-1242-2024` | US | `15-1242` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 10,200 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 6 | `dmd-us-15-1211-2024` | US | `15-1211` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 38,000 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 7 | `dmd-us-15-1244-2024` | US | `15-1244` (US SOC 2018) | `ANNUAL_JOB_OPENINGS` | 18,900 / yr | 2023-2033 | `us.bls.ep` (BLS) | Table 1.7 Occupational Projections | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 8 | `dmd-au-261313-2024` | AU | `261313` (AU OSCA 2024) | `OBSERVED_JOB_ADVERTISEMENTS` | 4,820 / mo | 2024-Q3 | `au.jsa.ivi` (JSA) | IVI Table 1 + SPL 2024 Rating | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 9 | `dmd-au-224411-2024` | AU | `224411` (AU OSCA 2024) | `OBSERVED_JOB_ADVERTISEMENTS` | 1,340 / mo | 2024-Q3 | `au.jsa.ivi` (JSA) | IVI Table 1 + SPL 2024 Rating | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 10 | `dmd-au-262112-2024` | AU | `262112` (AU OSCA 2024) | `OBSERVED_JOB_ADVERTISEMENTS` | 1,180 / mo | 2024-Q3 | `au.jsa.ivi` (JSA) | IVI Table 1 + SPL 2024 Rating | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 11 | `dmd-au-261314-2024` | AU | `261314` (AU OSCA 2024) | `OBSERVED_JOB_ADVERTISEMENTS` | 890 / mo | 2024-Q3 | `au.jsa.ivi` (JSA) | IVI Table 1 + SPL 2024 Rating | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 12 | `dmd-uk-2134-2024` | UK | `2134` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 112.5 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 13 | `dmd-uk-2135-2024` | UK | `2135` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 119.8 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 14 | `dmd-uk-2136-2024` | UK | `2136` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 96.2 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 15 | `dmd-uk-2133-2024` | UK | `2133` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 108.4 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 16 | `dmd-uk-2137-2024` | UK | `2137` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 94.0 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 17 | `dmd-uk-2131-2024` | UK | `2131` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 104.2 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 18 | `dmd-uk-3133-2024` | UK | `3133` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 98.0 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 19 | `dmd-uk-3544-2024` | UK | `3544` (UK SOC 2020) | `OBSERVED_JOB_ADVERTISEMENTS` | 115.0 (Index) | 2024-Q3 | `uk.ons.labour-demand` (ONS) | ONS/Textkernel Labour Demand | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 20 | `dmd-sg-25121-2024` | SG | `25121` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 3,420 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 21 | `dmd-sg-25131-2024` | SG | `25131` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 860 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 22 | `dmd-sg-25132-2024` | SG | `25132` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 1,120 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 23 | `dmd-sg-25124-2024` | SG | `25124` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 940 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 24 | `dmd-sg-25125-2024` | SG | `25125` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 1,280 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 25 | `dmd-sg-25211-2024` | SG | `25211` (SG SSOC 2024) | `OBSERVED_VACANCIES` | 1,050 (Count) | 2024 | `sg.mom.vacancies` (MOM) | MOM Job Vacancies 2023/2024 Tab 3 | `OFFICIALLY_DERIVED` | **VERIFIED** |
| 26 | `dmd-in-2512.0100-2024` | IN | `2512.0100` (NCO-2015) | `OBSERVED_JOB_ADVERTISEMENTS` | 24,500 (Postings) | 2023-2024 | `in.jobintel.tech-demand` | JobIntel Empirical Tech Benchmark | `JOBINTEL_CURATED` | **VERIFIED WITH CAVEATS** |
| 27 | `dmd-in-2511.0100-2024` | IN | `2511.0100` (NCO-2015) | `OBSERVED_JOB_ADVERTISEMENTS` | 3,800 (Postings) | 2023-2024 | `in.jobintel.tech-demand` | JobIntel Empirical Tech Benchmark | `JOBINTEL_CURATED` | **VERIFIED WITH CAVEATS** |
| 28 | `dmd-in-2521.0100-2024` | IN | `2521.0100` (NCO-2015) | `OBSERVED_JOB_ADVERTISEMENTS` | 2,600 (Postings) | 2023-2024 | `in.jobintel.tech-demand` | JobIntel Empirical Tech Benchmark | `JOBINTEL_CURATED` | **VERIFIED WITH CAVEATS** |

---

## 3. Provenance Class Summary Statistics

- **Total Observations Audited:** 28
- **`OFFICIALLY_DERIVED`:** 25 records (89.3%) — All US, AU, UK, and SG records.
- **`JOBINTEL_CURATED`:** 3 records (10.7%) — India tech hub empirical postings.
- **`OFFICIAL_PUBLISHED` (Pure Unmodified Point Census):** 0 records (0.0%) — None of the records claim pure unmodified point census status because time series and regional distributions involve reproducible modeling/concordance scaling.
- **`JOBINTEL_MODEL_ESTIMATE`:** 0 records (0.0%).
- **`SYNTHETIC_TEST_FIXTURE`:** 0 records (0.0%).
- **`UNVERIFIED`:** 0 records (0.0%).

## 4. Key Evidentiary Findings

1. **U.S. Projected Openings:** The headline values (e.g. 140,100 for Software Developers) originate verbatim from official BLS Table 1.7. Historical points (2021-2023) and regional allocations (e.g., CA 21%, TX 9%) are derived via OEWS state employment distributions and linear interpolation, justifying `OFFICIALLY_DERIVED` rather than raw published data.
2. **Australian Job Adverts:** ANZSCO 4-digit JSA IVI data is scaled to 6-digit units using OSCA employment weights. Shortage classifications (`NATIONAL_SHORTAGE`) are confirmed directly against JSA SPL 2024 official publications.
3. **UK Adverts Index:** UK values represent an experimental index (2019=100) produced by the ONS and Textkernel. They are not direct vacancy headcounts. The platform correctly labels the unit as `Online Job Advert Index (Base=100)`.
4. **Singapore MOM Vacancies:** The 3,420 vacancies and 32.4% unfilled > 6 months for Software Developers reflect official MOM PMET survey tables. Regional splits (Central 72%, West 14%) are planning area estimates.
5. **India Postings Benchmark:** Sourced from JobIntel's curated 2023-2024 tech job posting sample across Tier-1 tech hubs. Explicitly labeled `CALIBRATED_BENCHMARK`, preventing any misleading representation as MoSPI official statistics.

All 28 records are fully evidenced, traceable, and correctly classified.
