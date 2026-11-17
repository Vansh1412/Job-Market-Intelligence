# SPRINT 3B.3.3.1: SALARY INTERVAL CONTRACT & DISPERSION AUDIT
## Critical Forensic Investigation: API Schemas, Interval Semantics & Presentation Contracts

**Sprint ID:** 3B.3.3.1  
**Audit Target:** Salary prediction response contract, dispersion properties, and UI presentation  
**Auditor:** Independent Principal Engineer & API Contract Reviewer  
**Audit Date:** 2026-11-17  
**Finding Verdict:** **VERIFIED WITH LIMITATIONS (API ENVELOPE AMBIGUITY / UI COMPLIANT)**

---

## 1. Executive Summary

This audit examined every occurrence of `confidence_interval`, `empirical_mae_dispersion`, `holdout_median_ae`, and `holdout_median_ae_lpa` across the backend services, schemas, API endpoints, test suites, and frontend rendering logic.

**Core Findings:**
1. **Frontend Presentation (Clean & Compliant):**
   - The frontend UI (`PredictorPage.tsx`) does **NOT** display any range, interval, or probability claim.
   - The UI presents a singular **point estimate** (`$185,000` / `₹14.25 LPA`), dedicated scope notices (Base Salary vs CTC Midpoint), and explicit holdout error metrics ($N$, MAE, Median AE, $R^2$).
   - The UI explicitly states: *"JOBINTEL reports verified point estimates with empirical error metrics rather than uncalibrated probability intervals."*
2. **Backend API Contract (Ambiguous Envelope):**
   - In both `src/backend/services/usa_service.py` and `src/backend/services/india_service.py`, the JSON payload continues to return a top-level dictionary key named **`confidence_interval`**.
   - Although Sprint 3B.3.3 added `"interval_type": "empirical_mae_dispersion"` and an explicit explanatory note within that dictionary, retaining the outer key `"confidence_interval"` with `"lower"`, `"upper"`, and `"display"` risks misleading external API consumers into treating an empirical error band ($pred \pm MAE$) as a calibrated statistical confidence interval.

---

## 2. Occurrence Trace & Codebase Audit

### 2.1 Trace Matrix of Audited Identifiers

| Identifier | Location | Role in Codebase |
| :--- | :--- | :--- |
| `confidence_interval` | `src/backend/services/usa_service.py:261` | Dictionary key in live USA prediction response payload. |
| `confidence_interval` | `src/backend/services/india_service.py:304` | Dictionary key in live India prediction response payload. |
| `confidence_interval` | `frontend/src/types.ts:201` | Optional property in TypeScript `PredictionResult` interface. |
| `empirical_mae_dispersion` | `src/backend/services/usa_service.py:266` | Value of `interval_type` tag in USA response. |
| `empirical_mae_dispersion` | `src/backend/services/india_service.py:309` | Value of `interval_type` tag in India response. |
| `holdout_median_ae` | `src/backend/services/usa_service.py:282` | Numeric metadata property (`26384.22`) in USA model metadata. |
| `holdout_median_ae_lpa` | `src/backend/services/india_service.py:326` | Numeric metadata property (`2.08`) in India model metadata. |
| `holdout_median_ae_lpa` | `src/backend/services/india_service.py:26` | Module constant `INDIA_MODEL_MEDIAN_AE_LPA = 2.08`. |

---

## 3. Actual API Payload Examples

### 3.1 USA Live Prediction Response Payload (`POST /api/predict/usa`)
```json
{
  "country": "USA",
  "currency": "USD",
  "currency_symbol": "$",
  "predicted_salary": 185000.0,
  "predicted_salary_display": "$185,000",
  "confidence_interval": {
    "lower": 148619.36,
    "upper": 221380.64,
    "display": "$148,619 - $221,381",
    "margin_mae": 36380.64,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  },
  "baseline_salary": 180413.0,
  "delta_vs_baseline": 4587.0,
  "pct_vs_baseline": 2.5,
  "model_metadata": {
    "model_name": "XGBoost Regressor (Tuned)",
    "feature_count": 123,
    "overall_mae": 36380.64,
    "overall_rmse": 51082.06,
    "overall_r2": 0.4233,
    "evaluation_sample_size": 6808,
    "holdout_median_ae": 26384.22,
    "mape": 21.71,
    "pay_concept": "Estimated Annual Base Salary (Excludes RSUs, Bonuses, and Equity)",
    "disclaimer": "Historical holdout MAE does not guarantee accuracy for any individual prediction. Excludes equity grants, RSUs, and variable bonuses."
  }
}
```

