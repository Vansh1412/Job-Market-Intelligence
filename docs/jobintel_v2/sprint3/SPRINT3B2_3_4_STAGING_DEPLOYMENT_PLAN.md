# JOBINTEL 2.0 — SPRINT 3B.2.3.4
## CONTROLLED STAGING DEPLOYMENT RUNBOOK & READINESS PLAN

**Plan Version:** 1.0  
**Target Branch:** `staging/sprint2c3`  
**Target Commit SHA:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Production Baseline SHA:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`master`, strictly isolated)  
**Execution Status:** READY — PENDING EXPLICIT USER AUTHORIZATION  
**Note:** NO DEPLOYMENT PERFORMED IN SPRINT 3B.2.3.4.

---

## 1. SCOPE AND DEPLOYMENT TARGETS

This document establishes the exact execution procedure for deploying the Sprint 3B.2 Global Job Demand Intelligence release to the isolated staging environments.

### Deployment Environments
1. **Staging Backend Service:**
   - **Provider:** Render
   - **Service Name:** `jobintel-backend-staging`
   - **Service URL:** `https://jobintel-backend-staging.onrender.com`
   - **Target Git Ref:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)
2. **Staging Frontend Application:**
   - **Provider:** Vercel
   - **Project Name:** `jobintel-staging`
   - **Project ID:** `prj_Og513XzDt3k6UygBsL0KUkXD89jk`
   - **Public Alias:** `https://jobintel-staging.vercel.app`
   - **Target Git Ref:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)

---

## 2. PRE-DEPLOYMENT PREREQUISITES CHECKLIST

Prior to triggering deployment, the release engineer must verify that all prerequisites remain green:

- [x] **Local Working Tree Clean:** Zero uncommitted changes, zero untracked source files.
- [x] **Git Provenance Verified:** Commits `f149859` and `d1a8b02` pushed to `origin/staging/sprint2c3`.
- [x] **Direct Ancestry Confirmed:** Linear history from `5897413` with zero divergence.
- [x] **Production Isolation Confirmed:** `master` branch invariant at `198b79d`.
- [x] **Backend Regression Pass:** 371 / 371 Python pytest tests passing.
- [x] **Frontend Regression Pass:** 17 / 17 Vitest unit tests passing.
- [x] **Frontend Build Clean:** `npm --prefix frontend run build` completed with 0 errors.
- [x] **Parity Tests Pass:** 30 / 30 golden prediction and archetype tests passing.
- [x] **Model Artifact Integrity:** 19 / 19 artifacts match cryptographic SHA-256 manifest.
- [x] **API Contracts Verified:** UK publication gate, null serialization, shortage independence confirmed.
- [x] **Live Baseline Probed:** Staging backend healthy (404 on demand routes confirms un-deployed state).

---

## 3. ORDER OF DEPLOYMENT OPERATIONS

To prevent frontend contract mismatches, deployment MUST follow a strict sequential order: **Backend First, Frontend Second**.

```
+-----------------------------------------------------------+
| 1. Trigger Render Staging Backend Deployment               |
|    Commit: d1a8b027d10031b3568a3141f639e2f40a49be18       |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 2. Verify Backend Live Health & Demand Endpoints          |
|    - GET /health -> 200 OK                                |
|    - GET /api/ready -> 200 OK                             |
|    - GET /v1/demand/market-summary -> 200 OK              |
|    - GET /v1/demand/occupations/2134?market=UK -> null    |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 3. Deploy Vercel Staging Frontend                         |
|    Project: jobintel-staging (prj_Og513XzDt3k6UygBsL0KUk) |
|    Commit: d1a8b027d10031b3568a3141f639e2f40a49be18       |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 4. Browser Integration & Live UI Audit                    |
|    - Verify Demand Intelligence Navigation Tab            |
|    - Verify 5 Sub-Tabs & Interactive Visualizations       |
|    - Verify UK Gate Banner & Disclaimers                  |
|    - Verify Skill Gap Calculator Interactivity            |
+-----------------------------------------------------------+
```

---

## 4. STEP-BY-STEP DEPLOYMENT EXECUTION INSTRUCTIONS

