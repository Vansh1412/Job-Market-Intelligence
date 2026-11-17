# JOBINTEL 2.0 — SPRINT 3B.3.3.2.1
## DOCUMENT 07: SALARY PREDICTION API CONTRACT & DEPRECATION AUDIT

**Sprint:** 3B.3.3.2.1 — Independent Security, Statistical Contract & Release Audit  
**Auditor Role:** Principal API Architect & Contract Auditor  
**Audit Target:** Schema Inspection of `confidence_interval` vs `prediction_interval`  
**Execution Mode:** STRICTLY READ-ONLY  
**Date:** 2026-11-17  
**Status:** DIVERGENCE IDENTIFIED (DOCUMENTED DUAL EMISSION NOT IN CODE)  

---

### 1. Executive Summary

Section 6 of the audit mandate requires an independent inspection of the salary API response contracts:
> *"Determine whether the legacy alias and canonical field contain identical values.*  
> *Determine whether external clients could mistake empirical dispersion for calibrated coverage.*  
> *A dual-emission strategy is not automatically safe."*

This forensic audit reveals a **direct contract divergence between sprint documentation and runtime code**:
- The Sprint 3B.3.3.2 release documentation (Document 07 and Document 11) claimed that the API was updated to dual-emit `prediction_interval` and `confidence_interval`.
- In actual runtime code (`usa_service.py`, `india_service.py`, `predict.py`, `india.py`), **the API emits ONLY `confidence_interval`**. The field `prediction_interval` is not present in the serialized JSON responses.

---

### 2. Runtime JSON Response Contract

Direct inspection of live API responses from `POST /api/v1/predict/estimate` and `POST /api/v1/india/predict`:

#### USA Response Payload:
```json
{
  "country": "USA",
  "currency": "USD",
  "predicted_salary": 180413.0,
  "confidence_interval": {
    "lower": 144032.36,
    "upper": 216793.64,
    "display": "$144,032 - $216,794",
    "margin_mae": 36380.64,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  }
}
```

#### India Response Payload:
```json
{
  "country": "India",
  "currency": "INR",
  "predicted_salary_lpa": 10.0,
  "confidence_interval": {
    "lower_lpa": 6.5,
    "upper_lpa": 13.5,
    "display": "₹6.50 - ₹13.50 LPA",
    "margin_mae_lpa": 3.5,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  }
}
```

---

### 3. Risk of Misinterpreting Empirical Dispersion for Calibrated Coverage

#### 3.1 Potential Client Misunderstandings
1. **Name Misleadingness (`confidence_interval`):**
   The dictionary key is named `confidence_interval`. In statistics, a confidence interval estimates a population mean, while a user expects an individual salary range.
2. **Coverage Assumption Risk:**
   Third-party API clients or automated scrapers reading `lower` and `upper` might assume this represents a standard $95\%$ or $80\%$ probability interval.
3. **Mitigating Architectural Factors in Runtime Code:**
   The backend developers included two safeguarding metadata fields inside the dictionary:
   - `"interval_type": "empirical_mae_dispersion"`
   - `"interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."`
   This is transparent and technically accurate, preventing consumer deception if the metadata fields are inspected.

---

### 4. Deprecation Roadmap & Backward Compatibility Audit

#### 4.1 Evaluation of the Documented 4-Phase Deprecation Plan
Document 07 in Sprint 3B.3.3.2 proposed:
- Phase 1: Dual emission (`prediction_interval` + `confidence_interval`).
- Phase 2: Deprecation notice headers in Sprint 3B.4.
- Phase 3: External client migration in Sprint 3B.4.
- Phase 4: Retirement of `confidence_interval` in Sprint 4.0.

#### 4.2 Audit Finding on Deprecation:
- Because Phase 1 was **never committed to the actual Python schemas or service code**, external clients have not yet received `prediction_interval`.
- Transitioning directly to dual emission requires modifying `src/backend/services/usa_service.py` and `src/backend/services/india_service.py` to add `prediction_interval` alongside `confidence_interval`.
- No breaking change currently exists for existing clients because `confidence_interval` has been maintained continuously.

---

### 5. Findings Summary & Action Items

- **Claim:** Salary API dual-emits `prediction_interval` and `confidence_interval`.
- **Evidence:** Runtime JSON inspection proves only `confidence_interval` is emitted.
- **Risk:** Clients expecting `prediction_interval` will receive `undefined`.
- **Required Action:**
  1. Synchronize documentation to reflect that the runtime contract currently emits `confidence_interval` with `interval_type: "empirical_mae_dispersion"`.
  2. In the next authorized implementation sprint (Sprint 3B.3.3.3), formally implement dual emission in `usa_service.py` and `india_service.py` if the canonical key `prediction_interval` is mandated.
- **Status:** **VERIFIED WITH LIMITATIONS** (Runtime code is backward-compatible and self-disclosing, but differs from sprint documentation claims).
