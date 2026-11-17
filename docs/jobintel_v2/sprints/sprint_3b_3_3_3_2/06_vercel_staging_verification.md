# JOBINTEL 2.0 — SPRINT 3B.3.3.3.2
## DOCUMENT 06: VERCEL STAGING FRONTEND DEPLOYMENT VERIFICATION

**Sprint:** 3B.3.3.3.2 — Controlled Staging Integration, Deployment & Post-Deployment Verification  
**Target Environment:** Staging Frontend (`https://jobintel-staging.vercel.app`)  
**Provider:** Vercel (Preview Deployment with Dedicated Staging Alias)  
**Status:** DEPLOYED, ALIASED & FUNCTIONALLY VERIFIED  

---

### 1. Vercel Staging Project Configuration & Pre-Flight Audit

| Parameter | Mandated / Staging Setting | Live Verified Setting | Method | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Project Name** | `jobintel-staging` | `jobintel-staging` | Vercel CLI inspection | **VERIFIED** |
| **Project ID** | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | `prj_Og513XzDt3k6UygBsL0KUkXD89jk` | `.vercel/project.json` | **VERIFIED** |
| **Deployment Type** | Preview / Staging | Preview (`target: null`, `env: preview`) | `npx vercel --yes` (NO `--prod`) | **VERIFIED** |
| **Staging Backend URL**| `https://jobintel-backend-staging.onrender.com` | `https://jobintel-backend-staging.onrender.com` | `vercel env pull` check | **VERIFIED** |
| **Production Target Isolation** | `job-market-intelligence-dusky.vercel.app` untouched | Confirmed 39 days old; zero prod deployments | `npx vercel alias ls` | **PASS (ISOLATED)** |

---

### 2. Deployment Execution & Artifact Metadata

- **Deployment ID:** `dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj`
- **Deployment URL:** `https://jobintel-staging-91nzi686a-vansh1412s-projects.vercel.app`
- **Inspector URL:** `https://vercel.com/vansh1412s-projects/jobintel-staging/FEgo25f5VUR6wkRbaTJqPojxwDBj`
- **Assigned Staging Alias:** `https://jobintel-staging.vercel.app`
- **Target Git Commit:** `c7b13ff` (`c7b13ff78fcf709841fce2c3e17b8f9e2b1236ea`)
- **Build Machine Specification:** 2 vCPU, 8192 MiB RAM (`basic` machine)
- **Ready State:** `READY` (HTTP 200)

---

### 3. Alias Assignment & Resolution Audit

Executed command:
`npx vercel alias set jobintel-staging-91nzi686a-vansh1412s-projects.vercel.app jobintel-staging.vercel.app`

Verified via `npx vercel alias ls`:
```
source                                                     url                         age
jobintel-staging-91nzi686a-vansh1412s-projects.vercel.app  jobintel-staging.vercel.app 2d
```

---

### 4. SPA Rewrite & Deep-Link Resolution Verification

Verified that single-page application routing handles direct URL navigation properly without 404 errors:

| Route Path | HTTP Response Code | Content Length | SPA Fallback Status |
| :--- | :--- | :--- | :--- |
| `/` | 200 OK | 1,494 bytes | **PASS** |
| `/predictor` | 200 OK | 1,494 bytes | **PASS** |
| `/skills` | 200 OK | 1,494 bytes | **PASS** |
| `/occupations` | 200 OK | 1,494 bytes | **PASS** |
| `/demand` | 200 OK | 1,494 bytes | **PASS** |
| `/market-explorer` | 200 OK | 1,494 bytes | **PASS** |

**Phase 6 Verdict:** Vercel staging deployment is complete, correctly configured to talk strictly to the staging backend, and alias is verified live. Ready for Phase 7 (End-to-End Staging Browser Audit).
