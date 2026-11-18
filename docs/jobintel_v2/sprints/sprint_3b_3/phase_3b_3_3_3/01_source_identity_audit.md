# SPRINT 3B.3.3.3.3: SOURCE IDENTITY & LINEAGE AUDIT

**Audit Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Current Local HEAD SHA:** `d0b176a7f47e18919861c115749cb0cc6a225167`  
**Remote `origin/staging/sprint2c3` SHA:** `d0b176a7f47e18919861c115749cb0cc6a225167`  
**Staging Baseline SHA:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Production Master Baseline SHA:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Auditor Status:** STRICTLY READ-ONLY  
**Verification Verdict:** **CONDITIONAL PASS — IDENTITY LIMITATION DISCLOSED**

---

## 1. GIT WORKSPACE & BRANCH INTEGRITY

Forensic inspection of the local git working directory confirms that the active branch is synchronized with the remote staging branch, with zero uncommitted working tree modifications to tracked files.

### 1.1 Git Status & Branch Output
```bash
$ git branch --show-current
staging/sprint2c3

$ git rev-parse HEAD
d0b176a7f47e18919861c115749cb0cc6a225167

$ git rev-parse origin/staging/sprint2c3
d0b176a7f47e18919861c115749cb0cc6a225167

$ git status --short
?? frontend/node_modules/
```
*(Tracked file tree is 100% clean. Only standard untracked `node_modules/` exists for frontend dependency execution).*

### 1.2 Linear Commit Lineage
The linear progression from baseline `d1a8b02` to HEAD `d0b176a` is fully documented:
```
* d0b176a (HEAD -> staging/sprint2c3, origin/staging/sprint2c3) docs(sprint3b): publish complete staging deployment and browser verification evidence
* c7b13ff docs(sprint3b): add staging deployment records and verification evidence
* f2a0777 fix(skills): guard against unmounted modeling cohort parquet in cloud deployment
* cf282bc docs(sprint3b): publish sprint 3b.3.3.3 remediation report
* d27f667 docs(sprint3b): publish final audit report and verification evidence
* 2dd55d7 test(employer): add adversarial multi-jurisdiction regression tests
* 62f5525 feat(api): implement employer resolver and align salary prediction contract
* d1a8b02 (baseline) docs(audit): publish phase 3b.3.3 staging release gate audit and remediation requirements
```

---

## 2. RENDER STAGING BACKEND DEPLOYMENT AUDIT

### 2.1 Service Overview
- **Service Name:** `jobintel-backend-staging`
- **Public URL:** `https://jobintel-backend-staging.onrender.com`
- **Environment:** Staging (Docker / Uvicorn Python runtime)

### 2.2 Response Headers & Identity Probing
A live probe was executed against `https://jobintel-backend-staging.onrender.com/health`:
```http
HTTP/1.1 200 OK
Date: Tue, 17 Nov 2026 17:38:00 GMT
Content-Type: application/json
Content-Length: 172
Connection: keep-alive
rndr-id: 9a202d6d-2391-419b
x-render-origin-server: uvicorn
Server: cloudflare
CF-RAY: ...
```

### 2.3 Identity Assessment & Disclosure
- **Cryptographic Commit Header:** Absent. Public edge proxying through Cloudflare strips internal Render git metadata.
- **API Credentials:** `RENDER_API_KEY` is not provisioned in the local environment, preventing direct querying of the Render Management API.
- **Functional Source Parity:** As proven in [03_skills_runtime_verification.md](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3/phase_3b_3_3_3/03_skills_runtime_verification.md) and [04_api_regression_matrix.md](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3/phase_3b_3_3_3/04_api_regression_matrix.md), the deployed backend runs the code introduced in `f2a0777` (fixing the unmounted cohort bug) and `62f5525` (employer resolver and empirical salary contract).
- **Classification:** **UNVERIFIED (Functionally verified via live endpoints and model bitwise parity)**.

---

## 3. VERCEL STAGING FRONTEND DEPLOYMENT AUDIT

### 3.1 Project & Deployment Metadata
Forensic query of the Vercel staging deployment configuration via Vercel CLI reveals:
- **Project Name:** `jobintel-staging`
- **Project ID:** `prj_Og513XzDt3k6UygBsL0KUkXD89jk`
- **Latest Deployment ID:** `dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj`
- **Deployment Status:** `Ready`
- **Deployment Target:** `preview`
- **Created Timestamp:** 2026-11-17 22:42:27 IST
- **Deployment URL:** `https://jobintel-staging-91nzi686a-vansh1412s-projects.vercel.app`
- **Staging Canonical Alias:** `https://jobintel-staging.vercel.app`

### 3.2 Canonical Alias Resolution
```bash
$ npx vercel alias ls
jobintel-staging.vercel.app -> jobintel-staging-91nzi686a-vansh1412s-projects.vercel.app (dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj)
```
The canonical staging frontend URL `https://jobintel-staging.vercel.app` maps directly to preview deployment `dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj`.

---

## 4. SUMMARY AUDIT TABLE

| Dimension | Target Identity / Expectation | Verified Value | Evidence Method | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Local Branch** | `staging/sprint2c3` | `staging/sprint2c3` | `git branch` | **VERIFIED** |
| **Local HEAD SHA** | `d0b176a...` | `d0b176a7f47e18919861c115749cb0cc6a225167` | `git rev-parse HEAD` | **VERIFIED** |
| **Remote Branch SHA** | `d0b176a...` | `d0b176a7f47e18919861c115749cb0cc6a225167` | `git rev-parse origin/...` | **VERIFIED** |
| **Production Baseline** | `198b79d...` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `git rev-parse origin/master` | **VERIFIED** |
| **Render Backend Service**| `jobintel-backend-staging` | `https://jobintel-backend-staging.onrender.com` | Live HTTP probe | **VERIFIED** |
| **Render Commit SHA** | Match HEAD (`d0b176a`) | *Unverified via edge headers; functionally verified* | Cloudflare header probe | **DISCLOSED** |
| **Vercel Frontend ID** | `dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj` | `dpl_FEgo25f5VUR6wkRbaTJqPojxwDBj` | Vercel CLI | **VERIFIED** |
| **Vercel Staging Alias** | `jobintel-staging.vercel.app` | Resolves to `dpl_FEgo25f5...` | `vercel alias ls` | **VERIFIED** |
