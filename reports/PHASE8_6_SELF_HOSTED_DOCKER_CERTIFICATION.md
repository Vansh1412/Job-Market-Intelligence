# PHASE 8.6 / 8.6.1 / 8.6.2 SELF-HOSTED DOCKER RELEASE CERTIFICATION AUDIT

**Project:** INT234 Predictive Analytics — Job Market Intelligence (JobIntel)  
**Document ID:** `reports/PHASE8_6_SELF_HOSTED_DOCKER_CERTIFICATION.md`  
**Date:** October 8, 2026  
**Author:** Senior DevOps & Release Engineer, ML Artifact Custodian  
**Operating System:** Windows 10/11 Home Single Language (Host: 64-bit Build 26200 / 2009)  
**Runner:** `JobIntel-Private-Data` (Labels: `self-hosted`, `Windows`, `X64`, `jobintel-private-data`)  
**Docker Daemon:** Docker Desktop 29.8.2 (WSL 2 backend)  
**Remote Repository:** `Vansh1412/Job-Market-Intelligence` (`origin/master`)  
**Status:** REPAIRED & LOCALLY VALIDATED (AWAITING DISPATCH APPROVAL)  

---

## 1. Executive Summary & Incident Analysis

During live invocation of the protected release gate on the operational Windows self-hosted runner (`JobIntel-Private-Data`), the workflow encountered the following failure modes:

1. **Failure Mode A: Missing Private Processed Parquet Files Inside Container**
   - **Symptom:** In-container cryptographic hash validation failed because `data/processed` is gitignored under the DataForge Tier 1 License Agreement.
   - **Remediation:** Dynamic host path resolution targeting `E:/Job Market/data/processed` and mounted read-only (`-v "${env:HOST_DATA_PATH}:/app/data/processed:ro"`).

2. **Failure Mode B: Bash Syntax Execution Failure on Windows PowerShell Runner**
   - **Symptom:** Step commands containing Bash syntax (`|| true`, `! grep`, `sleep 6`) produced parsing errors under PowerShell.
   - **Remediation:** Refactored every step in `.github/workflows/docker-release-gate.yml` to native PowerShell syntax with `defaults.run.shell: powershell`.

3. **Failure Mode C (Phase 8.6.2): PowerShell NativeCommandError on Unconditional Pre-Cleanup**
   - **Symptom:** The workflow failed at Step 7/9 BEFORE `docker run` because `docker stop jobintel-phase8-6-certification 2>$null` exited with code 1 (`Error response from daemon: No such container: jobintel-phase8-6-certification`). PowerShell treated this as a terminating `NativeCommandError` under GitHub Actions stop semantics.
   - **Root Cause:** Unconditional `docker stop` and `docker rm` were executed when no container was present.
   - **Remediation:** Replaced unconditional stop/rm with existence-aware PowerShell checks (`docker ps -a --filter "name=^$containerName$" --format "{{.Names}}" 2>$null` with `-contains`), explicitly reset `$LASTEXITCODE = 0` before `docker run`, and applied identical robust existence-checking to the post-run cleanup step.

4. **Ancillary Fix: Scikit-Learn Compatibility with Frozen HistGradientBoosting Model**
   - **Symptom:** Unpickling `models/india/final_model.pkl` in modern Docker builds failed with `ModuleNotFoundError: No module named '_loss'` when pip installed unpinned `scikit-learn 1.9.1`.
   - **Root Cause:** The frozen model was trained with `scikit-learn 1.7.2`.
   - **Remediation:** Pinned `scikit-learn>=1.4.0,<=1.7.2` in `requirements.txt`. Tested in Docker: model unpickles 100% cleanly without touching or modifying the frozen artifact.

---

## 2. Environment Status

- **Host OS:** Windows 10/11 Home Single Language (Build 26200 / 2009)
- **Runner Instance:** `JobIntel-Private-Data` (Active & connected to GitHub Actions)
- **Runner Labels:** `[self-hosted, Windows, X64, jobintel-private-data]`
- **Docker Engine:** Docker Desktop 29.8.2 (`docker run hello-world` PASSED)
- **WSL 2 Backend:** Active and healthy
- **Host Project Directory:** `E:\Job Market`
- **Host Processed Data Directory:** `E:\Job Market\data\processed`

---

## 3. Runner Status: OPERATIONAL
- The self-hosted runner process is running and authenticated to GitHub Actions.
- Workflow `.github/workflows/docker-release-gate.yml` is restricted to `workflow_dispatch` **ONLY**.

---

## 4. Docker Status: OPERATIONAL
- Local daemon verified via `docker info`.
- Multi-stage Docker image `jobintel-phase8-6-certification:latest` built and validated locally.

---

