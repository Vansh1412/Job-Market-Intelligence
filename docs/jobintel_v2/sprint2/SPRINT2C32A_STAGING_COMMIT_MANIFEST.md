# JOBINTEL 2.0 — SPRINT 2C.3.2A: STAGING COMMIT MANIFEST
**Milestone:** Phase F — Explicit Staging Commit Allowlist & Manifest  
**Execution Timestamp:** 2026-11-15T12:11:00+05:30  
**Evaluator Roles:** Senior Git/DevOps Engineer, Release Manager  
**Workspace:** `E:\Job Market` | **Branch:** `staging/sprint2c3`  

---

## 1. Executive Summary

This manifest specifies the explicit allowlist of individual files and verified directories approved for inclusion in the Sprint 2C.3.2A staging release commit (`feat(jobintel): prepare sprint 2 global foundation and governance for staging`).

In accordance with Phase F rules:
- `git add .` and `git add -A` were strictly forbidden and never used.
- Every path was staged individually and verified via `git diff --cached`.
- All binary models (`.pkl`), private datasets (`data/`, `*.parquet`), and temporary caches (`__pycache__/`, `.pytest_cache/`) are completely excluded.

---

## 2. Approved Commit Allowlist

### 2.1 Modified Tracked Source Files (7 Files)
```
requirements.txt
src/backend/main.py
src/backend/routers/india.py
src/backend/routers/predict.py
src/backend/routers/usa.py
src/india/modeling.py
src/run_phase5_experiments.py
```

### 2.2 Operational Configurations (1 File)
```
src/backend/config/revocation_manifest.json
```

### 2.3 Global Foundation & Catalog Modules (8 Files)
```
src/backend/data_catalog/__init__.py
src/backend/data_catalog/registry.py
src/backend/employers/__init__.py
src/backend/employers/registry.py
src/backend/markets/__init__.py
src/backend/markets/registry.py
src/backend/routers/v1.py
```

### 2.4 Governance Engine Subsystem (7 Files)
```
src/backend/governance/__init__.py
src/backend/governance/engine.py
src/backend/governance/lifecycle.py
src/backend/governance/revocation.py
src/backend/governance/schemas.py
src/backend/governance/service.py
src/backend/governance/training_governance.py
```

### 2.5 Data Schemas (7 Files)
```
src/backend/schemas/__init__.py
src/backend/schemas/data.py
src/backend/schemas/employer.py
src/backend/schemas/governance.py
src/backend/schemas/market.py
src/backend/schemas/salary.py
src/backend/schemas/uk_salary.py
```

### 2.6 UK Ingestion & Descriptive Salary Modules (7 Files)
```
src/backend/ingestion/__init__.py
src/backend/ingestion/__main__.py
src/backend/ingestion/ashe2025.py
src/backend/ingestion/contracts.py
src/backend/ingestion/runner.py
src/backend/routers/uk_salary.py
src/backend/services/uk_salary_service.py
```

### 2.7 Regression & Governance Test Suites (6 Files)
```
tests/test_ashe_ingestion.py
tests/test_global_foundation.py
tests/test_governance_engine.py
tests/test_uk_salary_api.py
tests/test_uk_salary_service.py
tests/uk_salary_fixtures.py
```

### 2.8 Documentation & Architecture Audits (`docs/jobintel_v2/`)
```
docs/jobintel_v2/m0/
docs/jobintel_v2/sprint1/
docs/jobintel_v2/sprint2/
```

---

## 3. Explicit Exclusion List (Never Staged)

- `.env`, `.env.*` (Protected by `.gitignore`)
- `data/` (All raw and processed private datasets)
- `*.parquet` (All parquet observations)
- `jobs-tier1-L-2026-08-01/` (Proprietary raw corpus)
- `models/**/*.pkl` (Frozen binary model files)
- `scratch/` (Temporary scripts and investigation artifacts)
- `frontend/dist/` (Client build output)
- `frontend/node_modules/` (Third-party client dependencies)
- `*__pycache__*` (Python bytecode)

---

## 4. Allowlist Manifest Verification

**STATUS: ALLOWLIST APPROVED FOR SELECTIVE STAGING**  
All files meet functional requirements and security criteria.
