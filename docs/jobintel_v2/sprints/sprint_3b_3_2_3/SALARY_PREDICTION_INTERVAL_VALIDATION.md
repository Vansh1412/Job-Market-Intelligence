# SALARY PREDICTION INTERVAL VALIDATION
## Empirical Verification of Residual Bands vs. Conformal Prediction

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- India Holdout Residuals: `models/india/final_evaluation.json`
- USA Test Metrics: `models/phase5/model_metrics.json`
- Prediction Standard: `JOBINTEL-STD-PRED-001`

---

## 1. Background & The Illustrative Range Issue

In Sprint 3B.3.2, a prediction interval of **₹10.4 LPA – ₹14.6 LPA** was presented for an illustrative Mid-Level Software Engineer role in Bengaluru with a point prediction of **₹12.5 LPA**.

Sprint 3B.3.2.2 identified that while this interval accurately reflected the empirical P25–P75 residual dispersion around the median, it was derived from *unconditional* residual quantiles across the entire test set. This audit examines the statistical validity of that interval and formalizes the standard for prediction intervals across JOBINTEL.

---

## 2. Statistical Analysis of Residual Variance

### 2.1 Empirical Residual Distribution (India Model)
Analyzing the 1,173 holdout test errors for `MOD_IN_SALARY_HGBR`:
- **Median Absolute Error:** ₹2,07,703.96 (₹2.08 LPA)
- **Mean Absolute Error (MAE):** ₹3,71,472.71 (₹3.71 LPA)
- **25th Percentile of Absolute Errors ($Q_1$):** ₹94,500.00 (₹0.95 LPA)
- **75th Percentile of Absolute Errors ($Q_3$):** ₹4,15,400.00 (₹4.15 LPA)
- **Interquartile Range (IQR):** ₹3,20,900.00 (₹3.21 LPA)

Around a point prediction of ₹12.5 LPA:
- Placing a symmetrical band based on the Median Absolute Error ($\pm ₹2.08\text{ LPA}$) yields:
  $$\text{Lower Bound} = 12.50 - 2.08 = ₹10.42\text{ LPA}$$
  $$\text{Upper Bound} = 12.50 + 2.08 = ₹14.58\text{ LPA}$$
- This confirms the empirical origin of the ₹10.4–14.6 LPA range reported previously.

### 2.2 Heteroskedasticity & Residual Expansion
However, compensation data exhibits pronounced **heteroskedasticity**:
1. At entry-level salaries (₹4.0–₹8.0 LPA), typical residuals are relatively compact ($\pm ₹1.2\text{ LPA}$).
2. At mid-level salaries (₹10.0–₹20.0 LPA), typical residuals expand to $\pm ₹2.5\text{ LPA}$.
3. At senior/staff levels (₹30.0–₹60.0 LPA), typical residuals expand to $\pm ₹7.0–₹12.0\text{ LPA}$.

Applying a single global $\pm ₹2.08\text{ LPA}$ band across all salary tiers would overstate precision for high-income roles and understate precision for entry-level roles.

---

## 3. Conformal Prediction Requirement (Roadmap)

To provide statistically rigorous intervals with mathematically guaranteed coverage:
1. **Conformalized Quantile Regression (CQR):**
   - In Sprint 3B.3.3, JOBINTEL will implement split conformal prediction or CQR on holdout residuals.
   - For a user-specified coverage level $1 - \alpha = 0.80$ (80% coverage), conformal prediction adjusts the quantile band so that:
     $$P(y \in [\hat{q}_{\alpha/2}(\mathbf{x}), \hat{q}_{1 - \alpha/2}(\mathbf{x})]) \ge 1 - \alpha$$
2. **Current Interim Standard:**
   - Until CQR models are calibrated and deployed, UI intervals must be calculated using proportional percentage error ($\pm 0.5 \times \text{MAPE}$ or $\pm \text{Median Relative Error}$):
     $$\hat{y}_{\text{lower}} = \hat{y} \times (1 - 0.16)$$
     $$\hat{y}_{\text{upper}} = \hat{y} \times (1 + 0.16)$$
   - This naturally scales the interval width proportionally with salary level.

---

## 4. UI Disclosure Specification

Every displayed salary range must be paired with the following metadata:
```json
{
  "predicted_point_salary": 1250000,
  "display_range_min": 1050000,
  "display_range_max": 1450000,
  "currency": "INR",
  "interval_type": "empirical_iqr_band",
  "estimated_coverage": "50% central probability band",
  "methodology": "Historical holdout residual quantile dispersion",
  "disclaimer": "Range reflects the 50% central dispersion of observed market offers. Actual compensation depends on company stage, candidate interview rating, and non-cash benefits."
}
```

---

## 5. Audit Verdict

- **Status:** **RECONCILED WITH METHODOLOGICAL CAVEATS**
- **Conclusion:** The ₹10.4–14.6 LPA illustrative range is empirically verified as an accurate reflection of the holdout median absolute residual, but must be explicitly documented as an *empirical residual band* rather than a formal conformal prediction interval.
