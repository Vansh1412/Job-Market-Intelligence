# JobIntel Phase 8.5: Data Governance and Data-Custody Specification

**Document ID:** `reports/PHASE8_5_DATA_GOVERNANCE.md`  
**Date:** October 8, 2026  
**Status:** ACTIVE REGULATORY POLICY (SSOT)  
**Author:** Antigravity Data Custodian & Security Engineering  
**Classification:** Internal Data Governance Protocol  

---

## 1. Executive Summary & Purpose

The JobIntel project utilizes machine learning models trained on proprietary tech job market posting datasets. This document defines the mandatory data governance, licensing compliance, and custody boundaries governing all continuous integration (CI), container builds, and release verification gates.

---

## 2. Why Proprietary Datasets Are Excluded from Git

1. **Licensing Restrictions (DataForge Tier 1 Agreement):**
   - The primary dataset package `jobs-tier1-L-2026-08-01` is licensed under the **DataForge Dataset License Agreement (Tier 1 — Internal Analytics)**, audited in [`reports/license_compliance.md`](file:///e:/Job%20Market/reports/license_compliance.md).
   - Section 4(b) explicitly prohibits the licensee to *"sell, rent, lease, publish, or otherwise make the Raw Data (in whole or in substantial part) available to any third party as a standalone dataset, API, or bulk download."*
   - Section 1.3 & 3.1 prohibit committing or uploading record-level data (`data/raw/` and `data/processed/*.parquet`) to public repositories.
2. **Git Version Control Safeguards:**
   - [`.gitignore`](file:///e:/Job%20Market/.gitignore) and [`.dockerignore`](file:///e:/Job%20Market/.dockerignore) enforce quarantine boundaries:
     ```gitignore
     data/raw/
     data/processed/
     *.parquet
     *.csv
     ```
   - Zero raw job postings or record-level Parquets are tracked in Git history.

---

## 3. Why Docker Cannot `COPY` Datasets from Public Checkout

1. **Clean Public Checkout Reality:**
   Public GitHub Actions runners (`ubuntu-latest`) execute within ephemeral cloud VMs initialized strictly from `git clone`. Because the Parquets are not tracked in Git, `data/processed/` does not exist on the runner.
2. **Build Failure Prevention:**
   A `COPY data/processed/ /app/data/processed/` instruction in [`Dockerfile`](file:///e:/Job%20Market/Dockerfile) fails when building from a public checkout.
3. **Image Layer Sanitization:**
   Baking proprietary Parquets into Docker image layers would create an exportable container image containing licensed data, violating license terms if the image were published.
4. **Resolution:**
   [`Dockerfile`](file:///e:/Job%20Market/Dockerfile) creates an empty mount directory:
   ```dockerfile
   RUN mkdir -p /app/data/processed/india
   ```
   The image builds purely from code, dependencies, compiled frontend assets, and model weights.

---

## 4. Runtime Read-Only Data Volume Mount Policy

To satisfy runtime data requirements without embedding data into the container image:

1. **Mount Syntax:**
   On the controlled machine hosting the protected data, the container is started with a read-only bind volume mount:
   ```bash
   docker run -d --name jobintel-app -p 8000:8000 \
     -v "E:/Job Market/data/processed:/app/data/processed:ro" \
     jobintel-phase8-3-certification
   ```
2. **Read-Only (`:ro`) Enforcement:**
   The `:ro` flag ensures that the running container process cannot write, modify, delete, or corrupt the frozen on-disk Parquets.
3. **Data Access Boundary:**
   Only the container running on the trusted host machine can access the files. The data never leaves the host.

---

## 5. Dual-Track Release Architecture: Public CI vs. Protected Release Gate

The repository operates on a strict separation of concerns:

| Boundary | Public CI (`ci.yml`) | Protected Release Gate (`docker-release-gate.yml`) |
|---|---|---|
| **Runner Environment** | GitHub-hosted `ubuntu-latest` | Self-hosted `[self-hosted, jobintel-private-data]` |
| **Trust Domain** | Public / Untrusted | Controlled / Trusted Local Machine |
| **Data Access** | **Zero proprietary data** | **Local frozen Parquet cohorts mounted `:ro`** |
| **Triggers** | `push` to master, `pull_request` | `workflow_dispatch` (manual) / `push` to master |
| **Test Scope** | Frontend build, Vitest (9/9), ESLint, Python compilation, code-only contract tests | 10/10 SHA-256 verification, Docker build, Docker runtime, `/api/ready`, prediction parity, full 87 backend tests |
| **Artifact Upload** | None | **Zero dataset uploads** |

---

## 6. Prohibition of Synthetic Fallbacks

Scientific integrity strictly forbids mocking or fabricating data:
- **No Synthetic Data Generation:** If the Parquet datasets are absent, the application or test MUST NOT generate synthetic rows to pass readiness.
- **Honest Readiness Probe:** [`/api/ready`](file:///e:/Job%20Market/src/backend/main.py#L112) queries [`ModelRegistry`](file:///e:/Job%20Market/src/backend/models/model_registry.py). If datasets are missing, it returns HTTP 503 (`registry_status: RED`, `artifacts_verified_count: 8/10`).
- **Absence = Blocked:** An environment without data is classified as `BLOCKED` or `PENDING VERIFICATION`, never falsely declared `READY`.

---

## 7. Cryptographic SHA-256 Verification Protocol

Before any release candidate can be certified, all 10 frozen artifacts must match bit-for-bit:

1. `models/india/final_model.pkl`: `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310`
2. `models/india/final_preprocessor.pkl`: `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead`
3. `data/processed/india/india_modeling_cohort.parquet`: `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec`
4. `models/india/india_pca_v1.pkl`: `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897`
5. `models/india/india_kmeans_v1.pkl`: `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a`
6. `models/phase5/best_model.pkl`: `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd`
7. `models/phase5/best_pipeline.pkl`: `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19`
8. `data/processed/modeling_dataset.parquet`: `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b`
9. `models/pca_phase4_1.pkl`: `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0`
10. `models/kmeans_phase4_1_k7.pkl`: `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106`

---

## 8. Data Custody Sign-Off

The data governance architecture guarantees that JobIntel satisfies 100% of its licensing obligations while maintaining an uncompromised verification pipeline.
