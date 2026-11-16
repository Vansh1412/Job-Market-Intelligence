# JOBINTEL 2.0 — SPRINT 3B.2.2
# PHASE 4: INDIA CALIBRATED BENCHMARK DISCLOSURES

**Document ID:** `SPRINT3B2_2_INDIA_BENCHMARK_DISCLOSURE`  
**Milestone:** Sprint 3B.2.2 — Statistical Disclosure Hardening  
**Date:** 2026-11-16  
**Auditor / Architect:** Principal Data Governance Architect & Labour Statistics Specialist  
**Target Branch:** `staging/sprint2c3`  
**HEAD Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  
**Production Master Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  

---

## 1. Executive Summary

This document formalizes the statistical disclosures and UI branding implemented for the India labour demand intelligence dataset. In accordance with Sprint 3B.2.1 Audit findings, the India dataset is strictly designated as a **`CALIBRATED_BENCHMARK`** and **`JOBINTEL_CURATED`** empirical resource.

The interface prominently alerts users that India demand numbers represent an empirical sample of technology-hub postings, completely eliminating any possibility that users conflate them with official Ministry of Statistics and Programme Implementation (MoSPI) national surveys.

---

## 2. Institutional & Methodological Context

### 2.1 The Indian Labour Statistics Landscape
The National Sample Survey Office (NSSO) under MoSPI conducts the **Periodic Labour Force Survey (PLFS)**. PLFS rigorously tracks employment-to-population ratios, labour force participation, and activity status across urban and rural sectors. 

However, India **does not publish an official, high-frequency, national enterprise job vacancy register** analogous to the U.S. JOLTS or Australian JSA IVI. Official government statistics on open job postings at the 8-digit National Classification of Occupations (NCO-2015) level do not exist.

### 2.2 JobIntel Benchmark Construction
To provide career intelligence for digital engineering roles, JobIntel ingests an empirical sample of 2023–2024 tech job advertisements:
- **Coverage Scope:** Major IT clusters — Bengaluru (34%), Hyderabad (21%), National Capital Region (NCR - Delhi/Gurgaon/Noida, 18%), Pune (14%), and other tech centers (13%).
- **Sampling Limitations:** Represents formal corporate IT, software engineering, and multinational capability centers (GCCs). It truncates informal, non-digital, and non-urban labour segments.

---

## 3. Mandatory User-Facing Disclosures

### 3.1 Badge Specification
In `frontend/src/pages/DemandPage.tsx`, whenever an Indian occupation or market view is active, the interface renders a dedicated amber badge:

```text
CALIBRATED BENCHMARK — EMPIRICAL TECH SAMPLE
```

### 3.2 Mandatory Warning & Explanation
Directly beneath the occupation header, the UI displays an alert box containing the mandatory legal disclosure:

> **⚠️ Methodology Disclosure:** *"Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."*

### 3.3 Strict Terminology Prohibitions
The frontend, backend schemas, API responses, and documentation are strictly audited to prohibit misleading claims:
- ❌ **Prohibited Terms:** "Official national vacancies", "National employment census", "MoSPI vacancy survey", "PLFS vacancy observations", "Government job-opening statistics".
- ✅ **Permitted Terms:** "JobIntel empirical tech benchmark", "Validated tech posting sample", "Calibrated IT hub demand indicator".

---

## 4. Contract and Code Integration

### 4.1 Schema Representation
In `src/backend/schemas/demand.py`:
- `provenance = DemandProvenance.JOBINTEL_CURATED`
- `provenance_label = "JobIntel research benchmark"`
- `data_quality_grade = "CALIBRATED_BENCHMARK"`
- `benchmark_disclosure = "Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."`

### 4.2 Service Layer Integration
In `src/backend/services/demand_service.py`:
When `market_id == MarketId.IN`:
```python
benchmark_disc = (
    "Based on a JobIntel empirical technology-hub job-posting sample. "
    "This is not an official MoSPI national vacancy census and does not "
    "represent every occupation or region in India."
)
regional_disc = "Regional breakdowns reflect technology-hub posting sample shares across Bangalore, Hyderabad, NCR, and Pune."
```

---

## 5. Automated Verification

Tested and validated in `tests/test_demand_intelligence.py`:
- `test_india_calibrated_benchmark_disclosure`: Asserts presence of `benchmark_disclosure`, verifies `provenance == "JOBINTEL_CURATED"`, and confirms `provenance_label == "JobIntel research benchmark"`.
- Result: **PASS** (100% compliance).
