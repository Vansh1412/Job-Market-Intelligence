# JOBINTEL 2.0 — SPRINT 3B.3.3.2.1
## DOCUMENT 01: INDEPENDENT SKILL POPULATION LINEAGE & DATASET AUDIT

**Sprint:** 3B.3.3.2.1 — Independent Security, Statistical Contract & Release Audit  
**Auditor Role:** Principal Statistical Auditor & Data Governance Reviewer  
**Audit Target:** Skill Population Lineage & Prevalence Reproducibility across USA & India  
**Execution Mode:** STRICTLY READ-ONLY  
**Date:** 2026-11-17  

---

### 1. Audit Target & Executive Overview

This audit independently investigates the empirical data pipelines, source datasets, normalization rules, and numerator/denominator constructions for the skill frequency metrics across the USA and India markets in JOBINTEL 2.0.

#### Core Claims Under Audit:
1. **USA Labor Corpus:** Population $N = 335,995$, Python count $n = 31,676$, prevalence $9.4\%$.
2. **India Labor Cohort:** Population $N = 5,323$, Python count $n = 723$ (or $644$), prevalence $13.6\%$ (or $12.1\%$).
3. **Discrepancy Investigation:** Origin of $5,316$ versus $5,323$ in Indian cohort documentation.

---

### 2. USA Labor Corpus Forensic Lineage

#### 2.1 Dataset Verification & Cryptographic Provenance
- **Primary Processed Dataset:** `data/processed/cleaned_jobs.parquet`
  - Exact Shape: $(335,995\text{ rows}, 24\text{ columns})$
  - SHA-256 Hash Prefix: `bc9ed42e4720470c...`
- **Supervised Modeling Subset:** `data/processed/modeling_dataset.parquet`
  - Exact Shape: $(34,036\text{ rows}, 102\text{ columns})$
  - SHA-256 Hash Prefix: `68895e3823cca91f...`
  - Retention Rate: $\frac{34,036}{335,995} = 10.13\%$ of general corpus (representing tech roles with valid, non-outlier base compensation).

#### 2.2 Numerator, Denominator & Prevalence Reconstruction
- **Dataset Columns Inspected:** In `cleaned_jobs.parquet` and `src/backend/routers/skills.py`:
  - Python postings count: $n = 31,676$.
  - Total observational corpus denominator: $N = 335,995$.
- **Mathematical Quotient:**
  $$\text{True Prevalence} = \frac{31,676}{335,995} = 0.09427521... \rightarrow 9.43\% \approx 9.4\%$$
- **Flawed Supervised Cohort Conflation (Previous Defect):**
  $$\frac{31,676}{34,036} = 0.93066 \rightarrow 93.1\% \neq 9.4\%$$
- **Verification Finding:** The displayed prevalence of $9.4\%$ is mathematically and empirically derived from the **full $N = 335,995$ postings corpus**, NOT the supervised salary subset ($N = 34,036$). The backend API exposes `population_size: 335995`, and the frontend correctly renders this value.

---

### 3. India Labor Cohort Forensic Lineage

#### 3.1 Dataset Verification & Cryptographic Provenance
- **Primary Processed Postings:** `data/processed/india/india_job_postings.parquet`
  - Exact Shape: $(97,679\text{ rows}, 34\text{ columns})$
  - SHA-256 Hash Prefix: `81046f95f4d1ab05...`
- **Extracted Job Skills Relational Table:** `data/processed/india/india_job_skills.parquet`
  - Exact Shape: $(751,947\text{ rows}, 2\text{ columns})$
  - SHA-256 Hash Prefix: `c3dede3f446b12a2...`
- **Supervised Modeling Cohort:** `data/processed/india/india_modeling_cohort.parquet`
  - Exact Shape: $(5,859\text{ rows}, 299\text{ columns})$
  - SHA-256 Hash Prefix: `d4e32be45d84b159...`
- **Archetype & Skill Provenance Metadata:** `models/india/india_archetype_metadata.json`
  - `n_total_cohort`: $5,859$
  - `n_skill_bearing`: **$5,323$**

#### 3.2 Resolution of the 5,316 vs. 5,323 Discrepancy
Forensic review of `docs/jobintel_v2/sprints/sprint_3b_3_3_1/01_skill_cohort_audit.md` revealed:
- An auditor in Sprint 3B.3.3.1 observed the top skill count $723$ and reported prevalence $13.6\%$.
- The auditor performed an **informal back-calculation**:
  $$\frac{723}{0.136} = 5,316.176 \approx 5,316$$
- They hypothesized that the denominator was $5,316$.
- **Ground Truth Verification:** Inspection of the actual pipeline artifact (`india_archetype_metadata.json`) establishes that the true number of skill-bearing job requisitions in the modeling cohort is **$N = 5,323$**.
- $5,316$ was an artifact of roundoff division, whereas $5,323$ is the genuine physical dataset row count.

#### 3.3 Skill Count Discrepancy (Python vs. Development)
Inspection of `data/processed/india/india_skill_analytics.json` (284 skills) revealed:
- The count of **$723$** belongs to **"Development"** (`skill_development`):
  $$\frac{723}{5,323} = 0.135825... \rightarrow 13.58\% \approx 13.6\%$$
- The count of **$663$** belongs to **"Java"** (`skill_java`):
  $$\frac{663}{5,323} = 0.12455... \rightarrow 12.46\% \approx 12.5\%$$
- The count of **$644$** belongs to **"Python"** (`skill_python`):
  $$\frac{644}{5,323} = 0.12098... \rightarrow 12.10\% \approx 12.1\%$$
- **Finding:** The prompt's reference to "Python count: 723" was an inherited mislabeling from earlier sprint notes where the #1 skill (Development, $723$) was conflated with Python ($644$). Both $723$ and $644$ share the identical denominator of **$5,323$**.

---

### 4. Cross-Market Skill Endpoints Audit

| Market | Target Metric | Stored Count ($n$) | Population ($N$) | Calculated Quotient | Displayed % | API Exposed $N$ | Frontend $N$ | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **USA** | Python | 31,676 | 335,995 | $9.43\%$ | $9.4\%$ | 335,995 | 335,995 | **VERIFIED** |
| **USA** | SQL | 28,154 | 335,995 | $8.38\%$ | $8.4\%$ | 335,995 | 335,995 | **VERIFIED** |
| **USA** | AWS | 16,140 | 335,995 | $4.80\%$ | $4.8\%$ | 335,995 | 335,995 | **VERIFIED** |
| **India** | Development | 723 | 5,323 | $13.58\%$ | $13.6\%$ | 5,323 | 5,323 | **VERIFIED** |
| **India** | Java | 663 | 5,323 | $12.46\%$ | $12.5\%$ | 5,323 | 5,323 | **VERIFIED** |
| **India** | Python | 644 | 5,323 | $12.10\%$ | $12.1\%$ | 5,323 | 5,323 | **VERIFIED** |
| **India** | SQL | 538 | 5,323 | $10.11\%$ | $10.1\%$ | 5,323 | 5,323 | **VERIFIED** |

---

### 5. Findings Summary & Action Items

- **Claim:** USA skill percentages match $N = 335,995$; India skill percentages match $N = 5,323$.
- **Evidence:** Parquet datasets, `india_skill_analytics.json`, `india_archetype_metadata.json`, and backend routers.
- **Risk:** Conflation of skill names in informal text (Development 723 vs Python 644).
- **Required Action:** Ensure all external marketing and documentation correctly cites Python at $12.1\%$ ($n = 644$) and Development at $13.6\%$ ($n = 723$) for India.
- **Status:** **VERIFIED**.
