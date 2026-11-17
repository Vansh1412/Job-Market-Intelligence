# SPRINT 3B.3.2.1 — DELIVERABLE 4
# SOURCE AUTHORIZATION FORENSIC AUDIT
## Independent Verification of 14 Data Sources, Licensing Permissions & Contradiction Analysis

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Data Governance Specialist, Legal/Licensing Auditor  
**Dataset Under Audit:** `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_source_catalog.json`  
**Crosswalk Generated:** `docs/jobintel_v2/sprints/sprint_3b_3_2_1/OBSERVATION_TO_SOURCE_CROSSWALK.csv`  

---

## 1. SOURCE CATALOG VERIFICATION SUMMARY

All 14 sources defined in the Sprint 3B.3.2 catalog were independently audited across primary publisher documentation, access protocols, statutory mandates, licensing frameworks, commercial reuse rights, and storage/redistribution terms.

```
+----------------------------------------------------------------------------------------------------+
| SOURCE CATALOG STATUS SUMMARY                                                                      |
+---------------------+---------------------------------+--------------------+-----------------------+
| Category Status     | Claimed in Sprint 3B.3.2 Report | Audit Verified     | Variance / Discrepancy|
+---------------------+---------------------------------+--------------------+-----------------------+
| APPROVED            | 11 sources                      | 11 sources         | 0 (Exact Match)       |
| REVIEW_REQUIRED     | 2 sources                       | 2 sources          | 0 (Exact Match)       |
| REVOKED             | 1 source                        | 1 source           | 0 (Exact Match)       |
| Total Sources       | 14 sources                      | 14 sources         | 0 (Full Reconciled)   |
+---------------------+---------------------------------+--------------------+-----------------------+
```

---

## 2. DETAILED 14-SOURCE AUDIT TABLE

| Source ID | Publisher & Country | License Framework | Access / Auth Method | Commercial Use? | Attribution Required? | Audit Status | Audit Assessment & Governance Citation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `src_au_wgea` | Workplace Gender Equality Agency (AU) | CC BY 4.0 International | Bulk CSV / No Auth | **Yes** | Yes (WGEA citation) | **APPROVED** | Authoritative statutory employer workforce size bands. Open government license. |
| `src_au_abr` | Australian Taxation Office (AU) | data.gov.au Terms / CC BY 3.0 AU | Bulk XML / No Auth | **Yes** | Yes (ABR citation) | **APPROVED** | Sovereign Australian Business Register. Authoritative for ABN and legal names. |
| `src_us_sec_edgar` | U.S. Securities & Exchange Commission (US) | U.S. Public Domain (17 U.S.C. § 105)| REST API / User-Agent | **Yes** | None (Public Domain)| **APPROVED** | Sovereign US federal filings (Forms 10-K). Authoritative for exact headcount and CIK. |
| `src_us_usajobs` | U.S. Office of Personnel Management (US) | U.S. Public Domain / Open Data Policy| REST API / Auth Token | **Yes** | None (Public Domain)| **APPROVED** | Sovereign federal employment postings. Restricted to public sector entities. |
| `src_uk_companies_house` | Companies House (UK) | Open Government Licence v3.0 (OGL) | REST API / API Key | **Yes** | Yes (OGL citation) | **APPROVED** | Authoritative statutory UK corporate registry. Real-time verification of CRN and PSC. |
| `src_uk_gender_pay_gap` | Government Equalities Office (UK) | Open Government Licence v3.0 (OGL) | Bulk CSV / No Auth | **Yes** | Yes (OGL citation) | **APPROVED** | Authoritative statutory headcount size reporting for employers with $\ge 250$ staff. |
| `src_sg_acra` | ACRA via data.gov.sg (SG) | Singapore Open Data Licence v1.0 | Bulk CSV / API Key | **Yes** | Yes (SODL citation)| **APPROVED** | Authoritative Singapore business registry directory for UEN and corporate status. |
| `src_in_sebi_brsr` | SEBI via BSE & NSE (IN) | Public Regulatory Disclosures | PDF/XBRL Filings | **Yes** | Yes (SEBI citation) | **APPROVED** | Mandatory audited Business Responsibility & Sustainability Reporting for listed firms. |
| `src_first_party_greenhouse`| Greenhouse Software / Employers | Direct Employer Career Terms | Public JSON Endpoint | **Conditional** | Yes (Company portal)| **APPROVED** | Direct first-party employer-authorized vacancy feed. No scraping involved. |
| `src_first_party_lever` | Lever Inc. / Employers | Direct Employer Career Terms | Public JSON Endpoint | **Conditional** | Yes (Company portal)| **APPROVED** | Direct first-party employer-authorized vacancy feed. No scraping involved. |
| `src_global_lightcast_skills`| Lightcast (formerly Emsi BG) | CC BY 4.0 International | Open API / CC Terms | **Yes** | Yes (Lightcast) | **APPROVED** | Open-source taxonomy for skill normalization. Verified CC BY license. |
| `src_sg_mycareersfuture` | Workforce Singapore (SG) | Website Terms of Use (Anti-scraping)| HTML Scraping | **No** | Yes | **REVIEW_REQUIRED**| Anti-scraping clause in Terms of Use. Permitted only if official partner API is granted. |
| `src_in_mca21` | Ministry of Corporate Affairs (IN) | NDSAP / Portal Terms | CAPTCHA Gated Portal | **No** | Yes | **REVIEW_REQUIRED**| Automated ingestion blocked by anti-bot challenge and session expiration. |
| `src_commercial_aggregators`| LinkedIn, Indeed, Naukri, Seek | Proprietary Commercial Terms | HTML Scraping | **No** | N/A | **REVOKED** | **STRICTLY PROHIBITED.** Terms of Service Section 8 violation, CFAA and anti-bot risk. |

