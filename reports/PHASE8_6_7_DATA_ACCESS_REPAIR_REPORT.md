# PHASE 8.6.7 — HOST-SIDE BACKEND TEST DATA ACCESS REPAIR & RE-CERTIFICATION REPORT

**Repository:** `Vansh1412/Job-Market-Intelligence`  
**Branch:** `master`  
**Date:** October 9, 2026  
**Status:** **PASS (100% CERTIFIED)** — Awaiting Manual Protected GitHub Actions Dispatch  

---

## 1. Executive Summary

In the protected GitHub Actions release gate run on the self-hosted Windows runner, **Step 20: Host-Side Backend Tests with Linked Private Data** failed with 68 failed and 30 passed tests. Analysis revealed that all 68 test failures were downstream of missing private datasets (`data/processed/modeling_dataset.parquet` and `data/processed/india/india_modeling_cohort.parquet`), which prevented model registry initialization and empirical calculation across backend services.

The root cause was definitively isolated: on a clean runner workspace checkout, the parent `data/` directory does not exist because private datasets are untracked in Git. Consequently, Windows `mklink /J` failed silently with `"The system cannot find the path specified"`, causing host-side pytest to execute without data access.

We implemented a robust, safe junction lifecycle in Step 20 and Step 22 that:
1. Validates the host source directory and verifies that both required private datasets exist and are non-empty.
2. Ensures the parent `data/` directory exists before creating the junction.
3. Prints a concise data-access diagnostic (verifying file existence and byte sizes without exposing row contents).
4. Executes the test suite in a `try...finally` block that safely unlinks the junction and preserves native exit codes.
5. In Step 22, performs residual reparse-point cleanup without touching the private source data on the `E:` drive.

Testing on both the host repository and the self-hosted runner workspace confirmed that **all 98/98 backend tests pass**, all 9 frontend tests pass, the frontend builds cleanly, and all 10 frozen research artifact cryptographic signatures match bit-for-bit.

---

## 2. Root Cause Forensic Analysis

| Factor | Detail / Finding |
| :--- | :--- |
| **Runner Workspace Location** | `D:\EVERYTHING\GitHubActionsRunner\_work\Job-Market-Intelligence\Job-Market-Intelligence` |
| **Private Data Source Location** | `E:\Job Market\data\processed` |
| **Git Exclusion Policy** | Per Dataforge Tier 1 license compliance, `data/` and all `.parquet` files are ignored in `.gitignore`. |
| **Clean Checkout State** | `actions/checkout@v4` checks out only git-tracked files. The runner workspace contained no `data/` folder. |
| **Failure Mechanism** | Step 20 attempted `cmd.exe /c "mklink /J \"${{ github.workspace }}\data\processed\" \"${env:HOST_DATA_PATH}\""`. On Windows, `mklink /J` requires the immediate parent directory (`data/`) to exist; without it, `mklink` fails with `The system cannot find the path specified.` (exit code 1). |
| **Silent Cascade** | The unhandled exit code allowed execution to proceed directly to `python -m pytest tests/ -v`. |
| **Observed Failure Profile** | 68 tests failed with `FileNotFoundError` or downstream `ModelIntegrityError` (`india_cohort` missing in `ModelRegistry`). Exactly 30 tests passed (routing, schema validation, and unit tests independent of dataset files). |
| **Why Container Succeeded** | Step 9 launched Docker with `-v "${env:HOST_DATA_PATH}:/app/data/processed:ro"`. The Docker engine automatically creates mount points in container filesystems, so in-container runtime checks passed completely. |

---

## 3. Exact Code Changes

### File Modified: `.github/workflows/docker-release-gate.yml`

