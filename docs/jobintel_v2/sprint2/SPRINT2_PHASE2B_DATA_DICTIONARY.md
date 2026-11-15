# Sprint 2 Phase 2B — UK ASHE API Data Dictionary

**Status:** API contract documentation for the gated, read-only Phase 2B implementation. The current source is not publicly approved or published, so live endpoints fail closed and do not return observations.

## Source and measure

| Field | Definition |
|---|---|
| Source ID | `uk.ons.ashe` |
| Edition | ONS ASHE Table 15, 2025 revised |
| Reference period | Tax year ending 5 April 2025 |
| Geography | 11 Great Britain work regions in the source; no Northern Ireland or UK total |
| Occupation classification | SOC 2020 unit groups; four-character unit-group code |
| Measure | Full-time annual gross pay median, Table 15.7a, paired with the ONS Table 15.7b CV |
| Population | Adult-rate full-time employee jobs held for over one year, under the ONS ASHE definition |
| Currency and period | GBP, annual; values are source values and are not annualized or converted by this API |
| Attribution | Source: Office for National Statistics, Annual Survey of Hours and Earnings, ASHE Table 15, 2025 revised; Open Government Licence v3.0. |
| Source registry status | `REVIEW_REQUIRED`; catalog validation `NOT_COLLECTED` |
| Current manifest status | `publication_eligible: false`; local preparation only |
| Dataset/manifest source reference | `https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15` |
| Current catalog reference | `https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsocashetable15` (does not resolve during this audit and does not exactly match the dataset reference) |

## Response fields

| Field | Meaning |
|---|---|
| `context.market_id` | Constant `UK`. |
| `context.source_id` | Constant `uk.ons.ashe`. |
| `context.reference_period` | The source period above. |
| `context.measure` | The specific published median measure above. |
| `context.population_definition` | Population statement carried with each response. |
| `context.occupation_classification` | Constant `SOC 2020 unit group`. |
| `context.geography_coverage` | The ordered 11 source work-region labels. |
| `context.transformation_version` | `ashe-table15-2025r-v1.0.2`. |
| `context.data_quality_status` | `VALIDATED` after full local artifact validation. |
| `context.publication_status` | `NOT_PUBLISHED` for local-only data or while the live catalog is not approved, validated, and reference-aligned. `PUBLISHED` is possible only after artifact approval metadata and the live publication gate both pass. |
| `context.source_attribution` | Source attribution string above. |
| `soc_code` | Four digit SOC 2020 unit-group identifier. It is not mapped from SOC 2010. |
| `official_title` | Official SOC unit-group title. |
| `source_description` | Occupation description preserved from the ONS workbook. |
| `region_label` | ONS Great Britain work-region label. |
| `annual_gross_median_gbp` | Original numeric ONS median as a decimal. Unavailable when source status is not `REPORTED`; JSON uses a decimal string to preserve precision. |
| `original_ons_median_cell` | Original source cell text, including `x` or empty text where applicable. |
| `cv_percent` | Original paired ONS CV value, without recalculation. |
| `original_ons_cv_cell` | Original CV source cell text. |
| `cv_quality_band` | Source-derived CV quality category preserved with the observation. |
| `value_status` | Source-aware status enum: `REPORTED`, `SUPPRESSED_QUALITY`, `SUPPRESSED_DISCLOSURE`, `NOT_APPLICABLE`, `NIL_OR_NEGLIGIBLE`, or `BLANK_UNKNOWN`. |
| `reported_count`, `suppressed_count`, `blank_count` | Coverage counts over the stated denominator. Suppressed and blank states remain distinct; no missing status is treated as zero. |
| `source_archive_sha256`, `processed_dataset_sha256` | Uppercase SHA-256 checksums for the verified archive and prepared CSV. |
| `ingested_at` | UTC timestamp from the local preparation manifest; it is not the source reference period. |

## Operations intentionally absent

The API does not calculate averages, rankings, employee-level distributions, percentiles, or major-group aggregates. It does not impute suppressed/blank observations, calculate a salary value from a CV, transform currency, or infer missing values. Region comparison returns source observations and explicit reportable coverage only.

## Release gate

Every endpoint first requires `uk.ons.ashe` to have reuse status `APPROVED`, validation status `VALIDATED`, and a matching manifest whose `publication_eligible` value is exactly `true`. The repository currently meets none of these publication conditions. Until the source terms and intended public uses are documented and reviewed, the endpoints return a generic HTTP 503 `UK_DATA_NOT_PUBLISHED` response before loading the dataset. No salary values are returned.

Local artifact validation is separate from source reuse approval, catalog validation, publication eligibility, and runtime API availability. The current local manifest remains `LOCAL_PREPARATION_ONLY`, non-publishable, and unchanged. A future `PUBLICATION_APPROVED` manifest must be separately reviewed and include approval metadata bound to the source and processed dataset checksum; successful local integrity validation alone never makes local data public.

## Source identity validation

The dataset CSV rows and manifest must agree exactly on source ID, dataset source reference, catalog source reference, and the boolean `source_reference_matches_catalog`. The current local artifact accurately records the canonical ONS Table 15 data URL separately from the current catalog URL and sets the match flag to `false`; service integrity may accept this local-only condition, but the publication lifecycle rejects it. A publishable artifact requires the dataset, manifest, nested data provenance, approval record, and live catalog entry to carry the same exact source reference, `source_reference_matches_catalog: true`, and the approved processed dataset checksum. The live source geography and reference period must also match Great Britain and 2025. URLs are compared as exact strings; no alias inference or silent catalog rewrite occurs.

The official [ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) lists the 2025 revised download and links to OGL v3.0. Public availability and the general licence link do not change the current source review decision or authorize this public dashboard use.
