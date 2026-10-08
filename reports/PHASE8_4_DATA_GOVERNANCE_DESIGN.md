# JobIntel Phase 8.4: Data-Governed Docker Release Strategy Design

**Document ID:** `reports/PHASE8_4_DATA_GOVERNANCE_DESIGN.md`  
**Date:** October 8, 2026  
**Status:** DESIGN ONLY — NO CHANGES MADE  
**Author:** Antigravity AI Engineering & Release Gate Lead  
**Baseline Commit:** `f425876` (`fix: repair CI frozen-artifact and Docker data gate`)

---

## 1. Current Infrastructure & Environment Baseline

A comprehensive diagnostic audit of the host environment was performed:

| Component | State / Specification | Diagnostic Evidence |
|---|---|---|
| **Operating System** | Microsoft Windows 11 Home Single Language (64-bit) | Version 10.0.26200, Build 26200 |
| **Physical Memory (RAM)** | 16.0 GB Total Physical RAM (~15.7 GB Usable) | `16,849,256,448` bytes (`Win32_ComputerSystem`) |
| **Storage Availability** | Drive E: 136.7 GB Free<br>Drive D: 437.2 GB Free<br>Drive C: 46.5 GB Free | Ample disk capacity for Docker images & local cache |
| **Docker Engine / CLI** | **Not Installed / Not on PATH** | `Get-Command docker` returned command not found |
| **WSL Subsystem** | **Not Installed** | `wsl --status` returned Windows Subsystem for Linux is not installed |
| **Git Working Tree** | Clean, on branch `master` at commit `f425876` | `git status --short` is empty |
| **GitHub Remote** | `https://github.com/Vansh1412/Job-Market-Intelligence.git` | Public repository, default branch `master` |

---

## 2. Data Governance & Licensing Constraints

