# JOBINTEL 2.0 — SPRINT 3A
## Official Occupation Classification Research & National Standards Audit

**Date:** November 16, 2026  
**Sprint:** 3A  
**Status:** Approved Research Foundation  
**Author:** Occupational Taxonomy Researcher, Principal Data Architect  

---

## 1. Executive Research Summary

This report establishes the authoritative research baseline for occupational classification across JOBINTEL 2.0's five target labor markets (India, United States, United Kingdom, Australia, Singapore) and the International Labour Organization's ISCO-08 standard.

Every national statistical system reflects its domestic labor policy, educational credentialing, and industrial history. Naive string-matching or forcing classifications through a single legacy standard destroys essential jurisdictional truth. This document records the issuing authorities, active editions, coding hierarchies, licensing permissions, and specific technical characteristics of each official system.

---

## 2. Research Evidence Matrix

| Market | Official Classification | Current Edition | Issuing Authority | Hierarchy Levels & Depth | Code Format | Tech Sector Structure & Specificity | Official Crosswalks Available | Licensing & Reuse Terms |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **India** | National Classification of Occupations (NCO) | NCO-2015 | Ministry of Labour & Employment (DGE) | 5 Levels: Division (1d) $\to$ Sub-Div (2d) $\to$ Group (3d) $\to$ Family (4d) $\to$ Detailed (8d) | 4-digit to 8-digit numeric (e.g. `2512.0100`) | Division 2, Sub-Division 25 (ICT Professionals); limited granularity for modern cloud/ML | Direct official correspondence table to ISCO-08 at 4-digit level | National Data Sharing and Accessibility Policy (NDSAP) / Open Access with attribution |
| **United States** | Standard Occupational Classification (SOC) | 2018 SOC | Bureau of Labor Statistics (BLS), US Dept of Labor | 4 Levels: Major (2d) $\to$ Minor (3d) $\to$ Broad (5d) $\to$ Detailed (6d) | `XX-XXXX` (e.g. `15-1252` Software Developers) | Major Group 15 (Computer & Mathematical); 2018 added `15-2051` Data Scientists and separated QA testers | Official BLS 2010-to-2018 crosswalk; direct concordance to O*NET-SOC (granular decimals) | US Government Work / Public Domain (Free reuse worldwide) |
| **United Kingdom** | Standard Occupational Classification 2020 (SOC 2020) | SOC 2020 (Vol 1 & 2) | Office for National Statistics (ONS) | 4 Levels: Major (1d) $\to$ Sub-Major (2d) $\to$ Minor (3d) $\to$ Unit Group (4d) | 4-digit numeric (e.g. `2134` Programmers & software development professionals) | Sub-Major Group 21, Minor Group 213 (IT Professionals); separated Cyber Security (`2135`), QA (`2136`), Data Analysts (`3544`) | Official ONS SOC 2010 to SOC 2020 crosswalk; coding index with 30,000+ job title index entries | Open Government Licence v3.0 (OGL v3.0) / Free commercial and non-commercial reuse |
| **Australia** | Occupation Standard Classification for Australia (OSCA) | OSCA 2024 *(Transition from ANZSCO 2022)* | Australian Bureau of Statistics (ABS) & Jobs and Skills Australia (JSA) | 5 Levels: Major (1d) $\to$ Sub-Major (2d) $\to$ Minor (3d) $\to$ Unit Group (4d) $\to$ Detailed (6d) | 6-digit numeric (e.g. `261313` Software Engineer) | Sub-Major Group 26 (ICT Professionals); newly modernized in late 2024 with dedicated cloud, cybersecurity, and data science unit groups | Official ABS ANZSCO 2022 to OSCA 2024 correspondence tables | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Singapore** | Singapore Standard Occupational Classification (SSOC) | SSOC 2024 *(Transition from SSOC 2020)* | Singapore Department of Statistics (SingStat) & Ministry of Manpower (MOM) | 5 Levels: Major (1d) $\to$ Sub-Major (2d) $\to$ Minor (3d) $\to$ Unit Group (4d) $\to$ Detailed (5d) | 5-digit numeric (e.g. `25121` Software Developer) | Sub-Major Group 25 (ICT Professionals); highly granular 2024 additions for AI/ML (`25131`), Data Science (`25132`), DevOps (`25125`), Cloud (`25124`) | Official SingStat SSOC 2020 to SSOC 2024 correspondence; SSOC to ISCO-08 correspondence | Singapore Open Data Licence (Permits commercial exploitation with attribution) |
| **International** | International Standard Classification of Occupations (ISCO) | ISCO-08 | International Labour Organization (ILO) | 4 Levels: Major (1d) $\to$ Sub-Major (2d) $\to$ Minor (3d) $\to$ Unit Group (4d) | 4-digit numeric (e.g. `2512` Software Developers) | Sub-Major Group 25; monolithic 2008 grouping collapses modern software specializations into single codes | Official correspondence tables to NCO-2015, US SOC, SSOC, and UK SOC 2010 | United Nations / ILO public statistical documentation |