### Step 1: Render Staging Backend Deployment
1. Navigate to the Render Dashboard for `jobintel-backend-staging` (or trigger via Render Deploy Hook / API if configured).
2. Ensure the build points to repository `Vansh1412/Job-Market-Intelligence` and branch `staging/sprint2c3`.
3. Trigger manual deployment for commit `d1a8b027d10031b3568a3141f639e2f40a49be18`.
4. Monitor build logs:
   - Ensure Python 3.11 environment boots cleanly.
   - Verify dependencies install without version conflicts.
   - Verify FastAPI startup log: `DemandService initialized with 28 observations, 7 metric defs, 10 sources, 11 skill sets`.
   - Confirm server starts on port `10000`.

### Step 2: Post-Backend Health Verification
Execute live HTTP probes against the staging backend:
```bash
# 1. Check health
curl -s https://jobintel-backend-staging.onrender.com/health | jq .status
# Expected: "healthy"

# 2. Check ready
curl -s https://jobintel-backend-staging.onrender.com/api/ready | jq .status
# Expected: "ready"

# 3. Check demand market summary
curl -s https://jobintel-backend-staging.onrender.com/v1/demand/market-summary | jq .markets[].market
# Expected: ["US", "AU", "SG", "UK", "IN"]

# 4. Check UK publication gate serialization
curl -s https://jobintel-backend-staging.onrender.com/v1/demand/occupations/2134?market=UK | jq .primary_metric_value
# Expected: null
```

### Step 3: Vercel Staging Frontend Deployment
1. Using the Vercel CLI (or Vercel Dashboard connected to `staging/sprint2c3`):
   ```bash
   cd frontend
   vercel --prod=false
   ```
   *(Or link explicitly to `prj_Og513XzDt3k6UygBsL0KUkXD89jk` and assign to `jobintel-staging.vercel.app`)*
2. Verify that environment variables point to staging backend:
   ```env
   VITE_API_URL=https://jobintel-backend-staging.onrender.com
   ```
3. Ensure the deployment aliases correctly to:
   `https://jobintel-staging.vercel.app`

### Step 4: Browser Integration & End-to-End Verification
1. Launch browser audit against `https://jobintel-staging.vercel.app`.
2. Inspect the **Job Demand** tab:
   - **Tab 1: Overview:** Verify KPI cards and cross-market demand momentum chart render cleanly.
   - **Tab 2: Market Profiles:** Select UK; verify the "UK Demand Data Withheld Pending Review" warning banner displays and no numerical volume charts are visible. Select US; verify BLS job openings and regional distributions render.
   - **Tab 3: Cross-Market Comparability:** Select US vs UK; verify comparability matrix renders with methodological mismatch warnings.
   - **Tab 4: Skill Gap Analysis:** Select an occupation, enter skills; verify match percentage calculation and rule-based recommendation list.
   - **Tab 5: Data Sources & Governance:** Verify OGL v3.0, BLS public domain, and JobIntel benchmark citations display accurately.

---

## 5. ROLLBACK & DISASTER RECOVERY PROTOCOL

If any unexpected failure occurs during deployment:

### Backend Rollback
1. In the Render Dashboard, select the previous successful deployment corresponding to commit `58974134e56b4c3ec6b6119b7b4739e9cce857f3`.
2. Click **Rollback to this deploy**.
3. Verify `/health` returns status `healthy` and version `2.0.0`.

### Frontend Rollback
1. In Vercel CLI or Dashboard:
   ```bash
   vercel rollback jobintel-staging.vercel.app
   ```
   Or select the previous deployment from the Vercel deployment history and promote it to the production/staging domain.
2. Confirm `https://jobintel-staging.vercel.app` loads the Sprint 3B.1.6 interface without console errors.

### Production Protection Guarantee
- Production services (`job-market-intelligence-6ral.onrender.com` and `job-market-intelligence-dusky.vercel.app`) are mapped exclusively to the `master` branch.
- No staging deployment action touches or modifies production credentials, DNS records, or environments.

---

## 6. READINESS VERDICT

All automated validations, regression tests, contract audits, and environment baselines are complete.

The staging deployment plan is fully articulated and ready for immediate execution upon user authorization.

**Readiness Verdict:** `READY FOR STAGING DEPLOYMENT AUTHORIZATION`
