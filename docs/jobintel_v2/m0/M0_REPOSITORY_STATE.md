# M0 Repository State

## Git snapshot

**VERIFIED FROM GIT**, captured before documentation authoring:

| Item | Result |
|---|---|
| Working directory / repository root | `E:/Job Market` |
| Branch | `master` |
| HEAD | `198b79d` — `fix(routing): mount API routers natively at both /api and root prefixes` |
| Upstream | `origin/master` at `https://github.com/Vansh1412/Job-Market-Intelligence.git` |
| Recent commits | `198b79d`, `82685b6`, `f8f549a`, `a4d2e5f`, `5ad906f` |
| Start status | clean; no staged, modified, or untracked files |
| Tracked file count | 523 |
| Tracked checkout bytes | 58,222,955 (~55.5 MiB; filesystem size, not packed Git object size) |
| `.gitattributes` | absent |

No existing user changes required preservation at start. New files under `docs/jobintel_v2/m0/` are intentional audit deliverables. `git status --short --ignored` after validation showed ignored local datasets, `frontend/node_modules`, `frontend/dist`, `.pytest_cache`, and pre-existing ignored research outputs; they were not removed or changed by cleanup.

## Large files and artifacts

Largest tracked files include notebooks (`notebooks/05_salary_modeling.ipynb`, ~5.6 MB; `notebooks/04_archetype_discovery.ipynb`, ~1.8 MB) and model/artifact figures. Tracked model artifacts include `models/kmeans_phase4_k7.pkl` (~1.35 MB), `models/phase5/best_model.pkl` (~0.62 MB), and `models/india/final_model.pkl` (~0.55 MB). These are expected project artifacts, not accidental large data exports. Largest-files listing was from filesystem sizes of `git ls-files` paths.

## Private data and ignore rules

`git ls-files '*.parquet'` and `git ls-files 'data/'` returned no tracked files. `*.parquet`, `*.csv`, `data/raw/`, `data/processed/`, `jobs-tier1-L-2026-08-01/`, and `nextgig_jobs_2026-06.parquet` are ignored in `.gitignore`; selected aggregate CSV/JSON outputs under `reports/tables/` are explicitly unignored. **VERIFIED FROM GIT and `.gitignore`**.

Ignored workspace data includes raw public/third-party job posting files and derived India/USA processed Parquet cohorts (examples and metadata only are inventoried in `M0_DATA_PRIVACY_AND_QUALITY.md`). The local root `nextgig_jobs_2026-06.parquet` is ~39.8 MB and ignored. Ignored does not itself prove license compliance or privacy safety.

## Secret and binary screening

Tracked candidate-path screening found no private `.env`, key, certificate, or credential filenames; `.env.example` is the only tracked `.env`-pattern file. A heuristic tracked-text scan for common AWS/GitHub/Google key formats, private-key headers, and credential assignments found zero candidate files; it emitted no secret values. **VERIFIED BY EXECUTED HEURISTIC SCAN**; this is not a comprehensive secret-scanner guarantee. The repo contains expected model pickles, image outputs, notebooks, and screenshots. No unexpected tracked Parquet dataset was found.

## Actual configuration files found

- `.gitignore`, `.dockerignore`, `.env.example`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, root `vercel.json`, `render.yaml`
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/vercel.json`, Vite/TypeScript/Vitest/Oxlint configs
- `.github/workflows/ci.yml`, `docker-build-manual.yml`, `docker-release-gate.yml`
- `src/backend/config/artifact_manifest.json`
- No root `pyproject.toml`, `.gitattributes`, or root npm manifest/lockfile.

## Preservation and limits

At start the tracked and untracked working tree was clean. Validation generated ignored `frontend/dist` and `.pytest_cache`; no source or tracked build artifact changed. No reset, stash, checkout, cleanup, dependency install, commit, push, or deploy was performed.


## Largest tracked files (filesystem byte sizes)

| Relative path | Approx. size |
|---|---:|
| `notebooks/05_salary_modeling.ipynb` | 5.56 MB |
| `reports/figures/phase4_1/09_pca_cluster_scatter.png` | 2.14 MB |
| `notebooks/04_archetype_discovery.ipynb` | 1.83 MB |
| `notebooks/04_1_archetype_correction.ipynb` | 1.57 MB |
| `notebooks/03_eda.ipynb` | 1.54 MB |
| `models/kmeans_phase4_k7.pkl` | 1.35 MB |
| `reports/figures/phase4/08_pca_cluster_scatter.png` | 1.19 MB |
| `reports/figures/final_architecture.png` | 1.18 MB |
| `reports/figures/phase5/10_predicted_vs_actual.png` | 0.91 MB |
| `reports/figures/phase5/11_residual_vs_predicted.png` | 0.89 MB |
| `reports/figures/phase3/08_skill_cooccurrence_heatmap.png` | 0.83 MB |

These are notebooks, documented visualizations, and expected model assets; no large raw data export appears in the tracked list. The ~39.8 MB root Parquet and datasets under `data/` are ignored, not tracked.
