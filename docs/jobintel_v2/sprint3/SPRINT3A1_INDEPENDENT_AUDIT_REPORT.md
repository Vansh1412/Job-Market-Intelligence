# JOBINTEL 2.0 — SPRINT 3A.1 INDEPENDENT AUDIT REPORT
## Independent Occupation Registry, Source Authenticity & Concordance Audit

**Document Reference:** `JOBINTEL-AUDIT-SPRINT3A1-20261116`  
**Date:** 2026-11-16  
**Auditor:** Independent Principal Data & Systems Auditor (JOBINTEL Architecture & Governance Team)  
**Audit Scope:** Sprint 3A Global Occupation Intelligence Implementation  
**Target Repository:** `E:\Job Market` (`https://github.com/Vansh1412/Job-Market-Intelligence`)  
**Target Branch:** `staging/sprint2c3` (Commit `13f362c3ffef6473dce8e40ee42b643b96baaca4`)  
**Production Baseline:** `master` at commit `198b79dcdff08a5be5f08847c4262d31a3ce261e` (Verified Untouched)  
**Overall Audit Verdict:** **`VERIFIED WITH LIMITATIONS`**

---

## 1. EXECUTIVE SUMMARY & AUDIT BASELINE

This independent audit conducts an objective, evidence-based verification of the **Global Occupation Intelligence** subsystem implemented in Sprint 3A. The subsystem establishes foundational classification registries, canonical concepts, and cross-market concordance crosswalks across five target jurisdictions (**United Kingdom, United States, Australia, Singapore, and India**) plus international reference benchmarks (**ILO ISCO-08**).

### Scope of Audit
The audit inspected and evaluated:
1. **8 Classification Systems** registered in `src/backend/data/occupations/classifications.json`.
2. **30 National Occupation Records** registered in `src/backend/data/occupations/national_occupations.json`.
3. **12 Canonical Occupation Concepts** registered in `src/backend/data/occupations/canonical_occupations.json`.
4. **32 Concordance Mappings** registered in `src/backend/data/occupations/mappings.json` (15 canonical mappings, 17 national cross-market mappings).
5. **9 API Endpoints** mounted under `/v1/occupations` and `/api/v1/occupations`.
6. **Frontend User Interface** (`frontend/src/pages/OccupationsPage.tsx`, routing, and state integration).
7. **Quality, Governance & Security Baselines** (zero secret leakage, zero model regressions, preserved fail-closed UK ASHE governance).

### Overall Audit Verdict: `VERIFIED WITH LIMITATIONS`
The Sprint 3A implementation is technically robust, syntactically clean, and structurally sound. Schema enforcement, relationship directionality, and test suites (312/312 backend tests, 9/9 frontend tests, clean production build) pass with 100% compliance.

However, a strict and honest audit standard dictates a verdict of **`VERIFIED WITH LIMITATIONS`** based on the following three operational and empirical findings:
1. **Rule-Based Heuristic Scoring vs. Empirical Calibration:** The concordance confidence scores ($0.72$ to $1.00$) represent structured expert heuristic judgments rather than empirically calibrated posterior probabilities derived from labelled cross-market test datasets.
2. **Curated vs. Verbatim Task Provenance:** While UK SOC 2020 and US SOC 2018 records contain verbatim/official government definitions and tasks, records for Australia (OSCA 2024), Singapore (SSOC 2024), and India (NCO-2015) rely on JobIntel-curated task summaries derived from official statistical publications rather than direct raw gazette extracts.
3. **Partial Cross-Market Coverage:** 14 of 30 national occupations currently lack active mapping relationships, and 5 of 12 canonical concepts (Data Engineer, Database Administrator, Systems Analyst, Network Engineer, IT Project Manager) have zero linked national records, awaiting Sprint 3B cross-market salary data binding.

---

## 2. REPOSITORY & DEPLOYMENT BASELINE

| Property | Target State | Audited State | Status |
| :--- | :--- | :--- | :--- |
| **Active Branch** | `staging/sprint2c3` | `staging/sprint2c3` | `VERIFIED` |
| **Commit HEAD** | `13f362c` | `13f362c3ffef6473dce8e40ee42b643b96baaca4` | `VERIFIED` |
| **Origin Staging** | Synced | `origin/staging/sprint2c3` at `13f362c` | `VERIFIED` |
| **Master Baseline** | `198b79d` | `198b79dcdff08a5be5f08847c4262d31a3ce261e` | `VERIFIED (Untouched)` |
| **Working Tree** | Clean | Clean (`git status --porcelain` empty) | `VERIFIED` |
| **Staging Backend** | Cloud | `https://jobintel-backend-staging.onrender.com` | `PROVISIONED` |
| **Staging Frontend**| Cloud | `https://jobintel-staging.vercel.app` | `PROVISIONED` |

