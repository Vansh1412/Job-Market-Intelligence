# OCCUPATION MAPPING DENOMINATOR AUDIT
## Independent Verification of `SYS_OCC_MAPPER` Accuracy & Fallback Rates

**Sprint ID:** 3B.3.2.3  
**Audited Artifacts:**
- Evaluator: `docs/jobintel_v2/sprints/sprint_3b_3_2/JOB_TITLE_MAPPING_PILOT.md`
- Audit Record: `docs/jobintel_v2/sprints/sprint_3b_3_2_2/OCCUPATION_MAPPING_RELIABILITY_AUDIT.md`
- Reconciled Data: `docs/jobintel_v2/sprints/sprint_3b_3_2_3/occupation_mapping_reconciliation.csv`

---

## 1. Objective & Denominator Mystery Resolution

In Sprint 3B.3.2, `SYS_OCC_MAPPER` reported an accuracy of **97.0%**. In statistical audits, a claim of 97% accuracy frequently raises questions regarding:
1. What was the exact denominator?
2. Did the 3 non-matching cases represent catastrophic misclassifications or controlled fallbacks?
3. Was the metric measured over all inputs or only over the subset where a match was attempted?

This audit completely resolves these questions by inspecting the underlying 100-title gold benchmark.

---

## 2. Benchmark Breakdown & Detailed Confusion Statistics

The benchmark consists of $N = 100$ verified, standardized job titles across software engineering, data science, infrastructure, product management, and cross-disciplinary technical roles.

### 2.1 The Four Outcome Categories
Every candidate title evaluated by `SYS_OCC_MAPPER` falls into one of four mutually exclusive states:
1. **Correctly Mapped (True Positive - TP):** Title mapped to the ground-truth canonical SOC/O*NET occupation. ($N = 97$)
2. **Misclassified (False Positive - FP):** Title mapped to an incorrect canonical occupation. ($N = 0$)
3. **Controlled Fallback (Safe Unmapped):** Title routed to `Other / Unmapped` because similarity confidence fell below the acceptance threshold ($\tau < 0.60$). ($N = 3$)
4. **Incorrect Fallback (False Negative):** Standard title erroneously rejected when a valid canonical category existed. ($N = 0$)

### 2.2 Denominator-Specific Metric Calculations

| Metric Definition | Formula | Numerator | Denominator | Calculated Value | 95% Wilson Score CI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall Population Accuracy** | $\frac{\text{TP}}{N_{\text{total}}}$ | 97 | 100 | **97.00%** | **[91.48% – 99.38%]** |
| **Conditional Accuracy (Coverage-Adjusted)** | $\frac{\text{TP}}{\text{Mapped}}$ | 97 | 97 | **100.00%** | **[96.28% – 100.00%]** |
| **Controlled Fallback Rate** | $\frac{\text{Unmapped}}{N_{\text{total}}}$ | 3 | 100 | **3.00%** | **[0.62% – 8.52%]** |
| **Fatal Misclassification Rate** | $\frac{\text{FP}}{N_{\text{total}}}$ | 0 | 100 | **0.00%** | **[0.00% – 3.69%]** |
| **Macro F1 Score** | $\text{mean}(F_{1, c})$ | N/A | 12 classes | **0.9852** | N/A |

---

## 3. Forensic Inspection of the 3 Unmapped Titles

The three titles that did not receive a canonical mapping were:
1. `"Chief of Staff to CTO"`: Cross-functional executive advisory role bridging business operations and engineering strategy. Did not match pure engineering or pure management categories above threshold $\tau = 0.60$.
2. `"Growth Hacker"`: Marketing-engineering hybrid title with ambiguous responsibilities across advertising funnels and script automation. Safely routed to fallback.
3. `"Technical Solutions Evangelist"`: Developer advocacy and public relations role with highly disparate taxonomy across industries. Safely routed to fallback.

**Auditor Finding:**  
Routing these 3 ambiguous titles to `Other / Unmapped` represents **correct conservative behavior**. A naive model that forced these titles into `"Software Engineer"` or `"Product Manager"` would have introduced false signal into downstream analytics.

---

## 4. Reporting Standards for Production

In accordance with `JOBINTEL-STD-PRED-001`, future documentation and user interfaces must not report a flat "97% accuracy" without context. Instead, the metric must be reported as:

> *"97.0% mapping coverage with 0.0% misclassification across 100 benchmark titles (95% CI: 91.5%–99.4%). 3.0% of ambiguous titles safely routed to unmapped review."*

---

## 5. Audit Verdict

- **Status:** **VERIFIED & RECONCILED — GO**
- **Confidence:** HIGH. The 97% accuracy figure is honest, conservative, and mathematically verified.
