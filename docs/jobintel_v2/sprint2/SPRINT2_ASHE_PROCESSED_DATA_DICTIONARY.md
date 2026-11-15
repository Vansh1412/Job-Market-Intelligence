# Sprint 2 Phase 2A — ASHE Processed Data Dictionary

**Artifact:** ASHE 2025 revised Table 15 (4), full-time annual gross median by occupation and GB work region  
**Transformation:** `ashe-table15-2025r-v1.0.2`  
**Source status:** `REVIEW_REQUIRED`; output is `LOCAL_PREPARATION_ONLY` and `publication_eligible: false`

## Dataset grain and row meaning

One row represents one ONS-published cell for a four-digit SOC 2020 occupation unit group in one of the eleven source work regions. It is an aggregate survey estimate, not an individual salary, employer, job posting, or person-level record. There are 412 occupation codes × 11 regions = 4,532 unique keys.

The selected source statistic is Table 15.7a **Median** of **Annual pay — Gross** in the **Full-Time** worksheet. It is GBP gross annual earnings before income tax, National Insurance and other deductions, excluding payments in kind, for adult-rate employee jobs held for over a year. Annual earnings can reflect absence effects. It refers to the tax year ending 5 April 2025. It must not be combined with weekly/hourly measures or presented as an individual salary distribution.

## Column dictionary

| Output column | Type / nullable | Source or derivation | Meaning and handling |
|---|---|---|---|
| `observation_id` | string, required | Deterministic hash of exact region/code key plus archive identity | Stable aggregate-cell ID; does not encode or invent a geography code. |
| `run_id` | string, required | Archive checksum prefix + transformation version | Links row to the machine-readable run manifest. |
| `market_id` | literal `UK` | Contract constant | Product market label. It does not imply full-UK geography. |
| `occupation_code` | four-digit string | Source code with Excel text apostrophe removed for keying | Canonical source SOC 2020 unit-group key; no SOC 2010 crosswalk is applied. |
| `occupation_description` | string, required | Occupation text after the region delimiter in source `Description` | ASHE table wording, trimmed for field use; remains separate from official SOC title. |
| `official_occupation_title` | string, required | Official ONS SOC 2020 structure workbook joined by exact code | Classification title. It is not substituted for the ASHE description where wording differs. |
| `source_occupation_code` | string, required | Original source `Code` cell string | Preserves source formatting, including the leading apostrophe used by Excel. |
| `classification_id` | literal `SOC` | Contract constant | Classification family. |
| `classification_version` | literal `2020` | Verified workbook and official code-set match | SOC version. |
| `major_group_code` | integer 1–9 | Official SOC 2020 hierarchy | Major-group parent for coverage reporting; not a calculated salary aggregate. |
| `major_group_title` | string, required | Official SOC 2020 hierarchy | Official major-group label. |
| `geography_code` | null | Not present in Table 15 (4) | No regional code is fabricated. |
| `geography_level` | literal `WORK_REGION` | Source dimension | Source-defined work region, not residence region. |
| `geography_label` | string | Parsed from the leading region text in source `Description` | One of 11 source labels: East, East Midlands, London, North East, North West, Scotland, South East, South West, Wales, West Midlands, Yorkshire and The Humber. |
| `source_description` | string, required | Original source `Description` cell | Full source description retained for traceability. |
| `salary_value` | decimal or null | Original numeric source median converted exactly through its decimal string representation | Present only for `REPORTED`; finite and >0. No annualization, FX conversion, imputation, averaging, or quantile calculation. |
| `original_ons_median_cell` | string; may be empty | Original source median cell, normalized to decimal text only for numeric cells | Preserves numeric value text or source marker; blank remains empty and is distinguished by `value_status`. |
| `original_ons_cv` | decimal or null | Paired Table 15.7b median CV cell | Original numeric coefficient of variation, in percent; finite and nonnegative. For reported cells it must be ≤20%. |
| `original_ons_cv_cell` | string or null | Original paired CV cell representation | Preserves numeric CV text or marker `x`, `.`, `..`, `:`, `-`; null indicates source blank. |
| `cv_quality_band` | string, required | Deterministic band from source CV or source marker | Numeric bands: `CV_LE_5`, `CV_GT_5_LE_10`, `CV_GT_10_LE_20`, `CV_GT_20`; marker states are explicit (`CV_GT_20_SUPPRESSED`, `CV_UNAVAILABLE`, `CV_BLANK_UNKNOWN`, etc.). |
| `value_status` | enum string | ONS median cell classification | See status table below; a null salary is never interpreted as zero. |
| `salary_measure_code` | literal `15.7a` | ONS workbook ID | Annual gross pay estimate workbook. |
| `earnings_definition` | literal `Gross annual pay` | ONS measure | Kept separate from basic, overtime, incentive, weekly and hourly measures. |
| `statistic` | literal `MEDIAN` | ONS source column | The employee-job median estimate as published by ONS. |
| `employee_group` | literal `FULL_TIME` | ONS worksheet | Source definition of full-time; not inferred from an occupation. |
| `currency` | literal `GBP` | ONS source measure | No currency conversion is performed. |
| `salary_period` | literal `ANNUAL` | ONS source measure | Annual period as published; not re-derived from weekly/hourly pay. |
| `reference_period` | literal `Tax year ending 5 April 2025` | ONS workbook and bulletin | Pay reference period; distinct from ingestion timestamp. |
| `source_id` | literal `uk.ons.ashe` | Sprint 1 source catalog ID | Catalog status remains `REVIEW_REQUIRED`. |
| `source_asset_version` | literal `2025-revised-table15-four-digit` | Pinned edition/table family | Exact source edition and table family. |
| `source_archive_sha256` | 64-char uppercase hex | SHA-256 of official ZIP | Verified value: `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3`. |
| `source_estimate_workbook` | string | Archive member name | Table 15.7a workbook identity; no local absolute path. |
| `source_estimate_sha256` | 64-char uppercase hex | SHA-256 of selected XLSX | Binds the estimate data to the archive member. |
| `source_cv_workbook` | string | Archive member name | Paired Table 15.7b workbook identity. |
| `source_cv_sha256` | 64-char uppercase hex | SHA-256 of selected CV XLSX | Binds CVs to the archive member. |
| `classification_reference_file` | string | Official ONS SOC 2020 workbook filename | Basis for code and hierarchy validation. |
| `classification_reference_sha256` | 64-char uppercase hex | SHA-256 of official SOC workbook | Verified value: `B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3`. |
| `source_reference` | URL string | Canonical ONS Table 15 landing page | Official source link used in provenance. |
| `catalog_source_reference` | URL string | Existing Sprint 1 catalog entry | Recorded for audit; currently differs from canonical URL. |
| `source_reference_matches_catalog` | boolean | Exact URL comparison | `false` for current catalog entry; the registry was not modified. |
| `source_attribution` | string | ONS/OGL attribution | Carries provider, dataset, edition and licence reference in each prepared row. |
| `transformation_version` | string | Pipeline constant | `ashe-table15-2025r-v1.0.2`. |

