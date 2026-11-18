# SPRINT 3B.3.3.4.3 — BASELINE AND ARTIFACT INVENTORY
**Sprint:** 3B.3.3.4.3 — Employer Registry Data Readiness, Source Governance & Publication Eligibility Audit  
**Date:** 2026-11-18  
**Audit Role:** Principal Data Architect, Data Governance Auditor, Compliance Analyst, Entity Resolution Specialist & QA Lead  
**Execution Mode:** STRICTLY READ-ONLY (No code, schema, model, or database mutation)

---

## 1. System Baseline

| Environment / Asset | Target / Value | Verification Status |
|---|---|---|
| **Repository** | `Job-Market-Intelligence` | Verified |
| **Active Staging Branch** | `staging/sprint2c3` | Verified |
| **Local Staging HEAD** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | Matches remote `origin/staging/sprint2c3` |
| **Remote Staging HEAD** | `1f5472c420538a397aa986fe64c6d7b6f9c7eb8b` | Verified |
| **Production Master Baseline** | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | FROZEN — Zero access or mutation |
| **Staging Frontend URL** | `https://jobintel-staging.vercel.app` | Verified live |
| **Staging Backend URL** | `https://jobintel-backend-staging.onrender.com` | Verified live |
| **Worktree Status** | Clean (0 modified tracked files) | Verified |
| **Registry State** | Exactly 0 employer profiles loaded in active memory (`_registry = EmployerRegistry()`) | Verified |

---

## 2. Comprehensive Artifact Inventory

The following table provides the exhaustive cryptographic and metadata inventory of all historical employer datasets, source catalogs, observation ledgers, benchmarks, and configuration manifests evaluated during this audit.

| Artifact | Version | Records | SHA-256 | Evidence Type | Status |
|---|---|---:|---|---|---|
| [employer_pilot_records.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.json) | 1.0 | 28 | `6689d608c996ce1efbbf82bd5b9fef3f4fab01cd1a2f1cafba0b5931d9bb6ba9` | Raw Research Dataset | `VERIFIED_PRESENT` |
| [employer_pilot_records.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.csv) | 1.0 | 28 | `fc32442686ca4d7ddc84df37296106776f2413feed8851a9c89ddb8a85910211` | Raw Research Dataset | `VERIFIED_PRESENT` |
| [employer_candidate_register.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_candidate_register.csv) | 1.0 | 45 | `2d59d2645826d3f98d467a8ce8441c27c478df8c4bfa98ab56b9f3d2f9dd64e4` | Candidate Universe | `VERIFIED_PRESENT` |
| [employer_source_catalog.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_source_catalog.json) | 1.0 | 14 | `db1f6203e201f4d0421407d89c003475225feb7e69c5f8c2a3db256c64c4bae7` | Governance Catalog | `VERIFIED_PRESENT` |
| [employer_evidence_ledger.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_evidence_ledger.csv) | 1.0 | 8 | `f9ff9b3247786c72bbefdff015d00243318eab80ccdf906e1d6bd8c2dfdacee5` | Legal Evidence Ledger | `VERIFIED_PRESENT` |
| [employer_hiring_observations.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_hiring_observations.json) | 1.0 | 32 | `1712946b10d5b7f44af5703f34b31685b12fc53df86a1dc998dedc6aa1ead059` | Empirical Observations | `VERIFIED_PRESENT` |
| [employer_skill_observations.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_skill_observations.json) | 1.0 | 22 | `d33255094ae970c2eaa9f7a00752710dd2550a6fb926c1a45ef9f8a8b19665b6` | Empirical Observations | `VERIFIED_PRESENT` |
| [employer_entity_resolution_gold.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_entity_resolution_gold.json) | 1.0 | 100 | `d53cf59b756abe1611a53ef79aad418c27846aec8dff1d49d978287148289f05` | Validation Benchmark | `VERIFIED_PRESENT` |
| [job_title_mapping_gold.json](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2/data/job_title_mapping_gold.json) | 1.0 | 100 | `ef161e37a8776f87a41bc2ac40c573859f893b143d392d3ac60b90f0913c411c` | Validation Benchmark | `VERIFIED_PRESENT` |
| [EMPLOYER_PUBLICATION_ELIGIBILITY_MATRIX.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2_1/EMPLOYER_PUBLICATION_ELIGIBILITY_MATRIX.csv) | 2.0 | 82 | `234bf5821167c2a4285e5517eeca60f9206884f82c63a813bdc42f219af34f6e` | Publication Decision Matrix | `VERIFIED_PRESENT` |
| [OBSERVATION_TO_SOURCE_CROSSWALK.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2_1/OBSERVATION_TO_SOURCE_CROSSWALK.csv) | 2.0 | 54 | `cbef95330258b4351cf320763df3c65fe17159eb25de282b6d18abf8071273db` | Provenance Crosswalk | `VERIFIED_PRESENT` |
| [ENTITY_RESOLUTION_CONFUSION_MATRIX.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2_1/ENTITY_RESOLUTION_CONFUSION_MATRIX.csv) | 2.0 | 17 | `1c065ef43eb8de8c8347f5446b25262a107c839af84e15253c89789f4a4d6c90` | Statistical Benchmark | `VERIFIED_PRESENT` |
| [employer_resolution_confusion_matrix.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2_3/employer_resolution_confusion_matrix.csv) | 2.1 | 9 | `c41356138dcef0c199c0800d16dc9f6a466c37ca28217597b6153912b98d506c` | Statistical Benchmark | `VERIFIED_PRESENT` |
| [skill_extraction_benchmark.csv](file:///./docs/jobintel_v2/sprints/sprint_3b_3_2_3/skill_extraction_benchmark.csv) | 2.1 | 20 | `ebe55a411736251f9700581fcb0bb22ea86eba2f802435a6dd77f28ea0974df4` | Guardrail Unit Benchmark | `VERIFIED_PRESENT` |
| [artifact_manifest.json](file:///./src/backend/config/artifact_manifest.json) | 2.0 | 1 | `ca7054373a0e7e2618207da86248fe170f1fe5c61ca620b063431c6fb12b0d8d` | System Configuration | `VERIFIED_PRESENT` |
| [revocation_manifest.json](file:///./src/backend/config/revocation_manifest.json) | 2.0 | 1 | `702d949164da58f7e06614fcb42fd9a41d968f6461196ea9d75ce503f5c371ce` | System Configuration | `VERIFIED_PRESENT` |

---

## 3. Preliminary Forensic Observations

1. **Clean Worktree & Frozen Master:** The audit executed under strict read-only constraints. Production master commit `198b79dcdff08a5be5f08847c4262d31a3ce261e` remains completely isolated.
2. **Empty Registry Baseline:** Backend file `src/backend/employers/registry.py` instantiates an empty registry `_registry = EmployerRegistry(())`. No employer records currently exist in staging or production memory.
3. **Historical Data Integrity:** All 16 primary historical files were located and successfully fingerprinted with SHA-256 hashes.
4. **Delimitation Flaws Discovered:** Formatting anomalies (unquoted comma fields and blank separator rows) were forensically detected in `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_candidate_register.csv` and `docs/jobintel_v2/sprints/sprint_3b_3_2_3/skill_extraction_benchmark.csv`. These did not prevent programmatic inspection but represent data governance defects documented in Phase 2 and Phase 6.
