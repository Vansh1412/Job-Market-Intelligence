# JOBINTEL 2.0 — SPRINT 3B.2.3 UK PUBLICATION GATE & LEAKAGE AUDIT REPORT
## Endpoint-by-Endpoint Leakage Audit, Semantic Value Inspection & Licensing Governance

**Audit Date:** November 16, 2026  
**Auditor:** Independent Principal Backend Security Engineer & Data Governance Auditor  
**Audit Scope:** Independent inspection of `src/backend/routers/demand.py`, `src/backend/services/demand_service.py`, `src/backend/schemas/demand.py`, and `src/backend/data/demand/sources.json`.

---

### 1. AUDIT OBJECTIVE & CONTEXT

The UK Labour Demand dataset published experimentally by the Office for National Statistics (ONS) incorporates proprietary online vacancy scraping telemetry supplied by Textkernel BV. While academic and internal governmental analysis of these experimental series is permitted, downstream commercial redistribution in a SaaS analytics platform presents licensing risks.

Sprint 3B.2.2 implemented a technical publication gate. This independent audit evaluated:
1. Whether all UK endpoints enforce the gate without numerical data leakage.
2. The semantic distinction between measured zero, withheld status, and null.
3. The independence and authenticity of qualitative shortage indicators.
4. The boundary between technical withholding and legal source redistribution permission.

---

### 2. ENDPOINT-BY-ENDPOINT AUDIT RESULTS

All 8 demand endpoints were audited using FastAPI `TestClient` queries for UK market data (`market=UK` / `market_id=UK`):

| # | Endpoint Tested | Request Context | Status Code | Gated Fields Observed | Leakage Detected? | Audit Result |
|---|---|---|---|---|---|---|
| 1 | `GET /api/v1/demand/markets` | Public Market List | 200 OK | `coverage_status: "WITHHELD_PENDING_REVIEW"`, `publication_status: "REVIEW_REQUIRED"` | None | **PASS** |
| 2 | `GET /api/v1/demand/occupations?market=UK` | Public Observation List | 200 OK | All 8 observations have `value: 0.0`, `time_series: []`, `regional_breakdown: []` | None | **PASS** |
| 3 | `GET /api/v1/demand/occupations/2134?market=UK` | Public Occupation Detail | 200 OK | `primary_metric_value: 0.0`, `trend_time_series: []`, `regional_distribution: []`, `publication_gate_active: true`, `publication_gate_code: "UK_DEMAND_DATA_NOT_PUBLISHED"` | None | **PASS** |
| 4 | `GET /api/v1/demand/occupations/2134/trends?market=UK` | Time-Series Trends | 200 OK | `time_series: []`, `publication_gate_active: true`, `publication_gate_code: "UK_DEMAND_DATA_NOT_PUBLISHED"` | None | **PASS** |
| 5 | `GET /api/v1/demand/occupations/2134/regions?market=UK` | Regional Breakdown | 200 OK | Returns empty list `[]` | None | **PASS** |
| 6 | `GET /api/v1/demand/occupations/2134/skills?market=UK` | Occupation Skills | 200 OK | Returns 13 competencies sourced from official occupational framework | None | **PASS** |
| 7 | `GET /api/v1/demand/compare?canonical_id=...&market_a=US&market_b=UK` | Cross-Market Comparison | 200 OK | `metric_b.value: 0.0`, Injects warning: *"UK demand data is currently withheld pending source-use and redistribution review. Direct value comparisons are unavailable."* | None | **PASS** |
| 8 | `POST /api/v1/demand/skills/gaps` | UK Skill Gap Analysis | 200 OK | Evaluates curriculum weights; does not expose advert volumes | None | **PASS** |
| 9 | `GET /api/v1/demand/sources` | Source Registry List | 200 OK | `publication_status: "REVIEW_REQUIRED"`, `restricted_use: ["PUBLIC_REDISTRIBUTION", "COMMERCIAL_SAAS_DISPLAY"]` | None | **PASS** |
| 10| `service.list_observations(..., public_view=False)` | Internal Research View | Internal | Preserves original values (e.g. `112.5`), 7 time-series points for internal audit reconciliation | Controlled | **PASS** |

