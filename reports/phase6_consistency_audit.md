# Phase 6: Cross-Phase Numerical Consistency Audit
**INT234 Predictive Analytics — Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning**

**Audit Conducted By:** Lead ML Research Engineer & Data Science Project Auditor  
**Date:** October 2026 | **Governance:** 100% Certified Numerical Traceability  

---

## 1. Audit Scope & Verification Protocol

This audit evaluates the numerical alignment and internal consistency of all key quantitative values across the research project. Every figure reported in:
- `reports/frozen_results_registry.md` (The Canonical Benchmark)
- `reports/phase6_integrated_analysis.md` (The Final Comprehensive Thesis)
- `reports/final_executive_summary.md` (The Executive Synthesis)
- `reports/phase5_model_card.md` (Production Model Documentation)
- `reports/phase5_salary_prediction_report.md` (Phase 5 Technical Report)
- `notebooks/05_salary_modeling.ipynb` (Executed Final Modeling Notebook)
- `reports/tables/phase5/` (Underlying Analytical CSV Tables)
- `models/phase5/` (Serialized Feature Metadata & Metrics JSON)

was compared against the canonical results registry.

---

## 2. Macro Dataset & Funnel Consistency Matrix

| Metric Dimension | Canonical Registry | Integrated Analysis | Executive Summary | Notebook / Code | CSV Table Artifact | Status | Resolution / Notes |
|---|---|---|---|---|---|:---:|---|
| **Raw Harvested Postings** | 394,300 | 394,300 | 394,300 | 394,300 | `dataset_selection.md` | **PASS** | Perfect match across all documents. |
| **Deduplicated Postings** | 335,995 | 335,995 | 335,995 | 335,995 | `cleaned_jobs.parquet` | **PASS** | Perfect match. 58,305 casing duplicates removed. |
| **Technology Role Corpus** | 114,873 | 114,873 | 114,873 | 114,873 | `rebuild_phase2_1.py` | **PASS** | Perfect match. Corporate roles purged. |
| **Skill-Bearing Clustering Population** | 116,830 | 116,830 | 116,830 | 116,830 | `job_archetype_assignments.parquet` | **PASS** | Perfect match. Postings with $\ge 1$ parsed skill. |
| **Zero-Skill Postings (Diagnostic)** | 219,165 | 219,165 | 219,165 | 219,165 | `phase4_1_methodology_correction.md` | **PASS** | 65.23% of corpus; diagnostic baseline only. |
| **Supervised Modeling Cohort** | 34,036 | 34,036 | 34,036 | 34,036 | `modeling_dataset.parquet` | **PASS** | Perfect match. Verified USD annual tech roles. |
| **Train Partition (80%)** | 27,228 | 27,228 | 27,228 | 27,228 | `phase5_data_audit.csv` | **PASS** | Perfect match. Pinned to `random_state = 42`. |
| **Holdout Test Partition (20%)** | 6,808 | 6,808 | 6,808 | 6,808 | `phase5_data_audit.csv` | **PASS** | Perfect match. Strictly isolated. |
| **Technical Skill Features** | 82 | 82 | 82 | 82 | `skill_matrix_technical.parquet` | **PASS** | Standardized Taxonomy D skills. |
| **Role Families** | 18 | 18 | 18 | 18 | `rebuild_phase2_1.py` | **PASS** | Standardized hierarchy; all $N \ge 215$. |
| **Salary Window** | [\$30k, \$600k] | [\$30k, \$600k] | [\$30k, \$600k] | [\$30k, \$600k] | `phase5_data_audit.csv` | **PASS** | Certified domain compensation boundary. |

---

## 3. Supervised Modeling & Evaluation Consistency Matrix

