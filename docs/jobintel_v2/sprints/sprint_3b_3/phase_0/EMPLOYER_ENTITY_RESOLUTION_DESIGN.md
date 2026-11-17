# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER ENTITY RESOLUTION & CORPORATE HIERARCHY DESIGN
### Multi-Tier Identity Matching, Corporate Disambiguation, Registry Crosswalking & Agency Filtering

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-ENTITY-RESOLUTION`  
**Execution Phase:** Phase 0 (Identity Resolution Architecture Audit)  
**Date of Audit:** 2026-11-17  
**Core Directive:** Name matching alone is strictly insufficient. Implement deterministic multi-tier resolution.

---

## 1. THE ENTITY AMBIGUITY CHALLENGE

In multi-market employer intelligence, corporate names are inherently ambiguous:
1. **Corporate Hierarchy Fragmentation:** A single global brand operates through dozens of distinct legal entities (e.g., `Alphabet Inc.` [US Holding CIK: `0001652044`], `Google LLC` [Delaware operating company], `Google UK Limited` [CRN: `03977902`], `Google India Private Limited` [CIN: `U72900KA2003PTC033028`], `Google Asia Pacific Pte. Ltd.` [Singapore UEN: `200817984R`]).
2. **Commercial Brands vs Legal Names:** Job seekers search for "Google", "Amazon", or "Microsoft", while job advertisements may be legally issued by "Google Operations LLC", "Amazon Data Services, Inc.", or "Microsoft Ireland Operations Limited".
3. **Third-Party Staffing Agency Conflation:** Recruitment agencies (e.g., Randstad, Adecco, Michael Page, TeamLease) advertise positions for clients without disclosing client identities, or using vague descriptors ("Leading multinational investment bank").
4. **Name Collisions Across Jurisdictions:** A local entity in Australia named "Mercury Technologies Pty Ltd" is legally and operationally distinct from "Mercury Technologies, Inc." in California.

> [!CRITICAL]
> **Definitive Rule:**  
> Company name matching alone is **scientifically and legally insufficient**. Automated fuzzy matching on raw strings produces unacceptable false-positive merges.

---

## 2. MULTI-TIER ENTITY RESOLUTION ARCHITECTURE

The JobIntel Entity Resolution Engine implements a **four-tier sequential matching pipeline**:

```
[Raw Ingested Employer Record]
              |
              v
+-----------------------------------------------------------+
| TIER 1: Deterministic National Registration Key Matching   |
| (Match on CIN, CIK, CRN, ABN, UEN)                        |
| -> Exact Match = 100% Deterministic (AUTO-VERIFIED)       |
+-----------------------------+-----------------------------+
                              | No match / Key absent
                              v
+-----------------------------------------------------------+
| TIER 2: Canonical Root Web Domain Resolution              |
| (Match on extracted root domain: e.g. 'stripe.com')       |
| -> Domain Match = 95% High Confidence (AUTO-VERIFIED)     |
+-----------------------------+-----------------------------+
                              | No domain / Unregistered
                              v
+-----------------------------------------------------------+
| TIER 3: Legal Name Normalization + Country Concordance    |
| (Regex suffix stripping, uppercase, Country constraint)   |
| -> Normalized Exact Match = 80% Medium (REVIEW_REQUIRED)  |
+-----------------------------+-----------------------------+
                              | Distance > 0
                              v
+-----------------------------------------------------------+
| TIER 4: Fuzzy String Similarity (Jaro-Winkler >= 0.92)    |
| -> NEVER AUTO-COMMITTED | Strict UNVERIFIED Review Queue  |
+-----------------------------------------------------------+
```

---

### Tier 1: Deterministic National Registration Key Matching (100% Precision)
- **Mechanism:** Direct cross-reference against authoritative national registries using official alphanumeric identifiers.
- **Identifiers by Market:**
  - **India (IN):** Corporate Identification Number (CIN) — 21-character alphanumeric code encoding listing status, 5-digit industry NIC, state, year of incorporation, and ROC registration number.
  - **United States (US):** Central Index Key (CIK) — 10-digit SEC code, and IRS Employer Identification Number (EIN).
  - **United Kingdom (UK):** Companies House Company Registration Number (CRN) — 8-character code (e.g. `00002065` or `SC123456`).
  - **Australia (AU):** Australian Business Number (ABN) — 11-digit unique identifier, or Australian Company Number (ACN) — 9 digits.
  - **Singapore (SG):** Unique Entity Number (UEN) — 9 or 10-character standard identification number.
- **Outcome:** If a matching key exists in the master registry, the entity is linked with **100% confidence** (`MATCH_TIER_1_STATUTORY_REGISTRATION`).

---

### Tier 2: Canonical Root Web Domain Resolution (95% Precision)
- **Mechanism:** In digital recruitment, job postings originate from or link to an official corporate domain (e.g., `careers.google.com/jobs`, `boards.greenhouse.io/stripe`, `jobs.lever.co/databricks`).
- **Domain Normalization Algorithm:**
  1. Extract hostname from job posting URL or applicant redirection URL.
  2. Strip protocol (`https://`), port, and `www.` prefixes.
  3. Resolve through Public Suffix List (PSL) to isolate the **registrable domain** (e.g. `careers.stripe.com` $\to$ `stripe.com`; `amazon.co.uk` $\to$ `amazon.co.uk`).
  4. Exclude generic ATS hosting domains (e.g., `greenhouse.io`, `lever.co`, `workday.com`, `smartrecruiters.com`, `myworkdayjobs.com`). For these platforms, extract the tenant slug token (`boards.greenhouse.io/{slug}` $\to$ lookup slug in ATS tenant registry).
