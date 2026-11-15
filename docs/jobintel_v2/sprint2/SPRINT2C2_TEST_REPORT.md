# SPRINT 2C.2 TEST EXECUTION REPORT
## Comprehensive Verification of Corrective Fixes, Application Integration, Hierarchy & Regression Invariants

- **Document Identifier:** `JOBINTEL-S2C2-TEST-002`
- **Execution Date:** November 13, 2026
- **Test Harness:** Pytest 8.4.2 (Python 3.13.9) | Vitest 5.0.3 (Node.js)
- **Status:** 100% PASSED (282 Backend Tests, 9 Frontend Tests — 291 Total)
- **Target Repository:** `e:\Job Market` | **Commit Baseline:** `198b79d` (master)

---

## 1. Test Suite Summary Table

```
+===================================================================================================+
|                                    TEST EXECUTION METRICS                                         |
+===================================================================================================+
|  TEST SUITE                  COMMAND                        PASSED   FAILED   TIME       STATUS   |
+---------------------------------------------------------------------------------------------------+
|  Governance Engine (2C.2)    python -m pytest tests/test_    28       0        2.33s      PASSED   |
|                              governance_engine.py -v                                              |
|  UK Salary API & Gating      python -m pytest tests/test_    31       0        5.58s      PASSED   |
|                              uk_salary_api.py -v                                                  |
|  Golden Prediction Parity    python -m pytest tests/test_    8        0        4.08s      PASSED   |
|                              cloud_contracts.py tests/test_                                       |
|                              golden_predictions.py -v                                             |
|  ASHE Ingestion Contracts    python -m pytest tests/test_    27       0        3.97s      PASSED   |
|                              ashe_ingestion.py -q                                                 |
|  Full Backend Test Suite     python -m pytest tests -q       282      0        18.03s     PASSED   |
|  Frontend Vitest Suite       npm --prefix frontend test --   9        0        0.80s      PASSED   |
|                              --run                                                                |
+---------------------------------------------------------------------------------------------------+
|  TOTAL REPOSITORY SUITE                                      291      0        20.36s     PASSED   |
+===================================================================================================+
```

---

## 2. Governance Engine Requirement Matrix (28 Tests)

All 20 baseline requirements (A through T) and all 8 Sprint 2C.2 corrective requirements passed cleanly:

