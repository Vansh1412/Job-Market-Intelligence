# Sprint 1 Implementation Plan

This plan is written before code changes. Work is incremental and additive.

| Step | Files to add | Verification / acceptance |
|---|---|---|
| 1. Typed market and common schemas | `src/backend/schemas/__init__.py`, `market.py`, `data.py`, `salary.py`, `employer.py`; `src/backend/markets/__init__.py`, `registry.py` | Instantiate all five configs; reject invalid market/currency/status; verify correct capability states and no false timestamps. |
| 2. Source catalog and provenance | `src/backend/data_catalog/__init__.py`, `registry.py` | Unique source IDs, supported source/reuse/validation enums; no approved or collected claim without evidence. |
| 3. Quality validator | `src/backend/data_catalog/validation.py` | Valid and invalid records; missing fields, salary, currency, period, market, source, and duplicate IDs yield structured issues; rejected contents not echoed. |
| 4. Employer foundation | `src/backend/employers/__init__.py`, `registry.py` | Empty default registry; typed profiles and locations require source evidence; duplicate company IDs rejected; no fabricated records. |
| 5. Additive API | `src/backend/routers/v1.py`; register once in `src/backend/main.py` under `/api/v1` | Response-model tests; market/source lists; 404 paths; employers returns empty list; existing root and `/api` routes stay registered. |
| 6. Tests and docs | `tests/test_global_foundation.py`, update/add API contract tests; `SPRINT1_DATA_DICTIONARY.md`, `SPRINT1_TEST_REPORT.md`, `SPRINT1_COMPLETION_REPORT.md` | Run targeted tests, existing backend CI subset, existing India/USA regression tests, compile check. Report actual collected/passed/failed/skipped/timeout details. |

No existing prediction service, request schema, frontend component, model file, artifact hash, dependency, environment variable, Render/Vercel config, database, or CI workflow needs modification. Only `src/backend/main.py` is modified to register the additive router. If testing reveals existing model parity regression, investigate; do not alter model behavior to make tests pass.

## Acceptance checks

- All five markets exist with accurate metadata and explicit capability states.
- UK/AU/SG salary prediction stays `NOT_IMPLEMENTED`; source listings do not imply data integration.
- Source metadata includes public reference and review state; no local path or fabricated freshness.
- Shared schemas preserve native compensation units and source definitions.
- Validation reports every rejected row and issue without silent dropping or data echo.
- Employer registry is operational and evidence-gated but empty until verified records are provided.
- New `/api/v1` routes have typed responses and tests; old endpoint contracts and model artifacts remain byte-identical.
- No dependencies or deployment settings change.
