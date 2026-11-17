# SPRINT 3B.3.2.1 — DELIVERABLE 2
# ARTIFACT INVENTORY AND HASH AUDIT
## Physical Presence Verification, Cryptographic Hashing & Artifact Register

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Principal Data Auditor, QA Lead  
**Audit Target Directory:** `docs/jobintel_v2/sprints/sprint_3b_3_2/`  

---

## 1. INVENTORY VERIFICATION SUMMARY

A physical filesystem audit was conducted on every claimed artifact from Sprint 3B.3.2.

- **Claimed Reports in Sprint 3B.3.2 Final Report:** 16 Markdown deliverables.
- **Physically Found Reports:** 16 Markdown deliverables (**100% Present**).
- **Claimed Data Artifacts in Sprint 3B.3.2 Final Report:** 9 data artifacts.
- **Physically Found Data Artifacts:** 9 data artifacts (**100% Present**).
- **Total Files Audited:** **25 files**.

```
+----------------------------------------------------------------------------------------------------+
| ARTIFACT INVENTORY VERIFICATION SUMMARY                                                            |
+--------------------------+-----------------------+-----------------------+-------------------------+
| Category                 | Claimed in Report     | Physically Verified   | Verification Status     |
+--------------------------+-----------------------+-----------------------+-------------------------+
| Markdown Audit Reports   | 16 documents          | 16 documents          | PASS — 100% Present     |
| Structured JSON Datasets | 6 datasets            | 6 datasets            | PASS — 100% Present     |
| Structured CSV Datasets  | 3 datasets            | 3 datasets            | PASS — 100% Present     |
| Benchmark Gold Sets      | 2 benchmark files     | 2 benchmark files     | PASS — 100% Present     |
| Total Physical Artifacts | 25 files              | 25 files              | PASS — FULL RECONCILIATION
+--------------------------+-----------------------+-----------------------+-------------------------+
```

---

## 2. COMPLETE PHYSICAL ARTIFACT REGISTER

Every file was inspected directly, and its SHA-256 digest, byte size, file type, and Git tracking status were recorded.

The structured CSV export is saved at:  
[ARTIFACT_HASH_REGISTER.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2_1/ARTIFACT_HASH_REGISTER.csv)

### 2.1 Sprint 3B.3.2 Markdown Reports (16 Files)

