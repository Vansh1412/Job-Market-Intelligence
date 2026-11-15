# M0 Deployment Audit

## Repository configuration — VERIFIED FROM CONFIGURATION

- Vercel root `vercel.json`: build command `cd frontend && npm install && npm run build`, output `frontend/dist`, SPA rewrite to `/index.html`.
- `frontend/vercel.json`: Vite framework, `npm run build`, output `dist`, catch-all rewrite, immutable one-year asset cache. This file duplicates the root Vercel configuration in frontend-relative terms; actual selected Vercel root is **NOT VERIFIED**.
- Render `render.yaml`: Python web service `jobintel-backend`, free plan, Oregon, branch `master`; build `pip install --upgrade pip && pip install -r requirements.txt`; start `uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT --workers 1`; health `/api/ready`; Python `3.11.9`; `JOBINTEL_ENV=production`; CORS list includes localhost and three Vercel hostnames.
- Backend `main.py` additionally includes defaults, merges `CORS_ORIGINS`, strips `*`, enables credentials and all methods/headers.
- Root frontend API default is relative `/api`; production frontend needs `VITE_API_BASE_URL` set to deployed backend origin if frontend and backend are separate domains. `.env.example` documents the variable but does not supply a production URL.
- Runtime dependencies are in unpinned-range `requirements.txt`; no Python lockfile or `pyproject.toml`. Frontend has `package-lock.json` but CI and Vercel configuration fallback to `npm install` in places rather than consistently requiring `npm ci`.

## Artifact/runtime strategy

`main.py` calls `sync_and_verify_artifacts(enforce_all=False)` at startup then initializes the registry. Docker image copies `src/`, `models/`, `reports/` and frontend build; Render’s render.yaml is a native Python service and does not use Dockerfile. Private data are ignored by Git, with code fallbacks/optional cohorts documented in the model registry. **NOT VERIFIED:** external R2/S3 credentials, bucket settings, Render env state, actual Vercel project root/env, live deployed artifact set, DNS/health, or current production runtime.

## Risks and drift

- `Dockerfile` uses `CORS_ORIGINS="*"`, but FastAPI startup filters wildcard out; this path should be evaluated separately if Docker is used.
- Legacy `docs/deployment/cloud-architecture.md` describes AWS ECS/S3, while newer free deployment docs and `render.yaml` describe Render/Vercel. Current config wins; docs are stale/drifted.
- README and current requirements reference broader Python range than Render’s 3.11.9 runtime. Host baseline used Python 3.13.9; CI config uses 3.11.
- No hardcoded `localhost` in the production API base default; localhost appears in development proxy, default CORS, sample config and docs. Root/repo URLs should be checked against live Vercel configuration before launch.
- Dependencies include research/notebook/scientific libraries in the single runtime requirements file. Which are truly needed by Render is not verified by deployment profiling.
- Repository contains model and report artifacts totaling several MB; image size and Render memory on this exact commit were not measured. Older deployment docs cite ~310 MB measured peak and 512 MB limit, but this is historical documentation, not current live verification.
