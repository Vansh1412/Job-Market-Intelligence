# SPRINT 3B.3.3.2: BASELINE AND SCOPE SPECIFICATION
## Critical Defect Remediation, Employer Resolver Hardening & Mathematical Reconciliation

**Sprint ID:** 3B.3.3.2  
**Target Branch:** `staging/sprint2c3`  
**Current Baseline Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`  
**Production Baseline Commit:** `198b79dcdff08a5be5f08847c4262d31a3ce261e`  
**Execution Type:** Controlled Corrective Implementation & Adversarial Verification  
**Auditor / Engineer:** Principal Backend Engineer, Senior Full-Stack Engineer, Data Governance Architect & Security Engineer  
**Date:** 2026-11-17  

---

## 1. Project Context & Preceding Audit Findings

This sprint directly succeeds:
1. **Sprint 3B.3.3 (Controlled Implementation):** Delivered initial transparency cards, point estimates, employer entity resolution, and occupational alignment indices.
2. **Sprint 3B.3.3.1 (Forensic Implementation Audit):** Issued verdict **`CONDITIONAL PASS — RELEASE BLOCKED`** due to two critical blocking defects:
   - **Finding SKL-01 (Skill Denominator Conflation):** `SkillsPage.tsx` displayed Python postings as `31,676 postings (Cohort N = 34,036)` alongside a `9.4%` prevalence badge. In reality, $34,036$ was the supervised salary modeling training set, whereas the $31,676$ count was observed from the $335,995$ general job posting corpus ($31,676 / 335,995 = 9.43\%$). Displaying $31,676$ out of $34,036$ implied a mathematically absurd $93.1\%$ prevalence.
   - **Finding RES-01 (Employer Resolver Security Vulnerability):** In `src/backend/employers/resolver.py`, statutory identifier matching used substring containment (`request.statutory_identifier.lower() in str(src.source_reference).lower()`) and immediately returned `AUTOMATICALLY_RESOLVED` without validating whether `candidate_name` contradicted the registered entity. This allowed subsidiary names (e.g. "Google India Private Limited") or arbitrary entities passing an SEC CIK to automatically resolve to the US parent, completely bypassing parent-subsidiary anti-collapsing governance. Furthermore, `statutory_authority` was ignored.

---

## 2. Git State & Working Tree Baseline

Before initiating any edits, the environment was verified:
- `git branch --show-current`: `staging/sprint2c3`
- `git rev-parse HEAD`: `d1a8b027d10031b3568a3141f639e2f40a49be18`
- `git rev-parse master`: `198b79dcdff08a5be5f08847c4262d31a3ce261e` (100% isolated and untouched)
- `git diff --check`: 0 whitespace errors
- Tracked modified files from Sprint 3B.3.3 preserved:
  - `frontend/src/pages/OccupationsPage.tsx`
  - `frontend/src/pages/PredictorPage.tsx`
  - `frontend/src/pages/SkillsPage.tsx`
  - `src/backend/routers/v1.py`
  - `src/backend/schemas/employer.py`
  - `src/backend/services/india_service.py`
  - `src/backend/services/usa_service.py`
- Untracked files preserved:
  - `src/backend/employers/resolver.py`
  - `tests/test_employer_resolver.py`
  - `frontend/src/__tests__/prediction_display.test.ts`
  - `docs/jobintel_v2/sprints/sprint_3b_3_3/` (10 files)
  - `docs/jobintel_v2/sprints/sprint_3b_3_3_1/` (10 files)

---

## 3. Work Package Scope & Targeted File Modifications

| Work Package ID | Priority | Description | Target Files |
| :--- | :--- | :--- | :--- |
| **WP-FIX-01** | **CRITICAL** | Skill Denominator Correction: Align numerator, denominator, and prevalence. Expose explicit population metadata in API. Update frontend to render verified observation corpus. Add mathematical integrity tests. | - `src/backend/routers/skills.py`<br>- `src/backend/services/india_service.py`<br>- `frontend/src/types.ts`<br>- `frontend/src/pages/SkillsPage.tsx`<br>- `tests/test_skill_denominator_integrity.py` |
| **WP-FIX-02** | **CRITICAL** | Employer Resolver Security Hardening: Implement structured exact statutory token parsing, authority validation, legal-entity contradiction checks, and conservative manual-review routing. Add 25+ adversarial tests. | - `src/backend/employers/resolver.py`<br>- `src/backend/schemas/employer.py`<br>- `src/backend/routers/v1.py`<br>- `tests/test_employer_resolver.py` |
| **WP-FIX-03** | **MODERATE** | USA Median Absolute Error Reconciliation: Forensically investigate $26,384.22 vs $26,775.59 divergence, document evaluation contract, preserve genuine metrics without altering model binaries. | - `docs/jobintel_v2/sprints/sprint_3b_3_3_2/06_salary_metric_reconciliation.md` |
| **WP-FIX-04** | **MODERATE** | Salary Interval API Contract Decision: Audit usage of legacy `confidence_interval` key, evaluate backward compatibility vs semantic correctness, document deprecation/migration plan without breaking external consumers. | - `docs/jobintel_v2/sprints/sprint_3b_3_3_2/07_salary_api_contract_decision.md` |
| **WP-FIX-05** | **MODERATE** | Pagination Architectural Assessment: Review default unbounded list on `GET /v1/employers`, document adequacy for current 28-employer cohort, and specify database migration requirements. | - `docs/jobintel_v2/sprints/sprint_3b_3_3_2/08_pagination_assessment.md` |
| **WP-FIX-06** | **CRITICAL** | Comprehensive Regression & Build Verification: Execute full backend suite (376+ tests), frontend suite (20+ tests), TypeScript build, Vite production bundle, golden prediction tests, and UK governance gate. | - Automated test runners |

---

## 4. Preservation & Safety Commitments

1. Zero machine learning model retraining or binary modification (`models/phase5/best_model.pkl`, `models/india/final_model.pkl` remain untouched).
2. Zero tampering with genuine evaluation metrics.
3. Zero bypasses of UK demand publication gating (`value: null`, `UK_DEMAND_DATA_NOT_PUBLISHED`).
4. Zero commits, zero pushes to remote, and zero deployments to Render or Vercel.
5. Production `master` remains completely isolated.
