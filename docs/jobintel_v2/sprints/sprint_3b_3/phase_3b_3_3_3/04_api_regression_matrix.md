# SPRINT 3B.3.3.3.3: LIVE STAGING API REGRESSION MATRIX

**Audit Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Target Staging Service:** `https://jobintel-backend-staging.onrender.com`  
**Auditor Mode:** STRICTLY READ-ONLY  
**Verification Verdict:** **PASS (ALL CORE SERVICES VERIFIED LIVE)**

---

## 1. HEALTH, READINESS & METADATA CONTRACTS

| Endpoint | Method | Expected Status | Live Status | Latency | Response Verification Details | Status |
| :--- | :-: | :-: | :-: | :-: | :--- | :---: |
| `/health` | GET | 200 | **200 OK** | 185.2 ms | `status: "healthy"`, all 9 mandatory ML models verified loaded in memory | **PASS** |
| `/api/ready` | GET | 200 | **200 OK** | 162.4 ms | `status: "ready"`, downstream inference pipelines verified ready | **PASS** |
| `/meta` | GET | 200 | **200 OK** | 170.8 ms | Platform version and supported features metadata returned | **PASS** |

---

## 2. EMPLOYER INTELLIGENCE & RESOLVER CONTRACTS

Employer resolution services were evaluated to verify multi-jurisdiction matching and fail-closed security:

| Endpoint | Method | Payload / Target | Live Status | Latency | Observed Response & Governance Behavior | Status |
| :--- | :-: | :--- | :-: | :-: | :--- | :---: |
| `/api/v1/employers` | GET | Pagination list | **200 OK** | 210.1 ms | Returns standard paginated employer structure (`count: 0`, `items: []`) | **PASS** |
| `/api/v1/employers/UNKNOWN` | GET | Non-existent ID | **404 Not Found** | 195.4 ms | Clean JSON error: `{"detail": "Employer not found"}` | **PASS** |
| `/api/v1/employers/resolve` | POST | Distinct entity: `{"candidate_name": "Unknown Startup Inc"}` | **200 OK** | 240.6 ms | `match_type: "NO_MATCH"`, `resolved_company_id: null`, `review_status: "CONFIRMED_DISTINCT"`. Fail-closed identity preservation. | **PASS** |
| `/api/v1/employers/resolve` | POST | Invalid schema: `{"invalid_field": 123}` | **422 Unprocessable** | 180.2 ms | Pydantic validation error returned; invalid payload safely rejected | **PASS** |

---

## 3. SALARY INTELLIGENCE & STATISTICAL CONTRACTS

Prediction endpoints were probed with certified profiles to verify prediction accuracy and interval contract honesty:

### 3.1 USA Salary Prediction Contract
- **Endpoint:** `POST /api/usa/predict`
- **Payload:**
  ```json
  {
    "Role_Family": "Software Engineer",
    "experience_band": "Senior",
    "City": "San Francisco",
    "skills": ["python", "aws", "docker"]
  }
  ```
- **Live Response:**
  ```json
  {
    "predicted_salary": 212332.30,
    "confidence_interval": {
      "interval_type": "empirical_mae_dispersion",
      "interval_lower": 181822.42,
      "interval_upper": 242842.18,
      "dispersion_metric": "holdout_mae",
      "dispersion_value": 30509.88,
      "note": "Empirical dispersion based on holdout MAE; does not guarantee individual salary coverage."
    }
  }
  ```
- **Auditor Verification:**
  - `predicted_salary`: `$212,332.30` matches golden manifest profile.
  - `confidence_interval`: Emitted with honest `interval_type: "empirical_mae_dispersion"`.
  - Forbidden `prediction_interval`: **Strictly ABSENT** from the payload.
  - Coverage guarantee claims: **Purged**. Explanatory disclaimer present.
  - **Status:** **PASS (STRICT COMPLIANCE)**.

### 3.2 India Salary Prediction Contract
- **Endpoint:** `POST /api/india/predict`
- **Payload:**
  ```json
  {
    "normalized_role": "Backend Developer",
    "experience_midpoint_years": 5.0,
    "experience_range_years": 2.0,
    "city_grouped": "Bangalore",
    "skills": ["Python", "Django", "PostgreSQL"]
  }
  ```
- **Live Response:**
  - Predicted salary: `16.37 LPA` (matches golden profile).
  - Interval type: `empirical_mae_dispersion`.
  - Explanatory note: Accompanying empirical dispersion disclaimer returned.
  - **Status:** **PASS (STRICT COMPLIANCE)**.

---

## 4. OCCUPATIONS INTELLIGENCE CONTRACTS

| Endpoint | Method | Live Status | Latency | Response Verification Details | Status |
| :--- | :-: | :-: | :-: | :--- | :---: |
| `/api/v1/occupations/classifications` | GET | **200 OK** | 195.2 ms | Returns 8 international taxonomy systems (US SOC, UK SOC, O*NET, ISCO-08, ANZSCO, SSOC, NCO-2015, ESCO) | **PASS** |
| `/api/v1/occupations/canonical` | GET | **200 OK** | 225.4 ms | Returns 12 cross-market canonical tech occupations | **PASS** |
| `/api/v1/occupations/coverage` | GET | **200 OK** | 210.8 ms | Market concordance matrix across all supported geographies | **PASS** |

---

## 5. DEMAND INTELLIGENCE & UK PUBLICATION GATING

| Endpoint | Method | Target / Query | Live Status | Observed Response & Gating Enforcement | Status |
| :--- | :-: | :--- | :-: | :--- | :---: |
| `/v1/demand/markets` | GET | None | **200 OK** | Catalogs 5 global markets (US, UK, AU, SG, IN) | **PASS** |
| `/v1/demand/metrics` | GET | None | **200 OK** | Catalogs 7 international labour demand indicators | **PASS** |
| `/v1/demand/occupations` | GET | `?market=US` | **200 OK** | Active US BLS and Lightcast demand series returned | **PASS** |
| `/v1/demand/occupations/UK_SOC_2020:2134` | GET | `?market=UK` | **200 OK** | `publication_gate_active: true`, `primary_metric_value: null`, `gate_code: "UK_DEMAND_DATA_NOT_PUBLISHED"`. Strict data suppression verified. | **PASS** |
| `/api/v1/markets/UK/salary/occupations` | GET | None | **503 Unavailable** | Fail-closed governance gate: `{"detail": "UK salary intelligence publication gate active: UK_DATA_NOT_PUBLISHED"}` | **PASS** |

---

## 6. REGRESSION AUDIT CONCLUSION

All core backend services and analytical APIs operating on Render staging demonstrate 100% adherence to their statistical, security, and governance contracts. Zero regressions detected.