---

### 3. CRITICAL SEMANTIC AUDIT: ZERO VERSUS WITHHELD VERSUS NULL

The audit evaluated how withheld numeric metrics are represented in API responses:

#### Current Schema Implementation:
- In `src/backend/schemas/demand.py`:
  - `DemandObservation.value` is defined as `float` (mandatory, non-nullable).
  - `OccupationDemandProfile.primary_metric_value` is defined as `float` (mandatory, non-nullable).
- In `src/backend/services/demand_service.py`:
  - When the gate is active in public view, `metric_val = 0.0` is returned.
  - The profile attaches `publication_gate_active: True`, `publication_gate_code: "UK_DEMAND_DATA_NOT_PUBLISHED"`, and `publication_gate_message`.

#### Evaluation & Risk Assessment:
- **Semantic Ambiguity:** Returning `0.0` rather than `null` carries semantic ambiguity. A client reading only `primary_metric_value` without inspecting `publication_gate_active` could mistakenly assume the measured demand volume is zero.
- **Frontend Mitigation:** In `frontend/src/pages/DemandPage.tsx`, the frontend explicitly guards against this by checking `occupationProfile.publication_gate_active` and rendering a full-width red warning banner, suppressing charts and numerical displays.
- **Audit Verdict:** The technical gate successfully withholds data. However, for API consumers, representing withheld values as `0.0` is an **architectural limitation**.
- **Corrective Recommendation for Sprint 3B.3:** Update schema definition to `primary_metric_value: float | None = None` and `value: float | None = None` to enable explicit `null` serialization when gated.

---

### 4. QUALITATIVE SHORTAGE STATUS SOURCE AUDIT

The audit investigated whether the retention of `shortage_status: "NATIONAL_SHORTAGE"` for UK occupations (e.g., SOC 2134 Programmers and software development professionals) violates licensing restrictions:

1. **Source Attribution:**
   - The shortage status does NOT originate from the Textkernel online advert feed.
   - It is sourced from `uk.gov.shortage` ("UK Immigration Salary List & Shortage Indicators", published by the UK Home Office / Migration Advisory Committee / Skills England).
2. **License Status:**
   - Sourced under Open Government Licence v3.0 (`OGL v3.0`).
   - `publication_status: "PUBLISHED"`.
3. **Conclusion:**
   - Qualitative shortage classifications are legally permitted for public display under OGL v3.0 and are independent of Textkernel digital advert telemetry.

---

### 5. TECHNICAL WITHHOLDING VERSUS LEGAL PERMISSION BOUNDARY

| Dimension | Audit Finding |
|---|---|
| **Technical Publication Gate** | **VERIFIED OPERATIONAL.** Server-side zeroing, empty time-series, and empty regional breakdowns prevent leakage across all public endpoints. |
| **Source-Use Permission** | **PERMITTED FOR INTERNAL RESEARCH.** Research and academic benchmarking permitted under ONS terms. |
| **Commercial Redistribution** | **WITHHELD / REVIEW REQUIRED.** Public commercial redistribution terms are under formal review. |
| **Public API Eligibility** | **WITHHELD.** No numeric time-series or regional series are published. |
| **Internal Audit Eligibility** | **PERMITTED.** Verified via `public_view=False` internal research parameter. |

---

### 6. AUDIT VERDICT

```text
UK PUBLICATION GATE AUDIT VERDICT: CLOSED WITH LIMITATIONS
Status: PASS (Technical Withholding Verified; 0 Leakage Detected)
Documented Limitation: Gated values serialize as 0.0 instead of null due to Pydantic float typing.
Legal Status: Technically gated; commercial redistribution review remains active.
```
