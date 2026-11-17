# JOBINTEL 2.0 — FRONTEND PREDICTION CLAIMS AUDIT
## Repository-Wide Claims Analysis, False Precision Audit & Presentation Guidelines

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Product Integrity Reviewer  
**Dataset Reference:** `docs/jobintel_v2/sprints/sprint_3b_3_2_2/prediction_claims.csv`  

---

## 1. REPOSITORY-WIDE SCAN FINDINGS

An automated AST and regex scan across all code, frontend, and documentation directories identified **493 matches** containing performance phrases, certainty keywords, or accuracy statements.

```
+----------------------------------------------------------------------------------------------------+
| CLAIMS AUDIT CATEGORIZATION BREAKDOWN (493 MATCHES)                                               |
+--------------------------+-----------------------+--------------------+----------------------------+
| Category Classification  | Match Count           | Share (%)          | Audit Action Required      |
+--------------------------+-----------------------+--------------------+----------------------------+
| Legitimate Engineering   | 421 matches           | 85.4%              | APPROVED (Data integrity,  |
| Statements               |                       |                    | residual axes, test asserts)|
| Technical Benchmark Docs | 48 matches            | 9.7%               | CAVEAT TAGS REQUIRED       |
| Frontend UI Strings      | 14 matches            | 2.8%               | REWRITE MANDATED           |
| Marketing / Overstatement| 10 matches            | 2.0%               | REMOVAL / CORRECTION       |
| Total Matches Audited    | 493 matches           | 100.0%             | Complete Coverage          |
+--------------------------+-----------------------+--------------------+----------------------------+
```

---

## 2. FALSE PRECISION AUDIT ACROSS PRODUCT MODULES

### 2.1 What Is False Precision?
False precision occurs when an estimated number is presented with more significant figures than the underlying measurement or statistical model warrants, creating an illusion of exactitude.

### 2.2 Product-Wide False Precision Audit

| Product Module | Current Uncorrected Presentation | Mandated Standard Presentation | Statistical Rationale |
| :--- | :--- | :--- | :--- |
| **Salary Intelligence (India)** | `₹12,47,839 / yr` or `₹12.478 LPA` | **`₹12.5 LPA`** (with `₹10.4–14.6 LPA` range) | Model holdout MAE is ₹3.71 LPA. Fractional lakhs imply non-existent accuracy. |
| **Salary Intelligence (USA)** | `$142,391.14 / year` | **`$142,000 / year`** (with `$115K–$168K` range)| Model test MAE is $36,380. Displaying cents or single dollars is misleading. |
| **Employer Match Scoring** | `Match: 98.74%` | **`High Match`** (or `Match Tier 1`) | Similarity scores are heuristic weights, not 4-digit probability metrics. |
| **Demand Vacancy Flow** | `Growth Momentum: +43.2%` | **`N = 64 Active Vacancies`** | Postings represent open requisitions, not percentage employment growth. |
| **Skill Requirement Analysis**| `Python: 89.4% demanded` | **`Python: Requested in 18 of 20 postings (90%)`** | Fractions on small samples ($N < 50$) distort perceived precision. |

---

## 3. SEPARATION OF STORED SOURCE VALUES VS. DISPLAY PRESENTATION

A critical platform governance rule established in this audit:

```
====================================================================================================
THE DUAL DATA FIDELITY RULE:
1. UNDERLYING DATA & BACKEND APIS MUST PRESERVE FULL FLOATING-POINT AND EXACT INTEGER VALUES.
2. FRONTEND PRESENTATION LAYERS MUST APPLY STATISTICAL ROUNDING AND RANGE FORMATTING.
====================================================================================================
```
- **In the Database & API Payload:** Stored model predictions, residuals, and official government statistics must remain unaltered (e.g. `raw_prediction: 1247839.62`, `mae_lpa: 3.714727`). Never round or truncate data inside backend storage or pipelines.
- **In the Frontend React Component:** Formatters must round values to appropriate significant figures (e.g. `formatSalaryLPA(val)` $\to$ `₹12.5 LPA`) and append the required residual interval bands.

---

## 4. CLAIMS REVISION REGISTER (HIGH-SEVERITY FINDINGS)

The top claims requiring remediation prior to production release are documented in [prediction_claims.csv](file:///e:/Job%20Market/docs/jobintel_v2/sprints/sprint_3b_3_2_2/prediction_claims.csv):

1. **Claim CLM-001 (Resolver Zero Error):**
   - *Current Text:* *"Resolver V2 achieved 0.00% false merge rate and proved false merge rate < 0.1%"*
   - *Status:* **UNSUPPORTED**.
   - *Remedy:* Replace with: *"Resolver V2 achieved 0.00% false merges across 55 negative pairs in the benchmark (95% Wilson CI: [0.00% - 6.53%]). Proving error rate < 0.1% requires N >= 3,000 true negative pairs."*
2. **Claim CLM-003 (Render Zero OOM Risk):**
   - *Current Text:* *"In-memory storage on Render Free tier operates with zero OOM risk."*
   - *Status:* **MISLEADING**.
   - *Remedy:* Replace with: *"In-memory dataset heap (~0.84 MB for 100 employers) presents low baseline risk, but large unpaginated JSON serialization responses and concurrent query spikes present operational risk without pagination."*
3. **Claim CLM-006 (Title Mapping 95% Confidence):**
   - *Current Text:* *"Confidence scores of 0.95 represent 95% mapping probability."*
   - *Status:* **UNSUPPORTED**.
   - *Remedy:* Replace with: *"Heuristic mapping confidence is an uncalibrated similarity indicator. Calibrated probability requires post-hoc Platt / temperature scaling."*
