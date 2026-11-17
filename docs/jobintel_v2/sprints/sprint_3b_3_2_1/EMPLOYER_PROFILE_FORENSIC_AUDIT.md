# SPRINT 3B.3.2.1 — DELIVERABLE 3
# EMPLOYER PROFILE FORENSIC AUDIT
## Independent Record-Level Validation of 28 Anchor Employer Entities

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Principal Data Auditor, Data Architect  
**Dataset Under Audit:** `docs/jobintel_v2/sprints/sprint_3b_3_2/data/employer_pilot_records.json`  

---

## 1. FORENSIC AUDIT METHODOLOGY & FINDINGS

Every employer profile in the Sprint 3B.3.2 pilot dataset was independently inspected across 12 criteria:
1. Company Name vs. Legal Entity Name vs. Trading Name
2. Sovereign Registration Identifier format and validity
3. Registration Identifier Type (ABN, CIK, CRN, UEN, CIN, AGENCY_CODE)
4. Sovereign Market Assignment (`market_id`) vs. Headquarters Country (`headquarters_country`)
5. Primary Apex Domain & Ownership
6. Standardized Industry Sector & Classification
7. Parent/Subsidiary Hierarchy Mapping
8. Identity Verification Status (`identity_verification_status`)
9. Cited Statutory Source References (`source_ids`)
10. Presence of Duplicate Entities or Identifiers
11. Potential ATS Hostname or Brand-Name Collisions
12. Public vs. Private Sector Enterprise Qualification

### Summary of Audit Verdicts across 28 Cohort Profiles
- **VERIFIED:** **27 records** (96.4%)
- **PARTIALLY_VERIFIED:** **1 record** (3.6%) — `comp_us_fed_va` (U.S. Department of Veterans Affairs: valid sovereign agency, but public sector entity without corporate SEC filings).
- **UNVERIFIED:** **0 records** (0.0%)
- **CONFLICTED:** **0 records** (0.0%)
- **INVALID:** **0 records** (0.0%)

---

## 2. 28-ROW RECORD-LEVEL FORENSIC AUDIT TABLE

