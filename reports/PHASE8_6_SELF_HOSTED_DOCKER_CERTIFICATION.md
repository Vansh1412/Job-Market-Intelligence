# PHASE 8.6 SELF-HOSTED DOCKER CERTIFICATION

**Project:** INT234 Predictive Analytics — Job Market Intelligence (JobIntel)  
**Document ID:** `reports/PHASE8_6_SELF_HOSTED_DOCKER_CERTIFICATION.md`  
**Date:** October 8, 2026  
**Author:** Senior DevOps & Release Engineer, ML Artifact Custodian  
**Operating System:** Windows 10/11 Home Single Language (Host: 64-bit Build 26200 / 2009)  
**Git Base Commit:** `6569c1a`  
**Remote Repository:** `Vansh1412/Job-Market-Intelligence` (`origin/master`)  
**Status:** EVIDENCE-BASED AUDIT COMPLETE  

---

## 1. Environment

- **Host Machine:** Windows 10/11 Home Single Language (Build 26200 / 2009)
- **CPU Architecture:** x86_64 / 64-bit
- **Available RAM:** ~16 GB Physical Memory (15.7 GB usable)
- **Available Disk Storage:** Drive E (>136 GB free)
- **Local Python Environment:** Python 3.13.9 / Conda base on PATH
- **Local Node Environment:** Node.js v20+, npm, Vite 8.3.3
- **Repository Path:** `E:\Job Market`

---

## 2. Runner Status

- **Check Executed:**
  - `Get-Process -Name "*Runner*", "*actions*"` -> No active GitHub runner process detected.
  - `Get-Service -Name "*runner*", "*actions*"` -> No active GitHub runner service detected.
  - Runner Directory Probe (`C:\actions-runner`, `E:\actions-runner`, `~\actions-runner`) -> `False` (Not found).
- **Status:** `NOT PROVISIONED / UNVERIFIED`
- **Assessment:** A self-hosted runner labeled `[self-hosted, jobintel-private-data]` has not yet been registered or started on this machine.
- **Workflow State:** The queued workflow in GitHub Actions is correctly waiting for a registered runner matching these labels.

---

## 3. Docker Status

- **Diagnostics Executed:**
  - `docker --version` -> `The term 'docker' is not recognized as a name of a cmdlet, function, script file, or operable program.`
  - `docker info` -> Command not recognized.
  - `where.exe docker` -> `Could not find files for the given pattern(s).`
  - `wsl --status` -> `The Windows Subsystem for Linux is not installed.`
  - `where.exe wsl` -> Stub exists at `C:\Windows\System32\wsl.exe`, but WSL feature is disabled.
- **Status:** `NOT PROVISIONED / BLOCKED`
- **Assessment:** Docker CLI, Docker Engine, and WSL 2 are unavailable on the host. Per Absolute Safety Rules 14 & 22, the assistant will NOT automatically install Docker Desktop, WSL, or Windows optional features without explicit user authorization.

---

## 4. Dataset Availability

Local filesystem verification on host machine (`E:\Job Market`):
- `data/processed/india/india_modeling_cohort.parquet`: **EXISTS** (5,859 rows, 299 columns)
  - Actual SHA-256: `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec`
  - Status: `PASS`
- `data/processed/modeling_dataset.parquet`: **EXISTS** (34,036 rows, 128 columns)
  - Actual SHA-256: `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b`
  - Status: `PASS`
- **Git Quarantine:** `git ls-files data/processed` -> 0 files tracked (`PASS`).

---

## 5. Frozen Artifact Verification

Cryptographic SHA-256 verification executed against all 10 frozen artifacts on disk:

