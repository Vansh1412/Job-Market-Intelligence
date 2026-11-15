# Sprint 2 Phase 2B — UK Salary API Contracts

**Contract state:** designed before implementation; read-only; release gate closed.
**Base path:** `/api/v1/markets/UK/salary` (uppercase `UK` follows `MarketId`).

## Publication behavior (applies to all routes)

Every route checks catalog approval, catalog validation, exact dataset/manifest/catalog source identity, and a complete publication approval record before accessing the processed CSV. It hashes the approved file against the manifest and approval checksum on each request. Current state is `REVIEW_REQUIRED`, `NOT_COLLECTED`, and `publication_eligible=false`; each endpoint therefore returns HTTP **503** and no salary or observation metadata.

```json
{
  "detail": {
    "code": "UK_DATA_NOT_PUBLISHED",
    "message": "UK salary analytics are not currently published."
  }
}
```

The successful 200 schemas/examples below specify the contract for a future source-approved and publishable artifact. They are not available in the current runtime state. There is no environment switch, query/header override, or administrative bypass.

## Separate validation and release states

| Control | What it proves | Current state | Effect on API |
|---|---|---|---|
| Local artifact validation | Manifest/data identity, checksums, schema, row counts, source-cell statuses, and provenance are internally consistent. The local artifact may be validated for internal use while still not cleared for public use. | Phase 2A artifact is validated in local preparation mode. | Does not authorize any endpoint. |
| Source reuse approval | The source's terms have been reviewed for the proposed activity, recorded as `APPROVED` in the source registry and future release manifest. | `REVIEW_REQUIRED`. | Must be approved before the gate can open. |
| Catalog validation | The source entry and intended release metadata have been reviewed and marked `VALIDATED` in the live registry and future manifest. This is distinct from validating CSV rows. | `NOT_COLLECTED`. | Must be validated before the gate can open. |
| Publication eligibility | A separate release decision recorded in a `PUBLICATION_APPROVED` manifest with `publication_eligible: true` and complete approval metadata bound to source ID and processed checksum. | `false`; current manifest is `LOCAL_PREPARATION_ONLY`. | Must be true before the service may load. |
| Public API availability | Runtime policy checks live catalog reuse and validation states plus manifest approval; then the service verifies the actual processed artifact and checksum. | Unavailable. | All five endpoints return 503 without loading the service. |

The current local manifest is preserved unchanged. A future publishable artifact must be separate and include `publication_approval` fields for approval ID, reviewer, timestamp, source ID, approved reuse and catalog states, approved public display use, and the processed dataset SHA-256. Service integrity validation accepts the coherent future lifecycle but does not itself authorize publication. `UKSalaryContext.publication_status` is `NOT_PUBLISHED` unless both that manifest and the live catalog satisfy the gate.

Source identity is exact string equality; no URL normalization or alias inference is used. In `LOCAL_PREPARATION_ONLY`, the current dataset and manifest consistently record the canonical ASHE data reference, the separate current catalog URL, and `source_reference_matches_catalog: false`. This accurate local provenance is permitted for internal integrity validation only. `PUBLICATION_APPROVED` requires data, manifest, nested provenance, approval record, and live catalog to carry the same source ID and exact canonical source reference, a true match flag, and matching SOC 2020 / GB geography / 2025 reference period. The live catalog's current source URL, UK-wide geography and 2026 period do not satisfy those conditions.

The [official ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) currently lists both the 2025 revised edition and a newer 2026 provisional edition and links to OGL v3.0. The repository source catalog URL differs and did not resolve during this audit. ONS's general licence link is not an approval decision for this JobIntel use. Source reuse remains `REVIEW_REQUIRED`, catalog validation remains `NOT_COLLECTED`, and all UK capabilities remain `NOT_IMPLEMENTED`.

## Endpoints

