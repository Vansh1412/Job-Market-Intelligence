# JOBINTEL 2.0 — PREDICTION REALISM & EVIDENCE INTEGRITY STANDARD
## Engineering Standard, Language Governance & Statistical Reporting Principles

**Standard Identifier:** `JOBINTEL-STD-PRED-001`  
**Version:** 1.0.0  
**Effective Date:** November 2026  
**Auditor & Lead Architect:** Senior ML Reliability Engineer & Statistical Auditor  
**Scope:** Platform-Wide (Backend, Models, APIs, Documentation, Frontend UI, Marketing Disclosures)  

---

## 1. PURPOSE & CORE PHILOSOPHY

JOBINTEL 2.0 is an enterprise-grade Global Career and Employer Intelligence Platform. Its mission is to deliver actionable, evidence-backed labour market intelligence without misleading job seekers, employers, or analysts into treating statistical estimates as guaranteed real-world outcomes.

### 1.1 The Golden Rule of Realistic Reporting
```
====================================================================================================
THE GOLDEN RULE OF PREDICTION REPORTING:
DO NOT FABRICATE, MODIFY, LOWER, RAISE, OR TWIST ACTUAL EVALUATION METRICS TO MAKE THEM LOOK REALISTIC.
====================================================================================================
```
- If a model genuinely achieves **97% accuracy** on a rigorous, validated evaluation set, report **97.0%**, together with the exact test sample size, methodology, and operational limitations.
- If a model achieves **76% accuracy**, report **76.0%** honestly, documenting the error patterns and business bounds.
- If a model achieves **100% accuracy** on a benchmark, report **100.0%**, while explicitly investigating and disclosing the sample boundaries (e.g., small benchmark size, rule-based coverage).
- **The objective is realistic reporting, never artificially manufactured metrics.**

---

## 2. EVALUATION TARGET PHILOSOPHY (THE 85–90% ASPIRATION)

JOBINTEL adopts approximately **85% to 90%** as a practical evaluation aspiration for classification, extraction, and mapping tasks where the dataset, label quality, and real-world variance make such a target statistically meaningful.

### 2.1 Critical Clarifications on the Target Range
1. **Not a Mandatory Minimum:** Models achieving below 85% (such as exploratory clustering or novel NLP tasks) are acceptable if their limitations, confidence thresholds, and review workflows are honestly communicated.
2. **Not a Mandatory Maximum or Ceiling:** High performance (> 90%) is celebrated and retained when independently validated. Never intentionally degrade a model to fit within 85–90%.
3. **Task-Specific Metric Selection:**
   - **Continuous Regression (Salary):** Accuracy percentages are mathematically invalid. Use Mean Absolute Error (MAE), Median Absolute Error, Root Mean Squared Error (RMSE), and $R^2$.
   - **Entity Resolution:** Accuracy is misleading due to severe class imbalance. Prioritize Precision and Type I False Merge Rates over raw accuracy.
   - **Taxonomy Mapping:** Track overall accuracy alongside unmapped rates and Expected Calibration Error (ECE).

---

## 3. PROHIBITED CERTAINTY LANGUAGE VS. PERMITTED EVIDENCE LANGUAGE

Uncertainty is an intrinsic property of statistical inference and labour market dynamics. Absolute claims mislead users and create legal liability.

### 3.1 Prohibited Statements (Strictly Banned)
- ❌ *"100% accurate predictions"*
- ❌ *"Guaranteed salary"* or *"Guaranteed CTC"*
- ❌ *"Definitely the best career path / occupation"*
- ❌ *"100% employer match"*
- ❌ *"This candidate will earn ₹X / $Y"*
- ❌ *"The model is completely reliable and zero error"*
- ❌ *"This company will hire N employees next quarter"*
- ❌ *"Mastering this skill guarantees a job offer"*

### 3.2 Mandated Replacement Language
- ✅ *"The model estimates a benchmark compensation of..."*
- ✅ *"Based on N observed statutory filings / job postings..."*
- ✅ *"The estimated statistical range is [Lower - Upper]..."*
- ✅ *"The available labour market evidence suggests..."*
- ✅ *"This profile exhibits high estimated similarity to..."*
- ✅ *"This result has limited supporting evidence and should be interpreted with caution."*
- ✅ *"Advertised vacancy flow indicates active recruitment; confirmed hires and net growth are not measured."*

---

## 4. MATHEMATICAL DISTINCTION OF PREDICTION CONCEPTS

Platform components must never conflate distinct statistical quantities in documentation, APIs, or UI cards:

| Statistical Concept | Mathematical Definition | Permitted Interpretation |
| :--- | :--- | :--- |
| **Model Conditional Median** | $\hat{y} = f(X)$ from regression | Model's central tendency estimate given input attributes. |
| **Observed Cohort Median** | $\text{Median}(Y_{\text{cohort}})$ | Empirical median of recorded historical observations. |
| **Prediction Interval** | $[\hat{y} - z \cdot \hat{\sigma}, \hat{y} + z \cdot \hat{\sigma}]$ | Statistical uncertainty range encompassing a future observation. |
| **Salary Range** | $[y_{\min}, y_{\max}]$ from posting | Employer's advertised compensation bracket. |
| **Heuristic Match Score** | $S \in [0, 1]$ from rules/TF-IDF | Feature similarity; **NOT a calibrated probability**. |
| **Calibrated Probability** | $P(Y=1 \mid S = s) \approx s$ | Empirically verified likelihood of correctness. |
