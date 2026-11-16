# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 1: STANDARDIZED PROVENANCE MODEL & DISCLOSURES

**Document ID:** `SPRINT3B2_2_PROVENANCE_DISCLOSURES`  
**Milestone:** Sprint 3B.2.2 — Provenance Hardening & Transparency  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Data Governance Architect & Frontend Lead  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

## 1. Executive Summary

In response to Sprint 3B.2.1 Audit finding #1 (where demand records were labeled with a generic official badge regardless of whether they were directly measured, scaled, or curated), Sprint 3B.2.2 establishes an explicit, standardized **Six-Tier Provenance Classification Framework**.

This framework eliminates the ambiguity between direct official publications, derived statistical transformations, and empirical benchmarks. Every demand observation in JobIntel 2.0 now programmatically exposes its exact provenance class, user-facing label, methodological description, transformation identifier, and derivation summary.

---

## 2. Six-Tier Semantic Provenance Architecture

```
   ┌────────────────────────────┬─────────────────────────────┬────────────────────────────────────────────────────────┐
   │ Internal Provenance Enum   │ User-Facing Label           │ Semantic Boundary & Evidentiary Standard               │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ OFFICIAL_PUBLISHED         │ Official statistic          │ Verbatim point census/survey from official agency;     │
   │                            │                             │ zero mathematical transformation or disaggregation.    │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ OFFICIALLY_DERIVED         │ Derived from official data  │ Grounded in published official statistics, but scaled, │
   │                            │                             │ annualized, or weighted via reproducible models.       │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ JOBINTEL_CURATED           │ JobIntel research benchmark │ Empirically collected, de-duplicated, and calibrated  │
   │                            │                             │ private or industry tech posting dataset.              │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ JOBINTEL_MODEL_ESTIMATE    │ Model-derived estimate      │ Machine learning or econometric regression output;     │
   │                            │                             │ not a direct empirical observation.                    │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ SYNTHETIC_TEST_FIXTURE     │ Test data                   │ Test fixture generated for system verification;        │
   │                            │                             │ strictly barred from public production display.        │
   ├────────────────────────────┼─────────────────────────────┼────────────────────────────────────────────────────────┤
   │ UNVERIFIED                 │ Verification pending        │ Evidence or licensing verification incomplete;         │
   │                            │                             │ must be withheld from public release.                  │
   └────────────────────────────┴─────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Schema Contract Implementation

The provenance model is formalized in Pydantic v2 schemas (`src/backend/schemas/demand.py`) and TypeScript interfaces (`frontend/src/types.ts`).

### 3.1 Pydantic Model (`src/backend/schemas/demand.py`)
```python
class DemandProvenance(StrEnum):
    OFFICIAL_PUBLISHED = "OFFICIAL_PUBLISHED"
    OFFICIALLY_DERIVED = "OFFICIALLY_DERIVED"
    JOBINTEL_CURATED = "JOBINTEL_CURATED"
    JOBINTEL_MODEL_ESTIMATE = "JOBINTEL_MODEL_ESTIMATE"
    SYNTHETIC_TEST_FIXTURE = "SYNTHETIC_TEST_FIXTURE"
    UNVERIFIED = "UNVERIFIED"