| Method and path | Query/path inputs | 200 response | Current state |
|---|---|---|---|
| `GET /api/v1/markets/UK/salary/occupations` | Optional `q` (1–100 chars; literal case-insensitive substring match over SOC code, official title, ASHE source description); `page` (1–10,000, default 1); `page_size` (1–100, default 25) | `UKOccupationPage`; all 412 occupations, including zero-reported-cell occupations, with explicit coverage counts; deterministic SOC-code ordering | 503, no rows |
| `GET /api/v1/markets/UK/salary/occupations/{soc_code}` | Four digit SOC 2020 unit-group code | `UKOccupationDetail`; code/title/source description and all 11 region states | 503; after approval, unknown valid code is 404 |
| `GET /api/v1/markets/UK/salary/occupations/{soc_code}/regions` | Four digit SOC 2020 unit-group code | `UKRegionComparison`; 11 region states for the same occupation and source measure; numeric comparison contains reported medians only and status counts retain unavailable states | 503; after approval, unknown valid code is 404 |
| `GET /api/v1/markets/UK/salary/regions/{region}/occupations` | Exact source region label in URL-encoded path; `value_status` from supported status enum (default `REPORTED`); bounded `page`, `page_size` | `UKRegionOccupationPage`; page results and coverage counts over all 412 occupation-region cells | 503; after approval, unknown region is 404 |
| `GET /api/v1/markets/UK/salary/metadata` | None | `UKSalaryMetadata`; source, measure, population, SOC, geography, reference period, transformation, quality and coverage metadata | 503; metadata is withheld until policy permits |

### Input and ordering rules

- `soc_code` must match `^[0-9]{4}$`; malformed code is 422. Unknown well-formed code is 404 only after the publication gate opens. With the current gate closed, valid-looking requests return the same 503 response without data lookup.
- `region` is one exact ASHE label: `East`, `East Midlands`, `London`, `North East`, `North West`, `Scotland`, `South East`, `South West`, `Wales`, `West Midlands`, `Yorkshire and The Humber`. URL-encode spaces. There is no source region code, so the API does not invent one.
- `q` is literal substring search, normalized using Unicode case-folding after trimming. No edit distance, title mapping or cross-classification matching occurs. Search length outside bounds is 422.
- Pages are 1-based and capped at 10,000; page size is 1–100. A page beyond the end returns 200 with `items: []` and the same `total_count`, not an unbounded query.
- Ordering is stable lexicographic SOC code (all codes are fixed four-digit strings); region order follows the 11 source geography labels in the ASHE contract.
- Regional occupation listings default to `value_status=REPORTED`. Callers may request a supported status explicitly; rows with no numeric median never contain a salary amount. Coverage metadata always reports the full 412-cell regional denominator and status totals.

## Shared response context

Each successful response embeds `context: UKSalaryContext`:

| Field | Type | Definition |
|---|---|---|
| `market_id` | literal `UK` | Product market ID; geographic coverage is narrower and stated separately. |
| `source_id` | literal `uk.ons.ashe` | Existing source catalog identifier. |
| `reference_period` | string | `Tax year ending 5 April 2025`. |
| `measure` | string | ONS Table 15.7a full-time annual gross pay median, paired with Table 15.7b median CV. |
| `population_definition` | string | Adult-rate full-time employee jobs held for over one year; annual gross earnings under the ASHE definition. This is not an employee-level extract. |
| `occupation_classification` | literal/string | `SOC 2020`, unit group. No SOC 2010 relabeling or other crosswalk. |
| `geography_coverage` | 11-label array | Great Britain work regions only; no Northern Ireland or UK-total estimate. |
| `transformation_version` | string | `ashe-table15-2025r-v1.0.2`. |
| `data_quality_status` | enum/string | Source-value validation status. It is separate from licensing and publication approval. |
| `publication_status` | literal | `PUBLISHED` only when the approved manifest and live catalog both satisfy the publication gate; otherwise `NOT_PUBLISHED`. |
| `source_attribution` | string | ONS / ASHE 2025 revised attribution and OGL reference. |

## Observation and status contracts

`UKRegionObservation` fields: `region_label`, `value_status`, optional `annual_gross_median_gbp`, `original_ons_median_cell`, optional `cv_percent`, optional `original_ons_cv_cell`, and `cv_quality_band`.

- `REPORTED`: finite positive GBP/year median and finite source CV in percent (≤20 for the selected column). `original_ons_median_cell` and CV preserve source numeric text.
- `SUPPRESSED_QUALITY`: no median amount; original cell marker `x`; CV state is retained.
- `SUPPRESSED_DISCLOSURE`, `NOT_APPLICABLE`, `NIL_OR_NEGLIGIBLE`, and `BLANK_UNKNOWN` retain distinct states. They have no salary amount. The current selected column contains only `REPORTED`, `SUPPRESSED_QUALITY`, and `BLANK_UNKNOWN`.

