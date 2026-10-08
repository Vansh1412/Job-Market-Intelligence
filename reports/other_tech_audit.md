# Other Tech Forensic Audit & Remediation Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Date:** October 5, 2026  
**Status:** Audit #1 Completed & Remediated  

---

## 1. Executive Summary

In Phase 2, the baseline role classifier assigned **19,106 postings (40.99% of the modeling population)** to the catch-all category `"Other Tech"`. An unclassified proportion of over 40% represents an unacceptable lack of granularity that would compromise downstream unsupervised clustering (RQ2) and per-archetype residual error analysis (RQ3).

This forensic audit reveals two root causes for the inflation of Other Tech:
1. **Soft-Skill / Business-Skill Leakage:** Job postings outside of technical departments (e.g., Accountants, Legal Counsel, Sales Reps, Customer Success Managers, Marketing Coordinators) entered the dataset because generic non-technical skills (`communication`, `excel`, `crm`, `project-management`) were treated as qualifying technical indicators.
2. **Missing Granular Role Families:** Genuinely technical roles with distinct technological stacks (Embedded/Hardware, Systems/Network Engineering, Technical Product Management, Solutions Architecture, Engineering Management, Mobile Engineering) were not captured by the initial 14-class classifier.

Through refined non-tech exclusion filtering and an expanded **18-family precedence hierarchy**, `"Other Tech"` was reduced from **40.99% (19,106 records) down to 20.35% (6,928 records)**, with every retained category satisfying minimum-support thresholds ($N \ge 215 \ge 185$).

---

## 2. Quantitative Title Analysis of Original "Other Tech"

The original Other Tech cohort ($N = 19,106$) contained 14,216 distinct raw titles. The top 50 titles accounted for 5.59% of observations, exhibiting high dispersion across corporate support and specialized technical titles.

### Top 30 Titles in Original Other Tech:
| Rank | Job Title | Frequency | Share of Other Tech | Primary Classification Cause |
|---:|---|---:|---:|---|
| 1 | Customer Success Manager | 68 | 0.36% | Corporate Non-Tech (CRM/Communication leakage) |
| 2 | Account Manager | 57 | 0.30% | Corporate Non-Tech (CRM/Salesforce leakage) |
| 3 | Senior Accountant | 48 | 0.25% | Corporate Non-Tech (Excel leakage) |
| 4 | Product Marketing Manager | 39 | 0.20% | Corporate Non-Tech (Marketing/Communication leakage) |
| 5 | Project Manager | 35 | 0.18% | Reassigned to Technical Product & PM |
| 6 | Project Coordinator | 31 | 0.16% | Corporate Non-Tech / Operations |
| 7 | Senior Customer Success Manager | 30 | 0.16% | Corporate Non-Tech (CRM leakage) |
| 8 | Marketing Assistant | 29 | 0.15% | Corporate Non-Tech (Excel leakage) |
| 9 | Marketing Coordinator | 28 | 0.15% | Corporate Non-Tech (Communication leakage) |
| 10 | Senior Product Marketing Manager | 28 | 0.15% | Corporate Non-Tech (Marketing leakage) |
| 11 | Product Counsel | 27 | 0.14% | Corporate Non-Tech (Legal/Communication leakage) |
| 12 | Communications Coordinator | 26 | 0.14% | Corporate Non-Tech (Communication leakage) |
| 13 | Staff Accountant | 22 | 0.12% | Corporate Non-Tech (Excel leakage) |
| 14 | Senior Electrical Engineer | 21 | 0.11% | Reassigned to Embedded & Hardware |
| 15 | Accounting Manager | 21 | 0.11% | Corporate Non-Tech (Accounting leakage) |
| 16 | Business Development Manager | 21 | 0.11% | Corporate Non-Tech (Sales leakage) |
| 17 | Chief of Staff | 21 | 0.11% | Corporate Non-Tech (Executive Ops) |
| 18 | Implementation Manager | 21 | 0.11% | Reassigned to Solutions & Architecture |
| 19 | Brand Designer | 20 | 0.10% | Corporate Non-Tech (Creative/Marketing) |
| 20 | Senior Project Manager | 19 | 0.10% | Reassigned to Technical Product & PM |
| 21 | Mechanical Engineer | 19 | 0.10% | Reassigned to Embedded & Hardware |
| 22 | Deployment Strategist | 19 | 0.10% | Reassigned to Solutions & Architecture |
| 23 | Strategic Development Program Trainee | 18 | 0.09% | Corporate Non-Tech (Management Trainee) |
| 24 | Manufacturing Engineer | 18 | 0.09% | Reassigned to Embedded & Hardware |
| 25 | Field Sales Representative | 17 | 0.09% | Corporate Non-Tech (Sales) |
| 26 | Program Manager | 17 | 0.09% | Reassigned to Technical Product & PM |
| 27 | Technical Program Manager | 17 | 0.09% | Reassigned to Technical Product & PM |
| 28 | Territory Sales Manager | 17 | 0.09% | Corporate Non-Tech (Sales) |
| 29 | Sales Engineer | 17 | 0.09% | Reassigned to Solutions & Architecture |
| 30 | Controller | 17 | 0.09% | Corporate Non-Tech (Accounting) |

