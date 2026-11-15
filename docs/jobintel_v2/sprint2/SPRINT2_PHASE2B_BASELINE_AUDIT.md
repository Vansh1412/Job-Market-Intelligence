# Sprint 2 Phase 2B.0 — Baseline Audit

**Audit date:** 2026-11-12
**Repository:** `E:\Job Market`
**Branch / HEAD:** `master` / `198b79dcdff08a5be5f08847c4262d31a3ce261e`
**Phase:** Pre-implementation audit; no Phase 2B application code has been changed.

## Working-tree baseline and preservation

At audit start, `git status --short --untracked-files=all` reported **2 modified tracked files and 64 untracked paths**. This existing state was inspected and preserved; nothing was reset, cleaned, stashed, deleted, moved, or overwritten.

| Existing worktree state | Paths / inventory |
|---|---|
| Modified tracked | `requirements.txt` (Phase 2A openpyxl declaration), `src/backend/main.py` (pre-existing Sprint 1 additive `/api/v1` router registration) |
| Untracked M0 docs | 18 files under `docs/jobintel_v2/m0/` |
| Untracked Sprint 1 docs | 7 files under `docs/jobintel_v2/sprint1/` |
| Untracked Sprint 2 docs | 19 files under `docs/jobintel_v2/sprint2/`, including Phase 2A implementation/review deliverables and earlier planning/research documents |
| Untracked Sprint 1 source/tests | `src/backend/data_catalog/` (3 files), `employers/` (2), `markets/` (2), `routers/v1.py`, `schemas/` (5), and `tests/test_global_foundation.py` (14 total) |
| Untracked Phase 2A source/test | `src/backend/ingestion/` (5 files) and `tests/test_ashe_ingestion.py` (6 total) |

The detailed path-by-path inventory was captured by the initial status command. All M0, Sprint 1, Sprint 2 and Phase 2A untracked work is preserved. The current backend main import/registration is pre-existing; Phase 2B router registration will be a separately identifiable additive change.

## Existing architecture and conventions

- FastAPI entry point is `src.backend.main:app`. The application has a lifespan that synchronizes/verifies configured artifacts and initializes the existing India/USA model registry. Phase 2B must not add UK data loading to this startup path, so missing/corrupt UK data cannot block existing markets.
- Existing domain routers are mounted under both `/api` and root for compatibility. The Sprint 1 router is mounted once under `/api` at `/api/v1` and currently exposes markets, sources and employers only, all as typed GET endpoints.
- Existing v1 response errors use FastAPI `HTTPException` and its `{"detail": ...}` response convention. Unknown registry IDs return 404. No global custom error handler was found.
- The UK market already exists in `markets/registry.py`. At baseline all six capabilities and data availability are `NOT_IMPLEMENTED`; currency is GBP, classification is SOC 2020, and sources reference the ASHE/labour-demand/SOC catalog IDs. No UK salary API or salary service existed.
- The ASHE source is `uk.ons.ashe`, `reuse_review_status=REVIEW_REQUIRED`, and `validation_status=NOT_COLLECTED`. The catalog URL differs from the canonical verified ONS reference. The source catalog also describes UK-wide coverage and a 2026 period, whereas this verified ASHE asset is a 2025-revised Great Britain-only release. These catalog discrepancies are documented and must not be silently edited or presented as corrected facts.
- Existing salary contract `SalaryObservation` models a positive Decimal in a normalized period but does not preserve ONS source-cell status, original source CV, or ASHE-specific provenance. Phase 2B needs market-specific response schemas and must not coerce suppressed/blank rows into ordinary salary observations.
- The Phase 2A adapter and contracts already parse the verified 2025 revised Table 15.7a median and paired 15.7b CV. The processed file is 6,302,989 bytes, has 4,532 source-cell rows, and is present locally under ignored `data/processed/`. Its recorded checksum is `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`.
- `MarketService` uses cached accessors for optional parquet cohorts, while `ModelRegistry` verifies artifact hashes and loads frozen models. The UK descriptive service will remain separate from model loading and use a lazy, one-time validated data store rather than per-request parsing or ingestion.
- Existing API paths include exact `/api/v1/markets` and `/api/v1/markets/{market_id}`. Proposed UK nested `/api/v1/markets/UK/salary/...` paths do not collide with these exact routes; OpenAPI is available for final conflict verification.

## Release and deployment controls

- `publication_eligible` in the ASHE manifest is false. Source reuse stays `REVIEW_REQUIRED`; catalog validation stays `NOT_COLLECTED`.
- UK salary prediction and public salary analytics must remain unavailable. Australia and Singapore remain `NOT_IMPLEMENTED`.
- `.gitignore` excludes `data/raw/`, `data/processed/`, CSV and parquet files. Baseline `git ls-files data` was empty. Raw workbooks and processed CSV must remain ignored.
- `render.yaml` uses one Uvicorn worker, Python 3.11.9 and the existing `uvicorn src.backend.main:app` command with health check `/api/ready`. It is frozen for this phase. Vercel/frontend configuration is also frozen.
- No database, paid infrastructure, external API, background task or scheduled ingestion is present or authorized.
- The only Phase 2A dependency addition is `openpyxl>=3.1.0,<4.0.0`; no Python lockfile exists. This phase should add no dependency.

## Baseline test status

Executed before Phase 2B application edits, on Python 3.13.9 from the repository root:

| Command | Result |
|---|---|
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_ashe_ingestion.py` | **27 passed in 11.88s** |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_routing_contracts.py tests/test_schema_contracts.py tests/test_cloud_contracts.py tests/test_global_foundation.py` | **43 passed in 6.90s** |
| USA golden, India golden, and combined golden/parity commands | USA **1 passed**, India **1 passed**, combined **15 passed**. Because sandbox loopback sockets block `TestClient`, the unchanged tests ran with approved local-socket access outside the sandbox; see `SPRINT2_ASHE_PIPELINE_TEST_REPORT.md` for exact commands and diagnosis. The app verified 10/10 model artifacts. |

These results establish the Phase 2B baseline only. The full backend suite and frontend build have not yet been run for Phase 2B.

## Registry baseline

| Item | Baseline |
|---|---|
| UK salary prediction | `NOT_IMPLEMENTED` |
| UK salary analytics | `NOT_IMPLEMENTED` |
| UK source data availability | `NOT_IMPLEMENTED` in product market registry |
| ASHE source reuse | `REVIEW_REQUIRED` |
| ASHE catalog validation | `NOT_COLLECTED` |
| ASHE manifest publication eligibility | `false` |
| AU / SG capabilities | `NOT_IMPLEMENTED` |

No API contract may return salary values while the source and manifest remain in these states. No registry update is planned for this release-gated phase.
