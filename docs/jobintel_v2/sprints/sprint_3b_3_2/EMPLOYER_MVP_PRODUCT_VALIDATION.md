# SPRINT 3B.3.2 — DELIVERABLE 13
# EMPLOYER MVP PRODUCT VALIDATION
## Module-by-Module Qualification of the Global Employer Intelligence Feature Set

---

## 1. EXECUTIVE OVERVIEW

This document presents the product-level qualification of the six proposed Employer Intelligence modules against the empirical evidence gathered during the Sprint 3B.3.2 five-market data acquisition pilot.

The qualification evaluates whether each module can be implemented honestly, accurately, and without misleading users, fabricating data, or breaching corporate terms of service.

```
+----------------------------------------------------------------------------------------------------+
| MODULE READINESS QUALIFICATION SUMMARY                                                             |
+----------+--------------------------------+--------------------+-----------------------------------+
| Module   | Product Capability             | Readiness Verdict  | Critical Governance Constraints   |
+----------+--------------------------------+--------------------+-----------------------------------+
| Module A | Employer Directory & Search    | READY              | Inverted index, domain lookup     |
| Module B | Employer Profile & Hierarchy   | READY              | Dual headcount, sovereign IDs     |
| Module C | Hiring Intelligence (Stock/Flow| LIMITED / CONDITIONAL| Stock certified; flow ATS-only  |
| Module D | Skills & Qualifications        | LIMITED / CONDITIONAL| Posting-level; sample size tag  |
| Module E | Employer Comparison            | LIMITED / CONDITIONAL| Strict pairwise; NO scores/ranks|
| Module F | Employer Geographic Map        | DEFERRED           | Metro hubs only; no pin mapping   |
+----------+--------------------------------+--------------------+-----------------------------------+
```

---

## 2. MODULE-BY-MODULE DETAILED AUDIT

### 2.1 Module A: Employer Directory & Search

**Product Scope:** Searchable directory allowing users to discover employers across five markets by name, domain, industry sector, headquarters country, and establishment size band.

- **Empirical Evidence Supporting Capability:**
  - Pilot dataset contains 28 anchor employers with 100% verified identifiers, standardized industry classifications (ANZSIC, NAICS, UK SIC, SSIC, NIC), and primary domains.
  - Sub-microsecond query latency achieved via in-memory inverted hash maps (`p50 = 3.10 µs` for ID lookup, `p50 = 3.20 µs` for domain lookup, `p50 = 10.40 µs` for market/industry filter).
- **Search Determinism & Reproducibility:**
  - Search results are strictly deterministic and based on exact or tokenized prefix matching against legal names, trading names, and registered domains. Zero fuzzy hallucination or black-box re-ranking.
- **Identified Limitations:**
  - Searching by fuzzy typos requires an explicit phonetic or Levenshtein index (e.g. `RapidFuzz`) capped at a similarity threshold $\ge 0.85$ to prevent false entity collisions.
- **Module Readiness Verdict:** **`READY`**.

---

### 2.2 Module B: Employer Profile & Corporate Structure

**Product Scope:** Comprehensive profile page presenting verified corporate identity, legal entity name, trading name, statutory registration identifier (ABN, CIK, UEN, CIN, Company Number), corporate hierarchy (parent/subsidiary), industry classification, and operating markets.

- **Empirical Evidence Supporting Capability:**
  - All 28 anchor records include primary legal entity names, verified registration identifiers, statutory authority citations, and operating market arrays.
  - Parent/subsidiary relationships are formally mapped (e.g. `EMP_AU_003` Canva Pty Ltd $\to$ `EMP_AU_003` Canva Group; `EMP_US_001` Google LLC $\to$ `EMP_US_001_P` Alphabet Inc.).
  - Dual headcount model accurately displays both categorical size bands (e.g. WGEA `"5000+"`) and verified scalar headcounts (e.g. SEC 10-K `182,502`).
- **Data Governance Integrity:**
  - Every profile features a dedicated "Data Provenance" drawer detailing the primary statutory source, last verification timestamp, and license citation.
- **Identified Limitations:**
  - Global parent/subsidiary mappings are limited to public disclosures; private corporate subsidiaries without public registry filings cannot be resolved.
- **Module Readiness Verdict:** **`READY`**.

---

### 2.3 Module C: Hiring Intelligence (Stock vs. Flow)

**Product Scope:** Analysis of an employer's workforce dynamics, comparing overall workforce size (stock) with current open hiring demand (flow).

- **Empirical Evidence Supporting Capability:**
  - Pilot dataset contains 32 verified statutory headcount observations (stock) from WGEA, SEC 10-K, UK Gender Pay Gap, SG MOM, and SEBI BRSR.
  - Active hiring vacancy volume (flow) is acquired exclusively from direct, authorized employer ATS endpoints (Greenhouse, Lever, Workday) and statutory vacancy releases.
- **Stock vs. Flow Semantic Distinction:**
  - The UI contract strictly isolates:
    - **Workforce Headcount (Stock):** "Verified establishment workforce at fiscal year-end."
    - **Open Vacancies (Flow):** "Unfilled job openings posted on official careers portal as of observation date."
  - Absolute prohibition on equating open job postings with net new job creation or verified hires.