The project operates under the **DataForge Dataset License Agreement (Tier 1 — Internal Analytics)** audited in [`reports/license_compliance.md`](file:///e:/Job%20Market/reports/license_compliance.md):

1. **Section 4(b) Public Redistribution Prohibition:**
   > *"Licensee shall not sell, rent, lease, publish, or otherwise make the Raw Data (in whole or in substantial part) available to any third party as a standalone dataset, API, or bulk download."*
2. **Section 1.3 & Section 3.1 Record-Level Quarantine:**
   > *"Can we upload `data/raw/` or `data/processed/*.parquet` to GitHub? NO. Constitutes prohibited publication of Raw Data. All data files must remain local."*
3. **Derived Materials vs. Record-Level Data:**
   - Machine learning model weights (`models/*.pkl`), aggregate metrics, and source code are legally recognized as permissible **Derived Materials**.
   - Raw postings (`data/raw/`) and individual record-level analytical cohorts (`data/processed/modeling_dataset.parquet` and `data/processed/india/india_modeling_cohort.parquet`) are **strictly quarantined** to the local machine and protected by [`.gitignore`](file:///e:/Job%20Market/.gitignore).
4. **Zero-Leakage Governance:**
   - Proprietary Parquet files must never be committed to Git.
   - Parquets must never be base64-encoded into GitHub Actions Secrets.
   - Parquets must never be hosted on unapproved third-party cloud buckets.

---

## 3. Why GitHub-Hosted Runners Cannot Perform the Release Gate

Public GitHub-hosted runners (`ubuntu-latest`) execute within ephemeral Microsoft Azure virtual machines that initialize strictly from a clean `git clone` of the repository:

1. **Absence of Processed Datasets in Git Checkout:**
   Because `data/processed/` and `*.parquet` are intentionally and lawfully excluded by [`.gitignore`](file:///e:/Job%20Market/.gitignore), the repository cloned onto `ubuntu-latest` contains zero Parquet files.
2. **Docker Build Layer Failure:**
   The production [`Dockerfile`](file:///e:/Job%20Market/Dockerfile#L42) specifies:
   ```dockerfile
   COPY data/processed/ /app/data/processed/
   ```
   When BuildKit parses the build context on a clean GitHub runner, it aborts immediately because `data/processed/` does not exist.
3. **Runtime Readiness Probe Failure:**
   Even if the `COPY` instruction were bypassed, the running container's health check queries [`GET /api/ready`](file:///e:/Job%20Market/src/backend/main.py#L95), which triggers [`ModelRegistry.get_readiness_status()`](file:///e:/Job%20Market/src/backend/models/model_registry.py#L187). The registry validates all 10 frozen artifacts:
   - If `data/processed/modeling_dataset.parquet` or `data/processed/india/india_modeling_cohort.parquet` is missing, `artifacts_verified_count` drops to 8/10, setting `registry_status = RED` and returning HTTP 503 Service Unavailable.
4. **Impossibility of In-Runner Reconstruction:**
   The deterministic pipeline scripts ([`src/rebuild_phase2_1.py`](file:///e:/Job%20Market/src/rebuild_phase2_1.py) and [`src/india/feature_engineering.py`](file:///e:/Job%20Market/src/india/feature_engineering.py)) require the raw DataForge snapshot (`data/raw/dataset_A/data/jobs.parquet`), which is 394,300 rows and likewise cannot be committed or transmitted to GitHub runners.

**Conclusion:** The full containerized release gate cannot execute on public GitHub-hosted infrastructure without violating data license governance.

---

## 4. Self-Hosted Runner Feasibility Analysis

A GitHub Actions **self-hosted runner** allows executing workflows on a dedicated, controlled machine while retaining full cryptographic and data custody.

### Technical Feasibility Assessment

| Parameter | Finding | Feasibility Impact |
|---|---|---|
| **Host Compute & RAM** | 16 GB RAM, 8-core CPU | **Sufficient.** Exceeds requirements for Docker container execution, Pytest, and Node build. |
| **Host Disk Space** | >136 GB free on Drive E: | **Sufficient.** Ample capacity for runner binaries, Docker layers, and temp workspaces. |
| **Local Data Presence** | All 10/10 frozen artifacts are present on Drive E: with bit-for-bit verified SHA-256 hashes | **Verified.** Full data access without transmitting data over the internet. |
| **Host Daemon Requirement** | Docker CLI and WSL2 are currently not installed | **Prerequisite Required.** WSL2 or Docker Desktop must be provisioned before execution. |
| **Network & Outbound Port** | Outbound HTTPS (port 443) to `api.github.com` | **Standard.** Self-hosted runners use long-polling via HTTPS; no inbound open ports required. |

---

## 5. Docker Runtime Data Strategy (Mount vs. Build Context)

Two architectural patterns exist for providing protected data to Docker on the self-hosted runner:

### Option A: Local Build Context (Current Dockerfile)
- **Mechanism:** On the self-hosted runner, the runner workspace directory has local access to `data/processed/`. The `docker build` command uses the local files during image building.
- **Pros:** Preserves existing [`Dockerfile`](file:///e:/Job%20Market/Dockerfile) unchanged.
- **Cons:** Embeds the proprietary Parquets into the resulting local Docker image layers. The image cannot be pushed to any container registry.

### Option B: Runtime Read-Only Volume Mount (Recommended Architecture)
- **Mechanism:**
  1. [`Dockerfile`](file:///e:/Job%20Market/Dockerfile) is updated to create `/app/data/processed` as an empty directory rather than `COPY data/processed/ /app/data/processed/`.
  2. The container image builds cleanly on any environment (code, dependencies, frontend, models).
  3. At runtime on the self-hosted release gate, the protected datasets are mounted read-only:
     ```bash
     docker run -d --name jobintel-app -p 8000:8000 \
       -v "E:/Job Market/data/processed:/app/data/processed:ro" \
       jobintel-phase8-3-certification
     ```
- **Pros:**
  - Strict data isolation: The Docker image itself contains zero proprietary raw/processed cohorts.
  - Immutability: The `:ro` flag guarantees that the running container cannot write, mutate, or corrupt the frozen on-disk Parquets.
  - Portability: The Dockerfile can build cleanly on both GitHub-hosted and self-hosted environments.

---

## 6. Security Implications on a Public Repository

Because `Vansh1412/Job-Market-Intelligence` is a **public repository**, deploying a self-hosted runner introduces specific security threat vectors that must be mitigated:

### Threat Model: Pull Request Code Execution
- **Risk:** If an external user opens a Pull Request against the public repository, a default self-hosted runner could execute arbitrary code submitted in the PR, potentially accessing local disk files.
- **Mandatory Countermeasures:**
  1. **Strict Branch Trigger:** The self-hosted workflow must trigger **ONLY on `push` to `master`** (or manual `workflow_dispatch`). It must **NEVER trigger on `pull_request`**.
  2. **Custom Runner Label:** The runner must be tagged with a unique, explicit label:
     ```yaml
     runs-on: [self-hosted, jobintel-private-data]
     ```
     Generic labels (`runs-on: self-hosted`) must not be used.
  3. **GitHub Repository Settings:** Under `Settings -> Actions -> General -> Fork pull request workflows from outside collaborators`, configure: **"Require approval for all outside collaborators"**.
  4. **Zero Artifact Leakage:** The workflow must strictly prohibit `actions/upload-artifact` targeting any path inside `data/` or any file matching `*.parquet`.
  5. **Ephemeral Execution & Read-Only Mounts:** Volume mounts must always specify `:ro`.

---

## 7. Dual-Track Release-Gate Architecture

```
                                  [ Git Push to master ]
                                            |
                    +-----------------------+-----------------------+
                    |                                               |
         [ Track 1: GitHub-Hosted CI ]              [ Track 2: Self-Hosted Gate ]
         runs-on: ubuntu-latest                     runs-on: [self-hosted, jobintel-private-data]
                    |                                               |
         - Checkout tracked code                    - Checkout tracked code
         - Set up Python & Node                     - Verify 10/10 Frozen Hashes on Disk
         - Install dependencies                     - Build Production Docker Image
         - Frontend Vitest (9/9)                    - Mount data/processed:ro
         - Frontend Build (Vite SPA)                - In-Container 10/10 Hash Verification
         - Code-only unit tests                     - /api/health & /api/ready Probes
                    |                               - USA & India Prediction Parity Tests
             [ STATUS: PASS ]                       - Cross-Market & Skills Endpoints
                                                    - Container Log Security Audit
                                                                    |
                                                             [ STATUS: PASS ]
                                                                    |
                                                      =============================
                                                      FINAL VERDICT: RC READY
                                                      =============================
```

---

## 8. Exact Files That Would Change (Upon Approval)

If the user approves implementing this data-governed release strategy:

1. **[`.github/workflows/docker-release-gate.yml`](file:///e:/Job%20Market/.github/workflows/docker-release-gate.yml)**
   - Update `runs-on: [self-hosted, jobintel-private-data]`.
   - Remove `pull_request` event trigger; retain `push` to `master` and `workflow_dispatch`.
   - Update Docker run step to include read-only data volume mount (`-v "E:/Job Market/data/processed:/app/data/processed:ro"`).
2. **[`Dockerfile`](file:///e:/Job%20Market/Dockerfile)**
   - Replace `COPY data/processed/ /app/data/processed/` with `RUN mkdir -p /app/data/processed /app/data/processed/india` to allow clean builds in environments where Parquets are injected at runtime via volume mount.
3. **[`reports/docker_validation.md`](file:///e:/Job%20Market/reports/docker_validation.md)**
   - Document the verified self-hosted runtime container execution.

---

## 9. Exact Files That Will NOT Change

The following files are strictly frozen and will **never** be altered:

1. All 10 Frozen Research Artifacts:
   - `models/india/final_model.pkl` (`7a3490d7...`)
   - `models/india/final_preprocessor.pkl` (`0ee1dabf...`)
   - `models/india/india_pca_v1.pkl` (`8591e3d3...`)
   - `models/india/india_kmeans_v1.pkl` (`4465a3d8...`)
   - `models/phase5/best_model.pkl` (`55c1b7fd...`)
   - `models/phase5/best_pipeline.pkl` (`815fd9a3...`)
   - `models/pca_phase4_1.pkl` (`ef4ef56b...`)
   - `models/kmeans_phase4_1_k7.pkl` (`4d6d2509...`)
   - `data/processed/india/india_modeling_cohort.parquet` (`d4e32be4...`)
   - `data/processed/modeling_dataset.parquet` (`68895e38...`)
2. All Application Code ([`src/backend/**`](file:///e:/Job%20Market/src/backend/)): Zero changes to routers, prediction logic, or model loading.
3. All Frontend Code ([`frontend/src/**`](file:///e:/Job%20Market/frontend/src/)): Zero changes to UI, state, or components.
4. Repository Safeguards ([`.gitignore`](file:///e:/Job%20Market/.gitignore)): Zero changes to raw and processed data exclusion rules.
5. All Backend Test Suites ([`tests/**`](file:///e:/Job%20Market/tests/)): Zero test modifications.

---

## 10. Rollback Strategy

If any failure occurs during potential implementation:
1. Revert any staged or committed workflow edits back to commit `f425876`:
   ```bash
   git reset --hard f425876
   git push origin master
   ```
2. Unregister and terminate the local GitHub Actions runner service via `./config.cmd remove`.
3. Stop and prune all local Docker containers and image tags:
   ```bash
   docker stop jobintel-phase8-3-certification
   docker rm jobintel-phase8-3-certification
   ```

---

## 11. Verification Plan

When executed under user authorization:
1. **Pre-Flight:** Re-calculate SHA-256 for all 10 on-disk artifacts. Verify 10/10 exact matches.
2. **Runner Registration:** Start the runner with label `jobintel-private-data`. Verify `Active / Idle` state in GitHub repository settings.
3. **Workflow Trigger:** Push or trigger `docker-release-gate.yml`.
4. **Execution Audit:** Monitor all 18 gate steps:
   - Docker CLI & daemon verification.
   - Production image build.
   - Container start with `-v ...:/app/data/processed:ro`.
   - In-container cryptographic verification of all 10 artifacts.
   - Live HTTP probes: `/api/health`, `/api/ready` (expect HTTP 200, `GREEN`, 10/10).
   - Live prediction inference: USA endpoint and India endpoint.
   - Live skills endpoints and cross-market endpoint.
   - ModelRegistry singleton identity check inside container.
   - Full Pytest test suite inside container.
   - Frontend Vitest tests (9/9) and build check.
   - Container log audit (0 fatal errors, 0 Tracebacks).
   - Clean container shutdown and prune.
5. **Final Sign-Off:** Declare `RC READY` only upon complete green execution.

---

## 12. Final Status

**`DESIGN ONLY — NO CHANGES MADE`**  
Awaiting explicit user review and authorization prior to any installation or configuration.
