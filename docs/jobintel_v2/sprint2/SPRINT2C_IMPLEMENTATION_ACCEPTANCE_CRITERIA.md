# SPRINT 2C — IMPLEMENTATION ACCEPTANCE CRITERIA
## Verification Matrix, Automated Regression Invariants & Test Specifications for Sprint 2C.1

- **Document Identifier:** `JOBINTEL-S2C-SPEC-008`
- **Status:** Approved Engineering Specification (Sprint 2C.0 Consolidation)
- **Authority:** Subordinate to `SPRINT2C_GOVERNANCE_MASTER_STANDARD.md`
- **Date:** November 2026
- **Applies to:** QA Lead, Backend Engineers, CI/CD Automated Test Harness

---

## 1. Non-Negotiable Invariant Preservation Gates

Before any new Sprint 2C.1 implementation code may be merged, the automated test harness must prove that the following baseline invariants remain completely intact:

| Invariant ID | Test Assertion | Target Baseline | Failure Consequence |
|---|---|---|---|
| `INV-01` | **India Prediction Parity** | `tests/test_golden_predictions.py` passes with $10^{-6}$ tolerance | Immediate Build Abort |
| `INV-02` | **USA Prediction Parity** | `tests/test_golden_predictions.py` passes with $10^{-6}$ tolerance | Immediate Build Abort |
| `INV-03` | **Artifact Bitwise Integrity** | 10 model artifact SHA-256 digests match `artifact_manifest.json` | Immediate Build Abort |
| `INV-04` | **Prediction Schema Invariance** | `SalaryResponse.salary_value` remains finite, positive Decimal ($> 0$) | Immediate Build Abort |
| `INV-05` | **UK Fail-Closed Gating** | All 5 UK endpoints return `HTTP 503 UK_DATA_NOT_PUBLISHED` | Immediate Build Abort |
| `INV-06` | **Zero Working-Tree Mutation** | Working-tree status remains clean; no untracked raw data leakage | Immediate Build Abort |

---

## 2. Acceptance Criteria by Architecture Module

### 2.1 Module 1: Schema & Contract Separation
- **`AC-SCH-01`:** `src/backend/schemas/salary.py` must NOT be modified to introduce nullability. Model prediction contracts must remain strictly positive.
- **`AC-SCH-02`:** Statistical observation responses must be isolated in `src/backend/schemas/uk_salary.py` (or a dedicated `src/backend/schemas/statistical_salary.py`).
- **`AC-SCH-03`:** Statistical models must support:
  - `salary_value: Decimal | None = None`
  - `value_status: ASHEValueStatus` (`REPORTED`, `SUPPRESSED_QUALITY`, `BLANK_UNKNOWN`, `SUPPRESSED_DISCLOSURE`, `NOT_APPLICABLE`, `NIL_OR_NEGLIGIBLE`)
  - `original_cell_marker: str` (`"x"`, `".."` , `""`, `":"`, `"-"`)
  - `cv_quality_band: str` (`PRECISE`, `REASONABLY_PRECISE`, `ACCEPTABLE`, `UNRELIABLE`)

### 2.2 Module 2: Governance Policy Engine (`src/backend/governance/`)
- **`AC-POL-01` (Fail-Closed Default):** If a source has no registered contract or an `UNKNOWN` permission state, `engine.evaluate()` must return `DENIED` with reason `ERR_GOV_SOURCE_UNREGISTERED` or `ERR_GOV_OPERATION_UNAUTHORIZED`.
- **`AC-POL-02` (Multi-Market Failure Isolation):** If `uk.ons.ashe` is locked, suspended, or corrupted, the policy engine must return `DENIED` for UK routes while simultaneously returning `ALLOWED` for valid India and USA prediction requests.
- **`AC-POL-03` (Bitwise Checksum Gate):** If the physical CSV on disk diverges from `manifest.processed_dataset_sha256` by even 1 byte, `engine.verify_dataset()` must raise `IntegrityError` and block route activation.
- **`AC-POL-04` (URL Alignment Gate):** If `manifest.source_reference` does not match `catalog.source_reference`, `source_reference_matches_catalog` must evaluate to `False`, blocking publication.
- **`AC-POL-05` (Information Leakage Prevention):** Public API error responses must return sanitized strings (e.g., `UK_DATA_NOT_PUBLISHED`), never exposing internal file paths, raw coordinate tuples, or environment details.
- **`AC-POL-06` (Revocation Cache Synchronization):** Calling the policy reload hook (`POST /api/v1/governance/reload-policies`) must invalidate in-memory grants within 10 milliseconds. Routine cache revalidation must not exceed a 30-second TTL.

