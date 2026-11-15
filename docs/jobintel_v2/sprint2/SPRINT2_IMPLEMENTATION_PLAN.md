# Sprint 2 Implementation Plan (Approval Required)

**State:** Awaiting explicit user approval. This plan authorizes no code modification, dataset download, employer population, dependency change, frontend integration, deployment, or publication.

## Recommended bounded scope

One real, read-only UK descriptive salary and SOC 2020 vertical slice, conditional on source approval. Choose one exact ONS ASHE table/edition and one reported salary measure only after file-level definitions and license notices are reviewed. Keep demand aggregates deferred pending Textkernel-derived source review. Keep employer registry empty; document source and entity rules only. Do not add UK prediction/ML in Sprint 2.

## Sequence and phase gates

| Phase | Work after approval | Evidence required to proceed |
|---|---|---|
| 0. Close source gate | Verify exact current ASHE edition, workbook/table and measure; inspect file-level licensing/attribution; decide selected public derived use. Verify SOC 2020 selected machine-readable asset. | Source approval record with URL, filename/version, checksum, terms/attribution and intended use. Otherwise mark blocked; no download/use. |
| 1. Contract refinement | Validate selected source columns against proposed `SPRINT2_DATA_DICTIONARY.md`; define issue codes, missingness, geographic and SOC code validation; finalize response models. | Reviewable source-to-contract mapping and no unsupported fields. |
| 2. Offline ingestion | Implement small isolated ingestion contracts/command; immutable raw input manifest, checksum, deterministic parse/normalize, redacted quality report; reuse Sprint 1 validation/provenance. | Fixture tests and verified no startup/request-time ingestion. No extra dependencies unless separately approved. |
| 3. Quality and processed artifact | Run approved real file once, investigate exceptions/outliers/suppression; publish versioned processed data only if acceptance passes. | Actual counts, coverage, checksum, rejection reasons, data quality review and source attribution. |
| 4. UK domain/analytics | Implement exact SOC registry and supported aggregate calculations, source and limitation metadata; no ambiguous implicit mapping. | Calculation definitions and tests tied to source measures. |
| 5. Additive API | Add bounded GET-only endpoints under `/api/v1`; response schemas, explicit empty/unavailable/404 behavior. | Real HTTP integration and OpenAPI checks against actual FastAPI app. |
| 6. Frontend (separate sub-gate) | Add a focused UK experience to existing React architecture only after backend API passes. Reuse existing UI; do not alter India/USA flows. | User-facing feature approval; real data provenance, loading/error/empty states and UI tests. |
| 7. Employer foundation | Keep empty unless exact source/fields approved; add verification only for evidence-backed data. No scraping without permission. | Employer source and personal-data review; source citations for each populated fact. |
| 8. Regression/final docs | Backend CI subset, full relevant backend tests, HTTP checks, India/USA golden parity, artifact hashes, frontend checks if changed, complete diff/file inventory. | Actual completed output; failures/blocked tests disclosed. |

## Non-negotiable safeguards

- Do not alter India/USA services, schemas, APIs, model artifacts, feature contracts or prediction behavior.
- No dependency, deployment, CI or infrastructure changes without separate approval.
- Do not read or expose private local datasets; do not commit source data, credentials or generated artifacts.
- Keep source reuse `REVIEW_REQUIRED` until evidence is recorded.
- Reject non-finite, zero and negative salary values; stable issue codes; never echo rejected data.
- Keep API read-only and metadata/provenance rich; no unsupported source stats.
- No commits, pushes or deployment without approval.

## Approval checklist

Please explicitly approve or revise each item before implementation:

1. Selected first source: one exact ASHE publication/table/edition, after the source gate; no dataset is pre-approved by this plan.
2. Initial measure scope: one source-reported full-time median gross annual salary statistic if available and non-suppressed; preserve official definition and do not annualize/convert.
3. SOC 2020 structure: use official codes and descriptions, retain version; title search returns candidates and does not silently choose ambiguous matches.
4. Deferred scope: ONS/Textkernel labour-demand data, employer scraping, employer records, UK prediction, Australia/Singapore, and frontend work until the backend vertical slice has its own review gate.
5. Proposed offline ingestion, local ignored data layout, additive read-only API design, and no new dependencies/infrastructure.
6. Permission to begin code changes only after the exact source/license gate is resolved. If that gate cannot be resolved, implementation remains blocked rather than substituting unapproved data.