| File Name | Byte Size | SHA-256 Digest (Truncated) | Git Tracking Status | Content Audit |
| :--- | :--- | :--- | :--- | :--- |
| `PREFLIGHT_AND_REPOSITORY_BASELINE.md` | 6,346 | `21e88e355977925c2759e663da59f776269df1fa33f389360980aa8a2212f718` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_COHORT_SELECTION.md` | 11,384 | `a9ca907e9c4a27c9569b91e13ba9b6e8fead1544869c9b19dfb48c2c1da039a3` | Untracked (Staging Working Copy) | Verified |
| `SOURCE_QUALIFICATION_REGISTER.md` | 13,572 | `f826f82e81e02ae07fa82ca23d778347f77b738a1a3e81fc0693a32f6a9c1be7` | Untracked (Staging Working Copy) | Verified |
| `FIVE_MARKET_DATA_ACQUISITION_REPORT.md` | 10,101 | `840d5134ddb32b814a0f4433a0bcf4769062088f17bc1dbd75ff38cf662111fe` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_PILOT_DATA_DICTIONARY.md` | 10,813 | `fd61757ea133b2713f0ae9c2e0bb1d0c4ca778cf84050f28249bf55d5bb2bb98` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_ENTITY_RESOLUTION_PILOT.md` | 5,968 | `b218d9e6ae9a067d2fe919a32c2538965a36398b1ecf20a672921206f4044ff0` | Untracked (Staging Working Copy) | Verified |
| `ENTITY_RESOLUTION_EVALUATION.md` | 6,821 | `0950dca8f58bc94386b0369a0391a27df0b7405e3a8fa6a8f34185265ecb5c49` | Untracked (Staging Working Copy) | Verified |
| `JOB_TITLE_MAPPING_PILOT.md` | 4,535 | `2a172a714c3b502ea8148b61c9441f92e4e138a379dbdd8b11a9eb482eb5847e` | Untracked (Staging Working Copy) | Verified |
| `SKILL_EXTRACTION_EVALUATION.md` | 5,626 | `0529af81df0f29d20c4c478a0c20a9696b025f18ee08537dbd1112bc556e4210` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_DATA_QUALITY_REPORT.md` | 5,546 | `8a7a0054948858c359bb29cf8534882dfba81e7d23d9b4db7d59fe5ba1a5e12f` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_PROVENANCE_AUDIT.md` | 5,470 | `0580b03eb03799890a8a65842c943147ca481977fe49b29ecdb804f8f3c77b49` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_STORAGE_MEMORY_BENCHMARK.md` | 10,967 | `eb5ec3862b49c57e6c92d53bfd12f3e820c754d9241951591c2b53b8114f828a` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_MVP_PRODUCT_VALIDATION.md` | 11,063 | `5944593f4b077effaa0db6ca38dd907ce7ec22495b45a0b779a83eb3389659b6` | Untracked (Staging Working Copy) | Verified |
| `FIVE_MARKET_EMPLOYER_COVERAGE_MATRIX.md` | 10,613 | `a24d18eb11f39fc2e6a9f4ca3df68c2dca11e6d8a39d8e5e89d18b248a398f62` | Untracked (Staging Working Copy) | Verified |
| `EMPLOYER_PILOT_RISK_REGISTER.md` | 10,400 | `eafe616bfbaa18903332fe0fc1665aebcf8f7f0c1a2f9ec67b1cb4ecfefc5a04` | Untracked (Staging Working Copy) | Verified |
| `SPRINT_3B3_2_FINAL_AUDIT_REPORT.md` | 19,194 | `ffd956f712c49bfeb3eeb2951052c92557c5bf333a9ec11e4f9b88cf2e176b6b` | Untracked (Staging Working Copy) | Verified |

### 2.2 Sprint 3B.3.2 Data Artifacts (9 Files)

| File Name | Byte Size | SHA-256 Digest | Records Contained | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| `employer_candidate_register.csv` | 12,552 | `2d59d2645826d3f9f8e4e9f73315a6e8df8fc8774775d713919e99a4c0eb305c` | 45 candidates | Verified Complete |
| `employer_source_catalog.json` | 16,211 | `db1f6203e201f4d01b1cb407c086d061f185ef3571d798ca74d17dbb9e6f3ebc` | 14 source definitions | Verified Valid JSON |
| `employer_pilot_records.json` | 28,198 | `6689d608c996ce1ebbbdf988995a9477bcf7047814b7e9ee063251268b8b0934` | 28 anchor employers | Verified Valid JSON |
| `employer_pilot_records.csv` | 7,956 | `fc32442686ca4d7d31b67664e7c3ee1c742fa7aa43b179374ee48d56353d7f95` | 28 anchor employers | Verified 1:1 Parity |
| `employer_hiring_observations.json` | 21,573 | `1712946b10d5b7f4be47565c52c2df6d4fcb4369796078ef3c9907beab2a3c74` | 32 observations | Verified Valid JSON |
| `employer_skill_observations.json` | 10,956 | `d33255094ae970c2ce0e633d7d741cb30058b725c4efcf9163e77a28e83b4c6e` | 22 skill requirements| Verified Valid JSON |
| `employer_evidence_ledger.csv` | 3,194 | `f9ff9b3247786c72e25eaeb604467ecbcabdc0b18128eeffea79a83d735071df` | 8 audit records | Verified Valid CSV |
| `employer_entity_resolution_gold.json` | 36,409 | `d53cf59b756abe16adfc85a9bc662580556db1e36780c7a5f6e632cb7c251fc4` | 100 labeled pairs | Verified Valid JSON |
| `job_title_mapping_gold.json` | 24,918 | `ef161e37a8776f874c7689104085424cf374ffbe68c56fa769f44ba625299e4b` | 100 labeled titles | Verified Valid JSON |

---

## 3. AUDIT FINDINGS ON PHYSICAL ARTIFACTS

1. **Existence Confirmed:** All 25 claimed artifacts exist on the filesystem. No artifact was fabricated in name or missing.
2. **Cryptographic Baseline Established:** Full SHA-256 hashes are recorded in `ARTIFACT_HASH_REGISTER.csv`.
3. **Important Distinction:** As mandated by the audit directive, cryptographic hashes verify file integrity and bit-level preservation, but do **not** constitute proof of source authenticity, legal license authorization, or factual correctness. Those dimensions are forensically examined in Phases 2 through 10.