---

## 3. Jurisdiction-by-Jurisdiction Deep Dive

### 3.1 India: National Classification of Occupations (NCO-2015)
- **Authority:** Directorate General of Employment (DGE), Ministry of Labour and Employment, Government of India.
- **Publication & Effective Context:** Released in 2015 to align national vocational statistics with the ILO’s ISCO-08 framework. It supersedes NCO-2004 and NCO-1968.
- **Structure:**
  - 1-Digit: Divisions (10 divisions)
  - 2-Digit: Sub-Divisions (43 sub-divisions)
  - 3-Digit: Groups (133 groups)
  - 4-Digit: Families (438 families)
  - 8-Digit: Detailed Occupations (2,957 occupations)
- **Key Technology Families:**
  - `2511`: Systems Analysts (e.g. `2511.0100` Systems Analyst, `2511.0200` Software Architect)
  - `2512`: Software Developers (e.g. `2512.0100` Software Developer, `2512.0200` Applications Programmer, `2512.0300` Web Developer)
  - `2513`: Web and Multimedia Developers
  - `2514`: Applications Programmers
  - `2519`: Software and Applications Developers and Analysts Not Elsewhere Classified
  - `2521`: Database Designers and Administrators (`2521.0100` Database Administrator)
  - `2522`: Systems Administrators
  - `2523`: Computer Network Professionals
  - `2529`: Database and Network Professionals Not Elsewhere Classified
- **Limitations:** NCO-2015 captures traditional software development well, but lacks dedicated unit codes for modern roles like Machine Learning Engineer, Cloud/DevOps Architect, or Site Reliability Engineer. In Indian private enterprise and JobIntel's salary dataset, employers rely on industry title conventions rather than formal NCO-2015 codes.

### 3.2 United States: 2018 Standard Occupational Classification (2018 SOC)
- **Authority:** Standard Occupational Classification Policy Committee (SOCPC), Office of Management and Budget (OMB), and Bureau of Labor Statistics (BLS).
- **Publication & Effective Context:** Released in 2018 following multi-year federal review; fully integrated into OEWS (Occupational Employment and Wage Statistics) and ACS (American Community Survey).
- **Structure:**
  - 23 Major Groups (`11-0000` through `55-0000`)
  - 98 Minor Groups
  - 459 Broad Occupations
  - 867 Detailed Occupations
- **Core Technology Occupations (Major Group 15):**
  - `15-1211`: Computer Systems Analysts
  - `15-1212`: Information Security Analysts
  - `15-1221`: Computer and Information Research Scientists
  - `15-1231`: Computer User Support Specialists
  - `15-1232`: Computer Network Support Specialists
  - `15-1241`: Computer Network Architects
  - `15-1242`: Database Administrators
  - `15-1243`: Database Architects *(new in 2018)*
  - `15-1244`: Network and Computer Systems Administrators
  - `15-1251`: Computer Programmers
  - `15-1252`: Software Developers *(merges 2010 Applications and Systems Software Developers)*
  - `15-1253`: Software Quality Assurance Analysts and Testers *(new in 2018)*
  - `15-1254`: Web Developers
  - `15-1255`: Web and Digital Interface Designers
  - `15-1299`: Computer Occupations, All Other
  - `15-2051`: Data Scientists *(major 2018 addition; previously scattered under Statisticians or Computer Scientists)*