| Test Name | Focus Area / Requirement | Verified Outcome | Duration |
|---|---|---|---|
| `test_req_a_permission_state_validation` | Req A: PermissionState enums | All 7 states validated | 0.01s |
| `test_req_b_unknown_permissions_denied_by_default` | Req B: Fail-closed unreviewed | `GOV_DENIED_UNKNOWN_SOURCE` | 0.01s |
| `test_req_c_conditional_permissions_with_unmet_conditions` | Req C: Caveat requirements | `GOV_DENIED_CONDITIONS_UNMET` | 0.02s |
| `test_req_d_approval_bound_to_exact_dataset_hash` | Req D: Artifact checksum | `GOV_DENIED_CHECKSUM_MISMATCH` | 0.02s |
| `test_req_e_approval_invalidated_by_changed_dataset_version` | Req E: Dataset version | `GOV_DENIED_VERSION_MISMATCH` | 0.02s |
| `test_req_f_license_version_mismatch` | Req F: License versioning | `GOV_DENIED_LICENSE_VERSION_MISMATCH` | 0.02s |
| `test_req_g_geography_and_audience_mismatch` | Req G: Geo and audience scope | `GOV_DENIED_GEOGRAPHY_MISMATCH` | 0.02s |
| `test_req_h_commercial_use_without_commercial_permission` | Req H: Commercial restriction | `GOV_DENIED_COMMERCIAL_RESTRICTION` | 0.02s |
| `test_req_i_expired_approval` | Req I: Temporal expiry | `GOV_DENIED_APPROVAL_EXPIRED` | 0.02s |
| `test_req_j_revoked_approval` | **F-01/F-02: Approval Revocation** | `GOV_DENIED_APPROVAL_REVOKED` (via engine) | 0.02s |
| `test_req_k_source_wide_revocation` | Req K: Source kill-switch | `GOV_DENIED_REVOKED_SOURCE` | 0.02s |
| `test_req_l_release_specific_revocation` | Req L: Release kill-switch | `GOV_DENIED_REVOKED_RELEASE` | 0.02s |
| `test_req_m_suspended_release` | Req M: Suspended lifecycle | `GOV_DENIED_RELEASE_SUSPENDED` | 0.02s |
| `test_req_n_model_lineage_missing_or_mismatched` | Req N: Lineage integrity | Missing lineage & commercial blocked | 0.02s |
| `test_req_o_uk_remains_blocked_under_unresolved_permission` | Req O: UK review state | `GOV_DENIED_UNREVIEWED_SOURCE` | 0.02s |
| `test_req_p_india_usa_prediction_regression` | Req P: Prediction policy | Research inference allowed under Tier 1 | 0.02s |
| `test_req_q_malformed_manifest_isolation` | Req Q: Multi-market isolation | UK corruption isolated from US | 0.02s |
| `test_req_r_policy_cache_invalidation` | **F-02: Decision Flip Test** | Policy flips from ALLOWED to REVOKED | 0.02s |
| `test_req_s_invalid_lifecycle_transitions` | Req S: Lifecycle state machine | Terminal REVOKED protected; jumps blocked | 0.01s |
| `test_req_t_url_metadata_field_validation` | Req T: Tripartite URLs | Additive URLs populated, reference intact | 0.01s |
| `test_f07_dataset_scope_revocation_affects_all_releases` | **F-07: Dataset Scope** | Revoking dataset revokes rel1 and rel2 | 0.02s |
| `test_f07_release_scope_revocation_isolates_target_release` | **F-07: Sibling Isolation** | Rel1 revoked; Rel2 allowed | 0.02s |
| `test_f07_source_revocation_overrides_all_lower_level_approvals`| **F-07: Scope Precedence** | Source revocation overrides approval | 0.02s |
| `test_f07_model_scope_revocation` | **F-07: Model Scope** | Model revocation halts model inference | 0.02s |
| `test_f03_lifecycle_serving_state_matrix` | **F-03: Lifecycle Matrix** | All 7 lifecycle states tested for serving | 0.03s |
| `test_f06_revocation_persistence_manifest_loading` | **F-06: Manifest Loading** | Valid load, missing fallback, corrupt fallback | 0.02s |
| `test_f05_training_entrypoint_governance_blocks` | **F-05: Training Gates** | India and US training halts with PermissionError | 0.04s |
| `test_f04_application_integration_service` | **F-04: App Integration** | UK 503 fail-closed; US/IN inference recorded | 0.03s |

---

## 3. Full Backend Test Suite Output Log

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: E:\Job Market
plugins: anyio-4.10.0, hydra-core-1.3.6, typeguard-4.6.0
collected 282 items

........................................................................ [ 25%]
........................................................................ [ 51%]
........................................................................ [ 76%]
..................................................................       [100%]
============================= 282 passed in 18.03s =============================
```

---

## 4. Frontend Vitest Output Log

```text
> frontend@0.0.0 test
> vitest run --run

 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/routing.test.ts (3 tests) 3ms
 ✓ src/__tests__/calculator.test.ts (3 tests) 4ms
 ✓ src/__tests__/skills_contract.test.ts (3 tests) 3ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Start at  22:11:03
   Duration  804ms
```

---

## 5. Verification Sign-Off

- **Tests Added:** 8 new integration and negative test cases.
- **Tests Broken:** 0.
- **Tests Weakened:** 0.
- **Test Invariants:** All existing tests continue to assert strict numerical tolerances ($10^{-6}$), exact checksums, and HTTP 503 fail-closed responses.

