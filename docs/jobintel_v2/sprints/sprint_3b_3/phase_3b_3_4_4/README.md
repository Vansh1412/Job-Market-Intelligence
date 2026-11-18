# SPRINT 3B.3.3.4.4 — DOCUMENTATION MAP & ARTIFACT DIRECTORY

**Sprint:** 3B.3.3.4.4: Controlled Five-Employer Staging Ingestion, Provenance Validation & Live Registry Qualification  
**Platform:** JOBINTEL 2.0 — Global Career and Employer Intelligence Platform  
**Target Environment:** Staging (`staging/sprint2c3`)  
**Production Status:** STRICTLY FROZEN (`198b79dcdff08a5be5f08847c4262d31a3ce261e`)  
**Verdict:** **PASS — FIVE-EMPLOYER STAGING PILOT VERIFIED**

---

## Sprint Deliverables Directory

| # | Artifact Filename | Type | Description |
| :--- | :--- | :--- | :--- |
| **01** | [`01_runtime_and_ingestion_baseline.md`](./01_runtime_and_ingestion_baseline.md) | Markdown | Staging runtime baseline, in-memory storage topology, Render free-tier analysis, and frozen models. |
| **02** | [`02_candidate_evidence_gate_matrix.csv`](./02_candidate_evidence_gate_matrix.csv) | CSV | Comprehensive evaluation of Gates A, B, C, D across the 5 sovereign employer candidates. |
| **03** | [`03_candidate_source_permission_register.csv`](./03_candidate_source_permission_register.csv) | CSV | Source licensing, terms of use, redistribution rights, and statutory privacy compliance matrix. |
| **04** | [`04_candidate_identity_evidence.md`](./04_candidate_identity_evidence.md) | Markdown | Exhaustive forensic evidence, sovereign registry URLs, Infosys CIN resolution, and Arm UK code analysis. |
| **05** | [`05_ingestion_candidate_manifest.csv`](./05_ingestion_candidate_manifest.csv) | CSV | Standardized ingestion manifest containing candidate records, statutory IDs, and source citations. |
| **06** | [`06_staging_ingestion_execution_log.md`](./06_staging_ingestion_execution_log.md) | Markdown | Execution logs for CLI commands (`--dry-run`, `--execute`, `--status`), SHA-256 hash, and audit events. |
| **07** | [`07_post_ingestion_api_validation.md`](./07_post_ingestion_api_validation.md) | Markdown | Full REST API contract verification for `/api/v1/employers` and `/api/v1/employers/resolve`. |
| **08** | [`08_live_staging_frontend_qualification.md`](./08_live_staging_frontend_qualification.md) | Markdown | Live qualification of the `/employers` route and interactive Resolution Workbench on Vercel staging. |
| **09** | [`09_security_and_production_isolation.md`](./09_security_and_production_isolation.md) | Markdown | Application security review, production freeze enforcement, model immutability, and privacy compliance. |
| **10** | [`10_test_and_artifact_integrity_report.md`](./10_test_and_artifact_integrity_report.md) | Markdown | 462 automated test results (411 backend + 51 frontend) and 19 model SHA-256 checksum verifications. |
| **11** | [`11_rollback_and_failure_review.md`](./11_rollback_and_failure_review.md) | Markdown | Deterministic rollback protocol (`--rollback`), failure mode resilience, and RTO/RPO metrics. |
| **12** | [`SPRINT_3B_3_3_4_4_FINAL_REPORT.md`](./SPRINT_3B_3_3_4_4_FINAL_REPORT.md) | Markdown | Master engineering and qualification report with executive findings, architecture, and verdict. |
| **13** | [`README.md`](./README.md) | Markdown | This document index and navigation guide. |

---

## Ingested Five-Candidate Cohort Summary

```
+----------------------------------------------------------------------------------------------------+
| Company ID         | Legal Name            | Market | Authority & Statutory ID | Headcount Basis   |
+--------------------+-----------------------+--------+--------------------------+-------------------+
| comp_au_atlassian  | Atlassian Pty Ltd     | AU     | ASIC / ABR: 53102443916  | WGEA (1k - 5k)    |
| comp_us_microsoft  | Microsoft Corporation | US     | U.S. SEC: 0000789019     | SEC 10-K (228,000)|
| comp_uk_arm        | Arm Limited           | UK     | Companies House: 02557590| UK GPG (1k - 5k)  |
| comp_sg_dbs        | DBS Bank Ltd.         | SG     | ACRA: 196800306E         | Annual (36,000)   |
| comp_in_infosys    | Infosys Limited       | IN     | MCA: L85110KA1981PLC013115| SEBI BRSR (317,240)|
+----------------------------------------------------------------------------------------------------+
```
