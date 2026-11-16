# JOBINTEL 2.0 — SPRINT 3B.2
## PHASE 0: REPOSITORY AND IMPLEMENTATION AUDIT

**Milestone:** Sprint 3B.2 — Phase 0 Baseline Audit  
**Date:** 2026-11-16  
**Auditor / Roles:** Principal Data Scientist, Labour Market Intelligence Researcher, Backend Architect, Lead QA  
**Target Branch:** `staging/sprint2c3`  
**Current HEAD:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

### 1. REPOSITORY AND BASELINE VERIFICATION

A comprehensive preflight audit confirms the repository is in an approved, clean, and isolated state:

| Parameter | Observed State | Status |
| :--- | :--- | :---: |
| **Git Branch** | `staging/sprint2c3` | **VERIFIED** |
| **Git Commit SHA** | `58974134e56b4c3ec6b6119b7b4739e9cce857f3` | **VERIFIED** |
| **Remote Staging** | `origin/staging/sprint2c3` in exact sync with local HEAD | **VERIFIED** |
| **Production Master** | `origin/master` at `198b79dcdff08a5be5f08847c4262d31a3ce261e` (untouched) | **VERIFIED** |
| **Working Tree** | Clean; zero tracked modifications; prior audit reports untracked | **VERIFIED** |
| **Staging Deployments** | Vercel (`dpl_4ETTzWDUttnGmCwS6uCcFp8fFsvb`) & Render healthy | **VERIFIED** |

---

### 2. ANSWERS TO MANDATORY AUDIT QUESTIONS

#### Q1: Is there already a demand-related service?
**No.** `src/backend/services/` contains `occupation_service.py`, `salary_service.py`, `market_service.py`, `archetype_service.py`, `task_similarity.py`, `uk_salary_service.py`, `usa_service.py`, and `india_service.py`. There is currently no `demand_service.py`.

#### Q2: Is there existing job advertisement data?
**Yes, in research modeling cohorts only.** 
- `data/processed/cleaned_jobs.parquet` contains ~34k US tech job postings from Dataset A/B.
- `data/processed/india/cleaned_india_jobs.parquet` and `india_job_skills.parquet` contain ~5.8k Indian tech job postings.
These datasets serve USA and India salary ML models and skill frequency analytics. They are static research snapshots, not real-time multi-market administrative vacancy feeds.
- In `src/backend/data_catalog/registry.py`, three official vacancy/demand sources are cataloged with status `NOT_COLLECTED`:
  - `au.jsa.ivi` (Jobs and Skills Australia Internet Vacancy Index)
  - `uk.ons.labour-demand` (ONS Labour Demand Volumes by SOC 2020)
  - `sg.mom.vacancies` (Singapore MOM Job Vacancy Statistics)

#### Q3: Are there existing occupation-skill mappings?
**Yes, partial.**
- In `src/backend/data/occupations/canonical_occupations.json`, each of the 12 canonical concepts specifies a curated list of `core_competencies`.
- In `src/backend/data/occupations/national_occupations.json`, task statements (`tasks`) and `entry_qualifications` are defined for all 30 national/international records.
- In `src/backend/routers/skills.py`, skill frequencies, co-occurrences, and salary associations are computed for USA job postings.
- However, there is no structured multi-market occupation-to-skill demand matrix linking official classifications to empirical skill frequencies.

#### Q4: Are there existing employer records?
**No active records.** `src/backend/employers/registry.py` defines `EmployerRegistry`, which initializes with an empty tuple (`()`). Calling `GET /api/v1/employers` returns an empty array `[]`.

#### Q5: Is any demand analytics implementation already present?
**Architecturally planned, but unmounted.**
- `src/backend/schemas/market.py` defines `MarketCapability.DEMAND_ANALYTICS`.
- In `src/backend/markets/registry.py`:
  - India and USA are configured with `demand_analytics: CapabilityStatus.PARTIAL`.
  - UK, Australia, and Singapore are configured with `demand_analytics: CapabilityStatus.NOT_IMPLEMENTED`.
- There are no routers, endpoints, or calculation engines for demand analytics in the current codebase.

#### Q6: Which existing schemas can be reused?
- `src/backend/schemas/market.py`: `MarketId`, `MarketConfig`, `MarketCapability`, `CapabilityStatus`.
- `src/backend/schemas/occupation.py`: `NationalOccupation`, `CanonicalOccupation`, `OccupationMapping`.
- `src/backend/schemas/data.py`: `DataSource`, `SourceCategory`, `ReuseReviewStatus`, `ValidationStatus`.
- `src/backend/schemas/governance.py`: Governance checks, fail-closed revocation mechanisms.

#### Q7: Which components can be extended without duplication?
- `src/backend/data_catalog/registry.py`: Update existing source definitions (`au.jsa.ivi`, `uk.ons.labour-demand`, `sg.mom.vacancies`) and add BLS Employment Projections / JSA Skills Priority List / MOM Job Vacancies / MOSPI PLFS.
- `src/backend/markets/registry.py`: Upgrade `demand_analytics` capability status to `AVAILABLE` or `PARTIAL` as data is integrated.
- `frontend/src/components/AppHeader.tsx` & `frontend/src/App.tsx`: Route `/demand` and header navigation item.

