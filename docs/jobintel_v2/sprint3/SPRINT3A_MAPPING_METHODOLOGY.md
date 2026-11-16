# JOBINTEL 2.0 — SPRINT 3A
## Occupation Mapping Methodology & Calibrated Confidence Framework

**Date:** November 16, 2026  
**Sprint:** 3A  
**Status:** Approved Methodology Standard (`JOBINTEL-S3A-METH-001`)  
**Author:** Occupational Taxonomy Researcher, Labor Market Data Engineer  

---

## 1. Principles of Cross-Border Occupation Mapping

Cross-border occupation concordance cannot be established through superficial job title matching. Superficial similarities routinely obscure fundamental divergences in job duties, seniority, and required qualifications.

### High-Risk Mapping Anti-Patterns & False Friends
1. **Data Analyst vs. Business Analyst:**
   - *Data Analyst (e.g. UK SOC `3544`, US SOC `15-2051.01`):* Focuses on querying relational and non-relational data stores, statistical programming (Python, R, SQL), dashboard construction, and descriptive data modeling.
   - *Business Analyst (e.g. UK SOC `2431`, US SOC `13-1111`):* Focuses on business process modeling, organizational workflows, financial feasibility, and stakeholder requirement translation. Often belongs to Business/Financial Operations, not Computer/Mathematical occupations.
   - *Verdict:* Must be classified as `RELATED_BUT_DISTINCT` or `PARTIAL_OVERLAP`. Never `EXACT_MATCH`.
2. **Software Developer vs. Software Engineer:**
   - *UK & US Context:* In US SOC `15-1252` and UK SOC `2134`, software engineering and software development are functionally aggregated into a single unit group.
   - *Australia OSCA 2024 Context:* Explicitly distinguishes Software Engineer (`261313`) from Developer Programmer (`261312`) and Analyst Programmer (`261311`).
   - *Verdict:* A mapping between US SOC `15-1252` and AU OSCA `261313` is `BROADER_THAN` from US to AU, and `NARROWER_THAN` from AU to US.
3. **Data Scientist vs. Machine Learning Engineer:**
   - *Data Scientist:* Focuses on hypothesis testing, exploratory data analysis, statistical inference, feature discovery, and algorithmic prototyping.
   - *Machine Learning / MLOps Engineer:* Focuses on productionizing model pipelines, low-latency inference endpoints, distributed training infrastructure, model monitoring, and containerized deployment.
   - *Verdict:* Where a national system has distinct codes (e.g. Singapore SSOC `25131` AI/ML Engineer vs `25132` Data Scientist), mapping them to a monolithic data science code must be marked as `PARTIAL_OVERLAP` or `CLOSE_MATCH`, never `EXACT_MATCH`.

---

## 2. Multi-Dimensional Evidence Rubric

Every concordance mapping is derived through a systematic evaluation across six evidence dimensions:

