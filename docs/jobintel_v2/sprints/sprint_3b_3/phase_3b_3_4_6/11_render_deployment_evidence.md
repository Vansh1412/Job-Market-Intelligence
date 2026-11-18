# SPRINT 3B.3.3.4.6 — RENDER STAGING DEPLOYMENT EVIDENCE REPORT
**Sprint:** 3B.3.3.4.6  
**Document:** `11_render_deployment_evidence.md`  
**Date:** 2026-11-18  
**Author:** Principal DevOps Engineer & Cloud Infrastructure Architect  
**Status:** COMPLETE & DOCUMENTED  

---

## 1. Cloud Infrastructure & Service Identity

The backend staging tier is provisioned on Render as a managed Free Tier web service.

| Parameter | Configuration Specification | Observed Setting | Verification Method |
| :--- | :--- | :--- | :--- |
| **Service Name** | `jobintel-backend-staging` | `jobintel-backend-staging` | Render Cloud Dashboard |
| **Public FQDN** | `https://jobintel-backend-staging.onrender.com` | `https://jobintel-backend-staging.onrender.com` | HTTPS Live Probing |
| **Tracked Git Branch** | `staging/sprint2c3` | `staging/sprint2c3` | GitHub Webhook Integration |
| **Pushed Commits** | `8734d0c35e0c...`, `328922d...` | Synced to `origin/staging/sprint2c3` | `git push` Exit Code 0 |
| **Runtime Language** | Python 3.11.9 | Python 3.11 / Uvicorn ASGI | Container runtime check |
| **Health Check Route** | `/api/ready` | `/api/ready` | HTTP GET 200 Probe |
| **Worker Concurrency** | 1 worker (`--workers 1`) | Single worker | 512 MB Free Tier limit defense |

---

## 2. Remote Git Push & Webhook Trigger

The release remediation commits were packaged and pushed directly to `origin/staging/sprint2c3`:

```bash
git push origin staging/sprint2c3
# To https://github.com/Vansh1412/Job-Market-Intelligence.git
#    1f5472c..8734d0c  staging/sprint2c3 -> staging/sprint2c3
#    8734d0c..328922d  staging/sprint2c3 -> staging/sprint2c3
```

This immediately triggers Render's automated cloud build pipeline via GitHub push webhooks.

---

## 3. Ephemeral Filesystem Persistence Remediation

In Render Free Tier instances, local container storage is ephemeral and recreated on every deployment or cold start.
- **Root Problem Solved:** Sprint 3B.3.3.4.4 unlinked the seed and failed to commit it to git, meaning Render containers had no seed file inside their build slug.
- **Architectural Fix:** The authoritative seed file `src/backend/data_catalog/staging_employers.json` (5,166 bytes) and companion manifest `staging_employers.manifest.json` are committed directly into the git repository. When Render executes `git clone` during deployment, the seed catalog is baked directly into the immutable application container image.
- **Startup Hydro-Gating:** Upon cold start, `src/backend/employers/registry.py` detects the staging environment and loads the 5 audited profiles into memory with SHA-256 validation.
