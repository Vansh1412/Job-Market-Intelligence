# JOBINTEL 2.0 — SPRINT 3B.2.3.2
# PHASE 9 & 10 — PROPOSED STAGING RELEASE MANIFEST & RISK REGISTER

**Sprint:** 3B.2.3.2 — Final Diff Review & Controlled Staging Commit Preparation  
**Date:** 2026-11-16  
**Auditor:** Principal Software Architect & Senior Git Release Engineer  

---

## 1. Proposed Release Manifest

This manifest categorizes every file in the repository into its strict staging release disposition.

### 1.1 Category A: REQUIRED FOR STAGING RELEASE (17 Implementation Files)
These files represent the core executable implementation, data schemas, datasets, and automated test coverage for Global Job Demand Intelligence:

```text
# Backend Core, Routing & Schemas
src/backend/main.py
src/backend/routers/demand.py
src/backend/schemas/demand.py
src/backend/services/demand_service.py

# Demand Datasets & Source Registries
src/backend/data/demand/metrics.json
src/backend/data/demand/sources.json
src/backend/data/demand/observations.json
src/backend/data/demand/shortage_indicators.json
src/backend/data/demand/skill_demands.json

# Frontend Core, Routing, Types & UI
frontend/src/App.tsx
frontend/src/components/AppHeader.tsx
frontend/src/services/api.ts
frontend/src/types.ts
frontend/src/pages/DemandPage.tsx

# Automated Unit & Contract Test Suites
frontend/src/__tests__/routing.test.ts
frontend/src/__tests__/demand_contract.test.ts
tests/test_demand_intelligence.py
```

### 1.2 Category B: DOCUMENTATION ONLY (Audit & Architecture Reports)
These files provide end-to-end auditability and evidence for the Sprint 3B.1.3 through Sprint 3B.2.3.2 sequence:

```text
# Sprint 3B.1 Verification & Browser Closure Reports
docs/jobintel_v2/sprint3/SPRINT3B1_3_INDEPENDENT_CLOSURE_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B1_4_CONTROLLED_STAGING_VERIFICATION.md
docs/jobintel_v2/sprint3/SPRINT3B1_5_DEPLOYMENT_IDENTITY_AND_BROWSER_CLOSURE.md
docs/jobintel_v2/sprint3/sprint3b1_6/SPRINT3B1_6_DEPLOYMENT_AUDIT.md

# Sprint 3B.2 Core Architecture & Methodology Reports
docs/jobintel_v2/sprint3/SPRINT3B2_API_CONTRACTS.md
docs/jobintel_v2/sprint3/SPRINT3B2_DATA_DICTIONARY.md
docs/jobintel_v2/sprint3/SPRINT3B2_FINAL_REPORT.md
docs/jobintel_v2/sprint3/SPRINT3B2_INGESTION_ARCHITECTURE.md
docs/jobintel_v2/sprint3/SPRINT3B2_LIMITATIONS.md
docs/jobintel_v2/sprint3/SPRINT3B2_METRIC_METHODOLOGY.md
docs/jobintel_v2/sprint3/SPRINT3B2_PHASE0_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_SOURCE_RESEARCH.md
docs/jobintel_v2/sprint3/SPRINT3B2_TEST_REPORT.md

# Sprint 3B.2.1 Independent Provenance Audit Reports
docs/jobintel_v2/sprint3/SPRINT3B2_1_COMPARABILITY_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_DATA_INVENTORY.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_INGESTION_SCRIPT_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_MARKET_VALIDATION.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_RECORD_PROVENANCE_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_RELEASE_READINESS.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_SKILL_GAP_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_1_TEST_RECONCILIATION.md

# Sprint 3B.2.2 Disclosure Hardening Reports
docs/jobintel_v2/sprint3/SPRINT3B2_2_FINAL_REPORT.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_INDIA_BENCHMARK_DISCLOSURE.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_PHASE0_BASELINE.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_PROVENANCE_DISCLOSURES.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_REGIONAL_ESTIMATE_DISCLOSURES.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_SKILL_GAP_METHODOLOGY.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_TEST_RECONCILIATION.md
docs/jobintel_v2/sprint3/SPRINT3B2_2_UK_SOURCE_PERMISSION_REVIEW.md

# Sprint 3B.2.3 Independent Closure Audit Reports
docs/jobintel_v2/sprint3/SPRINT3B2_3_API_FRONTEND_CONSISTENCY.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_BASELINE_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_FINAL_REPORT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_INDIA_BENCHMARK_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_PROVENANCE_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_REGIONAL_DISCLOSURE_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_REGRESSION_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_RELEASE_ISOLATION_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_SKILL_GAP_AUDIT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_UK_PUBLICATION_GATE_AUDIT.md

# Sprint 3B.2.3.1 UK Serialization Remediation Reports
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_BASELINE.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_API_SEMANTICS.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_UK_GATE_TESTS.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_FRONTEND_VERIFICATION.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_REGRESSION_REPORT.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_1_FINAL_REPORT.md

# Sprint 3B.2.3.2 Final Diff & Commit Preparation Reports
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_BASELINE.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_CHANGE_INVENTORY.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_BACKEND_REVIEW.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_FRONTEND_REVIEW.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_DATA_AND_MODEL_INTEGRITY.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_TEST_VERIFICATION.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_RELEASE_MANIFEST.md
docs/jobintel_v2/sprint3/SPRINT3B2_3_2_FINAL_REPORT.md
```

