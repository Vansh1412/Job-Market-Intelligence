# JOBINTEL 2.0 — SPRINT 3B.3.3.2
## DOCUMENT 07: SALARY API CONTRACT DECISION & DEPRECATION ROADMAP

**Sprint:** 3B.3.3.2 — Critical Defect Remediation & Employer Resolver Hardening  
**Package:** WP-FIX-04  
**Author:** Principal API Architect & Full-Stack Lead  
**Date:** 2026-11-17  
**Status:** ARCHITECTURALLY APPROVED  

---

### 1. Context & Statistical Rationale

In Sprint 3B.3.3, JOBINTEL updated the salary prediction endpoints (`/api/v1/predict/salary`, `/api/v1/salary/predict`, `/api/v1/india/salary/predict`, `/api/v1/uk/salary/predict`) to adopt statistical prediction realism:
- **Prediction Interval vs. Confidence Interval:**
  In rigorous statistics, a *Confidence Interval* quantifies the uncertainty around an estimated population parameter (such as the true mean $\mu$). A *Prediction Interval* quantifies the uncertainty for an *individual future observation* ($Y = \hat{y} + \epsilon$).
  Because a job seeker or recruiter wants to know the expected range for an individual compensation package, the interval emitted by conformal prediction or quantile bounds is fundamentally a **Prediction Interval**.

---

### 2. Backward Compatibility Implementation

To prevent breaking existing API consumers, mobile wrappers, or frontend components deployed in earlier sprints:
1. **Dual Emission Contract:**
   All salary prediction endpoints emit BOTH keys:
   - `prediction_interval`: Canonical, statistically precise object containing `lower`, `upper`, `nominal_coverage: 0.80`, `empirical_coverage: 0.802`, and `method: "Conformalized Residual Distribution"`.
   - `confidence_interval`: Legacy alias dictionary `{ "lower": ..., "upper": ... }` mirroring the prediction interval bounds.
2. **Schema Definition (`src/backend/schemas/prediction.py`):**
   ```python
   class SalaryPredictionResponse(BaseModel):
       predicted_salary: float
       currency: str
       prediction_interval: PredictionInterval
       confidence_interval: dict[str, float]  # Deprecated backward-compatible alias
       calibration_status: str
       caveat: str
   ```
3. **Frontend Compatibility:**
   Frontend TypeScript types (`frontend/src/types.ts`) support `prediction_interval ?? confidence_interval`, ensuring graceful rendering regardless of which field is prioritized.

---

### 3. Formal Deprecation Roadmap

| Milestone | Target Sprint | Architectural Action | Client Impact |
| :--- | :--- | :--- | :--- |
| **Phase 1: Dual Emission** | Sprint 3B.3.3 (Current) | Emit both `prediction_interval` and `confidence_interval`. | Zero breaking changes. All legacy clients continue functioning. |
| **Phase 2: Deprecation Notice** | Sprint 3B.3.4 (Staging Release) | Add OpenTelemetry / FastAPI `Deprecation` header when `confidence_interval` is accessed. | Warnings logged for upstream consumers. |
| **Phase 3: Client Migration** | Sprint 3B.4 (Global Launch) | Migrate any remaining external SDKs and dashboard widgets to `prediction_interval`. | Code refactoring for third-party consumers. |
| **Phase 4: Field Retirement** | Sprint 4.0 (Major Release) | Remove `confidence_interval` from response schemas. | Breaking change for un-migrated legacy clients. |

---

### 4. Audit Verdict

The dual-emission architecture satisfies both statistical rigor and enterprise production backward compatibility. No immediate breaking change is introduced, and a structured 4-phase deprecation path is established.
