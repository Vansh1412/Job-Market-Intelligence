# Sprint 1 Data Dictionary

All names below are serialized as JSON field names. Pydantic models are frozen after creation. Optional fields may be absent or `null` unless noted. No schema exposes local paths or source row contents.

## Enumerations

| Type | Values |
|---|---|
| `MarketId` | `IN`, `US`, `UK`, `AU`, `SG` |
| `CurrencyCode` | `INR`, `USD`, `GBP`, `AUD`, `SGD` |
| `CapabilityStatus` | `AVAILABLE`, `PARTIAL`, `NOT_IMPLEMENTED`, `UNAVAILABLE` |
| `MarketCapability` | `salary_prediction`, `salary_analytics`, `skills_analytics`, `demand_analytics`, `occupation_mapping`, `employer_intelligence` |
| `SourceCategory` | `OFFICIAL_STATISTICS`, `COMPANY_DISCLOSURE`, `COMPANY_CAREER_PAGE`, `PERMITTED_JOB_POSTING`, `EXISTING_PROJECT_DATA` |
| `ReuseReviewStatus` | `APPROVED`, `REVIEW_REQUIRED`, `RESTRICTED`, `UNKNOWN` |
| `ValidationStatus` | `NOT_COLLECTED`, `PENDING`, `VALIDATED`, `REJECTED` |
| `SalaryPeriod` | `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY`, `ANNUAL`, `OTHER` |
| `EmployerCategory` | `INDIAN_HEADQUARTERED`, `MULTINATIONAL_OPERATING_IN_INDIA`, `OTHER_INTERNATIONAL` |
| `EmployerVerificationStatus` | `UNVERIFIED`, `REVIEW_REQUIRED`, `VERIFIED` |
| `EmployerLocationType` | `HEADQUARTERS`, `OFFICE`, `RESEARCH`, `OTHER` |

## Market metadata

### `MarketConfig`

| Field | Type / constraints | Meaning |
|---|---|---|
| `market_id` | `MarketId` | Stable market identifier. |
| `display_name` | string, 2–80 chars | Human-readable market name. |
| `iso_country_code` | two uppercase letters | ISO country code; UK market uses `GB`. |
| `primary_currency` | `CurrencyCode` | Market’s native reporting currency. It does not trigger conversion. |
| `salary_reporting_convention` | string, 4–240 chars | Describes existing or intended salary meaning and period. |
| `occupational_classification` | string, 3–160 chars | Classification name or existing project role-family convention. |
| `occupational_classification_version` | optional string, max 80 chars | Version where specified. |
| `capabilities` | complete map of `MarketCapability` to `CapabilityStatus` | Explicit state for each product capability. |
| `data_availability` | `CapabilityStatus` | Market source-data availability state. |
| `source_ids` | tuple of unique source ID strings | References in the source catalog. |
| `last_successful_update` | optional timezone-aware datetime | Null until a successful update is observed. |

## Data catalog and provenance

### `DataSource`

| Field | Type / constraints | Meaning |
|---|---|---|
| `source_id` | 2–96 chars; lowercase alphanumeric plus `.`, `_`, `-` | Stable catalog key. |
| `source_name` | string, 2–160 chars | Public or project source name. |
| `source_organization` | string, 2–160 chars | Publishing or owning organization. |
| `source_reference` | optional HTTP(S) URL | Public source reference, not a local file location. |
| `source_category` | `SourceCategory` | Type of source. |
| `reuse_review_status` | `ReuseReviewStatus` | Reuse review state; official external sources remain `REVIEW_REQUIRED`. |
| `dataset_description` | string, 4–600 chars | Short description of coverage and limitations. |
| `geographic_coverage` | tuple of strings | Geographic scope. |
| `update_frequency` | optional string, max 100 chars | Known release cadence. |
| `reference_period` | optional `YYYY`, `YYYY-MM`, or `YYYY-Qn` | Period described by source metadata. |
| `collected_at` | optional timezone-aware datetime | Null while the source has not been collected. |
| `validation_status` | `ValidationStatus` | Collection/validation lifecycle. |

### `DataProvenance`

| Field | Type / constraints | Meaning |
|---|---|---|
| `source_id` | source ID string | Catalog source for the data. |
| `collected_at` | timezone-aware datetime | Collection time. |
| `reference_period` | `YYYY`, `YYYY-MM`, or `YYYY-Qn` | Period represented by the data. |
| `geographic_coverage` | tuple of strings | Coverage represented by this dataset. |
| `dataset_description` | string, 4–600 chars | Description of the specific dataset. |
| `validation_status` | `ValidationStatus` | State of validation. |

