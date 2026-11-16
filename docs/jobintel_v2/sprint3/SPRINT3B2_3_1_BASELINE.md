# JOBINTEL 2.0 — SPRINT 3B.2.3.1 BASELINE AUDIT REPORT
## Phase 0: Repository Baseline, Code Inspection & Defect Mapping

**Sprint:** 3B.2.3.1 (UK Publication State Serialization Remediation & Regression Verification)  
**Audit Date:** November 16, 2026  
**Auditor:** Principal Backend Architect, Pydantic v2 Specialist & API Security Auditor  
**Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Execution Mode:** Focused Semantic Remediation (Strict Remote Read-Only: 0 Git Commits, 0 Pushes, 0 Remote Deployments)  

---

### 1. REPOSITORY & COMMIT BASELINE VERIFICATION

The exact Git environment status was verified prior to any remediation:

```text
git status --short --branch
## staging/sprint2c3...origin/staging/sprint2c3
 M frontend/src/App.tsx
 M frontend/src/__tests__/routing.test.ts
 M frontend/src/components/AppHeader.tsx
 M frontend/src/services/api.ts
 M frontend/src/types.ts
 M src/backend/main.py
?? docs/jobintel_v2/sprint3/...
?? frontend/src/__tests__/demand_contract.test.ts
?? frontend/src/pages/DemandPage.tsx
?? src/backend/data/demand/
?? src/backend/routers/demand.py
?? src/backend/schemas/demand.py
?? src/backend/services/demand_service.py
?? tests/test_demand_intelligence.py

git branch --show-current: staging/sprint2c3
git rev-parse HEAD: 58974134e56b4c3ec6b6119b7b4739e9cce857f3
git rev-parse master: 198b79dcdff08a5be5f08847c4262d31a3ce261e
git rev-parse origin/master: 198b79dcdff08a5be5f08847c4262d31a3ce261e
git rev-parse origin/staging/sprint2c3: 58974134e56b4c3ec6b6119b7b4739e9cce857f3
```

- **Production Master Isolation:** Certified intact. Zero commits or diffs between local `master` and `origin/master`.
- **Staging Working Tree:** Working tree preserves the Sprint 3B.2.2 implementation and Sprint 3B.2.3 audit reports. No commits created.

---

### 2. TARGETED CODE INSPECTION & DEFECT MAPPING

The audit located every non-nullable numeric field, publication gate check, and serialization point affecting UK demand data:

| Component | File Path | Line Range | Original Implementation | Identified Defect | Required Remediation |
|---|---|---|---|---|---|
| **DemandObservation Schema** | `src/backend/schemas/demand.py` | Line 189 | `value: float` (non-nullable) | Conflates withheld state with measured zero; fails Pydantic validation if `None` is passed. | Change to `value: float | None = None`. |
| **OccupationDemandProfile Schema** | `src/backend/schemas/demand.py` | Line 219 | `primary_metric_value: float` (non-nullable) | Conflates withheld state with measured zero; fails Pydantic validation if `None` is passed. | Change to `primary_metric_value: float | None = None`. |
| **Observation List Serializer** | `src/backend/services/demand_service.py` | Lines 240–246 | `"value": 0.0` when `is_gate_active` | Injects synthetic measured zero into sanitized public response list. | Set `"value": None`. |
| **Occupation Profile Serializer** | `src/backend/services/demand_service.py` | Lines 394–400 | `metric_val = 0.0` when `is_gate_active` | Returns `0.0` in public profile payload instead of `null`. | Set `metric_val = None`. |
| **Comparability Serializer** | `src/backend/services/demand_service.py` | Lines 663–665 | `val_b = 0.0 if gate_b else obs_b.value` | Sets `metric_b.value = 0.0` in cross-market comparison payload when UK is Market B. | Set `val_b = None if gate_b else obs_b.value`. |
| **Frontend TypeScript Types** | `frontend/src/types.ts` | Lines 654, 680 | `value: number`, `primary_metric_value: number` | TypeScript types mandate `number`; fails typecheck if `null` received. | Change to `number | null`. |
| **Frontend UI Rendering** | `frontend/src/pages/DemandPage.tsx` | Line 772, Lines 864–889 | Calls `.toLocaleString()` directly; empty time-series/regional arrays render blank boxes. | Unsafe on `null`; blank charts confuse user without explicit empty state. | Implement `formatMetricValue(val, isGated)`; add explicit empty state cards. |

---

### 3. BASELINE VERDICT

```text
BASELINE INSPECTION VERDICT: DEFECT LOCATED & CONFINED
Targeted scope: 2 Pydantic schema fields, 3 service serialization branches, 2 TypeScript type definitions, and frontend UI empty states.
Zero impact on salary models, occupation concordance, or non-UK market data.
Proceeding to Phase 1: Define Semantic Publication States.
```
