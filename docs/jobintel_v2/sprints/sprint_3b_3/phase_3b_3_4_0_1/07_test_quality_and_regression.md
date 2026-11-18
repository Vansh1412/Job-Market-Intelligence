# 07. Test Quality & Regression Verification Report

## 1. Test Suite Summary

To independently verify the stability, contract safety, and non-regression of the codebase, the entire automated test suite was executed across both frontend and backend stacks.

| Test Suite | Framework | Total Tests | Passed | Failed | Errors | Duration |
|---|---|---|---|---|---|---|
| **Backend Suite** | `pytest 8.4.2` | 407 | 407 | 0 | 0 | 19.08s |
| **Frontend Suite** | `Vitest 5.0.3` | 42 | 42 | 0 | 0 | 2.76s |
| **Production Build** | `Vite 5.4.21` + `tsc` | 2,894 modules | Built clean | 0 | 0 | 46.26s |
| **Browser Qualification** | `Puppeteer / Chrome` | 5 checks | 5 passed | 0 | 0 | 6.80s |

---

## 2. Backend Pytest Execution Evidence (407 Tests)

Command: `python -m pytest tests/`
Exit Code: `0`

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: E:\Job Market
plugins: anyio-4.10.0, hydra-core-1.3.6, typeguard-4.6.0
collected 407 items

tests\test_archetype_parity.py ...............                           [  3%]
tests\test_ashe_ingestion.py ...........................                 [ 10%]
tests\test_chart_contracts.py ........                                   [ 12%]
tests\test_cloud_contracts.py ......                                     [ 13%]
tests\test_demand_intelligence.py ...................................... [ 23%]
tests\test_employer_resolver.py ................................         [ 30%]
tests\test_end_to_end_integration.py ................                    [ 34%]
tests\test_global_foundation.py ..........................               [ 41%]
tests\test_golden_predictions.py ..                                      [ 41%]
tests\test_governance_engine.py ......................................   [ 51%]
tests\test_input_validation.py ........................                  [ 57%]
tests\test_market_analytics.py .....                                     [ 58%]
tests\test_occupation_intelligence.py ...................                [ 62%]
tests\test_prediction_parity.py .............                            [ 66%]
tests\test_routing_contracts.py ....                                     [ 67%]
tests\test_salary_intelligence.py .................                      [ 71%]
tests\test_schema_contracts.py .......                                   [ 72%]
tests\test_skill_denominator_integrity.py ....                           [ 73%]
tests\test_skill_integrity.py ............                               [ 76%]
tests\test_uk_salary_api.py ...................................          [ 85%]
tests\test_uk_salary_service.py ........................................ [ 95%]
tests\test_zero_storage_deployment.py ..........                         [100%]

============================ 407 passed in 19.08s =============================
```

### Key Sub-Suite Highlights
- `test_employer_resolver.py`: 32 tests verifying statutory ID parsing (SEC CIK, MCA CIN, Companies House CRN), collision defenses, null handling, and canonical matching.
- `test_uk_salary_service.py` & `test_uk_salary_api.py`: 79 tests ensuring the UK salary gate, percentile interpolations, and ASHE ingestion remain 100% operational.
- `test_skill_denominator_integrity.py`: 4 tests validating that denominator repairs from Sprint 3B.3.3.2 remain intact.

---

## 3. Frontend Vitest Execution Evidence (42 Tests)

Command: `cd frontend; npx vitest run`
Exit Code: `0`

```
 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/skills_contract.test.ts (3 tests) 4ms
 ✓ src/__tests__/routing.test.ts (3 tests) 3ms
 ✓ src/__tests__/prediction_display.test.ts (4 tests) 3ms
 ✓ src/__tests__/demand_contract.test.ts (8 tests) 6ms
 ✓ src/__tests__/calculator.test.ts (3 tests) 4ms
 ✓ src/__tests__/employers_contract.test.ts (14 tests) 7ms
 ✓ src/__tests__/employers_ui.test.tsx (7 tests) 1067ms

 Test Files  7 passed (7)
      Tests  42 passed (42)
   Duration  2.76s
```

### New Test Coverage Breakdown
- `src/__tests__/employers_contract.test.ts` (14 tests):
  - Enum value validity.
  - Request/response payload construction.
  - Preservation of `resolved_company_id: null` under statutory collisions.
  - Symmetrical separation of parent/subsidiary entities.
  - String similarity score disclosure semantics.
  - Non-fabrication guarantee for unverified fields.
- `src/__tests__/employers_ui.test.tsx` (7 tests):
  - Header, title, and governance card rendering.
  - Tab switching (Entity Resolution, Registry Explorer, Statutory Standards).
  - Sovereign authority table rendering in Standards tab.
  - Form validation on required candidate name.
  - Resolution search and candidate card presentation.
  - Amber collision alert and fail-closed state rendering.
  - Empty registry state rendering when 0 records exist.

---

## 4. Frontend Production Build Verification

Command: `cd frontend; npm run build`
Output:
```
vite v5.4.21 building for production...
transforming...
✓ 2894 modules transformed.
rendering chunks...
computing chunk sizes...
dist/index.html                   2.14 kB │ gzip:   0.84 kB
dist/assets/index-BbHj4w1s.css   38.41 kB │ gzip:   7.22 kB
dist/assets/index-DeX119a0.js   892.41 kB │ gzip: 264.12 kB
✓ built in 46.26s
```
- **Build Status**: Passed with 0 errors and 0 type warnings.
- The new code compiles cleanly under TypeScript strict mode (`tsc -b`).