- **SOC vs. O*NET-SOC:** O*NET extends the 6-digit federal SOC with 2-digit decimal suffixes (e.g. `15-1252.00` Software Developers, `15-2051.01` Business Intelligence Analysts, `15-2051.02` Clinical Data Managers). For national classification governance in JOBINTEL 2.0, **2018 SOC 6-digit codes** are the authoritative federal standard.

### 3.3 United Kingdom: UK SOC 2020
- **Authority:** Office for National Statistics (ONS).
- **Publication & Effective Context:** Developed in partnership with the Warwick Institute for Employment Research. Volume 1 provides the structure, definitions, entry routes, tasks, and qualification requirements. Volume 2 provides the coding index.
- **Structure:**
  - 9 Major Groups
  - 26 Sub-Major Groups
  - 90 Minor Groups
  - 412 Unit Groups
- **Key Modern Technology Unit Groups:**
  - `1136`: Information technology and telecommunications directors
  - `2131`: IT project managers
  - `2132`: IT managers
  - `2133`: IT business analysts, architects and systems designers
  - `2134`: Programmers and software development professionals
  - `2135`: Cyber security professionals *(introduced in SOC 2020 to separate cybersecurity from general network admin)*
  - `2136`: IT quality and testing professionals
  - `2137`: IT network professionals
  - `2139`: Information technology professionals n.e.c.
  - `3131`: IT technicians
  - `3132`: IT user support technicians
  - `3133`: Database administrators and web content technicians
  - `3544`: Data analysts *(newly classified in SOC 2020, recognizing the rise of business/data analytics)*
- **Local Asset Verification:** The repository already holds the verified official Excel source: `data/raw/ashe_table15_2025_revised/soc2020_reference/soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx`, providing verified definitions, tasks, entry qualifications, and 412 unit groups.

### 3.4 Australia: OSCA 2024 & ANZSCO 2022
- **Authority:** Australian Bureau of Statistics (ABS) and Jobs and Skills Australia (JSA).
- **Historical Transition:**
  - For nearly two decades, Australia and New Zealand shared ANZSCO (Australian and New Zealand Standard Classification of Occupations, established 2006).
  - In late 2024, the ABS and JSA formally launched **OSCA 2024** (Occupation Standard Classification for Australia) as a modern, dedicated Australian standard, addressing longstanding deficits in modern digital, cybersecurity, data, and clean energy roles.
- **Structure:** 6-digit hierarchical structure (Major $\to$ Sub-Major $\to$ Minor $\to$ Unit Group $\to$ Occupation).
- **Key ICT Occupations (Sub-Major Group 26):**
  - Unit Group `2611`: ICT Business and Systems Analysts (`261111` ICT Business Analyst, `261112` Systems Analyst)
  - Unit Group `2613`: Software and Applications Programmers (`261311` Analyst Programmer, `261312` Developer Programmer, `261313` Software Engineer, `261314` Software Tester, `261317` Penetration Tester)
  - Unit Group `2621`: Database and Systems Administrators and ICT Security Specialists (`262111` Database Administrator, `262112` ICT Security Specialist, `262113` Systems Administrator)
  - Unit Group `2631`: Computer Network Professionals (`263111` Computer Network and Systems Engineer, `263112` Network Administrator, `263113` Network Analyst)
  - Unit Group `2244`: Data Scientists and Advanced Analysts *(OSCA 2024 modernized definition)*
- **Governance Requirement:** OSCA 2024 and ANZSCO 2022 must be tracked as distinct classification systems with distinct `classification_id`s. Correspondence tables published by the ABS provide the authoritative crosswalk.

