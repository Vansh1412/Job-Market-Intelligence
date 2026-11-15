# JOBINTEL 2.0 — SPRINT 2C.3: VERCEL STAGING FRONTEND REPORT
**Milestone:** Phase 6 — Vercel Staging Frontend Deployment & Build Qualification  
**Execution Date:** 2026-11-15T11:18:00+05:30  
**Evaluator Roles:** Senior Frontend Engineer, Release Manager  
**Workspace:** `e:\Job Market`  

---

## 1. Executive Summary

This report documents the staging frontend build qualification, artifact chunking, TypeScript verification, unit testing, and deployment readiness for Vercel preview environments.

The frontend SPA was compiled using TypeScript 6.0.2 and Vite 8.3.3 (`tsc -b && vite build`). All 2,891 modules were transformed without warnings or errors. Unit tests passed 100% (9/9 tests). Automated remote cloud deployment to Vercel is gated pending user authentication via `vercel login` or `VERCEL_TOKEN`.

---

## 2. Frontend Build Artifacts & Bundle Audit

Executed build command: `npm --prefix frontend run build`

```
vite v8.3.3 building client environment for production...
transforming...
✓ 2891 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                             1.49 kB │ gzip:   0.75 kB
dist/assets/index-ghKHOxN1.css              5.12 kB │ gzip:   1.78 kB
dist/assets/rolldown-runtime-hePW80VL.js    0.71 kB │ gzip:   0.42 kB
dist/assets/icons-EoReK5Au.js              18.87 kB │ gzip:   7.16 kB
dist/assets/vendor-DaDWtDB3.js            207.23 kB │ gzip:  64.96 kB
dist/assets/index-Cl3Cdlcm.js             276.91 kB │ gzip:  71.83 kB
dist/assets/recharts-DJoC-9V5.js          374.34 kB │ gzip: 107.64 kB
✓ built in 1m 8s
```

### 2.1 Chunking & Performance Analysis
- **Total Uncompressed Bundle:** 884.67 kB.
- **Total Gzipped Transfer Size:** 254.54 kB.
- **Vendor Splitting:** High-weight dependencies (`recharts`, `react`, `react-dom`, `lucide-react`) are isolated into independent cached chunks (`vendor`, `recharts`, `icons`), maximizing CDN cache hit ratios.
- **Long-term Cache Headers:** Configured via `frontend/vercel.json`:
  ```json
  {
    "source": "/assets/(.*)",
    "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
  }
  ```

---

## 3. Frontend Unit & Contract Test Suite

Executed command: `npm --prefix frontend test -- --run`

```
 RUN  v5.0.3 E:/Job Market/frontend

 ✓ src/__tests__/routing.test.ts (3 tests) 8ms
 ✓ src/__tests__/calculator.test.ts (3 tests) 12ms
 ✓ src/__tests__/skills_contract.test.ts (3 tests) 9ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Start at  11:06:50
   Duration  10.26s
```

| Test Suite | Tests | Result | Verification Scope |
| :--- | :--- | :--- | :--- |
| `routing.test.ts` | 3 | PASS | Verifies client-side route transitions and active tab highlighting |
| `calculator.test.ts` | 3 | PASS | Verifies client-side salary math and unit formatting |
| `skills_contract.test.ts` | 3 | PASS | Verifies 284 India skill tokens and 82 USA skill tokens contract |

---

## 4. API Client Staging Configuration

In `frontend/src/services/api.ts`:
```typescript
const envApiUrl = import.meta.env.VITE_API_BASE_URL;
const API_BASE = (typeof envApiUrl === 'string' && envApiUrl.trim() !== '')
  ? envApiUrl.trim().replace(/\/+$/, '')
  : '/api';
```
- In staging preview deployments, `VITE_API_BASE_URL` is set to `https://jobintel-backend-staging.onrender.com`.
- In local development or same-origin deployment, it defaults cleanly to `/api`.

---

## 5. Vercel Cloud Deployment Status & Blocker Disclosure

Executed probe: `npx vercel whoami`

```
Vercel CLI 65.16.0
> Logged out.
> Run `vercel deploy --temporary` to create a temporary deployment you can claim later, or `vercel login` to log in.
```

| Item | Requirement | Actual Status | Blocker Description |
| :--- | :--- | :--- | :--- |
| **Vercel Authentication** | Active session | **LOGGED OUT** | Vercel CLI is installed but not authenticated to an account |
| **Vercel Token** | `VERCEL_TOKEN` in env | **UNSET** | No non-interactive CI/CD deploy token provided |
| **Production Protection** | Keep `dusky` untouched | **PROTECTED** | Production alias `job-market-intelligence-dusky.vercel.app` is safe |

### 5.1 Remediation Steps for Remote Provisioning
To deploy the staging preview to Vercel:
1. Run `npx vercel login` in an interactive shell, OR
2. Supply `VERCEL_TOKEN` and execute `npx vercel deploy --build-env VITE_API_BASE_URL="https://jobintel-backend-staging.onrender.com"`.

---

## 6. Vercel Staging Qualification Verdict

**VERDICT: FRONTEND BUILD QUALIFIED — DEPLOYMENT READY**  
The frontend bundle is fully built, minified, tested, and ready for instantaneous deployment once Vercel credentials are authenticated.
