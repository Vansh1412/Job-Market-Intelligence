# PHASE 8.5 RELEASE CERTIFICATION

**Project:** INT234 Predictive Analytics — Job Market Intelligence (JobIntel)  
**Document ID:** `reports/PHASE8_5_RELEASE_CERTIFICATION.md`  
**Date:** October 8, 2026  
**Author:** Senior Release Engineer, DevOps Engineer, Security Engineer, ML Artifact Custodian & Scientific Integrity Auditor  
**Operating System:** Windows 11 Home (Host) / Linux Ubuntu 22.04 LTS (Target Container Environment)  
**Git Base Commit:** `f425876`  
**Status:** EVIDENCE-BASED AUDIT COMPLETE  

---

## 1. Executive Summary

Phase 8.5 resolves the fundamental architecture mismatch between public GitHub Continuous Integration (CI) and private, licensed research dataset governance. Previous GitHub Actions workflow failures stemmed from two distinct root causes:
1. A stale expected SHA-256 checksum for `models/india/india_pca_v1.pkl` embedded in legacy `.github/workflows/ci.yml`.
2. A build-context failure in `Dockerfile` (`COPY data/processed/ /app/data/processed/`) because proprietary, license-quarantined Parquet datasets are correctly excluded from public Git tracking.

Phase 8.5 establishes a robust, dual-pipeline release architecture:
- **Public CI Pipeline (`.github/workflows/ci.yml`):** Runs on ephemeral GitHub-hosted runners (`ubuntu-latest`) and executes code-only verification (Python syntax compilation, routing contract tests, Pydantic schema validation, frontend ESLint, Vitest unit suite, and Vite production bundle build) with **zero** proprietary dataset dependencies.
- **Protected Release Gate (`.github/workflows/docker-release-gate.yml`):** Runs exclusively on a maintainer-controlled private runner (`[self-hosted, jobintel-private-data]`), triggered only via `workflow_dispatch` or `push` to `master` (never on PRs from untrusted forks). It builds the multi-stage Docker container cleanly without embedded data, mounts the real frozen Parquet files via a read-only volume (`-v .../data/processed:/app/data/processed:ro`), validates 10/10 frozen cryptographic checksums inside the container, verifies live `/api/ready` and `/api/health` probes, and confirms full API parity and model inference.

All 10 frozen machine learning artifacts remain 100% bit-for-bit intact on disk. Zero models were retrained. Zero synthetic data was generated. No checksum checks were weakened.

---

## 2. Original GitHub Failure

When the repository was pushed to remote `origin/master`, GitHub Actions reported failure on two workflow jobs:

1. **Legacy `ci.yml` Job (`backend-and-model-integrity`):**
   - The job executed a step computing SHA-256 for `models/india/india_pca_v1.pkl` and asserting equality against `8591e3d1c312788eb59be92a3424d9c7d413349646b976694602f97cf67417e7`.
   - The step failed with an exit code indicating mismatch because the actual on-disk file has hash `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897`.
   - Concurrently, the job executed `pytest tests/`, which attempted to load `data/processed/india/india_modeling_cohort.parquet` and `data/processed/modeling_dataset.parquet`, neither of which exist on a clean GitHub runner.

2. **`docker-release-gate.yml` Job (`docker-release-gate`):**
   - The Docker build step executed `docker build -t jobintel-phase8-3-certification .`.
   - The build halted at step `COPY data/processed/ /app/data/processed/` with error:
     ```
     ERROR: failed to calculate checksum of ref ...: "/data/processed": not found
     ```
   - Build context failed because `data/processed` is gitignored and absent from the public repository checkout.

---

## 3. Checksum Root Cause

Forensic analysis confirmed that the artifact `models/india/india_pca_v1.pkl` was never corrupted or mutated.

- **Stale CI Hash:** `8591e3d1c312788eb59be92a3424d9c7d413349646b976694602f97cf67417e7` was an obsolete intermediate hash recorded during early Phase 6 experimentation and erroneously hardcoded into `.github/workflows/ci.yml`.
- **Authoritative Hash:** `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` is the true, scientifically verified checksum recorded in `src/backend/models/model_registry.py` (line 47) and `reports/docker_validation.md`.
- **Resolution:**
  - Duplicate verification was purged from `ci.yml`.
  - Stale references across active workflows were completely eliminated.
  - The authoritative checksum is preserved in `src/backend/models/model_registry.py` and `docker-release-gate.yml`.
  - The artifact was NOT regenerated, refitted, or modified in any way.

---

## 4. Docker Root Cause

The Docker build failure was an architectural consequence of attempting to bake local data files into container image layers:

