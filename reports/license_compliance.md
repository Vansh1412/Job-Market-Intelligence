# License Compliance and Data Governance Audit
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Licensor:** DataForge (`data@dataforge.example`)  
**Audited License Agreement:** `data/raw/dataset_A/LICENSE.md`  
**License Tier:** Tier 1 — Internal Analytics (Derived-Metrics Edition, One-Time Snapshot)  
**Date:** October 5, 2026  

---

## 1. Executive Summary & Legal Status

An exhaustive legal and compliance inspection of `data/raw/dataset_A/LICENSE.md` was conducted prior to data processing. 

### Core Determinations:
- **Academic / Student Research Use:** **PERMITTED.** Section 3.1 expressly authorizes the licensee to use the Dataset for *"internal business analysis, research, benchmarking, and reporting within Licensee's organization."*
- **Creation of Derived Materials (Models, Features, Summaries):** **PERMITTED.** Section 1.2 and Section 3.1 allow the generation of *"analyses, models, reports, visualizations, aggregated statistics, or machine-learning model weights created by Licensee using the Dataset, provided that the Dataset records themselves cannot be extracted, reconstructed, or reverse-engineered from such materials in substantially their original form."*
- **Inclusion in Academic Submission (INT234 Coursework):** **PERMITTED.** Section 3.1 explicitly states: *"Licensee may share Derived Materials (but not Raw Data) with third parties, including in publications, provided no Dataset records are disclosed at record level."*
- **Public Redistribution of Raw Data:** **STRICTLY PROHIBITED.** Section 4(b) prohibits the licensee to *"sell, rent, lease, publish, or otherwise make the Raw Data (in whole or in substantial part) available to any third party as a standalone dataset, API, or bulk download."*
- **Public GitHub Commits:** **PROHIBITED FOR RAW AND RECORD-LEVEL DATA.** The raw files (`jobs.parquet`, `jobs.csv`, etc.) and any exported record-level files must never be committed or pushed to public version-control repositories.
- **Citation and Academic Attribution:** **PERMITTED & REQUIRED.** Section 4(e) prohibits removing provenance notices. The dataset can and must be formally cited as: *DataForge (2026). Tech Job Postings with Parsed Salaries (ATS Direct) [Data file and documentation]. Version 1.0 (L slice).*

---

## 2. Granular Compliance Matrix

| Question / Action | Permitted? | License Clause Reference | Operational Restriction |
|---|---|---|---|
| **Can we use this data for INT234 Academic Task 2?** | **YES** | Section 3.1 (Tier 1 Grant) | Internal academic research use is fully licensed. |
| **Can we train ML models (Ridge, RF, GB, MLP)?** | **YES** | Section 1.2 & Section 3.1 | Modeling weights, loss curves, and feature coefficients are authorized Derived Materials. |
| **Can we publish figures, heatmaps, PCA projections, and tables in the academic report?** | **YES** | Section 3.1 | Aggregated visualizations and summary statistics do not expose individual record-level PII or raw rows. |
| **Can we upload `data/raw/` or `data/processed/*.parquet` to GitHub?** | **NO** | Section 1.3, 3.1, 4(b) | Constitutes prohibited publication of Raw Data. All data files must remain local. |
| **Can we share code (`src/`, `notebooks/`, `app.py`) on GitHub?** | **YES** | Section 1.2 | Code and pipeline logic are original intellectual property, independent of the proprietary raw data. |
| **Can we distribute trained model files (`models/*.joblib`)?** | **YES** | Section 1.2 | Trained weights and pipelines do not reconstruct or emit record-level postings. |
| **Can we cite DataForge and quote schema definitions from the Data Dictionary?** | **YES** | Section 4(e), Schedule B | Proper attribution is required; descriptive metadata is non-proprietary fact. |

---

## 3. Technical Safeguards & Implementation

To enforce 100% compliance with DataForge Tier 1 terms, the following controls have been implemented:

1. **Local Storage Isolation:**
   - Raw data files remain strictly quarantined in `data/raw/dataset_A/`.
   - Processed analytical artifacts remain strictly on the local machine in `data/processed/`.

2. **Git Version Control Safeguards (`.gitignore`):**
   - The project root `.gitignore` has been updated with explicit ignore rules:
     ```gitignore
     # DataForge Tier 1 License Compliance: Never commit raw data or full-record exports
     data/raw/
     data/processed/
     *.parquet
     *.csv
     jobs-tier1-L-2026-08-01/
     nextgig_jobs_2026-06.parquet
     ```

3. **Public Submission Manifest:**
   - **What CAN be committed to GitHub or submitted digitally:**
     - Python source code (`src/*.py`)
     - Jupyter notebooks (`notebooks/*.ipynb` with aggregated outputs)
     - Analytical markdown reports (`reports/*.md`)
     - Figures and charts (`reports/figures/*.png`)
     - Aggregated tables (`reports/tables/*.csv` or `.md`)
     - Trained pipeline artifacts (`models/*.joblib`)
     - Project documentation (`README.md`, `requirements.txt`)
   - **What must NEVER be committed or uploaded publicly:**
     - `data/raw/dataset_A/data/jobs.parquet`
     - `data/raw/dataset_A/data/jobs.csv`
     - `data/processed/cleaned_jobs.parquet`
     - `data/processed/modeling_dataset.parquet`
     - `data/processed/skill_matrix.parquet`
     - Candidate dataset `nextgig_jobs_2026-06.parquet`

---

## 4. Conclusion & Sign-Off

The project operates in full compliance with the DataForge Dataset License Agreement (Tier 1). No unauthorized data redistribution will occur, and all deliverables presented to academic evaluators represent lawful Derived Materials.