---

## 3. CLASSIFICATION SYSTEMS AUTHENTICITY AUDIT (ALL 8 SYSTEMS)

All 8 classification systems in `classifications.json` were audited for authoritative provenance, publishing body, legal licensing, and hierarchical structure.

| Classification ID | Market | Issuing Authority & Formal Title | Edition / Vintage | Code Regex | Hierarchy Depth | Status | License Framework | Audit Verdict |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| `UK_SOC_2020` | UK | **Office for National Statistics (ONS)**<br>UK Standard Occupational Classification 2020 | 2020 Vol 1 & 2 | `^\d{4}$` | 4 Levels (Major, Sub-Major, Minor, Unit) | Active | Open Government Licence v3.0 (OGL v3.0) | **`VERIFIED`** |
| `US_SOC_2018` | US | **Bureau of Labor Statistics (BLS)**<br>Standard Occupational Classification 2018 | 2018 Revision | `^\d{2}-\d{4}$` | 4 Levels (Major, Minor, Broad, Detailed) | Active | US Government Work (Public Domain) | **`VERIFIED`** |
| `AU_OSCA_2024` | AU | **ABS & Jobs and Skills Australia (JSA)**<br>Occupation Standard Classification for Australia 2024 | 2024 Release 1.0 (Nov 2024) | `^\d{6}$` | 5 Levels (Major, Sub-Major, Minor, Unit, Occupation) | Active | Creative Commons Attribution 4.0 (CC BY 4.0) | **`VERIFIED`** |
| `AU_ANZSCO_2022`| AU | **Australian Bureau of Statistics (ABS)**<br>Australian and New Zealand Standard Classification of Occupations | 2022 Release (ANZSCO 2021/2022) | `^\d{6}$` | 5 Levels (Major, Sub-Major, Minor, Unit, Occupation) | Superseded | Creative Commons Attribution 4.0 (CC BY 4.0) | **`VERIFIED`** |
| `SG_SSOC_2024` | SG | **Singapore Department of Statistics (SingStat)**<br>Singapore Standard Occupational Classification 2024 | 2024 Edition | `^\d{5}$` | 5 Levels (Major, Sub-Major, Minor, Unit, Detailed) | Active | Singapore Open Data Licence (Attribution Required)| **`VERIFIED`** |
| `SG_SSOC_2020` | SG | **Singapore Department of Statistics (SingStat)**<br>Singapore Standard Occupational Classification 2020 | 2020 Edition | `^\d{5}$` | 5 Levels (Major, Sub-Major, Minor, Unit, Detailed) | Superseded | Singapore Open Data Licence (Attribution Required)| **`VERIFIED`** |
| `IN_NCO_2015` | IN | **Directorate General of Employment (DGE), MoLE**<br>National Classification of Occupations 2015 | 2015 Edition (ISCO-08 Aligned) | `^\d{4}(\.\d{4})?$` | 5 Levels (Division, Sub-Div, Group, Family, Detailed) | Active | Government of India Open Data / NDSAP | **`VERIFIED WITH LIMITATIONS`** |
| `INT_ISCO_08` | INT | **International Labour Organization (ILO)**<br>International Standard Classification of Occupations 2008 | ISCO-08 | `^\d{4}$` | 4 Levels (Major, Sub-Major, Minor, Unit) | Active | UN / ILO Open Statistical Documentation | **`VERIFIED`** |

### Specific Findings on Classifications:
1. **Australian Modernization (OSCA 2024 vs. ANZSCO 2022):** The inclusion of OSCA 2024 as the active classification and ANZSCO 2022 as inactive is verified as authoritative. ABS and JSA formally released OSCA in late 2024 to replace ANZSCO for Australian labor analysis, modernizing digital occupations (e.g., dedicated Data Scientist 224411).
2. **Singapore Taxonomy (SSOC 2024 vs. 2020):** SSOC 2024 represents SingStat's latest operational standard, featuring granular tech classifications including Cloud Architect (25124), DevOps Engineer (25125), and AI/ML Engineer (25131). Marking SSOC 2020 inactive is appropriate.
3. **Indian Taxonomy Limitations (`IN_NCO_2015`):** While NCO-2015 is the official Ministry of Labour & Employment standard, its 2015 vintage precedes modern AI/ML, Cloud, and DevOps specializations. As a result, software roles are clustered under `2512.0100` (Software Developer) without native statistical sub-divisions. This requires a `VERIFIED WITH LIMITATIONS` verdict.

---

## 4. NATIONAL OCCUPATION RECORD AUDIT (ALL 30 RECORDS)

Each of the 30 national occupation records in `national_occupations.json` was examined for field completeness, composite ID structure, task clarity, entry qualifications, and provenance.

