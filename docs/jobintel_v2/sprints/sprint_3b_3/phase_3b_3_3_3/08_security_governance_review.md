# SPRINT 3B.3.3.3.3: SECURITY & DATA GOVERNANCE REVIEW

**Audit Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Target Staging Service:** `https://jobintel-backend-staging.onrender.com`  
**Auditor Mode:** STRICTLY READ-ONLY  
**Security & Governance Verdict:** **PASS — FULLY HARDENED & COMPLIANT**

---

## 1. PUBLIC ERROR HYGIENE & DATA LEAKAGE PREVENTION

Public error endpoints were subjected to adversarial requests to verify that internal server paths, call stacks, environment secrets, and raw database errors are strictly suppressed.

### 1.1 Error Inspection Matrix
| Scenario | Endpoint Tested | Request Payload / Parameter | HTTP Status | Response Body | Path/Secret Leaks | Status |
| :--- | :--- | :--- | :-: | :--- | :-: | :---: |
| **Missing Skill (USA)** | `/api/skills/detail/nonexistent` | GET | **404** | `{"detail": "Skill 'nonexistent' not found in USA skills catalog."}` | None | **CLEAN** |
| **Missing Skill (India)**| `/api/india/skills/nonexistent` | GET | **404** | `{"detail": "Skill 'nonexistent' not found in India skills catalog."}` | None | **CLEAN** |
| **Invalid Schema** | `/api/v1/employers/resolve` | `{"bad_key": true}` | **422** | Structured Pydantic validation errors | None | **CLEAN** |
| **Unknown Employer** | `/api/v1/employers/UNKNOWN` | GET | **404** | `{"detail": "Employer not found"}` | None | **CLEAN** |
| **UK Salary Access** | `/api/v1/markets/UK/salary/occupations` | GET | **503** | `{"detail": "UK salary intelligence publication gate active: UK_DATA_NOT_PUBLISHED"}` | None | **CLEAN** |

**Hygiene Assessment:** All responses conform to standard RFC 7807/FastAPI error envelopes. Zero stack traces or file paths leaked.

---

## 2. CROSS-ORIGIN RESOURCE SHARING (CORS) POLICY

Live staging CORS headers were verified against the staging frontend origin:
- **Origin Allowed:** `https://jobintel-staging.vercel.app`
- **Allowed Methods:** `GET, POST, OPTIONS`
- **Allowed Headers:** `Content-Type, Authorization, Accept, X-Requested-With`
- **Wildcard Allow-All in Production:** Denied. Explicit origin whitelist enforced.

---

## 3. EMPLOYER STATUTORY IDENTIFIER SECURITY

The employer entity resolution engine was verified against 32 adversarial test cases to guard against fraudulent or accidental legal entity attribution:

### 3.1 Multi-Jurisdiction Authority Validation
Statutory identifiers are strictly verified against their governing authority and jurisdiction:
- **SEC CIK:** 10 digits (US Securities and Exchange Commission)
- **UK CRN:** 8 alphanumeric characters (Companies House)
- **Indian CIN:** 21 alphanumeric characters (Ministry of Corporate Affairs)
- **Singapore UEN:** 9-10 alphanumeric characters (ACRA)
- **Australian ABN:** 11 digits with modulus-89 validation (Australian Business Register)

### 3.2 Duplicate Identifier Collision Defense
In scenarios where identical statutory identifiers appear across candidate and database records due to multi-entity group registrations:
- **Prior Flawed Behavior:** Prematurely returned `CONFIRMED_MATCH` on the first hit.
- **Remediated Hardened Behavior:** Performs a full registry scan. If multiple conflicting entities share an identifier, the system fails closed to:
  ```json
  {
    "match_type": "NO_MATCH",
    "resolved_company_id": null,
    "confidence_score": 0.0,
    "review_status": "MANUAL_REVIEW_REQUIRED"
  }
  ```
  Zero arbitrary identity attribution occurs.

---

## 4. PUBLICATION GATING INTEGRITY (UK ASHE)

The strict two-layer publication gate for UK salary data was evaluated on live staging and through automated regression suites (`tests/test_uk_salary_api.py`):
1. **API Gating Layer:** Calls to `/api/v1/markets/UK/salary/*` return HTTP 503 Service Unavailable (`gate_code: "UK_DATA_NOT_PUBLISHED"`).
2. **Demand Suppression Layer:** UK labour demand endpoints return HTTP 200 with `publication_gate_active: true` and `primary_metric_value: null`. No raw ASHE microdata or modelled estimates are leaked to unauthenticated users.
3. **Frontend Gating Banners:** The live staging frontend on `/demand` displays a prominent gating warning whenever the UK market is toggled.