| # | Artifact Path | Expected Authoritative SHA-256 | Actual Host SHA-256 | Result |
| :-: | :--- | :--- | :--- | :-: |
| 1 | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | `7a3490d7...` | **PASS** |
| 2 | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | `0ee1dabf...` | **PASS** |
| 3 | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | `d4e32be4...` | **PASS** |
| 4 | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | `8591e3d3...` | **PASS** |
| 5 | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | `4465a3d8...` | **PASS** |
| 6 | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | `55c1b7fd...` | **PASS** |
| 7 | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | `815fd9a3...` | **PASS** |
| 8 | `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | `68895e38...` | **PASS** |
| 9 | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | `ef4ef56b...` | **PASS** |
| 10 | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | `4d6d2509...` | **PASS** |

**Score:** 10/10 MATCH (**100% BIT-FOR-BIT INTACT**).

---

## 6. Docker Build

- **Status:** `BLOCKED`
- **Reason:** Docker engine is unavailable on the local host. Cannot execute `docker build` until Docker Desktop / WSL 2 is installed.
- **Specification:** `Dockerfile` is verified and configured with multi-stage build, `RUN mkdir -p /app/data/processed/india`, and `.dockerignore` excludes all `*.parquet` files.

---

## 7. Docker Runtime

- **Status:** `BLOCKED`
- **Reason:** Host lacks Docker daemon. Actual container cannot be started until Docker is provisioned.
- **Specification:** Runtime architecture enforces read-only bind volume mount (`-v "E:/Job Market/data/processed:/app/data/processed:ro"`).

---

## 8. Health Verification

- **In-Container Probe (`GET /api/health`):** `BLOCKED` (container not started).
- **Host Native Baseline (`GET /api/health`):** `PASS` (HTTP 200, status `healthy` verified in Phase 8.1 / 8.5 test suite).

---

## 9. Readiness Verification

- **In-Container Probe (`GET /api/ready`):** `BLOCKED` (container not started).
- **Host Native Baseline (`GET /api/ready`):** `PASS` (HTTP 200, status `ready`, `artifacts_verified_count == 10` verified in Phase 8.1 / 8.5 test suite).

---

## 10. USA Inference

- **In-Container Execution:** `BLOCKED`
- **Host Native Contract:** `PASS`
  - Contract: 123 input features.
  - Model: `XGBRegressor` via singleton `ModelRegistry`.
  - Holdout Metrics: MAE = $36,380.64, RMSE = $51,082.06, R² = 0.4233, MAPE = 21.71%.

---

## 11. India Inference

- **In-Container Execution:** `BLOCKED`
- **Host Native Contract:** `PASS`
  - Contract: 290 input features.
  - Model: `HistGradientBoostingRegressor` (log1p target) via singleton `ModelRegistry`.
  - Holdout Metrics: MAE = ₹3.71 LPA, RMSE = ₹6.22 LPA, R² = 0.5798, MAPE = 35.22%.

---

## 12. Skills API

- **In-Container Execution:** `BLOCKED`
- **Host Native Baseline:** `PASS`
  - USA & India skills endpoints return full inventories (118 and 284 skills).
  - Unknown skills properly trigger HTTP 404.

---

## 13. Market API

- **In-Container Execution:** `BLOCKED`
- **Host Native Baseline:** `PASS`
  - Experience, role, and location disaggregations return empirical metrics without mock data.

---

## 14. Archetype API

- **In-Container Execution:** `BLOCKED`
- **Host Native Baseline:** `PASS`
  - USA 7-cluster and India 6-cluster PCA/KMeans projections map strictly to frozen models.

---

## 15. Cross-Market API

- **In-Container Execution:** `BLOCKED`
- **Host Native Baseline:** `PASS`
  - Cross-market comparative overview returns empirical distributions and metrics.

---

## 16. Calculator Parity

- **In-Container Execution:** `BLOCKED`
- **Host Native Baseline:** `PASS`
  - Frontend salary calculator predictions match backend live inference bit-for-bit with zero FX substitution.

---

## 17. Security Verification

- **Trigger Hardening:**
  - Workflow `.github/workflows/docker-release-gate.yml` trigger updated to `workflow_dispatch` **ONLY** (commit `6569c1a`).
  - `push`, `pull_request`, and `pull_request_target` triggers are completely disabled.
  - Zero possibility of untrusted fork code executing on the private runner.
- **Secrets & Token Isolation:** No runner registration tokens, personal access tokens, or credentials are hardcoded or committed.
- **Quarantine Boundaries:** Zero Parquet files tracked in Git; zero Parquet files uploaded to GitHub.
- **Status:** `PASS`

---

## 18. Post-Run Hash Verification

- **In-Container / Host Post-Container Hash Check:** `NOT APPLICABLE` (container execution did not take place).
- **Current On-Disk Hash Audit:** 10/10 MATCH confirmed in Section 5.

---

## 19. GitHub Actions Result

- **Public CI Pipeline (`.github/workflows/ci.yml`):**
  - Triggered on push to `master`.
  - Code-only test execution (11/11 contract tests, 9/9 Vitest tests, ESLint, Vite bundle build).
  - Status: `PASS`.
- **Protected Release Gate (`.github/workflows/docker-release-gate.yml`):**
  - Runner target: `[self-hosted, jobintel-private-data]`.
  - Status: `QUEUED / WAITING FOR RUNNER`.
  - Diagnosis: Normal expected behavior. The workflow is waiting for the maintainer to provision and launch the self-hosted runner.

---

## 20. Remaining Issues

1. **Docker CLI / Engine Absent on Host:** Docker Desktop and WSL 2 are not installed on the Windows host.
2. **GitHub Runner Not Yet Started:** The self-hosted runner process is not running.

---

## 21. Final Verdict

# **`BLOCKED`** (Docker Runtime & Self-Hosted Runner Verification)
### Public Code CI & Artifact Integrity: **`PASS`**

> **Reasoning:** In strict accordance with Master Prompt Section 34 & 35:
> - Frozen artifacts: `PASS` (10/10 exact match).
> - Public CI: `PASS` (clean, code-only, passing).
> - Security boundary: `PASS` (`workflow_dispatch` only, zero fork PR execution).
> - Docker build & run: `BLOCKED` (Docker engine not provisioned on host).
> - Self-hosted runner: `BLOCKED` (Runner not yet registered on host).
>
> The release candidate cannot be marked `READY` until the user provisions Docker and starts the trusted self-hosted runner.
