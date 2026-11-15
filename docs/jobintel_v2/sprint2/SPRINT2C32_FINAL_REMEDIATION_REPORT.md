# JOBINTEL 2.0 — SPRINT 2C.3.2 FINAL REMEDIATION & VERIFICATION REPORT
**Staging Artifact Integrity, Checksum Normalization, Model Registry Semantics, and Python Runtime Qualification**

---

## 1. Executive Verdict

```
EXECUTIVE VERDICT: PASS — STAGING INTEGRITY AND RUNTIME FULLY QUALIFIED
```

All reported staging discrepancies have been mathematically diagnosed, surgically remediated, regression-tested (305/305 tests passing), safely committed on `staging/sprint2c3`, pushed to GitHub remote `origin`, and verified live against the public staging backend at `https://jobintel-backend-staging.onrender.com`.

The production branch `master` remains 100% untouched at baseline commit `198b79d`.

---

## 2. Commit Hashes & Baseline Audit

| Parameter | Master Baseline | Pre-Remediation Staging | Post-Remediation Staging |
| :--- | :--- | :--- | :--- |
| **Branch** | `master` | `staging/sprint2c3` | `staging/sprint2c3` |
| **Commit SHA** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `4ad9209709861bed1261a09d4b578f1e75544f1b` | `3446949133177deeced161f7a286c293f1ea9f80` |
| **Commit Subject** | `fix(routing): mount API routers natively...` | `docs(jobintel): finalize sprint 2C.3.2A...` | `fix(staging): remediate artifact integrity, line endings, model registry logging, and python version` |
| **Remote Status** | `origin/master` (untouched) | — | `origin/staging/sprint2c3` (up to date) |
| **Working Tree** | Clean | Clean | Clean |

---

## 3. Exact Changed Files & Line-Level Diff Summary

Seven (7) files were added or modified in commit `3446949`:

1. **`.gitattributes` (NEW FILE, +29 lines):**
   - Configures `text=auto eol=lf` across all JSON, Python, and Markdown files.
   - Strictly marks `*.pkl`, `*.joblib`, `*.parquet`, and media as `binary` to prevent line-ending normalization.

2. **`.python-version` (NEW FILE, +1 line):**
   - Pins the Render native runtime buildpack to Python `3.11.9`.

3. **`requirements.txt` (MODIFIED, +1 / -1 lines):**
   - Line 12: Changed `xgboost>=2.0.0,<4.0.0` $\rightarrow$ `xgboost==3.2.0` (matching the version documented in `reports/reproducibility.md`).

4. **`src/backend/config/artifact_manifest.json` (MODIFIED, +6 / -6 lines):**
   - Updated the 6 text JSON artifact checksums from Windows CRLF values to authoritative Git/Linux LF SHA-256 values. Zero changes to model entries.

5. **`src/backend/utils/s3_sync.py` (MODIFIED, +31 / -2 lines):**
   - Implemented separate, granular reporting for `mandatory_models_status`, `metadata_status`, `optional_datasets_status`, and `sync_completeness`.
   - Retained overall `status: DEGRADED` when optional research datasets are unmounted.

6. **`src/backend/models/model_registry.py` (MODIFIED, +29 / -9 lines):**
   - Separated mandatory model verification count (9/9) from optional research cohort availability (0/1).
   - Added explicit fields `mandatory_verified_count`, `mandatory_total_count`, `optional_verified_count`, and `optional_total_count` to the status envelope.

7. **`src/backend/main.py` (MODIFIED, +13 / -5 lines):**
   - Updated startup lifespan logger to clearly report:
     `Model Registry Status: GREEN (Mandatory Models: 9/9 verified, Optional Cohorts: 0/1 mounted)`
     `Cloud Artifact Sync Report: Status DEGRADED (Mandatory: 9/9, Metadata: 6/6, Optional Cohorts: 0/4, Completeness: PARTIAL_MANDATORY_VERIFIED)`

---

## 4. Checksum Normalization: Before & After Proof

For each of the six affected JSON files, the raw Git object bytes (`git cat-file -p HEAD:<path>`) were analyzed. It was mathematically proven that the previous manifest hashes were the Windows CRLF (`\r\n`) representations, whereas the replacement hashes represent the canonical UNIX LF (`\n`) bytes stored in Git:

