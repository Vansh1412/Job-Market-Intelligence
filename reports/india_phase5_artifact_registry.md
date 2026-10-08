# Phase India-5 Artifact Registry

**Project:** INT234 Predictive Analytics -- Job Market Intelligence  
**Phase:** India-5 (Skill Archetype Discovery + PCA + K-Means + Stability + Salary Association + RQ3 Error Stratification)  
**Date:** October 7, 2026  
**Status:** Certified & Validated (30/30 Gates Passed)  

---

## 1. Source Code

| Artifact | File Path | Purpose | Size | Status |
|---|---|---|---|---|
| **Archetype Engine** | [`src/india/archetypes.py`](file:///e:/Job%20Market/src/india/archetypes.py) | Master production script for population audit, PCA evaluation, K-Means cluster sweep, stability analysis, archetype profiling, Kruskal-Wallis salary testing, leakage-safe holdout error stratification, figure rendering, and artifact serialization. | 65,038 B | Validated |

---

## 2. Processed Datasets

| Artifact | File Path | Purpose | Size | Status |
|---|---|---|---|---|
| **Skill PCA Projection** | [`data/processed/india/india_skill_pca.parquet`](file:///e:/Job%20Market/data/processed/india/india_skill_pca.parquet) | Retained 15 principal components for all 5,323 skill-bearing postings, mapped with stable identifiers (`job_id`, `content_fingerprint`). | 783,165 B | Validated |
| **Archetype Assignments**| [`data/processed/india/india_archetype_assignments.parquet`](file:///e:/Job%20Market/data/processed/india/india_archetype_assignments.parquet) | Stable archetype assignments (`IND_ARC_01` to `IND_ARC_06` and `IND_ARC_UNASSIGNED`) across all 5,859 cohort postings. Excludes target/salary features to prevent leakage. | 261,867 B | Validated |

---

## 3. Serialized Models & Metadata

| Artifact | File Path | Purpose | Size | Status |
|---|---|---|---|---|
| **PCA Model** | [`models/india/india_pca_v1.pkl`](file:///e:/Job%20Market/models/india/india_pca_v1.pkl) | Fitted 15-component centered covariance PCA model on binary skill matrix. | 37,446 B | Validated |
| **K-Means Model** | [`models/india/india_kmeans_v1.pkl`](file:///e:/Job%20Market/models/india/india_kmeans_v1.pkl) | Fitted $k=6$ K-Means model on the 15-dimensional PCA representation. | 22,617 B | Validated |
| **Holdout Pipeline** | [`models/india/india_holdout_archetype_pipeline.pkl`](file:///e:/Job%20Market/models/india/india_holdout_archetype_pipeline.pkl) | Leakage-safe PCA + K-Means pipeline fitted exclusively on training partition skills for out-of-sample holdout error stratification. | 55,644 B | Validated |
| **Archetype Metadata** | [`models/india/india_archetype_metadata.json`](file:///e:/Job%20Market/models/india/india_archetype_metadata.json) | Complete machine-readable metadata specifying cohort, parameters, stability metrics, archetype definitions, and formal test statistics. | 4,494 B | Validated |

---

## 4. Analytical Tables (15 Required CSVs)

| Table Artifact | File Path | Purpose | Size | Status |
|---|---|---|---|---|
| **1. Skill Prevalence** | [`reports/tables/india/india_skill_prevalence.csv`](file:///e:/Job%20Market/reports/tables/india/india_skill_prevalence.csv) | Prevalence, frequency counts, and sparsity percentages across all 284 skills ($N = 5,323$). | 19,444 B | Validated |
| **2. PCA Variance** | [`reports/tables/india/india_pca_variance.csv`](file:///e:/Job%20Market/reports/tables/india/india_pca_variance.csv) | Eigenvalues, explained variance ratios, and cumulative variance across all components. | 21,115 B | Validated |
| **3. PCA Loadings** | [`reports/tables/india/india_pca_loadings.csv`](file:///e:/Job%20Market/reports/tables/india/india_pca_loadings.csv) | Factor loadings for all 284 skills across the 15 retained principal components. | 99,944 B | Validated |
| **4. K-Means Metrics** | [`reports/tables/india/india_kmeans_metrics.csv`](file:///e:/Job%20Market/reports/tables/india/india_kmeans_metrics.csv) | Silhouette, Davies-Bouldin, Calinski-Harabasz, inertia, and size imbalance across $k \in [2, 10]$. | 1,075 B | Validated |
| **5. Cluster Stability** | [`reports/tables/india/india_cluster_stability.csv`](file:///e:/Job%20Market/reports/tables/india/india_cluster_stability.csv) | Pairwise ARI and AMI across seeds `[42, 7, 21, 100, 123]` (Mean ARI = 0.8035). | 565 B | Validated |
| **6. Archetype Sizes** | [`reports/tables/india/india_archetype_sizes.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_sizes.csv) | Observation counts and market shares for all 6 archetypes and unassigned cohort. | 725 B | Validated |
| **7. Archetype Profiles** | [`reports/tables/india/india_archetype_profiles.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_profiles.csv) | Multidimensional profiles (dominant roles, skills, experience, work mode, top cities). | 3,381 B | Validated |
| **8. Skill Lift** | [`reports/tables/india/india_archetype_skill_lift.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_skill_lift.csv) | Prevalence enrichment ratios ($\text{Lift} = P_{\text{cluster}} / P_{\text{overall}}$) for all 284 skills. | 204,854 B | Validated |
| **9. Salary Summary** | [`reports/tables/india/india_archetype_salary_summary.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_salary_summary.csv) | Descriptive salary statistics (Median, IQR, Mean, Std, Min, Max, Delta vs cohort). | 974 B | Validated |
| **10. Salary Test** | [`reports/tables/india/india_archetype_salary_test.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_salary_test.csv) | Kruskal-Wallis omnibus test results ($H = 817.91, p = 1.55 \times 10^{-174}, \epsilon^2 = 0.1529$). | 387 B | Validated |
| **11. Salary Post-Hoc** | [`reports/tables/india/india_archetype_posthoc.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_posthoc.csv) | Pairwise Dunn rank-sum tests with Holm multiplicity adjustment across all 15 pairs. | 2,996 B | Validated |
| **12. Error Summary** | [`reports/tables/india/india_archetype_error_summary.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_error_summary.csv) | Holdout prediction error metrics (MAE, RMSE, MedAE, Mean Residual, Relative MAE). | 1,307 B | Validated |
| **13. Error Test** | [`reports/tables/india/india_archetype_error_test.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_error_test.csv) | Kruskal-Wallis test on absolute errors ($H = 66.15, p = 6.48 \times 10^{-13}, \epsilon^2 = 0.0575$). | 411 B | Validated |
| **14. Error Post-Hoc** | [`reports/tables/india/india_archetype_error_posthoc.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_error_posthoc.csv) | Pairwise Dunn rank-sum tests with Holm adjustment on prediction errors. | 3,302 B | Validated |
| **15. Integrated Summary**| [`reports/tables/india/india_archetype_salary_error_summary.csv`](file:///e:/Job%20Market/reports/tables/india/india_archetype_salary_error_summary.csv) | Master synthesis table linking Archetype, N, Share, Salary, IQR, and Error metrics. | 1,308 B | Validated |

---

## 5. Research Figures (13 Required PNGs)

| Figure Artifact | File Path | Visual Content | Size | Status |
|---|---|---|---|---|
| **Figure 1** | [`reports/figures/india/india_skill_prevalence.png`](file:///e:/Job%20Market/reports/figures/india/india_skill_prevalence.png) | Horizontal bar chart of top 25 skills by market prevalence in skill-bearing postings. | 113,880 B | Validated |
| **Figure 2** | [`reports/figures/india/india_pca_scree.png`](file:///e:/Job%20Market/reports/figures/india/india_pca_scree.png) | PCA scree curve with eigenvalue elbow indicator at 15 components. | 90,694 B | Validated |
| **Figure 3** | [`reports/figures/india/india_pca_cumulative_variance.png`](file:///e:/Job%20Market/reports/figures/india/india_pca_cumulative_variance.png) | Cumulative explained variance curve showing 37.74% at 15 components. | 94,942 B | Validated |
| **Figure 4** | [`reports/figures/india/india_pca_loadings.png`](file:///e:/Job%20Market/reports/figures/india/india_pca_loadings.png) | Top positive and negative loading skills for PC1 (Java Backend) and PC2 (Big Data). | 111,736 B | Validated |
| **Figure 5** | [`reports/figures/india/india_pca_clusters.png`](file:///e:/Job%20Market/reports/figures/india/india_pca_clusters.png) | 2D scatter of PC1 vs PC2 colored by archetype with descriptive caption. | 373,098 B | Validated |
| **Figure 6** | [`reports/figures/india/india_cluster_sizes.png`](file:///e:/Job%20Market/reports/figures/india/india_cluster_sizes.png) | Bar chart of archetype cluster sizes ($N$ and percentage of skill-bearing postings). | 133,029 B | Validated |
| **Figure 7** | [`reports/figures/india/india_archetype_skill_heatmap.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_skill_heatmap.png) | Heatmap of skill prevalence across archetypes for 24 discriminative skills. | 264,253 B | Validated |
| **Figure 8** | [`reports/figures/india/india_archetype_skill_lift_heatmap.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_skill_lift_heatmap.png) | Heatmap of skill lift ratios ($P_{\text{cluster}} / P_{\text{overall}}$) across archetypes. | 290,063 B | Validated |
| **Figure 9** | [`reports/figures/india/india_archetype_salary_distribution.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_salary_distribution.png) | Boxplots of observed annual salary (LPA) by archetype with cohort median benchmark. | 106,250 B | Validated |
| **Figure 10** | [`reports/figures/india/india_archetype_salary_medians.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_salary_medians.png) | Ranked horizontal bar chart of median salary by archetype with IQR error bars. | 133,935 B | Validated |
| **Figure 11** | [`reports/figures/india/india_archetype_error_mae.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_error_mae.png) | Dual-axis bar chart comparing Holdout MAE (LPA) and Relative MAE (%) by archetype. | 86,117 B | Validated |
| **Figure 12** | [`reports/figures/india/india_archetype_error_distribution.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_error_distribution.png) | Boxplot distribution of absolute prediction errors on held-out test data by archetype. | 89,746 B | Validated |
| **Figure 13** | [`reports/figures/india/india_archetype_predicted_vs_actual.png`](file:///e:/Job%20Market/reports/figures/india/india_archetype_predicted_vs_actual.png) | Scatter plot of actual vs predicted salary on holdout, colored by archetype. | 329,867 B | Validated |

---

## 6. Formal Research Reports

| Report Artifact | File Path | Purpose | Size | Status |
|---|---|---|---|---|
| **Phase 5 Research Report** | [`reports/india_phase5_archetype_discovery.md`](file:///e:/Job%20Market/reports/india_phase5_archetype_discovery.md) | Exhaustive 28-section scientific monograph detailing research questions, methodology, stability, salary associations, holdout error stratification, and limitations. | 27,107 B | Validated |
| **Artifact Registry** | [`reports/india_phase5_artifact_registry.md`](file:///e:/Job%20Market/reports/india_phase5_artifact_registry.md) | Comprehensive catalog and integrity registry of all Phase India-5 deliverables. | Current | Validated |