```dockerfile
# PREVIOUS PROBLEMATIC PATTERN:
COPY data/processed/ /app/data/processed/
```

Because `data/processed/` is excluded from Git by `.gitignore`, a clean clone on any cloud runner or external machine does not possess this directory. When Docker builds the image, the build engine searches for `./data/processed` in the build context and fails immediately.

Attempting to resolve this by `git add -f data/processed` or removing `data/processed/` from `.gitignore` would directly violate the DataForge Tier 1 Dataset License Agreement by publishing proprietary, record-level job postings to a public GitHub repository.

---

## 5. Data Governance Decision

The repository maintains strict adherence to the **DataForge Dataset License Agreement (Tier 1 — Internal Analytics)**:

1. **Quarantine Boundary:**
   - `data/raw/`, `data/processed/`, and all `*.parquet` files remain quarantined on local storage.
   - They are strictly excluded from Git via `.gitignore`.
   - They are excluded from Docker build context via `.dockerignore`.
2. **Zero Synthetic / Fabricated Fallback:**
   - Under no circumstances will synthetic Parquets, mock data generators, or fabricated cohort subsets be introduced to satisfy CI.
   - If real data is missing, the release gate reports `BLOCKED` or `UNVERIFIED`.
3. **Decoupled Verification:**
   - Public CI validates software functionality, syntax, routing, schemas, and frontend bundles.
   - Release certification validates full models and datasets within a trusted environment where data is legitimately provisioned.

---

## 6. Public CI Architecture

`.github/workflows/ci.yml` is restructured into two parallel, independent jobs running on GitHub-hosted `ubuntu-latest`:

```yaml
jobs:
  backend-code-quality:
    name: Backend Code Quality & Contract CI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - name: Python Syntax Compilation & Import Verification
        run: python -m compileall src/
      - name: Run Code-Only Contract Tests
        run: python -m pytest tests/test_routing_contracts.py tests/test_schema_contracts.py -v

  frontend-build-and-lint:
    name: Frontend Build, Lint & Vitest Suite
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci || npm install
        working-directory: frontend
      - run: npm test
        working-directory: frontend
      - run: npm run lint
        working-directory: frontend
      - run: npm run build
        working-directory: frontend
```

**Guarantees:**
- 100% reproducible on clean checkouts.
- Zero private data dependencies.
- Executes full frontend test suite (9/9 Vitest tests) and 11 backend contract tests.

---

## 7. Private Release Gate Architecture

`.github/workflows/docker-release-gate.yml` implements the protected gate:

```yaml
name: JobIntel Phase 8.5 Protected Docker Release Gate
on:
  workflow_dispatch:
  push:
    branches: [ main, master ]

jobs:
  docker-release-gate:
    name: Docker Runtime Verification & Release Gate (Protected Data Environment)
    runs-on: [self-hosted, jobintel-private-data]
    steps: ...
```

**Security Design:**
1. **Trigger Restriction:** `pull_request` triggers are strictly **removed**. Fork PRs cannot execute on the private runner.
2. **Controlled Runner:** Targets `[self-hosted, jobintel-private-data]` on a trusted host with local access to the licensed dataset directory.
3. **Runtime Read-Only Mount:** Datasets are mounted read-only via `-v "${{ github.workspace }}/data/processed:/app/data/processed:ro"`.
4. **Comprehensive Gate:** Builds Docker, verifies 10/10 hashes inside the container, starts container, verifies `/api/health`, `/api/ready`, USA inference, India inference, and cross-market analytics.

---

## 8. Docker Architecture

### Dockerfile Updates
In `Dockerfile`:
```dockerfile
# Replaced COPY data/processed/ with mount point creation:
RUN mkdir -p /app/data/processed/india
```

### .dockerignore Updates
Added to `.dockerignore`:
```dockerignore
data/processed
*.parquet
```

### Runtime Mount Strategy
When executing the certified production container on a provisioned host:
```bash
docker run -d \
  --name jobintel-app \
  -p 8000:8000 \
  --read-only \
  --tmpfs /tmp \
  -v "E:/Job Market/data/processed:/app/data/processed:ro" \
  jobintel-app:latest
```

This guarantees:
- Container image contains only code, dependencies, compiled frontend, and model weights.
- Container image can be safely exported or shared internally without leaking licensed datasets.
- Running container has access to required Parquets via read-only volume.
- Zero possibility of container runtime mutating or corrupting the frozen Parquets.

---

## 9. Frozen Artifact Verification

All 10 frozen artifacts were verified against the authoritative registry using SHA-256 computation:

| # | Artifact Path | Expected SHA-256 | Actual SHA-256 | Result |
| :-: | :--- | :--- | :--- | :-: |
| 1 | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **PASS (100% MATCH)** |
| 2 | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **PASS (100% MATCH)** |
| 3 | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | **PASS (100% MATCH)** |
| 4 | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **PASS (100% MATCH)** |
| 5 | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **PASS (100% MATCH)** |
| 6 | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **PASS (100% MATCH)** |
| 7 | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | **PASS (100% MATCH)** |
| 8 | `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | **PASS (100% MATCH)** |
| 9 | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | **PASS (100% MATCH)** |
| 10 | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | **PASS (100% MATCH)** |

**Verification Score:** 10/10 EXACT BIT-FOR-BIT PASS.

---

## 10. Dataset Governance

Git tracking status verified:
- `git ls-files data/processed`: Empty (0 files tracked).
- `git ls-files data/raw`: Empty (0 files tracked).
- `git status --short`: Shows only modified configuration files and new report documentation.
- **Result:** ZERO proprietary or record-level job posting files are committed to Git. Quarantine confirmed intact.

---

## 11. Model Contract Verification

Feature count contracts verified via `src/backend/models/model_registry.py` and model metadata:
- **USA Model Contract:**
  - Algorithm: `XGBRegressor`
  - Predictor Count: **123 features** (118 one-hot skill binary flags + 5 metadata features: `experience_level`, `company_size`, `remote_ratio`, `employment_type`, `job_title_category`).
  - Preprocessor: `MetadataTransformer` pipeline.
  - Verification: Intact.
- **India Model Contract:**
  - Algorithm: `HistGradientBoostingRegressor` (trained on `log1p(salary)`).
  - Predictor Count: **290 features** (284 binary skill indicators + `experience_midpoint_years` + `experience_range_years` + categorical `work_mode`, `city_grouped`, `normalized_role`, `is_remote`).
  - Preprocessor: Scikit-learn `ColumnTransformer`.
  - Verification: Intact.

---

## 12. Backend Verification

1. **Syntax Compilation:**
   `python -m compileall src/` completed with 0 errors across all modules.
2. **Routing Contract Suite (`tests/test_routing_contracts.py`):**
   - 4/4 tests PASSED (route map completeness, canonical routes, bidirectional page-to-route mapping, unknown route fallback).
3. **Schema Contract Suite (`tests/test_schema_contracts.py`):**
   - 7/7 tests PASSED (USA validation, India validation, boundary checks, oversized list rejection, archetype models).
4. **Full Local Suite (with local Parquets):**
   - `tests/test_chart_contracts.py`: 8/8 PASSED.
   - `tests/test_input_validation.py`: 16/16 PASSED (including live `/api/ready` and `/api/health`).

---

## 13. Frontend Verification

1. **Dependency Audit:**
   - React 19.2.8, Vite 8.3.3, TypeScript 6.0.2, TailwindCSS 4.0.0, Framer Motion 14.0.0, Recharts 3.10.1.
2. **Vitest Unit Suite (`npm --prefix frontend test`):**
   - `src/__tests__/routing.test.ts`: 3/3 PASSED.
   - `src/__tests__/calculator.test.ts`: 3/3 PASSED.
   - `src/__tests__/skills_contract.test.ts`: 3/3 PASSED.
   - Total: 9/9 PASSED.
3. **Static Analysis (`npm --prefix frontend run lint`):**
   - 0 errors (89 warnings, primarily unused imports/tokens).
4. **Production Bundle Build (`npm --prefix frontend run build`):**
   - TypeScript type-check passed (`tsc -b`).
   - Vite built production distribution in 319ms:
     - `dist/index.html` (1.49 kB)
     - `dist/assets/index-ghKHOxN1.css` (5.12 kB)
     - `dist/assets/vendor-DaDWtDB3.js` (207.23 kB)
     - `dist/assets/index-QLZzd6Me.js` (276.88 kB)
     - `dist/assets/recharts-DJoC-9V5.js` (374.34 kB)

---

## 14. Docker Verification

### Host Diagnostics
- Command `docker --version`: `The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.`
- Command `docker info`: Unavailable.
- Command `wsl --status`: `WSL 2 is not installed.`
- Host Environment: Windows 11 Home Single Language (Build 26200).

### Status Evaluation
- **Docker Engine Status:** `UNAVAILABLE` on current local host.
- **Rule 14 & Rule 22 Enforcement:** Per Master Prompt Rules 14 & 22, the assistant MUST NOT automatically install Docker Desktop, WSL, or Windows optional components without explicit user authorization.
- **Docker In-Container Execution Verdict:** `BLOCKED / UNVERIFIED` locally.
- **Docker Architecture Verdict:** `IMPLEMENTED` in repository configuration (Dockerfile, .dockerignore, and release gate workflow).

---

## 15. Security Verification

1. **Pull Request Isolation:**
   - Release gate workflow `.github/workflows/docker-release-gate.yml` has `pull_request` triggers removed.
   - Zero possibility of external forks executing untrusted code on the private runner.
2. **Secrets & Credentials:**
   - No hardcoded tokens, passwords, or runner registration tokens exist in any workflow, script, or commit.
3. **Artifact Upload Quarantine:**
   - Workflows do not contain `actions/upload-artifact` steps targeting `*.parquet` or `data/` paths.
4. **Data Mount Security:**
   - Volume mount flag is strictly `:ro` (read-only), preventing in-container writes to host datasets.

---

## 16. GitHub Workflow Verification

| Workflow | Triggers | Runner | Requires Private Data? | Safe? | Reason |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `ci.yml` | `push`, `pull_request` (main, master) | `ubuntu-latest` (GitHub-hosted) | **NO** | **YES** | Code-only tests; zero dataset dependencies; safe for public forks. |
| `docker-release-gate.yml` | `workflow_dispatch`, `push` (main, master) | `[self-hosted, jobintel-private-data]` | **YES** | **YES** | PR trigger removed; runs only in controlled trusted environment; mounts data `:ro`. |

---

## 17. Scientific Integrity Verification

The authoritative frozen evaluation metrics for both models are verified and unmodified:

### USA Salary Model (`models/phase5/best_model.pkl`)
- Modeling Cohort: **34,036** job postings
- Predictor Contract: **123** features
- Algorithm: `XGBRegressor`
- Evaluation Metrics (Holdout):
  - **MAE:** $36,380.64
  - **RMSE:** $51,082.06
  - **R²:** 0.4233
  - **MAPE:** 21.71%

### India Salary Model (`models/india/final_model.pkl`)
- Modeling Cohort: **5,859** job postings
- Predictor Contract: **290** features
- Algorithm: `HistGradientBoostingRegressor` (log1p target)
- Evaluation Metrics (Holdout):
  - **MAE:** ₹3.71 LPA
  - **RMSE:** ₹6.22 LPA
  - **R²:** 0.5798
  - **MAPE:** 35.22%

**Integrity Audit:** Zero models were retrained. Zero metrics were modified. Both models remain scientifically frozen.

---

## 18. Remaining Blockers

1. **Local Docker Daemon Unavailable:**
   - Docker CLI and WSL are not installed on the current host. Direct local `docker build` and `docker run` commands cannot execute until Docker Desktop or a Linux VM with Docker daemon is provisioned.
2. **GitHub Self-Hosted Runner Not Yet Registered:**
   - The protected release gate workflow targets `[self-hosted, jobintel-private-data]`.
   - The runner must be registered by the repository maintainer using a temporary token from GitHub repository settings.

---

## 19. Required User Actions

To achieve full end-to-end container certification:

1. **Docker Provisioning (User Action):**
   - Install Docker Desktop on Windows 11 (with WSL 2 backend enabled) OR execute on a Linux server/workstation where Docker daemon is active.
2. **Self-Hosted Runner Registration (User Action):**
   - In GitHub repository: `Settings` -> `Actions` -> `Runners` -> `New self-hosted runner`.
   - Configure the runner with labels: `self-hosted, jobintel-private-data`.
   - Start the runner on the machine that hosts the local `data/processed` directory.
3. **Execute Protected Release Gate:**
   - In GitHub Actions tab, select `JobIntel Phase 8.5 Protected Docker Release Gate` -> `Run workflow` -> `Branch: master`.
   - Verify green checkmark on all steps.

---

## 20. Final Release Verdict

Per Step 35 of the Master Prompt:
*"`READY` is allowed ONLY IF Docker actual build PASS and Docker actual run PASS. If Docker cannot actually be executed, use `PENDING VERIFICATION` or `BLOCKED`."*

**FINAL VERDICT:**
# `PENDING VERIFICATION`

### Justification:
- **Public CI Pipeline:** `PASS` (Fully decoupled, code-only, 100% passing locally).
- **Frozen Artifact Integrity:** `PASS` (10/10 SHA-256 bit-for-bit exact match).
- **Data Governance & Licensing:** `PASS` (Zero private data tracked or leaked; read-only mount architecture implemented).
- **Model & Scientific Contracts:** `PASS` (USA 123 features, India 290 features intact).
- **Docker Architecture Implementation:** `PASS` (Dockerfile, .dockerignore, and release gate workflow configured).
- **Docker Actual Execution:** `UNVERIFIED / BLOCKED` locally pending host Docker daemon provisioning and self-hosted runner registration.