| Key | Path | Old Manifest Hash (Windows CRLF `\r\n`) | New Manifest Hash (Canonical LF `\n`) | Semantic JSON Change |
| :--- | :--- | :--- | :--- | :--- |
| `india_skill_analytics` | `reports/tables/india/india_skill_analytics.json` | `805e33aeca78dfa7ce0c6da2ec2b04654e91c053ccaffd9e2219ca0c9c0378c5` | `08875b53c5bb76766761c62177daa5c65423dde8c642ba127b210b291197825c` | None (Bitwise identical) |
| `india_final_feature_list` | `models/india/final_feature_list.json` | `710aebaca840d4300a1e5f513fbe4826310abad9aa99e0547e63c0aabbef610e` | `9085e3a0d95fc555e8b6bf4e31e4f86e1e97326ac51648164e723f9169b38d95` | None (Bitwise identical) |
| `india_final_model_metadata` | `models/india/final_model_metadata.json` | `3e2aed92bee6a939295ac0d07fe4701856d079ea6f279952cb71b26565af3cb3` | `077a4c291d76d9332affe63d089e06023b31376ea24b39171d2e63934f76219f` | None (Bitwise identical) |
| `india_archetype_metadata` | `models/india/india_archetype_metadata.json` | `e49c22b85111408d4e87e4a29cb1afc5e76d9ac0d97bbe3789cca9311a2f4cff` | `7d49f6a00c5018b1ab2d46dbbdb1648e09e1e4d785edfd599bc9b74b7d2abd99` | None (Bitwise identical) |
| `usa_feature_metadata` | `models/phase5/feature_metadata.json` | `6f436976d2004b8b97934c7866ca7b3769cb938147d6a4ef1eea3a439dea7a5b` | `c4b72be3d4f2bd6a64c132cf23a5b5f6133c7ad0ff9bbf3ea40a8260f011abdb` | None (Bitwise identical) |
| `usa_model_metrics` | `models/phase5/model_metrics.json` | `06f372ff9cfde71890f5ef2be9ecafeceea6bc50ef503f173ee13124301b52c3` | `9d777fa4bb663543d62776df48d547765e83ac4ca2f32d8b3ce38aec2945bc18` | None (Bitwise identical) |

---

## 5. Model Integrity & Dataset Availability Results

### A. Nine (9) Mandatory Models (100% Bitwise Match to Certified Hashes)

| Model Key | Path | Size | Certified SHA-256 Checksum | Integrity Status |
| :--- | :--- | :--- | :--- | :--- |
| `india_salary_model` | `models/india/final_model.pkl` | 549,969 B | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | **MATCH** |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | 10,527 B | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | **MATCH** |
| `india_pca` | `models/india/india_pca_v1.pkl` | 37,446 B | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | **MATCH** |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | 22,617 B | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | **MATCH** |
| `usa_salary_model` | `models/phase5/best_model.pkl` | 619,464 B | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | **MATCH** |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | 3,317 B | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | **MATCH** |
| `usa_scaler` | `models/scaler_phase4_1.pkl` | 1,161 B | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | **MATCH** |
| `usa_pca` | `models/pca_phase4_1.pkl` | 6,355 B | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | **MATCH** |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | 468,479 B | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | **MATCH** |

### B. Four (4) Optional Private Datasets (Preserved Excluded from Git)

| Dataset Key | Manifest Path | Required | Git Tracked | Status on Cloud Staging | Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `india_cohort` | `data/processed/india/...` | `False` | No | `UNMOUNTED_RESEARCH_COHORT` | Row-level proprietary survey; zero-storage policy |
| `usa_cohort` | `data/processed/...` | `False` | No | `UNMOUNTED_RESEARCH_COHORT` | Row-level tech postings; zero-storage policy |
| `skill_matrix_technical` | `data/processed/...` | `False` | No | `UNMOUNTED_RESEARCH_COHORT` | Co-occurrence matrix; zero-storage policy |
| `job_archetype_assignments` | `data/processed/...` | `False` | No | `UNMOUNTED_RESEARCH_COHORT` | Archetype row assignments; zero-storage policy |

---

## 6. Separate Status Semantics Verification

The application now strictly separates and independently computes:

1. **Model Registry Readiness (`get_status_report()`):**
   - `status`: `"GREEN"` (computed strictly from `mandatory_verified_count == 9`)
   - `mandatory_verified_count`: `9`
   - `mandatory_total_count`: `9`
   - `optional_verified_count`: `0` (on cloud)
   - `optional_total_count`: `1`

2. **Artifact Synchronization Completeness (`sync_and_verify_artifacts()`):**
   - `status`: `"DEGRADED"` (accurately reflects that unmounted optional datasets are absent)
   - `mandatory_models_status`: `"VERIFIED_LOCAL"` (`9/9`)
   - `metadata_status`: `"VERIFIED_LOCAL"` (`6/6`)
   - `optional_datasets_status`: `"ALL_UNMOUNTED"` (`0/4`)
   - `sync_completeness`: `"PARTIAL_MANDATORY_VERIFIED"`

---

## 7. Python Runtime & XGBoost Compatibility

- **Python Runtime Selection:**
  - Pinning via `.python-version` containing `3.11.9` ensures Render's native buildpack targets Python 3.11.9.
- **XGBoost Version Pinning:**
  - Confirmed `models/phase5/best_model.pkl` booster config metadata specifies `version: [3, 2, 0]`.
  - Pinned `xgboost==3.2.0` in `requirements.txt`.
  - Zero serialization warnings emitted during model loading.
  - USA golden prediction parity confirmed: predicts `$244,423.42` for senior AI engineer profile, matching frozen benchmarks bitwise.