- **Outcome:** Direct match on registered corporate domain achieves **95% confidence** (`MATCH_TIER_2_CANONICAL_DOMAIN`).

---

### Tier 3: Legal Name Normalization & Country Concordance (80% Precision)
- **Mechanism:** When neither national registration key nor web domain is present, apply deterministic rule-based name normalization constrained by country of operation.
- **Normalization Rules:**
  1. Convert all characters to uppercase.
  2. Strip punctuation, hyphens, periods, commas, and special characters (`&` $\to$ `AND`).
  3. Strip legal corporate suffixes by jurisdiction:
     - **US:** `INC`, `INCORPORATED`, `CORP`, `CORPORATION`, `LLC`, `LIMITED LIABILITY COMPANY`, `LP`, `CO`, `COMPANY`.
     - **UK:** `LTD`, `LIMITED`, `PLC`, `PUBLIC LIMITED COMPANY`, `LLP`.
     - **AU:** `PTY LTD`, `PTY LIMITED`, `PROPRIETARY LIMITED`, `LTD`, `NL`.
     - **SG:** `PTE LTD`, `PRIVATE LIMITED`, `LTD`.
     - **IN:** `PVT LTD`, `PRIVATE LIMITED`, `LTD`, `LIMITED`, `LLP`.
  4. Collapse redundant whitespaces.
- **Strict Constraint:** Normalized string comparison **must match within the same country code**. A match between "ACME LTD" in UK and "ACME INC" in US is rejected.
- **Outcome:** Flagged as `MATCH_TIER_3_NORMALIZED_NAME` (`REVIEW_REQUIRED`).

---

### Tier 4: Fuzzy String Matching & Human Review Queue
- **Mechanism:** Algorithmic similarity using Jaro-Winkler distance and token sort ratio.
- **Hard Rule:** **ZERO AUTOMATIC MERGING.** Any match with similarity score between $0.85$ and $0.99$ without Tier 1 or Tier 2 verification is routed to the **Human Review Queue** (`EmployerVerificationStatus.REVIEW_REQUIRED`).
- **Safety Policy:** It is vastly better to maintain two separate unmerged company records than to mistakenly combine two distinct businesses.

---

## 3. CORPORATE HIERARCHY & GRAPH MODELING

Corporate structures are modeled as a **Directed Acyclic Graph (DAG)** of legal entities:

```
                  [Global Parent Holding Entity]
                      Alphabet Inc. (US: CIK)
                                 |
        +------------------------+------------------------+
        |                                                 |
        v                                                 v
[Operating Entity]                               [Operating Entity]
Google LLC (Delaware)                           Waymo LLC (Delaware)
        |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
[Local Subsidiary]   [Local Subsidiary]   [Local Subsidiary]
Google UK Limited    Google India Pvt Ltd Google Asia Pacific
(UK: CRN)            (IN: CIN)            (SG: UEN)
```

### Hierarchy Attributes in Data Model:
- `parent_employer_id`: Explicit link to legal parent holding company.
- `subsidiary_ids`: Child entities verified through statutory annual accounts (e.g., Exhibit 21 of SEC Form 10-K: *"Subsidiaries of the Registrant"*).
- `commercial_brands`: Consumer brands owned and operated by the entity.

### UX Aggregation Rules:
- When a user views an employer profile (e.g. "Google"), the UI provides an explicit toggle:
  - **Local Operating Entity View:** Postings and headcount strictly for `Google UK Limited`.
  - **Consolidated Enterprise View:** Aggregated global statistics clearly disclosing parent-level consolidation.

---

## 4. RECRUITMENT AGENCY & THIRD-PARTY STAFFING FILTER

To protect data integrity, third-party staffing agencies must be strictly segregated from direct operating employers.

### Detection & Segregation Protocol:
1. **Official Licensing Registers:**
   - Singapore: Ministry of Manpower (MOM) Employment Agencies Directory (~4,000 licensed agencies).
   - UK: Gangmasters and Labour Abuse Authority (GLAA) register and standard SIC codes (`78109`, `78200`).
   - US: NAICS code `561320` (Temporary Help Services) and `561311` (Employment Placement Agencies).
   - India: NIC-2008 code `7810` / `7820`.
2. **Postings Filter:**
   - All postings originating from recognized agency domains or containing agency keywords (*"Our client is a...", "Recruiting on behalf of..."*) are tagged:
     `is_staffing_agency_posting: true`
   - These postings are **excluded from direct employer hiring counts** and surfaced only under a dedicated "Recruitment Agency Opportunities" view.

---

## 5. RESOLUTION BENCHMARK & EVALUATION METRICS

During Phase 1 implementation, the resolution engine will be evaluated against a certified golden test dataset of 250 enterprise profiles:

$$\text{Precision} = \frac{\text{True Merges}}{\text{True Merges} + \text{False Merges}} \ge 99.5\%$$
$$\text{Recall} = \frac{\text{True Merges}}{\text{True Merges} + \text{False Splits}} \ge 92.0\%$$

Any algorithm producing false-positive merges $> 0.5\%$ fails the qualification gate.

**Audit Status:** `PASS — ENTITY RESOLUTION ARCHITECTURE SPECIFIED`
