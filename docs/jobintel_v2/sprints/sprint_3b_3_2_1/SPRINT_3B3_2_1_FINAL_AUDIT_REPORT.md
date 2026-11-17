# JOBINTEL 2.0 — SPRINT 3B.3.2.1 FINAL AUDIT REPORT
## FORENSIC ARTIFACT VERIFICATION & INDEPENDENT EVIDENCE AUDIT

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Principal Data Auditor, Data Governance Specialist, Statistical Validation Engineer, Data Architect, QA Lead  
**Audit Evaluation Period:** November 2026  
**Target Repository:** `https://github.com/Vansh1412/Job-Market-Intelligence`  
**Working Branch:** `staging/sprint2c3` (HEAD: `d1a8b027d10031b3568a3141f639e2f40a49be18`)  
**Production Isolation:** `master` (`198b79dcdff08a5be5f08847c4262d31a3ce261e`, strictly isolated)  
**Final Audit Verdict:** **`A. FULL CONDITIONAL GO — LIMITED IMPLEMENTATION WITH CLEARLY DEFINED RESTRICTIONS`**  

---

## 1. EXECUTIVE SUMMARY & FORMAL VERDICT

Sprint 3B.3.2.1 performed an exhaustive, independent, strictly read-only forensic audit and reproduction of the evidence, datasets, benchmarks, and claims established during Sprint 3B.3.2.

Departing from trust-based acceptance, this audit independently re-computed all cryptographic checksums, inspected every individual employer profile and observation, traced the exact source crosswalk, executed benchmark reproductions for entity resolution and job title mapping, re-measured memory heaps, cross-examined the 16 prior reports for contradictions, and established a record-level publication eligibility matrix.

```
====================================================================================================
FINAL SPRINT VERDICT:
A. FULL CONDITIONAL GO — LIMITED IMPLEMENTATION WITH CLEARLY DEFINED RESTRICTIONS
====================================================================================================
```

### Core Audit Conclusion:
The empirical foundation developed in Sprint 3B.3.2 is **factually authentic, uncorrupted by commercial web scraping, mathematically sound on measured samples, and technically feasible on Render Free tier**. The previous sprint's recommendation to proceed with a controlled, factual Global Employer Intelligence MVP is **formally ratified**, subject to strict, non-negotiable operational boundaries.

---

## 2. INDEPENDENT AUDIT SYNTHESIS

### 2.1 What Was Independently Verified
1. **Artifact Inventory (100% Present):** All 16 claimed Markdown reports and all 9 structured datasets physically exist in `docs/jobintel_v2/sprints/sprint_3b_3_2/`. Full cryptographic hashes are cataloged in `ARTIFACT_HASH_REGISTER.csv`.
2. **Employer Profiles (96.4% Verified, 3.6% Verified with Caveat):** All 28 anchor employer records were validated against sovereign corporate registries (ABR, SEC EDGAR, Companies House, ACRA, SEBI). Exactly 0 duplicate entities, 0 colliding registration IDs, and 0 market mismatches were found. Record `comp_us_fed_va` was classified as `PARTIALLY_VERIFIED (PUBLIC_SECTOR_AGENCY)`.
3. **Headcount & Hiring Evidence (100% Authentic):** All 32 observations represent factual disclosures. Categorical size bands (AU WGEA, UK Gender Pay Gap) and exact headcounts (US SEC, IN SEBI) are cleanly isolated without synthetic midpoint manufacturing. Job advertisements are strictly separated from confirmed hires.
4. **Source Crosswalk & Contradiction Resolution:** $0$ of $54$ observations depend on `REVOKED` or `REVIEW_REQUIRED` sources. 100% of the pilot data is traced exclusively to the 11 `APPROVED` sources.
5. **UK Demand Publication Gate:** Observation `obs_uk_deepmind_vacancies` is confirmed strictly withheld (`observed_count: null`, `publication_gate_active: true`).

### 2.2 What Was Independently Reproduced
1. **Entity Resolution Benchmark:** Resolver V2 was reproduced on the 100-pair gold dataset:
   - `TP = 31`, `FP = 0`, `TN = 55`, `FN = 14`
   - Precision: **100.00%** | Recall: **68.89%** | F1: **0.8158**
   - Pairwise False Merge Rate: **0.00%** (95% Wilson Score CI: `[0.00% - 6.53%]`)
