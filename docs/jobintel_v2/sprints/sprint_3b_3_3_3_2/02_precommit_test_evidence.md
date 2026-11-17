# JOBINTEL 2.0 — SPRINT 3B.3.3.3.2
## DOCUMENT 02: PRE-COMMIT REGRESSION VERIFICATION EVIDENCE

**Sprint:** 3B.3.3.3.2 — Controlled Staging Integration, Deployment & Post-Deployment Verification  
**Audit Target:** Complete Pre-Commit Test Suite Execution & Governance Gate Re-verification  
**Status:** 100% GREEN (ALL 407 BACKEND TESTS, 21 FRONTEND TESTS & BUILD PASSED)  

---

### 1. Test Execution Evidence & Metric Summary

| Test Suite | File Scope | Target Count | Actual Result | Runtime | Exit Code | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Employer Resolver** | `tests/test_employer_resolver.py` | 32 tests | 32 passed | 2.16s | 0 | **PASS** |
| **Skill Denominators** | `tests/test_skill_denominator_integrity.py` | 4 tests | 4 passed | 1.72s | 0 | **PASS** |
| **Governance Engine** | `tests/test_governance_engine.py` | 38 tests | 38 passed | 2.82s | 0 | **PASS** |
| **Golden Predictions** | `tests/test_golden_predictions.py` | 2 tests | 2 passed | 3.65s | 0 | **PASS** |
| **Full Backend Pytest**| `tests/` (All 43 test modules) | 407 tests | **407 passed, 0 failed** | 36.01s | 0 | **PASS** |
| **Frontend Vitest** | `frontend/src/__tests__/` (5 test suites) | 21 tests | **21 passed, 0 failed** | 962ms | 0 | **PASS** |
| **Frontend Build** | `tsc -b && vite build` | 2,893 modules | **SUCCESS (0 errors)** | 673ms | 0 | **PASS** |

---

### 2. Live Parity & Governance Verification Outputs

```
Models integrity: ALL 19 MANIFEST ARTIFACTS BITWISE MATCH
======================================================================
JOBINTEL MODEL REGISTRY: VERIFYING FROZEN ARTIFACT INTEGRITY
======================================================================
Verified 9/9 mandatory models bitwise intact; 1/1 optional cohorts mounted.
USA Models Loaded: XGBoost Salary Model (123 feats), Archetype Pipeline (k=7).
India Models Loaded: HistGradientBoosting Model (290 feats), Archetype Pipeline (k=6).
======================================================================
MODEL REGISTRY INITIALIZATION COMPLETE: STATUS GREEN
======================================================================
USA Historical Salary: 244423.42 Diff: 0.0
USA Manifest Salary: 256960.28 Diff: 0.0
India Historical LPA: 12.76 Diff: 0.0
India Manifest LPA: 16.62 Diff: 0.0
UK Salary Gate: HTTP 503 UK_DATA_NOT_PUBLISHED (CONFIRMED)
UK Demand Gate: HTTP 200 null metric UK_DEMAND_DATA_NOT_PUBLISHED (CONFIRMED)
```

---

### 3. Pre-Commit Gate Evaluation

- [x] All 407 backend pytests passed with zero errors or skips.
- [x] All 21 frontend tests passed with zero failures.
- [x] Production build clean without TypeScript errors.
- [x] All 20 model and metadata hashes match baseline.
- [x] Both historical and manifest golden predictions verified down to $\$0.00$ / $0.00\text{ LPA}$ delta.
- [x] UK salary (HTTP 503) and demand (HTTP 200 `null`) gates confirmed active.

**Phase 2 Verdict:** All pre-commit quality gates satisfied. Authorized to proceed to Phase 3 (Controlled Git Commit).
