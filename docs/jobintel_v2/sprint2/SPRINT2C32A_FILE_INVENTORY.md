# JOBINTEL 2.0 — SPRINT 2C.3.2A: COMPLETE FILE INVENTORY REPORT
**Milestone:** Phase B — Complete Change Inventory & Classification  
**Execution Timestamp:** 2026-11-15T12:07:00+05:30  
**Evaluator Roles:** Principal Software Architect, Senior Backend Engineer, Application Security Engineer  
**Workspace:** `E:\Job Market` | **Branch:** `staging/sprint2c3`  

---

## 1. Executive Summary

This report delivers the comprehensive change inventory and classification for every modified tracked file and untracked file considered for inclusion in the staging release commit.

Every path has been individually examined for functional purpose, architectural lineage, security posture, and deployment necessity. Zero files are staged based on directory name alone.

---

## 2. Modified Tracked Files Inventory (7 Files)

| File / Path | Classification | Purpose | Security Review | Commit Decision | Reason |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `requirements.txt` | Configuration | Adds `openpyxl>=3.1.0,<4.0.0` for offline ASHE XLSX parsing | **CLEAN** (Public pinned PyPI package) | **INCLUDE** | Mandatory for ASHE ingestion and test execution |
| `src/backend/main.py` | Source Code | Mounts `v1.router` and `uk_salary.router` natively at `/api` and `/` | **CLEAN** (Double-mounted routes, CORS intact) | **INCLUDE** | Core API entrypoint required for staging |
| `src/backend/routers/india.py` | Source Code | Adds `record_inference_governance(market="India")` audit call | **CLEAN** (Audit logging only, no credentials) | **INCLUDE** | Connects live India inference to governance |
| `src/backend/routers/predict.py` | Source Code | Adds `record_inference_governance(market="USA")` audit call | **CLEAN** (Audit logging only, no credentials) | **INCLUDE** | Connects legacy USA prediction route to governance |
| `src/backend/routers/usa.py` | Source Code | Adds `record_inference_governance(market="USA")` audit call | **CLEAN** (Audit logging only, no credentials) | **INCLUDE** | Connects dedicated USA prediction route to governance |
| `src/india/modeling.py` | Source Code | Adds `TrainingGovernanceGate` evaluation before training execution | **CLEAN** (Gate evaluation hook, no secrets) | **INCLUDE** | Enforces governance gate before training |
| `src/run_phase5_experiments.py`| Source Code | Adds `TrainingGovernanceGate` evaluation before USA ML execution | **CLEAN** (Gate evaluation hook, no secrets) | **INCLUDE** | Enforces governance gate before training |

---

## 3. Untracked Source & Implementation Files Inventory (10 Components)

| File / Path | Classification | Purpose | Security Review | Commit Decision | Reason |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `src/backend/config/revocation_manifest.json` | Configuration | Authoritative revocation registry configuration (schema v1.0.0) | **CLEAN** (Zero active revocations, public operational policy) | **INCLUDE** | Required by Gate 1 in GovernanceEngine |
| `src/backend/data_catalog/` | Source Code | Central data catalog registry and source metadata loaders | **CLEAN** (In-memory metadata registry, zero secrets) | **INCLUDE** | Required for `/api/v1/sources` and catalog governance |
| `src/backend/employers/` | Source Code | Employer profile intelligence foundation and registry | **CLEAN** (Read-only employer models, zero PII) | **INCLUDE** | Required for `/api/v1/employers` |
| `src/backend/governance/` | Source Code | Central governance engine, lifecycle, revocation, schemas | **CLEAN** (Strict policy evaluation, sanitized errors) | **INCLUDE** | Core Sprint 2C governance framework foundation |
| `src/backend/ingestion/` | Source Code | ASHE 2023–2025 offline ingestion pipeline and contracts | **CLEAN** (Deterministic parsing code, no raw data) | **INCLUDE** | Implements reproducible ASHE ingestion |
| `src/backend/markets/` | Source Code | Multi-market configuration registry (IN, US, UK) | **CLEAN** (Metadata configs, currency conventions) | **INCLUDE** | Required for `/api/v1/markets` endpoints |
| `src/backend/routers/uk_salary.py` | Source Code | 5 fail-closed UK descriptive salary endpoints | **CLEAN** (Enforces HTTP 503 `UK_DATA_NOT_PUBLISHED`) | **INCLUDE** | Mandatory for UK market fail-closed contract |
| `src/backend/routers/v1.py` | Source Code | Global intelligence foundation router (`/v1`) | **CLEAN** (Standard FastAPI router endpoints) | **INCLUDE** | Exposes global market/source/employer metadata |
| `src/backend/schemas/` | Source Code | Pydantic data, employer, governance, and market schemas | **CLEAN** (Type definitions and validators only) | **INCLUDE** | Type contracts used across all backend routers |
| `src/backend/services/uk_salary_service.py` | Source Code | UK salary analytical service and publication gate | **CLEAN** (Fail-closed gate, suppression math) | **INCLUDE** | Backend service logic for UK salary domain |

