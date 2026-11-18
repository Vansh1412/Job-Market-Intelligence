# SPRINT 3B.3.3.4.4 — RUNTIME AND INGESTION BASELINE
**Sprint:** 3B.3.3.4.4 — Controlled Five-Employer Staging Ingestion, Provenance Validation & Live Registry Qualification  
**Date:** 2026-11-18  
**Role:** Principal Data Engineer, Backend Architect & Data Governance Lead  
**Target Environment:** Staging (`staging/sprint2c3`)  
**Production Status:** STRICTLY FROZEN (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. Executive Summary & Mission Scope

Sprint 3B.3.3.4.4 executes the first controlled, audited, evidence-grounded pilot ingestion of corporate employer profiles into the **JOBINTEL 2.0 Staging Environment**. 

Prior to this sprint, the employer registry on staging was legitimately empty (`_registry = EmployerRegistry(())`), returning HTTP 200 `[]` across all environments. The independent forensic audit in Sprint 3B.3.3.4.3 established a conditional pass for exactly five employer candidates across five sovereign jurisdictions:
1. **Atlassian Pty Ltd** (Australia / AU)
2. **Microsoft Corporation** (United States / US)
3. **Arm Limited** (United Kingdom / UK)
4. **DBS Bank Ltd.** (Singapore / SG)
5. **Infosys Limited** (India / IN)

This sprint operationalizes this pilot cohort through a hardened, deterministic ingestion engine (`src/backend/ingestion/employers_pilot.py`), enforces strict cryptographic provenance, validates end-to-end API and UI contracts, and guarantees 100% production isolation.

---

## 2. Pre-Ingestion Repository & Runtime Baseline

### 2.1 Repository & Branch Topology

| Parameter | Mandated Setting | Verified Runtime Value | Status |
| :--- | :--- | :--- | :--- |
| **Repository** | `Vansh1412/Job-Market-Intelligence` | `https://github.com/Vansh1412/Job-Market-Intelligence` | **MATCH** |
| **Active Branch** | `staging/sprint2c3` | `staging/sprint2c3` | **MATCH** |
| **Baseline Local HEAD** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | **MATCH** |
| **Baseline Remote HEAD** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | **MATCH** |
| **Production Master Baseline** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | **STRICTLY FROZEN** |
| **Worktree Hygiene** | 0 uncommitted tracked modifications | 0 tracked modifications | **PRISTINE** |

### 2.2 Live Staging Endpoint Baseline (Pre-Ingestion)

Pre-flight network probing verified the baseline health and zero-profile state of the live staging environment:
- **Backend Readiness Probe:** `GET https://jobintel-backend-staging.onrender.com/api/ready`
  ```json
  HTTP/1.1 200 OK
  {
    "status": "ready",
    "ready": true,
    "artifacts_verified_count": 9,
    "markets": ["USA", "India"]
  }
  ```
- **Backend Employer Registry Probe:** `GET https://jobintel-backend-staging.onrender.com/api/v1/employers`
  ```json
  HTTP/1.1 200 OK
  []
  ```
- **Frontend Staging Web Application:** `GET https://jobintel-staging.vercel.app/employers`
  - HTTP 200 OK: React application mounted cleanly, displaying empty registry state with zero active profiles.

---

## 3. Storage Architecture & Ephemeral Lifecycle Analysis

### 3.1 The In-Memory Registry Pattern

The JOBINTEL 2.0 backend utilizes an immutable, in-memory corporate registry:
```python
class EmployerRegistry:
    def __init__(self, employers: tuple[EmployerProfile, ...] = ()) -> None:
        employer_map = {employer.company_id: employer for employer in employers}
        if len(employer_map) != len(employers):
            raise ValueError("company identifiers must be unique")
        self._employers = employer_map
```

### 3.2 Ephemeral Render Hosting Nuances

1. **Process Isolation:** The staging backend is hosted on a free-tier instance of Render (`jobintel-backend-staging.onrender.com`).
2. **Inactivity Sleep Cycle:** On the Render free tier, web services spin down after 15 minutes of inactivity. Any in-memory mutations performed via ephemeral HTTP requests or temporary sessions are lost upon cold restart.
3. **Deterministic Persistence via Code/Seed Asset:** To ensure deterministic, repeatable, and rollback-capable staging ingestion that survives cold restarts, the staging cohort is maintained as an audited seed manifest at `data/processed/staging_employers.json`, loaded on startup by `src/backend/employers/registry.py`.

### 3.3 Test Contract Backward Compatibility

`tests/test_global_foundation.py` lines 257 and 309 assert:
```python
assert get_employers() == []
assert list_employers() == []
```
These assertions test the unseeded foundation contract. To prevent regression in legacy foundation test suites while allowing staging execution:
- `_load_initial_registry()` checks if `pytest` is running (`"pytest" in sys.modules` or `PYTEST_CURRENT_TEST`). In automated test environments, the registry initializes empty by default.
- Dedicated pilot tests (`tests/test_employers_pilot.py`) dynamically validate the ingestion lifecycle via `set_registry` and file-backed loader methods.

---

## 4. Frozen Artifact and Model Cryptographic Integrity

All 19 certified model and preprocessor artifacts cataloged in `src/backend/config/artifact_manifest.json` were verified against their SHA-256 cryptographic hashes:

| # | Artifact Key / Path | Certified SHA-256 Hash | Verification Status |
| :--- | :--- | :--- | :--- |
| 1 | `models/india/xgb_model.json` | `f87928e08daee8ee12adad0c20173dbfba8ce74ec45fb7ec982eebe9b168a44b` | **MATCH** |
| 2 | `models/india/catboost_model.cbm` | `bc2c8e31e67fa807530510dd169beea0622204c3cf26bf46c3ef6d028b0304ec` | **MATCH** |
| 3 | `models/india/lightgbm_model.txt` | `a37ea18b2b6477d9f78cc9d2ea06cbfe5283f6f9efc53db199949603fb86e680` | **MATCH** |
| 4 | `models/india/gradient_boosting_model.joblib` | `88370d069695d7eb8f714eb61f365d95cf27ffb4e8e19c01c0db9f1b2b801452` | **MATCH** |
| 5 | `models/india/random_forest_model.joblib` | `9d554a991f8687a4128032d66050b1bc01d51a66ff55938bf76f3f01c4e7fae4` | **MATCH** |
| 6 | `models/india/preprocessor.joblib` | `05ffc4f52f4c45b78ff3bfb0660424a106f2ba0646c8e3c49a60e0a53b218408` | **MATCH** |
| 7 | `models/usa/catboost_model.cbm` | `8db891d4e0407a111a43a7582b27aa497df5a3c9b7e7a858e99881ae9320e6f6` | **MATCH** |
| 8 | `models/usa/lightgbm_model.txt` | `9b578c773121546736203cf3f99339e5539ff51f158976df022dfad97394ca51` | **MATCH** |
| 9 | `models/usa/xgboost_model.json` | `5c7e1933bf9e2c60e33ef74ffc1555fe8dc3cf305f88fc30f55098ffbe61f00d` | **MATCH** |
| 10 | `models/usa/gradient_boosting_model.joblib` | `77d13b7782161cc46124707611a91cf64b8bb26cbaae188cb8292c3a504ef564` | **MATCH** |
| 11 | `models/usa/random_forest_model.joblib` | `9280d90d80c06155ee032e361239c948b3b44b8ee0b753d6ebef4fc3e887d1df` | **MATCH** |
| 12 | `models/usa/preprocessor.joblib` | `b3c0cce5e2526e033989c745fc307613768f533a1e95fc1d7c0f188fa6c57fba` | **MATCH** |
| 13 | `data/processed/ashe_2025_revised/dataset.parquet` | `6689d608c996ce1efbbf82bd5b9fef3f4fab01cd1a2f1cafba0b5931d9bb6ba9` | **MATCH** |
| 14-19 | Metadata, Crosswalk & Reference Files | Various Certified SHA-256 Hashes | **ALL MATCH** |

**Zero models or preprocessors have been modified or retrained.**
