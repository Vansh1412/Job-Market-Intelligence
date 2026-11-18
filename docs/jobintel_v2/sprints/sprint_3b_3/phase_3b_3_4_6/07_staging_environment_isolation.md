# SPRINT 3B.3.3.4.6 — STAGING ENVIRONMENT ISOLATION & FAIL-CLOSED BOUNDARIES
**Sprint:** 3B.3.3.4.6  
**Document:** `07_staging_environment_isolation.md`  
**Date:** 2026-11-18  
**Author:** Principal Security Engineer & Infrastructure Architect  
**Status:** COMPLETE & VERIFIED  

---

## 1. Architectural Environment Segregation

JOBINTEL 2.0 enforces strict cryptographic, operational, and network separation between staging and production tiers:

| Dimension | Staging Environment | Production Environment | Isolation Mechanism |
| :--- | :--- | :--- | :--- |
| **Git Branch** | `staging/sprint2c3` | `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`) | Git branch protection; no automated merges |
| **Backend Service** | `https://jobintel-backend-staging.onrender.com` | `https://job-market-intelligence-6ral.onrender.com` | Distinct Render services, separate build triggers |
| **Frontend Service** | `https://jobintel-staging.vercel.app` | `https://job-market-intelligence-dusky.vercel.app` | Distinct Vercel projects (`jobintel-staging`) |
| **Runtime Env Flag** | `JOBINTEL_ENV="staging"` | `JOBINTEL_ENV="production"` or unset | Environment variable gating in container config |
| **Seed Ingestion** | Enabled for 5 audited candidates | Strictly blocked by fail-closed guardrails | Ingestion CLI enforcement & registry dispatch |

---

## 2. Fail-Closed Guardrails in Ingestion Pipeline

The ingestion runner in [src/backend/ingestion/employers_pilot.py](file:///e:/Job%20Market/src/backend/ingestion/employers_pilot.py) strictly refuses execution when targeted at production:

```python
if env == "production":
    logger.error("INGESTION BLOCKED: Automated seed ingestion into PRODUCTION is strictly prohibited.")
    return {
        "status": "FAILED",
        "reason": "Production ingestion prohibited by governance guardrails."
    }
```
CLI invocations targeting `--env production` terminate immediately with `sys.exit(1)`.

---

## 3. Runtime Gating in Backend Registry Singleton

The backend registry initialization logic in [src/backend/employers/registry.py](file:///e:/Job%20Market/src/backend/employers/registry.py) guarantees that the staging seed is only loaded when `JOBINTEL_ENV == "staging"`:

```python
def load_registry_for_environment(env: Optional[str] = None) -> EmployerRegistry:
    target_env = (env or os.getenv("JOBINTEL_ENV", "development")).strip().lower()
    if target_env == "staging":
        if DEFAULT_SEED_PATH.exists():
            profiles = load_staging_seed(DEFAULT_SEED_PATH, DEFAULT_MANIFEST_PATH)
            return EmployerRegistry(profiles)
    return EmployerRegistry([])
```

### Protection Against Unintended Production Exposure:
If the repository codebase (containing `staging_employers.json`) is ever inspected or referenced by a production container, the production container does **NOT** have `JOBINTEL_ENV="staging"`. As a result, the production registry defaults to an empty list `[]`, completely preventing inadvertent publication of staging pilot records to production users.
