# SPRINT 2C.2 INTEGRATION MATRIX & ENDPOINT POLICY MAPPING
## Controlled Governance Application Enforcement, Lifecycle Binding & Runtime Maturity Analysis

- **Document Identifier:** `JOBINTEL-S2C2-INT-003`
- **Milestone:** Sprint 2C.2 Controlled Integration
- **Date:** November 13, 2026
- **Status:** COMPLETED & VERIFIED
- **Target Repository:** `e:\Job Market` | **Commit Baseline:** `198b79d` (master)

---

## 1. System Integration Maturity Progression

Sprint 2C.2 moves JOBINTEL 2.0 governance from isolated units (Tiers A & B) into active runtime integration and enforcement (Tiers C & D):

- **Tier A — Exists:** Code/schema is authored and syntactically valid.
- **Tier B — Tested:** Unit tests specifically exercise the module in isolation.
- **Tier C — Integrated:** Application services or routers instantiate and invoke the module during request processing.
- **Tier D — Enforced:** HTTP request routes or runtime middleware fail closed based on engine policy decisions.

```
+---------------------------------------------------------------------------------------------------+
| GOVERNANCE MATURITY PROGRESSION (Sprint 2C.1 vs Sprint 2C.2)                                      |
+------------------------------------+--------------------------+-----------------------------------+
| Component / Layer                  | Sprint 2C.1 Level        | Sprint 2C.2 Level                 |
+------------------------------------+--------------------------+-----------------------------------+
| Governance Schemas                 | Tier A + B               | Tier A + B + C + D (Enforced)     |
| Revocation Registry (In-Memory)    | Tier A + B               | Tier A + B + C + D (Enforced)     |
| Revocation Manifest Persistence    | Not Present              | Tier A + B + C + D (Enforced)     |
| Scoped Policy Engine               | Tier A + B               | Tier A + B + C + D (Enforced)     |
| Lifecycle State Gating             | Tier A + B (Partial)     | Tier A + B + C + D (Enforced)     |
| UK Salary Routes Gating            | Tier D (Legacy 503 only) | Tier A + B + C + D (Layered 503)  |
| USA & India Inference Auditing     | Not Integrated           | Tier A + B + C (Audited/Recorded) |
| Model Training Entrypoints Gate    | Standalone Module        | Tier A + B + C + D (Enforced)     |
+------------------------------------+--------------------------+-----------------------------------+
```

---

## 2. Comprehensive Endpoint-to-Policy Mapping Table

Every active HTTP endpoint in the JOBINTEL 2.0 backend application is mapped to its authoritative governance operation, data source, authorization status, and enforcement mechanism:

| Route / HTTP Method | Endpoint Description | Governing Data Source | Intended Governance Operation | Authorization Decision | Runtime Enforcement Mechanism |
|---|---|---|---|---|---|
| `GET /api/v1/markets/UK/salary/occupations` | UK SOC 2020 occupation list | `uk.ons.ashe` | `PUBLIC_AGGREGATE_DISPLAY` | **DENIED** (`GOV_DENIED_UNREVIEWED_SOURCE`) | `verify_uk_salary_governance()` $\to$ `HTTP 503 UK_DATA_NOT_PUBLISHED` |
| `GET /api/v1/markets/UK/salary/occupations/{soc_code}` | UK Occupation salary details | `uk.ons.ashe` | `PUBLIC_AGGREGATE_DISPLAY` | **DENIED** (`GOV_DENIED_UNREVIEWED_SOURCE`) | `verify_uk_salary_governance()` $\to$ `HTTP 503 UK_DATA_NOT_PUBLISHED` |
| `GET /api/v1/markets/UK/salary/occupations/{soc}/regions` | UK Regional salary comparisons | `uk.ons.ashe` | `PUBLIC_AGGREGATE_DISPLAY` | **DENIED** (`GOV_DENIED_UNREVIEWED_SOURCE`) | `verify_uk_salary_governance()` $\to$ `HTTP 503 UK_DATA_NOT_PUBLISHED` |
| `GET /api/v1/markets/UK/salary/regions/{region}/occupations`| Regional occupation breakdown | `uk.ons.ashe` | `PUBLIC_AGGREGATE_DISPLAY` | **DENIED** (`GOV_DENIED_UNREVIEWED_SOURCE`) | `verify_uk_salary_governance()` $\to$ `HTTP 503 UK_DATA_NOT_PUBLISHED` |
| `GET /api/v1/markets/UK/salary/metadata` | UK ASHE descriptive metadata | `uk.ons.ashe` | `PUBLIC_AGGREGATE_DISPLAY` | **DENIED** (`GOV_DENIED_UNREVIEWED_SOURCE`) | `verify_uk_salary_governance()` $\to$ `HTTP 503 UK_DATA_NOT_PUBLISHED` |
| `POST /api/usa/predict` | Live USA salary prediction | `us.jobintel.market-data` | `INTERNAL_MODEL_INFERENCE` | **AUTHORIZED (TIER 1 RESEARCH)** | `record_inference_governance()` records audit event; serves inference |
| `POST /api/india/predict` | Live India salary prediction | `in.jobintel.market-data` | `INTERNAL_MODEL_INFERENCE` | **AUTHORIZED (TIER 1 RESEARCH)** | `record_inference_governance()` records audit event; serves inference |
| `POST /api/predict/estimate` | Legacy profile salary estimate | `us.jobintel.market-data` | `INTERNAL_MODEL_INFERENCE` | **AUTHORIZED (TIER 1 RESEARCH)** | `record_inference_governance()` records audit event; serves inference |
| `POST /api/usa/archetype` | USA career archetype mapping | `us.jobintel.market-data` | `INTERNAL_ANALYTICS` | **AUTHORIZED (UNRESOLVED COMMERCIAL)** | Dimension reduction via frozen PCA matrices |
| `POST /api/india/archetype` | India career archetype mapping | `in.jobintel.market-data` | `INTERNAL_ANALYTICS` | **AUTHORIZED (UNRESOLVED COMMERCIAL)** | Dimension reduction via frozen PCA matrices |
| `GET /api/v1/markets` | Supported market listing | Platform Config | `INTERNAL_ANALYTICS` | **AUTHORIZED (PUBLIC METADATA)** | Read-only platform metadata |
| `GET /api/v1/sources` | Authoritative data catalog | Platform Config | `INTERNAL_ANALYTICS` | **AUTHORIZED (PUBLIC METADATA)** | Read-only data catalog listing |
| `GET /health`, `/api/health` | Liveness health probe | Infrastructure | N/A (System Probe) | **AUTHORIZED (PUBLIC SYSTEM)** | Verifies process liveness & memory footprint |
| `GET /ready`, `/api/ready` | Readiness deployment probe | Model Registry | N/A (System Probe) | **AUTHORIZED (PUBLIC SYSTEM)** | Cryptographic model artifact checksum probe |

