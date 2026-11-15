# SPRINT 2C.2.2 — TASK 4: DEPLOYMENT ARTIFACT AND CONTAINER VERIFICATION

**Document:** `SPRINT2C2_2_ARTIFACT_VERIFICATION.md`  
**Author:** Principal Software Architect, Senior Backend Engineer, Security Auditor  
**Date:** November 13, 2026  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Repository:** `e:\Job Market` (`master` branch)

---

## 1. EXECUTIVE SUMMARY

This audit verified the composition, cryptographic integrity, secret hygiene, and runtime behavior of the deployment artifacts packaged for Render and containerized environments.

**Local vs Live Staging Distinction:**
- **Local Artifact Verification (Performed Here):** Verifies that the Git repository, local filesystem packaging directives, Dockerfile build stages, and file exclusion rules (`.gitignore`, `.dockerignore`) bundle all necessary operational assets (code, frozen model weights, config manifests) while strictly excluding raw datasets and sensitive environment files.
- **Live Staging Deployment (Pending Cloud Execution):** Refers to provisioning an actual running web service on Render's cloud infrastructure and routing requests through public DNS and CDN layers.

---

## 2. ARTIFACT PACKAGING AUDIT

### 2.1 File Inclusion Checklist

| Target Operational Asset | Path in Repository | Target Location in Deployment / Container | Verification Method | Status |
|---|---|---|---|:---:|
| **Revocation Manifest** | `src/backend/config/revocation_manifest.json` | `/app/src/backend/config/revocation_manifest.json` | Packaged via `COPY src/ /app/src/` | **VERIFIED** |
| **Certified Artifacts Config** | `src/backend/config/certified_artifacts.json` | `/app/src/backend/config/certified_artifacts.json` | Packaged via `COPY src/ /app/src/` | **VERIFIED** |
| **All 10 Model Artifacts** | `models/` & `data/processed/india/` | `/app/models/` & `/app/data/processed/india/` | Packaged via `COPY models/` & `mkdir -p` | **VERIFIED** |
| **FastAPI Backend Code** | `src/backend/` | `/app/src/backend/` | Packaged via `COPY src/` | **VERIFIED** |
| **Dependencies Specification** | `requirements.txt` | `/app/requirements.txt` | Packaged via `COPY requirements.txt .` | **VERIFIED** |

### 2.2 Exclusion of Sensitive Data & Raw Datasets
Both `.gitignore` and `.dockerignore` were inspected line-by-line:
- **Raw Datasets Strictly Excluded:**
  - `data/raw/` (completely excluded)
  - `jobs-tier1-L-2026-08-01/` (completely excluded)
  - `nextgig_jobs_*.parquet` (completely excluded)
  - `*.parquet` and `*.csv` (wildcard excluded, with whitelist only for aggregate research tables in `reports/tables/`)
- **Secrets and Credentials Strictly Excluded:**
  - `.env`, `.env.*`, `*.pem`, `*.key`, `*.token` are strictly ignored.
  - No database connection strings, API tokens, AWS keys, or private secrets exist in the codebase.

---

## 3. MODEL ARTIFACT INTEGRITY CHECK (10/10 BITWISE PARITY)

The Centralized Model Registry was invoked on the local packaged files, verifying exact SHA-256 cryptographic hashes:

```
======================================================================
JOBINTEL MODEL REGISTRY: VERIFYING FROZEN ARTIFACT INTEGRITY
======================================================================
Verified 10/10 frozen artifacts bitwise intact.
USA Models Loaded: XGBoost Salary Model (123 feats), Archetype Pipeline (k=7).
India Models Loaded: HistGradientBoosting Model (290 feats), Archetype Pipeline (k=6).
======================================================================
MODEL REGISTRY INITIALIZATION COMPLETE: STATUS GREEN
======================================================================
```

| Model / Preprocessor Artifact | Path | Exact SHA-256 Digest | Status |
|---|---|---|:---:|
| `india_salary_model` | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **VERIFIED** |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **VERIFIED** |
| `india_cohort` | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | **VERIFIED** |
| `india_pca` | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **VERIFIED** |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **VERIFIED** |
| `usa_salary_model` | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **VERIFIED** |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | **VERIFIED** |
| `usa_scaler` | `models/scaler_phase4_1.pkl` | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | **VERIFIED** |
| `usa_pca` | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | **VERIFIED** |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | **VERIFIED** |

---

## 4. FUNCTIONAL BEHAVIORAL VERIFICATION

### 4.1 Startup Verification
- Invoked `FastAPI` application lifespan.
- Model registry initialized cleanly with zero warnings.
- Cloud artifact sync reported `status: OK (Verified: 10/10)`.

### 4.2 Readiness Probe
- `GET /api/ready`: Returns HTTP 200 with `ready: True`, `artifacts_verified_count: 10`.

### 4.3 Golden Predictions Parity
- Executed `tests/test_golden_predictions.py`:
  - USA XGBoost holdout prediction matches reference outputs bitwise.
  - India HistGradientBoosting holdout prediction matches reference outputs bitwise.

### 4.4 UK Route Fail-Closed Enforcement
- Executed `tests/test_uk_salary_api.py::test_task2_layer1_blocks_real_publication_state`:
  - All 5 routes (`/occupations`, `/occupations/{soc}`, `/occupations/{soc}/regions`, `/regions/{reg}/occupations`, `/metadata`) returned HTTP 503 `UK_DATA_NOT_PUBLISHED`.
  - Zero salary data was leaked.

---

## 5. CONCLUSION

The deployment artifact is completely packaged, verified bitwise against frozen model baselines, sanitized of raw data and secrets, and ready for staging deployment.