#### Q8: Which existing API routes must remain unchanged?
All existing routes must be preserved without breaking modifications:
- Prediction routes: `/api/predict`, `/api/usa/*`, `/api/india/*`
- Occupation routes: `/v1/occupations/*`
- Salary routes: `/v1/salary/*`
- UK salary routes: `/v1/markets/UK/salary/*` (enforcing HTTP 503 fail-closed)
- Foundation routes: `/health`, `/api/ready`, `/meta`, `/v1/markets`, `/v1/sources`, `/v1/employers`
- Market analytics routes: `/skills/*`, `/archetypes/*`, `/overview/*`

#### Q9: Are there source licensing restrictions?
**Yes.**
- **US BLS / O*NET:** Public domain / CC BY 4.0. Redistribution allowed.
- **UK ONS:** Open Government Licence v3.0 (OGL). Redistribution allowed with attribution.
- **Australia ABS / JSA:** Creative Commons Attribution 4.0 International (CC BY 4.0). Redistribution allowed with attribution.
- **Singapore MOM / SingStat:** Singapore Open Data Licence. Redistribution allowed with attribution.
- **India MOSPI PLFS:** Open Government Data (OGD) Licence India. Redistribution allowed with attribution.
- **Commercial job board postings (Indeed, LinkedIn, Seek, Naukri):** Proprietary; raw scraping or row-level redistribution prohibited without commercial API licensing. Only official statistics, open government data, or aggregated modeling benchmarks may be stored and displayed.

#### Q10: Can the proposed data be legally stored and displayed?
**Yes**, provided:
1. Data is ingested exclusively from official statistical agencies (BLS, ONS, JSA, MOM, MOSPI) under their open government licences (CC BY 4.0, OGL v3, Singapore Open Data Licence, OGD India).
2. Data is stored as structured, versioned, aggregated statistical observations (not raw private user/posting records).
3. Clear attribution, reference periods, and methodology disclaimers accompany every display.

---

### 3. TECHNICAL RISKS & RESOURCE CONSTRAINTS

1. **Measurement Heterogeneity:**
   - US BLS measures projected annual job openings (growth + replacement).
   - Australia JSA IVI measures online job advertisement volume indices.
   - Singapore MOM measures job vacancy counts and proportion unfilled > 6 months.
   - UK ONS measures online job advert counts by SOC 2020.
   - India MOSPI PLFS measures labour force survey worker proportions by occupational division.
   - *Mitigation:* Explicit `measurement_type` enum; strict demand comparability engine; zero collapsed universal demand score.
2. **Ephemerality of Render Free Tier:**
   - Render containers do not have persistent writable storage; local writes to disk reset on deployment or container sleep.
   - *Mitigation:* Store versioned JSON datasets in repository under `src/backend/data/demand/`, loaded into in-memory registries at startup (identical to `src/backend/data/occupations/` and `src/backend/data/salary/`).
3. **Memory Footprint:**
   - Avoid loading massive multi-gigabyte raw scraping files.
   - *Mitigation:* Ingest clean, structured, verified aggregate observations (~100 to 500 KB per dataset).

---

### 4. PLANNED FILE ARCHITECTURE

#### New Files to Create:
- `src/backend/schemas/demand.py`: Pydantic models for demand observations, metrics, trends, skill requirements, shortage indicators, comparability results.
- `src/backend/services/demand_service.py`: Demand registry, time-series calculation, regional aggregation, skill gap analysis, demand comparability engine.
- `src/backend/routers/demand.py`: FastAPI router implementing `/v1/demand/*` endpoints.
- `src/backend/data/demand/`:
  - `metrics.json`: Demand metric registry with strict mathematical definitions and permitted/prohibited interpretations.
  - `sources.json`: Source provenance, licensing, and update frequencies.
  - `observations.json`: Multi-market demand observations mapped to national occupations.
  - `skill_demands.json`: Evidence-based skill requirements by occupation and market.
  - `shortage_indicators.json`: Official shortage ratings and priority status.
- `tests/test_demand_intelligence.py`: Comprehensive test suite for demand schemas, calculations, comparability, and API contracts.
- `frontend/src/pages/DemandPage.tsx`: Rich React/TypeScript demand intelligence experience.

#### Files to Safely Update (Additive Only):
- `src/backend/main.py`: Include `demand.router` under `/v1/demand` and `/api/v1/demand`.
- `src/backend/markets/registry.py`: Update `MarketCapability.DEMAND_ANALYTICS` to reflect active coverage.
- `frontend/src/types.ts`: Add TypeScript interfaces for demand data models.
- `frontend/src/services/api.ts`: Add demand API client methods.
- `frontend/src/App.tsx`: Add `/demand` route to `ROUTE_MAP` and render `DemandPage`.
- `frontend/src/components/AppHeader.tsx`: Add `Demand` navigation pill with trending chart icon.

---

### 5. PHASE 0 CONCLUSION

The repository state is clean and ready. All prerequisites are satisfied. Proceeding to Phase 1 (Official Data Source Research).