---

## 8. Full Regression Test Execution (305 / 305 Passing)

- **Specialized Domain Test Suites:** 144/144 passed in 20.06s
  - `tests/test_governance_engine.py`: 36 passed
  - `tests/test_uk_salary_api.py`: 16 passed
  - `tests/test_ashe_ingestion.py`: 10 passed
  - `tests/test_global_foundation.py`: 26 passed
  - `tests/test_cloud_contracts.py`: 26 passed
  - `tests/test_golden_predictions.py`: 20 passed
  - `tests/test_zero_storage_deployment.py`: 10 passed
- **Full Backend Pytest Suite:** 296/296 passed in 26.98s
- **Full Frontend Vitest Suite:** 9/9 passed in 1.18s
- **Total:** 305/305 tests passing (100% green).

---

## 9. Live Staging Remote Verification Evidence

Validated via direct HTTP calls to `https://jobintel-backend-staging.onrender.com`:

```text
================================================================================
JOBINTEL 2.0 LIVE STAGING REMOTE VERIFICATION SUITE
Target: https://jobintel-backend-staging.onrender.com
================================================================================

[TEST 1] /health & Model Registry Reporting:
HTTP Status: 200
Overall Service Status: healthy
Registry Status: GREEN
Mandatory Models Verified: 9 / 9
Optional Cohorts Mounted: 0 / 1
PASS: Registry explicitly distinguishes 9/9 mandatory models and 0/1 unmounted cohorts.

[TEST 2] /api/ready:
HTTP Status: 200
Ready: True
Status: ready
Artifacts Verified Count: 9
Markets: ['USA', 'India']
PASS: /api/ready responds HTTP 200 ready=True.

[TEST 3] UK Salary Fail-Closed Governance Protection (5 endpoints):
  /api/v1/markets/UK/salary/metadata -> HTTP 503 | Code: UK_DATA_NOT_PUBLISHED | Msg: UK salary analytics are not currently published.
  /api/v1/markets/UK/salary/occupations -> HTTP 503 | Code: UK_DATA_NOT_PUBLISHED | Msg: UK salary analytics are not currently published.
  /api/v1/markets/UK/salary/occupations/1001 -> HTTP 503 | Code: UK_DATA_NOT_PUBLISHED | Msg: UK salary analytics are not currently published.
  /api/v1/markets/UK/salary/occupations/1001/regions -> HTTP 503 | Code: UK_DATA_NOT_PUBLISHED | Msg: UK salary analytics are not currently published.
  /api/v1/markets/UK/salary/regions/UKC/occupations -> HTTP 503 | Code: UK_DATA_NOT_PUBLISHED | Msg: UK salary analytics are not currently published.
PASS: All 5 UK endpoints strictly return HTTP 503 UK_DATA_NOT_PUBLISHED.

[TEST 4] USA Live Prediction (/api/usa/predict):
HTTP Status: 200
Country: USA
Currency: USD
Predicted Salary: $244,423.42
Archetype: Systems & Core Backend Engineering (SYS_ENG)
PASS: USA prediction executes successfully with USD output.

[TEST 5] India Live Prediction (/api/india/predict):
HTTP Status: 200
Country: India
Currency: INR
Predicted Salary LPA: 12.76 Lakhs/year
Predicted Salary INR: ₹1,275,646
Archetype: Big Data Engineering & Distributed Systems
PASS: India prediction executes successfully with INR LPA output.

[TEST 6] Foundation Endpoints (/api/v1/markets, /api/v1/sources, /api/v1/employers):
  /api/v1/markets: HTTP 200, count: 5 markets (US, IN, UK, EU, CA)
  /api/v1/sources: HTTP 200, count: 11 data sources
  /api/v1/employers: HTTP 200, count: 0 (schema present, zero records populated)
PASS: Foundation endpoints respond normally without regression.
```

---

## 10. Production Isolation Guarantee

1. **`master` Branch:** 100% untouched at commit `198b79dcdff08a5be5f08847c4262d31a3ce261e`.
2. **Production Render Service (`job-market-intelligence-6ral.onrender.com`):** Configured with `branch: master` in `render.yaml`. Pushing `staging/sprint2c3` cannot affect production Render.
3. **Production Vercel Service (`job-market-intelligence-dusky.vercel.app`):** Connected strictly to `master`. Pushing `staging/sprint2c3` cannot trigger production Vercel.
4. **GitHub Actions CI:** Triggers strictly on `[main, master]`. Zero workflow collisions.

---

## 11. Remaining Limitations & Unresolved Risks

1. **UK ASHE Data Publication:** Remains fail-closed with HTTP 503 `UK_DATA_NOT_PUBLISHED` by design, as legal reuse approval is pending.
2. **Private Row-Level Datasets:** Remain unmounted in cloud staging under zero-storage data compliance policy.
3. **Render Free Tier Cold-Starts:** Free instance sleeps after 15 minutes of inactivity; initial wakeup latency can be 30–50 seconds.