---

## 4. Untracked Test Suite Inventory (6 Modules)

| File / Path | Classification | Purpose | Security Review | Commit Decision | Reason |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `tests/test_ashe_ingestion.py` | Test Code | Tests for ASHE workbook parsing and determinism (22 tests) | **CLEAN** (Uses mock cells and synthetic fixtures) | **INCLUDE** | CI regression gate for UK data pipeline |
| `tests/test_global_foundation.py` | Test Code | Tests for multi-market catalog and observation models (24 tests) | **CLEAN** (Synthetic contract tests, no secrets) | **INCLUDE** | CI regression gate for Global Foundation |
| `tests/test_governance_engine.py` | Test Code | Comprehensive governance engine test suite (38 tests) | **CLEAN** (Covers all 20 Sprint 2C.1 requirements) | **INCLUDE** | CI regression gate for GovernanceEngine |
| `tests/test_uk_salary_api.py` | Test Code | Tests verifying 5 UK routes fail closed with HTTP 503 (35 tests) | **CLEAN** (Verifies zero salary observation leakage) | **INCLUDE** | CI regression gate for UK fail-closed safety |
| `tests/test_uk_salary_service.py` | Test Code | Unit tests for UK salary statistical calculations (28 tests) | **CLEAN** (Synthetic numerical tests) | **INCLUDE** | CI regression gate for UK analytical service |
| `tests/uk_salary_fixtures.py` | Test Code | Shared synthetic fixtures for UK salary testing | **CLEAN** (Synthetic test dictionaries only) | **INCLUDE** | Shared helper fixtures imported by test suites |

---

## 5. Untracked Documentation Inventory (`docs/jobintel_v2/`)

| File / Path | Classification | Purpose | Security Review | Commit Decision | Reason |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `docs/jobintel_v2/m0/` (18 files) | Documentation | M0 repository baseline, model artifact, and feature audits | **CLEAN** (Architecture specifications and audits) | **INCLUDE** | Immutable historical foundation audit records |
| `docs/jobintel_v2/sprint1/` (7 files) | Documentation | Sprint 1 API contracts, data dictionary, and test reports | **CLEAN** (Data engineering specifications) | **INCLUDE** | Sprint 1 architectural provenance records |
| `docs/jobintel_v2/sprint2/` (71 files) | Documentation | Sprint 2 governance, ASHE, staging, and audit reports | **CLEAN** (Technical and governance standards) | **INCLUDE** | Complete Sprint 2 authoritative audit ledger |

---

## 6. Inventory Summary & Staging Recommendations

- **Total Modified Tracked Files:** 7
- **Total Untracked Source / Test Files:** 16 (comprising 49 Python and JSON files across directories)
- **Total Documentation Files:** 96 Markdown documents
- **All Files Safe to Commit:** **YES**. Every file is free of secrets, credentials, binary pickles, and raw observation datasets.
