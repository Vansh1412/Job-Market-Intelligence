# Sprint 2 Proposed Ingestion Design

**Status:** Design only, pending source and implementation approval. No downloads or ETL have occurred.

## Proposed workflow

1. Operator explicitly supplies a source ID and exact approved local input asset to an offline command. Ordinary unit tests use small checked-in synthetic fixtures only; no network access is required.
2. Verify that source status, exact edition and intended use are approved for the specified display/derived use. If status is `REVIEW_REQUIRED`, `UNKNOWN`, or `RESTRICTED`, fail closed before parsing/publishing.
3. Identify format and filename; calculate SHA-256; create a run manifest. A different checksum creates a new immutable run/version rather than replacing the raw input.
4. Parse only documented sheets/columns. Record original-to-canonical column mapping and parser/transform version. Reject unexpected headers or ambiguous units.
5. Validate schema, types, duplicates, missingness, salary measure/currency/period/value, SOC code, geography, reference period, suppression markers, and source consistency.
6. Write accepted transformed aggregate data into a temporary output, verify its checksum/schema and data invariants, then atomically publish to the versioned processed location.
7. Produce a redacted quality summary with totals, issue-code counts and coverage. Do not put rejected values, source text or private file paths in logs, reports, or HTTP output.
8. The API reads only the current explicitly validated processed version. Ingestion never runs at FastAPI startup or in the request path.

## Proposed layout (after approval)

```text
data/
  raw/          # exact source downloads; ignored, never overwritten
  processed/    # validated derived aggregates; ignored
  reports/      # redacted run summaries; ignored
src/backend/ingestion/
  contracts.py
  manifest.py
  runner.py
  uk/            # source adapter only if justified
```

The repository already ignores `data/raw/`, `data/processed/`, and `*.parquet`. Confirm `data/reports/` is ignored before writing there; do not change `.gitignore` unless necessary and separately inspect the whole diff. No raw or processed dataset should be committed.

## Audit and deterministic rules

- One source asset checksum per run; no silent overwrite.
- Stable issue codes and generic messages, with rejected source values excluded.
- No imputation of suppressed/missing salary values.
- No FX conversion, annualization, or combining hourly/weekly/annual statistics.
- Store native GBP and salary period; preserve gross/basic and median/mean distinctions.
- Do not auto-accept title-to-SOC matches when multiple candidate codes exist.
- Same input checksum + same parser/transform version + same config must produce byte-stable or semantically identical output (define normalization/order before acceptance).
- Row counts and accepted + rejected invariant recorded; duplicate IDs blocked.
- Source and transformation provenance travels with every published aggregate/API result.

## Runtime/resource and dependency constraints

No external download in CI, no startup ETL, scheduler, paid service or database. The source is XLSX and no XLSX reader was declared, so Phase 2A added only `openpyxl>=3.1.0,<4.0.0`, justified as the parser required to read the ONS source and create offline workbook fixtures. No other dependency or infrastructure was added. Profile peak memory and processed size on an approved file before deciding to bundle a derived read-only artifact for Render; do not assume a free-tier memory fit.

## Phase 2A implementation status

The local-only pipeline is implemented in `src/backend/ingestion/` with typed contracts, an ASHE 2025 adapter, deterministic runner and CLI. It writes only to ignored `data/processed/`, verifies the pinned archive and SOC reference, preserves all 4,532 source-cell states, writes a machine-readable manifest and redacted quality report, and fails closed on validation errors. It does not run at application startup or in an API request. The source remains `REVIEW_REQUIRED`; public release is not enabled. See `SPRINT2_INGESTION_IMPLEMENTATION.md`, `SPRINT2_ASHE_PROCESSED_DATA_DICTIONARY.md`, and `SPRINT2_ASHE_PIPELINE_TEST_REPORT.md` for implementation details and actual test results.

## Proposed tests after approval

Unit fixtures: expected and unexpected columns; malformed types; invalid/infinite/zero/negative salary; multiple definitions; suppressed/missing markers; duplicate dimension keys; valid and unknown SOC codes; invalid geography/reference periods; clean checksum/changed checksum; deterministic repeat run; rejected-content non-disclosure; manifest provenance invariants. API tests should consume a validated fixture artifact or injected service fixture, not trigger downloads. Full HTTP tests must use the actual FastAPI app and a real local HTTP client/server as appropriate for Windows asyncio constraints.