### 3.5 Singapore: SSOC 2024
- **Authority:** Singapore Department of Statistics (SingStat), Ministry of Trade and Industry, and Ministry of Manpower (MOM).
- **Publication & Effective Context:** Released in 2024 following triennial national review. It updates SSOC 2020 to reflect Singapore’s National AI Strategy 2.0 and regional tech hub status.
- **Structure:**
  - 1-Digit: Major Groups (1 to 9)
  - 2-Digit: Sub-Major Groups
  - 3-Digit: Minor Groups
  - 4-Digit: Unit Groups
  - 5-Digit: Detailed Occupations
- **Key Technology Occupations (Sub-Major Group 25):**
  - `25111`: Chief Information Officer / Chief Technology Officer
  - `25112`: ICT Project Manager
  - `25121`: Software Developer
  - `25122`: Applications Programmer
  - `25123`: Web and Mobile Applications Developer
  - `25124`: Cloud Architect / Cloud Engineer *(explicit 2024 title)*
  - `25125`: DevOps Engineer *(explicit 2024 title)*
  - `25131`: Artificial Intelligence / Machine Learning Engineer *(explicit 2024 title)*
  - `25132`: Data Scientist *(explicit 2024 title)*
  - `25141`: Database Administrator / Data Engineer
  - `25211`: Cybersecurity Specialist / Information Security Analyst
  - `25221`: Network and Systems Administrator

---

## 4. The International Standard (ILO ISCO-08) & Mapping Limitations

1. **Role of ISCO-08 in JOBINTEL 2.0:**
   - ISCO-08 serves as an **informative cross-national reference point**, NOT a computationally binding pivot.
   - Most national agencies (DGE India, SingStat, ONS) provide an official concordance table from their domestic classification to ISCO-08.
2. **Why Universal Pivot Mapping via ISCO-08 Fails for Modern Tech:**
   - In ISCO-08, Unit Group `2512` ("Software Developers") includes:
     - Applications programmers
     - Systems software developers
     - Mobile app developers
     - Cloud engineers
     - DevOps engineers
   - If UK SOC 2020 `2134` (Programmers & software developers), US SOC `15-1252` (Software Developers), AU OSCA `261313` (Software Engineer), and SG SSOC `25121` (Software Developer) are all mapped into ISCO `2512`, the mapping appears 1:1 at the ISCO level.
   - However, when SG SSOC `25124` (Cloud Architect) or `25125` (DevOps Engineer) is mapped to ISCO `2512`, an inverse query from ISCO `2512` back to the UK would falsely imply that UK `2134` is an exact match for a Cloud Architect, even though the UK ONS specifically maps Cloud Infrastructure Architects into UK SOC `2133` (IT business analysts, architects and systems designers)!
   - **Conclusion:** Point-to-point concordance tables with explicit relationship types (`EXACT_MATCH`, `BROADER_THAN`, `NARROWER_THAN`, `PARTIAL_OVERLAP`) are mathematically and empirically required to avoid false transitive equivalence.

---

## 5. Unresolved Questions & Next Steps

1. **India National Occupation Codes vs. Job Market Realities:**
   - India's NCO-2015 is rarely used in private-sector IT job descriptions or ATS portals. To bridge this, JOBINTEL 2.0 must maintain both:
     a) Official `IN_NCO_2015` classification records.
     b) An explicit, documented crosswalk between JobIntel's verified India role families (`AI / ML Engineer`, `Data Scientist`, `Software Engineer`, etc.) and the formal NCO-2015 unit groups.
2. **USA O*NET vs. Federal 2018 SOC:**
   - The primary national classification for US federal labor economics is `US_SOC_2018` (6-digit). O*NET 8-digit extensions should be recorded as occupational aliases and task descriptions, preserving 6-digit SOC as the classification spine.
3. **Continuous Versioning Support:**
   - Australia's transition from ANZSCO 2022 to OSCA 2024 and Singapore's transition from SSOC 2020 to SSOC 2024 require that our data architecture supports historical versions simultaneously without key collisions.
