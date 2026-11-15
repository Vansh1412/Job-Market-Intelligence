# Sprint 1 Repository Audit

Audit refreshed 2026-11-04 before implementation. Repository root `E:/Job Market`; branch `master`; HEAD `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`fix(routing): mount API routers natively at both /api and root prefixes`). Start tree has only `?? docs/jobintel_v2/`, the previously authored M0 report directory. No pre-existing M0 document is modified or replaced. No `AGENTS.md` was found.

## Audited existing contracts and components

- FastAPI app: `src/backend/main.py`; CORS allowlist from defaults and `CORS_ORIGINS`; lifespan attempts optional artifact sync and initializes model registry. Existing 11 routers are each included at `/api` and root. They remain unchanged by the Sprint 1 additive plan.
- Existing market prediction routes: `src/backend/routers/india.py` (`GET /india/options`, `POST /india/predict`, archetype and analytics) and `usa.py` (`GET /usa/options`, `POST /usa/predict`, archetype and analytics). Prediction request schemas and output semantics are frozen.
- Market-specific services: `services/india_service.py`, `usa_service.py`, `market_service.py`, `archetype_service.py`; legacy inference/data service modules remain in place.
- Model loading: `models/model_registry.py`; registry verifies SHA-256 before pickle/joblib loads. `config/artifact_manifest.json` records model and data artifacts. M0 found all manifest hashes matched local files while nine expected artifact byte sizes are stale. Sprint 1 does not alter these registries or files.
- Feature contracts: India 290 raw fields → 327 transformed columns; USA 123 model inputs (41 metadata + 82 skills). Current services and golden/parity tests are preserved.
- Frontend: React/Vite app in `frontend/src`; `services/api.ts` defaults to `/api`; current `MarketType` supports USA and India. No frontend change is planned because Sprint 1 endpoints are additive and there is no verified dataset for new market UI.
- Current tests: Python tests under `tests/`, CI runs `test_routing_contracts.py`, `test_schema_contracts.py`, `test_cloud_contracts.py`; frontend Vitest, Oxlint, TypeScript/Vite build. Prior M0 recorded 17/17 for the backend CI subset, frontend build success, 89 lint warnings, frontend workers timing out before tests, and full pytest collection timeout. These are historical baseline results, not Sprint 1 results.
- Deployment: `render.yaml` starts one Uvicorn worker and probes `/api/ready`; root and frontend Vercel configs build the static Vite app. Neither deployment file nor frontend configuration needs modification for this additive API.
- Dependencies: Pydantic v2 and FastAPI are already declared in `requirements.txt`; no dependency addition is planned.

## Existing coupling and planned boundary

Prediction routes and services are intentionally market-specific and contain different payloads and transformations. Global registry/data catalog/employer directory will live in new modules and will not call, wrap, or normalize prediction services. A separate versioned router will expose only registry metadata and empty employer records until evidence-backed entries exist.

Detailed architecture, API response models, and incremental file plan are in `SPRINT1_ARCHITECTURE_DESIGN.md`, `SPRINT1_API_CONTRACTS.md`, and `SPRINT1_IMPLEMENTATION_PLAN.md`.