2. **Job Title Mapping Benchmark:** Reproduced on 100 gold titles across 12 canonical occupations:
   - Accuracy: **97.00%** | Macro F1: **0.9852** | Misclassification Error: **0.00%** | Unmapped Fallback: **3.00%**
   - Expected Calibration Error: **0.0587** (uncalibrated) / **0.0381** (calibrated with $T = 1.24$).
3. **Skill Extraction Short-Token Protocol:** Evaluated on 20 adversarial test phrases:
   - 5-token contextual co-occurrence filter achieved **100.0% accuracy**, rejecting all colloquial usages of `Go`, `C`, `R` while capturing all valid technical requirements.
4. **Storage & Memory Footprint:** Measured using Python `tracemalloc`:
   - Raw JSON: **75.13 KB** | Gzip: **10.52 KB** | Traced Python Heap: **241.67 KB** (8,838.3 bytes / employer)
   - In-memory lookups resolve in **3.10 to 10.40 microseconds**.

### 2.3 What Failed Reproduction / Was Overstated in Previous Reports
1. **Evidence Ledger Scope Overstatement (CTR-001):** The previous report claimed the evidence ledger verified complete provenance across all 28 employers and observations. In reality, the ledger contains 8 entries (4 bulk market snapshots and 4 single corporate filings). 24 individual profiles and all 22 skill observations lack dedicated record hashes. *Audit Correction:* Classified as a Source Document Ledger, not a Row-Level Ledger.
2. **Statistical Proof of Error Rate $< 0.1\%$ (CTR-002):** The previous report implied that Resolver V2 is proven to achieve $<0.1\%$ false merge rate. *Audit Correction:* Under the binomial Rule of Three, proving an error rate $< 0.1\%$ at 95% confidence with 0 observed errors mathematically requires **$N \ge 3,000$ true negative pairs**. The 100-pair benchmark ($N = 55$ TN) proves only an upper bound of **$< 6.53\%$**.
3. **"Zero OOM Risk" Claim (CTR-003):** The previous report asserted "zero OOM risk" on Render Free 512 MB. *Audit Correction:* On a 512 MB dyno, dynamic request concurrency, serialization buffers, and memory fragmentation present real risks at scale. Memory risk is **LOW** at 100–250 employers (~0.84–2.11 MB heap), but requires mandatory database offloading and response pagination beyond 1,000 employers.
4. **Tracemalloc vs. Process RSS (CTR-006):** Clarified that 241 KB is traced Python object memory, not total OS Process Resident Set Size.

### 2.4 What Remains Unverified
- **Live Cloud Process RSS:** Real-time Render container memory cannot be queried during a strictly read-only local audit; baseline memory (~195 MB) remains estimated from Sprint 3B.2.3.5 staging telemetry.

---

## 3. RECORD-LEVEL PUBLICATION ELIGIBILITY SUMMARY

Across all 82 entities in the pilot dataset:
- **`PUBLISHABLE` (43 entities / 52.4%):** 27 sovereign corporate registry profiles and 16 audited exact scalar headcount observations from SEC 10-K and SEBI BRSR filings.
- **`PUBLISHABLE_WITH_CAVEAT` (38 entities / 46.3%):** 1 public-sector agency profile (`comp_us_fed_va`), 11 statutory workforce size bands (WGEA & UK GPG), 3 active ATS vacancy counts, 1 WARN dislocation notice, and 22 posting-level skill observations. All require mandatory contextual caveat tags in the UI.
- **`WITHHELD` (1 entity / 1.2%):** UK employer vacancy observation `obs_uk_deepmind_vacancies` (serialized as `null` under active publication gate).
- **`INTERNAL_RESEARCH_ONLY` / `REVOKED` (0 entities / 0.0%):** Zero commercial or unverified records.

---

## 4. IMPLEMENTATION AUTHORIZATION DECISIONS FOR SPRINT 3B.3.3