```
                  ┌─────────────────────────────────────┐
                  │      EVIDENCE EVALUATION MATRIX     │
                  └──────────────────┬──────────────────┘
                                     │
      ┌──────────────────────────────┼──────────────────────────────┐
      │                              │                              │
┌─────▼───────────────┐   ┌──────────▼──────────┐   ┌───────────────▼─────┐
│ 1. OFFICIAL TABLES  │   │ 2. TASK CONCORDANCE │   │ 3. SKILL OVERLAP    │
│ Government Crosswalk│   │ Core Duties Match   │   │ Required Tech Stack │
└─────┬───────────────┘   └──────────┬──────────┘   └───────────────┬─────┘
      │                              │                              │
      ├──────────────────────────────┼──────────────────────────────┤
      │                              │                              │
┌─────▼───────────────┐   ┌──────────▼──────────┐   ┌───────────────▼─────┐
│ 4. CREDENTIAL/ENTRY │   │ 5. HIERARCHY SCOPE  │   │ 6. INDUSTRY CONTEXT │
│ Degree, Certs, Reg  │   │ Unit Group Level    │   │ Tech vs Non-Tech    │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

1. **Official Correspondence Support (Weight: 35%):**
   - Does an official government agency (ONS, BLS, ABS, SingStat, ILO) publish a verified crosswalk between the source and target classifications or via an authoritative common bridge?
2. **Task and Duty Concordance (Weight: 25%):**
   - Comparison of verified official task descriptions published in national classification volumes. High score requires $\ge 70\%$ of core duties to align.
3. **Skill and Competency Overlap (Weight: 15%):**
   - Alignment of core analytical tools, programming languages, operational systems, and methodologies.
4. **Credentialing & Educational Entry Routes (Weight: 10%):**
   - Comparison of typical qualification levels (e.g. UK RQF Level 6/7 vs US Bachelor's/Master's vs Australian AQF Level 7/8).
5. **Hierarchical Scope & Granularity (Weight: 10%):**
   - Alignment of hierarchy depth (e.g. 4-digit unit group vs 6-digit detailed code).
6. **Industry & Organizational Context (Weight: 5%):**
   - Verification that the role operates within equivalent organizational boundaries (e.g. in-house technology team vs third-party consultancy).

---

## 3. Calibrated Confidence Scoring & Review States

### 3.1 Review States
Every mapping is assigned one of eight formal review states:

| Review State | Description | Permitted Score Range | Default Score |
| :--- | :--- | :--- | :--- |
| **`VERIFIED_OFFICIAL`** | Established directly by an authoritative government crosswalk or gazetted correspondence table. | $0.95 \le C \le 1.00$ | $0.98$ (or $1.00$ if official 1:1) |
| **`VERIFIED_REVIEWED`** | Thoroughly vetted by qualified labor economists/researchers against the multi-dimensional rubric with full task comparison. | $0.85 \le C \le 0.95$ | $0.90$ |
| **`DERIVED_HIGH_CONFIDENCE`** | Strong empirical alignment across tasks, skills, and hierarchical level; pending formal committee signoff. | $0.75 \le C < 0.85$ | $0.80$ |
| **`DERIVED_MEDIUM_CONFIDENCE`**| Moderate alignment; notable differences in secondary tasks, reporting hierarchy, or credential requirements. | $0.60 \le C < 0.75$ | $0.70$ |
| **`LOW_CONFIDENCE`** | Weak or speculative concordance; high risk of misrepresentation. | $0.40 \le C < 0.60$ | $0.50$ |
| **`REVIEW_REQUIRED`** | Candidate mapping awaiting evidence verification; hidden from production comparisons. | $0.00 \le C < 0.40$ | $0.20$ |
| **`UNMAPPED`** | Confirmed that no acceptable counterpart exists in the target jurisdiction. | $0.00$ | $0.00$ |
| **`REJECTED`** | Previously proposed mapping formally invalidated due to proven task divergence. | $0.00$ | $0.00$ |

### 3.2 Approximation Disclosure Mandate
Any API response or user interface element displaying an international comparison where confidence $C < 0.95$ must present an explicit approximation warning:
> *"This cross-market comparison relies on an occupational concordance between {source_title} ({source_code}) and {target_title} ({target_code}) with an evaluated confidence of {confidence_score}%. Roles differ in specific duties, regulatory credentialing, or reporting hierarchies."*

---

## 4. Mapping Provenance Mandate

No anonymous, unversioned, or unverified mappings are permitted in JOBINTEL 2.0. Every mapping record must preserve:
1. `mapping_id`: Deterministic hash or stable slug (e.g. `map_uk2134_us151252_v1`).
2. `source_classification_id` & `target_classification_id`: Explicit system identifiers (`UK_SOC_2020`, `US_SOC_2018`).
3. `source_occupation_code` & `target_occupation_code`.
4. `relationship_type`: Formal enum (`EXACT_MATCH`, `CLOSE_MATCH`, `BROADER_THAN`, `NARROWER_THAN`, `PARTIAL_OVERLAP`, `RELATED_BUT_DISTINCT`, `NO_SUPPORTED_MAPPING`).
5. `methodology`: `OFFICIAL_CROSSWALK`, `EXPERT_ASSESSMENT`, or `CALIBRATED_TASK_OVERLAP`.
6. `confidence_score` & `review_status`.
7. `evidence_sources`: Full URL citations or official publication references.
8. `notes_and_limitations`: Explaining exact boundary conditions, task differences, and exclusions.
9. `created_at` & `updated_at`.
