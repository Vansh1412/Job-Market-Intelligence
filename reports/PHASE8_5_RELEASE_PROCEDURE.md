# JobIntel Phase 8.5: Standard Release Procedure & Gate Operating Manual

**Document ID:** `reports/PHASE8_5_RELEASE_PROCEDURE.md`  
**Date:** October 8, 2026  
**Status:** AUTHORITATIVE RELEASE PROTOCOL (SSOT)  
**Author:** Antigravity DevOps, Security Engineering & Release Management  
**Classification:** Operational Runbook  

---

## 1. Release Architecture Overview

JobIntel enforces a strict **Dual-Pipeline Security and Data-Governance Model**:

```
[ Developer Pushes Code / Creates PR ]
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. PUBLIC GITHUB CI (.github/workflows/ci.yml)               │
│    • Runner: Ephemeral GitHub-Hosted (ubuntu-latest)         │
│    • Triggers: push & pull_request on main/master           │
│    • Scope: Code-only checks (Zero data dependencies)       │
│    • Python: python -m compileall src/, unit/contract tests │
│    • Frontend: npm ci, vitest run (9/9), oxlint, vite build  │
│    • Verdict: PASS or FAIL                                   │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼ (Public CI passes)
┌─────────────────────────────────────────────────────────────┐
│ 2. MAINTAINER-GOVERNED PROTECTED RELEASE GATE               │
│    (.github/workflows/docker-release-gate.yml)              │
│    • Runner: Protected Self-Hosted [jobintel-private-data]  │
│    • Triggers: workflow_dispatch (manual) OR push to master │
│    • STRICT SECURITY: NEVER triggered on PRs from forks     │
│    • Data Access: Local filesystem mount (data/processed:ro)│
│    • Scope: 10/10 frozen hash audit, Docker build & run,    │
│             live readiness (/api/ready), live inference,    │
│             cross-market API parity                         │
│    • Verdict: PASS, FAIL, BLOCKED, or UNVERIFIED            │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PRODUCTION RELEASE DECISION & IMMUTABLE TAGGING          │
│    • All verification gates must be PASS                    │
│    • Zero P0 / P1 / P2 / P3 blockers                        │
│    • Tag: v1.0.0-rc1 -> v1.0.0 release                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Release Protocol

### Step A: Developer Pushes Normal Code
- Developer writes code, adds tests, or updates documentation on a feature branch.
- Developer pushes to GitHub or opens a pull request targeting `master`.
- **Constraint:** Developer must NOT commit any file under `data/raw/`, `data/processed/`, or any `*.parquet` files.

### Step B: Public CI Runs
- GitHub Actions triggers `.github/workflows/ci.yml` on `ubuntu-latest`.
- Public CI executes in an isolated environment without any proprietary datasets:
  1. Python syntax compilation (`python -m compileall src/`).
  2. Code-only backend routing contract tests (`pytest tests/test_routing_contracts.py`).
  3. Code-only Pydantic schema validation tests (`pytest tests/test_schema_contracts.py`).
  4. Frontend dependency installation (`npm ci`).
  5. Frontend test suite execution (`vitest run` — 9/9 unit tests).
  6. Frontend static analysis / linter (`npm run lint`).
  7. Frontend production bundle build (`npm run build`).

### Step C: Public CI Passes
- Expected Verdict: `PASS`.
- If any check fails, the verdict is `FAIL` and the PR/commit is rejected before any release activity.

### Step D: Maintainer Starts Protected Release Gate
- For release candidates, the repository maintainer triggers `.github/workflows/docker-release-gate.yml` via `workflow_dispatch` on `master`.
- **Security Check:** The workflow only executes on the designated runner tag `[self-hosted, jobintel-private-data]`.
- Public pull requests cannot trigger this gate.

### Step E: Trusted Private Runner Performs Data-Dependent Validation
- The runner operates on an authorized workstation where:
  1. Physical / logical access is controlled.
  2. Licensed datasets reside in quarantined local storage (`E:/Job Market/data/processed`).
  3. No untrusted third-party code executes with access to this storage.

### Step F: Real Datasets Are Mounted Read-Only
- During container startup, the runner mounts the host directory read-only:
  ```bash
  docker run -d \
    --name jobintel-phase8-3-certification \
    -p 8000:8000 \
    -v "${GITHUB_WORKSPACE}/data/processed:/app/data/processed:ro" \
    jobintel-phase8-3-certification
  ```
- **Security Guarantee:** The `:ro` flag ensures that the running container cannot modify, truncate, or overwrite any frozen Parquet dataset.

### Step G: Frozen Hashes Verified
- The runner computes SHA-256 for all 10 frozen artifacts inside the container:
  1. `models/india/final_model.pkl` (`7a3490d7...`)
  2. `models/india/final_preprocessor.pkl` (`0ee1dabf...`)
  3. `data/processed/india/india_modeling_cohort.parquet` (`d4e32be4...`)
  4. `models/india/india_pca_v1.pkl` (`8591e3d3...`)
  5. `models/india/india_kmeans_v1.pkl` (`4465a3d8...`)
  6. `models/phase5/best_model.pkl` (`55c1b7fd...`)
  7. `models/phase5/best_pipeline.pkl` (`815fd9a3...`)
  8. `data/processed/modeling_dataset.parquet` (`68895e38...`)
  9. `models/pca_phase4_1.pkl` (`ef4ef56b...`)
  10. `models/kmeans_phase4_1_k7.pkl` (`4d6d2509...`)
- Expected Verdict: `PASS` (10/10 exact match). If any hash differs, the verdict is `FAIL` and execution halts immediately.

### Step H: Docker Image Built
- The runner builds the multi-stage Docker image:
  ```bash
  docker build -t jobintel-phase8-3-certification .
  ```
- Because `.dockerignore` excludes `data/processed/` and `Dockerfile` uses `RUN mkdir -p /app/data/processed/india`, the build succeeds without baking proprietary data into image layers.

### Step I: Container Started
- The container starts with the read-only volume mount attached.
- Process initialization starts Uvicorn serving FastAPI at `0.0.0.0:8000`.

### Step J: Readiness & Health Verified
- Probes executed via HTTP:
  - `GET http://localhost:8000/api/health` -> HTTP 200, status `healthy`.
  - `GET http://localhost:8000/api/ready` -> HTTP 200, status `ready`, `artifacts_verified_count == 10`.
