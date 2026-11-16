# JOBINTEL 2.0 — SPRINT 3A FINAL REPORT
## Global Occupation Intelligence: Taxonomy, Classification Mapping & Canonical Occupation Registry

**Date:** November 16, 2026  
**Sprint:** 3A  
**Branch:** `staging/sprint2c3`  
**Baseline HEAD Commit:** `8a3ddbca38a46126a6d28d5802ff396a26e95af9`  
**Final Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (STRICTLY UNTOUCHED)  
**Status:** **PASS** (100% Unqualified Qualification)  
**Authors:** Principal Data Architect, Occupational Taxonomy Researcher, Backend Architect, Frontend Architect, QA Engineer  

---

## 1. Executive Summary

Sprint 3A successfully established the versioned, extensible **Global Occupation Intelligence** foundation for JOBINTEL 2.0 across all five target jurisdictions (India, United States, United Kingdom, Australia, Singapore) and the International Labour Organization's ISCO standard.

### Core Architectural Principle
> **"National occupation classifications remain authoritative within their respective jurisdictions. The canonical occupation layer is an interoperability layer, not a replacement for national standards."**

Rather than naively homogenizing occupational titles or forcing them through an obsolete universal bridge, JOBINTEL 2.0 preserves native national classifications (UK SOC 2020, US 2018 SOC, AU OSCA 2024 / ANZSCO 2022, SG SSOC 2024, IN NCO-2015, ILO ISCO-08). On top of these official systems, it introduces a lightweight, harmonized canonical career concept layer and direct bilateral concordance crosswalks backed by verifiable government correspondence tables, task concordance rubrics, explicit relationship types, and calibrated confidence scores.

---

## 2. Classification System Coverage

| Market | Official Classification System | Current Edition / Version | Governing Authority | Hierarchy Levels | Code Format | Official Tech Unit Groups / Specificity | License & Terms | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UK** | UK Standard Occupational Classification | SOC 2020 (Vol 1 & 2) | Office for National Statistics (ONS) | 4 Levels (Major $\to$ Sub-Major $\to$ Minor $\to$ Unit) | `^\d{4}$` (e.g. `2134`) | Unit Groups `2131`-`2139`, `3133`, `3544` | Open Government Licence v3.0 | **VERIFIED OFFICIAL** |
| **US** | Standard Occupational Classification | 2018 SOC | Bureau of Labor Statistics (BLS) | 4 Levels (Major $\to$ Minor $\to$ Broad $\to$ Detailed) | `^\d{2}-\d{4}$` (e.g. `15-1252`) | Major Group 15; separated `15-2051` Data Scientists, `15-1253` QA | Public Domain (US Gov Work) | **VERIFIED OFFICIAL** |
| **AU** | Occupation Standard Classification for Australia | OSCA 2024 *(Transition from ANZSCO)*| Australian Bureau of Statistics (ABS) & JSA | 5 Levels (Major $\to$ Sub-Major $\to$ Minor $\to$ Unit $\to$ Occ) | `^\d{6}$` (e.g. `261313`) | Sub-Major Group 26; modern AI, cloud, security, and data codes | CC BY 4.0 | **VERIFIED OFFICIAL** |
| **AU** | Australian & NZ Standard Classification | ANZSCO 2022 *(Historical Reference)* | Australian Bureau of Statistics (ABS) | 5 Levels | `^\d{6}$` | Pre-OSCA historical baseline | CC BY 4.0 | **VERIFIED OFFICIAL** |
| **SG** | Singapore Standard Occupational Classification | SSOC 2024 | Singapore Department of Statistics (SingStat) | 5 Levels (Major $\to$ Sub-Major $\to$ Minor $\to$ Unit $\to$ Occ) | `^\d{5}$` (e.g. `25121`) | Sub-Major Group 25; dedicated AI/ML (`25131`), Cloud (`25124`), DevOps (`25125`) | Singapore Open Data Licence | **VERIFIED OFFICIAL** |
| **SG** | Singapore Standard Occupational Classification | SSOC 2020 *(Historical Reference)* | Singapore Department of Statistics (SingStat) | 5 Levels | `^\d{5}$` | Pre-2024 historical baseline | Singapore Open Data Licence | **VERIFIED OFFICIAL** |
| **IN** | National Classification of Occupations | NCO-2015 | Directorate General of Employment (DGE) | 5 Levels (Division $\to$ Sub-Div $\to$ Group $\to$ Family $\to$ Occ) | `^\d{4}(\.\d{4})?$` (e.g. `2512.0100`) | Division 2, Sub-Division 25 (aligned with ISCO-08) | India Open Data (NDSAP) | **VERIFIED OFFICIAL** |
| **INT** | International Standard Classification | ISCO-08 | International Labour Organization (ILO) | 4 Levels (Major $\to$ Sub-Major $\to$ Minor $\to$ Unit) | `^\d{4}$` (e.g. `2512`) | Informative reference layer; rejected as universal pivot | UN / ILO Public Standards | **VERIFIED OFFICIAL** |

