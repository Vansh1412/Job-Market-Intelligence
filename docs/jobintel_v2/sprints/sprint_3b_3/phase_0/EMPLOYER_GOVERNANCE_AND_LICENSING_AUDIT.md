# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER GOVERNANCE, INTELLECTUAL PROPERTY & LEGAL AUDIT
### Statutory Data Rights, Web Scraping Jurisprudence, PII Elimination, Terms of Service Compliance & Publication Gating

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-LEGAL-GOVERNANCE-AUDIT`  
**Execution Phase:** Phase 0 (Legal, Governance & Regulatory Compliance Audit)  
**Date of Audit:** 2026-11-17  
**Guiding Principle:** Strict adherence to data privacy statutes, database directives, contract law, and fail-closed publication gating.

---

## 1. LEGAL & INTELLECTUAL PROPERTY LANDSCAPE

Acquiring and publishing employer intelligence requires navigating four distinct legal domains:
1. **Government Open Data Licences:** Authoritative public registers released under statutory open licences.
2. **Website Terms of Service & Contract Law:** Legal boundaries surrounding automated web collection and commercial use of private web portals.
3. **Database Rights & Copyright Statutes:** *Sui generis* database protection (EU/UK) and compilation copyright.
4. **Data Privacy & Personal Identifiable Information (PII) Statutes:** GDPR (EU/UK), DPDP Act 2023 (India), CCPA/CPRA (California), and PDPA (Singapore).

---

## 2. JURISPRUDENCE & WEB COLLECTION CASE LAW AUDIT

### A. United States Jurisprudence: The CFAA vs Breach of Contract Dichotomy
- ***hiQ Labs, Inc. v. LinkedIn Corp.* (9th Cir. 2022):** The Ninth Circuit reaffirmed that automated scraping of publicly available web data that is not behind a password gate does not violate the Computer Fraud and Abuse Act (CFAA) under 18 U.S.C. § 1030 (*"access without authorization"*).
- ***Meta Platforms, Inc. v. Bright Data Ltd.* (N.D. Cal. 2024):** While CFAA claims failed, the court addressed state-law **breach of contract** claims. When a user creates an account or accepts terms, the contract is enforceable. However, for logged-out scrapers that never consented to terms of service, breach of contract claims face substantial legal hurdles.
- ***Ryanair Designated Activity Co. v. PR Aviation BV* (EU CJEU 2015):** The Court of Justice of the European Union ruled that contractual prohibitions on scraping can be legally binding even for unprotected public data if the user accepts the terms.
- **JobIntel Policy Directive:** **ZERO UNAPPROVED COMMERCIAL WEB SCRAPING.** JobIntel will not employ headless scraping agents against platforms with explicit anti-scraping terms (Indeed, LinkedIn, Naukri). All recruitment data must originate from:
  1. Direct, permissive employer ATS JSON endpoints (e.g. Greenhouse public job board APIs).
  2. Public domain government databases.
  3. Authorized third-party data partnership feeds.

---

### B. European & UK *Sui Generis* Database Rights
- **Directive 96/9/EC on the Legal Protection of Databases / UK Copyright and Rights in Databases Regulations 1997:**
  - In the UK and EU, substantial investment in obtaining, verifying, or presenting contents creates a *sui generis* database right.
  - Extracting or re-utilizing a "substantial part" of a commercial job board database without authorization constitutes database infringement, regardless of whether copyright applies.
- **JobIntel Safeguard:** The UK publication gate established in Sprint 3B.2 (`UK_DEMAND_DATA_NOT_PUBLISHED`) is permanently maintained for proprietary commercial job board feeds (e.g. Textkernel). UK employer data is strictly sourced from **Companies House (OGL v3.0)** and certified public sponsor registers.

---

## 3. ABSOLUTE PII ELIMINATION & PRIVACY SAFEGUARDS

Under the General Data Protection Regulation (GDPR), UK Data Protection Act 2018, India's Digital Personal Data Protection Act 2023 (DPDP), and California Consumer Privacy Act (CCPA):
1. **Personal Data Definition:** Any information relating to an identified or identifiable natural person.
2. **The Inherent Risk in Job Postings:**
   - Job postings frequently contain recruiter names, talent acquisition email addresses, hiring manager telephone numbers, and executive bios.
   - Company registration filings often contain personal residential addresses of company directors or registered agents of small LLCs.

> [!CAUTION]
> **MANDATORY PII ELIMINATION PROTOCOL:**  
> 1. **Zero Personal Contact Storage:** Recruiter names, emails, direct telephone lines, and personal LinkedIn handles must be discarded at the ingestion parser level before database persistence.  
> 2. **Physical Address Sanitization:** Full street addresses (e.g. *"14 Elm Street, Apt 4B"*) are permanently scrubbed. Only municipality, administrative state/region, and country are retained.  
> 3. **Sole Proprietor Exclusion:** Micro-entities where the legal entity name is an individual's personal name (e.g., *"John Doe Consulting"*) are tagged `EXCLUDE_INDIVIDUAL_PROPRIETOR` to prevent publishing personal data under the guise of corporate intelligence.

---

## 4. SIX SOURCE APPROVAL STATES & GOVERNANCE GATES

Every data source feeding the Global Employer Intelligence module must have an explicit legal record in `src/backend/config/employer_sources_manifest.json` under one of six discrete states:

```
                  +--------------------------------+
                  |            UNKNOWN             |
                  +---------------+----------------+
                                  | Initial discovery
                                  v
                  +--------------------------------+
                  |        REVIEW_REQUIRED         |
                  +---------------+----------------+
                                  | Legal evaluation
                 +----------------+----------------+
                 |                                 |
                 v                                 v
  +------------------------------+  +------------------------------+
  |         CONDITIONAL          |  |           APPROVED           |
  | (e.g. Non-commercial,       |  | (e.g. OGL v3.0, CC BY 4.0,   |
  |  attribution mandatory,      |  |  US Public Domain, full      |
  |  internal caching only)      |  |  commercial SaaS rights)     |
  +--------------+---------------+  +--------------+---------------+
                 |                                 |
                 +----------------+----------------+
                                  | License change / Terms breach
                                  v
                  +--------------------------------+
                  |       EXPIRED / REVOKED        |
                  | (Fail-closed API rejection;    |
                  |  instant UI withholding)       |
                  +--------------------------------+
