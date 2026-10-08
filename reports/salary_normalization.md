# Salary Normalization and Target Variable Engineering Report
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Dataset:** Tech Job Postings with Parsed Salaries (ATS Direct), Package `jobs-tier1-L-2026-08-01`  
**Date:** October 5, 2026  

---

## 1. Executive Summary

Salary is the primary continuous target variable ($y$) for the regression track of INT234 Academic Task 2. This report establishes the scientific protocol for salary validation, period harmonization, currency treatment, midpoint construction, and outlier detection.

To avoid introducing synthetic precision or purchasing power parity (PPP) confounding, the primary regression modeling population is restricted to **USD Annual Salaries**. With **24,358 valid technical postings**, this cohort provides exceptional statistical power and domain realism without relying on noisy historical foreign-exchange conversions.

---

## 2. Original Salary Fields & Data Integrity Audit

Dataset A provides five distinct salary-related fields:

| Field Name | Type | Description | Non-Null Rate (Raw) | Non-Null Rate (Dedup) |
|---|---|---|---:|---:|
| `salary_min` | `float64` | Lower bound of posted salary range | 27.2% (107,151) | 29.56% (99,329) |
| `salary_max` | `float64` | Upper bound of posted salary range | 27.2% (107,151) | 29.56% (99,329) |
| `salary_currency` | `object` | ISO 4217 currency code (USD, GBP, EUR, CAD, etc.) | 27.2% (107,151) | 29.56% (99,329) |
| `salary_period` | `object` | Pay period: `year`, `hour`, `month`, `week`, `day` | 27.2% (107,151) | 29.56% (99,329) |
| `salary_from_text` | `bool` | `False` if structured ATS field; `True` if parsed from body | 100.0% (394,300) | 100.0% (335,995) |

### Integrity Verification:
- **Dual Bound Co-occurrence:** Exactly 100% of records with `salary_min` also possess `salary_max`. There are zero single-bounded or asymmetric records.
- **Bound Order Verification:** Across all 99,329 records with salary, **zero records have `salary_min > salary_max`** (100% logical consistency).
- **Non-Positive Values:** Exactly 121 records contain non-positive values (`salary_min <= 0` or `salary_max <= 0`), which are discarded as invalid placeholders.
- **Unusable/Missing Records:** 236,666 postings (70.44% of deduplicated rows) have null salaries. As mandated by zero-leakage rules, missing target values are **never fabricated or imputed**. Unlabeled rows are cleanly partitioned away from the supervised regression dataset.

---

## 3. Empirical Distribution: Currencies & Pay Periods

### 3.1 Pay Periods (Deduplicated Corpus)
| Period | Count | Share (%) | Description |
|---|---:|---:|---|
| `year` | 68,284 | 68.75% | Annual salaried compensation (standard for salaried knowledge workers) |
| `hour` | 24,744 | 24.91% | Hourly wage rates (common in contracting, retail, support) |
| `month` | 5,978 | 6.02% | Monthly pay rates (common in European and Asian postings) |
| `week` | 191 | 0.19% | Weekly stipends/contracting rates |
| `day` | 132 | 0.13% | Daily contractor day-rates |

### 3.2 Top Currencies (Deduplicated Corpus)
| Currency | Total Valid | Year | Hour | Month | Week | Day |
|---|---:|---:|---:|---:|---:|---:|
| **USD** | **86,071 (86.65%)** | **62,138** | 22,195 | 1,586 | 107 | 45 |
| **GBP** | 7,633 (7.68%) | 2,254 | 1,988 | 3,279 | 78 | 34 |
| **EUR** | 3,640 (3.66%) | 2,429 | 375 | 780 | 4 | 52 |
| **CAD** | 1,125 (1.13%) | 999 | 119 | 6 | 1 | 0 |
| **INR** | 155 (0.16%) | 77 | 47 | 30 | 1 | 0 |
| Other (33 currencies) | 705 (0.71%) | 387 | 20 | 297 | 0 | 1 |

---

## 4. Currency Conversion Methodology vs. Currency Restriction

The project blueprint states:
> *"If currency conversion is necessary, use a clearly documented conversion methodology. If a reliable conversion is not possible, restrict the modeling dataset to an appropriate currency or explicitly justify the alternative."*

### Why Currency Restriction to USD is Scientifically Superior:
1. **Dominant Market Share:** Within technical and engineering roles, USD represents **90.58% (25,943 of 28,641)** of all available salary observations.
2. **Temporal Exchange Rate Volatility:** Dataset A postings span from January 2020 through August 2026. Converting GBP, EUR, or INR into USD using static spot rates introduces artificial variance caused by macro currency swings rather than actual skill or job compensation differences.
3. **Purchasing Power Parity (PPP) & Geographic Distortion:** In software engineering, compensation structures are geographically anchored:
   - A Senior Software Engineer in London making £85,000 (~$110,000 at nominal exchange rates) is compensated in the 80th percentile of the UK tech market.
   - However, $110,000 in the US tech market corresponds to an entry/mid-level compensation band.
   - Forcing cross-currency nominal conversion conflates geographic macro-economics with technical skill premiums, severely degrading regression performance and obscuring skill archetype valuations.
4. **Conclusion:** Restricting supervised regression modeling to **USD Annual Salaries** eliminates cross-currency noise while preserving a massive, homogeneous analytical sample of **24,358 tech postings**.

---

## 5. Target Variable Construction: `salary_midpoint`

Where both `salary_min` and `salary_max` are present and positive, the primary target variable is computed as:

$$\text{salary\_midpoint} = \frac{\text{salary\_min} + \text{salary\_max}}{2}$$

For fixed, single-rate postings where $\text{salary\_min} = \text{salary\_max}$, the formula naturally yields the exact posted salary.

### Summary Statistics for Tech USD Annual Midpoint ($N = 24,358$):
- **Mean:** \$187,176
- **Standard Deviation:** \$84,100
- **Minimum:** \$0 (filtered prior to modeling)
- **1st Percentile:** \$70,500
- **5th Percentile:** \$95,000
- **25th Percentile (Q1):** \$145,000
- **50th Percentile (Median):** \$180,000
- **75th Percentile (Q3):** \$220,000
- **95th Percentile:** \$300,000
- **99th Percentile:** \$386,000
- **Maximum:** \$4,085,000

---

## 6. Outlier Boundaries & Log Transformation

1. **Low-End Truncation:** Records with `salary_midpoint < $30,000` (representing erroneous part-time rates or mislabeled annual figures in tech) are excluded.
2. **High-End Truncation:** Postings with `salary_midpoint > $600,000` (rare executive anomalies representing <0.1% of data) are isolated to protect linear and neural estimators from extreme gradient spikes.
3. **Log Transformation:** Because salary distributions exhibit characteristic positive (right) skewness, the target variable is transformed:
   $$y_{\text{log}} = \ln(\text{salary\_midpoint})$$
   Models trained on $y_{\text{log}}$ will have predictions back-transformed ($\hat{y} = \exp(\hat{y}_{\text{log}})$) when calculating evaluation metrics in original dollar units (MAE and RMSE).
