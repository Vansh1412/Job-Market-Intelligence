# JOBINTEL 2.0 — SPRINT 3B.3.2
# DELIVERABLE 1: PREFLIGHT AND REPOSITORY BASELINE REPORT
## Verification of Git Baseline, Code Isolation, Existing Schemas & Governance Architecture

**Document Version:** 1.0.0  
**Phase:** Sprint 3B.3.2 (Five-Market Data Acquisition Pilot)  
**Audit Date:** November 2026  
**Auditor:** Principal Data Architect & Quality Assurance Lead  
**Execution Type:** Strictly Read-Only Empirical Pilot  
**Target Baseline:** `staging/sprint2c3` (`d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)

---

## 1. GIT REPOSITORY PREFLIGHT EXECUTION

Prior to executing any empirical data collection or analysis for Sprint 3B.3.2, the repository state was independently inspected and validated via direct Git commands:

```bash
$ git status --short
?? docs/jobintel_v2/sprint3/SPRINT3B2_3_3_FINAL_REPORT.md
?? docs/jobintel_v2/sprint3/SPRINT3B2_3_4_API_AND_DATA_CONTRACT_AUDIT.md
?? docs/jobintel_v2/sprint3/SPRINT3B2_3_4_BASELINE.md
...
?? docs/jobintel_v2/sprints/
?? node_modules/

$ git branch --show-current
staging/sprint2c3

$ git rev-parse HEAD
d1a8b027d10031b3568a3141f639e2f40a49be18

$ git rev-parse origin/staging/sprint2c3
d1a8b027d10031b3568a3141f639e2f40a49be18

$ git rev-parse master
198b79dcdff08a5be5f08847c4262d31a3ce261e
```

### 1.1 Baseline Validation Findings
| Dimension | Expected Baseline | Actual Verified State | Audit Result |
| :--- | :--- | :--- | :---: |
| **Working Branch** | `staging/sprint2c3` | `staging/sprint2c3` | **PASS** |
| **Local Staging HEAD** | `d1a8b027d10031b3568a3141f639e2f40a49be18` | `d1a8b027d10031b3568a3141f639e2f40a49be18` | **PASS** |
| **Remote Staging HEAD** | `d1a8b027d10031b3568a3141f639e2f40a49be18` | `d1a8b027d10031b3568a3141f639e2f40a49be18` | **PASS** |
| **Production Master HEAD** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | **PASS** |
| **Tracked File Changes** | `0 modified files` | `0 modified files` (Clean working tree) | **PASS** |
| **Untracked Directories** | Documentation & scratch only | `docs/jobintel_v2/sprints/` | **PASS** |

**Conclusion:** The repository is verified clean, synchronized with remote staging, and completely isolated from production `master`.

---

## 2. EXISTING EMPLOYER SUB-SYSTEM AUDIT

An architectural audit of existing employer modules in `src/backend/` reveals the following baseline:

### 2.1 Existing Pydantic Schemas (`src/backend/schemas/employer.py`)
- Defines frozen Pydantic v2 models:
  - `EmployerCategory`: `INDIAN_HEADQUARTERED`, `MULTINATIONAL_OPERATING_IN_INDIA`, `OTHER_INTERNATIONAL`.
  - `EmployerVerificationStatus`: `UNVERIFIED`, `REVIEW_REQUIRED`, `VERIFIED`.
  - `EmployerLocationType`: `HEADQUARTERS`, `OFFICE`, `RESEARCH`, `OTHER`.
  - `EmployerSourceReference`: Source name, organization, URL, timezone-aware timestamp.
  - `EmployerLocation`: City, state/region, country code, location type, verification status, verification source.
  - `EmployerProfile`: `company_id`, `company_name`, `headquarters_country`, `company_category`, `industry`, `official_website`, `operating_markets`, `source_references`, `locations`.
- **Preflight Observation:** The existing schemas were tailored to India and multinational operations. The Phase 0/3B.3.1 data model design generalizes this for global multi-market entities without breaking backward compatibility.

### 2.2 Existing In-Memory Registry (`src/backend/employers/registry.py`)
- Implements `EmployerRegistry` class managing immutable profiles.
- Exposes `get_employers() -> list[EmployerProfile]` and `get_employer(company_id: str) -> EmployerProfile`.

### 2.3 Existing API Router (`src/backend/routers/v1.py`)
- Mounts legacy endpoints:
  - `GET /v1/employers`
  - `GET /v1/employers/{company_id}`
- Exposes existing markets (`/v1/markets`) and sources (`/v1/sources`).

---

## 3. EXISTING OCCUPATION & DEMAND FOUNDATION

### 3.1 Canonical Occupations (`src/backend/data/occupations/canonical_occupations.json`)
The platform currently anchors around **12 active canonical occupation concepts**:
1. `CAN_OCC_SOFTWARE_ENGINEER`: Software Engineer
2. `CAN_OCC_DATA_SCIENTIST`: Data Scientist
3. `CAN_OCC_DATA_ANALYST`: Data Analyst
4. `CAN_OCC_ML_ENGINEER`: Machine Learning Engineer
5. `CAN_OCC_DATA_ENGINEER`: Data Engineer
6. `CAN_OCC_DEVOPS_ENGINEER`: DevOps & Cloud Engineer
7. `CAN_OCC_CYBERSECURITY_ANALYST`: Cybersecurity & Information Security Professional
8. `CAN_OCC_DATABASE_ADMIN`: Database Administrator & Architect
9. `CAN_OCC_SYSTEMS_ANALYST`: Systems Analyst & Solutions Architect
10. `CAN_OCC_NETWORK_ENGINEER`: Network & Systems Engineer
11. `CAN_OCC_QA_TEST_ENGINEER`: Quality Assurance & Software Test Engineer
12. `CAN_OCC_IT_PROJECT_MGR`: IT Project & Program Manager

### 3.2 National Occupational Classifications (`src/backend/schemas/occupation.py`)
- `ClassificationId`:
  - `US_SOC_2018` (US Bureau of Labor Statistics)
  - `UK_SOC_2020` (UK Office for National Statistics)
  - `AU_ANZSCO_2022` / `AU_OSCA_2024` (Australian Bureau of Statistics / JSA)
  - `SG_SSOC_2020` / `SG_SSOC_2024` (Singapore Department of Statistics)
  - `IN_NCO_2015` (India Ministry of Labour and Employment)
  - `INT_ISCO_08` (International Labour Organization anchor)

### 3.3 Governance & Revocation Sub-system (`src/backend/governance/`)
- `src/backend/governance/revocation.py`: Centralized `RevocationManifest` supporting dynamic source revocation and publication gating.
- `src/backend/governance/lifecycle.py`: Data lifecycle states (`ACTIVE`, `DEPRECATED`, `EXPIRED`, `REVOKED`, `WITHHELD`).
- `src/backend/governance/engine.py`: Dynamic policy enforcement.

---

## 4. PREFLIGHT CERTIFICATION & SCOPE CONFIRMATION

1. **Isolation Guarantee:** All Sprint 3B.3.2 pilot code, datasets, evaluation test suites, and documentation will reside strictly under `docs/jobintel_v2/sprints/sprint_3b_3_2/`.
2. **Zero Ingestion into Production:** No datasets generated during this empirical pilot will be committed to `src/backend/data/` or loaded into live API routers.
3. **UK Demand Publication Gate:** The Textkernel UK demand publication gate deployed in Sprint 3B.2.3.5 remains 100% active and uncompromised.
4. **Readiness:** The repository is in an optimal state to begin Phase 1 (Employer Cohort Selection).
