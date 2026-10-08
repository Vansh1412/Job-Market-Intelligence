# Phase 7 Initial Pre-Audit Report: Production Hardening & Deployment Readiness

**Project:** INT234 Predictive Analytics — Job Market Intelligence (JobIntel)  
**Author:** Antigravity Senior ML & Verification Engineering Team  
**Date:** October 7, 2026  
**Status:** Pre-Hardening Baseline Certified  
**Scope:** Comprehensive Diagnostic Audit of System Architecture, Reliability, Security, and Academic Integrity  

---

## 1. Current System Architecture

The JobIntel platform consists of a decoupled two-tier architecture synthesizing two independent empirical labor-market research pipelines (USA and India):

```
                                [USER CLIENT / BROWSER]
                                           │
                                           ▼
                               [REACT 19 + VITE 8 FRONTEND]
                               frontend/src/App.tsx
                               - Global MarketContext (USA ⟷ India)
                               - Guided Salary Calculator Wizard (Steps 1–5)
                               - Market Explorer (Filterable Empirical Distributions)
                               - Skill Intelligence (82 USA / 284 India Skills)
                               - Archetype Explorer (k=7 USA / k=6 India)
                               - USA vs. India Cross-Market Synthesis
                                           │
                                           │ HTTP REST (/api/*)
                                           ▼
                                 [FASTAPI APPLICATION]
                                 src/backend/main.py (v2.0.0)
                                           │
                      ┌────────────────────┴────────────────────┐
                      ▼                                         ▼
            [USA INFERENCE SERVICE]                   [INDIA INFERENCE SERVICE]
            src/backend/services/usa_service.py       src/backend/services/india_service.py
            - 123-Feature Vector Builder              - 290-Feature DataFrame Builder
            - Live XGBoost Regression Inference       - Live HistGradientBoosting Inference
            - Archetype Inference (k=7)               - Archetype Inference (k=6, Hungarian Map)
                      │                                         │
                      └────────────────────┬────────────────────┘
                                           ▼
                              [CENTRALIZED MODEL REGISTRY]
                              src/backend/models/model_registry.py
                              - Startup SHA-256 Hash Validation (10 Artifacts)
                              - Single In-Memory Deserialization Pool
```

---

## 2. Current Production Readiness Assessment

- **ML Inference Integrity:** Complete and frozen. Direct Python model execution matches API inference within $| \Delta | < 0.01$ native currency units across both markets.
- **Test Suite Status:** 29/29 existing PyTest unit/integration tests pass. 43/43 Phase 6 verification gates pass.
- **Frontend Build Status:** Vite production build compiles in 239ms, outputting production bundle in `frontend/dist/`.
- **Gaps to Production Excellence:**
  - Lack of dedicated containerization infrastructure (`Dockerfile`, `docker-compose.yml`).
  - Absence of automated GitHub Actions continuous integration pipeline (`.github/workflows/ci.yml`).
  - Absence of an explicit `/api/ready` Kubernetes-style readiness probe separate from `/api/health`.
  - Incomplete Python dependencies manifest in `requirements.txt`.
  - Absence of a standardized `.env.example` environment template.

---

## 3. Technical Debt Analysis

