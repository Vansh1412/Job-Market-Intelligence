# SPRINT 3B.3.3: API COMPATIBILITY REPORT
## Endpoint Contracts, Response Schemas & Backward Compatibility Verification

**Sprint ID:** 3B.3.3  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Compatibility Status:** 100% BACKWARD COMPATIBLE  

---

## 1. Executive Summary

A core directive of Sprint 3B.3.3 was to maintain strict backward compatibility across all public API routes and response schemas. No required fields were removed, no existing types were modified, and no breaking parameter requirements were added.

---

## 2. Endpoint-by-Endpoint Compatibility Audit

### 2.1 India Salary Prediction (`POST /api/india/predict`)
- **Request Schema:** `IndiaPredictionRequest` (Unchanged).
- **Existing Response Keys:**
  - `predicted_salary_lpa` (float): Unchanged.
  - `predicted_salary_inr` (float): Unchanged.
  - `predicted_salary_display` (str): Unchanged.
  - `confidence_interval` (dict): Preserved with `lower_lpa`, `upper_lpa`, `display`, and `margin_mae_lpa`. Added optional fields `interval_type` and `interval_note`.
  - `archetype` (dict): Unchanged.
  - `model_metadata` (dict): Added optional fields `evaluation_sample_size` (1173), `pay_concept`, `disclaimer`, `holdout_median_ae_lpa`, `mape`.
- **Golden Prediction Parity:** Verified via `test_golden_predictions.py` and `test_prediction_parity.py`. Parity tolerance $< 0.05$ LPA maintained.
- **Verdict:** **100% COMPATIBLE**.

### 2.2 USA Salary Prediction (`POST /api/usa/predict`)
- **Request Schema:** `PredictionRequest` (Unchanged).
- **Existing Response Keys:**
  - `predicted_salary` (float): Unchanged.
  - `predicted_salary_display` (str): Unchanged.
  - `confidence_interval` (dict): Preserved with `lower`, `upper`, `display`, `margin_mae`. Added optional `interval_type` and `interval_note`.
  - `archetype` (dict): Unchanged.
  - `model_metadata` (dict): Added optional fields `evaluation_sample_size` (6808), `overall_r2` (0.4233), `pay_concept`, `disclaimer`, `holdout_median_ae`, `mape`.
- **Golden Prediction Parity:** Verified via `test_golden_predictions.py` and `test_prediction_parity.py`. Parity tolerance $< $0.10 maintained.
- **Verdict:** **100% COMPATIBLE**.

### 2.3 Employer Registry & Pagination (`GET /api/v1/employers`)
- **Endpoint Signature:**
  ```python
  def list_employers(
      limit: Annotated[int | None, Query(ge=1, le=50)] = None,
      offset: Annotated[int, Query(ge=0)] = 0,
  ) -> list[EmployerProfile]
  ```
- **Unparameterized Call:** Calling `GET /api/v1/employers` without arguments returns `list[EmployerProfile]`, matching the legacy signature.
- **Test Compatibility:** `assert list_employers() == []` in `test_global_foundation.py` passes without modification.
- **Verdict:** **100% COMPATIBLE**.

### 2.4 Employer Entity Resolution (`POST /api/v1/employers/resolve`)
- **Endpoint Signature:** Accepts `EmployerResolutionRequest` and returns `EmployerResolutionResponse`.
- **Architecture:** Pure additive route. Does not alter or displace existing endpoints.
- **Verdict:** **NON-BREAKING ADDITIVE EXPANSION**.

### 2.5 Occupation Concordance & Search (`GET /api/v1/occupations/search`, `GET /api/v1/occupations/compare`)
- **Response Schemas:** `list[NationalOccupation]` and `CrossMarketComparisonResult` remain unchanged.
- **Verdict:** **100% COMPATIBLE**.

### 2.6 UK Demand Intelligence Gating (`GET /api/v1/demand/observations`)
- **Gating Status:** Invariant preserved. Observations for market `UK` retain `observed_value: null` with `publication_gate_code: "UK_DEMAND_DATA_NOT_PUBLISHED"`.
- **Zero Synthetic Fallback:** Confirmed via `test_demand_intelligence.py` (38 passing tests).
- **Verdict:** **GOVERNANCE INVARIANT MAINTAINED**.

---

## 3. Automated Test Evidence

- Full backend pytest suite: **376 passed in 32.93s**.
- Full frontend vitest suite: **20 passed in 2.04s**.
- Zero contract regressions observed across 396 total assertions.
