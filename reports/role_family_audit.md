# Role Family Classification Hierarchy & Precedence Audit
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Date:** October 5, 2026  
**Status:** Audit #2 Completed & Verified  

---

## 1. Executive Summary

In job posting text, titles frequently contain multi-word combinations with semantic overlap across engineering disciplines, leadership tiers, and technical specializations. For example:
- *"Senior Machine Learning Engineer"* contains both `"machine learning"` and `"engineer"`.
- *"Senior Engineering Manager"* contains `"senior"`, `"engineering"`, and `"manager"`.
- *"Cloud Security Architect"* contains `"cloud"`, `"security"`, and `"architect"`.
- *"Data Platform Engineer"* contains `"data"`, `"platform"`, and `"engineer"`.

Without an explicit, deterministic precedence hierarchy, rule-based classifiers produce unpredictable assignments that depend arbitrarily on evaluation order. This audit establishes a defensible, empirical 18-tier precedence hierarchy that resolves all semantic conflicts and ensures consistent, interpretable role categorization.

---

## 2. Tested Conflict-Resolution Table

| Ambiguous / Overlapping Title | Competing Families | Precedence Decision | Justification |
|---|---|---|---|
| **Senior Machine Learning Engineer** | ML/AI Engineer vs. Software Engineer | **ML / AI Engineer** | Specialized domain expertise (ML/AI) takes precedence over generic software engineering. |
| **Senior Engineering Manager** | Engineering Management vs. Software Engineer | **Engineering Management** | People management and organizational leadership dictate compensation bands more strongly than individual contributor engineering. |
| **Cloud Security Engineer** | Security Engineer vs. DevOps / Cloud | **Security Engineer** | Security governance and compliance represents a specialized risk domain distinct from general cloud infrastructure provisioning. |
| **Data Platform Engineer** | Data Engineer vs. DevOps / Cloud | **Data Engineer** | The primary data pipeline and storage infrastructure mandate places this in Data Engineering. |
| **Full Stack Python Developer** | Full-Stack vs. Backend vs. Software Engineer | **Full-Stack Developer** | Architectural scope across the full application stack takes precedence over language-specific backend syntax. |
| **Solutions Architect** | Solutions & Architecture vs. Software Engineer | **Solutions & Architecture** | Customer-facing and high-level enterprise design duties differ fundamentally from day-to-day code production. |
| **Technical Product Manager** | Technical Product & PM vs. Software Engineer | **Technical Product & PM** | Product roadmap ownership and backlog management take precedence over technical implementation keywords. |
| **Lead QA Automation Engineer** | QA / SDET vs. Engineering Management | **QA / SDET** | Specialized software testing and verification focus takes precedence over the generic `"lead"` title prefix. |
| **iOS Mobile Developer** | Mobile Engineer vs. Frontend Developer | **Mobile Engineer** | Native mobile OS runtime specialization (iOS/Swift) is distinct from browser-based web frontend development. |
| **Firmware Engineer** | Embedded & Hardware vs. Software Engineer | **Embedded & Hardware** | Low-level hardware-interfacing code (bare-metal, C/C++, RTOS) represents a dedicated physical engineering domain. |

---

## 3. The 18-Tier Precedence Hierarchy

The final classification algorithm processes candidate titles through the following strict sequential pipeline:

```text
TIER 1:  Engineering Management (CTO, VP Eng, Director of Eng, Engineering Manager)
   ↓
TIER 2:  ML / AI Engineer (Machine Learning, Deep Learning, Computer Vision, NLP, LLM, MLOps)
   ↓
TIER 3:  Data Scientist (Data Science, Applied Scientist, Research Scientist, Statistician)
   ↓
TIER 4:  Data Engineer (Data Engineering, Big Data, Data Warehouse, ETL, Database Engineer)
   ↓
TIER 5:  Data / BI Analyst (Data Analyst, Business Intelligence, Analytics Engineer)
   ↓
TIER 6:  Security Engineer (Cybersecurity, Infosec, AppSec, Cloud Security, SecOps)
   ↓
TIER 7:  DevOps / Cloud / Platform (DevOps, Site Reliability / SRE, Cloud Engineer, Platform Engineer)
   ↓
TIER 8:  QA / SDET (Quality Assurance, Test Automation, Software Test Engineer)
   ↓
TIER 9:  Solutions & Architecture (Solutions Architect, Enterprise Architect, Sales Engineer, TAM, FDE)
   ↓
TIER 10: Technical Product & PM (Technical Product Manager, TPM, Product Owner, Product Designer)
   ↓
TIER 11: Mobile Engineer (iOS Developer, Android Developer, Mobile Engineer, Flutter, React Native)
   ↓
TIER 12: Embedded & Hardware (Embedded Systems, Firmware, Robotics, Hardware, Electrical, Manufacturing)
   ↓
TIER 13: Systems & Network Engineer (Systems Engineer, Network Engineer, Sysadmin, IT Support Engineer)
   ↓
TIER 14: Frontend Developer (Frontend Developer, UI Developer, Web Developer, React/Angular/Vue Developer)
   ↓
TIER 15: Backend Developer (Backend Developer, API Engineer, Server Engineer, Java/Python/Go Developer)
   ↓
TIER 16: Full-Stack Developer (Full-Stack Engineer, Full Stack Developer)
   ↓
TIER 17: Core Software Engineer (Software Engineer, SWE, Software Developer, Applications Engineer)
   ↓
TIER 18: Skill-Fallback & Other Tech (Residual tech postings classified via primary skill or marked Other Tech)
```

---

## 4. Final Distribution Across the 18 Role Families ($N = 34,036$)

| Rank | Role Family | Final Count | Share (%) | Minimum Support Rule Status |
|---:|---|---:|---:|---|
| 1 | **Other Tech** | 6,928 | 20.35% | Maintained (Diverse technical specializations) |
| 2 | **Software Engineer** | 6,511 | 19.13% | Passed ($N \ge 185$) |
| 3 | **ML / AI Engineer** | 5,963 | 17.52% | Passed ($N \ge 185$) |
| 4 | **Technical Product & PM** | 2,494 | 7.33% | Passed ($N \ge 185$) |
| 5 | **Data Scientist** | 1,954 | 5.74% | Passed ($N \ge 185$) |
| 6 | **DevOps / Cloud / Platform** | 1,677 | 4.93% | Passed ($N \ge 185$) |
| 7 | **Data Engineer** | 1,624 | 4.77% | Passed ($N \ge 185$) |
| 8 | **Solutions & Architecture** | 864 | 2.54% | Passed ($N \ge 185$) |
| 9 | **Engineering Management** | 827 | 2.43% | Passed ($N \ge 185$) |
| 10 | **Embedded & Hardware** | 820 | 2.41% | Passed ($N \ge 185$) |
| 11 | **Full-Stack Developer** | 737 | 2.17% | Passed ($N \ge 185$) |
| 12 | **Security Engineer** | 692 | 2.03% | Passed ($N \ge 185$) |
| 13 | **Backend Developer** | 684 | 2.01% | Passed ($N \ge 185$) |
| 14 | **Systems & Network Engineer** | 652 | 1.92% | Passed ($N \ge 185$) |
| 15 | **Frontend Developer** | 582 | 1.71% | Passed ($N \ge 185$) |
| 16 | **QA / SDET** | 503 | 1.48% | Passed ($N \ge 185$) |
| 17 | **Mobile Engineer** | 309 | 0.91% | Passed ($N \ge 185$) |
| 18 | **Data / BI Analyst** | 215 | 0.63% | Passed ($N \ge 185$) |
| — | **Total Cohort** | **34,036** | **100.00%** | **All 18 categories verified statistically viable** |

---

## 5. Audit Conclusions

The 18-tier hierarchy resolves semantic ambiguity through principled precedence rules. Crucially, every single family satisfies the minimum sample-size rule ($N \ge 185$), ensuring adequate statistical power for archetype-level error evaluation (RQ3) and multi-class classification modeling.
