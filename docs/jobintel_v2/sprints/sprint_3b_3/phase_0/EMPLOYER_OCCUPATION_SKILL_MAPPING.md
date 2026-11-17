# JOBINTEL 2.0 — SPRINT 3B.3 (PHASE 0)
## EMPLOYER OCCUPATION & SKILL MAPPING ARCHITECTURE
### Cross-Market Concordance, Taxonomic Crosswalking, Skill Normalization & Confidence Calibration

**Document ID:** `JOBINTEL-V2-SPRINT3B3-PH0-OCCUPATION-SKILL-MAPPING`  
**Execution Phase:** Phase 0 (Taxonomy Concordance & Skill Architecture Audit)  
**Date of Audit:** 2026-11-17  
**Guiding Principle:** Preserve raw employer titles, link through official crosswalks, and never assume title equivalence across national jurisdictions.

---

## 1. THE TAXONOMIC HETEROGENEITY PROBLEM

Employers publish arbitrary, idiosyncratic, and non-standardized job titles (e.g., *"Member of Technical Staff 3"*, *"Cloud Ninja"*, *"Software Craftsman"*, *"AVP - Engineering"*).

Attempting to analyze employer demand directly from raw title strings creates fatal fragmentation:
1. **Title Inflation & Divergence:** In the US, an "Associate" in tech is typically an entry-level professional, while in Indian banking/consulting an "Associate" may be an experienced mid-level specialist, and in the UK an "Associate Director" is senior leadership.
2. **National Classification Variance:** When employers post in different countries, each national government categorizes the work under a distinct statistical classification system:
   - **United States:** SOC 2018 (Standard Occupational Classification, 867 detailed occupations).
   - **United Kingdom:** SOC 2020 (Office for National Statistics, 412 unit groups).
   - **Australia:** ANZSCO 2022 (Australian and New Zealand Standard Classification of Occupations, 1,076 occupations).
   - **Singapore:** SSOC 2020 (Singapore Standard Occupational Classification, 1,003 5-digit occupations).
   - **India:** NCO-2015 (National Classification of Occupations, based on ISCO-08).

JOBINTEL 2.0 resolves this through an **intermediate canonical abstraction layer** while preserving raw verbatim titles.

---

## 2. THE THREE-TIER OCCUPATION MAPPING PIPELINE

```
[Raw Employer Job Title: e.g. "Lead React & Node Full-Stack Engineer"]
                                  |
                                  v
+-------------------------------------------------------------------+
| TIER 1: VERBATIM CAPTURE (Immutable)                              |
| Raw Title: "Lead React & Node Full-Stack Engineer"                |
| Employer ID, Country, Raw Job Description                         |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| TIER 2: NATIONAL TAXONOMY CROSSWALK (Market-Specific)             |
| Match against native classification using country rules:          |
|   US -> SOC 2018: 15-1252 (Software Developers)                   |
|   UK -> SOC 2020: 2134 (Programmers & Software Dev Professionals) |
|   AU -> ANZSCO 2022: 261313 (Software Engineer)                   |
|   SG -> SSOC 2020: 25121 (Software & Applications Developer)      |
|   IN -> NCO-2015: 2512.0100 (Software Engineer)                   |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| TIER 3: CANONICAL OCCUPATION HARMONIZATION                        |
| Map to JobIntel Canonical Concept:                                |
|   -> CAN_OCC_SOFTWARE_ENGINEER                                    |
| Seniority Normalization:                                          |
|   -> LEAD_PRINCIPAL (Score: 0.94)                                 |
+-------------------------------------------------------------------+
```

---

## 3. MAPPING PROVENANCE CLASSIFICATIONS

Every mapping assigned to an employer observation must carry an explicit **mapping provenance tag**:

