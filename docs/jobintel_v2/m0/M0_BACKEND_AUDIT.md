# M0 Backend Audit

## Application lifecycle and runtime

**VERIFIED FROM SOURCE CODE:** FastAPI application object `app` is in `src/backend/main.py`, app version `2.0.0`. The lifespan calls `sync_and_verify_artifacts(enforce_all=False)` from `utils/s3_sync.py`, logs any sync exception and proceeds to `get_model_registry()`. The registry verifies hashes and loads the mandatory models on startup. CORS origins are the union of explicit defaults and `CORS_ORIGINS`, excluding `*`; credentials are allowed, methods/headers are wildcarded. There is no authentication dependency or user/session system in the route code.

Routers: `usa`, `india`, `cross_market`, `overview`, `salary`, `skills`, `archetypes`, `predict`, `models`, `error_analysis`, `methodology`. Each is mounted twice, at `/api` and at root. System endpoints are `/`, `/health` and `/api/health`, `/ready` and `/api/ready`, `/meta` and `/api/meta`.

## Modules

- `models/model_registry.py`: singleton, hard-coded expected SHA-256 table, verification, `joblib`/`pickle` loading, status summary.
- `inference_service.py`: legacy USA prediction path.
- `services/usa_service.py`, `india_service.py`: market-specific option, feature-build, inference, output calculation.
- `services/market_service.py`: market aggregates and cross-market summary, with code fallbacks.
- `services/archetype_service.py`: market-specific clustering classification and archetype details.
- `data_service.py`: cached/loaded static aggregates from reports/data and fallback behavior.
- `utils/s3_sync.py`: optional object-storage artifact sync and hash checks. This audit did not access external storage.
- `routers/`: endpoint input/output adaptation. Pydantic request classes exist for India and USA prediction/archetype and legacy `/predict`.

## Model and data loading

Hash checks are performed before deserialization. Registry source is reviewed; then local artifacts were only hashed for this audit, not deserialized by the audit command itself. The repository’s test suite may deserialize the verified tracked models when run. Production loading behavior is **VERIFIED FROM SOURCE CODE**, not a live production check. Several services read aggregates from `reports/tables/...` first, then `data/processed/...`; availability and parity of all paths vary by deployment image.

## Validation and error behavior

Pydantic constrains India required strings (max 120), experience midpoint (0–35), experience range (0–15, default 2), work mode (max 60, default Hybrid), and skills (max 60). USA requires role/seniority/city (maximum 120/60/120), remote defaults true, skills maximum 60. Router functions catch broad exceptions: prediction/archetype errors generally become HTTP 400; option/analytics errors 500; India skill detail returns 404 if absent. Legacy `/predict` schema does not specify equivalent length/range constraints.

## Operational gaps / unknowns

- No rate limiting, authentication, dependency-injected authorization, or explicit per-endpoint response models were found in routers. The API appears intentionally public; production access control is **NOT VERIFIED**.
- Readiness is based on registry status/count; it does not validate every analytics dataset.
- Startup is synchronous for artifact loading inside lifespan. Cold-start duration under current Render state was not measured.
- Security headers, request size limits, logging redaction, and deployed CORS behavior are **NOT VERIFIED** by source/config review alone.
- Code includes broad `except Exception` and dynamic error details; this may expose internals in response details in some routes. Treat as a review item, not confirmed exploit.

## Source map

`src/backend/main.py`; `models/model_registry.py`; `data_service.py`; `inference_service.py`; all `routers/*.py`; `services/*.py`; `utils/s3_sync.py`; `config/artifact_manifest.json`.