### Field Provenance Classification
- **Official Verbatim:** Directly transcribed from official government classification gazettes, volumes, or statutory statistical releases.
- **Officially Derived:** Extracted and harmonized directly from official statistical tables and reference documents.
- **Curated by JOBINTEL:** Expertly drafted and standardized by JobIntel based on official occupational profiles, educational frameworks, and industry hiring standards.

| Composite ID | Title | Market | Class Code | Level | Task Count | Definition Provenance | Task Provenance | Qualification Provenance | Audit Verdict |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| `UK_SOC_2020:2134` | Programmers and software development professionals | UK | 2134 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:2135` | Cyber security professionals | UK | 2135 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:2136` | IT quality and testing professionals | UK | 2136 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:2133` | IT business analysts, architects & systems designers | UK | 2133 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:2137` | IT network professionals | UK | 2137 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:2131` | IT project managers | UK | 2131 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:3133` | Database administrators & web content technicians | UK | 3133 | Unit Group | 3 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `UK_SOC_2020:3544` | Data analysts | UK | 3544 | Unit Group | 4 | Official Verbatim (ONS) | Official Verbatim (ONS) | Officially Derived (ONS) | **`VERIFIED`** |
| `US_SOC_2018:15-1252` | Software Developers | US | 15-1252 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-2051` | Data Scientists | US | 15-2051 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-1212` | Information Security Analysts | US | 15-1212 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-1253` | Software Quality Assurance Analysts and Testers | US | 15-1253 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-1242` | Database Administrators | US | 15-1242 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-1244` | Network and Computer Systems Administrators | US | 15-1244 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `US_SOC_2018:15-1211` | Computer Systems Analysts | US | 15-1211 | Detailed | 4 | Official Verbatim (BLS) | Officially Derived (BLS) | Officially Derived (BLS) | **`VERIFIED`** |
| `AU_OSCA_2024:261313` | Software Engineer | AU | 261313 | Occupation | 4 | Officially Derived (ABS) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `AU_OSCA_2024:224411` | Data Scientist | AU | 224411 | Occupation | 4 | Officially Derived (ABS) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `AU_OSCA_2024:262112` | ICT Security Specialist | AU | 262112 | Occupation | 4 | Officially Derived (ABS) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `AU_OSCA_2024:261314` | Software Tester | AU | 261314 | Occupation | 4 | Officially Derived (ABS) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25121` | Software Developer | SG | 25121 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25132` | Data Scientist | SG | 25132 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25131` | AI / Machine Learning Engineer | SG | 25131 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25124` | Cloud Architect | SG | 25124 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25125` | DevOps Engineer | SG | 25125 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `SG_SSOC_2024:25211` | Cybersecurity Specialist | SG | 25211 | Detailed | 4 | Officially Derived (SingStat)| Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `IN_NCO_2015:2512.0100`| Software Developer | IN | 2512.0100 | Detailed | 4 | Officially Derived (DGE) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `IN_NCO_2015:2511.0100`| Systems Analyst | IN | 2511.0100 | Detailed | 4 | Officially Derived (DGE) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `IN_NCO_2015:2521.0100`| Database Administrator | IN | 2521.0100 | Detailed | 4 | Officially Derived (DGE) | Curated by JOBINTEL | Curated by JOBINTEL | **`VERIFIED WITH LIMITATIONS`** |
| `INT_ISCO_08:2512` | Software Developers | INT | 2512 | Unit Group | 3 | Official Verbatim (ILO) | Official Verbatim (ILO) | Officially Derived (ILO) | **`VERIFIED`** |
| `INT_ISCO_08:2511` | Systems Analysts | INT | 2511 | Unit Group | 3 | Official Verbatim (ILO) | Official Verbatim (ILO) | Officially Derived (ILO) | **`VERIFIED`** |

### Synthesis on Records:
- **Composite Key Integrity:** 100% (30/30) conform to `{classification_id}:{occupation_code}`.
- **Hierarchy Conformance:** Leaf flags (`is_leaf=True`) are correctly asserted across unit groups and detailed occupations.
- **Limitation Note:** For AU, SG, and IN records, task lists and entry route strings are high-fidelity JobIntel curations rather than raw government gazette paragraphs. This must be maintained transparently in data documentation.

---

## 5. CANONICAL OCCUPATION CONCEPT AUDIT (ALL 12 CONCEPTS)

The canonical layer establishes jurisdiction-neutral reference benchmarks to enable international analytics and cross-border salary interoperability.