| Mapping Classification | Definition | Methodological Basis | Confidence Range |
| :--- | :--- | :--- | :---: |
| **`EXACT_MAPPING`** | Unambiguous exact lexical or code-level match between employer title and standard unit group. | Direct verbatim dictionary equality with standardized title catalog. | $0.98 - 1.00$ |
| **`OFFICIALLY_CROSSWALKED`** | Derived using authorized bilateral concordance tables published by statistical agencies. | Official crosswalks (e.g. BLS SOC $\to$ O\*NET 28.0; ABS ANZSCO $\to$ ISCO-08; ONS SOC 2020 crosswalks). | $0.92 - 0.97$ |
| **`DERIVED_MAPPING`** | Programmatic NLP extraction matching tokenized job title, department, and duty descriptions. | Rule-based token parser, domain ontology embeddings, and seniority stripping. | $0.80 - 0.91$ |
| **`CURATED_MAPPING`** | Verified and certified by human labour market researcher for edge cases. | Manual domain expert audit. | $1.00$ (Gold) |
| **`UNMAPPED_CLASSIFICATION`**| Employer title cannot be assigned with confidence $\ge 0.80$. | Preserved as raw title without assigning a misleading canonical tag. | $< 0.80$ |

---

## 4. CANONICAL SKILL EXTRACTION & TAXONOMY ALIGNMENT

Employer job descriptions contain unstructured text outlining required competencies. JOBINTEL 2.0 maps these against the frozen, verified **JobIntel Skills Taxonomy** (`src/backend/artifacts/skills_taxonomy.json`).

### Extraction & Normalization Rules:
1. **Lemmatization & Variant Aliasing:**
   - Text variant `"ReactJS"`, `"React.js"`, `"React"` $\to$ Canonical Token: `skill_react`.
   - Text variant `"K8s"`, `"Kubernetes Container Orchestration"` $\to$ Canonical Token: `skill_kubernetes`.
   - Text variant `"Postgres"`, `"PostgreSQL"` $\to$ Canonical Token: `skill_postgresql`.
2. **Contextual Disambiguation:**
   - Short acronyms (e.g. `"Go"`, `"C"`, `"R"`) must be evaluated with boundary constraints (`\bGo\b`) and co-occurring technical tokens (e.g. `golang`, `concurrency`, `backend`) to avoid false-positive extraction from common English words.
3. **Requirement Hierarchy Classification:**
   - **`MANDATORY_REQUIRED`:** Stated in sections titled *"Requirements"*, *"Must Have"*, *"Qualifications"*, or preceded by *"Proficiency in..."*.
   - **`PREFERRED_BONUS`:** Stated in sections titled *"Nice to Have"*, *"Bonus Skills"*, *"Preferred Qualifications"*.
   - **`CONTEXTUAL_MENTION`:** Skills mentioned in company background or team overview without direct candidate obligation.

---

## 5. CONFIDENCE CALIBRATION & QUALITY GATES

To ensure algorithmic accountability, every automated mapping generates a calibrated confidence score:

$$C_{\text{composite}} = w_{\text{title}} \cdot S_{\text{title}} + w_{\text{dept}} \cdot S_{\text{dept}} + w_{\text{skills}} \cdot S_{\text{skills}}$$

Where:
- $w_{\text{title}} = 0.55$, $w_{\text{dept}} = 0.15$, $w_{\text{skills}} = 0.30$.
- $S_{\text{title}}$: Token cosine similarity between title and standard task descriptors.
- $S_{\text{skills}}$: Jaccard overlap between extracted posting skills and canonical archetype core skills.

### Production Routing Gates:
- $C_{\text{composite}} \ge 0.85$: **Auto-approved** (`DERIVED_MAPPING`).
- $0.70 \le C_{\text{composite}} < 0.85$: **Flagged for Human Review** (`EmployerVerificationStatus.REVIEW_REQUIRED`).
- $C_{\text{composite}} < 0.70$: **Marked as `UNMAPPED_CLASSIFICATION`** (Raw title preserved; zero canonical misattribution).

**Audit Status:** `PASS — OCCUPATION & SKILL MAPPING ARCHITECTURE FULLY SPECIFIED`
