# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 2: REGIONAL ESTIMATES & CLASSIFICATION INHERITANCE DISCLOSURES

**Document ID:** `SPRINT3B2_2_REGIONAL_ESTIMATE_DISCLOSURES`  
**Milestone:** Sprint 3B.2.2 — Statistical Disclosure Hardening  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Data Governance Architect & Labour Statistics Specialist  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

## 1. Executive Summary

This document details the corrective disclosures implemented to address Sprint 3B.2.1 Audit findings regarding derived sub-national regional breakdowns and occupational taxonomy inheritance. 

Prior to this sprint, regional figures risked being interpreted as direct, independently measured local field surveys. Sprint 3B.2.2 implements explicit schema-level tags, UI disclosure banners, and methodological caveats across the United States, Australia, and Singapore modules.

---

## 2. Market-by-Market Derivation Framework

### 2.1 United States: Employment-Weighted State Allocations
- **Underlying National Metric:** U.S. Bureau of Labor Statistics (BLS) Employment Projections 2023–2033, Table 1.7 projected annual openings (e.g., 140,100 for Software Developers `15-1252`).
- **Derivation Mechanism:** State-level opening values (e.g., California 29,420, Texas 12,600, Washington 11,200) are computed by multiplying the national projected openings by state occupational employment shares from the BLS Occupational Employment and Wage Statistics (OEWS) May 2023 survey.
- **Mandatory User Disclosure:**
  > **ℹ️ Regional Disclosure:** *"State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."*
- **Temporal Nature Caveat:**
  > *"U.S. values represent 10-year annualized projected openings (growth plus replacement needs), not current spot vacancies."*

### 2.2 Australia: Four-Digit ANZSCO Classification Inheritance
- **Underlying Series:** Jobs and Skills Australia (JSA) Internet Vacancy Index (IVI), which publishes newly advertised online vacancies at the **four-digit ANZSCO unit group** level (e.g., `2613` Software and Applications Programmers).
- **Derivation Mechanism:** Detailed six-digit occupation figures (e.g., `261313` Software Engineer) are calculated by scaling the broader 4-digit unit group total using empirical staffing weights from the Australian Occupation Standard Classification (OSCA 2024).
- **Mandatory User Disclosure:**
  > **⚠️ Classification Inheritance Disclosure:** *"Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."*
- **Regional Note:** State-level shares reflect JSA IVI state series distributions.

### 2.3 Singapore: Modelled Planning Area Proxies
- **Underlying National Metric:** Ministry of Manpower (MOM) Job Vacancies Survey 2023/2024, Table 3 (Commonly Sought After PMETs) vacancy counts.
- **Derivation Mechanism:** Sub-national distributions (e.g., Central 72%, West 14%, East 8%) reflect urban planning area proxies based on enterprise tech cluster concentrations.
- **Mandatory User Disclosure Label:**
  ```text
  MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED
  ```
- **Explanatory Copy:**
  > *"Sub-national shares are planning area proxies derived from enterprise cluster estimates, not measured regional vacancy counts."*
- **Population Definition:** Clarifies that MOM survey covers private enterprises with at least 25 employees and the public sector.

---

## 3. Schema and Contract Integration

In `src/backend/schemas/demand.py`:

```python
class RegionalDemandPoint(BaseModel):
    region_code: str
    region_name: str
    value: float
    share_percentage: float | None = None
    index_vs_national: float | None = None
    is_derived: bool = False
    derivation_method: str | None = None
    disclosure_label: str | None = None

class OccupationDemandProfile(BaseModel):
    ...
    regional_disclosure: str | None = None
    occupation_inheritance_disclosure: str | None = None
    benchmark_disclosure: str | None = None
```

All 70 regional breakdown records in `src/backend/data/demand/observations.json` have `is_derived = True` (with `derivation_method` and `disclosure_label` populated) for US, AU, SG, and IN.

---

## 4. UI Implementation (`DemandPage.tsx`)

In `frontend/src/pages/DemandPage.tsx`:
1. The **Geographic & Regional Concentration** card inspects `occupationProfile.regional_disclosure` and renders a prominent, styled disclosure banner before the regional bars.
2. The **Classification Inheritance** notice is rendered in amber warning styling whenever a six-digit occupation is derived from a four-digit group.
3. On mobile and desktop layouts, disclosures are rendered inline above the charts without layout breakage.

---

## 5. Automated Verification

The disclosures are verified by automated tests in `tests/test_demand_intelligence.py`:
- `test_us_regional_allocation_disclosure`: Asserts presence of employment-weighting explanation.
- `test_au_occupation_inheritance_disclosure`: Asserts presence of 4-digit ANZSCO inheritance disclosure.
- `test_sg_modelled_regional_warning`: Asserts presence of `MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED` warning.

All tests pass with 100% compliance.
