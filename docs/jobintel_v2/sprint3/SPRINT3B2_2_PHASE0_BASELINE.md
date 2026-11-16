# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 0: BASELINE AND AUDIT RECONCILIATION

**Date:** 2026-11-16  
**Auditor / Architect:** Principal Software Architect, Data Governance Engineer & QA Lead  
**Repository:** `https://github.com/Vansh1412/Job-Market-Intelligence`  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Execution Mode:** Controlled remediation, evidence-backed disclosure hardening, regression testing.

---

## 1. Baseline Repository State

```text
Branch: staging/sprint2c3 (in sync with origin/staging/sprint2c3)
HEAD: 58974134e56b4c3ec6b6119b7b4739e9cce857f3
Master: 198b79dcdff08a5be5f08847c4262d31a3ce261e
Working Tree: 6 tracked modified files (Sprint 3B.2 uncommitted work), untracked Sprint 3B.2 and 3B.2.1 artifacts.
```

### 1.1 Tracked Modified Files
1. `frontend/src/App.tsx` (+5 lines: `/demand` route registration)
2. `frontend/src/__tests__/routing.test.ts` (+4, -1 lines: routing assertion for `/demand`)
3. `frontend/src/components/AppHeader.tsx` (+3 lines: navigation item for Demand)
4. `frontend/src/services/api.ts` (+49 lines: demand API client methods)
5. `frontend/src/types.ts` (+189 lines: demand TypeScript interfaces)
6. `src/backend/main.py` (+3 lines: demand router inclusion under `/api/v1/demand`)

### 1.2 Untracked Core Implementation Files
1. `src/backend/data/demand/` (`metrics.json`, `sources.json`, `observations.json`, `skill_demands.json`, `shortage_indicators.json`)
2. `src/backend/schemas/demand.py`
3. `src/backend/services/demand_service.py`
4. `src/backend/routers/demand.py`
5. `frontend/src/pages/DemandPage.tsx`
6. `frontend/src/__tests__/demand_contract.test.ts`
7. `tests/test_demand_intelligence.py`

### 1.3 Untracked Audit Reports
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_DATA_INVENTORY.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_RECORD_PROVENANCE_AUDIT.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_INGESTION_SCRIPT_AUDIT.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_MARKET_VALIDATION.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_SKILL_GAP_AUDIT.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_COMPARABILITY_AUDIT.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_TEST_RECONCILIATION.md`
- `docs/jobintel_v2/sprint3/SPRINT3B2_1_RELEASE_READINESS.md`

---

## 2. Sprint 3B.2.1 Audit Findings & Corrective Actions Matrix

| # | Audit Finding from Sprint 3B.2.1 | Corrective Action in Sprint 3B.2.2 | Affected Files |
|---|---|---|---|
| 1 | Provenance displayed as generic official badge without semantic distinction between directly observed, derived, and benchmark data. | Standardize 6 provenance categories with user-friendly labels and tooltip/expandable disclosures. | `src/backend/schemas/demand.py`, `src/backend/services/demand_service.py`, `frontend/src/types.ts`, `frontend/src/pages/DemandPage.tsx` |
| 2 | US state allocations represent employment-weighted derivations from OEWS, not measured spot vacancies. | Add explicit badge and disclosure: *"State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."* | `frontend/src/pages/DemandPage.tsx`, `src/backend/data/demand/observations.json` |
| 3 | Australian 6-digit OSCA occupation counts inherit from 4-digit ANZSCO IVI groups. | Add disclosure: *"Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."* | `frontend/src/pages/DemandPage.tsx`, `src/backend/data/demand/observations.json` |
| 4 | Singapore regional breakdown is a planning region proxy. | Add label `MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED` with explanatory limitations. | `frontend/src/pages/DemandPage.tsx`, `src/backend/data/demand/observations.json` |
| 5 | UK ONS / Textkernel experimental labour demand source has unresolved third-party redistribution terms. | Implement server-side publication gate: classify as `REVIEW_REQUIRED`, return `UK_DEMAND_DATA_NOT_PUBLISHED` / unavailable state on frontend without leaking restricted values. Preserve UK salary 503 independently. | `src/backend/routers/demand.py`, `src/backend/services/demand_service.py`, `frontend/src/pages/DemandPage.tsx` |
| 6 | India demand dataset is an empirical tech cluster posting sample, not an official MoSPI vacancy census. | Add prominent `CALIBRATED BENCHMARK` badge with mandatory methodology disclaimer explaining scope and limitations. | `frontend/src/pages/DemandPage.tsx`, `frontend/src/types.ts` |
| 7 | Skill gap engine must be mathematically transparent and prevent "employability probability" misinterpretations. | Explicitly document formula (matched weight / total weight * 100), explain rule-based recommendations, and enforce neutral terminology ("Skill Coverage", "Market Alignment"). | `src/backend/services/demand_service.py`, `frontend/src/pages/DemandPage.tsx` |
| 8 | Test reporting reconciliation: resolve duplicate counts and document root pytest discovery behavior. | Re-run all test suites; report deduplicated 374 unique tests; document `archive/` legacy discovery isolation. | `tests/`, `frontend/src/__tests__/`, documentation |

---

## 3. Files Permitted to Change vs. Files Strictly Frozen

### 3.1 Files Permitted to Change
- `src/backend/schemas/demand.py`: Add provenance metadata fields, licensing status enum, and disclosure models.
- `src/backend/services/demand_service.py`: Add UK publication gate check, enriched observation metadata, and disclosure helpers.
- `src/backend/routers/demand.py`: Enforce UK publication gate (`UK_DEMAND_DATA_NOT_PUBLISHED`), leak prevention.
- `src/backend/data/demand/sources.json`: Add licensing terms, rights notice, and publication status (`REVIEW_REQUIRED` for UK).
- `src/backend/data/demand/observations.json`: Ensure provenance enums and derivation metadata are explicitly recorded.
- `frontend/src/types.ts`: Update TypeScript interfaces for provenance labels, licensing gates, and regional disclosures.
- `frontend/src/pages/DemandPage.tsx`: Implement provenance badge component, expandable methodology disclosures, UK withheld state, India benchmark badge, regional warning labels, and skill formula breakdown.
- `tests/test_demand_intelligence.py`: Add automated regression tests for provenance, UK gate, India benchmark, regional disclosures, and skill gap edge cases.
- `frontend/src/__tests__/demand_contract.test.ts`: Add frontend tests for updated contracts and disclosure states.

### 3.2 Files Strictly Frozen
- `data/models/*`: All trained ML model artifacts (CatBoost, XGBoost, PCA, Scalers).
- `src/backend/services/uk_salary_service.py` & `src/backend/routers/uk_salary.py`: Existing UK salary fail-closed HTTP 503 behavior must remain completely untouched.
- `src/backend/services/salary_service.py`: Cross-market salary intelligence logic.
- Production branch `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`).

---

## 4. Phase 0 Audit Conclusion

The baseline state is verified and stable. All uncommitted Sprint 3B.2 work is mapped and preserved. We are ready to proceed with Phase 1: Standardized Provenance Model.