| Canonical Concept ID | Preferred Title | Occupational Family | Competency Count | Linked Sources Count | Over-Generalization Risk | Duplicate Risk | Audit Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `CAN_OCC_SOFTWARE_ENGINEER` | Software Engineer | Software & Applications Development | 5 | 5 | Low | None | **`VERIFIED`** |
| `CAN_OCC_DATA_SCIENTIST` | Data Scientist | Data & Advanced Analytics | 5 | 3 | Low | None | **`VERIFIED`** |
| `CAN_OCC_DATA_ANALYST` | Data Analyst | Data & Business Intelligence | 5 | 1 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_ML_ENGINEER` | Machine Learning Engineer | Artificial Intelligence & MLOps | 5 | 1 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_DATA_ENGINEER` | Data Engineer | Data Infrastructure & Architecture | 5 | 0 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_DEVOPS_ENGINEER` | DevOps & Cloud Engineer | Infrastructure & Cloud Platforms | 5 | 1 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_CYBERSECURITY_ANALYST` | Cybersecurity & InfoSec Professional | Security & Risk Management | 5 | 2 | Moderate | None | **`VERIFIED`** |
| `CAN_OCC_DATABASE_ADMIN` | Database Administrator & Architect | Data Infrastructure & Architecture | 5 | 0 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_SYSTEMS_ANALYST` | Systems Analyst & Solutions Architect | Systems & Enterprise Architecture | 5 | 0 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_NETWORK_ENGINEER` | Network & Systems Engineer | Infrastructure & Cloud Platforms | 5 | 0 | Low | None | **`VERIFIED WITH LIMITATIONS`** |
| `CAN_OCC_QA_TEST_ENGINEER` | QA & Software Test Engineer | Quality Assurance & Verification | 5 | 2 | Low | None | **`VERIFIED`** |
| `CAN_OCC_IT_PROJECT_MGR` | IT Project & Program Manager | Technology Management & Governance | 5 | 0 | Low | None | **`VERIFIED WITH LIMITATIONS`** |

### Synthesis on Canonical Concepts:
1. **Scope Precision:** All 12 concepts exhibit distinct, non-overlapping competency sets. No conceptual duplication was discovered.
2. **Current Linkage Gaps (Sprint 3A limitation):** 7 concepts have active national source links; 5 concepts currently have zero mapped national records (`CAN_OCC_DATA_ENGINEER`, `CAN_OCC_DATABASE_ADMIN`, `CAN_OCC_SYSTEMS_ANALYST`, `CAN_OCC_NETWORK_ENGINEER`, `CAN_OCC_IT_PROJECT_MGR`). National records for these roles exist in `national_occupations.json` (e.g., `UK_SOC_2020:2131`, `US_SOC_2018:15-1242`), but explicit mappings were deferred to Sprint 3B. This warrants `VERIFIED WITH LIMITATIONS` for those five concepts.

---

## 6. CONCORDANCE MAPPINGS AUDIT (ALL 32 MAPPINGS)

The concordance mapping registry `mappings.json` was audited across all **32 individual mappings** (15 canonical mappings and 17 national cross-market mappings).

### Important Technical Distinction: Heuristic Weights vs. Calibrated Probabilities
> [!IMPORTANT]
> The `confidence_score` values ($0.72$ to $1.00$) in `mappings.json` are **rule-based expert heuristic affinity scores**, not empirical Bayesian posterior probabilities. JOBINTEL 2.0 does not currently possess a labeled cross-market resume-vacancy test dataset to compute empirical logistic calibration curves. The schema validation rule strictly reserves $1.00$ for `VERIFIED_OFFICIAL` mappings (official government crosswalks), which is mathematically sound for expert rules.

### Detailed Audit of All 32 Mappings