1. **Step 20: Robust Directory Junction Lifecycle & Diagnostics:**
   - **Source Resolution:** Normalized `$env:HOST_DATA_PATH` to Windows backslashes with fallback to `E:\Job Market\data\processed`.
   - **Pre-flight Assertion:** Verified existence, readability, and non-zero size for both `modeling_dataset.parquet` and `india\india_modeling_cohort.parquet` on the host.
   - **Safe Workspace Mapping:** Verified whether `${{ github.workspace }}\data\processed` already exists; created parent `${{ github.workspace }}\data` directory before creating junction; verified junction creation with `New-Item -ItemType Junction`.
   - **Concise Diagnostics:** Printed file paths, byte sizes, and readable status before invoking pytest (no row contents printed).
   - **Safe Teardown:** Ran pytest in a `try...finally` block. In `finally`, verified the target is a ReparsePoint before removing with `cmd.exe /c "rmdir \"...\""` (unlinks junction without touching target files), and removed empty parent `data\` folder.
   - **Exit-Code Preservation:** Preserved `$LASTEXITCODE` from pytest and surfaced native failures without masking.

2. **Step 22: Hardened Residual Cleanup:**
   - Verified that `${{ github.workspace }}\data\processed` possesses the `ReparsePoint` file attribute before calling `rmdir`.
   - Cleaned up empty parent `${{ github.workspace }}\data` directory if left behind.

---

## 4. Test Verification: Before vs. After

### Backend Pytest Suite (`python -m pytest tests/ -v`)

| Test Module | Run 20 (Before) | Phase 8.6.7 (After) | Status |
| :--- | :---: | :---: | :---: |
| `tests/test_prediction_parity.py` | FAILED (11) | **11 passed** | **RESOLVED** |
| `tests/test_archetype_parity.py` | FAILED (15) | **15 passed** | **RESOLVED** |
| `tests/test_chart_contracts.py` | FAILED (8) | **8 passed** | **RESOLVED** |
| `tests/test_end_to_end_integration.py` | FAILED (15) | **16 passed** | **RESOLVED** |
| `tests/test_input_validation.py` | FAILED (2) | **17 passed** | **RESOLVED** |
| `tests/test_market_analytics.py` | FAILED (5) | **5 passed** | **RESOLVED** |
| `tests/test_skill_integrity.py` | FAILED (10) | **12 passed** | **RESOLVED** |
| `tests/test_golden_predictions.py` | FAILED (2) | **2 passed** | **RESOLVED** |
| `tests/test_routing_contracts.py` | 4 passed | **4 passed** | **PASS** |
| `tests/test_schema_contracts.py` | 8 passed | **8 passed** | **PASS** |
| **TOTAL** | **30 passed, 68 failed** | **98 passed, 0 failed (100%)** | **100% PASS** |

- **Execution Time on Runner Workspace:** 10.78 seconds.
- **Execution Time on Local Workspace:** 11.84 seconds.
- **Remaining Failures:** 0.

---

## 5. Frozen Research Artifact Cryptographic Integrity (10/10)

| Index | Artifact Path | Expected & Verified SHA-256 Hash | Status |
| :---: | :--- | :--- | :---: |
| 1 | `models/india/final_model.pkl` | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **MATCH (100%)** |
| 2 | `models/india/final_preprocessor.pkl` | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **MATCH (100%)** |
| 3 | `data/processed/india/india_modeling_cohort.parquet` | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | **MATCH (100%)** |
| 4 | `models/india/india_pca_v1.pkl` | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **MATCH (100%)** |
| 5 | `models/india/india_kmeans_v1.pkl` | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **MATCH (100%)** |
| 6 | `models/phase5/best_model.pkl` | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **MATCH (100%)** |
| 7 | `models/phase5/best_pipeline.pkl` | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | **MATCH (100%)** |
| 8 | `data/processed/modeling_dataset.parquet` | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | **MATCH (100%)** |
| 9 | `models/pca_phase4_1.pkl` | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | **MATCH (100%)** |
| 10 | `models/kmeans_phase4_1_k7.pkl` | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | **MATCH (100%)** |

---

## 6. Scientific & Engineering Governance Contracts

1. **USA Model Feature Count:** Exactly 123 features (`assert usa_feats == 123`).
2. **India Model Feature Count:** Exactly 290 features (`assert india_feats == 290`).
3. **USA Archetype Count:** Exactly 7 archetypes.
4. **India Archetype Count:** Exactly 6 archetypes.
5. **Model Registry Status:** Initialized with status **`GREEN`**, zero drift.
6. **Cross-Market Isolation:** Independent dual-currency modeling (USD for USA, INR/LPA for India), no synthetic FX translation.
7. **Frontend Validation:**
   - Vitest: 9 passed across 3 test suites (`routing`, `skills_contract`, `calculator`).
   - ESLint: 0 errors.
   - Vite Build: Production bundle generated in 20.83s (`dist/index.html`, assets compiled cleanly).
8. **Git Hygiene & Data Privacy:**
   - Executed `git ls-files *.parquet *.csv *.raw data/`: returned **0 entries**.
   - Verified that no private data, temporary junction, or raw parquet was committed to git.

---

## 7. Final Certification Verdict

# **`STATUS: PASS`** (Ready for Manual Dispatch)

The root cause of Step 20 failure has been repaired cleanly. Both host-side backend and frontend test suites pass 100%. Cryptographic integrity is verified across all 10 frozen artifacts. In accordance with the project constraints, **automatic GitHub Actions dispatch was withheld**. The release gate is ready for manual workflow dispatch.