---

## 3. Data & Concordance Evidence

1. **Ingested Datasets Manifest (`src/backend/data/occupations/`):**
   - `classifications.json`: 8 systems, 3.8 KB.
   - `canonical_occupations.json`: 12 canonical concepts, 5.2 KB.
   - `national_occupations.json`: 30 core tech national occupations, 18.4 KB.
   - `mappings.json`: 31 concordance crosswalk records with full provenance, 22.1 KB.
2. **Quality & Integrity Metrics:**
   - Total parsed records: 81 records.
   - Rejected / malformed records: 0.
   - Invariant check: 100% of composite `occupation_id`s enforce `{classification_id}:{code}`.
   - Synthetic 1.00 score check: Enforced via Pydantic validator—only `VERIFIED_OFFICIAL` government tables may receive 1.00.
   - Negative state check: `UNMAPPED` and `NO_SUPPORTED_MAPPING` records enforce confidence = 0.00.
   - Approximation warning check: 100% of mappings with confidence $< 0.95$ generate an explicit approximation disclaimer.

---

## 4. API Endpoints Deliverable

All endpoints mounted under `/api/v1/occupations` and `/v1/occupations`:

1. `GET /v1/occupations/classifications` (supports `?market=UK`)
2. `GET /v1/occupations/classifications/{classification_id}`
3. `GET /v1/occupations/classifications/{classification_id}/occupations` (paginated)
4. `GET /v1/occupations/search?q={query}` (deterministic code $\to$ title $\to$ alias scoring)
5. `GET /v1/occupations/canonical`
6. `GET /v1/occupations/canonical/{canonical_id}`
7. `GET /v1/occupations/compare?source_occupation_id={id}`
8. `GET /v1/occupations/{occupation_id}/mappings`
9. `GET /v1/occupations/{occupation_id}`

---

## 5. Frontend Deliverables

1. **New UI Page (`frontend/src/pages/OccupationsPage.tsx`):**
   - Mode 1: **Cross-Market Concordance**: Compare any occupation across international standards with confidence percentages, relationship type badges, methodology, and approximation warnings. Includes explicit **Unmapped Jurisdictions** cards.
   - Mode 2: **National Taxonomy Explorer**: Filter by country/market, view official classification details, search by code or title, and explore tasks and entry routes.
   - Mode 3: **Canonical Career Concepts**: Explore harmonized international career archetypes and their core technical competencies.
2. **Navigation & Routing:**
   - Registered `/occupations` in `ROUTE_MAP` and `PAGE_TO_ROUTE` in `App.tsx`.
   - Added `Occupations` link to desktop and mobile navigation in `AppHeader.tsx`.
   - Verified deep-linking and SPA fallback.

---

## 6. Testing, Parity & Production Safety

1. **Occupation Intelligence Test Suite (`tests/test_occupation_intelligence.py`):**
   - 15 / 15 tests passed in 3.46s.
2. **Total Backend Regression Suite:**
   - Prior baseline: 297 passed.
   - Current suite: **312 Passed / 0 Failed** in 26.88s (100% pass).
3. **Frontend Test Suite:**
   - 9 / 9 tests passed in 46.52s.
4. **Production Build:**
   - TypeScript compilation and Vite build succeeded cleanly in 41.81s (2,892 modules transformed).
5. **Frozen Baseline Preservation:**
   - India and USA predictive models: Zero changes. Golden predictions for India (`₹11.13 LPA`) and USA (`$185,572.06`) reproduce identically.
   - UK ASHE salary data: Returns `HTTP 503 UK_DATA_NOT_PUBLISHED` fail-closed.
   - Production branch (`master`): Commit `198b79d` remains 100% untouched.

---

## 7. Limitations & Open Governance Disclosures

1. **India NCO-2015 Granularity:** NCO-2015 provides direct ISCO-08 correspondence but lacks granular unit groups for modern cloud/ML roles. JobIntel maintains both official NCO-2015 codes and documented crosswalks from verified industry role families.
2. **Australia OSCA vs. ANZSCO:** OSCA 2024 is the active standard; ANZSCO 2022 is preserved for historical backwards compatibility.
3. **Unmapped Occupations:** Certain specialized roles (e.g. niche regional trades) have no credible international equivalent. These are explicitly exposed as unmapped rather than forcibly matched.

---

## 8. Final Verdict

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      JOBINTEL 2.0 — SPRINT 3A                                 ║
║            GLOBAL OCCUPATION INTELLIGENCE QUALIFICATION: PASS                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
