# JOBINTEL 2.0 — SPRINT 3A
## Repository & Architecture Audit: Global Occupation Intelligence

**Date:** November 16, 2026  
**Sprint:** 3A  
**Branch:** `staging/sprint2c3`  
**Baseline HEAD Commit:** `8a3ddbca38a46126a6d28d5802ff396a26e95af9`  
**Production Master Commit:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (UNTOUCHED)  
**Author:** Principal Data Architect, Occupational Taxonomy Researcher, Backend & QA Engineer  

---

## 1. Executive Summary

Sprint 3A establishes the **Global Occupation Intelligence** foundation for JOBINTEL 2.0. This audit verifies the current repository baseline, identifies existing classification and taxonomy assets, maps structural dependencies, and outlines the architectural blueprint for versioned national occupation registries, canonical interoperability concepts, and evidence-backed concordance crosswalks.

### Central Architectural Invariant
> **"National occupation classifications remain authoritative within their respective jurisdictions. The canonical occupation layer is an interoperability layer, not a replacement for national standards."**

---

## 2. Git and Deployment State

| Parameter | Value | Verification Status |
| :--- | :--- | :--- |
| **Active Branch** | `staging/sprint2c3` | `VERIFIED LOCALLY` |
| **Current HEAD SHA** | `8a3ddbca38a46126a6d28d5802ff396a26e95af9` | `VERIFIED LOCALLY` |
| **Tracking Remote** | `origin/staging/sprint2c3` | Up to date (`VERIFIED LOCALLY`) |
| **Master Production SHA** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | Strictly Untouched (`VERIFIED LOCALLY`) |
| **Working Tree** | Clean (0 modified tracked files, 0 staged files) | `VERIFIED LOCALLY` |
| **Staging Backend** | `https://jobintel-backend-staging.onrender.com` | Operational (`VERIFIED VIA HTTP`) |
| **Staging Frontend** | `https://jobintel-staging.vercel.app` | Operational, Deep-linking Ready (`VERIFIED IN BROWSER`) |

---

## 3. Existing Market & Taxonomy Architecture Audit

### 3.1 Five-Market Foundation (`src/backend/markets/registry.py`)
The existing market registry exposes five distinct national jurisdictions with explicit occupational metadata:

1. **India (`IN`):**
   - Currency: `INR`
   - Classification metadata: `"JobIntel India role families; no national occupational crosswalk is integrated."`
   - Predictive model: HistGradientBoostingRegressor (290 raw features $\to$ 327 model inputs).
   - Role families: 15 internal categories defined in `src/india/role_mapping.py` (e.g. "AI / ML Engineer", "Data Scientist", "Data Engineer", "Data Analyst", "Business Analyst", "Software Engineer").
2. **United States (`US`):**
   - Currency: `USD`
   - Classification metadata: `"JobIntel USA role families; no national occupational crosswalk is integrated."`
   - Predictive model: XGBRegressor (123 model inputs).
   - Role families: 18 internal categories defined in `src/backend/services/usa_service.py` (e.g. "ML / AI Engineer", "Data Scientist", "Data Engineer", "Data / BI Analyst", "Software Engineer").
3. **United Kingdom (`UK`):**
   - Currency: `GBP`
   - Classification metadata: `"UK Standard Occupational Classification"`, version `"SOC 2020"`.
   - Primary source ID: `uk.ons.soc2020` and `uk.ons.ashe`.
   - Descriptive intelligence status: Fail-closed HTTP 503 (`UK_DATA_NOT_PUBLISHED`).
4. **Australia (`AU`):**
   - Currency: `AUD`
   - Classification metadata: `"Occupation Standard Classification for Australia"`, version `"OSCA 2024"`.
   - Primary source ID: `au.abs.osca`.
   - Capability state: Initial descriptive intelligence.
5. **Singapore (`SG`):**
   - Currency: `SGD`
   - Classification metadata: `"Singapore Standard Occupational Classification"`, version `"SSOC 2024"`.
   - Primary source ID: `sg.singstat.ssoc2024`.
   - Capability state: Initial descriptive intelligence.

### 3.2 Existing Classification Standard (`SPRINT2C_CLASSIFICATION_GOVERNANCE_STANDARD.md`)
The repository contains an approved engineering standard (`JOBINTEL-S2C-STD-004`) establishing:
- **Preservation of Native National Classifications:** Official taxonomies remain primary; no forced homogenization.
- **Rejection of ISCO-08 as an Automatic Universal Pivot:** Ratified in 2008, ISCO-08 collapses modern technology roles into generic buckets (e.g. `2512` Software Developers merges software engineers, mobile developers, cloud engineers, and architects). ISCO is secondary/reference only.
- **5-State Crosswalk Taxonomy:** `EXACT_EQUIVALENCE`, `ONE_TO_MANY`, `MANY_TO_ONE`, `PARTIAL_OVERLAP`, `UNMAPPABLE`.
- **Evidence-Backed Confidence Scoring:** No synthetic 1.00 scores; requires documented methodology (`OFFICIAL_CROSSWALK`, `EXPERT_ASSESSMENT`, `CALIBRATED_MODEL_SCORE`).
- **Graph Consistency Invariants:** Version isolation, transitivity consistency, and bidirectional symmetry/asymmetry rules.

---

## 4. Existing Data Assets Audit