### `DataQualityIssue`, `RejectedRow`, and `DataQualityResult`

`DataQualityIssue` has `row_index` (zero-based integer), `code` (2–80 chars), optional `field` (max 120 chars), and a generic `message` (2–200 chars). Issue messages do not contain input values.

`RejectedRow` has a zero-based `row_index` and one or more `reason_codes`.

`DataQualityResult` has nonnegative `rows_seen`, `rows_accepted`, and `rows_rejected`; an `issues` tuple; and a `rejected_rows` tuple. It enforces `rows_seen = rows_accepted + rows_rejected` and exactly one rejected-row summary per rejected record.

## Salary observations

### `SalaryObservation`

| Field | Type / constraints | Meaning |
|---|---|---|
| `observation_id` | 2–120 chars; alphanumeric first, then alphanumeric/`.`/`_`/`:`/`-` | Record identifier. |
| `market_id` | `MarketId` | Market represented. |
| `occupation_id` | string, 1–120 chars | Source or canonical occupation identifier. |
| `occupational_classification` | string, 2–160 chars | Classification system. |
| `occupational_classification_version` | string, 1–80 chars | Classification version or project schema version. |
| `geographic_region` | optional string, max 160 chars | Region as defined by the source. |
| `salary_value` | finite positive `Decimal`, up to 20 digits and 4 decimal places | Amount in the source currency and stated period. NaN, positive/negative infinity, zero, and negative values are rejected. |
| `currency` | `CurrencyCode` | Native salary currency; no FX conversion is performed. |
| `salary_period` | `SalaryPeriod` | Source time basis; no annualization is performed. |
| `compensation_definition` | string, 3–300 chars | Source wording/definition such as basic, gross, or total. |
| `reference_period` | `YYYY`, `YYYY-MM`, or `YYYY-Qn` | Time period represented. |
| `source_id` | source ID string | Provenance catalog key. |
| `collected_at` | timezone-aware datetime | Collection time. |

## Employer records

### `EmployerSourceReference`

`source_name` and `source_organization` are required strings of 2–160 chars; `source_reference` is a required HTTP(S) URL; `collected_at` is an optional timezone-aware datetime.

### `EmployerLocation`

| Field | Type / constraints | Meaning |
|---|---|---|
| `city` | string, 1–120 chars | City from an evidence-backed location record. |
| `state_or_region` | optional string, max 120 chars | State, province, or region. |
| `country_code` | two uppercase letters | Country of the location. |
| `location_type` | `EmployerLocationType` | Headquarters, office, research site, or other. |
| `verification_status` | `EmployerVerificationStatus` | Defaults to `REVIEW_REQUIRED`. |
| `verification_source` | required `EmployerSourceReference` | Evidence reference for the location. |
| `verified_at` | optional timezone-aware datetime | Verification time. |

Every location requires a source reference; `VERIFIED` locations also require a verification timestamp.

### `EmployerProfile`

| Field | Type / constraints | Meaning |
|---|---|---|
| `company_id` | 2–120 chars; lowercase alphanumeric first, then alphanumeric/`.`/`_`/`-` | Stable company key. |
| `company_name` | string, 2–180 chars | Company name supported by references. |
| `headquarters_country` | two uppercase letters | Headquarters country. |
| `company_category` | `EmployerCategory` | Distinguishes Indian HQ, multinational operating in India, and other international. |
| `industry` | optional string, max 160 chars | Industry label. |
| `official_website` | optional HTTP(S) URL | Company website. |
| `operating_markets` | unique tuple of `MarketId` | Supported operating markets. |
| `source_references` | tuple with at least one `EmployerSourceReference` | Evidence references for the record. |
| `verification_status` | `EmployerVerificationStatus` | Defaults to `REVIEW_REQUIRED`. |
| `verified_at` | optional timezone-aware datetime | Verification time. |
| `locations` | tuple of `EmployerLocation` | Evidence-backed office locations; empty by default. |

Indian-headquartered employers must have HQ country `IN`. A multinational operating in India must have a non-`IN` HQ and include `IN` among operating markets. `VERIFIED` profiles require `verified_at`. The Sprint 1 production registry contains no profiles.
