# STATISTICAL LIMITATIONS REGISTER
## Comprehensive Inventory of Known Model Boundaries, Variances & Constraints

**Sprint ID:** 3B.3.2.3  
**Governance ID:** `JOBINTEL-REG-STAT-001`  
**Governing Standard:** `JOBINTEL-STD-PRED-001`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`

---

## 1. Purpose & Maintenance Policy

This register documents all known statistical, empirical, and architectural limitations of the algorithms, models, and data pipelines powering JOBINTEL 2.0.

In compliance with `JOBINTEL-STD-PRED-001`, documenting limitations is not an admission of platform failure; it is a mandatory quality assurance practice that prevents over-promising, protects platform credibility, and directs engineering priorities for upcoming sprints.

---

## 2. Statistical Limitations Inventory

### LIM-001: Heteroskedasticity in Salary Residual Dispersion
- **Affected System:** `MOD_IN_SALARY_HGBR` & `MOD_US_SALARY_XGB`
- **Root Cause:** In compensation distributions, absolute prediction error naturally scales with seniority. Errors at ₹40 LPA (or $250k) are substantially larger in absolute terms than errors at ₹6 LPA (or $60k).
- **Current State:** Prediction intervals in early documentation were derived from unconditional median absolute residuals ($\pm ₹2.08\text{ LPA}$), which understates uncertainty for high-income roles.
- **Remediation Plan:** Implement Conformalized Quantile Regression (CQR) in Sprint 3B.3.3 to dynamically scale interval widths as a function of the input feature vector.
- **Risk Level:** **MEDIUM**.

---

### LIM-002: Sample Size Constraint on Entity Resolution Error Bound
- **Affected System:** `SYS_EMP_RESOLVER_V2`
- **Root Cause:** Evaluating 55 true negative entity pairs without a false merge mathematically yields an upper 95% Wilson confidence bound of 6.53%.
- **Current State:** Claiming that error rates are proven below 0.1% ($p < 0.001$) is mathematically unsupported. Under the Rule of Three, proving $p < 0.001$ requires $N \ge 3,000$ negative pairs without an observed error.
- **Remediation Plan:** Expand the gold negative pair evaluation harness to $N \ge 3,000$ synthetic and real corporate subsidiary pairs.
- **Risk Level:** **HIGH** (if miscommunicated); **LOW** (if bounded to observed CI).

---

### LIM-003: In-Sample Calibration Bias for Temperature Scaling
- **Affected System:** `SYS_OCC_MAPPER`
- **Root Cause:** The temperature scaling parameter ($T = 1.24$) that reduced ECE from 5.87% to 3.81% was optimized and evaluated on the same 100 gold benchmark titles.
- **Current State:** In-sample optimization introduces optimistic evaluation bias. True out-of-sample ECE is unverified.
- **Remediation Plan:** Create an independent calibration set ($N = 500$) distinct from the test evaluation set.
- **Risk Level:** **MEDIUM**.

---

### LIM-004: Limited Sample Size in Adversarial Skill Extraction Testing
- **Affected System:** `SYS_SKILL_EXTRACTOR`
- **Root Cause:** The 5-token contextual co-occurrence filter was evaluated against 20 hand-crafted adversarial test phrases.
- **Current State:** While achieving 100% precision on these 20 edge cases confirms that the regex logic functions, it cannot guarantee 100% precision across millions of noisy, uncurated job descriptions.
- **Remediation Plan:** Annotate an empirical holdout corpus of 2,000 raw job postings and measure precision/recall under noisy real-world formatting.
- **Risk Level:** **MEDIUM**.

---

### LIM-005: Exclusion of Non-Base Compensation in US Modeling
- **Affected System:** `MOD_US_SALARY_XGB`
- **Root Cause:** The underlying job posting dataset only reports base salary midpoints. Equity grants (RSUs, options), signing bonuses, annual performance bonuses, and health insurance stipends are omitted.
- **Current State:** In the US tech market, total compensation at senior, staff, and executive levels often exceeds base pay by 50% to 150%. Presenting base salary as "total salary" would drastically mislead job seekers.
- **Remediation Plan:** Require explicit "Base Salary Only" UI labeling and develop an auxiliary equity tier estimation heuristic.
- **Risk Level:** **HIGH** (without UI disclosure); **LOW** (with disclosure).

---

### LIM-006: Advertised Vacancy Flow vs. Net Job Creation
- **Affected System:** `SYS_DEMAND_INTEL`
- **Root Cause:** Public job listings measure advertised requisition flow, not confirmed hires or net workforce expansion.
- **Current State:** A company may post a requisition to build a candidate pipeline, replace departing staff, or benchmark internal salaries without ever making a hire. Confusing vacancy flow with net headcount growth distorts economic reality.
- **Remediation Plan:** Maintain clear separation between statutory workforce census (balance sheet headcount) and open job listings (market activity flow).
- **Risk Level:** **MEDIUM**.

---

### LIM-007: Geographic Coverage Boundaries
- **Affected System:** `MOD_IN_SALARY_HGBR` & `MOD_US_SALARY_XGB`
- **Root Cause:** The India model is trained predominantly on 6 tier-1 tech metros (Bengaluru, Hyderabad, Pune, Mumbai, NCR, Chennai). The US model is concentrated in major tech states (CA, NY, WA, TX, MA).
- **Current State:** Extrapolating predictions to tier-3 towns, rural areas, or traditional non-tech sectors incurs high out-of-distribution uncertainty.
- **Remediation Plan:** Enforce input boundary checks in API gateways; trigger out-of-distribution disclaimers when location inputs fall outside verified clusters.
- **Risk Level:** **LOW**.

---

### LIM-008: UK Sovereign Vacancy Flow Withheld Status
- **Affected System:** `SYS_DEMAND_INTEL` (UK Market)
- **Root Cause:** High-resolution UK vacancy flow data requires official licensing verification under Crown Commercial Service / ONS terms.
- **Current State:** Data is gated and returns explicit `null` / `withheld` status in backend APIs.
- **Remediation Plan:** Maintain gating until licensing documentation is officially approved.
- **Risk Level:** **CONTROLLED** (by architectural design).

---

## 3. Governance Certification

All 8 identified limitations have been recorded in this permanent register. Sprint 3B.3.3 work packages will directly address items LIM-001 through LIM-005.