### 1.3 Category C: EXCLUDE FROM COMMIT (Strict Exclusions)
```text
scratch/* (all temporary scripts, test runners, parquet caches, logs)
.env, .env.local, .env.* (no secrets or environment overrides)
*.png, *.jpg, *.svg screenshots captured locally
Antigravity brain artifacts (stored in local user profile outside repo)
```

---

## 2. Proposed Commit Architecture & Messages

### Option 1 (Recommended): Two-Commit Staged Structure
Clean separation of implementation and documentation preserves git log clarity and granular revert capability:

#### Commit 1: Implementation & Tests
```git
feat(demand): implement global job demand intelligence, provenance disclosures, and UK publication gate (Sprint 3B.2)

- Ingest multi-market occupational demand observations for US, AU, UK, SG, and IN
- Implement 11-dimension cross-market demand comparability engine
- Implement skill gap analysis engine with transparent weighting formula
- Enforce fail-closed UK publication gate for Textkernel data (sanitized to null)
- Integrate qualitative shortage intelligence under Open Government Licence v3.0
- Add full frontend Demand Intelligence explorer with responsive disclosures
- Pass 38 demand unit/contract tests and 371 full-suite regression tests
```
*Files included:* All 17 files from Category A.

#### Commit 2: Audit & Architecture Documentation
```git
docs(sprint3): record sprint 3B.2 series audit, governance, remediation, and release qualification reports

- Record Sprint 3B.2 architectural definitions and metric methodologies
- Record Sprint 3B.2.1 independent provenance audit
- Record Sprint 3B.2.2 disclosure hardening and licensing review
- Record Sprint 3B.2.3 independent closure audit
- Record Sprint 3B.2.3.1 UK publication state serialization remediation
- Record Sprint 3B.2.3.2 final diff review and release qualification manifest
```
*Files included:* All Markdown reports from Category B under `docs/jobintel_v2/sprint3/`.

---

### Option 2: Consolidated Staging Release Commit
If a single atomic commit is preferred for staging:
```git
feat(demand): implement global job demand intelligence, provenance disclosures, UK gate, and documentation (Sprint 3B.2)
```
*Files included:* All files from Category A and Category B.

---

## 3. Rollback Runbook

If any regression is detected on staging post-commit:
1. **Local Revert:**
   ```bash
   git revert --no-edit HEAD
   ```
2. **Clean Working Tree Reset (if uncommitted):**
   ```bash
   git checkout -- frontend/src/ src/backend/main.py
   git clean -fd src/backend/data/demand/ src/backend/routers/ src/backend/schemas/ src/backend/services/ frontend/src/pages/ frontend/src/__tests__/demand_contract.test.ts tests/test_demand_intelligence.py
   ```
3. **Deployment Rollback:**
   - Vercel Staging: Re-alias `jobintel-staging.vercel.app` to previous stable deployment.
   - Render Staging: Trigger manual deploy of commit `58974134e56b4c3ec6b6119b7b4739e9cce857f3`.

---

## 4. Release Risk Register

| Risk Event | Severity | Baseline Evidence | Mitigation Applied | Release Blocker? |
| :--- | :---: | :--- | :--- | :---: |
| **UK Numeric Data Leakage** | Critical | Endpoint tests assert `value: null` and empty series | Pydantic schema nullable `float \| None`, service-layer sanitization | **NO (Remediated & Verified)** |
| **Withheld Data Treated as Zero** | High | Vitest & Pytest semantic tests | Withheld values serialize as JSON `null`; UI displays `'WITHHELD PENDING REVIEW'` | **NO (Remediated & Verified)** |
| **Model Weight / Inference Drift** | Critical | 19/19 SHA-256 hashes match SSOT; 30 parity tests pass | Zero model re-serialization; models frozen | **NO (Verified Invariant)** |
| **Production Target Contamination** | Critical | Git branch `staging/sprint2c3` verified; master SHA checked | All work strictly bounded to staging branch; master untouched | **NO (Verified Isolated)** |
| **Private Data / Secret Leakage** | Critical | Git status & filesystem inspection | `.env` files absent; raw parquet excluded by `.gitignore` | **NO (Verified Clean)** |
| **Unresolved Commercial License** | High | Source registry status `REVIEW_REQUIRED` | Fail-closed publication gate active; qualitative shortage runs on OGL v3.0 | **NO (Safely Gated)** |
| **Deployment Identity Unknown** | Medium | Render free-tier unverified SHA | Requires manual deployment SHA verification upon user authorization | **NO (Documented Limitation)** |
