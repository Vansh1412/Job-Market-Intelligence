# Sprint 2 Proposed Data Dictionary

**Status:** Proposed contract only. No UK records have been ingested. Names/fields require review against the exact selected source workbook before implementation.

## Core principles

- Keep all source-reported definitions and values. Store salary as GBP, without automatic FX, annualization, or period conversion.
- Distinguish gross/basic earnings, mean/median, employee/job population, full-/part-time, sex category, hours, and reporting period.
- Keep aggregate ASHE estimates aggregate; do not model or report them as individual salaries or individual-level distributions.
- Preserve source-native SOC 2020 code and source version. Candidate title matching is not an accepted canonical mapping without evidence/review.
- Model suppressed/not reported/not applicable/unavailable/invalid states explicitly. Never fill suppressed values.
- Every measurement must refer to a source ID, exact edition, source reference period, and transformation version.

## Proposed entities

### `UKOccupation`

| Field | Type | Meaning |
|---|---|---|
| `occupation_code` | string | Official SOC 2020 code, exact source formatting retained. |
| `classification_id` | enum/string | `SOC2020`. |
| `classification_version` | string | Edition/asset version used. |
| `hierarchy_level` | enum | Major, sub-major, minor, or unit group as supported by source. |
| `parent_code` | nullable string | Official parent code where defined. |
| `official_title` | string | Source description. |
| `source_id` | string | Sprint 1 catalog ID. |
| `source_asset_version` | string | Exact file/release reference. |
| `mapping_status` | enum | Exact official code, reviewed candidate, ambiguous, or unmapped. |

No invented crosswalk, title, or occupation-to-market equivalence.

### `UKSalaryAggregate`

| Field | Type | Meaning |
|---|---|---|
| `observation_id` | string | Stable key derived from edition and source dimensions, not source row content. |
| `market_id` | literal | `UK`. |
| `occupation_code` | string | Source SOC 2020 code. |
| `classification_id` / `classification_version` | string | Source classification and edition. |
| `geography_code` | nullable string | Official region code when the chosen source provides it. |
| `geography_level` | enum/string | UK, nation/region, or source-defined level. |
| `geography_label` | string | Source label. |
| `reference_period` | string/date | Source pay/reference period; not inferred from download date. |
| `measure_code` | string | Source’s measure identifier. |
| `earnings_definition` | string | Exact source definition, e.g. gross annual; do not collapse distinct definitions. |
| `statistic` | enum/string | Median, mean, percentile, hours, or other explicitly published statistic. |
| `employee_group` | string | Source definition for full-/part-time/sex grouping; preserve explicit “all” where source provides it. |
| `salary_value` | nullable decimal | Original reported amount. Null only with a non-value `value_status`; must be finite and > 0 if a salary amount is present. |
| `currency` | literal | `GBP` for UK reported salary. |
| `salary_period` | enum | As reported by source: hourly/weekly/annual/etc. |
| `value_status` | enum | Reported, suppressed, not reported, not applicable, unavailable, invalid. |
| `quality_marker` | nullable string/decimal | Source CV, suppression/quality marker or official flag; semantics documented. |
| `source_id` | string | Sprint 1 source catalog key. |
| `source_asset_version` | string | Exact ONS release/file ID and checksum reference. |
| `retrieved_at` | timezone-aware datetime | Ingestion retrieval timestamp, separate from reference period. |
| `transformation_version` | string | Deterministic parser/normalizer version. |

Constraints: duplicates are defined by the full source dimension key; reported median and mean remain distinct rows/fields by contract; invalid numerical values reject with stable issue codes; no rate/FX conversion is implied.

### `IngestionRun` / source asset manifest

| Field | Type | Meaning |
|---|---|---|
| `run_id` | string | Stable run identity. |
| `source_id`, `source_url` | string/URL | Catalog source and public reference. |
| `retrieved_at` | timezone-aware datetime | Acquisition time. |
| `source_reference_period` | string | Period covered by exact asset. |
| `dataset_version` | string | Publisher release/edition. |
| `file_format`, `original_filename` | string | Source file metadata; filename is not exposed via API. |
| `sha256` | 64-char hex | Exact input checksum. |
| `selected_variables` | string list | Source columns selected and mapping version. |
| `geographic_coverage` | string list | Validated coverage labels/codes. |
| `occupation_classification` / `version` | string | Classification applied. |
| `rows_seen`, `rows_accepted`, `rows_rejected` | nonnegative integers | Validation accounting; sum invariant. |
| `validation_summary` | issue-code counts | Redacted stable issue codes only. |
| `transformation_version` | string | Parser/transform version. |
| `status` | enum | Pending, validated, rejected, or failed. |

Raw filesystem paths and rejected row contents are never part of public schemas.

### Optional `UKDemandAggregate` (deferred)

Only if the exact ONS aggregate asset passes terms review: source-defined period, local-authority code, SOC 2020 code, measure (`new adverts` vs `live advert snapshot`), count, quality marker, ONS edition and source provenance. This is an online-advert measure only; it must not be named hires, total vacancies, employer recruitment or employment growth.

## Existing contracts to reuse

Reuse Sprint 1 `DataSource`, `DataProvenance`, `SalaryObservation`, `DataQualityIssue`, and `DataQualityResult` where the shape accurately represents source aggregate measures. Add a distinct aggregate contract if `SalaryObservation` would misleadingly imply a row-level salary observation. Avoid a second provenance or issue-code system.
