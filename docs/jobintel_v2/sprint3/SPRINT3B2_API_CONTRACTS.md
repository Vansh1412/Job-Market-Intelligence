# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 API CONTRACT SPECIFICATION: GLOBAL JOB DEMAND INTELLIGENCE

**Document ID:** `SPRINT3B2_API_CONTRACTS`  
**Milestone:** Sprint 3B.2 — Phase 6 API Implementation & Contracts  
**Date:** 2026-11-16  
**Auditor / Authors:** Backend Architect, Principal QA Engineer, API Governance Lead  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  

---

### 1. OVERVIEW & PREFIX PARITY

All demand intelligence endpoints are exposed under two strictly synchronized route hierarchies to support frontends running with or without the `/api` prefix:
- Canonical Base: `/v1/demand/*`
- Legacy / Proxy Base: `/api/v1/demand/*`

Every endpoint produces strongly-typed JSON complying with Pydantic v2 schemas and RFC 7807 error envelopes when errors occur.

---

### 2. ENDPOINT SPECIFICATIONS

#### 2.1 Market Demand Overview
- **Method & Path:** `GET /v1/demand/markets` (and `/api/v1/demand/markets`)
- **Description:** Returns high-level demand coverage, primary instruments, and observation totals across all 5 supported markets (US, AU, UK, SG, IN).
- **Query Parameters:** None.
- **Success Response (200 OK):**
```json
[
  {
    "market_id": "US",
    "market_name": "United States",
    "coverage_status": "AVAILABLE",
    "total_observations": 7,
    "primary_source_id": "us.bls.ep",
    "primary_source_name": "US BLS Employment Projections 2023-2033",
    "primary_metric_type": "ANNUAL_JOB_OPENINGS",
    "metric_label": "Annual Average Openings (2023-2033)",
    "license": "Public Domain (17 U.S.C. § 105)"
  },
  {
    "market_id": "AU",
    "market_name": "Australia",
    "coverage_status": "AVAILABLE",
    "total_observations": 4,
    "primary_source_id": "au.jsa.ivi",
    "primary_source_name": "Jobs and Skills Australia Internet Vacancy Index",
    "primary_metric_type": "OBSERVED_JOB_ADVERTISEMENTS",
    "metric_label": "Monthly Online Job Adverts Index",
    "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)"
  }
]
```

#### 2.2 Demand Metric Definitions
- **Method & Path:** `GET /v1/demand/metrics`
- **Description:** Returns metadata, underlying economic constructs, and statistical limitations for all 7 demand metric types.
- **Success Response (200 OK):** Array of `DemandMetricDefinition` objects.

#### 2.3 Demand Sources Catalog
- **Method & Path:** `GET /v1/demand/sources`
- **Description:** Returns official source citations, publishers, canonical URLs, update cycles, and legal licenses.
- **Success Response (200 OK):** Array of source metadata objects.

#### 2.4 List Demand Observations
- **Method & Path:** `GET /v1/demand/occupations`
- **Query Parameters:**
  - `market` (optional, string): 2-letter market code (`US`, `AU`, `UK`, `SG`, `IN`).
  - `canonical_id` (optional, string): Canonical occupation concept identifier.
  - `metric_type` (optional, string): Demand metric type filter.
- **Success Response (200 OK):** Array of `DemandObservation` objects (28 records total).

#### 2.5 Detailed Occupation Demand Profile
- **Method & Path:** `GET /v1/demand/occupations/{occupation_id}`
- **Path Parameters:**
  - `occupation_id` (string): National occupation identifier (e.g. `15-1252`, `261313`, `2134`) or canonical concept.
- **Query Parameters:**
  - `market` (string, default: `"US"`): Market identifier.
- **Success Response (200 OK):** `OccupationDemandProfile` object.
```json
{
  "occupation_id": "US_SOC_2018:15-1252",
  "occupation_title": "Software Developers",
  "market_id": "US",
  "canonical_id": "CAN_OCC_SOFTWARE_ENGINEER",
  "canonical_title": "Software Engineer",
  "primary_metric_type": "ANNUAL_JOB_OPENINGS",
  "primary_metric_value": 140100.0,
  "primary_metric_unit": "Annual Openings",
  "reference_period": "2023-2033",
  "trend_direction": "STRONG_GROWTH",
  "trend_percentage_change": 17.0,
  "trend_time_series": [
    {"period": "2021", "value": 128500.0, "is_projected": false},
    {"period": "2024", "value": 140100.0, "is_projected": false},
    {"period": "2033-Projected", "value": 165000.0, "is_projected": true}
  ],
  "regional_distribution": [
    {"region_code": "CA", "region_name": "California", "value": 29420.0, "share_percentage": 21.0, "index_vs_national": 150.0}
  ],
  "top_skills": [
    {"skill_name": "Python", "category": "PROGRAMMING_LANGUAGE", "importance_score": 92.0, "frequency_percentage": 68.5, "growth_rate": 8.2, "is_hot_skill": true}
  ],
  "shortage_status": "NO_SHORTAGE",
  "future_demand_rating": "Much faster than average (+17%)",
  "source_attributions": [
    {
      "source_id": "us.bls.ep",
      "source_name": "US BLS Employment Projections 2023-2033",
      "publisher": "U.S. Bureau of Labor Statistics",
      "license": "Public Domain (17 U.S.C. § 105)"
    }
  ],
  "methodology_disclaimers": [
    "Biased toward digital-first and professional occupations."
  ]
}
```

#### 2.6 Sub-Resource Endpoints
- `GET /v1/demand/occupations/{occupation_id}/trends`: Returns `time_series`, `trend_direction`, and `percentage_change`.
- `GET /v1/demand/occupations/{occupation_id}/regions`: Returns array of `RegionalDemandPoint`.
- `GET /v1/demand/occupations/{occupation_id}/skills`: Returns array of `SkillDemandItem`.

#### 2.7 11-Dimension Cross-Market Demand Comparison
- **Method & Path:** `GET /v1/demand/compare`
- **Query Parameters:**
  - `canonical_id` (string, required): e.g. `CAN_OCC_SOFTWARE_ENGINEER`.
  - `market_a` (string, required): e.g. `US`.
  - `market_b` (string, required): e.g. `AU`.
- **Success Response (200 OK):** `DemandComparisonResult` object evaluating all 11 dimensions with overall verdict (`METHODOLOGICALLY_DISTINCT`, `DIRECTIONALLY_COMPARABLE`, `DIRECTLY_COMPARABLE`, `NOT_COMPARABLE`).

#### 2.8 Skill Gap Analysis
- **Method & Path:** `POST /v1/demand/skills/gaps`
- **Request Body:**
```json
{
  "target_occupation_id": "15-1252",
  "market_id": "US",
  "user_skills": ["Python", "Java", "SQL", "Git"]
}
```
- **Success Response (200 OK):** `SkillGapAnalysisResult` detailing matched skills, missing critical skills, missing secondary skills, match percentage, readiness tier, and learning recommendations.
