# SPRINT 3B.3.3: TEST EXECUTION REPORT
## Automated Test Results, Regression Verification & Build Evidence

**Sprint ID:** 3B.3.3  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Execution Date:** 2026-11-17  
**Overall Test Verdict:** **100% PASS (376 Backend + 20 Frontend Tests Passing)**

---

## 1. Backend Test Suite Execution

### 1.1 Full Suite Execution Evidence
- **Command:** `python -m pytest tests/`
- **Execution Duration:** 32.93 seconds
- **Platform:** Windows (Python 3.13.9, pytest-8.4.2)
- **Total Tests Collected:** 376
- **Total Passed:** **376**
- **Total Failed:** **0**
- **Total Skipped:** **0**

### 1.2 Test Module Breakdown

| Test File | Tests Passed | Focus Area |
| :--- | :--- | :--- |
| `tests/test_archetype_parity.py` | 15 | Cross-market skill clustering parity |
| `tests/test_ashe_ingestion.py` | 27 | UK ASHE official wage survey ingestion |
| `tests/test_chart_contracts.py` | 8 | Chart visualization payload schemas |
| `tests/test_cloud_contracts.py` | 6 | Cloud microservice readiness & endpoints |
| `tests/test_demand_intelligence.py` | 38 | Global demand indicators, units & UK gating |
| `tests/test_employer_resolver.py` | **5 (NEW)** | Safe entity resolution & pagination controls |
| `tests/test_end_to_end_integration.py` | 16 | End-to-end user workflows & routing |
| `tests/test_global_foundation.py` | 26 | Registry integrity & base schema validation |
| `tests/test_golden_predictions.py` | 2 | Numerical parity against certified golden profiles |
| `tests/test_governance_engine.py` | 38 | Revocation manifests & source gate enforcement |
| `tests/test_input_validation.py` | 24 | Pydantic schema validation & error trapping |
| `tests/test_market_analytics.py` | 5 | Cross-market summary distributions |
| `tests/test_occupation_intelligence.py` | 19 | National taxonomies & concordance crosswalks |
| `tests/test_prediction_parity.py` | 13 | Bitwise / floating-point prediction parity |
| `tests/test_routing_contracts.py` | 4 | REST routing rules & version prefixes |
| `tests/test_salary_intelligence.py` | 17 | Salary percentiles, PPP & FX conversions |
| `tests/test_schema_contracts.py` | 7 | JSON response schema contracts |
| `tests/test_skill_integrity.py` | 12 | Skill frequency counts & category colors |
| `tests/test_uk_salary_api.py` | 35 | UK salary routes, authentication & gating |
| `tests/test_uk_salary_service.py` | 49 | UK salary statistics & percentiles |
| `tests/test_zero_storage_deployment.py` | 10 | Ephemeral in-memory database stability |
| **TOTAL** | **376** | **Zero Regressions** |

---

## 2. Frontend Test Suite Execution

### 2.1 Vitest Unit & Contract Suite
- **Command:** `cd frontend; npm test`
- **Execution Duration:** 2.04 seconds
- **Test Framework:** Vitest v5.0.3
- **Test Files:** 5 passed
- **Total Tests:** **20 passed**
- **Total Failed:** **0**

### 2.2 Frontend Test Suite Breakdown
1. `src/__tests__/demand_contract.test.ts`: **8 passed** (Demand metric formats, UK withheld status).
2. `src/__tests__/prediction_display.test.ts`: **3 passed (NEW)** (USA base pay scope, India CTC scope, non-probability match index).
3. `src/__tests__/calculator.test.ts`: **3 passed** (USA & India payload generation).
4. `src/__tests__/skills_contract.test.ts`: **3 passed** (Skill landscape schemas).
5. `src/__tests__/routing.test.ts`: **3 passed** (Page navigation contracts).

### 2.3 Production Build Verification
- **Command:** `cd frontend; npm run build`
- **Compiler:** `tsc -b && vite build`
- **Status:** **PASS** (Zero TypeScript compilation errors; built in 480ms).
- **Bundle Output:** Cleanly generated under `frontend/dist/`.

---

## 3. Parity & Regression Invariant Sign-Off

1. **Prediction Parity:** Direct Python model execution vs FastAPI prediction endpoints maintains $< 0.05\text{ LPA}$ (India) and $< $0.10 (USA) parity.
2. **Sovereign Gating:** UK demand vacancy flow remains serialized as `null` with code `UK_DEMAND_DATA_NOT_PUBLISHED`.
3. **Database Integrity:** Zero writes to production databases or persistent stores occurred.
