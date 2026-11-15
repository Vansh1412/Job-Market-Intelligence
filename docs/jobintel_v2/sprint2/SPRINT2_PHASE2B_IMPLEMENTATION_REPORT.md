# Sprint 2 Phase 2B — Implementation Report

**Corrective patch date:** 2026-11-12
**Scope:** Resolve the Phase 2B manifest lifecycle contradiction. Phase 2C, actual ONS approval, and publication remain out of scope.

## Result

Corrected the publication lifecycle so data-integrity validation can accept either the current local-only manifest or a distinct, separately reviewed future publication artifact. It no longer hard-requires `publication_eligible: false`. A future artifact is accepted only in `PUBLICATION_APPROVED` mode with `publication_eligible: true`, source reuse `APPROVED`, catalog validation `VALIDATED`, and a complete approval record bound to the source ID, exact data and catalog references, match flag, approved public display use, timezone-aware timestamp, and processed CSV SHA-256. Actual file checksums and row/provenance integrity are still verified independently by the service.

The current Phase 2A manifest is unchanged: it remains `LOCAL_PREPARATION_ONLY`, `publication_eligible: false`, and `source_reuse_review_status: REVIEW_REQUIRED`; the live registry remains `REVIEW_REQUIRED` / `NOT_COLLECTED`. The router still requires live catalog approval and validation plus a coherent publication approval record before service construction. All five routes therefore continue returning HTTP 503 `UK_DATA_NOT_PUBLISHED` without loading or exposing salary data.

The service checks the actual live catalog source ID and exact catalog URL against the manifest, then verifies every CSV row's data reference, catalog reference, and source-reference-match flag against that manifest. Local mode may preserve an accurately recorded mismatch (`false`) for internal integrity checks; publication mode rejects it and requires the dataset rows, data provenance, manifest, approval record, and live catalog to contain the exact same reference. Publication also requires live geography and reference period to match the Great Britain/2025 artifact. The lazy service validates the pinned processed CSV checksum and full SOC 2020/region grid, preserves original median/CV values, then builds compact immutable per-process indexes. `UKSalaryContext.publication_status` is `PUBLISHED` only when the complete publication record and current catalog source, URL, geography, period, reuse, and validation states pass. Local integrity validation alone never labels data `PUBLISHED`. The service reads no raw workbook, performs no ingestion at app startup, writes no dataset, and calculates no derived salary statistics.

The router reevaluates catalog state and reads the manifest on every request. For a potentially publishable request it verifies exact source identity, approval metadata, approved-use scope, and hashes the processed CSV against both the manifest checksum and approval checksum before obtaining the service. This is deliberately uncached: a catalog approval revocation or file replacement blocks the next request, even if a service index already exists. Errors remain generic and do not expose paths or approval detail.

The lifecycle has five independent questions: whether the local bytes and rows validate; whether source reuse is approved for the proposed use; whether the catalog/source metadata is validated; whether a reviewed artifact is explicitly eligible for publication; and whether runtime catalog plus manifest checks make the public API available. Passing one does not imply the next.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/markets/UK/salary/occupations` | Search and paginate SOC 2020 occupations with reported/suppressed/blank coverage. |
| GET | `/api/v1/markets/UK/salary/occupations/{soc_code}` | Return one occupation’s source observations for all 11 regions. |
| GET | `/api/v1/markets/UK/salary/occupations/{soc_code}/regions` | Return source regional observations and explicit coverage warning. |
| GET | `/api/v1/markets/UK/salary/regions/{region}/occupations` | Filter and paginate occupations in one region by source-value status. |
| GET | `/api/v1/markets/UK/salary/metadata` | Return release identity, provenance, checksums, and status counts without row values. |

## Files added for Phase 2B

- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_BASELINE_AUDIT.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_ARCHITECTURE.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_API_CONTRACTS.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_DATA_DICTIONARY.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_IMPLEMENTATION_REPORT.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_TEST_REPORT.md`
- `docs/jobintel_v2/sprint2/SPRINT2_PHASE2B_COMPLETION_REPORT.md`
- `src/backend/routers/uk_salary.py`
- `src/backend/schemas/uk_salary.py`
- `src/backend/services/uk_salary_service.py`
- `tests/test_uk_salary_api.py`
- `tests/test_uk_salary_service.py`
- `tests/uk_salary_fixtures.py`

## Existing file changed for Phase 2B

- `src/backend/main.py` — additive import and registration of the new `/api` UK salary router. This file already contained pre-existing Sprint 1 `/api/v1` changes before Phase 2B; those were preserved.

`requirements.txt` is modified in the working tree only for the pre-existing Phase 2A `openpyxl` declaration; Phase 2B made no dependency changes. No market capability, source registry, deployment, frontend, model, feature contract, or India/USA prediction service was changed.

## Runtime check

On the verified local processed artifact (4,532 rows, 412 occupations, 11 regions; CSV SHA-256 `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`), direct lazy service construction took 938.53 ms on this development environment. Python `tracemalloc` measured 13.06 MiB current / 13.27 MiB peak allocation. Across 5,000 occupation-detail service calls, median was 0.141 ms and p95 0.198 ms. These are local microbenchmarks, not production latency guarantees; they exclude HTTP/network transport and concurrent load.

## Release restrictions and follow-up

The [official ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) lists the 2025 revised download and currently also lists a newer 2026 provisional edition; its page links to OGL v3.0. The ONS page does not adjudicate JobIntel's intended public display use, and no reuse approval was recorded. The code's dataset source reference is the official Table 15 page, while the live catalog URL is a different, inaccessible `...4digitsocashetable15` URL. The catalog also says UK/2026, but the inspected artifact is 11 Great Britain work regions / tax year ending 5 April 2025. These remain unresolved and block publication. Do not infer URL equivalence or silently update catalog metadata. Source reuse remains `REVIEW_REQUIRED`; validation remains `NOT_COLLECTED`; all six UK capabilities remain `NOT_IMPLEMENTED`.

Synthetic approval metadata, matching URLs, and approved source entries exist only in isolated temporary test fixtures. They are not written to the local manifest, source catalog, or application data and are not evidence of actual ONS permission. Phase 2C has not started.
