# SPRINT 2C.1 TEST EXECUTION REPORT
## Comprehensive Governance Verification, Regression Invariants & Test Suite Evidence

- **Document Identifier:** `JOBINTEL-S2C1-TEST-002`
- **Execution Date:** November 13, 2026
- **Test Harness:** Pytest 8.4.2 (Python 3.13.9) | Vitest 5.0.3 (Node.js)
- **Status:** 100% PASSED (274 Backend Tests, 9 Frontend Tests)
- **Target Repository:** `e:\Job Market` | **Commit Baseline:** `198b79d` (master)

---

## 1. Test Execution Summary

The test harness executed 283 automated tests across the repository with zero failures, zero errors, and zero regressions:

```
+===================================================================================================+
|                                  TEST EXECUTION METRICS                                           |
+===================================================================================================+
|  TEST SUITE                  COMMAND                        PASSED   FAILED   TIME       STATUS   |
+---------------------------------------------------------------------------------------------------+
|  Governance Engine (New)     python -m pytest tests/test_    20       0        0.50s      PASSED   |
|                              governance_engine.py -v                                              |
|  Full Backend Suite          python -m pytest tests -q       274      0        29.40s     PASSED   |
|  Frontend Vitest Suite       npm --prefix frontend test --   9        0        0.88s      PASSED   |
|                              --run                                                                |
+---------------------------------------------------------------------------------------------------+
|  TOTAL REPOSITORY COVERAGE                                   283      0        30.78s     PASSED   |
+===================================================================================================+
```

---

## 2. Governance Engine Requirement Matrix (Tests A through T)

All 20 governance testing requirements mandated by Sprint 2C.1 were implemented in `tests/test_governance_engine.py` and passed cleanly:

| Req ID | Test Function Name | Assertion Tested | Outcome | Execution Time |
|---|---|---|---|---|
| **A** | `test_req_a_permission_state_validation` | Validates all 7 `PermissionState` enum members | PASSED | 0.01s |
| **B** | `test_req_b_unknown_permissions_denied_by_default` | Unregistered source fails closed with `GOV_DENIED_UNKNOWN_SOURCE` | PASSED | 0.01s |
| **C** | `test_req_c_conditional_permissions_with_unmet_conditions` | Unmet caveats return `CONDITIONAL` and `GOV_DENIED_CONDITIONS_UNMET` | PASSED | 0.02s |
| **D** | `test_req_d_approval_bound_to_exact_dataset_hash` | Checksum divergence triggers `GOV_DENIED_CHECKSUM_MISMATCH` | PASSED | 0.02s |
| **E** | `test_req_e_approval_invalidated_by_changed_dataset_version` | Dataset version change triggers `GOV_DENIED_VERSION_MISMATCH` | PASSED | 0.02s |
| **F** | `test_req_f_license_version_mismatch` | Divergent license version triggers `GOV_DENIED_LICENSE_VERSION_MISMATCH` | PASSED | 0.02s |
| **G** | `test_req_g_geography_and_audience_mismatch` | Outside approved geography/audience triggers scope denial | PASSED | 0.02s |
| **H** | `test_req_h_commercial_use_without_commercial_permission` | Commercial use of non-commercial approval triggers denial | PASSED | 0.02s |
| **I** | `test_req_i_expired_approval` | Lapsed temporal approval triggers `GOV_DENIED_APPROVAL_EXPIRED` | PASSED | 0.02s |
| **J** | `test_req_j_revoked_approval` | Revoked approval ID fails closed | PASSED | 0.01s |
| **K** | `test_req_k_source_wide_revocation` | Source-wide revocation halts all releases under source | PASSED | 0.02s |
| **L** | `test_req_l_release_specific_revocation` | Release revocation halts target release only | PASSED | 0.02s |
| **M** | `test_req_m_suspended_release` | Suspended lifecycle state blocks operation | PASSED | 0.02s |
| **N** | `test_req_n_model_lineage_missing_or_mismatched` | Missing lineage or Tier 1 commercial AI use denied | PASSED | 0.02s |
| **O** | `test_req_o_uk_remains_blocked_under_unresolved_permission` | UK ASHE in `REVIEW_REQUIRED` returns `GOV_DENIED_UNREVIEWED_SOURCE` | PASSED | 0.02s |
| **P** | `test_req_p_india_usa_prediction_regression` | Valid model lineage passes research inference evaluation | PASSED | 0.02s |
| **Q** | `test_req_q_malformed_manifest_isolation` | UK governance failure does NOT impair USA model evaluation | PASSED | 0.02s |
| **R** | `test_req_r_policy_cache_invalidation` | Cache invalidation updates audit timestamps | PASSED | 0.01s |
| **S** | `test_req_s_invalid_lifecycle_transitions` | State machine blocks invalid transitions and protects terminal states | PASSED | 0.02s |
| **T** | `test_req_t_url_metadata_field_validation` | Additive tripartite URLs exist and preserve `source_reference` | PASSED | 0.01s |

---

## 3. Full Backend Test Suite Log Output

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: E:\Job Market
plugins: anyio-4.10.0, hydra-core-1.3.6, typeguard-4.6.0
collected 274 items

........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
..........................................................               [100%]
274 passed in 29.40s
============================= 274 passed in 29.40s =============================
```

### Key Subsystems Verified:
1. **India & USA Golden Prediction Parity (`test_golden_predictions.py`):** All golden vectors match within $10^{-6}$ numerical tolerance.
2. **Model Artifact Integrity (`test_artifacts_integrity.py`):** All 10 model joblib artifacts match SHA-256 hashes bitwise.
3. **UK ASHE Ingestion Contracts (`test_ashe_ingestion.py`):** 4,532 grid rows, 412 SOC codes, 11 GB regions verified.
4. **UK Fail-Closed Serving (`test_uk_salary_api.py`):** All 5 UK salary routes fail closed with HTTP 503 `UK_DATA_NOT_PUBLISHED`.
5. **Zero Storage Deployment (`test_zero_storage_deployment.py`):** Readiness probes and prediction routes operate cleanly with private parquets unmounted.

---

## 4. Frontend Vitest Suite Log Output

```text
> frontend@0.0.0 test
> vitest run --run

 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/routing.test.ts (3 tests) 5ms
 ✓ src/__tests__/calculator.test.ts (3 tests) 6ms
 ✓ src/__tests__/skills_contract.test.ts (3 tests) 7ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Start at  21:08:42
   Duration  876ms
```

---

## 5. Test Regression Verdict

**VERDICT: ZERO REGRESSIONS DETECTED.**  
Every pre-existing test passed without modification. The 20 new tests seamlessly integrate with the test suite, providing comprehensive automated verification of all Sprint 2C.1 governance requirements.