### 2.3 Module 3: Zero-Retraining Safeguards
- **`AC-ML-01` (Pre-Commit Guard):** A pre-commit hook script (`scripts/hooks/pre-commit-zero-retraining.py`) must scan staged diffs and abort commits if calls to `fit()`, `fit_transform()`, or `train()` are detected on India or USA datasets.
- **`AC-ML-02` (Lineage Verification):** Service startup must verify that the loaded model weights correspond to the approved baseline commit (`198b79d`) recorded in `ModelProvenanceRecord`.

### 2.4 Module 4: Occupation Crosswalk Concordance
- **`AC-XWK-01` (Taxonomy Fidelity):** All crosswalk queries must explicitly identify source and target classification standards and versions (e.g., `UK_SOC_2020` $\leftrightarrow$ `AU_OSCA_2024`).
- **`AC-XWK-02` (Approximation Disclaimer):** Any crosswalk resolution with evaluated confidence $< 0.95$ must inject the mandatory user-facing approximation disclaimer into the payload.
- **`AC-XWK-03` (Symmetry / Asymmetry Enforcement):** `EXACT_EQUIVALENCE` mappings must assert identical bidirectional confidence scores; `ONE_TO_MANY` mappings must assert that inverse queries return `MANY_TO_ONE`.

### 2.5 Module 5: Employer Intelligence Safeguards
- **`AC-EMP-01` (Source Whitelist):** The employer ingestion runner must reject any input URL matching blacklisted domains (`linkedin.com`, `glassdoor.com`, `indeed.com`).
- **`AC-EMP-02` (PII Elimination):** Parsed employer records must be scanned for regex patterns matching email addresses, phone numbers, and individual personal names; any match aborts ingestion.
- **`AC-EMP-03` (K-Anonymity Filter):** If observed postings or reports for an employer in an occupation-region bucket is $< 5$, the API must return `value_status: "SUPPRESSED_DISCLOSURE"`.
- **`AC-EMP-04` (Posting vs. Hire Segregation):** All employer vacancy indicators must declare `data_nature: "ONLINE_JOB_ADVERTISEMENT"` and include the statutory notice: *"Posting volumes reflect recruitment marketing, not completed hires."*

---

## 3. Automated Regression Test Specifications

The following 12 automated test cases must be added to `tests/test_governance_engine.py` during Sprint 2C.1:

```python
# Test Case Specifications for Sprint 2C.1
def test_gov_01_unknown_source_fails_closed():
    """Unregistered source ID must return DENIED and HTTP 500/503."""
    ...

def test_gov_02_failure_isolation_preserves_unrelated_markets():
    """Locking UK ASHE must not alter HTTP 200 responses on India/US prediction routes."""
    ...

def test_gov_03_checksum_mismatch_blocks_service_boot():
    """Altering one byte of processed CSV causes UKSalaryService to halt initialization."""
    ...

def test_gov_04_url_discrepancy_blocks_publication():
    """soc2010ashetable15 vs socashetable15 discrepancy results in publication_eligible=False."""
    ...

def test_gov_05_salary_prediction_schema_remains_positive():
    """SalaryResponse rejects null and negative numbers; guarantees backward compatibility."""
    ...

def test_gov_06_statistical_schema_accepts_suppressions():
    """UKSalaryResponse successfully serializes 'x' quality suppressions with null salary."""
    ...

def test_gov_07_zero_retraining_hook_detects_fit_calls():
    """Pre-commit verification script detects and rejects scikit-learn fit() invocations."""
    ...

def test_gov_08_crosswalk_injects_approximation_disclaimer():
    """Query with confidence < 0.95 contains non-empty disclaimer string."""
    ...

def test_gov_09_employer_ingestion_blocks_blacklisted_domains():
    """Ingesting URL from LinkedIn raises SecurityGovernanceError."""
    ...

def test_gov_10_employer_k_anonymity_suppression():
    """Employer queries with count < 5 return SUPPRESSED_DISCLOSURE."""
    ...

def test_gov_11_revocation_cache_invalidation_within_ttl():
    """Revoked source transitions from 200 to 503 upon cache TTL expiration."""
    ...

def test_gov_12_sanitized_api_errors_prevent_path_leakage():
    """HTTP 503 response body contains no filesystem paths or raw coordinates."""
    ...
```

---

## 4. Non-Functional & Render Free-Tier Criteria

1. **Memory Overhead:** Total RAM consumed by in-memory manifests, crosswalk indexes, and permission trees must not exceed **10 MB** (well within Render's 512MB limit).
2. **Lookup Latency:** In-memory permission evaluation and crosswalk resolution must execute in $\le 1.0 \text{ ms}$ (99th percentile).
3. **Zero Database Dependency:** Governance enforcement must function with 100% fidelity using local read-only files, requiring no external PostgreSQL or Redis daemons.