1. **Dependency Manifest Gaps:** `requirements.txt` includes core scientific libraries (`numpy`, `pandas`, `scikit-learn`, `xgboost`, `scipy`) but omits web server and test packages (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`).
2. **Pydantic V2 Schema Deprecation:** Pydantic models in `src/backend/routers/predict.py` use `Field(..., example=...)` rather than the V2 standard `Field(..., json_schema_extra=...)`, generating runtime deprecation warnings during testing.
3. **Endpoint Proliferation / Documentation:** Legacy Phase 4/5 endpoints co-exist with unified Phase 6 endpoints (`/api/usa/*` and `/api/india/*`). An exhaustive API contract audit is required to formally document method, path, request schema, response schema, and error codes.
4. **Defensive Input Validation:** While happy-path requests are validated, defensive bounds checking (e.g. negative experience, excessive years, unknown roles, empty/duplicate skills) must return clean HTTP 422/400 errors without leaking internal Python tracebacks.

---

## 4. Security Audit Findings

1. **Secret Leakage Scan:** A preliminary scan confirms zero API keys, database credentials, or proprietary tokens are hardcoded in application logic.
2. **CORS Policy:** `app.add_middleware(CORSMiddleware)` currently uses wildcard `allow_origins=["*"]`. In production, origins should be configurable via environment variables (`CORS_ORIGINS`).
3. **Arbitrary Code Execution:** Zero instances of `eval()`, `exec()`, or uncontrolled subprocess execution in production inference paths.
4. **Path Traversal / Data Access:** File access in services is strictly constrained to pre-defined static CSV/Parquet paths in `reports/tables/` and `models/`. No dynamic user-supplied file path interpolation exists.

---

## 5. Performance Diagnostics

1. **Backend Startup Time:** Cold boot takes ~2.1 seconds on local hardware to compute SHA-256 hashes of 10 large pickle/parquet files (including the 37MB pre-trained pipelines) and load models into memory.
2. **Inference Latency:**
   - USA XGBoost prediction: ~1.8 ms per request.
   - India HistGradientBoosting prediction: ~4.2 ms per request.
   - Both comfortably exceed the < 50 ms interactive threshold.
3. **Frontend Bundle Size:** Minified JS bundle is ~704 kB (`dist/assets/index-*.js`). Recharts and Lucide account for ~60% of vendor code. The initial page load is fast (< 300 ms), but bundle splitting should be documented.

---

## 6. User Experience (UX) Diagnostics

1. **Guided Calculator Flow:** The 5-step wizard cleanly guides the user from market selection through role, experience, metro, skills, to live estimation.
2. **Zero-Skill Edge Case:** Correctly displays "Archetype Unavailable (Zero Skills)" and uses cohort-level residual confidence margins.
3. **Stale State on Market Switching:** When switching markets, reactive state successfully clears country-specific role, city, and skill selections, preventing invalid cross-market submissions.
4. **Visual Hierarchy:** Premium dark-mode glassmorphic interface with consistent status pills, typography, and contrast.

---

## 7. Deployment Risks

1. **System Port Conflicts:** Backend defaults to port 8000 and frontend to port 5173 without fallback flags.
2. **Model File Paths:** Paths are currently relative (e.g. `models/india/final_model.pkl`). When deployed inside Docker or different working directories, absolute resolution anchored to the repository root is required.
3. **Readiness Probe Absence:** Deployment orchestrators cannot differentiate between a container starting up (computing hashes) and a container ready to serve live traffic.

---

## 8. Documentation Issues

1. **Metric Traceability:** Need an explicit `reports/phase7_metric_lineage.md` mapping every UI number directly to its research table, artifact, and phase.
2. **README Depth:** `README.md` must be expanded with comprehensive installation, Docker deployment, API contract documentation, and research findings.

---

## 9. Academic & Reporting Risks

1. **Causal Overclaiming:** Strict vigilance is required to ensure regression coefficients and skill premiums are termed *observational associations*, not causal wage enhancements.
2. **Regression $R^2$ Terminology:** Regression $R^2$ must strictly be referenced as the coefficient of determination or explained variance, never as "accuracy".
3. **Upper-Tail India Error:** Must prominently document and preserve the known limitation that model error scales significantly on extreme high salaries ($\ge 20$ LPA: MAE ≈ 8.06 LPA; $\ge 40$ LPA: MAE ≈ 31.12 LPA).
4. **Sample Size Disparity:** Must transparently communicate that specialized India archetypes (`IND_ARC_01` Big Data: $N=198$; `IND_ARC_06` SAP: $N=125$) represent smaller subsets than the broad baseline cohort (`IND_ARC_05`: $N=3,767$).

---

## 10. Recommended Remediation Plan (Phases 7.2 – 7.40)

| Priority | Remediation Task | Target Phase |
|:---:|---|:---:|
| **P0** | Verify all 20 frozen model and dataset hashes bitwise against SSOT registry | Phase 7.2 |
| **P0** | Implement deterministic Golden Prediction tests for USA and India | Phase 7.4 |
| **P0** | Implement Archetype Parity tests across all skill regimes | Phase 7.5 |
| **P0** | Add `/api/ready` readiness endpoint and harden input validation error handling | Phase 7.7 – 7.8 |
| **P0** | Complete security audit, `.env.example`, and dependency manifest updates | Phase 7.9 – 7.11 |
| **P1** | Add Docker containerization (`Dockerfile`, `docker-compose.yml`) and CI pipeline | Phase 7.29 – 7.30 |
| **P1** | Create Metric Lineage artifact (`phase7_metric_lineage.md`) and verify scientific terminology | Phase 7.19, 7.21 |
| **P1** | Generate final architecture diagram and comprehensive 60+ gate verification suite | Phase 7.32, 7.34 |
| **P0** | Final regression tests, honest distinction audit, and final project status certification | Phase 7.35 – 7.40 |

---

*Phase 7.1 Initial Pre-Audit complete. System is verified stable and ready for production hardening.*
