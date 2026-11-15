# JOBINTEL 2.0 — SPRINT 2C.3: STAGING ARCHITECTURE & ISOLATION REPORT
**Milestone:** Phase 1 & Phase 2 — Access Verification & Environment Isolation  
**Execution Date:** 2026-11-15T11:16:00+05:30  
**Evaluator Roles:** Principal DevOps Engineer, Application Security Engineer, Release Manager  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report specifies the staging topology, service identity specifications, environment isolation boundaries, and the results of the access and credential verification audit for Sprint 2C.3.

In strict compliance with Master Prompt Section 2.1 (*Production Isolation*), Section 4 (*Environment & Access Verification*), and Section 17 (*Strict Stop Conditions*):
- **Production web services remain 100% untouched.**
- **No production environment variables, domains, DNS records, or branches were altered.**
- **Account access was independently probed via shell CLIs and environment variables without hallucination.**

---

## 2. Infrastructure Identity & Separation Matrix

| Dimension | Production Environment (UNTOUCHED) | Staging Specification (TARGET) | Isolation Mechanism |
| :--- | :--- | :--- | :--- |
| **Backend Host** | Render Free Web Service | Render Free Web Service | Distinct service name & ID |
| **Backend Service Name** | `jobintel-backend` | `jobintel-backend-staging` | Independent blueprint entry |
| **Backend URL** | `https://job-market-intelligence-6ral.onrender.com` | `https://jobintel-backend-staging.onrender.com` | Unique FQDN subdomains |
| **Backend Health Probe** | `/api/ready` | `/api/ready` | Distinct network target |
| **Backend Env Flag** | `JOBINTEL_ENV=production` | `JOBINTEL_ENV=staging` | Strict runtime environment gate |
| **Frontend Host** | Vercel SPA | Vercel Preview / Project | Distinct deployment alias |
| **Frontend Project** | `job-market-intelligence` | `jobintel-staging` | Independent Vercel project/preview |
| **Frontend Production URL** | `https://job-market-intelligence-dusky.vercel.app` | `https://jobintel-staging.vercel.app` | Completely isolated production alias |
| **Frontend API Target** | Production Backend | Staging Backend (`VITE_API_BASE_URL`) | Build-time client configuration |
| **Git Deployment Branch** | `master` | `staging` / `release/sprint2c-staging` | Isolated branch; zero push to master |

---

## 3. Account & Credential Verification Audit (Phase 1)

In accordance with Phase 1 audit requirements, each hosting provider was checked for local CLI availability, authenticated sessions, and environment tokens:

### 3.1 Render Access Audit
- **CLI Presence:** Not found in environment (`Get-Command *render*` returned standard Anaconda binaries `conda-render.exe`, `mako-render.exe`, no Render CLI).
- **Environment Tokens:** Checked `env:*RENDER*`. Both `RENDER_API_KEY` and `RENDER_SERVICE_ID` are **UNSET** in the current shell.
- **Home Configuration:** No `~/.render` or `~/.config/render` directory exists.
- **Audit Finding:** Staging backend provisioning via automated Render API or CLI is **BLOCKED** due to missing Render API credentials.

### 3.2 Vercel Access Audit
- **CLI Presence:** Vercel CLI `v65.16.0` (native) successfully verified via `npx vercel --version`.
- **Authentication Status:** Executed `npx vercel whoami`. Output:
  ```
  Vercel CLI 65.16.0
  > Logged out.
  > Run `vercel deploy --temporary` to create a temporary deployment you can claim later, or `vercel login` to log in.
  ```
- **Configuration File:** `C:\Users\chopr\AppData\Roaming\com.vercel.cli\Data\config.json` verified with `"usedBefore": false` and zero auth tokens.
- **Audit Finding:** Staging frontend preview deployment via Vercel CLI is **BLOCKED** due to logged-out status.

### 3.3 GitHub Access & Branch Isolation Audit
- **CLI Presence:** `gh` CLI is not installed (`The term 'gh' is not recognized`).
- **Remote Configuration:** Remote origin points to `https://github.com/Vansh1412/Job-Market-Intelligence.git`.
- **Branch Topology:** Only `master` and `remotes/origin/master` exist.
- **Production Push Risk:** Existing `render.yaml` specifies `branch: master` for the live production service (`jobintel-backend`). Pushing unvetted staging commits directly to `master` would automatically trigger a production deployment on Render, violating Section 2.1 and Section 17.
- **Audit Finding:** Direct push to `master` is **PROHIBITED**. An isolated branch (`staging` or `release/sprint2c-staging`) must be created if remote cloud deployment is authorized by the user.

---

## 4. Environment Variables Specification for Staging

### 4.1 Staging Backend (`jobintel-backend-staging`)
```bash
# Core Runtime Configuration
JOBINTEL_ENV=staging
PYTHON_VERSION=3.11.9
PORT=8000
PYTHONPATH=/app

# Whitelisted CORS Origins (STRICT: NO WILDCARDS ALLOWED)
CORS_ORIGINS="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,https://jobintel-staging.vercel.app,https://job-market-intelligence-dusky.vercel.app"

# Governance & Verification
GOVERNANCE_REVOCATION_MANIFEST="src/backend/config/revocation_manifest.json"
```

### 4.2 Staging Frontend (`jobintel-staging`)
```bash
# Build-time Vite Configuration
VITE_API_BASE_URL="https://jobintel-backend-staging.onrender.com"
```

---

## 5. Environment Isolation Safety Verdict

**VERDICT: ISOLATION SPECIFIED — CLOUD PROVISIONING GATE CLOSED**  
The staging architecture is fully isolated and decoupled from production. Because Render and Vercel credentials are unset/logged out in the local execution environment, the automated deployment gate is correctly closed to prevent hallucinated deployments or accidental production interference.
