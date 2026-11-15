# Sprint 1 API Contracts

New endpoints are additive and versioned under `/api/v1`. They use typed Pydantic v2 response models, expose no local file paths, and require no authentication today (same public API convention as current routes). Invalid path identifiers return 404. Existing `/api` and root routes retain current behavior.

| Method/path | Response | Empty/missing behavior |
|---|---|---|
| GET `/api/v1/markets` | `list[MarketConfig]` with five markets, native currency/convention, occupation scheme, capabilities, source IDs, data status, nullable last update | Always returns all configured market records. |
| GET `/api/v1/markets/{market_id}` | `MarketConfig` | 404 for unknown ID; IDs are `IN`, `US`, `UK`, `AU`, `SG`. |
| GET `/api/v1/sources` | `list[DataSource]` | Returns source metadata only; uncollected sources retain null timestamps. |
| GET `/api/v1/sources/{source_id}` | `DataSource` | 404 for unknown ID. |
| GET `/api/v1/employers` | `list[EmployerProfile]` | Initially `[]`; no unverified examples are seeded. |
| GET `/api/v1/employers/{company_id}` | `EmployerProfile` | 404 until a source-verified company is registered. |

## Data contracts

`MarketConfig`: market enum, ISO code, name, currency, salary convention, occupation system/version, capability map, data availability, source IDs, nullable update timestamp.

`DataSource`: source ID/name/organization/HTTP reference/category, reuse review state, description, geography, update cadence and reference period where known, nullable collection timestamp, validation state. No file paths, credentials, or dataset rows.

`DataProvenance`: source ID, collection timestamp, reference period, geographic coverage, dataset description, and validation state.

`SalaryObservation`: observation ID, market, occupation ID and classification/version, optional region, positive Decimal amount in source currency and period, unmodified compensation definition, reference period, source ID and collection timestamp. No FX, annualization, or interpretation of basic/gross/total compensation.

`DataQualityResult`: rows seen/accepted/rejected and structured row-index/code/field issues. It does not include rejected source contents.

`EmployerProfile` and `EmployerLocation`: typed company identity, HQ/operating distinction, optional industry/category/website, evidence references, verification status, city/region/country, location type, verification source/date. No seeded company/location records.

The endpoint schemas do not return salary observations or employer data in Sprint 1; those models establish future ingestion contracts.