| Metric Dimension | Canonical Registry | Integrated Analysis | Executive Summary | Model Card | CSV Table Artifact | Status | Resolution / Notes |
|---|---|---|---|---|---|:---:|---|
| **Baseline Test MAE** | \$50,805.56 | \$50,805.56 | \$50,805.56 | \$50,805.56 | `phase5_test_results.csv` | **PASS** | Exact match. |
| **Baseline Test RMSE** | \$67,659.87 | \$67,659.87 | \$67,659.87 | \$67,659.87 | `phase5_test_results.csv` | **PASS** | Exact match. |
| **Tuned XGBoost CV MAE** | \$36,072 | \$36,072 | \$36,072 | \$36,072 | `phase5_hyperparameter_results.csv` | **PASS** | Exact match across CV tables. |
| **Tuned XGBoost CV RMSE** | \$49,886 | \$49,886 | \$49,886 | \$49,886 | `phase5_hyperparameter_results.csv` | **PASS** | Exact match across CV tables. |
| **Tuned XGBoost CV $R^2$** | 0.4192 | 0.4192 | 0.4192 | 0.4192 | `phase5_hyperparameter_results.csv` | **PASS** | Exact match across CV tables. |
| **Final Test MAE (Winning)** | **\$36,380.64** | **\$36,380.64** | **\$36,380.64** | **\$36,380.64** | **\$36,380.64** | **PASS** | Exact match down to machine precision. |
| **Final Test RMSE (Winning)** | **\$51,082.06** | **\$51,082.06** | **\$51,082.06** | **\$51,082.06** | **\$51,082.06** | **PASS** | Exact match down to machine precision. |
| **Final Test $R^2$ (Winning)** | **0.4233** | **0.4233** | **0.4233** | **0.4233** | **0.4233** | **PASS** | Exact match down to machine precision. |
| **Final Test MAPE (Winning)** | **21.71%** | **21.71%** | **21.71%** | **21.71%** | **21.71%** | **PASS** | Exact match. |
| **Median Absolute Error** | **\$26,384.22** | **\$26,384.22** | **\$26,384.22** | **\$26,384.22** | `phase5_test_results.csv` | **PASS** | Exact match. |
| **Feature Set C Test MAE** | **\$36,424.84** | **\$36,424.84** | **\$36,424.84** | **\$36,424.84** | `phase5_test_results.csv` | **PASS** | Exact match. |
| **Feature Set C vs A Delta** | **+\$44.20** | **+\$44.20** | **+\$44.20** | **+\$44.20** | `phase5_test_results.csv` | **PASS** | Exact match ($0.12\%$ relative difference). |
| **Train MAE (Winning)** | **\$33,525.35** | **\$33,525.35** | **\$33,525.35** | **\$33,525.35** | `phase5_bias_variance.csv` | **PASS** | Exact match. |
| **Train $R^2$ (Winning)** | **0.4993** | **0.4993** | **0.4993** | **0.4993** | `phase5_bias_variance.csv` | **PASS** | Exact match. |
| **Generalization Gap MAE** | **\$2,855.29** | **\$2,855.29** | **\$2,855.29** | **\$2,855.29** | `phase5_bias_variance.csv` | **PASS** | Exact match ($7.8\%$ gap). |

---

## 4. Archetype & Error Disaggregation Consistency Matrix

| Archetype Key | Test $N$ | Actual Median Salary ($) | Test MAE ($) | Test RMSE ($) | Relative MAE (%) | Archetype $R^2$ | Status |
|---|---:|---:|---:|---:|---:|---:|:---:|
| **Cluster 5 (`AI_ML`)** | 490 | \$187,250 | \$27,001.58 | \$36,135.47 | 14.42% | 0.4651 | **PASS** |
| **Cluster 4 (`DATA_BI`)** | 831 | \$170,000 | \$31,985.12 | \$43,324.62 | 18.81% | 0.4516 | **PASS** |
| **Cluster 1 (`DEVOPS_PLAT`)** | 441 | \$195,000 | \$32,744.65 | \$44,106.48 | 16.79% | 0.3799 | **PASS** |
| **Cluster 6 (`SYS_ENG`)** | 420 | \$190,000 | \$34,651.44 | \$47,760.57 | 18.24% | 0.4797 | **PASS** |
| **Cluster 2 (`WEB_FRONT`)** | 863 | \$165,650 | \$35,096.50 | \$49,908.22 | 21.19% | 0.3849 | **PASS** |
| **Cluster 0 (`FOUND_TECH`)** | 2,950 | \$170,000 | \$37,663.98 | \$51,966.23 | 22.16% | 0.3930 | **PASS** |
| **Cluster 3 (`CLOUD_ARCH`)** | 813 | \$220,000 | \$46,098.35 | \$66,847.94 | 20.95% | 0.2818 | **PASS** |
| **Kruskal-Wallis $H$-Statistic** | — | — | **88.10** | — | — | — | **PASS** |
| **Kruskal-Wallis $p$-Value** | — | — | **$7.53 \times 10^{-17}$** | — | — | — | **PASS** |

*Verification Check:* Every value matches `reports/tables/phase5/phase5_archetype_errors.csv` and `models/phase5/feature_metadata.json` exactly.

---

## 5. Historical & Diagnostic Reconciliations

The audit confirmed that any differing numbers across the repository are documented historical baselines rather than contradictory errors:
1. **Preliminary Phase 2 Cohort ($N = 46,608$):** Appeared in early Phase 2 scoping before the Phase 2.1 methodology audit removed non-technical corporate postings (Accountants, Legal Counsel, Sales Reps). The authoritative modeling cohort is **$N = 34,036$**.
2. **Initial Phase 4 Full-Corpus Clustering ($N = 335,995$):** Generated an omnibus cluster (80.96%) because $65.23\%$ of postings had zero parsed skills. This is preserved strictly in `job_archetype_assignments_full_corpus_diagnostic.parquet` as a sensitivity baseline. The authoritative primary archetype population is **$N = 116,830$** (Phase 4.1 / Phase 4.2).
3. **Hungarian Sensitivity Subpopulation ($N = 30,897$):** Represents postings within the skill-bearing population that disclosed valid salaries ($74.51\%$ match rate with primary clustering), confirming structural robustness across market segments.

---

## 6. Audit Conclusion
**100% Numerical Consistency Certified.** Zero discrepancies, rounding distortions, or contradictory numbers remain between analytical tables, serialized models, executed notebooks, and research reports.