### 3.2 India Live Prediction Response Payload (`POST /api/india/predict`)
```json
{
  "country": "India",
  "currency": "INR",
  "currency_symbol": "₹",
  "predicted_salary_lpa": 14.25,
  "predicted_salary_inr": 1425000.0,
  "predicted_salary_display": "₹14.25 LPA",
  "predicted_salary_inr_display": "₹1,425,000",
  "confidence_interval": {
    "lower_lpa": 10.54,
    "upper_lpa": 17.96,
    "display": "₹10.54 - ₹17.96 LPA",
    "margin_mae_lpa": 3.71,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  },
  "baseline_salary_lpa": 10.0,
  "baseline_salary_inr": 1000000.0,
  "delta_vs_baseline_lpa": 4.25,
  "pct_vs_baseline": 42.5,
  "model_metadata": {
    "model_name": "HistGradientBoostingRegressor",
    "feature_count": 290,
    "overall_mae_lpa": 3.71,
    "overall_rmse_lpa": 6.22,
    "overall_r2": 0.5798,
    "evaluation_sample_size": 1173,
    "holdout_median_ae_lpa": 2.08,
    "mape": 35.22,
    "pay_concept": "Estimated Annual CTC / Salary Midpoint (Base + Fixed Allowances)",
    "disclaimer": "Historical holdout MAE does not guarantee accuracy for any individual prediction. Compensation variance expands at senior experience levels."
  }
}
```

---

## 4. Frontend Display Verification (`PredictorPage.tsx`)

| Display Element | Displayed in UI? | Actual Rendered Content | Compliance Assessment |
| :--- | :--- | :--- | :--- |
| **Point Estimate** | **YES** | Large typography: `$185,000` (USA) or `₹14.25 LPA` (India). | **COMPLIANT** |
| **Pay Concept Scope** | **YES** | Dedicated card: "Scope Notice (Base Salary Only)" vs "Scope Notice (Annualized CTC)". | **COMPLIANT** |
| **Empirical Error Metric** | **YES** | "MAE: $36,381 across N = 6,808 test postings (R² = 0.42)" / "Holdout MAE: $36,381 (Median AE: $26,384)". | **COMPLIANT** |
| **Salary Range / Interval** | **NO** | `result.confidence_interval` is **NOT rendered anywhere** on the page. | **COMPLIANT** |
| **Probability Claim** | **NO** | Zero coverage or probability claims rendered. Explicit disclaimer: *"JOBINTEL reports verified point estimates with empirical error metrics rather than uncalibrated probability intervals."* | **COMPLIANT** |

---

## 5. Findings Matrix

### Finding SAL-01: API Envelope Naming Legacy Conflation
- **Claim:** The backend API response contract clearly distinguishes empirical MAE dispersion from calibrated confidence intervals.
- **Actual Implementation:** The JSON payload retains `"confidence_interval"` as the outer key name. While internal fields (`"interval_type": "empirical_mae_dispersion"` and `"interval_note"`) clarify the semantics, external automated API consumers typically inspect outer key names (`response["confidence_interval"]`), which remains misleading.
- **Evidence:** `src/backend/services/usa_service.py` line 261, `src/backend/services/india_service.py` line 304.
- **Verification Method:** JSON payload inspection and TestClient invocation.
- **Risk:** External developers consuming the raw REST API could misinterpret `display: "$148,619 - $221,381"` as a 95% statistical confidence interval.
- **Required Action:**
  - Deprecate `confidence_interval` key in favor of `error_dispersion_band` or `empirical_mae_bounds`.
  - Maintain `confidence_interval` as a deprecated alias until a major version bump, but change primary documentation.
- **Status:** **`VERIFIED WITH LIMITATIONS`**

### Finding SAL-02: Absence of Pydantic Output Schemas on Prediction Routes
- **Claim:** Prediction routes enforce strict Pydantic response models.
- **Actual Implementation:** In `src/backend/routers/usa.py` and `src/backend/routers/india.py`, the route decorators `@router.post("/predict")` omit `response_model=...`. The endpoints return unstructured dictionaries.
- **Evidence:** `src/backend/routers/usa.py` line 48: `def predict_usa_salary(req: USAPredictionRequest):`.
- **Verification Method:** Router inspection.
- **Risk:** Type drift or unintentional serialization of unvalidated fields.
- **Required Action:** Define and bind explicit Pydantic response models (`USAPredictionResponse`, `IndiaPredictionResponse`) in a future sprint.
- **Status:** **`VERIFIED WITH LIMITATIONS`**

---

## 6. Conclusion

The user-facing frontend is fully compliant with the Prediction Realism Standard: it presents only point estimates, empirical error metrics, and non-guarantee notices, with zero fabricated intervals. However, the backend JSON contract retains the legacy key `confidence_interval`, which represents a lingering semantic limitation.