---

## 3. Training Entrypoint Governance Mapping

| Script Path | Function / Method | Governing Data Source | Intended Operation | Governance Decision | Technical Enforcement |
|---|---|---|---|---|---|
| `src/india/modeling.py` | `run_all_experiments()` | `in.jobintel.market-data` | `ML_TRAINING` | **PERMANENTLY DENIED** | Pre-flight call to `TrainingGovernanceGate` raises `PermissionError: GOV_DENIED_ZERO_RETRAINING_RULE` |
| `src/run_phase5_experiments.py` | `main()` | `us.jobintel.market-data` | `ML_TRAINING` | **UNAUTHORIZED WITHOUT TIER 2** | Pre-flight call to `TrainingGovernanceGate` raises `PermissionError: GOV_DENIED_TRAINING_UNAUTHORIZED` |
| `src/phase5/evaluation.py` | `evaluate_baselines_cv()` | Evaluation only | `INTERNAL_ANALYTICS` | Read-only holdout evaluation | Subordinate function called only by `run_phase5_experiments.py` |
| `src/backend/services/usa_service.py` | `USAService.predict()` | Frozen artifact | `INTERNAL_MODEL_INFERENCE` | **AUTHORIZED (RESEARCH)** | Loads verified `.joblib` model artifact; zero training calls |
| `src/backend/services/india_service.py`| `IndiaService.predict()` | Frozen artifact | `INTERNAL_MODEL_INFERENCE` | **AUTHORIZED (RESEARCH)** | Loads verified `.joblib` model artifact; zero training calls |

---

## 4. Unresolved Authorization Questions

In accordance with strict audit discipline, the platform does not assume or fabricate permissions:

1. **USA Model Commercial Exploitation Status:**
   - *Current State:* Evaluated as `INTERNAL_MODEL_INFERENCE` (Authorized).
   - *Unresolved Question:* DataForge Dataset A terms grant Tier 1 internal analytics rights. Commercial customer-facing inference (`COMMERCIAL_MODEL_INFERENCE`) remains **UNRESOLVED** until formal legal verification confirms Tier 2 commercial AI addendum.
   - *Technical Protection:* Any request submitting `operation=GovernanceOperation.COMMERCIAL_MODEL_INFERENCE` is rejected by Gate 3 with `GOV_DENIED_COMMERCIAL_RESTRICTION`.
2. **India Model Raw Provenance Clearance:**
   - *Current State:* Historical model weights frozen under Zero-Retraining rule.
   - *Unresolved Question:* Raw scraper provenance remains unverified. Retraining is permanently blocked. Inference is permitted under legacy research continuity.
3. **UK ASHE Descriptive Data Publication:**
   - *Current State:* Blocked under `REVIEW_REQUIRED` (`GOV_DENIED_UNREVIEWED_SOURCE`).
   - *Unresolved Question:* Requires formal sign-off from the Data Governance Board and dual-custody `ApprovalRecord` before release eligibility can be transitioned to `USE_APPROVED`.

