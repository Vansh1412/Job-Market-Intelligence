# JOBINTEL 2.0 — SPRINT 3B.2.3.1
# UK PUBLICATION STATE SERIALIZATION & API SEMANTICS

**Sprint:** 3B.2.3.1 — UK Publication State Serialization Remediation  
**Status:** COMPLETE & VERIFIED  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Backend Architect, Pydantic v2 Specialist & Data Governance Engineer  

---

## 1. Executive Summary & Semantic Defect Resolution

During the Sprint 3B.2.3 independent audit, finding **F-05 / F-08** established that UK demand metrics withheld pending source-use review were serialized across the REST API as `0.0`. This occurred because the Pydantic schemas typed `value` in `DemandObservation` and `primary_metric_value` in `OccupationDemandProfile` as non-nullable `float`.

In statistical and labor-market data systems, conflating an unavailable or withheld metric with a measured zero constitutes a severe semantic defect:
- `0.0` denotes a measured observation: zero job vacancies, zero posting volume, or total market absence.
- `null` (`None`) denotes an unmeasured, withheld, or unavailable value.

In Sprint 3B.2.3.1, this semantic defect was definitively remediated by migrating field types to nullable `float | None = None` in Python/Pydantic, updating service sanitization to emit `None`, and updating TypeScript schemas to `number | null`.

---

## 2. Definitive Semantic State Taxonomy

The JOBINTEL 2.0 Demand Intelligence API now strictly enforces three distinct states across all serialization endpoints:

| Semantic State | Python Value | JSON Representation | TypeScript Representation | Frontend Presentation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Measured Non-Zero** | `float` (e.g., `12450.0`) | `12450.0` | `number` | Formatted number (`"12,450"`) | Empirically observed demand metric. |
| **Measured Zero** | `float` (`0.0`) | `0.0` | `number` (`0`) | `"0"` | Measured empirical observation of zero postings or vacancies. |
| **Withheld Pending Review** | `None` (`publication_gate_active=True`) | `null` | `null` | `"WITHHELD PENDING REVIEW"` | Data withheld under governance publication gate pending licensing/source review. |
| **Unavailable / Missing** | `None` (`publication_gate_active=False`) | `null` | `null` | `"Not available"` | Metric not collected or unavailable for this occupation/market. |

---

## 3. Schema Modifications (`src/backend/schemas/demand.py`)

### 3.1 `DemandObservation` Schema
Prior to remediation:
```python
class DemandObservation(BaseModel):
    # ...
    value: float = Field(..., description="Value of the observation")
```

Remediated schema:
```python
class DemandObservation(BaseModel):
    # ...
    value: float | None = Field(
        None,
        description="Value of the observation, or None if withheld pending review or unavailable"
    )
```

### 3.2 `OccupationDemandProfile` Schema
Prior to remediation:
```python
class OccupationDemandProfile(BaseModel):
    # ...
    primary_metric_value: float = 0.0
```

Remediated schema:
```python
class OccupationDemandProfile(BaseModel):
    # ...
    primary_metric_value: float | None = Field(
        None,
        description="Primary metric value, or None if withheld pending review or unavailable"
    )
```

---

## 4. Service-Layer Sanitization (`src/backend/services/demand_service.py`)

The service layer controls public-view filtering and guarantees zero data leakage of raw withheld figures:

### 4.1 Observations Listing Sanitization (`list_observations`)
```python
if public_view:
    # Filter out observations from withheld markets or sanitize value
    sanitized = []
    for obs in results:
        if obs.get("country_code") in WITHHELD_MARKETS:
            sanitized_obs = dict(obs)
            sanitized_obs["value"] = None  # Correct semantic representation of withheld data
            sanitized.append(sanitized_obs)
        else:
            sanitized.append(obs)
    results = sanitized
```

### 4.2 Single Occupation Demand Profile (`get_occupation_demand_profile`)
```python
if public_view and is_withheld:
    metric_val = None  # Nullable: distinguishes withheld from measured 0.0
    time_series = []   # Withheld from public view
    reg_dist = []      # Withheld from public view
```

### 4.3 Market Comparability (`compare_demand`)
```python
if is_withheld_a:
    val_a = None
if is_withheld_b:
    val_b = None
```

---

## 5. JSON Serialization Comparison

### 5.1 UK Profile API Response (`/api/v1/demand/occupations/2136?country_code=GBR`)

#### Before Remediation (Sprint 3B.2.2 Defect):
```json
{
  "occupation_code": "2136",
  "occupation_title": "Programmers and software development professionals",
  "country_code": "GBR",
  "country_name": "United Kingdom",
  "primary_metric_name": "Online Job Postings (Indexed)",
  "primary_metric_value": 0.0,
  "publication_gate_active": true,
  "trend_direction": "stable",
  "qualitative_shortage_status": "Shortage",
  "shortage_evidence_source": "UK Migration Advisory Committee (MAC) Shortage List",
  "trend_time_series": [],
  "regional_distribution": []
}
```
*Defect:* `primary_metric_value: 0.0` falsely implied zero job postings existed in the UK.

#### After Remediation (Sprint 3B.2.3.1 Verified):
```json
{
  "occupation_code": "2136",
  "occupation_title": "Programmers and software development professionals",
  "country_code": "GBR",
  "country_name": "United Kingdom",
  "primary_metric_name": "Online Job Postings (Indexed)",
  "primary_metric_value": null,
  "publication_gate_active": true,
  "trend_direction": "stable",
  "qualitative_shortage_status": "Shortage",
  "shortage_evidence_source": "UK Migration Advisory Committee (MAC) Shortage List",
  "trend_time_series": [],
  "regional_distribution": []
}
```
*Integrity:* `primary_metric_value: null` strictly conveys withheld status.

---

### 5.2 Market Comparison API Response (`/api/v1/demand/compare?code_a=15-1252&country_a=USA&code_b=2136&country_b=GBR`)

#### Before Remediation:
```json
{
  "market_a": { "country_code": "USA", "value": 154200.0, "unit": "Annual Openings" },
  "market_b": { "country_code": "GBR", "value": 0.0, "unit": "Online Job Postings (Indexed)" },
  "comparability_verdict": "NOT DIRECTLY COMPARABLE"
}
```

#### After Remediation:
```json
{
  "market_a": { "country_code": "USA", "value": 154200.0, "unit": "Annual Openings" },
  "market_b": { "country_code": "GBR", "value": null, "unit": "Online Job Postings (Indexed)" },
  "comparability_verdict": "NOT DIRECTLY COMPARABLE"
}
```

---

## 6. Qualitative Shortage Independence

An essential architectural requirement confirmed during remediation is that qualitative shortage intelligence for the UK remains fully operational and independent of the raw posting volume:
- `qualitative_shortage_status`: `"Shortage"`
- `shortage_evidence_source`: `"UK Migration Advisory Committee (MAC) Shortage List"`
- Backing Source ID: `uk.gov.shortage` in `src/backend/data/demand/sources.json`.
- Licensing: Crown Copyright / Open Government Licence v3.0 (OGL v3.0).

Because OGL v3.0 freely permits commercial and non-commercial re-use, public presentation of MAC shortage determinations is legally sound and fully independent of Textkernel digital posting metrics.
