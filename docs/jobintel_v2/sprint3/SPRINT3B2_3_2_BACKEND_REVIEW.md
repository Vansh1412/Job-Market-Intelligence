# JOBINTEL 2.0 — SPRINT 3B.2.3.2
# PHASE 2 — BACKEND DIFF & ARCHITECTURE REVIEW

**Sprint:** 3B.2.3.2 — Final Diff Review & Controlled Staging Commit Preparation  
**Date:** 2026-11-16  
**Auditor:** Principal Backend Architect & Pydantic Specialist  

---

## 1. Executive Summary

A comprehensive diff audit was conducted across all backend modifications introduced throughout the Sprint 3B.2 series:
- `src/backend/schemas/demand.py`
- `src/backend/services/demand_service.py`
- `src/backend/routers/demand.py`
- `src/backend/main.py`

All backend changes adhere strictly to architectural separation of concerns, data governance, fail-closed access gating, and statistical disclosure requirements.

---

## 2. Demand Provenance & Data Model Verification

### 2.1 Provenance Taxonomy
The `DemandProvenance` enumeration in `src/backend/schemas/demand.py` strictly categorizes observations into 6 formal provenance tiers:
1. `OFFICIAL_PUBLISHED`: Directly extracted from government statistical releases (e.g., BLS, JSA, MOM) with no computational transformation.
2. `OFFICIALLY_DERIVED`: Derived through reproducible calculation, annualization, employment-weighting, or taxonomy concordance.
3. `JOBINTEL_CURATED`: Curated research benchmark compiled from empirical job posting samples (e.g., India tech hub benchmark).
4. `JOBINTEL_MODEL_ESTIMATE`: Econometric or ML model estimates based on multi-source feature modeling.
5. `SYNTHETIC_TEST_FIXTURE`: Synthetically generated test fixture for validation.
6. `UNVERIFIED`: Verification pending review.

Each tier maps to verified human-readable labels and descriptions in `PROVENANCE_METADATA`.

### 2.2 Observation Integrity
All 28 demand observations in `src/backend/data/demand/observations.json` retain their explicit provenance classification, transformation methodology notes, and reference periods. No synthetic or invented source identifiers exist.

---

## 3. UK Publication Gate & Serialization Review

### 3.1 Fail-Closed Publication Gate
In `src/backend/services/demand_service.py`:
- `is_gate_active = (src.get("publication_status") == "REVIEW_REQUIRED") or (m_val == MarketId.UK)`
- When active and `public_view=True`:
  - `metric_val = None`
  - `time_series = []`
  - `reg_dist = []`
  - `trend_dir = DemandTrendDirection.INSUFFICIENT_DATA`
  - `trend_pct = None`
  - `publication_gate_active = True`
  - `publication_gate_code = "UK_DEMAND_DATA_NOT_PUBLISHED"`
  - `publication_gate_message = "UK demand data is currently withheld pending source-use and redistribution review."`

### 3.2 Semantic Serialization Integrity (Remediated in 3B.2.3.1)
- `DemandObservation.value` and `OccupationDemandProfile.primary_metric_value` are typed as `float | None = None`.
- Serialized JSON produces `"primary_metric_value": null` instead of `0.0`.
- Genuine measured zeros (if observed) are retained as `0.0`.
- Cross-market comparison sanitizes withheld market values to `null` while leaving the unwithheld market intact.

---

## 4. Qualitative Shortage Independence

The separate government shortage source `uk.gov.shortage` is verified:
- Source Name: UK Home Office / Migration Advisory Committee (MAC) Shortage List
- Publisher: UK Home Office / Migration Advisory Committee
- License: **Open Government Licence v3.0 (OGL v3.0)**
- Independence: Crown copyright allows unrestricted commercial and non-commercial re-use. Qualitative shortage determinations (`"Shortage"`, `"Eligible skilled worker shortage"`) are completely independent of Textkernel digital vacancy volume data.

---

## 5. Regional Disclosures & Statistical Caveats

The backend service automatically injects mandatory statistical disclaimers and disclosures into every occupation profile:
- **United States:** `"State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."` (BLS 10-year annualized projection caveat included).
- **Australia:** `"Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."` (JSA IVI regional distribution disclaimer included).
- **Singapore:** `"MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED. Sub-national shares are planning area proxies derived from enterprise cluster estimates."`
- **India:** `"Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."`

---

## 6. API Stability & Regression Invariance

- Mount points in `src/backend/main.py`:
  - Mounts `demand.router` under `/api` and `/`.
  - Zero modification to existing salary (`/v1/salary/*`), occupation (`/v1/occupations/*`), health (`/health`), or readiness (`/ready`) routers.
- Response models across all existing endpoints remain 100% backward-compatible.
- No existing tests or model workflows are disturbed.