```

### Definitions:
1. **`UNKNOWN`:** Ingested source with unassessed licensing. Data is blocked from production exposure.
2. **`REVIEW_REQUIRED`:** Source identified but undergoing formal legal and intellectual property evaluation.
3. **`CONDITIONAL`:** Permitted for specific uses (e.g., academic analysis or research preview), but subject to operational constraints (e.g. display allowed only with explicit attribution; no raw bulk redistribution).
4. **`APPROVED`:** Fully validated open-access source permitting commercial SaaS integration, transformation, and distribution (e.g. Companies House OGL v3.0, WGEA Australia CC BY 4.0, SEC EDGAR Public Domain).
5. **`EXPIRED`:** Source license or authorization agreement has reached its termination date without renewal.
6. **`REVOKED`:** Source license rescinded or cease-and-desist issued. Triggered immediately by the centralized **Revocation Manifest** (`src/backend/config/revocation_manifest.json`).

---

## 5. SOURCE APPROVAL & SCOPING SPECIFICATION

An approved source entry in the governance manifest must specify exact operational boundaries:

```json
{
  "source_id": "uk.gov.companies_house",
  "source_name": "Companies House Public Data API",
  "publisher": "Companies House (UK Department for Business and Trade)",
  "canonical_url": "https://api.company-information.service.gov.uk",
  "license": "Open Government Licence v3.0",
  "approval_state": "APPROVED",
  "approved_scopes": {
    "permitted_purposes": ["RESEARCH", "COMMERCIAL_SAAS_ANALYTICS", "BENCHMARKING"],
    "storage_rights": "UNRESTRICTED_LOCAL_PERSISTENCE",
    "display_rights": "PUBLIC_INTERACTIVE_UI",
    "redistribution_rights": "AGGREGATED_AND_DERIVED_METRICS",
    "commercial_use": true,
    "pii_risk_tier": "LOW",
    "attribution_requirement": "Contains public sector information licensed under the Open Government Licence v3.0."
  },
  "revocation_trigger": "UPSTREAM_TERMS_REVISION"
}
```

**Audit Status:** `PASS — GOVERNANCE AND LEGAL AUDIT COMPLETE`