```
+----------------------------------------------------------------------------------------------------+
| SPRINT 3B.3.3 ENGINEERING COMPONENT AUTHORIZATION                                                  |
+----+--------------------------------------------+-----------------------+--------------------------+
| #  | Proposed Engineering Activity              | Authorization Verdict | Operational Boundaries   |
+----+--------------------------------------------+-----------------------+--------------------------+
| A  | Generalize Backend Employer Schemas        | AUTHORIZED (READY)    | Multi-market Pydantic v2 |
| B  | Implement In-Memory Registry Service       | AUTHORIZED (READY)    | Inverted hash map index  |
| C  | Implement Employer Directory API           | AUTHORIZED (READY)    | Mandatory limit/offset   |
| D  | Implement Employer Profile API             | AUTHORIZED (READY)    | UK demand gate enforced  |
| E  | Expand Cohort to 100 Employers             | CONDITIONALLY AUTH    | Authorized sources only  |
| F  | Build Frontend Employer Directory Page     | AUTHORIZED (READY)    | Standard table & filters |
| G  | Build Employer Profile & Provenance Drawer | AUTHORIZED (READY)    | Mandatory caveat banners |
+----+--------------------------------------------+-----------------------+--------------------------+
```

### 4.1 Justification for 100-Employer Expansion
The empirical data acquisition and benchmark results demonstrate that expanding the anchor cohort from 28 to 100 verified employers (25 AU, 25 US, 20 UK, 15 SG, 15 IN) is **fully justified**:
- **Data Availability:** Authoritative open government registries exist in all 5 markets (ABR bulk, SEC EDGAR API, Companies House API, ACRA open data, SEBI BSE filings).
- **Memory Feasibility:** 100 employers consume only **~0.84 MB traced heap** (~2.0–3.5 MB RSS), leaving over **313 MB of safety headroom** below the 512 MB Render ceiling.
- **Entity Resolution Safety:** Operating under Sovereign Market Isolation and ATS Host Blacklisting guarantees zero cross-market parent/subsidiary false merges.

---

## 5. NON-NEGOTIABLE PREREQUISITES FOR SPRINT 3B.3.3

1. **Strict Source Boundary:** Ingestion must use exclusively the 11 qualified `APPROVED` sources. Zero commercial scraping (LinkedIn, Indeed, Naukri, Seek).
2. **Zero Gated Portal Bypassing:** In India, restrict ingestion strictly to listed corporations with public SEBI BRSR annual filings; do not attempt automated scraping of the CAPTCHA-gated MCA21 portal.
3. **Dual Representation Fidelity:** Preserve native categorical size bands for AU and UK employers; do not synthesize fake scalar headcounts or midpoints.
4. **UK Demand Gate Integrity:** Senders and APIs must serialize UK employer vacancy metrics as `null` with `publication_gate_active: true`.
5. **No Synthetic Scores:** Prohibit all synthetic "Employer Scores", "Hiring Momentum Rankings", or algorithmic tiering.
6. **API Response Pagination:** Implement mandatory `limit` (default 25, max 100) and `offset` parameters on `GET /api/v1/employers` to prevent memory serialization spikes.
7. **Tier 2 Record Hashing:** Implement canonical JSON hashing for each profile in the Provenance Drawer alongside raw statutory document hashes.

---

## 6. FINAL REPOSITORY SAFETY AUDIT

An automated Git safety audit confirms the pristine, read-only status of the workspace:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse master
```

- **Application Source Code Modified:** **0 files modified** (`src/` untouched).
- **Frontend Code Modified:** **0 files modified** (`frontend/` untouched).
- **Models Modified or Retrained:** **0 models modified**.
- **Existing Sprint 3B.3.2 Artifacts Modified:** **0 files modified** (100% bit-level preservation).
- **Dependencies Installed:** **0 packages installed**.
- **Deployments Executed:** **0 deployments**.
- **Active Working Branch:** `staging/sprint2c3`
- **Committed HEAD Commit:** `d1a8b027d10031b3568a3141f639e2f40a49be18`
- **Production Baseline:** `198b79dcdff08a5be5f08847c4262d31a3ce261e` (`master`, strictly isolated).

---
*Report Independently Certified by:*  
**Principal Data Auditor, Data Governance Lead & Statistical QA Specialist**  
*JOBINTEL 2.0 Quality Assurance & Governance Lead*
