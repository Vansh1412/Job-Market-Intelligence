# Sprint 2 Proposed API Contracts

**Status:** Proposal; no UK analytical endpoint is implemented. Routes below require exact source/schema approval and a working data pipeline before they can be exposed.

## Existing versioned API (Sprint 1; already implemented)

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/v1/markets` | Market metadata list |
| GET | `/api/v1/markets/{market_id}` | One market; unknown market returns 404 |
| GET | `/api/v1/sources` | Source catalog |
| GET | `/api/v1/sources/{source_id}` | One source; unknown source returns 404 |
| GET | `/api/v1/employers` | Employer list (currently empty) |
| GET | `/api/v1/employers/{company_id}` | Employer detail; unknown ID returns 404 |

These are metadata-only routes. Their presence does not mean UK data analytics or employer records exist.

## Candidate additive UK endpoints

Only the first read-only salary/occupation vertical slice should be considered after source approval:

| Method | Candidate route | Purpose and gate |
|---|---|---|
| GET | `/api/v1/markets/UK/salary/summary` | Summary for one exact reported salary measure and reference period. Do not return a KPI until derived from the validated artifact. |
| GET | `/api/v1/markets/UK/occupations` | SOC 2020 hierarchy/search list; require version filter and bounded pagination. |
| GET | `/api/v1/markets/UK/occupations/{occupation_code}` | Exact SOC code detail and any supported salary aggregate; unknown code 404. |
| GET | `/api/v1/markets/UK/regions` | Only if the chosen ASHE asset has validated region-level estimates and region IDs. |
| GET | `/api/v1/markets/UK/data-quality` | Redacted quality/coverage summary for the served artifact, never rejected source contents or local paths. |

Do not implement demand endpoints in the first vertical slice. Reconsider only after Textkernel-derived dataset reuse is reviewed and an exact source edition has been approved.

## Proposed response shape

Response models should be typed Pydantic v2 models. A successful aggregate response includes:

```json
{
  "market_id": "UK",
  "data_status": "AVAILABLE",
  "source_id": "uk.ons.ashe.table15",
  "dataset_version": "<verified ONS edition>",
  "reference_period": "<source-defined period>",
  "occupation_classification": "SOC2020",
  "measure": {
    "code": "<source measure code>",
    "definition": "<source wording retained>",
    "statistic": "median",
    "salary_period": "ANNUAL",
    "currency": "GBP"
  },
  "coverage": {
    "geography_level": "<source-supported level>",
    "occupation_count": 0
  },
  "results": [],
  "limitations": ["Aggregate employee survey estimates; not individual salaries."]
}
```

The example uses placeholders and `0` only to show structure, not real source data. Production must not return fabricated sample values. Omit dimensions unsupported by the selected table; avoid an unconditional `occupation_count` if it cannot be calculated from actual validated rows.

## Semantics and HTTP behavior

- `GET` only; no ingestion, refresh, delete, prediction, or mutation route.
- An unknown exact occupation/source/market identifier returns 404.
- A known but unavailable dataset should use a documented, consistent empty/unavailable representation and must not masquerade as an observed zero. Final status code for unavailable data must be settled before implementation; recommendation: `200` with `data_status: NOT_IMPLEMENTED|UNAVAILABLE` and empty results only when the route exists but data is unavailable, versus 404 only for an unknown resource.
- Invalid query filters return 422 through typed validation; bounded pagination (`limit` + opaque/offset `cursor`) only where needed.
- Every result carries source edition/reference period/measure/currency or inherits them from an explicit response-level metadata object.
- No API response contains local paths, raw source rows, credentials, or rejected contents.
- OpenAPI schema and real HTTP behavior must be tested; no direct-handler-only verification.

## Compatibility

Keep existing India/USA endpoints unchanged. `/api/v1` remains additive. Do not add frontend client calls until response contracts are implemented and backed by approved, validated data.
