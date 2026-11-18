# SPRINT 3B.3.3.4.6 — INGESTION RUNNER SPECIFICATION & VALIDATION
**Sprint:** 3B.3.3.4.6  
**Document:** `08_ingestion_runner_validation.md`  
**Date:** 2026-11-18  
**Author:** Principal Data Engineer & QA Architect  
**Status:** COMPLETE & VERIFIED  

---

## 1. Pipeline CLI Architecture

The staging pilot ingestion runner is located at [src/backend/ingestion/employers_pilot.py](file:///e:/Job%20Market/src/backend/ingestion/employers_pilot.py). It provides a robust, fail-safe CLI for managing the staging employer seed:

```bash
# Display catalog status and manifest checksum
python -m src.backend.ingestion.employers_pilot --status

# Cryptographically verify the seed against its manifest
python -m src.backend.ingestion.employers_pilot --verify

# Execute safe staging ingestion (writes seed and manifest atomically)
python -m src.backend.ingestion.employers_pilot --env staging --execute

# Roll back staging seed
python -m src.backend.ingestion.employers_pilot --env staging --rollback
```

---

## 2. Validation Stages in `run_ingest`

Before any profile is written to disk, it passes through 5 mandatory validation gates:

1. **Statutory Entity Verification:** The legal company name, statutory identifier (e.g. ABN, CIK, CRN, UEN, CIN), and statutory authority (e.g. ASIC, SEC, Companies House, ACRA, MCA) must be present and conform to regulatory patterns.
2. **Jurisdiction & Market Alignment:** The legal incorporation jurisdiction must be compatible with the platform market.
3. **Headcount Evidence Validation:** The profile must supply either an audited headcount number or an official size band, backed by a cited regulatory basis (e.g. WGEA, SEC Form 10-K, UK Gender Pay Gap, ACRA Bizfile, SEBI BRSR) and explicit reporting scope (`DOMESTIC_OPERATING_BAND`, `GLOBAL_CONSOLIDATED`, `UK_OPERATING_BAND`, `GROUP_OPERATING_TOTAL`, `GLOBAL_AUDITED_TOTAL`).
4. **Source Attribution & Licensing:** An explicit public sector license and mandatory attribution notice must be declared.
5. **Deterministic Serialization:** JSON output is formatted with `indent=2`, sorted keys, explicit `\n` line endings, and hashed via SHA-256.

---

## 3. Test Suite Verification (`tests/test_employers_pilot.py`)

A comprehensive suite of 11 isolated unit and integration tests verifies every operational scenario:

| Test Name | Tested Behavior | Status |
| :--- | :--- | :--- |
| `test_staging_dry_run_does_not_write_files` | Dry run reports candidates without writing files to disk | **PASSED** |
| `test_staging_execute_and_rollback_lifecycle` | Validates full ingestion cycle and rollback using isolated `tmp_path` | **PASSED** |
| `test_staging_ingestion_idempotency` | Multiple executions produce identical files and identical SHA-256 digests | **PASSED** |
| `test_staging_ingestion_rejects_production_environment` | CLI and function fail immediately when targeting production | **PASSED** |
| `test_staging_ingestion_atomic_write` | Validates atomic file rename via `.tmp` file | **PASSED** |
| `test_load_staging_seed_success` | Validates clean seed loading and profile deserialization | **PASSED** |
| `test_load_staging_seed_missing_file_raises` | Validates `SeedIntegrityError` when seed is absent | **PASSED** |
| `test_load_staging_seed_checksum_mismatch_raises` | Validates `SeedIntegrityError` when file digest is altered | **PASSED** |
| `test_load_registry_for_environment_gating` | Validates dispatch on `JOBINTEL_ENV="staging"` vs other environments | **PASSED** |
| `test_status_and_verify_cli_functions` | Validates `--status` and `--verify` reporting | **PASSED** |
| `test_repository_seed_file_is_never_deleted_by_tests` | Proves repo seed is never touched or unlinked during test runs | **PASSED** |