| # | Mapping ID | Source Occupation | Target Type & ID | Rel Type | Confidence | Review Status | Method | Warning (<0.95) | Audit Verdict |
| :-: | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| 1 | `map_uk2134_us151252_v1` | `UK_SOC_2020:2134` | NATIONAL: `US_SOC_2018:15-1252` | `CLOSE_MATCH` | 0.92 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 2 | `map_us151252_uk2134_v1` | `US_SOC_2018:15-1252` | NATIONAL: `UK_SOC_2020:2134` | `CLOSE_MATCH` | 0.92 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 3 | `map_us151252_au261313_v1` | `US_SOC_2018:15-1252` | NATIONAL: `AU_OSCA_2024:261313` | `BROADER_THAN` | 0.90 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 4 | `map_au261313_us151252_v1` | `AU_OSCA_2024:261313` | NATIONAL: `US_SOC_2018:15-1252` | `NARROWER_THAN`| 0.90 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 5 | `map_us151252_sg25121_v1` | `US_SOC_2018:15-1252` | NATIONAL: `SG_SSOC_2024:25121` | `CLOSE_MATCH` | 0.94 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 6 | `map_sg25121_us151252_v1` | `SG_SSOC_2024:25121` | NATIONAL: `US_SOC_2018:15-1252` | `CLOSE_MATCH` | 0.94 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 7 | `map_in2512_isco2512_v1` | `IN_NCO_2015:2512.0100`| NATIONAL: `INT_ISCO_08:2512` | `EXACT_MATCH` | 1.00 | `VERIFIED_OFFICIAL` | `OFFICIAL_CROSSWALK` | No | **`VERIFIED`** |
| 8 | `map_isco2512_in2512_v1` | `INT_ISCO_08:2512` | NATIONAL: `IN_NCO_2015:2512.0100`| `EXACT_MATCH` | 1.00 | `VERIFIED_OFFICIAL` | `OFFICIAL_CROSSWALK` | No | **`VERIFIED`** |
| 9 | `map_us152051_au224411_v1` | `US_SOC_2018:15-2051` | NATIONAL: `AU_OSCA_2024:224411` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 10 | `map_au224411_us152051_v1` | `AU_OSCA_2024:224411` | NATIONAL: `US_SOC_2018:15-2051` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 11 | `map_us152051_sg25132_v1` | `US_SOC_2018:15-2051` | NATIONAL: `SG_SSOC_2024:25132` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 12 | `map_sg25132_us152051_v1` | `SG_SSOC_2024:25132` | NATIONAL: `US_SOC_2018:15-2051` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 13 | `map_uk2135_us151212_v1` | `UK_SOC_2020:2135` | NATIONAL: `US_SOC_2018:15-1212` | `CLOSE_MATCH` | 0.94 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 14 | `map_us151212_uk2135_v1` | `US_SOC_2018:15-1212` | NATIONAL: `UK_SOC_2020:2135` | `CLOSE_MATCH` | 0.94 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | Yes | **`VERIFIED`** |
| 15 | `map_uk2136_us151253_v1` | `UK_SOC_2020:2136` | NATIONAL: `US_SOC_2018:15-1253` | `EXACT_MATCH` | 0.97 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 16 | `map_us151253_uk2136_v1` | `US_SOC_2018:15-1253` | NATIONAL: `UK_SOC_2020:2136` | `EXACT_MATCH` | 0.97 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 17 | `map_uk3544_us152051_v1` | `UK_SOC_2020:3544` | NATIONAL: `US_SOC_2018:15-2051` | `PARTIAL_OVERLAP`| 0.72 | `DERIVED_MEDIUM_CONFIDENCE`| `EXPERT_ASSESSMENT`| Yes | **`VERIFIED`** |
| 18 | `map_can_softeng_uk2134_v1`| `UK_SOC_2020:2134` | CANONICAL: `CAN_OCC_SOFTWARE_ENGINEER`| `CLOSE_MATCH` | 0.95 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 19 | `map_can_softeng_us151252_v1`| `US_SOC_2018:15-1252` | CANONICAL: `CAN_OCC_SOFTWARE_ENGINEER`| `CLOSE_MATCH` | 0.96 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 20 | `map_can_softeng_au261313_v1`| `AU_OSCA_2024:261313` | CANONICAL: `CAN_OCC_SOFTWARE_ENGINEER`| `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 21 | `map_can_softeng_sg25121_v1`| `SG_SSOC_2024:25121` | CANONICAL: `CAN_OCC_SOFTWARE_ENGINEER`| `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 22 | `map_can_softeng_in2512_v1` | `IN_NCO_2015:2512.0100`| CANONICAL: `CAN_OCC_SOFTWARE_ENGINEER`| `CLOSE_MATCH` | 0.95 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 23 | `map_can_datascientist_us152051_v1`| `US_SOC_2018:15-2051`| CANONICAL: `CAN_OCC_DATA_SCIENTIST` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 24 | `map_can_datascientist_au224411_v1`| `AU_OSCA_2024:224411`| CANONICAL: `CAN_OCC_DATA_SCIENTIST` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 25 | `map_can_datascientist_sg25132_v1`| `SG_SSOC_2024:25132` | CANONICAL: `CAN_OCC_DATA_SCIENTIST` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 26 | `map_can_mleng_sg25131_v1` | `SG_SSOC_2024:25131` | CANONICAL: `CAN_OCC_ML_ENGINEER` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 27 | `map_can_cyber_uk2135_v1` | `UK_SOC_2020:2135` | CANONICAL: `CAN_OCC_CYBERSECURITY_ANALYST`| `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 28 | `map_can_cyber_us151212_v1` | `US_SOC_2018:15-1212` | CANONICAL: `CAN_OCC_CYBERSECURITY_ANALYST`| `CLOSE_MATCH` | 0.95 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 29 | `map_can_dataanalyst_uk3544_v1` | `UK_SOC_2020:3544` | CANONICAL: `CAN_OCC_DATA_ANALYST` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 30 | `map_can_qa_uk2136_v1` | `UK_SOC_2020:2136` | CANONICAL: `CAN_OCC_QA_TEST_ENGINEER` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 31 | `map_can_qa_us151253_v1` | `US_SOC_2018:15-1253` | CANONICAL: `CAN_OCC_QA_TEST_ENGINEER` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |
| 32 | `map_can_devops_sg25125_v1` | `SG_SSOC_2024:25125` | CANONICAL: `CAN_OCC_DEVOPS_ENGINEER` | `EXACT_MATCH` | 0.98 | `VERIFIED_REVIEWED` | `EXPERT_ASSESSMENT` | No | **`VERIFIED`** |

### Directionality Check Findings:
The relationship directionality is mathematically and conceptually verified:
- **`US_SOC_2018:15-1252` -> `AU_OSCA_2024:261313`:** Labeled `BROADER_THAN` (US aggregates software engineers, developer programmers, and web application builders).
- **`AU_OSCA_2024:261313` -> `US_SOC_2018:15-1252`:** Labeled `NARROWER_THAN` (AU isolates Software Engineer from Developer Programmer `261312`).
- Reciprocal inverse integrity is confirmed.

---

## 7. CROSS-MARKET SEMANTIC ALIGNMENT EVALUATION

Six critical cross-market occupational comparisons were audited for semantic fidelity and salary comparability.

```
                      [CAN_OCC_SOFTWARE_ENGINEER]
                     /      |             |     \
                    /       |             |      \
