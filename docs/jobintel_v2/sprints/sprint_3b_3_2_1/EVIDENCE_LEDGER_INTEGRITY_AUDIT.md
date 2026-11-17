# SPRINT 3B.3.2.1 — DELIVERABLE 8
# EVIDENCE LEDGER INTEGRITY AUDIT
## Forensic Verification of Cryptographic Hashes, Coverage Scope & Audit Limitations

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Principal Data Auditor, Cryptographic & Governance Specialist  
**Artifact Under Audit:** `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_evidence_ledger.csv`  

---

## 1. EVIDENCE LEDGER INSPECTION & STRUCTURAL FINDINGS

The Sprint 3B.3.2 evidence ledger contains exactly **8 cryptographic audit records**.

An independent audit was conducted to answer the seven critical questions mandated in Phase 7:

```
+----------------------------------------------------------------------------------------------------+
| EVIDENCE LEDGER FORENSIC AUDIT QUESTIONS & FINDINGS                                                |
+----+---------------------------------------------------+--------------------+----------------------+
| #  | Forensic Audit Question                           | Audit Finding      | Severity / Status    |
+----+---------------------------------------------------+--------------------+----------------------+
| 1  | What exactly is hashed in the evidence ledger?    | Primary Source File| Raw statutory docs   |
| 2  | Are hashes for raw files or derived records?      | Raw source files   | Source-level hashes  |
| 3  | Are all 28 employer profiles covered?             | PARTIAL (Bulk/Doc) | 4 bulk + 4 single doc|
| 4  | Are all 32 hiring observations covered?           | INDIRECT ONLY      | Sourced via snapshots|
| 5  | Are all 22 skill observations covered?            | NOT COVERED        | ATS feeds not hashed |
| 6  | Can hashes be independently validated?            | YES (On snapshots) | Valid SHA-256 digests|
| 7  | Is claim of "complete record-level hash" verified?| NOT VERIFIED       | OVERSTATED IN REPORT |
+----+---------------------------------------------------+--------------------+----------------------+
```

---

## 2. RECORD-BY-RECORD ANALYSIS OF THE 8 EVIDENCE LEDGER ENTRIES

| Evidence ID | Scope / Target Company | Source System | Statutory Citation | SHA-256 Checksum (Truncated) | Coverage Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `evi_wgea_2024` | `ALL_AU_QUALIFIED` | WGEA Data Explorer | Workplace Gender Equality Act 2012 s 13 | `b520da023479e184...` | Bulk Market Snapshot (AU Headcount Bands) |
| `evi_abr_bulk_2026` | `ALL_AU_QUALIFIED` | Australian Business Register| A New Tax System (ABN) Act 1999 | `c8d70db19e38096c...` | Bulk Market Snapshot (AU Corporate Entities) |
| `evi_sec_10k_msft_2024`| `comp_us_microsoft` | SEC EDGAR | 17 CFR § 229.101 (Item 101) | `5c9ee2674ee5fc1d...` | Single Statutory 10-K Document (Microsoft) |
| `evi_sec_10k_goog_2023`| `comp_us_alphabet` | SEC EDGAR | 17 CFR § 229.101 (Item 101) | `51196b22cc8e6bd1...` | Single Statutory 10-K Document (Alphabet) |
| `evi_uk_gpg_2024` | `ALL_UK_QUALIFIED` | UK Gender Pay Gap | Equality Act 2010 Regulations 2017 | `11e9860f2aade594...` | Bulk Market Snapshot (UK Headcount Bands) |
| `evi_ch_deepmind_2023` | `comp_uk_deepmind` | Companies House | Companies Act 2006 s 411 | `9d00027d6845f612...` | Single Statutory Filing Document (DeepMind) |
| `evi_sebi_brsr_tcs_2024`| `comp_in_tcs` | SEBI / BSE Portal | SEBI LODR Regulation 34(2)(f) | `c055a976a85c4e69...` | Single Integrated Annual Report (TCS) |
| `evi_acra_entities_2026`| `ALL_SG_QUALIFIED`| ACRA via data.gov.sg| ACRA Act (Cap. 2A) | `b3a70d1eff38384e...` | Bulk Market Snapshot (SG Registered UENs) |

---

## 3. INDEPENDENT AUDITOR DISCOVERY: SCOPE OVERSTATEMENT

### The Defect Identified in Previous Reporting
Sprint 3B.3.2 claimed:
> *"Cryptographic SHA-256 evidence ledger verifies complete provenance and reproducibility across all 28 anchor employers and observations."*

### The Forensic Reality
1. **The Ledger is a Source Document Catalog, not a Row-Level Ledger:**
   - 4 entries are bulk government registry datasets covering hundreds of thousands of companies in Australia, the UK, and Singapore (`ALL_AU_QUALIFIED`, `ALL_UK_QUALIFIED`, `ALL_SG_QUALIFIED`).
   - 4 entries are single PDF/HTML filing documents for specific anchor corporations (Microsoft, Alphabet, DeepMind, TCS).
2. **Missing Record-Level Hashes:**
   - The remaining 24 individual employer records (e.g. Canva, CBA, BHP, Pfizer, Cisco, Barclays, Unilever, Grab, Shopee, Infosys, Wipro, Reliance) do **not** have individual document hashes in `employer_evidence_ledger.csv`.
   - None of the 22 skill requirements extracted from ATS feeds have corresponding SHA-256 payloads in the ledger.
3. **Audit Assessment:**
   The hashes recorded in `employer_evidence_ledger.csv` are genuine, authentic SHA-256 digests of the underlying statutory source files. However, claiming that this ledger represents complete record-level cryptographic immutability across every profile and observation is **factually overstated**.

---

## 4. CORRECTIVE RECOMMENDATION FOR SPRINT 3B.3.3

To achieve true, unchallengeable cryptographic provenance in Sprint 3B.3.3:
1. **Dual Ledger Architecture:**
   - **Tier 1 (Source Ledger):** Maintain SHA-256 digests of raw downloaded bulk files and statutory PDFs (current approach).
   - **Tier 2 (Entity Mutation Ledger):** Generate deterministic SHA-256 hashes of canonical serialized JSON payloads for every individual profile (`employer_id`) and observation (`observation_id`).
2. **Provenance Disclosure:**
   In the user-facing Provenance Drawer, cite the Tier 1 statutory document reference and display the Tier 2 record hash for data integrity verification.
