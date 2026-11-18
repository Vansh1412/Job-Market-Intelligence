# SPRINT 3B.3.3.4.6 — BASELINE AUDIT & AUTHORIZATION
**Sprint:** 3B.3.3.4.6 — Controlled Five-Employer Staging Remediation, Safe Seed Integration & Live Cloud Deployment  
**Date:** 2026-11-18  
**Role:** Principal Platform Engineer, Data Engineer & Security Lead  
**Execution Mode:** CONTROLLED STAGING REMEDIATION & LIVE DEPLOYMENT  
**Working Branch:** `staging/sprint2c3`  
**Production Status:** STRICTLY FROZEN (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)  

---

## 1. Executive Summary & Authorization Scope

Sprint 3B.3.3.4.6 was initiated to resolve the critical deployment and persistence defect identified in Sprint 3B.3.3.4.5: namely, that the five-employer pilot cohort authored in Sprint 3B.3.3.4.4 was never committed or pushed to GitHub, leaving the live Render staging backend unpopulated.

### Explicit Authorization
- **AUTHORIZED:**
  - Correct the five-employer pilot implementation and schemas.
  - Eliminate the `sys.modules` test detection anti-pattern.
  - Implement safe, isolated pytest fixtures using `tmp_path` (preventing seed deletion).
  - Package the certified seed manifest into `src/backend/data_catalog/` with LF line endings and cryptographic checksum verification.
  - Execute full local test suites (418 backend, 51 frontend).
  - Commit focused changes to `staging/sprint2c3`.
  - Push `staging/sprint2c3` to GitHub and trigger Render staging deployment.
  - Deploy frontend to Vercel staging (`jobintel-staging`).
  - Perform live browser and API verification against `jobintel-backend-staging.onrender.com` and `jobintel-staging.vercel.app`.
- **STRICTLY NOT AUTHORIZED:**
  - Any production deployment, push to `master`, database mutation, or model artifact retraining.
  - Ingestion of any employer beyond the five named candidates.

---

## 2. Pre-Implementation Forensic Verification

| Check / Metric | Mandated Value | Observed Value | Status |
| :--- | :--- | :--- | :--- |
| **Git Working Branch** | `staging/sprint2c3` | `staging/sprint2c3` | **VERIFIED** |
| **Local HEAD SHA** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | **VERIFIED** |
| **Remote Staging HEAD** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | **VERIFIED** |
| **Production Baseline** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | **STRICTLY FROZEN** |
| **Staging Backend URL** | `https://jobintel-backend-staging.onrender.com` | Unseeded (0 employers) | **TARGET FOR REMEDIATION** |
| **Staging Frontend URL**| `https://jobintel-staging.vercel.app` | Displays 0-record banner | **TARGET FOR REMEDIATION** |

---

## 3. The Five Pristine Employer Candidates

The five sovereign corporate entities authorized for this pilot remain identical to those audited in Sprints 3B.3.3.4.3 through 3B.3.3.4.5:
1. **Atlassian Pty Ltd** (Australia / AU) — `comp_au_atlassian` — ABN `53102443916`
2. **Microsoft Corporation** (United States / US) — `comp_us_microsoft` — CIK `0000789019`
3. **Arm Limited** (United Kingdom / UK) — `comp_uk_arm` — CRN `02557590`
4. **DBS Bank Ltd.** (Singapore / SG) — `comp_sg_dbs` — UEN `196800306E`
5. **Infosys Limited** (India / IN) — `comp_in_infosys` — CIN `L85110KA1981PLC013115`