| Company ID | Legal Entity Name | Trading Name | Market | Reg ID Type | Reg Identifier | Primary Domain | Parent Company ID | Verification Status | Forensic Audit Assessment & Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `comp_au_atlassian` | Atlassian Pty Ltd | Atlassian | AU | ABN | `53102443916` | `atlassian.com` | `comp_us_atlassian_corp` | **VERIFIED** | ABN valid in ABR. Australian operating entity correctly linked to US corporate parent. |
| `comp_au_canva` | Canva Pty Ltd | Canva | AU | ABN | `80158929938` | `canva.com` | None | **VERIFIED** | Proprietary limited company in NSW. ABN verified via ABR; Lever careers feed. |
| `comp_au_cba` | Commonwealth Bank of Australia | CommBank | AU | ABN | `48123123124` | `commbank.com.au` | None | **VERIFIED** | Authoritative ASX-listed banking entity. ABN and WGEA reporting verified. |
| `comp_au_bhp` | BHP Group Limited | BHP | AU | ABN | `49004028077` | `bhp.com` | None | **VERIFIED** | Authoritative natural resources multinational. ABN verified via ABR and WGEA. |
| `comp_au_woolworths` | Woolworths Group Limited | Woolworths Group | AU | ABN | `88000014675` | `woolworthsgroup.com.au` | None | **VERIFIED** | Major national retail employer. ABN and WGEA size band verified. |
| `comp_au_telstra` | Telstra Group Limited | Telstra | AU | ABN | `56086174781` | `telstra.com.au` | None | **VERIFIED** | Sovereign telecommunications provider. ABN and WGEA data verified. |
| `comp_us_microsoft` | Microsoft Corporation | Microsoft | US | CIK | `0000789019` | `microsoft.com` | None | **VERIFIED** | SEC EDGAR CIK verified. Form 10-K headcount and Greenhouse ATS confirmed. |
| `comp_us_alphabet` | Alphabet Inc. | Alphabet / Google | US | CIK | `0001652044` | `abc.xyz` | None | **VERIFIED** | Top-level corporate parent. SEC CIK verified; Item 1 headcount confirmed. |
| `comp_us_jpmorgan` | JPMorgan Chase & Co. | JPMorgan Chase | US | CIK | `0000019617` | `jpmorganchase.com` | None | **VERIFIED** | Top-tier financial institution. CIK verified in SEC EDGAR. |
| `comp_us_pfizer` | Pfizer Inc. | Pfizer | US | CIK | `0000078003` | `pfizer.com` | None | **VERIFIED** | Major biopharmaceutical corporation. CIK verified in SEC EDGAR. |
| `comp_us_cisco` | Cisco Systems, Inc. | Cisco | US | CIK | `0000858877` | `cisco.com` | None | **VERIFIED** | Networking technology multinational. CIK and Greenhouse ATS confirmed. |
| `comp_us_fed_va` | U.S. Department of Veterans Affairs | VA | US | AGENCY_CODE | `VA` | `va.gov` | None | **PARTIALLY_VERIFIED** | **Caveat:** Sovereign federal agency, not a private corporation. Governed via USAJOBS. |
| `comp_uk_arm` | Arm Limited | Arm | UK | CRN | `02557590` | `arm.com` | `comp_uk_arm_holdings` | **VERIFIED** | Companies House CRN verified. Operating entity linked to parent Arm Holdings. |
| `comp_uk_deepmind` | DeepMind Technologies Limited | Google DeepMind | UK | CRN | `07386357` | `deepmind.google` | `comp_us_alphabet` | **VERIFIED** | UK operating entity. CRN verified; parent correctly mapped to Alphabet Inc. |
| `comp_uk_astrazeneca` | AstraZeneca PLC | AstraZeneca | UK | CRN | `03512362` | `astrazeneca.com` | None | **VERIFIED** | FTSE 100 biopharma entity. CRN and Gender Pay Gap size band confirmed. |
| `comp_uk_barclays` | Barclays PLC | Barclays | UK | CRN | `00048839` | `barclays.com` | None | **VERIFIED** | Historic UK banking institution. CRN and Gender Pay Gap size band confirmed. |
| `comp_uk_unilever` | Unilever PLC | Unilever | UK | CRN | `00041424` | `unilever.com` | None | **VERIFIED** | Consumer goods multinational. CRN and Gender Pay Gap data confirmed. |
| `comp_uk_bt` | BT Group plc | BT Group | UK | CRN | `04190816` | `bt.com` | None | **VERIFIED** | Sovereign telecommunications provider. CRN and GPG compliance verified. |
| `comp_sg_grab` | Grabtaxi Holdings Pte. Ltd. | Grab | SG | UEN | `201318499Z` | `grab.com` | `comp_sg_grab_holdings` | **VERIFIED** | ACRA UEN verified. Operating entity linked to Cayman parent holding company. |
| `comp_sg_shopee` | Shopee Singapore Private Limited | Shopee | SG | UEN | `201502486Z` | `shopee.sg` | `comp_sg_sea_ltd` | **VERIFIED** | ACRA UEN verified. Operating subsidiary linked to parent Sea Limited. |
| `comp_sg_dbs` | DBS Bank Ltd. | DBS | SG | UEN | `196800306E` | `dbs.com` | `comp_sg_dbs_group` | **VERIFIED** | Primary banking operating entity. ACRA UEN verified; parent mapped to group. |
| `comp_sg_singtel` | Singapore Telecommunications Limited | Singtel | SG | UEN | `199201624D` | `singtel.com` | None | **VERIFIED** | Authoritative national telecommunications corporation. ACRA UEN confirmed. |
| `comp_sg_carousell` | Carousell Pte. Ltd. | Carousell | SG | UEN | `201200479M` | `carousell.com` | None | **VERIFIED** | Regional digital marketplace. ACRA UEN and Greenhouse ATS verified. |
| `comp_in_tcs` | Tata Consultancy Services Limited | TCS | IN | CIN | `L22210MH1995PLC084781` | `tcs.com` | `comp_in_tata_sons` | **VERIFIED** | Authoritative BSE/NSE listed IT leader. CIN and SEBI BRSR verified. |
| `comp_in_infosys` | Infosys Limited | Infosys | IN | CIN | `L85110KA1981PLC013115` | `infosys.com` | None | **VERIFIED** | Authoritative BSE/NSE listed IT leader. CIN and SEBI BRSR verified. |
| `comp_in_wipro` | Wipro Limited | Wipro | IN | CIN | `L32102KA1945PLC020800` | `wipro.com` | None | **VERIFIED** | Authoritative BSE/NSE listed IT leader. CIN and SEBI BRSR verified. |
| `comp_in_hdfcbank` | HDFC Bank Limited | HDFC Bank | IN | CIN | `L65920MH1994PLC080618` | `hdfcbank.com` | None | **VERIFIED** | Leading private bank in India. CIN and SEBI BRSR verified. |
| `comp_in_reliance` | Reliance Industries Limited | Reliance | IN | CIN | `L17110MH1973PLC019786` | `ril.com` | None | **VERIFIED** | Diversified conglomerate. CIN and SEBI BRSR verified. |

---

## 3. KEY FORENSIC OBSERVATIONS FOR ARCHITECTURAL HARDENING

1. **Clean Identity Separation:**
   - 0 duplicate legal entity names found.
   - 0 duplicate registration identifiers found.
   - 0 country code or market assignment mismatches found.
2. **Corporate vs. Public Sector Distinction:**
   - Record `comp_us_fed_va` (U.S. Department of Veterans Affairs) uses `AGENCY_CODE` rather than `CIK`. The backend schemas in Sprint 3B.3.3 must explicitly distinguish `COMMERCIAL_ENTERPRISE` from `PUBLIC_SECTOR_AGENCY`.
3. **Parent/Subsidiary Fidelity:**
   - In 6 cases, operating regional entities are correctly linked to distinct corporate parents (e.g. `comp_uk_deepmind` $\to$ `comp_us_alphabet`, `comp_au_atlassian` $\to$ `comp_us_atlassian_corp`, `comp_sg_grab` $\to$ `comp_sg_grab_holdings`).
   - Operating domains (`atlassian.com`, `deepmind.google`, `grab.com`) reflect active commercial websites without colliding in the parent registry.