- **UK Publication Gate Compliance:**
  - UK employer demand flow is serialized as `null` with `publication_gate_active: true` and the statutory disclaimer: *"UK vacancy flow data withheld pending source-use review."* Statutory headcount (Gender Pay Gap size band) remains accessible.
- **Identified Limitations:**
  - Vacancy flow is only available for employers publishing direct ATS feeds. For employers without open ATS feeds, vacancy flow displays *"No active public vacancy feed verified."*
- **Module Readiness Verdict:** **`LIMITED / CONDITIONAL`** (Stock certified across 100% of cohort; Flow restricted to employers with authorized public ATS feeds; UK demand gate strictly enforced).

---

### 2.4 Module D: Skills & Qualifications Intelligence

**Product Scope:** Identification of key technical and domain skills requested by employers across the 12 canonical occupations.

- **Empirical Evidence Supporting Capability:**
  - 22 skill requirements analyzed from official job postings across technology, financial, and engineering employers.
  - Tested against the 5-token contextual co-occurrence protection protocol for ambiguous short tokens (`Go`, `C`, `R`, `SQL`, `AWS`, `ML`, `AI`).
- **Sample Size Transparency:**
  - Posting-level aggregation requires mandatory display of the sample size: *"Based on N = 14 verified job postings observed between [Start Date] and [End Date]."*
  - Sweeping corporate-wide claims (e.g. *"Google primarily hires Python engineers"*) are programmatically barred.
- **Identified Limitations:**
  - Skill demand reflects hiring specifications in active requisitions, not the internal skill inventory of existing tenured staff.
- **Module Readiness Verdict:** **`LIMITED / CONDITIONAL`** (Posting-level observations certified; aggregate claims prohibited; sample size tags mandatory).

---

### 2.5 Module E: Employer Comparison

**Product Scope:** Side-by-side comparison of 2–3 selected employers across verified statutory attributes.

- **Empirical Evidence Supporting Capability:**
  - Pairwise comparison supported across standardized dimensions: headquarters country, industry classification, establishment size band, operating markets, and verified job postings by canonical occupation.
- **Restriction to Compatible Metrics:**
  - Cross-market headcount comparisons strictly respect measurement boundaries (e.g., comparing an SEC exact headcount with a WGEA size band presents each in its native format rather than synthesizing a fraudulent scalar).
- **Prohibition on Synthetic Scores & Rankings:**
  - **Zero synthetic ranking, "Employer Score", or "Hiring Momentum Index".**
  - No algorithmic ordering that implies one employer is "better" or "faster growing" without verified longitudinal census data.
- **Module Readiness Verdict:** **`LIMITED / CONDITIONAL`** (Side-by-side display of compatible factual metrics certified; synthetic scores permanently excluded).

---

### 2.6 Module F: Employer Geographic Footprint / Map

**Product Scope:** Geographic visualization of an employer's headquarters and operational branch locations.

- **Empirical Evidence Supporting Capability:**
  - Corporate registries provide registered office addresses and principal operating cities (e.g., Sydney, Mountain View, London, Singapore, Mumbai).
- **Geocoding & Precision Audit:**
  - Statutory addresses in public filings are frequently legal registered agent offices (e.g. Corporation Trust Center in Delaware) rather than actual engineering or operations centers.
  - Latitude/longitude coordinates are not provided by statutory registries. Dynamic geocoding of commercial branch offices introduces unverified third-party assumptions and potential PII exposure.
- **Module Readiness Verdict:** **`DEFERRED`**.
  - **Action:** Defer interactive pin-based geographic mapping. For MVP, represent geographic footprint as a verified textual list of metropolitan hubs and sovereign operating markets (e.g. *"Operational Presence: Australia (Sydney, Melbourne), United States (San Francisco)"*).

---

## 3. OVERALL MVP READINESS SUMMARY

```
+----------------------------------------------------------------------------------------------------+
| INTEGRATED MVP FEATURE READINESS MATRIX                                                            |
+--------------------------+--------------------+----------------------------------------------------+
| Feature Component        | Status             | Release Qualification Conditions                   |
+--------------------------+--------------------+----------------------------------------------------+
| Core Directory (A)       | QUALIFIED FOR MVP  | In-memory lookup, deterministic prefix search       |
| Verified Profile (B)     | QUALIFIED FOR MVP  | Provenance drawer, dual headcount, sovereign IDs   |
| Stock Headcount (C.1)    | QUALIFIED FOR MVP  | Statutory filings only, explicit fiscal year tag   |
| Flow Vacancies (C.2)     | RESTRICTED MVP     | Direct ATS feeds only; UK publication gate enforced|
| Skill Requirements (D)   | RESTRICTED MVP     | Posting-level tags; short-token filter; sample size|
| Pairwise Comparison (E)  | RESTRICTED MVP     | Factual metrics only; zero synthetic scores        |
| Interactive Map (F)      | EXCLUDED FROM MVP  | Deferred; textual metropolitan list only           |
+--------------------------+--------------------+----------------------------------------------------+
```

**Overall Product Architecture Decision:**
The core employer intelligence value proposition is sound, reproducible, and technically verified under a **Controlled Factual Architecture**. By eliminating synthetic scores and deferring brittle branch-level geocoding, JOBINTEL 2.0 can deliver an enterprise-grade, legally compliant employer intelligence product.