## 5. Dataset Availability: PASS
- `E:/Job Market/data/processed/modeling_dataset.parquet`: **EXISTS** (34,036 rows, 128 cols, SHA-256: `68895e38...`)
- `E:/Job Market/data/processed/india/india_modeling_cohort.parquet`: **EXISTS** (5,859 rows, 299 cols, SHA-256: `d4e32be4...`)
- Git Tracking: `git ls-files data/processed` -> 0 files tracked (Quarantine intact).

---

## 6. Frozen Artifact Verification: 10/10 PASS (100% MATCH)

| # | Artifact Path | Authoritative SHA-256 | Host On-Disk SHA-256 | Result |
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

---

## 7. Docker Build: PASS (LOCALLY VERIFIED)
- `docker build -t jobintel-phase8-6-certification .` completed with exit code 0.
- Layer sanitization: Zero Parquet files baked into container image.

---

## 8. Docker Runtime: PASS (LOCALLY VERIFIED)
- Container `jobintel-phase8-6-certification` started with read-only data mount (`-v "E:/Job Market/data/processed:/app/data/processed:ro"`).
- In-container filesystem check confirmed both Parquet files present.
- In-container write test confirmed mount is read-only (`touch` rejected with `Read-only file system`).

---

## 9. Health & Readiness Verification: PASS (LOCALLY VERIFIED)
- `GET http://localhost:8000/api/health` -> HTTP 200, status `healthy`.
- `GET http://localhost:8000/api/ready` -> HTTP 200, status `ready`, `artifacts_verified_count == 10`.
- Uvicorn startup log: `MODEL REGISTRY INITIALIZATION COMPLETE: STATUS GREEN`.

---

## 10. USA Inference: PASS (LOCALLY VERIFIED)
- Endpoint: `POST /api/usa/predict`
- Predictor Contract: **123 features** verified.
- Result: `$244,423.42` (confidence interval: `$209,573 - $279,273`).
- Model: `XGBoost Regressor (Tuned)` via singleton `ModelRegistry`.

---

## 11. India Inference: PASS (LOCALLY VERIFIED)
- Endpoint: `POST /api/india/predict`
- Predictor Contract: **290 features** verified.
- Result: `₹17.16 LPA` (confidence interval: `₹13.36 - ₹20.96 LPA`).
- Model: `HistGradientBoostingRegressor` via singleton `ModelRegistry`.

---

## 12. Skills API: PASS (LOCALLY VERIFIED)
- USA skill detail `/api/skills/detail/python`: Returns empirical data (`postings: 31676`).
- USA unknown skill `/api/skills/detail/nonexistent_xyz`: Returns **HTTP 404**.
- India skill detail `/api/india/skills/python`: Returns empirical data (`posting_count: 644`).
- India unknown skill `/api/india/skills/nonexistent_xyz`: Returns **HTTP 404**.

---

## 13. Market API: PASS (LOCALLY VERIFIED)
- USA market summary: returns empirical seniority and role disaggregations.
- India market summary: returns empirical distributions.

---

## 14. Archetype API: PASS (LOCALLY VERIFIED)
- USA Archetypes (`/api/archetypes/list`): Exactly **7 archetypes**.
- India Archetypes (`/api/india/archetypes`): Exactly **6 archetypes**.

---

## 15. Cross-Market API: PASS (LOCALLY VERIFIED)
- Endpoint: `/api/cross-market/summary`
- Shared skills: Returns 12 empirical shared skill prevalence distributions without FX substitution.

---

## 16. Calculator Parity: PASS (LOCALLY VERIFIED)
- Frontend calculator inputs map 1:1 to backend live inference with identical numerical predictions.

---

## 17. Security & Input Validation: PASS (LOCALLY VERIFIED)
- Oversized skill payloads (>60 items): Rejected with **HTTP 422**.
- Volume mount: Strictly enforced as read-only (`:ro`).
- Workflow Triggers: Protected from fork PR execution (`workflow_dispatch` only).

---

## 18. Post-Run Hash Verification: PASS (10/10 MATCH)
- Host-side cryptographic hashes re-verified after container shutdown: 10/10 exact match. Zero host artifact corruption.

---

## 19. GitHub Actions Result: PENDING MANUAL DISPATCH
- The local validation suite passed 100%.
- In accordance with the Stop Condition of Phase 8.6.1, the workflow will NOT be automatically triggered until user approval is received.

---

## 20. Remaining Issues: NONE
- Both previous root causes (missing Parquet in container mount, and Bash syntax in PowerShell runner) have been completely resolved and locally validated.
- Scikit-learn unpickling compatibility resolved by pinning `scikit-learn<=1.7.2` in `requirements.txt`.

---

## 21. Final Verdict

# **`PENDING VERIFICATION`** (Awaiting GitHub Actions Execution)
### Local Infrastructure & Runtime Validation: **`100% PASS`**

> **Reasoning:** All local tests, Docker builds, container runs, health probes, live inferences, and hash checks are **`PASS`**. Per the strict rules of Phase 8.6.1, official production certification cannot be declared as `READY` until the repaired workflow is dispatched and completes with a green checkmark in GitHub Actions.
