# Sprint 2 Baseline Audit

**Status:** Phase 0/1 planning artifact; application implementation has not started.  
**Audit date:** 2026-11-10  
**Repository:** `E:/Job Market`  
**Branch / HEAD:** `master` / `198b79dcdff08a5be5f08847c4262d31a3ce261e`

## Scope and working-tree state

The baseline is the current checkout, including the accepted Sprint 1 work already present in the working tree. Before this planning work, `git status --short` showed `M src/backend/main.py`, untracked `src/backend/data_catalog/`, `src/backend/employers/`, `src/backend/markets/`, `src/backend/routers/v1.py`, `src/backend/schemas/`, `tests/test_global_foundation.py`, and the untracked `docs/jobintel_v2/` tree containing M0 and Sprint 1 documents. These are pre-existing Sprint 1 changes and must be preserved. This Sprint 2 planning step adds documentation only; no application code, data, dependency, frontend, model, or deployment file has been changed.

No Sprint 2 source file is considered implemented. No external dataset was downloaded or opened. Local data directories were inspected by names only; private or ignored dataset contents were not read.

## Complete untracked-file inventory at this audit checkpoint

`git ls-files --others --exclude-standard` showed 50 untracked files: the 18 existing M0 documents, 7 existing Sprint 1 documents, 14 existing Sprint 1 source/test files, and the 11 Sprint 2 planning documents created in this phase. The existing M0/Sprint 1 files predate this phase and are not treated as Sprint 2 output.

Existing M0 files: `m0/M0_API_INVENTORY.md`, `M0_ARTIFACT_INTEGRITY_MANIFEST.md`, `M0_BACKEND_AUDIT.md`, `M0_CURRENT_ARCHITECTURE.md`, `M0_DATA_PRIVACY_AND_QUALITY.md`, `M0_DECISIONS_REQUIRED.md`, `M0_DEPLOYMENT_AUDIT.md`, `M0_EXECUTIVE_SUMMARY.md`, `M0_FEATURE_CONTRACT_AUDIT.md`, `M0_FRONTEND_AUDIT.md`, `M0_GAP_ANALYSIS.md`, `M0_IMPLEMENTATION_ROADMAP.md`, `M0_MARKET_DATA_FEASIBILITY.md`, `M0_MODEL_ARTIFACT_INVENTORY.md`, `M0_REPOSITORY_STATE.md`, `M0_RISK_REGISTER.md`, `M0_TARGET_ARCHITECTURE.md`, and `M0_TEST_BASELINE.md`.

Existing Sprint 1 documents: `sprint1/SPRINT1_API_CONTRACTS.md`, `SPRINT1_ARCHITECTURE_DESIGN.md`, `SPRINT1_COMPLETION_REPORT.md`, `SPRINT1_DATA_DICTIONARY.md`, `SPRINT1_IMPLEMENTATION_PLAN.md`, `SPRINT1_REPOSITORY_AUDIT.md`, and `SPRINT1_TEST_REPORT.md`.

Existing Sprint 1 source/test files: `src/backend/data_catalog/{__init__.py,registry.py,validation.py}`, `src/backend/employers/{__init__.py,registry.py}`, `src/backend/markets/{__init__.py,registry.py}`, `src/backend/routers/v1.py`, `src/backend/schemas/{__init__.py,data.py,employer.py,market.py,salary.py}`, and `tests/test_global_foundation.py`.

Sprint 2 planning documents created in this phase: `sprint2/SPRINT2_API_CONTRACTS.md`, `SPRINT2_ARCHITECTURE_DESIGN.md`, `SPRINT2_BASELINE_AUDIT.md`, `SPRINT2_COMPLETION_REPORT.md`, `SPRINT2_DATA_DICTIONARY.md`, `SPRINT2_DATA_QUALITY_REPORT.md`, `SPRINT2_EMPLOYER_INTELLIGENCE_DESIGN.md`, `SPRINT2_IMPLEMENTATION_PLAN.md`, `SPRINT2_INGESTION_DESIGN.md`, `SPRINT2_SOURCE_FEASIBILITY.md`, and `SPRINT2_TEST_REPORT.md`.

## Current architecture