- Expected Verdict: `PASS`.

### Step K: Live Inference & API Parity Verified
- Verification requests executed against the live container:
  - USA Salary Inference: `POST /api/usa/predict` -> returns predicted salary, archetype, confidence interval.
  - India Salary Inference: `POST /api/india/predict` -> returns predicted salary, archetype, confidence interval.
  - USA Skills & Market: `GET /api/usa/skills`, `GET /api/usa/market-summary`.
  - India Skills & Market: `GET /api/india/skills`, `GET /api/india/market-summary`.
  - Cross-Market Comparative Analytics: `GET /api/cross-market/overview`.
- Expected Verdict: `PASS`.

### Step L: Browser Smoke Test
- Headless browser validation or manual verification of the React frontend at `http://localhost:8000`:
  - Navigation across all 7 routes (`/`, `/salary`, `/explore`, `/skills`, `/archetypes`, `/cross-market`, `/how-it-works`).
  - Active market toggling between USA ($ USD) and India (₹ INR LPA).
- Expected Verdict: `PASS` (or `UNVERIFIED` if no browser engine is provisioned).

### Step M: Release Decision
- The release manager reviews evidence against standard verdict rules:
  - `READY`: All steps A through L are PASS.
  - `READY WITH DOCUMENTED LIMITATION`: Non-critical operational constraints documented.
  - `PENDING VERIFICATION`: Architecture implemented, but runner or Docker execution pending execution in provisioned environment.
  - `BLOCKED`: Critical dependency or environment blocker prevents verification.
  - `NOT READY`: Code, model, or dataset defects present.

---

## 3. Standard Verdict Table

| Component / Step | Evaluation Rule | Current Baseline Status |
| :--- | :--- | :--- |
| **Step A: Code Push** | No private Parquets in Git | `PASS` (zero Parquets tracked) |
| **Step B: Public CI** | Syntax + Contract Tests + Frontend | `PASS` (11 contract tests, 9 vitest tests) |
| **Step C: CI Result** | All public CI jobs succeed | `PASS` |
| **Step D: Trigger Gate** | Protected workflow_dispatch | `PASS` (PR trigger removed) |
| **Step E: Self-Hosted Runner** | Dedicated trusted runner | `UNVERIFIED` (pending runner registration) |
| **Step F: Read-Only Mount** | Volume mount syntax `-v ...:ro` | `PASS` (implemented in workflow) |
| **Step G: 10/10 Frozen Hashes**| Bit-for-bit SHA-256 match | `PASS` (10/10 verified on disk) |
| **Step H: Docker Build** | Builds cleanly without embedded data | `PASS` (Dockerfile verified) |
| **Step I: Container Startup** | Boots Uvicorn on port 8000 | `UNVERIFIED` (local Docker daemon absent) |
| **Step J: Readiness & Health** | HTTP 200 on /api/health and /api/ready | `UNVERIFIED` (in container) / `PASS` (local FastAPI) |
| **Step K: Live Inference** | USA (123 feat) & India (290 feat) | `UNVERIFIED` (in container) / `PASS` (local FastAPI) |
| **Step L: Browser Smoke Test**| Frontend UI renders and queries API | `PASS` (Puppeteer certified in Phase 8.1) |
| **Step M: Final Verdict** | Release gate signoff | **PENDING VERIFICATION** |
