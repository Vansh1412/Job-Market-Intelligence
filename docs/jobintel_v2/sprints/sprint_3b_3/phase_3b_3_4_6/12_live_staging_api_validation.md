# SPRINT 3B.3.3.4.6 — LIVE STAGING API VALIDATION REPORT
**Sprint:** 3B.3.3.4.6  
**Document:** `12_live_staging_api_validation.md`  
**Date:** 2026-11-18  
**Author:** Independent QA Lead & Backend Architect  
**Status:** COMPLETE & 100% VERIFIED  

---

## 1. Executive Summary

Following the deployment of commit `8734d0c` and `328922d` to `staging/sprint2c3`, live HTTP network probes were executed against the Render staging backend (`https://jobintel-backend-staging.onrender.com`).

All 12 critical API endpoints responded with HTTP 200 OK, verifying:
- Exactly **5 sovereign employer profiles** populated and available in the live registry.
- 100% resolution accuracy for all 5 candidates when queried by corporate name, platform market, and statutory identifier.
- Strict fail-closed defense (`NO_MATCH` / `CONFIRMED_DISTINCT`) on synthetic unknown entities.

---

## 2. Live Employer Registry Inspection (`GET /api/v1/employers`)

- **Target URL:** `https://jobintel-backend-staging.onrender.com/api/v1/employers`
- **HTTP Status:** `200 OK`
- **Content-Type:** `application/json`
- **Observed Cohort Count:** Exactly 5 profiles

| # | Company Name | Sovereign ID | Jurisdiction | Statutory Authority | Statutory ID | Headcount Evidence | Publication Status |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Atlassian Pty Ltd** | `comp_au_atlassian` | Australia (AU) | ASIC | `53102443916` | Band: 1,000 to 4,999 (WGEA) | `APPROVED` |
| 2 | **Microsoft Corporation** | `comp_us_microsoft` | United States (US) | U.S. SEC | `0000789019` | Value: 228,000 (SEC Form 10-K) | `APPROVED` |
| 3 | **Arm Limited** | `comp_uk_arm` | United Kingdom (UK) | Companies House | `02557590` | Band: 1,000 to 4,999 (UK GPG) | `APPROVED` |
| 4 | **DBS Bank Ltd.** | `comp_sg_dbs` | Singapore (SG) | ACRA | `196800306E` | Value: 36,000 (Bizfile Disclosed) | `APPROVED` |
| 5 | **Infosys Limited** | `comp_in_infosys` | India (IN) | MCA | `L85110KA1981PLC013115` | Value: 317,240 (SEBI BRSR) | `APPROVED` |

---

## 3. Detail Endpoint Probes (`GET /api/v1/employers/{id}`)

| Probe Endpoint | HTTP Status | Canonical Name Returned | Verified Statutory Number | Headcount Disclosure Basis |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/employers/comp_au_atlassian` | `200 OK` | Atlassian Pty Ltd | `53102443916` | WGEA Size Band (1,000 to 4,999) |
| `/api/v1/employers/comp_us_microsoft` | `200 OK` | Microsoft Corporation | `0000789019` | SEC Form 10-K Consolidated |
| `/api/v1/employers/comp_uk_arm` | `200 OK` | Arm Limited | `02557590` | UK Gender Pay Gap Reporting Band |
| `/api/v1/employers/comp_sg_dbs` | `200 OK` | DBS Bank Ltd. | `196800306E` | Disclosed Operating Workforce |
| `/api/v1/employers/comp_in_infosys` | `200 OK` | Infosys Limited | `L85110KA1981PLC013115` | SEBI BRSR Audited Total |

---

## 4. Entity Resolution Probes (`POST /api/v1/employers/resolve`)

| Test Query | Target Market | Statutory ID & Authority | Live Staging Response | Confidence | Resolved ID | Review Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Atlassian Pty Ltd | `AU` | `53102443916` (ASIC) | `EXACT_IDENTIFIER_MATCH` | `1.0` | `comp_au_atlassian` | `AUTOMATICALLY_RESOLVED` |
| Microsoft Corporation | `US` | `0000789019` (U.S. SEC) | `EXACT_IDENTIFIER_MATCH` | `1.0` | `comp_us_microsoft` | `AUTOMATICALLY_RESOLVED` |
| Arm Limited | `UK` | `02557590` (Companies House) | `EXACT_IDENTIFIER_MATCH` | `1.0` | `comp_uk_arm` | `AUTOMATICALLY_RESOLVED` |
| DBS Bank Ltd. | `SG` | `196800306E` (ACRA) | `EXACT_IDENTIFIER_MATCH` | `1.0` | `comp_sg_dbs` | `AUTOMATICALLY_RESOLVED` |
| Infosys Limited | `IN` | `L85110KA1981PLC013115` (MCA) | `EXACT_IDENTIFIER_MATCH` | `1.0` | `comp_in_infosys` | `AUTOMATICALLY_RESOLVED` |
| Synthetic Unknown Corp | `US` | `9999999999` (US_SEC) | `NO_MATCH` | `0.0` | `null` | `CONFIRMED_DISTINCT` |

All entity resolution requests demonstrate 100% determinism, exact statutory authority validation, and fail-closed defense.
