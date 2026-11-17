# JOBINTEL 2.0 — SPRINT 3B.3.3.3
## DOCUMENT 03: SALARY API CONTRACT CORRECTION & STATISTICAL METADATA RECONCILIATION

**Sprint:** 3B.3.3.3 — Critical Employer Resolver Remediation & Salary Contract Correction  
**Components:** `src/backend/services/usa_service.py`, `src/backend/services/india_service.py`, `src/backend/routers/predict.py`, `src/backend/routers/india.py`  
**Focus:** Statistical Realism & API Contract Ground Truth  
**Status:** RECONCILED & STANDARDIZED  

---

### 1. Forensic Discrepancy & Background

During Sprint 3B.3.3.2, documentation (`07_salary_api_contract_decision.md`, `11_final_sprint_report.md`) claimed that JOBINTEL had implemented a dual-emission salary API contract:
1. Emitting a new canonical `prediction_interval` object claiming conformal prediction with $80\%$ nominal coverage.
2. Emitting `confidence_interval` as a legacy backward-compatibility alias.

Independent forensic audit `Sprint 3B.3.3.2.1` examined the codebase and found:
- **`prediction_interval` was never implemented in backend Python code.** Neither `USAService`, `IndiaService`, nor FastAPI schemas serialized a `prediction_interval` field.
- **The actual runtime API emits ONLY `confidence_interval`.**
- **The interval is an empirical MAE dispersion, NOT a conformal prediction interval.**
  The backend computes:
  $$\text{lower} = \max(0, \hat{y} - \text{MAE}_{\text{holdout}})$$
  $$\text{upper} = \hat{y} + \text{MAE}_{\text{holdout}}$$
  and attaches explicit metadata:
  ```json
  "confidence_interval": {
    "lower": 222110.28,
    "upper": 291810.28,
    "display": "$222,110 - $291,810",
    "margin_mae": 34850.0,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  }
  ```

---

### 2. Statistical Reality of Empirical MAE Dispersion

A $\pm 1 \text{ MAE}$ interval around point estimate $\hat{y}$ has well-known statistical properties:
- If errors follow a Laplace (double-exponential) distribution, $\pm 1 \text{ MAE}$ covers:
  $$P(|e| \le \text{MAE}) = 1 - e^{-1} \approx 63.2\%$$
- If errors follow a Normal distribution, $\text{MAE} \approx 0.7979 \sigma$, and $\pm 1 \text{ MAE}$ covers:
  $$P(|e| \le 0.7979 \sigma) \approx 57.5\%$$
- On empirical holdout validation sets (USA $N=1173$, India $N=1173$), empirical coverage ranges from $54\%$ to $62\%$, depending on archetype.
- **Claiming $80\%$ or $95\%$ coverage was mathematically false.**

---

### 3. Contract Decision & Permanent Standardization

To enforce absolute statistical realism and avoid breaking downstream consumers:

1. **Canonical Field Retained as `confidence_interval`:**
   - The runtime response contract remains unchanged.
   - Consumers rely on `confidence_interval.lower`, `confidence_interval.upper`, `confidence_interval.display`.
   - The frontend (`frontend/src/types.ts` and `frontend/src/pages/PredictorPage.tsx`) consumes `confidence_interval` directly.

2. **Full Disclosure Metadata Enforced:**
   - Every inference response contains:
     - `interval_type: "empirical_mae_dispersion"`
     - `interval_note: "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."`
     - `margin_mae`: The exact holdout MAE used.

3. **Documentation Purge:**
   - All references to unvalidated conformal prediction intervals, $80\%/95\%$ nominal coverage, and dual-emission `prediction_interval` are purged from official architectural documentation.
   - Future sprints considering conformal prediction must train and calibrate non-conformity scores on dedicated calibration splits before any schema change.

---

### 4. Verified Runtime API Output (USA & India)

#### USA Endpoint (`POST /api/usa/predict`):
```json
{
  "predicted_salary": 256960.28,
  "confidence_interval": {
    "lower": 222110.28,
    "upper": 291810.28,
    "display": "$222,110 - $291,810",
    "margin_mae": 34850.0,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  },
  "archetype": {
    "code": "SYS_ENG",
    "name": "Distributed Systems & Cloud Infrastructure",
    "typical_mae": 34850.0
  }
}
```

#### India Endpoint (`POST /api/india/predict`):
```json
{
  "predicted_salary_lpa": 16.62,
  "predicted_salary_inr": 1662308.0,
  "confidence_interval": {
    "lower_lpa": 12.82,
    "upper_lpa": 20.42,
    "display": "₹12.82 - ₹20.42 LPA",
    "margin_mae_lpa": 3.8,
    "interval_type": "empirical_mae_dispersion",
    "interval_note": "Empirical dispersion based on holdout MAE; not a calibrated statistical probability interval."
  },
  "archetype": {
    "archetype_id": "IND_ARC_03",
    "name": "Python, Cloud Data & Applied AI/ML",
    "typical_mae_lpa": 3.8
  }
}
```