PROVENANCE_METADATA: dict[DemandProvenance, dict[str, str]] = {
    DemandProvenance.OFFICIAL_PUBLISHED: {
        "label": "Official statistic",
        "description": "Directly extracted from official government statistical agency releases or statutory censuses with no computational transformation.",
    },
    DemandProvenance.OFFICIALLY_DERIVED: {
        "label": "Derived from official data",
        "description": "Produced through reproducible calculation, annualization, employment-weighting, or taxonomy concordance from verified official input statistics.",
    },
    DemandProvenance.JOBINTEL_CURATED: {
        "label": "JobIntel research benchmark",
        "description": "Curated research benchmark compiled and validated by JobIntel Research Labs from empirical industry posting samples.",
    },
    DemandProvenance.JOBINTEL_MODEL_ESTIMATE: {
        "label": "Model-derived estimate",
        "description": "Econometric or machine learning model estimate based on multi-source feature modeling.",
    },
    DemandProvenance.SYNTHETIC_TEST_FIXTURE: {
        "label": "Test data",
        "description": "Synthetically generated test fixture for system validation. Not for real-world interpretation.",
    },
    DemandProvenance.UNVERIFIED: {
        "label": "Verification pending",
        "description": "Source provenance or licensing verification is currently pending review.",
    },
}
```

### 3.2 Observation & Profile Fields
Each `DemandObservation` and `OccupationDemandProfile` records:
- `provenance`: `DemandProvenance`
- `provenance_label`: Human-readable label (e.g., `"Derived from official data"`)
- `provenance_description`: Detailed explanatory context
- `transformation_method`: Machine-readable method token (e.g., `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS`)
- `derivation_summary`: Natural language summary of the exact mathematical or concordance transformation applied.

---

## 4. Frontend Provenance Presentation (`DemandPage.tsx`)

In `frontend/src/pages/DemandPage.tsx`, the UI never uses a generic "Official" label for derived or benchmark data.

### 4.1 UI Style & Visual Design Token Mapping

| Provenance Key | Badge Label | Text Color | Background Fill | Border Stroke |
|---|---|---|---|---|
| `OFFICIAL_PUBLISHED` | Official statistic | `#10B981` (Emerald) | `rgba(16, 185, 129, 0.12)` | `rgba(16, 185, 129, 0.3)` |
| `OFFICIALLY_DERIVED` | Derived from official data | `#00F0FF` (Cyan) | `rgba(0, 240, 255, 0.12)` | `rgba(0, 240, 255, 0.3)` |
| `JOBINTEL_CURATED` | JobIntel research benchmark | `#F59E0B` (Amber) | `rgba(245, 158, 11, 0.12)` | `rgba(245, 158, 11, 0.3)` |
| `JOBINTEL_MODEL_ESTIMATE` | Model-derived estimate | `#8B5CF6` (Purple) | `rgba(139, 92, 246, 0.12)` | `rgba(139, 92, 246, 0.3)` |
| `SYNTHETIC_TEST_FIXTURE` | Test data | `#EC4899` (Pink) | `rgba(236, 72, 153, 0.12)` | `rgba(236, 72, 153, 0.3)` |
| `UNVERIFIED` | Verification pending | `#94A3B8` (Slate) | `rgba(148, 163, 184, 0.12)` | `rgba(148, 163, 184, 0.3)` |

### 4.2 Interactive Expandable Provenance Ledger
Users can click the Provenance Badge in the Occupational Demand Explorer to toggle a detailed methodology ledger displaying:
1. Full evidentiary description.
2. Exact transformation method code.
3. Derivation narrative detailing baseline sources, weighting systems, and concordance concordats.

---

## 5. Audit Ledger Across All 28 Observations

All 28 demand observations in `src/backend/data/demand/observations.json` were enriched and validated:

| Market | Total Records | Assigned Provenance | Transformation Method | Audit Verdict |
|---|---|---|---|---|
| **United States** | 7 | `OFFICIALLY_DERIVED` | `BLS_TABLE_1_7_ANNUALIZED_PLUS_OEWS_STATE_WEIGHTS` | **VERIFIED** |
| **Australia** | 4 | `OFFICIALLY_DERIVED` | `JSA_IVI_4DIGIT_ANZSCO_TO_6DIGIT_OSCA_SCALING` | **VERIFIED** |
| **United Kingdom** | 8 | `OFFICIALLY_DERIVED` | `ONS_TEXTKERNEL_EXPERIMENTAL_INDEX` | **VERIFIED (WITHHELD)** |
| **Singapore** | 6 | `OFFICIALLY_DERIVED` | `MOM_PMET_SURVEY_VACANCIES_PLUS_PLANNING_AREA_PROXIES` | **VERIFIED** |
| **India** | 3 | `JOBINTEL_CURATED` | `JOBINTEL_EMPIRICAL_TECH_HUB_POSTINGS_BENCHMARK` | **VERIFIED BENCHMARK** |

**Zero observations claim `OFFICIAL_PUBLISHED` falsely.** All derived and benchmark series are transparently acknowledged.
