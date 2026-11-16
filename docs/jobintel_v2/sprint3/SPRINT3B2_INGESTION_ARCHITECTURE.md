# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 INGESTION ARCHITECTURE: GLOBAL JOB DEMAND INTELLIGENCE

**Document ID:** `SPRINT3B2_INGESTION_ARCHITECTURE`  
**Milestone:** Sprint 3B.2 — Phase 3 & 4 Ingestion Architecture  
**Date:** 2026-11-16  
**Auditor / Authors:** Principal Data Engineer, Backend Architect, Release Governance Lead  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  

---

### 1. ARCHITECTURE OVERVIEW

The Job Demand Intelligence ingestion pipeline is engineered to ingest, validate, index, and serve descriptive occupational demand statistics across five international labour markets (USA, Australia, United Kingdom, Singapore, and India).

Because the platform operates in a containerized environment (Render Free Tier) characterized by **ephemeral filesystem storage**, the architecture rejects mutable local sqlite/flat-file write patterns in favor of **immutable, version-controlled JSON datasets** checked directly into git.

```
   [Official Data Sources]
   - US BLS Projections & O*NET
   - AU JSA IVI & SPL 2024
   - UK ONS Online Adverts & ISL
   - SG MOM Vacancies & SSG ICT
   - IN MOSPI PLFS & JobIntel Benchmark
             │
             ▼
   [Validation & Schema Enforcement]
   - Pydantic v2 Models (DemandObservation, DemandTimeSeriesPoint, etc.)
   - Non-collapsibility Assertions
   - Reference Period ISO Validation
             │
             ▼
   [Git-Tracked Immutable Storage]
   - src/backend/data/demand/metrics.json
   - src/backend/data/demand/sources.json
   - src/backend/data/demand/observations.json
   - src/backend/data/demand/skill_demands.json
   - src/backend/data/demand/shortage_indicators.json
             │
             ▼
   [Application Startup (FastAPI Lifespan)]
   - DemandService in-memory indexer
   - O(1) Lookups by (market_id, occupation_id, canonical_id)
   - Pre-computed trend & comparability caches
             │
             ▼
   [Demand API Endpoints]
   - /v1/demand/markets
   - /v1/demand/occupations
   - /v1/demand/compare
   - /v1/demand/skills/gaps
```

---

### 2. DATASET INVENTORY & DIRECTORY STRUCTURE

All demand datasets reside under `src/backend/data/demand/`:

1. `metrics.json`:
   Contains the catalog of 7 official `DemandMetricType` definitions, documenting display names, units, descriptions, underlying constructs, limitations, and comparability classes.
2. `sources.json`:
   Records source provenance for the 10 contributing data sources, including publisher agency, canonical URL, legal license (Public Domain, CC BY 4.0, OGL v3, SG Open Data, GODL India), update frequency, and reliability tier.
3. `observations.json`:
   Contains 28 atomic demand observation records linking national occupations across US, AU, UK, SG, and IN to empirical demand values, time-series points, regional distributions, and entry requirements.
4. `skill_demands.json`:
   Maintains curated skill matrices across the 12 canonical concepts, categorizing skills into 8 technical domains with importance scores, posting frequencies, and emerging "hot skill" flags.
5. `shortage_indicators.json`:
   Captures official government shortage classifications, state-level shortages, and recruitment tightness metrics (e.g., Singapore MOM % unfilled > 6 months).

---

### 3. VALIDATION RULES & INTEGRITY CONSTRAINTS

Prior to committing data or loading into the service registry, the pipeline validates:

1. **Referential Integrity:**
   - Every `observation.market_id` must match a valid `MarketId` (`US`, `AU`, `UK`, `SG`, `IN`).
   - Every `observation.occupation_id` must match a known national occupation in `national_occupations.json`.
   - Every `observation.canonical_id` (if present) must exist in `canonical_occupations.json`.
   - Every `observation.source_id` must be present in `sources.json`.
2. **Numeric Sanity Bounds:**
   - `importance_score` $\in [0.0, 100.0]$.
   - `frequency_percentage` $\in [0.0, 100.0]$.
   - `share_percentage` across regional breakdown $\approx 100.0$ (or subtotal of top regions $\le 100.0$).
   - `value` $\ge 0.0$ (negative vacancy counts are strictly rejected).
3. **Time-Series Monotonicity:**
   - Time-series periods must follow standard ordering (`YYYY-QX` or `YYYY`).
4. **Governance Isolation:**
   - UK salary fail-closed behavior (enforced in `uk_salary_service.py` via HTTP 503) must not be weakened or circumvented by demand endpoints. Demand data for UK (ONS advert volume index) is strictly segregated from salary data.

---

### 4. MEMORY FOOTPRINT & STARTUP BENCHMARKS

- Total raw JSON size: $\sim 65 \text{ KB}$.
- Parsing and indexing time at application startup: $< 15 \text{ ms}$.
- Memory overhead in container RAM: $< 2.5 \text{ MB}$.
- Ephemeral tolerance: Since datasets are checked into git and deployed as part of the application slug, container sleep, redeployment, and horizontal scaling introduce zero state drift.