The run manifest, not each row, records the UTC `ingested_at` timestamp. The CSV is deterministic across reruns; its `run_id` refers to the corresponding timestamped manifest.

## Estimate status and missingness

| `value_status` | Original median cell | `salary_value` | Meaning |
|---|---|---|---|
| `REPORTED` | Numeric source estimate | Positive finite decimal | Published estimate. Paired numeric CV is required and must be ≤20%. |
| `SUPPRESSED_QUALITY` | `x` | null | ONS quality suppression; source notes say CV >20% and unreliable for practical purposes. |
| `SUPPRESSED_DISCLOSURE` | `..` | null | ONS disclosure suppression. |
| `NOT_APPLICABLE` | `:` | null | ONS not-applicable state. |
| `NIL_OR_NEGLIGIBLE` | `-` | null | ONS nil/negligible marker, kept distinct from numeric zero. |
| `BLANK_UNKNOWN` | Empty source cell | null | Blank state; workbook legend does not define a single cause. Not assumed suppressed. |

In this exact full-time median column the output has 1,339 `REPORTED`, 2,818 `SUPPRESSED_QUALITY`, and 375 `BLANK_UNKNOWN` rows. The other documented estimate markers are supported by the parser contract but were absent in the observed median column. In the paired CV workbook, numeric values are retained; `x`, `.`, `..`, `:`, `-`, and blank remain distinct source states.

## Provenance manifest

`provenance_manifest.json` records source ID, exact ONS source URL and catalog URL, local-only processing mode, reuse review status, dataset edition, pay reference period, UTC ingestion timestamp, raw archive filename/size/SHA-256, archive member and extraction counts, selected workbook filenames/checksums, official SOC reference filename/checksum, transformation version, classification, region coverage, selected sheet/measure/variables, row/validation counts, marker counts, source attribution, Sprint 1 `DataProvenance` and `DataQualityResult`, processed CSV filename/checksum, and the redacted report filename. It contains no salary-cell dump or rejected source contents.

## Reproduction

```powershell
python -m src.backend.ingestion --local-preparation-only
```

See [SPRINT2_INGESTION_IMPLEMENTATION.md](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_INGESTION_IMPLEMENTATION.md>) for file paths, asset hashes, validation rules, and output state. The local machine-readable manifest and CSV are ignored data outputs and must not be committed.
