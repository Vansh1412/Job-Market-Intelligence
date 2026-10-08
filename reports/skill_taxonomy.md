# Skill Vocabulary Taxonomy and Matrix Partitioning Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Date:** October 5, 2026  
**Status:** Audit #4 Completed & Formally Taxonomized  

---

## 1. Executive Summary

In Phase 2, an empirical audit revealed that while the skill matrix was described as representing "technical skills", the top two most frequent skills were `"communication"` ($N = 18,856$) and `"crm"` ($N = 3,394$). Treating soft collaborative skills and business CRM operations interchangeably with programming languages and cloud infrastructure introduces confounding variance into unsupervised clustering (RQ2) and distorts regression coefficients (RQ1).

This report establishes a formal **4-tier Skill Taxonomy** across all 101 original controlled vocabulary tags delivered by DataForge. Furthermore, the dataset pipeline is upgraded to partition the skills into three distinct, specialized Parquet matrices:
1. `skill_matrix_technical.parquet` (82 pure technical competencies)
2. `skill_matrix_professional.parquet` (2 soft & collaborative competencies)
3. `skill_matrix_business.parquet` (7 business & functional application tools)

---

## 2. The 4-Tier Skill Taxonomy

```text
ALL 101 CONTROLLED SKILLS IN DATASET A
│
├── A. TECHNICAL SKILLS (82 Skills) ────────────► Primary PCA / K-Means Matrix
│   ├── Programming Languages (14)
│   ├── Cloud & Infrastructure (12)
│   ├── AI, Machine Learning & Data Science (21)
│   ├── Databases & Distributed Storage (5)
│   ├── Web, Mobile & API Frameworks (17)
│   ├── BI & Analytical Querying (4)
│   └── Specialized Engineering & Systems (9)
│
├── B. PROFESSIONAL / SOFT SKILLS (2 Skills) ──► Retained in Supervised Regressors
│   ├── communication
│   └── project-management
│
├── C. BUSINESS / FUNCTIONAL (7 Skills) ───────► Retained in Supervised Regressors
│   ├── crm, salesforce, sap, excel
│   └── product-management, figma, ui-ux
│
└── D. NOISE / NON-INFORMATIVE (10 Skills) ────► Purged Prior to Processing
    └── accounting, customer-success, financial-analysis, hubspot, legal,
        marketing, recruiting, sales, sem, seo
```

---

## 3. Comprehensive Categorization Inventory

### Category A: Technical Skills (82 Skills)
*Decision Rule: Concrete computing languages, frameworks, developer tools, system architectures, and technical algorithms.*

1. **Programming Languages (14):** `c#`, `c++`, `go`, `java`, `javascript`, `kotlin`, `php`, `python`, `ruby`, `rust`, `scala`, `swift`, `typescript`, `html-css`.
2. **Cloud, DevOps & Infrastructure (12):** `ansible`, `aws`, `azure`, `ci-cd`, `devops`, `docker`, `gcp`, `kubernetes`, `linux`, `microservices`, `serverless`, `terraform`.
3. **AI, Machine Learning & Big Data (21):** `airflow`, `bigquery`, `computer-vision`, `data-engineering`, `data-science`, `databricks`, `dbt`, `deep-learning`, `etl`, `hadoop`, `kafka`, `llm`, `machine-learning`, `nlp`, `numpy`, `pandas`, `pytorch`, `redshift`, `scikit-learn`, `spark`, `statistics`, `tensorflow`.
4. **Databases & Storage (5):** `elasticsearch`, `mongodb`, `nosql`, `postgresql`, `redis`.
5. **Web, Mobile & Networking Frameworks (17):** `android`, `angular`, `django`, `fastapi`, `flask`, `flutter`, `graphql`, `grpc`, `ios`, `next.js`, `node.js`, `rabbitmq`, `react`, `react-native`, `rest-api`, `spring`, `vue`.
6. **BI & Analytics Querying (4):** `looker`, `power-bi`, `sql`, `tableau`.
7. **Specialized Engineering & Tools (9):** `blockchain`, `embedded`, `gis`, `git`, `hardware`, `qa-testing`, `robotics`, `security`, `unity`.

### Category B: Professional & Soft Skills (2 Skills)
*Decision Rule: Behavioral, interpersonal, and procedural competencies applicable across all corporate roles.*
- `communication` ($N = 18,856$): Essential human collaboration indicator.
- `project-management` ($N = 4,210$): Agile/Scrum and delivery execution indicator.

### Category C: Business & Functional Skills (7 Skills)
*Decision Rule: Commercial software suites, CRM platforms, enterprise ERP tools, and product design software.*
- `crm`, `salesforce`, `sap`, `excel`: Enterprise administrative and customer operational platforms.
- `product-management`, `figma`, `ui-ux`: Digital design and product development workflows.

### Category D: Noise & Domain-Irrelevant Skills (10 Skills - Purged)
*Decision Rule: Non-technical functional tasks that caused cross-domain corporate leakage into the engineering modeling cohort.*
- `accounting`, `customer-success`, `financial-analysis`, `hubspot`, `legal`, `marketing`, `recruiting`, `sales`, `sem`, `seo`.

---

## 4. Multi-Hot Matrix Partitioning & Export Specification

To support both unsupervised clustering (RQ2) and supervised predictive modeling (RQ1 & RQ3), four Parquet files are exported to `data/processed/`:

| Parquet File | Columns | Rows | Analytical Role |
|---|---:|---:|---|
| `skill_matrix_technical.parquet` | **82** | 335,995 | **Primary Clustering Matrix:** Standardized technical skills for PCA & K-Means archetype discovery. |
| `skill_matrix_professional.parquet` | **2** | 335,995 | **Behavioral Analysis:** Isolates the salary premium of communication and project management. |
| `skill_matrix_business.parquet` | **7** | 335,995 | **Functional Tool Analysis:** Tracks enterprise CRM/ERP/Design tool premiums. |
| `skill_matrix.parquet` | **91** | 335,995 | **Full Multi-Hot Matrix:** Comprehensive union of Categories A, B, and C ($82 + 2 + 7 = 91$). |

---

## 5. Audit Conclusions

This taxonomy solves the "communication/CRM dominance" anomaly. Professional and business skills are isolated from the core technical feature space used for unsupervised job archetype discovery, while remaining accessible as covariates in supervised salary regression.
