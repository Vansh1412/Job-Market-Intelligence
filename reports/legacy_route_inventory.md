# Legacy Route Inventory & Deprecation Analysis

**Audit Date:** 2026-10-08  
**Scope:** `src/backend/routers/` mounted in `src/backend/main.py`  
**Purpose:** Identify active vs obsolete routes, verify callers, and define deprecation/retention policies.

---

## Route Inventory Matrix

| Route Prefix | Status | Active Frontend Callers | Test Suite Callers | Safe to Remove? | Policy & Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `/api/usa/*` | **ACTIVE (SSOT)** | `PredictorPage`, `ExploreMarketPage`, `ArchetypesPage` | `test_prediction_parity.py`, `test_chart_contracts.py` | **NO** | Core production API for USA salary prediction, market distributions, and archetypes. |
| `/api/india/*` | **ACTIVE (SSOT)** | `PredictorPage`, `ExploreMarketPage`, `SkillsPage`, `ArchetypesPage` | `test_skill_integrity.py`, `test_chart_contracts.py` | **NO** | Core production API for India salary prediction, market distributions, skills, and archetypes. |
| `/api/cross-market/*` | **ACTIVE (SSOT)** | `CrossMarketPage` | `test_end_to_end_integration.py` | **NO** | Core production API for empirical comparative synthesis between US and Indian tech markets. |
| `/api/skills/*` | **ACTIVE (HYBRID)** | `SkillsPage` (`/landscape`, `/detail/{skill}`) | `test_skill_integrity.py`, `test_chart_contracts.py` | **NO** | Core production API for USA Skill Explorer. Endpoints `/landscape` and `/detail/{skill_name}` are actively invoked by `SkillsPage.tsx`. Retain and maintain. |
| `/api/overview/*` | **LEGACY** | None (Archived `OverviewPage.tsx`) | `test_end_to_end_integration.py` | **PRESERVE** | Serves static Phase 3/5 data exploration tables. Deprecate in OpenAPI with `deprecated=True`; retain for external API backward compatibility. |
| `/api/salary/*` | **LEGACY** | None (Archived `SalaryPage.tsx`) | `test_end_to_end_integration.py` | **PRESERVE** | Legacy Phase 5 salary benchmark tables. Replaced in v2 by `/api/usa/market-summary`. Retain with `deprecated=True`. |
| `/api/predict/*` | **LEGACY** | None (Archived v1 predictor) | `test_end_to_end_integration.py`, `test_input_validation.py` | **PRESERVE** | Legacy USA-only predictor endpoint. Replaced in v2 by `/api/usa/predict` and `/api/india/predict`. Consolidated to delegate model inference to `ModelRegistry`. Retain with `deprecated=True`. |
| `/api/archetypes/*` | **LEGACY** | None (Archived v1 archetypes) | `test_archetype_parity.py` | **PRESERVE** | Legacy USA-only cluster list. Replaced in v2 by `/api/usa/archetypes` and `/api/india/archetypes`. Retain with `deprecated=True`. |
| `/api/models/*` | **LEGACY RESEARCH** | None (Archived `ModelEvalPage.tsx`) | None | **PRESERVE** | Exposes frozen CV tables and feature importance metrics for academic and research evaluation. Retain with `deprecated=True`. |
| `/api/error-analysis/*` | **LEGACY RESEARCH** | None (Archived `ErrorAnalysisPage.tsx`) | None | **PRESERVE** | Exposes archetype-level residual error tables and hypotheses from Phase 5 report. Retain with `deprecated=True`. |
| `/api/methodology/*` | **LEGACY RESEARCH** | None (`MethodologyPage.tsx` is static) | None | **PRESERVE** | Exposes pipeline stage definitions and leakage controls. Retain with `deprecated=True`. |

---

## Action Plan

1. **Retain All Endpoints:** In accordance with the strict requirement ("Do not break external API compatibility accidentally"), all legacy routers remain mounted in `src/backend/main.py`.
2. **Consolidate Model Execution:** `predict.py` and `data_service.py` have been refactored to delegate directly to `ModelRegistry`, ensuring zero duplicate models in process memory.
3. **Deprecation Metadata:** Mark legacy routers with `deprecated=True` or legacy tags in OpenAPI documentation to clearly distinguish JobIntel v2 unified production routes (`/api/usa`, `/api/india`, `/api/cross-market`, `/api/skills`) from Phase 5 legacy routes.
