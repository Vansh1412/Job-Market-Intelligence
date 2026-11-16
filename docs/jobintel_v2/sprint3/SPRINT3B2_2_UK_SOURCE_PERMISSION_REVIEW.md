# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 3: UK ONS / TEXTKERNEL SOURCE PERMISSION REVIEW & PUBLICATION GATE

**Document ID:** `SPRINT3B2_2_UK_SOURCE_PERMISSION_REVIEW`  
**Milestone:** Sprint 3B.2.2 — Governance & Licensing Enforcement  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Data Governance Architect & Release Governance Lead  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

## 1. Executive Summary

This document presents the source permission review of the United Kingdom labour demand dataset utilized in JobIntel 2.0. Following the independent audit finding of unresolved third-party licensing conditions, this sprint formally classifies the source as **`REVIEW_REQUIRED`** and implements an automated, leak-proof **Server-Side Publication Gate**.

Under this publication gate, all UK demand metrics, index numbers, time series, and regional points are withheld from public APIs and frontend views, while preserving the existing UK salary HTTP 503 fail-closed boundary independently.

---

## 2. Source Provenance & Rights Analysis

### 2.1 Dataset Provenance
- **Official Title:** *Labour demand volumes by Standard Occupational Classification (SOC 2020), UK*
- **Publishing Institution:** Office for National Statistics (ONS)
- **Partner / Data Provider:** Textkernel BV (an Amsterdam-based HR technology and job vacancy parsing provider)
- **Primary Canonical URL:** `https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourdemandvolumesbystandardoccupationalclassificationsoc2020uk`
- **Series Nature:** Experimental statistical index (Base 2019 = 100) tracking weekly and monthly online job adverts.

### 2.2 Legal & Licensing Evaluation

```
   ┌───────────────────────────────────┬────────────────────────────────────────────────────────┐
   │ Licensing Dimension               │ Legal Evaluation & Finding                             │
   ├───────────────────────────────────┼────────────────────────────────────────────────────────┤
   │ Crown Copyright / OGL v3.0        │ The ONS editorial report and headline publications     │
   │                                   │ are released under Open Government Licence v3.0.       │
   ├───────────────────────────────────┼────────────────────────────────────────────────────────┤
   │ Third-Party Proprietary Feeds     │ The underlying digital vacancy scraping, entity        │
   │                                   │ resolution, and deduplication are provided by          │
   │                                   │ Textkernel BV under commercial partnership terms.      │
   ├───────────────────────────────────┼────────────────────────────────────────────────────────┤
   │ Commercial SaaS Redistribution    │ OGL v3.0 excludes third-party rights. Terms regarding  │
   │                                   │ whether third parties may re-distribute or re-host     │
   │                                   │ index series within a commercial SaaS platform are     │
   │                                   │ ambiguous and require legal confirmation.              │
   ├───────────────────────────────────┼────────────────────────────────────────────────────────┤
   │ Governance Determination          │ Status set to: REVIEW_REQUIRED                         │
   │                                   │ Strict fail-closed publication gate enforced.          │
   └───────────────────────────────────┴────────────────────────────────────────────────────────┘
```

**Legal Conclusion:** In accordance with strict data governance standards, public availability on a government portal does **not** constitute authorization for third-party commercial software redistribution. Until unambiguous written confirmation or a commercial redistribution licence is established, the source must remain withheld from public release.

---

## 3. Server-Side Publication Gate Architecture

The publication gate is implemented across the schema, service, and routing layers:

### 3.1 Registry Metadata (`sources.json`)
```json
{
  "source_id": "uk.ons.labour-demand",
  "source_name": "ONS Labour Demand Volumes by SOC 2020",
  "publisher": "Office for National Statistics (ONS) / Textkernel",
  "canonical_url": "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourdemandvolumesbystandardoccupationalclassificationsoc2020uk",
  "license": "Open Government Licence v3.0 (OGL v3.0) / Textkernel Terms Under Review",
  "publication_status": "REVIEW_REQUIRED",
  "rights_notice": "Experimental statistics compiled by ONS using Textkernel online job vacancy data. Commercial SaaS redistribution and derived index redistribution terms are currently subject to review.",
  "allowed_use": ["INTERNAL_RESEARCH", "ACADEMIC_EVALUATION"],
  "restricted_use": ["PUBLIC_REDISTRIBUTION", "COMMERCIAL_SAAS_DISPLAY"]
}
```

### 3.2 Service Layer Enforcement (`demand_service.py`)
1. **Public vs. Internal View Distinction:**
   - Public view (`public_view=True`, default for all API endpoints): Withholds numeric index data.
   - Internal view (`public_view=False`): Allows read-only access for internal research and audits.
2. **Leak Prevention Mechanism:**
   When `publication_status == "REVIEW_REQUIRED"`:
   - `profile.publication_gate_active = True`
   - `profile.publication_gate_code = "UK_DEMAND_DATA_NOT_PUBLISHED"`
   - `profile.publication_gate_message = "UK demand data is currently withheld pending source-use and redistribution review."`
   - `profile.primary_metric_value = 0.0`
   - `profile.trend_time_series = []` (no historical numbers in payload)
   - `profile.regional_distribution = []` (no regional numbers in payload)
   - `profile.trend_direction = DemandTrendDirection.INSUFFICIENT_DATA`

### 3.3 Public API Endpoint Protection (`routers/demand.py`)
- `/v1/demand/occupations?market=UK`: Sanitizes all 8 UK observation records (`value: 0.0`, `time_series: []`, `regional_breakdown: []`, `notes: "UK_DEMAND_DATA_NOT_PUBLISHED: Withheld pending source-use and redistribution review."`).
- `/v1/demand/occupations/{id}?market=UK`: Returns profile with `publication_gate_active: True` and zeroed metric data.
- `/v1/demand/occupations/{id}/trends?market=UK`: Returns empty `time_series: []` and gate active flag.
- `/v1/demand/occupations/{id}/regions?market=UK`: Returns empty array `[]`.

---

## 4. Frontend Unavailable State Presentation (`DemandPage.tsx`)

In `frontend/src/pages/DemandPage.tsx`:
When `occupationProfile.publication_gate_active` is true:
1. **Prominent Alert Banner:** Displays red-bordered shield alert informing the user:
   > *"UK demand data is currently withheld pending source-use and redistribution review."*
2. **Governance Notice:**
   > *"ONS experimental online advert volumes utilize third-party job vacancy feeds from Textkernel BV. While UK shortage occupations from the Home Office Immigration Salary List remain accessible, numeric advertisement index distributions are withheld pending commercial redistribution and licensing review."*
3. **Data Masking:** Replaces the primary demand volume card with `WITHHELD PENDING REVIEW` in bold red text. Time series and regional cards display withheld notices. Zero restricted values exist in the client DOM or network responses.

---

## 5. Independent UK Salary 503 Isolation

The UK descriptive salary API gate remains completely isolated and enforced:
- Endpoint: `/api/v1/markets/UK/salary/occupations`
- Response: HTTP 503 `UK_DATA_NOT_PUBLISHED`
- Tested across all 14 tests in `tests/test_uk_salary_api.py` (100% pass).

The demand publication gate does not interfere with or weaken salary governance.