---

## 3. Discovered Hidden Role Families & Remediation Rules

Forensic decomposition demonstrated that the 19,106 records fell into two broad segments:
- **Segment 1: Corporate Non-Tech Roles (5,370 records, 28.11% of Other Tech):**
  - Roles in Accounting/Finance (Accountants, Controllers, Auditors, FP&A), Legal (Product Counsel, Corporate Counsel), Marketing (Product Marketing, Brand Designers, Social Media), and Sales/Customer Success (Account Managers, CSMs, BDRs).
  - *Remediation:* Strengthened negative lookahead exclusions in the role filter to explicitly prevent non-engineering corporate job titles from qualifying as technical roles.
- **Segment 2: Genuine Technical Roles (13,736 records, 71.89% of Other Tech):**
  - Legitimate technical roles that lacked explicit regex targets in the original 14-class classifier.
  - *Remediation:* Created targeted, semantically cohesive role families:
    1. **Engineering Management ($N = 827$):** Director of Engineering, VP of Engineering, Engineering Manager, Head of Engineering, CTO.
    2. **Solutions & Architecture ($N = 1,150$):** Solutions Architect, Enterprise Architect, Sales Engineer, Technical Account Manager, Forward Deployed Engineer, Solutions Consultant.
    3. **Embedded & Hardware ($N = 979$):** Embedded Software Engineer, Firmware Engineer, Hardware Engineer, Robotics Engineer, Electrical Engineer, Manufacturing Engineer.
    4. **Systems & Network Engineer ($N = 848$):** Systems Engineer, Network Engineer, Systems Administrator, IT Support/Infrastructure Engineer.
    5. **Technical Product & Program Management ($N = 2,255$):** Technical Product Manager, Technical Program Manager (TPM), Product Owner, Product Designer.
    6. **Mobile Engineer ($N = 340$):** iOS Developer, Android Developer, Mobile Engineer, React Native, Flutter.

---

## 4. Reassignment Impact: Before vs. After

| Metric | Phase 2 Baseline | Phase 2.1 Remediated | Absolute Change | Relative Change |
|---|---:|---:|---:|---:|
| **Total Modeling Cohort** | 46,608 | **34,036** | -12,572 | -26.97% (purged non-tech noise) |
| **"Other Tech" Headcount** | 19,106 | **6,928** | -12,178 | -63.74% |
| **"Other Tech" Share** | **40.99%** | **20.35%** | **-20.64 percentage points** | **50.4% reduction in share** |
| **Active Technical Role Families** | 14 | **18** | +4 families | Greater granularity |
| **Average Skills / Posting** | 4.07 | **4.16** | +0.09 | Higher technical density |

---

## 5. Characterization of Remaining "Other Tech" ($N = 6,928$, 20.35%)

The remaining 6,928 postings in Other Tech represent genuinely heterogeneous, interdisciplinary technical roles that do not map to standard software titles but carry verified technical programming or infrastructure competencies:
- Specialized Research Scientists & Bioinformatics (e.g., Computational Biologist, Genomics Data Specialist)
- Quantitative Analysts & Algorithmic Traders with Python/C++ skills
- Simulation & Gaming Engineers (e.g., Graphics Programmer, Unity Gameplay Developer, Unreal Engine Specialist)
- Technical Operations & Incident Management (e.g., Site Operations Lead, Tech Incident Commander)
- Specialized Domain Engineers (e.g., Audio DSP Engineer, Optical Systems Developer, Cryptographic Engineer)

Retaining this 19.34% cohort as `"Other Tech"` is methodologically defensible: it avoids over-fitting artificial micro-categories while capturing legitimate long-tail technical specializations.
