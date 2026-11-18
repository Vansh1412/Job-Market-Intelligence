# SPRINT 3B.3.3.4.4 — STAGING INGESTION EXECUTION & AUDIT LOG
**Sprint:** 3B.3.3.4.4 — Controlled Five-Employer Staging Ingestion, Provenance Validation & Live Registry Qualification  
**Date:** 2026-11-18  
**Operator:** Principal Data Engineer & Release Manager  
**Execution Environment:** Staging (`staging/sprint2c3`)  
**Status:** COMPLETED SUCCESSFULLY — 5 RECORDS INGESTED

---

## 1. Execution Overview & Pre-Flight Validation

The staging ingestion runner `src/backend/ingestion/employers_pilot.py` was executed under strict governance controls:
1. **Production Guardrail Check:** Verified rejection of `--env production` with security violation code 1.
2. **Pre-flight Dry Run:** Verified full schema validation, identifier resolution, and cryptographic hash computation.
3. **Controlled Ingestion Execution:** Ingested the audited 5-candidate cohort into `data/processed/staging_employers.json`.

---

## 2. Dry Run Execution Log

```
$ python -m src.backend.ingestion.employers_pilot --env staging --dry-run
DRY RUN RESULT:
{
  "mode": "DRY_RUN",
  "status": "PASS",
  "candidates_count": 5,
  "payload_sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5",
  "validation_report": {
    "status": "VALIDATED",
    "candidates_count": 5,
    "candidate_ids": [
      "comp_au_atlassian",
      "comp_us_microsoft",
      "comp_uk_arm",
      "comp_sg_dbs",
      "comp_in_infosys"
    ],
    "resolution_audit": [
      {
        "company_id": "comp_au_atlassian",
        "statutory_id": "53102443916",
        "statutory_authority": "ASIC",
        "match_type": "EXACT_IDENTIFIER_MATCH",
        "review_status": "AUTOMATICALLY_RESOLVED"
      },
      {
        "company_id": "comp_us_microsoft",
        "statutory_id": "0000789019",
        "statutory_authority": "US SEC",
        "match_type": "EXACT_IDENTIFIER_MATCH",
        "review_status": "AUTOMATICALLY_RESOLVED"
      },
      {
        "company_id": "comp_uk_arm",
        "statutory_id": "02557590",
        "statutory_authority": "UK Companies House",
        "match_type": "EXACT_IDENTIFIER_MATCH",
        "review_status": "AUTOMATICALLY_RESOLVED"
      },
      {
        "company_id": "comp_sg_dbs",
        "statutory_id": "196800306E",
        "statutory_authority": "ACRA",
        "match_type": "EXACT_IDENTIFIER_MATCH",
        "review_status": "AUTOMATICALLY_RESOLVED"
      },
      {
        "company_id": "comp_in_infosys",
        "statutory_id": "L85110KA1981PLC013115",
        "statutory_authority": "MCA",
        "match_type": "EXACT_IDENTIFIER_MATCH",
        "review_status": "AUTOMATICALLY_RESOLVED"
      }
    ]
  }
}
```

---

## 3. Staging Ingestion Execution Log

```
$ python -m src.backend.ingestion.employers_pilot --env staging --execute
[AUDIT EVENT] {"timestamp": "2026-11-18T04:30:37.182673+00:00", "event": "EMPLOYER_STAGING_INGESTION", "environment": "staging", "company_id": "comp_au_atlassian", "company_name": "Atlassian Pty Ltd", "statutory_id": "53102443916", "statutory_authority": "ASIC", "jurisdiction": "AU", "sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5"}
[AUDIT EVENT] {"timestamp": "2026-11-18T04:30:37.182673+00:00", "event": "EMPLOYER_STAGING_INGESTION", "environment": "staging", "company_id": "comp_us_microsoft", "company_name": "Microsoft Corporation", "statutory_id": "0000789019", "statutory_authority": "US SEC", "jurisdiction": "US", "sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5"}
[AUDIT EVENT] {"timestamp": "2026-11-18T04:30:37.182673+00:00", "event": "EMPLOYER_STAGING_INGESTION", "environment": "staging", "company_id": "comp_uk_arm", "company_name": "Arm Limited", "statutory_id": "02557590", "statutory_authority": "UK Companies House", "jurisdiction": "UK", "sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5"}
[AUDIT EVENT] {"timestamp": "2026-11-18T04:30:37.182673+00:00", "event": "EMPLOYER_STAGING_INGESTION", "environment": "staging", "company_id": "comp_sg_dbs", "company_name": "DBS Bank Ltd.", "statutory_id": "196800306E", "statutory_authority": "ACRA", "jurisdiction": "SG", "sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5"}
[AUDIT EVENT] {"timestamp": "2026-11-18T04:30:37.182673+00:00", "event": "EMPLOYER_STAGING_INGESTION", "environment": "staging", "company_id": "comp_in_infosys", "company_name": "Infosys Limited", "statutory_id": "L85110KA1981PLC013115", "statutory_authority": "MCA", "jurisdiction": "IN", "sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5"}
EXECUTION RESULT:
{
  "mode": "EXECUTE",
  "status": "SUCCESS",
  "records_written": 5,
  "seed_path": "E:\\Job Market\\data\\processed\\staging_employers.json",
  "payload_sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5",
  "audit_events_count": 5
}
```

---

## 4. Post-Execution Staging Status Inspection

```
$ python -m src.backend.ingestion.employers_pilot --env staging --status
STATUS REPORT:
{
  "mode": "STATUS",
  "seed_file_path": "E:\\Job Market\\data\\processed\\staging_employers.json",
  "seed_file_exists": true,
  "seed_file_records": 5,
  "seed_file_sha256": "0509508464e1e3fb86456e333fb1be38c99fe3d63e040db04d942832ef84d3a5",
  "in_memory_records": 5,
  "in_memory_ids": [
    "comp_au_atlassian",
    "comp_us_microsoft",
    "comp_uk_arm",
    "comp_sg_dbs",
    "comp_in_infosys"
  ]
}
```
