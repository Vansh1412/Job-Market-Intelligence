# JOBINTEL 2.0 — SPRINT 2C.3: BASELINE SNAPSHOT REPORT
**Milestone:** Phase 0 — Repository Reconnaissance and Baseline Snapshot  
**Execution Date:** 2026-11-15T11:15:00+05:30  
**Evaluator Roles:** Principal Software Architect, Senior DevOps Engineer, Release Manager  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report establishes the immutable pre-deployment baseline snapshot for JOBINTEL 2.0 Sprint 2C.3 (Controlled Staging Deployment, Infrastructure Provisioning, End-to-End Validation, Security Verification, and Release Qualification).

The repository state was captured prior to executing any deployment actions. Zero commits, zero pushes, and zero production mutations have occurred. All 10 frozen model artifacts and certified datasets remain 100% bitwise intact.

---

## 2. Git Repository Reconnaissance

| Metric | Recorded Value | Verification Status |
| :--- | :--- | :--- |
| **Current Branch** | `master` | VERIFIED |
| **HEAD Commit Hash** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | VERIFIED |
| **Commit Message** | `fix(routing): mount API routers natively at both /api and root prefixes` | VERIFIED |
| **Remote Origin URL** | `https://github.com/Vansh1412/Job-Market-Intelligence.git` | VERIFIED |
| **Remote Branches** | `origin/master` (single branch on remote) | VERIFIED |
| **Working Tree Status** | 7 modified tracked files (+39 lines, 0 deletions) | VERIFIED |
| **Staged Files** | 0 files | VERIFIED |
| **Untracked Directories** | `docs/jobintel_v2/`, `src/backend/governance/`, `src/backend/employers/`, `src/backend/markets/`, `src/backend/data_catalog/`, `src/backend/schemas/`, `tests/` | VERIFIED |
| **Git Diff Check** | Clean (0 whitespace errors; CRLF normalization warnings only) | VERIFIED |

### 2.1 Tracked Modified Files Diff Summary

```
 requirements.txt               |  3 +++
 src/backend/main.py            |  5 +++++
 src/backend/routers/india.py   |  2 ++
 src/backend/routers/predict.py |  2 ++
 src/backend/routers/usa.py     |  2 ++
 src/india/modeling.py          | 11 +++++++++++
 src/run_phase5_experiments.py  | 14 ++++++++++++++
 7 files changed, 39 insertions(+), 0 deletions(-)
```

---

## 3. Deployment Configuration Audit

### 3.1 Render Configuration (`render.yaml`)
- **Service Name:** `jobintel-backend` (Production Web Service)
- **Runtime:** `python` (Python 3.11.9)
- **Plan:** `free`
- **Region:** `oregon`
- **Tracked Branch:** `master`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Health Check Path:** `/api/ready`
- **Environment Variables:** `PYTHON_VERSION=3.11.9`, `JOBINTEL_ENV=production`, `CORS_ORIGINS="..."`
- **Production Isolation Finding:** `render.yaml` is hardwired to deploy the production web service upon pushes to `master`. Any push to `master` automatically triggers a production deployment on Render. Therefore, staging provisioning MUST NOT be triggered via git push to `master`.

### 3.2 Vercel Configuration (`vercel.json` & `frontend/vercel.json`)
- **Root Configuration (`vercel.json`):**
  - Build Command: `cd frontend && npm install && npm run build`
  - Output Directory: `frontend/dist`
  - SPA Rewrites: `/(.*)` -> `/index.html`
- **Frontend Configuration (`frontend/vercel.json`):**
  - Framework: `vite`
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Headers: Long-term cache immutable headers for `/assets/(.*)`.
- **Production Isolation Finding:** Vercel production service (`https://job-market-intelligence-dusky.vercel.app`) is automatically connected to `master`. Staging frontend deployments must be isolated preview deployments with explicit staging backend URL environment variables (`VITE_API_BASE_URL`).

### 3.3 Container Runtime Configuration (`Dockerfile` & `.dockerignore`)
- **Multi-stage Build:**
  - Stage 1: `node:20-alpine` builds frontend SPA (`npm run build`).
  - Stage 2: `python:3.11-slim` runtime environment with non-root `appuser` (UID 1000).
- **Security Controls:**
  - Non-root user execution (`USER appuser`).
  - Healthcheck probe configured to `http://localhost:8000/api/ready`.
  - Secrets strictly excluded.
- **Data Exclusion (`.dockerignore`):**
  - `data/raw/`, `data/processed/`, `*.parquet`, `jobs-tier1-L-2026-08-01/`, `.env*` explicitly ignored.
  - Zero raw or row-level observation files can leak into the Docker image.
- **Local Daemon Status:**
  - Docker CLI `v28.0.1` detected.
  - Docker Desktop Linux engine daemon is NOT running in the local Windows environment.
  - Verification Classification: `STATICALLY VERIFIED` for Dockerfile/ignore syntax; `NOT RUNTIME VERIFIED` for local daemon build.

---

## 4. Frozen ML Model Artifact Integrity

All 10 core frozen ML model artifacts and certified processed datasets were checked against `src/backend/config/artifact_manifest.json`:

| Artifact Key | Relative Path | Expected SHA-256 | Verification |
| :--- | :--- | :--- | :--- |
| `india_salary_model` | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | PASS |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | PASS |
| `india_pca` | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | PASS |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | PASS |
| `usa_salary_model` | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | PASS |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | PASS |
| `usa_scaler` | `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | PASS |
| `usa_pca` | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | PASS |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | PASS |
| `india_cohort` | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | PASS |

**Result:** 10/10 Core ML artifacts bitwise verified intact. 19/19 Total certified artifacts bitwise verified intact.

---

## 5. Pre-Deployment Baseline Verdict

**VERDICT: BASELINE VERIFIED — READY FOR STAGING EVALUATION**  
The repository state is clean, fully verified, unmutated, and ready for controlled staging deployment evaluation.