Every observation inherits the shared context, so its market, source, measure, reference period, population, classification, geography and transformation are unambiguous. Money and CV fields use Pydantic `Decimal` validation and serialize as JSON decimal strings to preserve source precision across clients; non-finite values are rejected before response serialization. Clients should parse these strings with a decimal type for exact arithmetic.

## Typed 200 response shapes

- `UKOccupationPage`: `context`, `items: UKOccupationSummary[]`, `page`, `page_size`, `total_count`, `has_next`, `coverage`.
- `UKOccupationSummary`: `soc_code`, `official_title`, `source_description`, `reported_region_count`, `suppressed_region_count`, `blank_region_count`, `expected_region_count`.
- `UKOccupationDetail`: `context`, `occupation`, `regions: UKRegionObservation[]`, `coverage`.
- `UKRegionComparison`: `context`, `soc_code`, `official_title`, `observations: UKRegionObservation[]`, `reported_regions_count`, `expected_regions_count`, `coverage_ratio`, `coverage_warning`.
- `UKRegionOccupationPage`: `context`, `region_label`, `items: UKRegionOccupationItem[]`, `page`, `page_size`, `total_count`, `has_next`, `coverage`.
- `UKRegionOccupationItem`: `soc_code`, `official_title`, `source_description`, `observation: UKRegionObservation`.
- `UKCoverage`: `reported_count`, `suppressed_count`, `blank_count`, `expected_count`, and reported coverage ratio. Counts always use the complete 11-region or 412-cell denominator as appropriate.
- `UKSalaryMetadata`: `context`, `edition`, `source_reference`, source checksum, observation count, status counts, occupation count and region count. It contains no filesystem path or workbook content.

### Representative successful response (contract illustration only)

This example shows how a future approved 200 response would encode an observation. It is not returned while publication is disabled.

```json
{
  "context": {
    "market_id": "UK",
    "source_id": "uk.ons.ashe",
    "reference_period": "Tax year ending 5 April 2025",
    "measure": "Full-time annual gross pay median (ONS Table 15.7a)",
    "population_definition": "Adult-rate full-time employee jobs held for over one year",
    "occupation_classification": "SOC 2020 unit group",
    "geography_coverage": ["East", "East Midlands", "London", "North East", "North West", "Scotland", "South East", "South West", "Wales", "West Midlands", "Yorkshire and The Humber"],
    "transformation_version": "ashe-table15-2025r-v1.0.2",
    "data_quality_status": "VALIDATED",
    "publication_status": "PUBLISHED",
    "source_attribution": "Source: Office for National Statistics, ASHE Table 15, 2025 revised; Open Government Licence v3.0."
  },
  "soc_code": "1150",
  "official_title": "Managers and directors in retail and wholesale",
  "observations": [
    {
      "region_label": "North East",
      "value_status": "REPORTED",
      "annual_gross_median_gbp": "31133.8",
      "original_ons_median_cell": "31133.8",
      "cv_percent": "13.8",
      "original_ons_cv_cell": "13.8",
      "cv_quality_band": "CV_GT_10_LE_20"
    }
  ],
  "reported_regions_count": 1,
  "expected_regions_count": 11,
  "coverage_ratio": 0.0909,
  "coverage_warning": "Only 1 of 11 regions has a reportable estimate; this is not a complete regional comparison."
}
```

## Errors

| HTTP | Response/detail code | Meaning |
|---:|---|---|
| 422 | FastAPI `detail` validation errors | Malformed SOC, unsupported region/status, or invalid query/pagination bounds. |
| 404 | `detail: "Occupation not found"` / `"Region not found"` | Unknown well-formed ID after publication gate passes. |
| 503 | `UK_DATA_NOT_PUBLISHED` | Current policy denies every UK salary endpoint. No observations are returned. |
| 503 | `UK_DATA_UNAVAILABLE` | Approved release path cannot load/validate its required local artifact or source metadata. Generic message only; no path or source row in response. |

The two 503 variants use the existing FastAPI `{"detail": ...}` convention. No 500 response includes an exception string, local path, or row values.

## Route and release review

The five route patterns are below `/api/v1/markets/UK/salary`; none conflicts with the six existing Sprint 1 `/api/v1` routes. All are GET-only. No route serves CSV/workbooks. UK salary analytics stays `NOT_IMPLEMENTED`/unavailable in the market registry while this gate is closed, and UK prediction remains `NOT_IMPLEMENTED`.
