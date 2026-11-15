# SPRINT 2C.2.2 — TASK 2: UK ROUTE AND DUAL-LAYER GATE VERIFICATION

**Document:** `SPRINT2C2_2_UK_GATE_VERIFICATION.md`  
**Author:** Principal Software Architect, Senior Backend Engineer, QA Lead  
**Date:** November 13, 2026  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Repository:** `e:\Job Market` (`master` branch)

---

## 1. EXACT REGISTERED UK SALARY ENDPOINTS

A comprehensive route audit of `app.routes` in `src/backend/main.py` confirmed that the UK salary endpoints are mounted via `app.include_router(uk_salary.router, prefix="/api")`, where `uk_salary.router` defines `prefix="/v1/markets/UK/salary"`.

The exact, authoritative registered paths for all five UK salary endpoints are:

| # | HTTP Method | Exact Registered Route Path | Handler Function | Response Model |
|---|:---:|---|---|---|
| **1** | `GET` | `/api/v1/markets/UK/salary/occupations` | `list_occupations` | `UKOccupationPage` |
| **2** | `GET` | `/api/v1/markets/UK/salary/occupations/{soc_code}` | `get_occupation` | `UKOccupationDetail` |
| **3** | `GET` | `/api/v1/markets/UK/salary/occupations/{soc_code}/regions` | `compare_occupation_regions` | `UKRegionComparison` |
| **4** | `GET` | `/api/v1/markets/UK/salary/regions/{region}/occupations` | `list_region_occupations` | `UKRegionOccupationPage` |
| **5** | `GET` | `/api/v1/markets/UK/salary/metadata` | `get_uk_salary_metadata` | `UKSalaryMetadata` |

### 1.1 Historical Documentation Reconciliation
In early Phase 2 exploratory architecture notes, routes were occasionally referenced with shorthand paths (e.g., `/api/v1/salary/uk/status` or `/salary/uk/occupations`). 

The canonical, production-registered prefix is `/api/v1/markets/UK/salary`, aligning with the REST API standard for multi-market intelligence (`/api/v1/markets/{market}/salary/*`). All documentation in `docs/jobintel_v2/` is now reconciled to these exact five registered routes.

---

## 2. DUAL-LAYER GOVERNANCE ARCHITECTURE

The UK descriptive salary pipeline implements a dual-layer defense-in-depth gate. Execution halts at the earliest failing layer:

```
Request to /api/v1/markets/UK/salary/*
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: Authoritative Governance Policy Engine                │
│ (src/backend/governance/service.py + engine.py)                 │
│ - Pre-flight Revocation Check: engine.check_revocation(SOURCE) │
│ - Revocation Registry Health Check: is_healthy == True          │
│ - Policy Gate: verify_uk_salary_governance()                    │
│   Checks: source_id="uk.ons.ashe", op=PUBLIC_AGGREGATE_DISPLAY  │
│   Source Status: REVIEW_REQUIRED -> allowed=False               │
│ - Result: Raises HTTP 503 UK_DATA_NOT_PUBLISHED                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │ (Only proceeds if Layer 1 APPROVED)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: Physical & Manifest Catalog Gate                       │
│ (src/backend/routers/uk_salary.py)                              │
│ - Manifest Presence & JSON Syntax Validation                    │
│ - Manifest Processing Mode: PUBLICATION_APPROVED                │
│ - Catalog vs Manifest Geography & Period Integrity Match       │
│ - Physical Dataset SHA-256 Checksum Match                       │
│ - Dual-Custody Approval Signature Verification                  │
│ - Result: Raises HTTP 503 UK_DATA_NOT_PUBLISHED or UNAVAILABLE  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ (Only proceeds if Layer 2 VALIDATED)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Lazy Load: UKSalaryService (NEVER REACHED IN UNAPPROVED STATE) │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPREHENSIVE TEST MATRIX & EVIDENCE

All required gate conditions were tested in `tests/test_uk_salary_api.py`.

### 3.1 Gating Conditions Test Results

| Test Condition | Governance Layer Tested | Test Method / Fixture | Observed Result | Verdict |
|---|:---:|---|---|:---:|
| **Real Unmodified State** | Layer 1 | `test_task2_layer1_blocks_real_publication_state` | All 5 routes return HTTP 503 `UK_DATA_NOT_PUBLISHED`; zero salary fields in body. | **PASS** |
| **Unapproved Catalog** | Layer 1 | `test_real_publication_dependency_denies_...[review_required_local]` | HTTP 503 `UK_DATA_NOT_PUBLISHED`. | **PASS** |
| **Revoked Source (Layer 1)** | Layer 1 | `test_task2_layer1_revocation_blocks_when_layer2_satisfied` | With Layer 2 fully satisfied via `published_fixture`, Layer 1 revocation immediately returns HTTP 503 `UK_DATA_NOT_PUBLISHED`. | **PASS** |
| **Degraded Revocation Registry** | Layer 1 | `test_task2_layer1_degraded_registry_blocks_when_layer2_satisfied` | With Layer 2 fully satisfied, an unverified registry immediately blocks request with HTTP 503 `UK_DATA_NOT_PUBLISHED`. | **PASS** |
| **Unapproved Manifest** | Layer 2 | `test_real_publication_dependency_denies_...[approved_wrong_use]` | Layer 1 passed; Layer 2 fails closed with HTTP 503. | **PASS** |
| **Invalid Checksum** | Layer 2 | `test_task2_layer2_blocks_when_layer1_satisfied` | Layer 1 passed; Layer 2 checksum mismatch fails with HTTP 503 `UK_DATA_UNAVAILABLE`. | **PASS** |
| **Source-Reference Mismatch** | Layer 2 | `test_real_publication_dependency_denies_...[approved_source_reference_mismatch]` | Layer 1 passed; catalog reference mismatch fails with HTTP 503. | **PASS** |
| **Missing Approval Record** | Layer 2 | `test_real_publication_dependency_denies_...[approved_missing_record]` | Layer 1 passed; missing approval in manifest fails with HTTP 503. | **PASS** |
| **Synthetic Valid Approval** | Layer 1 + 2 | `test_real_publication_dependency_passes_complete_isolated_approval` | Both Layer 1 and 2 satisfied in isolated test harness; returns HTTP 200 with valid metadata. | **PASS** |

### 3.2 Verification of Critical Safety Invariants

1. **Independent Layer Enforcement:** 
   - When Layer 1 fails, execution aborts before any Layer 2 file reads or checksum calculations.
   - When Layer 1 is satisfied in tests (`published_fixture`), Layer 2 independently blocks any defect in manifest structure, signature, or file checksum.
   - Even when Layer 2 is fully valid, a Layer 1 revocation immediately blocks the request.
2. **Zero Service Loading:**
   - In `test_every_endpoint_fails_closed_without_salary_leakage`, a monkeypatched `get_uk_salary_service` asserts that it is never called. Call list remained strictly `[]`.
3. **Zero Observation Leakage:**
   - Response payloads on denied requests strictly contain error details (`code: "UK_DATA_NOT_PUBLISHED"`, `message: "UK salary analytics are not currently published."`).
   - String scans across response bodies confirm no occurrences of `annual_gross_median_gbp`, `percentile_`, `sample_size`, or raw figures.
4. **Real State Invariance:**
   - The authoritative data catalog in `src/backend/data_catalog/registry.py` retains `publication_approved = False` and `reuse_review_status = REVIEW_REQUIRED` for `uk.ons.ashe`. No production metadata was modified.

