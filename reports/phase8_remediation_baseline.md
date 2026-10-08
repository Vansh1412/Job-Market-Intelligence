# Phase 8 Remediation Baseline Report

**Execution Timestamp:** 2026-10-08T14:01:00+05:30  
**Audit Target:** JobIntel Production Remediation & Hardening  
**Auditor / Role:** Principal Engineer, ML Systems Auditor, QA Lead  
**Operating System:** Windows (PowerShell)  
**Python Runtime:** Python 3.13.9 (`pytest 8.4.2`)  
**Node.js Runtime:** Node.js v20+ (`npm v10+`, `vite 8.3.3`)  

---

## 1. Git & Workspace Baseline

- **Repository Root:** `e:\Job Market`
- **Current Branch:** `master`
- **Initial Baseline Commit:** `Baseline state before Phase 8 remediation`
- **Git Status:** Clean workspace (committed baseline; no unstaged modifications)
- **Active Document:** `reports/phase7_dashboard_feasibility.md`

---

## 2. Active Application Architecture & Routes

### A. Active Frontend Routes (`frontend/src/App.tsx`)
The production application exclusively registers and serves the following 7 pages via client-side routing:

| Canonical URL Path | Page Identifier | Component | Purpose |
| :--- | :--- | :--- | :--- |
| `/` | `home` | `HomePage` | Production landing page, headline KPIs, market selector |
| `/salary`, `/calculator` | `calculator` | `PredictorPage` | 7-step deterministic salary calculator |
| `/explore` | `explore` | `ExploreMarketPage` | Empirical distributions by role, location, experience, skills |
| `/skills` | `skills` | `SkillsPage` | Skill landscape and individual skill profile explorer |
| `/archetypes` | `archetypes` | `ArchetypesPage` | Latent archetypes explorer (7 USA, 6 India) |
| `/cross-market`, `/comparison` | `comparison` | `CrossMarketPage` | Direct parallel synthesis between US and Indian tech markets |
| `/how-it-works`, `/howitworks` | `howitworks` | `MethodologyPage` | Research methodology, data lineage, governance notes |

*Unrouted / Orphan Frontend Pages in `frontend/src/pages/`:*
- `OverviewPage.tsx` (Unused legacy Phase 5 page)
- `SalaryPage.tsx` (Unused legacy Phase 5 page)
- `ModelEvalPage.tsx` (Unused legacy Phase 5 page)
- `ErrorAnalysisPage.tsx` (Unused legacy Phase 5 page)

---

### B. Active Backend Routes (`src/backend/main.py`)
Mounted Routers:
1. `src/backend/routers/usa.py` (`/api/usa/*`) — Active
2. `src/backend/routers/india.py` (`/api/india/*`) — Active
3. `src/backend/routers/cross_market.py` (`/api/cross-market/*`) — Active
4. `src/backend/routers/skills.py` (`/api/skills/*`) — Partially Active (calls to `/landscape` and `/detail/{skill}`)
5. `src/backend/routers/archetypes.py` (`/api/archetypes/*`) — Legacy / Unused by active UI
6. `src/backend/routers/overview.py` (`/api/overview/*`) — Legacy / Unused by active UI
7. `src/backend/routers/salary.py` (`/api/salary/*`) — Legacy / Unused by active UI
8. `src/backend/routers/predict.py` (`/api/predict/*`) — Legacy / Unused by active UI
9. `src/backend/routers/models.py` (`/api/models/*`) — Legacy / Unused by active UI
10. `src/backend/routers/error_analysis.py` (`/api/error-analysis/*`) — Legacy / Unused by active UI
11. `src/backend/routers/methodology.py` (`/api/methodology/*`) — Legacy / Unused by active UI

System Endpoints:
- `GET /` — Service status & metadata
- `GET /health`, `GET /api/health` — Liveness probe
- `GET /ready`, `GET /api/ready` — Readiness probe (`ModelRegistry.get_status_report()`)
- `GET /api/meta` — Comprehensive research metadata and cohort metrics

---

## 3. Frozen Model & Data Artifacts

All 10 production model and data artifacts verified via cryptographic SHA-256 calculation:

| Artifact Key | Path | Verified SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- |
| `india_salary_model` | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | FROZEN / VERIFIED |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | FROZEN / VERIFIED |
| `india_cohort` | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | FROZEN / VERIFIED |
| `india_pca` | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | FROZEN / VERIFIED |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | FROZEN / VERIFIED |
| `usa_salary_model` | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | FROZEN / VERIFIED |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | FROZEN / VERIFIED |
| `usa_cohort` | `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | FROZEN / VERIFIED |
| `usa_pca` | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | FROZEN / VERIFIED |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | FROZEN / VERIFIED |

---

## 4. Verification Commands & Baseline Status

- **Backend Pytest:**
  - Command: `python -m pytest -q`
  - Baseline Result: `80 passed, 5 warnings in 106.80s`
- **Frontend Linter:**
  - Command: `npm run lint` (oxlint)
  - Baseline Result: `0 errors, 111 warnings` (unused imports, hook deps)
- **Frontend Build:**
  - Command: `npm run build` (`tsc -b && vite build`)
  - Baseline Result: Clean build in 241ms; produced `dist/` bundle
- **Docker Environment:**
  - Host OS: Windows (PowerShell)
  - Docker CLI Daemon: Not installed on current host (`docker: command not found`). Containerization validation will be verified structurally, with files prepared for deployment environments.

---

## 5. Known Defects to Remediate (from Ponytail Audit)

### P0 Critical
1. **USA Skill Detail Contract:** `SkillsPage.tsx` expects `median_with`, `prevalence`, `delta`, `combos`, `roles`, `archetypes`. Backend `skills.py` returns `median_salary`, `prevalence_pct`, `delta_vs_cohort`, `companions`, and empty roles/archetypes. Results in 0.0% demand and +$0 delta for USA skills.
2. **Dockerfile Missing Data Directory:** `Dockerfile` Stage 2 copies `src/`, `models/`, `reports/`, but omits `data/`. In a container runtime, `india_cohort` is missing, causing `/api/ready` to return HTTP 503 and Docker healthcheck to fail.

### P1 High
3. **Unknown USA Skill Returns HTTP 200:** `skills.py:get_skill_detail` returns `{"error": ...}` with status 200 instead of `raise HTTPException(status_code=404)`.
4. **Framer Motion Variant Key Mismatch:** `motionTokens.ts` defines `hidden`/`visible`, but `PageHero`, `SkillsPage`, and `ArchetypesPage` pass `initial="initial" animate="animate"`, silently failing hero stagger animations.
5. **Hardcoded Cross-Market Arrays:** `market_service.py:get_cross_market_summary` uses static Python dictionaries for `shared_skills_tracking` and `role_demand_comparison` instead of aggregating the empirical parquet datasets.

### P2 Medium
6. **Dual Model Loading Architecture:** `data_service.py` uses `@lru_cache` `joblib.load()` without checksums, duplicating models in RAM alongside `ModelRegistry`.
7. **Legacy Backend Routers Mounted:** 8 unused routers mounted in `main.py` expose dead endpoints.
8. **Orphan Frontend Pages:** 4 unused pages (`OverviewPage`, `SalaryPage`, `ModelEvalPage`, `ErrorAnalysisPage`) and unused components.
9. **Abandoned Streamlit Codebase:** `app.py` and `src/dashboard/*` remain in root despite `streamlit` being absent from `requirements.txt`.
10. **CORS Configuration:** `allow_origins=["*"]` combined with `allow_credentials=True` violates CORS standards.
11. **Missing Frontend Test Suite:** No automated testing tool configured in `frontend/package.json`.
12. **Routing Test Asserting Mock Dictionary:** `tests/test_routing_contracts.py` asserts against an internal Python copy rather than `App.tsx`.

### P3 Low
13. **Unbounded Prediction Payloads:** No string length or skill array upper bounds on `/predict` endpoints.
14. **Undocumented Salesforce Skill Exclusion:** Magic filter in `market_service.py:156` without taxonomy documentation.
15. **Mobile Navigation Accessibility:** Mobile hamburger button lacks `aria-label`, `aria-expanded`, and `aria-controls`.
16. **Missing USA Skill Router Test Coverage:** `test_skill_integrity.py` only validates India endpoints.

---
*End of Baseline Report. Proceeding to Phase B.*