| Area | Current state | Evidence / files |
|---|---|---|
| Backend | FastAPI, Pydantic v2; normal entry point `src.backend.main:app`; router groups mounted under `/api` and root, with additive metadata router mounted under `/api/v1`. Lifespan performs optional artifact synchronization and initializes the model registry. | `src/backend/main.py`, `src/backend/routers/*.py` |
| Established prediction markets | India and USA have separate request contracts, services, preprocessing, frozen artifacts, and prediction routes. M0/Sprint 1 records India 290 raw features → 327 transformed columns and USA 123 inputs. | `src/backend/routers/india.py`, `usa.py`; `src/backend/services/india_service.py`, `usa_service.py`; `src/backend/models/model_registry.py`; audit docs under `m0/` and `sprint1/` |
| Global foundation | Five-market metadata registry and shared typed contracts; source catalog and provenance; salary contract; quality issue/result models; empty employer registry. | `src/backend/markets/`, `src/backend/data_catalog/`, `src/backend/schemas/`, `src/backend/employers/` |
| API clients / frontend | React 19 + Vite + TypeScript client defaults to `/api`; current app state and screens support India and USA. No UK data views/client methods exist. | `frontend/src/services/api.ts`, `frontend/src/context/MarketContext.tsx`, `frontend/src/App.tsx` |
| Data | Repository has `data/raw/` and `data/processed/` directories, both empty in the visible directory listing. `.gitignore` excludes these paths and parquet files. Other local and ignored project data exists outside these directories per prior M0 records; it is private and is not in scope for UK ingestion. | `data/`, `.gitignore`, `docs/jobintel_v2/m0/M0_DATA_PRIVACY_AND_QUALITY.md` |
| CI | `.github/workflows/ci.yml`: Ubuntu backend code/schema/cloud-contract subset (`tests/test_routing_contracts.py`, `test_schema_contracts.py`, `test_cloud_contracts.py`); frontend Vitest/lint/build; security/leakage scan. A separate protected Windows Docker release workflow exists. | `.github/workflows/ci.yml`, `.github/workflows/docker-release-gate.yml`, `.github/workflows/docker-build-manual.yml` |
| Deployment | Render free-tier single-worker Uvicorn service; Vercel static frontend configuration. These are frozen for this planning scope. | `render.yaml`, `vercel.json`, `frontend/vercel.json` |
| Dependencies/config | Existing requirements include FastAPI, Pydantic, pandas, PyArrow and Uvicorn. No explicit `openpyxl` declaration was found. `.env.example` variable names include `JOBINTEL_ENV`, host/port/log/workers, `CORS_ORIGINS`, `VITE_API_BASE_URL`, `ENFORCE_MODEL_HASH_VERIFICATION`; only names were inspected. | `requirements.txt`, `.env.example` |

## Sprint 1 integration verification

Sprint 1 documents describe the accepted metadata-only foundation and actual HTTP/regression checks. Current source matches the architectural intent: `/api/v1` is separate from India/USA prediction routers; the employer registry defaults to an empty tuple; external source reuse is marked `REVIEW_REQUIRED`; salary amounts use finite positive Decimal semantics; validation issue summaries do not serialize rejected source contents. The UK market entry is metadata only and sets product capabilities to `NOT_IMPLEMENTED`.

The six existing versioned routes are `GET /api/v1/markets`, `GET /api/v1/markets/{market_id}`, `GET /api/v1/sources`, `GET /api/v1/sources/{source_id}`, `GET /api/v1/employers`, and `GET /api/v1/employers/{company_id}`. They are not UK analytics endpoints.

Sprint 1 verification results are referenced from `sprint1/SPRINT1_TEST_REPORT.md` and `SPRINT1_COMPLETION_REPORT.md`. This Sprint 2 planning stage did not rerun those tests. Their previous successful results do not imply Sprint 2 data or analytics are operational.

## Existing UK-related functionality

- `MarketId.UK`, a UK market metadata entry, GBP currency, and UK source catalog entries exist.
- Catalogued official source families include ONS ASHE, ONS labour-demand advert counts, and SOC 2020. They remain `REVIEW_REQUIRED` and `NOT_COLLECTED`.
- There is no UK salary observation dataset, SOC registry/search, normalization pipeline, UK analytics service, or UK data API.
- There is no employer dataset; `/api/v1/employers` returns an empty registry. No UK company/job-posting record is present in the Sprint 1 registry.
- Existing frontend market enum/context and prediction workflows support only India and USA; UK integration would be a later implementation phase and is not started.

## Reusable modules and constraints

Reuse the existing Pydantic source/provenance and salary models in `src/backend/schemas/data.py` and `salary.py`; quality checks in `src/backend/data_catalog/validation.py`; source metadata in `src/backend/data_catalog/registry.py`; market metadata in `src/backend/markets/registry.py`; and additive router pattern in `src/backend/routers/v1.py`. Extend with evidence and tests only where the new UK contract needs fields that do not already exist. Do not create parallel source, market, or validation registries.

The India/USA prediction architecture, services, routers, schemas, model registry, model and preprocessing artifacts, feature dimensions, golden values, and runtime behavior are out of bounds. Also frozen: frontend/deployment configuration, dependency list, private data, and CI configuration. No download, API credential, external service, storage provider, or paid infrastructure is authorized by this plan.

## Risks and discrepancies to resolve after approval

1. ASHE Table 15’s current dataset page mixes release labels and contains an Oct 22, 2026 delay notice. Exact usable workbook, release/reference period, measures and table notes must be inspected after source approval.
2. Existing dependencies do not explicitly declare an XLSX reader. Do not assume an undeclared transitive package is available. Prefer a permitted CSV publication or an already-supported reader; if a new dependency is necessary, stop for separate approval.
3. The ONS labour-demand page publishes an aggregate dataset under OGL page terms but its underlying adverts are Textkernel-derived. No raw advert reuse or independent scraping is implied.
4. The frontend and market switch have no UK integration; adding one is a later approved phase, not a metadata-only task.
5. No private dataset provenance was examined for Sprint 2 and none is proposed for use.

See `SPRINT2_SOURCE_FEASIBILITY.md`, `SPRINT2_ARCHITECTURE_DESIGN.md`, `SPRINT2_DATA_DICTIONARY.md`, `SPRINT2_INGESTION_DESIGN.md`, `SPRINT2_API_CONTRACTS.md`, `SPRINT2_EMPLOYER_INTELLIGENCE_DESIGN.md`, and `SPRINT2_IMPLEMENTATION_PLAN.md` for proposals and gates.
