# SPRINT 2C — ARCHITECTURE DECISIONS & OPEN QUESTIONS
## Consolidated Architectural Decision Records (ADRs), Evidentiary Separation & Risk Ledger

- **Document Identifier:** `JOBINTEL-S2C-ADR-007`
- **Status:** Approved Architectural Record (Sprint 2C.0 Consolidation)
- **Authority:** Subordinate to `SPRINT2C_GOVERNANCE_MASTER_STANDARD.md`
- **Date:** November 2026
- **Applies to:** Engineering Leadership, Compliance Officers, Product Architecture

---

## 1. Evidentiary Baseline Separation

A core requirement of technical governance is the rigorous, uncompromising separation of verified facts from unverified claims, proposed decisions, and unresolved legal questions.

```
+---------------------------------------------------------------------------------------------------+
| FOUR-TIER EVIDENTIARY AUDIT SEPARATION                                                            |
+---------------------------------------------------------------------------------------------------+
| TIER 1: VERIFIED REPOSITORY FACTS (Directly Proven on Disk via SHA-256 & Code Inspection)         |
| • ASHE Archive SHA-256: AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3            |
| • Processed CSV SHA-256: DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E        |
| • Provenance Manifest SHA-256: C58B143BCA23849B5BCE762E42677AEE5A41FB2715A40D2054CA6059206FC95E  |
| • ASHE Estimate 15.7a SHA-256: 670924CAA882B8D2723D812F0B03B0DD4A40B145EA00F07DD3F0C9A7619250AA  |
| • ASHE CV 15.7b SHA-256: A4E18B88E39C8F7E47EAA7DDECE24FE6F8373332D2315CA76B575F7CC7B2C8EC        |
| • SOC 2020 Coding Index SHA-256: B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3|
| • ASHE Dimensions: Exactly 4,532 rows (412 SOC unit groups x 11 GB regions). 1,339 numeric medians,|
|   2,818 'x' quality suppressions, 375 blanks. Zero numeric P10-P90 percentiles in Table 15 (4).   |
| • DataForge Dataset A Contract: Schedule A has Tier 1 checked [X] and Tier 2 unchecked [ ].       |
| • India Raw Data: indian-job-market-dataset-2025.xlsx has NO license file, datasheet, or vendor ToS|
| • Employer Registry: src/backend/employers/registry.py is physically initialized empty: ().       |
| • Test Integrity: 254 backend pytest tests pass (23.74s); 9 frontend vitest tests pass (38.68s).  |
| • UK Endpoints: All 5 routes fail closed with HTTP 503 UK_DATA_NOT_PUBLISHED.                     |
+---------------------------------------------------------------------------------------------------+
| TIER 2: REPORTED BUT UNVERIFIED FACTS (Claims in Earlier Drafts Not Grounded in Code)             |
| • Synthetic SHA-256 digests in draft text (7BC6..., C3D8..., 9B2F..., D78A...). Formally rejected. |
| • Historical claims that employer intelligence had populated company profiles. Disproven; empty.   |
| • Claims that "zero-retraining" was an active technical sandbox. Disproven; it was unenforced.   |
+---------------------------------------------------------------------------------------------------+
| TIER 3: PROPOSED ARCHITECTURAL DECISIONS (Consolidated Standards for Sprint 2C)                  |
| • Standardize on the Canonical 9-State Data Lifecycle.                                           |
| • Enforce strict contract separation: Model predictions (positive) vs Statistical observations.   |
| • Adopt 7-State Purpose-Specific Permission Matrix across 7 orthogonal operations.               |
| • Reject automatic ISCO-08 pivot in favor of direct, evidence-backed concordance tables.          |
| • Adopt Multi-Tier Employer Evidence model and treat k=5 as minimum screening threshold.          |
| • Implement isolated, fail-closed GovernancePolicyEngine with 30s TTL cache.                      |
+---------------------------------------------------------------------------------------------------+
| TIER 4: UNRESOLVED QUESTIONS REQUIRING HUMAN / LEGAL REVIEW                                       |
| • Formal legal sign-off on commercial monetization of USA XGBoost model under DataForge Tier 1.   |
| • Acquisition of replacement open-government microdata for India (MOSPI PLFS).                    |
| • Completion of dual-custody executive sign-off for UK ASHE release.                             |
| • Reconciliation of ONS URL slug (soc2010ashetable15 vs socashetable15).                         |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Contradictions Resolved in Sprint 2C.0

1. **Resolution of Checksum Divergence:**
   - *Contradiction:* Earlier draft documentation cited illustrative hashes (`7BC6...`, `C3D8...`).
   - *Resolution:* Physical bitwise analysis established the real, immutable hashes on disk (`AC1202E9...`, `DEC9D305...`, `C58B143B...`, `670924CA...`). All standards now reference the real hashes.
2. **Rejection of Universal DAG / Acyclicity in Crosswalks:**
   - *Contradiction:* Previous proposals demanded all crosswalk mapping graphs be acyclic.
   - *Resolution:* Reciprocal 1:1 mappings naturally form cycles ($A \to B$ and $B \to A$). The acyclicity rule was eliminated and replaced with transitivity, version-isolation, and symmetry consistency rules.
3. **Rejection of Boolean Permission Model:**
   - *Contradiction:* Permissions were modeled as simple booleans (`can_publish: bool`).
   - *Resolution:* Replaced with an auditable 7-state enum (`UNKNOWN`, `REVIEW_REQUIRED`, `APPROVED`, `CONDITIONAL`, `DENIED`, `EXPIRED`, `REVOKED`) across 7 orthogonal operation checks.
4. **Prevention of Model Prediction Contract Mutation:**
   - *Contradiction:* Proposed refactoring `SalaryResponse` in `src/backend/schemas/salary.py` to allow nullable salaries.
   - *Resolution:* Rejected. Model predictions must remain non-null, strictly positive, and unchanged. Statistical observations are isolated in dedicated statistical response models.
5. **Rejection of ISCO-08 as an Automatic Universal Pivot:**
   - *Contradiction:* Assumed all national standards could be mapped losslessly through ILO ISCO-08.
   - *Resolution:* Documented ISCO-08's obsolescence for modern tech roles; mandated direct, versioned concordance tables.
6. **Clarification of Zero-Retraining Policy:**
   - *Contradiction:* Claimed zero-retraining was an active technical mechanism.
   - *Resolution:* Correctly classified as an enterprise **governance rule**, with technical CI/git hooks scheduled for Sprint 2C.1 implementation.
7. **Refinement of Anonymity Standard:**
   - *Contradiction:* Claimed $k=5$ provides a "universal guarantee of anonymity".
   - *Resolution:* Clarified that $k=5$ is a **minimum screening threshold**, requiring additional safeguards against inferential re-identification.
8. **Realistic Revocation Latency:**
   - *Contradiction:* Claimed "0-millisecond revocation".
   - *Resolution:* Specified realistic in-memory caching with 30-second TTL and explicit admin webhook invalidation.

---

## 3. Contradictions Still Unresolved (Pending Sprint 2C.1 & Legal Action)

1. **ASHE URL Slug Discrepancy:**
   - The ONS publication page URL contains `soc2010ashetable15` in its historical download path, whereas `src/backend/data_catalog/registry.py:79` declares `socashetable15`.
   - *Status:* Unresolved. Requires product decision: either update catalog URL to match ONS actual release slug or wait for ONS URL redirect.
2. **DataForge Commercial Deployment Ambiguity:**
   - Section 1.2 allows sharing "Derived Materials" (models), but Schedule A purchased only Tier 1, while Tier 2 explicitly governs "commercial model deployment".
   - *Status:* Unresolved. Requires formal legal counsel review before commercial paid API tiers can be launched.
3. **Empty Employer Registry Population Plan:**
   - `src/backend/employers/registry.py` is empty, but mock frontend components may expect sample data.
   - *Status:* Unresolved. Controlled population under Companies House API is queued for Phase 3.

---

## 4. Architectural Decision Records (ADRs)

### ADR-01: Adoption of Canonical 9-State Data Lifecycle
- **Context:** Multiple conflicting lifecycle representations existed across historical sprint documents.
- **Decision:** Formally adopt the 9-state machine defined in `SPRINT2C_GOVERNANCE_MASTER_STANDARD.md`.
- **Consequences:** All future ingestion scripts and policy checks must implement explicit transitions matching these 9 states.

### ADR-02: Strict Separation of Prediction vs. Observation Schemas
- **Context:** ONS statistics include suppressed cells (`x`, `..`), while ML models predict continuous values.
- **Decision:** Keep `src/backend/schemas/salary.py` frozen and positive. Dedicated schemas (`src/backend/schemas/uk_salary.py`) handle nullable statistical observations.
- **Consequences:** Preserves 100% backward compatibility for India and USA prediction APIs.

### ADR-03: Purpose-Specific 7-State Permission Evaluation
- **Context:** Boolean flags could not represent conditional, expired, or pending review states.
- **Decision:** Adopt the `PermissionState` enum evaluated across 7 orthogonal operation dimensions.
- **Consequences:** Every source must declare its permission matrix; unknown states fail closed.

### ADR-04: Version-Bound Approvals & Checksum Sealing
- **Context:** Approvals were previously documented as general policy statements.
- **Decision:** Approvals must be bound to exact physical artifact SHA-256 digests and version identifiers.
- **Consequences:** Any change in underlying data files immediately revokes approval.