---

## 3. CRITICAL CONTRADICTION AUDIT: CLAIM VS. RECORD-LEVEL EVIDENCE

### The Potential Contradiction
In Sprint 3B.3.2, the report asserted:
> *"The pilot uses 100% authorized statutory and direct ATS feeds."*

Yet the same report qualified `src_sg_mycareersfuture` and `src_in_mca21` as `REVIEW_REQUIRED`, and `src_commercial_aggregators` as `REVOKED`.

### Record-Level Investigation
Every individual observation in `employer_hiring_observations.json` (32 observations) and `employer_skill_observations.json` (22 observations) was cross-referenced against the source catalog to determine whether any observation was derived from a non-approved source.

The complete crosswalk is documented in [OBSERVATION_TO_SOURCE_CROSSWALK.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2_1/OBSERVATION_TO_SOURCE_CROSSWALK.csv).

### Findings of the Investigation
1. **Zero Observations from REVOKED Sources:**  
   $0$ of $54$ observations depend on `src_commercial_aggregators` (LinkedIn, Indeed, Naukri, Seek). Commercial scraping was completely avoided.
2. **Zero Observations from REVIEW_REQUIRED Sources:**  
   $0$ of $54$ observations depend on `src_sg_mycareersfuture` or `src_in_mca21`. In Singapore, vacancy flow was obtained via direct Greenhouse/Lever feeds (`comp_sg_grab`, `comp_sg_carousell`, `comp_sg_shopee`), while registry data was obtained from `src_sg_acra`. In India, corporate data was obtained from audited `src_in_sebi_brsr` filings, avoiding the gated MCA21 portal.
3. **100% of Pilot Data Sourced from APPROVED Sources:**  
   All $54$ observations are traced exclusively to the 11 `APPROVED` sources.
4. **Governance Gate Fully Respected:**  
   Observation `obs_uk_deepmind_vacancies` carries `publication_gate_active: true`, correctly withholding UK vacancy metrics in strict adherence to governance policies.

**Verdict on Contradiction Audit:** **`NO CONTRADICTION FOUND`**. The claim of 100% authorized source usage is empirically substantiated at the record level.