| Asset Location | Classification / Dataset | Format | Version | Record Count | Unique Codes | License / Source | Status in Repo |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `data/raw/ashe_table15_2025_revised/soc2020_reference/soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx` | UK SOC 2020 Structure & Descriptions | Excel (.xlsx) | SOC 2020 Vol 1 | 552 rows (412 4-digit unit groups) | 412 unit groups | UK ONS (Open Government Licence v3.0) | **Verified Local Official Source** |
| `data/raw/ashe_table15_2025_revised/` | UK ASHE Table 15 Earnings by SOC 2020 | Excel / CSV | 2025 revised | 412 occupations $\times$ 11 regions | 412 unit groups | UK ONS (OGL v3.0) | Local Ingestion Pipeline (Fail-Closed) |
| `data/raw/india/indian-job-market-dataset-2025.xlsx` | India Market Postings | Excel (.xlsx) | 2025 Sample | 6,800 rows | 15 internal role families | JobIntel Project Data | Raw Model Training Source |
| `data/raw/dataset_A/` & `dataset_B/` | US Job Postings | Parquet / CSV | 2024-2026 | ~150k rows | 18 internal role families | JobIntel Project Data | Raw Model Training Source |

---

## 5. Gap Analysis: Existing vs. Missing Capabilities

### Existing Capabilities
1. `MarketRegistry` with occupational classification metadata for all 5 markets (`src/backend/markets/registry.py`).
2. `SourceRegistry` containing official source definitions for `au.abs.osca`, `uk.ons.soc2020`, `sg.singstat.ssoc2024` (`src/backend/data_catalog/registry.py`).
3. Complete UK SOC 2020 4-digit unit group database (412 unit groups with titles, descriptions, tasks, qualification entry routes, and related job titles).
4. Automated ASHE ingestion pipeline with strict SOC 2020 code and hierarchy validation (`src/backend/ingestion/ashe2025.py`).
5. 297/297 passing backend test baseline and 9/9 passing frontend vitest baseline.

### Missing Capabilities (Sprint 3A Scope)
1. **No Unified Classification System Registry:** There is no schema or service for querying official classification metadata across all five markets.
2. **No National Occupation Registries for US, India, Australia, Singapore:** While UK SOC 2020 is parsed locally for ASHE validation, there is no normalized, queryable multi-country occupation store.
3. **No Canonical Occupation Concept Layer:** No interoperable abstraction linking equivalent roles across national boundaries.
4. **No Concordance / Crosswalk Store:** No evidence-backed mapping records connecting national occupation codes with explicit relationship types, confidence scores, and provenance.
5. **No Occupation API Endpoints:** No endpoints under `/api/v1/occupations/...`.
6. **No Occupation UI in Frontend:** Frontend has no view for exploring national classifications or viewing cross-market mappings.

---

## 6. Architectural Constraints & Risks

1. **Model Safety & Frozen Contracts:** Existing India HistGradientBoostingRegressor and USA XGBRegressor models rely on fixed feature orders and internal role families. The canonical occupation layer must be purely additive and must NOT alter model inference or feature vectors.
2. **UK Salary Data Gate:** UK ASHE salary data must remain under fail-closed HTTP 503 (`UK_DATA_NOT_PUBLISHED`). Occupation taxonomy metadata (titles, descriptions, codes) is public under OGL v3.0 and can be explored independently of salary figures.
3. **Licensing & Redistribution Rights:**
   - UK SOC 2020: ONS Open Government Licence (OGL v3.0) allows free commercial/non-commercial reuse with attribution.
   - US SOC: BLS / Federal Government works are in the US public domain.
   - Australia OSCA 2024 / ANZSCO: ABS materials are published under Creative Commons Attribution 4.0 International (CC BY 4.0).
   - Singapore SSOC 2024: Singapore Open Data Licence permits reuse with attribution.
   - India NCO: Ministry of Labour & Employment published NCO-2015. Government open data principles apply, but unit group coverage in modern tech is limited.
4. **Zero Paid Infrastructure:** Classification registries and mappings must be stored efficiently (versioned JSON / memory-mapped registries) without requiring PostgreSQL or external search services.

---

## 7. Recommended Implementation Approach

1. **Phase 1 (Research):** Complete research on official systems: US SOC (2018), UK SOC (2020), Australia OSCA (2024) & ANZSCO (2022), Singapore SSOC (2024), India NCO (2015), and ILO ISCO-08.
2. **Phase 2 (Architecture):** Formulate formal Pydantic v2 schemas for:
   - `ClassificationSystem`
   - `NationalOccupation`
   - `CanonicalOccupation`
   - `OccupationMapping`
   - `MappingProvenance`
3. **Phase 3 (Mapping Methodology):** Establish rigorous rubric for relationship types, confidence scoring, evidence dimensions, and review states.
4. **Phase 4 & 5 (Implementation & Data Ingestion):** Build clean, versioned curated registries covering foundational cross-market technology, engineering, data, and management occupations with full provenance and bidirectional crosswalks.
5. **Phase 6 (APIs & Frontend):** Implement additive REST endpoints under `/api/v1/occupations/...` and a clean, responsive Occupation Explorer & Cross-Market Comparison interface.
6. **Phase 7 (Verification):** Full test suite execution across schemas, APIs, search, regression parity, and production isolation.
