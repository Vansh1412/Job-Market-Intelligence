# Clustering Feature Policy and Archetype Discovery Protocol
**Project:** Job Market Intelligence: Skill-Based Job Archetype Discovery and Salary Prediction  
**Course / Task:** INT234 Predictive Analytics — Academic Task 2  
**Date:** October 5, 2026  
**Status:** Audit #6 Complete & Formally Adopted  

---

## 1. Research Question Context (RQ2)

Research Question 2 states:
> **RQ2:** Do job postings naturally form meaningful, skill-based job archetypes?

In unsupervised learning, K-Means clustering partitions observations into $k$ clusters by minimizing within-cluster sum-of-squares (inertia) in Euclidean distance space:

$$J = \sum_{j=1}^{k} \sum_{i \in S_j} ||\mathbf{x}_i - \boldsymbol{\mu}_j||^2$$

If high-frequency, non-technical soft skills (such as `"communication"`, which is present in >50% of postings) or generic operational tools (such as `"crm"`, `"excel"`, `"salesforce"`) are included in $\mathbf{x}_i$, their high variance and widespread co-occurrence will dominate the principal components in PCA and compress Euclidean distances. 

Consequently, K-Means would discover trivial, uninformative clusters (e.g., *"Communicative Jobs"* vs. *"Non-Communicative Jobs"*, or *"CRM Users"* vs. *"Non-CRM Users"*) rather than genuine technological archetypes (e.g., *"ML/AI Deep Learning Stack"*, *"Cloud Native DevOps / Kubernetes Platform"*, *"Full-Stack TypeScript / React"*, *"Big Data Engineering / Spark / Kafka"*).

---

## 2. Formal Clustering Feature Policy

### Policy Rule 1: Technical Isolation for Unsupervised Modeling
The feature space for PCA dimensionality reduction and K-Means clustering will be constructed **exclusively from `skill_matrix_technical.parquet` (the 82 curated technical skills)**.

### Policy Rule 2: Scaling Protocol
Binary indicators in $\{0, 1\}^{82}$ will be centered and scaled to unit variance using `StandardScaler` prior to PCA:
$$\tilde{x}_{ij} = \frac{x_{ij} - \bar{x}_j}{s_j}$$
This ensures that emerging technologies with moderate base rates (e.g., `pytorch`, `kubernetes`, `terraform`) are not mathematically eclipsed by legacy or high-baseline terms (e.g., `sql`).

### Policy Rule 3: Dimensionality Reduction via PCA
PCA will be applied to the scaled 82-dimensional technical space:
1. Scree plots and cumulative explained variance curves will be evaluated to select the number of principal components capturing $\ge 80\%$ variance.
2. The top 2 principal components (PC1 and PC2) will be preserved for 2D archetype visualization.
3. Component factor loadings ($L = V \sqrt{\Lambda}$) will be analyzed to assign empirical semantic interpretations to each latent dimension.

### Policy Rule 4: Downstream Role of Professional and Business Skills
Professional skills (`communication`, `project-management`) and business skills (`crm`, `salesforce`, `excel`, etc.) are **not discarded**. Instead, they are reserved as covariates in:
1. **Supervised Regression Modeling:** Feature Sets A and C will include these competencies to measure their specific marginal salary premiums (RQ1).
2. **Post-Hoc Cluster Profiling:** Once clusters are formed using pure technical skills, each archetype's centroid will be cross-tabulated against communication and project management to evaluate whether certain technical archetypes demand higher soft-skill co-occurrence.

---

## 3. Summary of Decision Matrix

| Analytical Stage | Input Feature Matrix | Rationale |
|---|---|---|
| **Phase 4: PCA & Scree Plot** | `skill_matrix_technical.parquet` (82 skills) | Extracts pure technological variance vectors without soft-skill distortion. |
| **Phase 4: K-Means Clustering** | Standardized 82 technical skills (or PCA projection) | Discovers organic, stack-based job archetypes (Cloud, ML, Data, Web, Embedded). |
| **Phase 4: Archetype Profiling** | Technical clusters × All 91 skills + Roles + Salary | Comprehensive multi-dimensional profiling of each discovered archetype. |
| **Phase 5: Supervised Salary Regression** | Feature Set A / C (All 91 skills + Seniority + Roles + Locations) | Maximizes explanatory power ($R^2$) for salary prediction. |
