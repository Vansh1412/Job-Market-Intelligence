# Sprint 2 Phase 2B — Completion Report

**State:** Implementation and repository verification finished for Phase 2B. This does not approve public release or authorize Phase 2C.

**Corrective acceptance readiness:** Ready for final human acceptance of the code patch. Public salary publication remains blocked by unresolved source-reference, geography/reference-period, and intended-use governance review.

## Delivered

Five additive read-only GET routes are implemented under `/api/v1/markets/UK/salary`: occupation search, occupation detail, regional comparison for an occupation, region occupation listing, and metadata. Typed immutable response contracts preserve SOC 2020 identifiers, the 2025 revised ASHE measure and period, original median/CV source cells, source status, geographic coverage, attribution, and provenance/checksums.

The local processed artifact validates against its pinned checksum and complete 4,532-cell grid. The router checks live catalog and manifest state and, only for an otherwise eligible publication, re-hashes the approved file on each request before obtaining the lazy service. Current source catalog status is `REVIEW_REQUIRED` / `NOT_COLLECTED`, its URL/geography/reference period do not match the dataset, and the manifest has `publication_eligible: false`; all five public paths fail closed with 503 and no salary-value leakage. No market capability or source status was changed.

## Verification

- Corrective UK service tests: 49 passed, including actual local manifest/artifact checks and synthetic future-manifest lifecycle checks.
- UK API tests: 31 passed, including all five blocked routes with the service factory forbidden, source-reference/checksum/metadata failure cases, revocation, and isolated synthetic success paths using the actual publication dependency.
- Corrective patch verification: 254 passed across five disjoint test commands covering all backend test files; see [SPRINT2_PHASE2B_TEST_REPORT.md](SPRINT2_PHASE2B_TEST_REPORT.md) for exact commands and outcomes.
- The monolithic all-tests command was not rerun; a previous attempt stalled at collection and is not claimed as a pass.
- All 9 India/USA model artifact hashes and 5 model/feature metadata hashes matched the artifact manifest.
- No app dependencies were added in Phase 2B. Existing pre-phase `openpyxl` declaration is unchanged.
- No frontend, deployment, model, feature contract, India/USA service, or raw/processed dataset changes were made.

## Files

Phase 2B adds the baseline, architecture, API contract, data dictionary, implementation, test, and completion reports; one router, one schema module, one service module; and the API/service tests plus fixtures. The only Phase 2B change to an existing source file is additive route registration in `src/backend/main.py`. The working tree also contains pre-existing Sprint 1/Phase 2A documents and code and a Phase 2A `requirements.txt` change; they were preserved and are inventoried in the current Git status.

## Remaining issues and boundaries

1. ONS reuse terms for public dashboard display and derived outputs have not been documented as approved. The official ONS Table 15 page links to OGL v3.0, but that alone is not a JobIntel use approval. The source remains `REVIEW_REQUIRED`.
2. The code/data reference points to the official [ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15), while the source catalog URL is different and did not resolve during this audit. The catalog also says UK-wide/2026 versus 11 Great Britain regions/2025 for the verified asset. No URL or metadata was silently changed.
3. Public data responses remain disabled by design. No user can access the local CSV through these routes under the current release gate.
4. The monolithic `pytest` command was not run in this corrective execution; an earlier Phase 2B attempt stalled during collection. The 254 current passes came from disjoint commands, not a monolithic run.

No commit, push, deployment, frontend release, registry approval, or Phase 2C work was performed. Public UK salary data remains unavailable pending human review and source-governance resolution.