(Close: 0.95)      /        | (Close: 0.96|       \ (Exact: 0.98)
                  v         v             v        v
        [UK 2134] <=======> [US 15-1252] =======> [AU 261313]
         Programmers   (0.92)  Software     (0.90)   Software
         & Devs                Developers            Engineer
                                  ||
                                  || (Close: 0.94)
                                  \/
                             [SG 25121]
                              Software Developer
```

### Case 1: UK 2134 (Programmers & Software Devs) vs. US 15-1252 (Software Developers)
- **Semantic Overlap:** Estimated $88\%$.
- **Breadth Mismatch:** UK 2134 is broader. It subsumes web developers, computer game programmers, and application programmers. In US SOC 2018, Web Developers are distinct under `15-1254`.
- **Confidence & Warning:** Assigned $0.92$ (`CLOSE_MATCH`). Correctly triggers approximation warning.
- **Salary Comparability:** **Comparability with Caveats.** UK ONS ASHE median figures include lower-tier web programmers, causing a slight downward bias relative to US BLS OEWS Software Developers. Direct conversions must display the approximation warning.

### Case 2: UK 2133 (IT Business Analysts, Architects) vs. US 15-1211 (Computer Systems Analysts)
- **Semantic Overlap:** Estimated $72\%$.
- **Breadth Mismatch:** UK 2133 bundles business analysts, systems designers, and enterprise architects. In US SOC 2018, enterprise architects are categorized under `15-1299.08`, while `15-1211` covers business systems analysts.
- **Implementation Finding:** In Sprint 3A, a direct crosswalk mapping between UK 2133 and US 15-1211 was **deliberately withheld** due to high structural asymmetry. Both exist in the registry, but mapping is deferred to Sprint 3B. This conservative governance decision is commendable.

### Case 3: UK 3544 (Data Analysts) vs. US 15-2051 (Data Scientists)
- **Semantic Overlap:** Estimated $45\%$.
- **Breadth Mismatch:** Massive qualification and task divergence. UK 3544 sits in Major Group 3 (Associate Professional / Technical) focusing on descriptive SQL, ETL, and BI reporting. US 15-2051 sits in Major Group 15 (Professional / Mathematical) requiring machine learning, statistical modeling, and experimental algorithms.
- **Confidence & Warning:** Assigned $0.72$ (`PARTIAL_OVERLAP`, `DERIVED_MEDIUM_CONFIDENCE`). Triggers high-priority approximation warning.
- **Salary Comparability:** **Incomparable without Extreme Caveats.** Comparing US Data Scientist compensation (~$108,000 median) with UK Data Analyst compensation (~£36,000 median) creates a severe apples-to-oranges distortion. The warning engine appropriately alerts downstream consumers.

### Case 4: IN 2512.0100 (Software Developer) vs. INT ISCO-08 2512 (Software Developers)
- **Semantic Overlap:** $100\%$.
- **Authority:** Government of India Directorate General of Employment (DGE) official Concordance Table.
- **Confidence:** $1.00$ (`EXACT_MATCH`, `VERIFIED_OFFICIAL`, `OFFICIAL_CROSSWALK`).
- **Salary Comparability:** Structurally identical role definition; economic purchasing power disparity must be handled via PPP adjustments in future salary modules.

### Case 5: SG 25121 (Software Developer) vs. US 15-1252 / UK 2134 / AU 261313
- **Semantic Overlap:** $94\%$.
- **Taxonomy Nuance:** Singapore SSOC 2024 explicitly carved out Cloud Architect (`25124`) and DevOps Engineer (`25125`). In US and UK taxonomies, these specialized titles are often aggregated into general software developer classifications.
- **Confidence:** $0.94$ (`CLOSE_MATCH`). Triggers approximation warning.

### Case 6: AU OSCA 261313 (Software Engineer) vs. US 15-1252
- **Semantic Overlap:** $90\%$.
- **Breadth Mismatch:** Australia's OSCA 2024 distinguishes Software Engineer (`261313`) from Developer Programmer (`261312`) and Analyst Programmer (`261311`). US 15-1252 encompasses all three.
- **Directionality:** US -> AU is `BROADER_THAN` ($0.90$); AU -> US is `NARROWER_THAN` ($0.90$).

---

## 8. PROGRAMMATIC QUANTITATIVE INTEGRITY VERIFICATION

Automated verification scripts (`audit_deep_check.py`) were executed against the four JSON registries.

```
Integrity Metric                     Expected    Actual      Status
----------------------------------------------------------------------
Classification Systems Count         8           8           PASS
National Occupations Count           30          30          PASS
Canonical Concepts Count             12          12          PASS
Concordance Mappings Count           31-32       32          PASS
Orphan Source Occupation IDs         0           0           PASS
Orphan Target Occupation IDs         0           0           PASS
Duplicate IDs across all datasets    0           0           PASS
Unmapped National Occupations        --          14          AUDITED
Multi-Mapped Source Occupations      --          13          AUDITED
Confidence Score Range               [0.0, 1.0]  [0.72, 1.0] PASS
Confidence Mean                      --          0.9553      AUDITED
Confidence Median                    --          0.9800      AUDITED
Mappings triggering Warning (<0.95)  --          9           AUDITED
```

### Unmapped National Occupations Audit (14 Records)
The following 14 occupations currently have no mapped edges:
- `UK_SOC_2020`: `2131` (IT project managers), `2133` (IT business analysts/architects), `2137` (IT network professionals), `3133` (Database administrators).
- `US_SOC_2018`: `15-1211` (Computer Systems Analysts), `15-1242` (Database Administrators), `15-1244` (Network Administrators).
- `AU_OSCA_2024`: `261314` (Software Tester), `262112` (ICT Security Specialist).
- `SG_SSOC_2024`: `25124` (Cloud Architect), `25211` (Cybersecurity Specialist).
- `IN_NCO_2015`: `2511.0100` (Systems Analyst), `2521.0100` (Database Administrator).
- `INT_ISCO_08`: `2511` (Systems Analysts).

> [!NOTE]
> All 14 unmapped occupations represent valid national classifications. They were successfully ingested into the catalog during Sprint 3A to establish taxonomic breadth, with concordance mappings intentionally scheduled for Sprint 3B.

---

## 9. API ROUTE & FRONTEND VERIFICATION

### Backend API Endpoints (9 Endpoints Audited)
All 9 endpoints under `/v1/occupations` were verified through automated FastAPI TestClient suites:

| Route | Method | Purpose | Verified Behavior |
| :--- | :---: | :--- | :---: |
| `/v1/occupations/classifications` | GET | List classification systems (optional market filter) | HTTP 200 (8 items) |
| `/v1/occupations/classifications/{id}` | GET | Retrieve single classification metadata | HTTP 200 / 404 |
| `/v1/occupations/classifications/{id}/occupations` | GET | Paginated list of occupations in classification | HTTP 200 (Pagination verified) |
| `/v1/occupations/search` | GET | Multi-market search with relevance scoring | HTTP 200 (Relevance scoring verified)|
| `/v1/occupations/canonical` | GET | List canonical career concepts | HTTP 200 (12 concepts) |
| `/v1/occupations/canonical/{id}` | GET | Retrieve single canonical concept details | HTTP 200 / 404 |
| `/v1/occupations/compare` | GET | Cross-market comparison with warnings | HTTP 200 (Warnings verified) |
| `/v1/occupations/{occupation_id}/mappings` | GET | List mappings originating from source | HTTP 200 / 404 |
| `/v1/occupations/{occupation_id}` | GET | Retrieve full national occupation profile | HTTP 200 / 404 |

### Test Suite Execution Evidence
- **Occupation Intelligence Suite:** `pytest tests/test_occupation_intelligence.py` -> **15 passed** in 2.17s.
- **Full Backend Suite:** `pytest tests/` -> **312 passed** in 27.62s. Zero regressions across existing governance, prediction parity, or schema tests.

### Frontend Verification Evidence
- **Vitest Test Suite:** `npm --prefix frontend test -- --run` -> **9 passed** (3 test files, 1.01s).
- **TypeScript & Production Bundling:** `npm --prefix frontend run build` (`tsc -b && vite build`) -> **Clean build**, 2,892 modules transformed, 0 errors, total bundle size within performance budgets.
- **UI Architecture:** `OccupationsPage.tsx` integrates tabbed filtering, search input, paginated tables, modal occupation inspectors, and visual concordance crosswalk chips displaying approximation badges when confidence $< 0.95$.

---

## 10. GOVERNANCE, SECURITY & REGRESSION VERIFICATION

| Check | Requirement | Audited Result | Status |
| :--- | :--- | :--- | :---: |
| **Secret Leakage** | Zero credentials, tokens, or private keys committed | Git log and tree inspection revealed zero leaked secrets | **`VERIFIED`** |
| **Restricted Data** | Zero unscrubbed microdata or restricted data committed | Only aggregated, public taxonomy definitions committed | **`VERIFIED`** |
| **Golden Prediction Parity**| India and USA ML salary predictions unchanged | `test_golden_predictions.py` and `test_prediction_parity.py` pass | **`VERIFIED`** |
| **UK ASHE Governance** | All 5 UK salary endpoints fail closed with HTTP 503 | `test_uk_salary_api.py` (35 tests) pass with HTTP 503 | **`VERIFIED`** |
| **Model Registry Status** | Frozen artifacts intact (10/10) | Verified GREEN; SHA-256 manifests match | **`VERIFIED`** |

---

## 11. FINAL AUDIT VERDICTS & ACTIONABLE RECOMMENDATIONS FOR SPRINT 3B

### Category-by-Category Verdict Summary
1. **Classification Systems (8):** **`VERIFIED`** (7 Verified, 1 Verified with Limitations due to NCO vintage).
2. **National Occupation Records (30):** **`VERIFIED WITH LIMITATIONS`** (17 Verified verbatim/official, 13 Verified with Limitations due to curated task provenance).
3. **Canonical Concepts (12):** **`VERIFIED WITH LIMITATIONS`** (7 Verified active, 5 Verified with Limitations due to pending national links).
4. **Concordance Mappings (32):** **`VERIFIED WITH LIMITATIONS`** (32 Verified structurally, noting heuristic vs. calibrated scoring).
5. **API & Frontend Contracts:** **`VERIFIED`** (100% test pass rate, clean build, robust error handling).
6. **Governance & Security:** **`VERIFIED`** (Zero regressions, zero leaks, fail-closed preserved).

### Identified Strengths
- **Rigorous Directionality:** Broad vs. narrow mappings are strictly inverted and mathematically consistent.
- **Fail-Safe Approximation Warning Engine:** Any crosswalk comparison with confidence $< 0.95$ proactively generates explanatory warning banners for downstream UI and API consumers.
- **Jurisdictional Modernization:** Early adoption of Australia's new OSCA 2024 and Singapore's SSOC 2024 gives JobIntel a significant statistical edge over platforms stuck on legacy ANZSCO.

### Identified Limitations & Risks
- **Heuristic Confidence Values:** Confidence numbers must not be advertised to external researchers as empirical posterior probabilities.
- **Unmapped Canonical Concepts:** 5 canonical concepts currently sit idle without mapped national occupations.
- **Indian Granularity Deficit:** NCO-2015 cannot natively isolate specialized technology roles without auxiliary keyword models.

### Actionable Roadmap for Sprint 3B (Cross-Market Salary Intelligence)
1. **Bind Remaining 14 National Occupations:** Complete concordance mappings for DBA, Systems Analyst, IT Project Manager, and Network Engineer across UK, US, AU, SG, and IN.
2. **Activate 5 Idle Canonical Concepts:** Link `CAN_OCC_DATA_ENGINEER`, `CAN_OCC_DATABASE_ADMIN`, `CAN_OCC_SYSTEMS_ANALYST`, `CAN_OCC_NETWORK_ENGINEER`, and `CAN_OCC_IT_PROJECT_MGR` to their corresponding national records.
3. **Calibrate Task Overlap Methodology:** Introduce an empirical Jaccard/TF-IDF task similarity calculator to replace pure expert heuristics with quantifiable task concordance metrics (`CALIBRATED_TASK_OVERLAP`).
4. **Enforce Cross-Market Salary Disclaimers:** When cross-market salary conversions are calculated in Sprint 3B, mandate that any pair with confidence $< 0.95$ or `PARTIAL_OVERLAP` automatically attaches an unavoidable statistical caveat flag to the payload.
5. **NCO Expansion Strategy:** For the Indian market, develop an explicit heuristic augmentation layer mapping Indian job descriptions to canonical concepts while retaining `IN_NCO_2015:2512.0100` as the underlying statutory reference code.

---
**Report Approved by:** Independent Audit Principal, JOBINTEL Architecture & Release Engineering  
**Signature:** `INDEPENDENT-AUDIT-VERIFIED-SPRINT3A1`
