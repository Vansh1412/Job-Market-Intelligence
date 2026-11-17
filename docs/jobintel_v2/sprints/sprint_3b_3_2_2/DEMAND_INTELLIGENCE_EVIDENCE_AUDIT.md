# JOBINTEL 2.0 — DEMAND INTELLIGENCE EVIDENCE AUDIT
## Independent Audit of Labour Market Observations, Non-Predictive Descriptive Semantics & Governance Gates

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Labour Market Statistics Specialist  
**System Audited:** `SYS_DEMAND_INTEL` (Global Job Demand Intelligence System)  

---

## 1. THE FOUNDATIONAL PRINCIPLE: DESCRIPTIVE VS. PREDICTIVE DEMAND

A fundamental failure mode in commercial talent intelligence platforms is presenting **historical or current job advertisements as predictive forecasts of future net employment growth**.

JOBINTEL 2.0 establishes the permanent architectural rule:
```
====================================================================================================
PERMANENT ARCHITECTURAL DIRECTIVE:
DESCRIPTIVE LABOUR MARKET OBSERVATIONS MUST REMAIN DESCRIPTIVE.
DO NOT INTRODUCE SYNTHETIC PREDICTIVE DEMAND SCORES OR UNVERIFIED FORECASTING ENGINES.
====================================================================================================
```

---

## 2. MANDATED SEMANTIC DISAMBIGUATIONS

To prevent misleading users, the platform enforces six strict semantic boundaries:

| # | What Is Observed (Factual Indicator) | What It Must NEVER Be Conflated With | Why the Distinction Is Critical |
| :-: | :--- | :--- | :--- |
| **1** | **Online Job Advertisements (Flow)** | **Confirmed New Hires** | An advertisement may be cancelled, backfill normal turnover, or remain unfilled. |
| **2** | **Active Job Openings** | **Total Establishment Headcount (Stock)**| A company of 10,000 staff posting 200 openings has 200 vacancies, not 10,200 staff. |
| **3** | **Rising Job Advertisement Volumes** | **Net Employment Growth** | Surging postings may reflect high employee churn rather than corporate expansion. |
| **4** | **Statutory Shortage Indicators (JSA / ONS)**| **Current Immediate Vacancies** | A statutory shortage reflects structural skills deficits, not daily job openings. |
| **5** | **10-Year Macro Employment Projections (BLS)**| **Current Monthly Job Demand** | Macro structural projections span a decade and cannot predict monthly hiring. |
| **6** | **Skill Requirement Frequencies in Postings**| **Actual National Skill Shortages** | High skill mentions in ads indicate employer demand, not a shortage of skilled workers. |

---

## 3. PROHIBITION OF SYNTHETIC SCORES & "DEMAND MOMENTUM"

### 3.1 Prohibited Synthetic Features
1. **No Universal "Global Demand Score":** Combining disparate metrics (Australian IVI index points, US BLS percentage growth, UK vacancy counts) into an unweighted 0–100 score is statistically meaningless and fraudulent.
2. **No "Employer Hiring Momentum Index":** Arbitrary scoring models that rank employers by growth momentum based solely on career page job counts are banned.
3. **No Unanchored Machine Learning Forecasters:** Training black-box LSTM or Prophet models on small, non-stationary vacancy time-series without structural backtesting or macroeconomic covariate modeling is prohibited.

---

## 4. UK DEMAND PUBLICATION GATE GOVERNANCE STATUS

- **Background:** In Sprint 3B.2.1, an independent audit revealed that UK labour market demand data lacked formal licensing and source-use clearance from the UK Office for National Statistics (ONS) and commercial aggregators.
- **Sprint 3B.2.3.1 Remediation:** The publication gate was hardened across the backend Pydantic schemas, replacing misleading zero floats (`0.0`) with explicit nullable fields (`null`).
- **Audit Verification in Sprint 3B.3.2.2:**
  - In `SYS_DEMAND_INTEL`, all UK employer demand flow metrics serialize as `null` with `publication_gate_active: true`.
  - The mandated statutory disclaimer is strictly enforced: *"UK vacancy flow data withheld pending source-use review."*
  - Statutory headcount size bands (UK Gender Pay Gap reporting service) remain accessible as factual historical disclosures.
- **Verdict:** **100% COMPLIANT**. The UK publication gate remains active, intact, and verified.
