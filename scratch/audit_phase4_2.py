import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    adjusted_mutual_info_score,
    silhouette_score,
    davies_bouldin_score
)
from scipy.optimize import linear_sum_assignment
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load data
DATA_DIR = "data/processed"
MODELS_DIR = "models"

X_raw = pd.read_parquet(os.path.join(DATA_DIR, "skill_matrix_technical.parquet"))
jobs_df = pd.read_parquet(os.path.join(DATA_DIR, "cleaned_jobs.parquet"))
model_df = pd.read_parquet(os.path.join(DATA_DIR, "modeling_dataset.parquet"))
assignments = pd.read_parquet(os.path.join(DATA_DIR, "job_archetype_assignments.parquet"))

primary_mask = (X_raw.sum(axis=1) > 0).values
X_prim = X_raw[primary_mask].copy()
jobs_prim = jobs_df[primary_mask].copy()

# 2. Check k=2 profiles and why k=2 collapses ecosystems
print("=== AUDIT: k=2 vs k=7 PROFILES ===")
scaler_cov = joblib.load(os.path.join(MODELS_DIR, "scaler_phase4_1.pkl"))
pca_cov = joblib.load(os.path.join(MODELS_DIR, "pca_phase4_1.pkl"))

X_pca = pca_cov.transform(scaler_cov.transform(X_prim.values.astype(np.float32)))

km2 = KMeans(n_clusters=2, random_state=42, n_init=10).fit(X_pca)
labels2 = km2.labels_
for c in range(2):
    n_c = (labels2 == c).sum()
    pct_c = n_c / len(labels2) * 100
    prev = X_prim[labels2 == c].mean().sort_values(ascending=False).head(5)
    print(f"k=2 Cluster {c}: N={n_c:,} ({pct_c:.1f}%), Top skills: {dict(np.round(prev, 3))}")

# 3. Audit FOUND_TECH heterogeneity
print("\n=== AUDIT: FOUND_TECH (Cluster 0) HETEROGENEITY ===")
c0_mask = (assignments["cluster_id"] == 0).values
X_c0 = X_prim[c0_mask]
jobs_c0 = jobs_prim[c0_mask]

skill_counts_c0 = X_c0.sum(axis=1)
print(f"Cluster 0 (FOUND_TECH) N = {len(X_c0):,} ({len(X_c0)/len(X_prim):.2%})")
print(f"Skill counts in Cluster 0:")
print(f"  Min: {skill_counts_c0.min()}, Median: {skill_counts_c0.median()}, Mean: {skill_counts_c0.mean():.2f}, Max: {skill_counts_c0.max()}")
print(f"  Single-skill postings (count == 1): {(skill_counts_c0 == 1).sum():,} ({(skill_counts_c0 == 1).mean():.2%})")
print(f"  Two-skill postings (count == 2): {(skill_counts_c0 == 2).sum():,} ({(skill_counts_c0 == 2).mean():.2%})")
print(f"  <= 2 skills postings: {(skill_counts_c0 <= 2).sum():,} ({(skill_counts_c0 <= 2).mean():.2%})")

# Top skills in C0
prev_c0 = X_c0.mean().sort_values(ascending=False).head(8)
print("Top skills in Cluster 0:")
for s, v in prev_c0.items():
    print(f"  {s}: {v:.2%}")

# Top role families in C0
rf_c0 = jobs_c0["role_family"].value_counts(normalize=True).head(5)
print("Top role families in Cluster 0:")
for r, v in rf_c0.items():
    print(f"  {r}: {v:.2%}")

# Centroid distance analysis
km7 = joblib.load(os.path.join(MODELS_DIR, "kmeans_phase4_1_k7.pkl"))
centroids = km7.cluster_centers_

# Distances of points in C0 to C0 centroid vs other clusters
dists_c0 = np.linalg.norm(X_pca[c0_mask] - centroids[0], axis=1)
print(f"Mean distance to centroid in C0: {dists_c0.mean():.4f}, Std: {dists_c0.std():.4f}")

for c in range(1, 7):
    dists_c = np.linalg.norm(X_pca[assignments['cluster_id'] == c] - centroids[c], axis=1)
    print(f"Cluster {c} ({assignments.loc[assignments['cluster_id'] == c, 'archetype_name'].iloc[0]}) mean dist to centroid: {dists_c.mean():.4f}, Std: {dists_c.std():.4f}")

# 4. Formal correspondence between Primary Model and Salary-Cohort Sensitivity
print("\n=== AUDIT: FORMAL CORRESPONDENCE BETWEEN PRIMARY AND SALARY COHORT ===")
salary_job_ids = set(model_df["job_id"].values)
salary_skill_mask = jobs_prim["job_id"].isin(salary_job_ids)

X_pca_salary = X_pca[salary_skill_mask]
pred_from_primary = km7.predict(X_pca_salary)

km_salary_independent = KMeans(n_clusters=7, random_state=42, n_init=10).fit(X_pca_salary)
labels_salary_independent = km_salary_independent.labels_

ari_salary = adjusted_rand_score(pred_from_primary, labels_salary_independent)
ami_salary = adjusted_mutual_info_score(pred_from_primary, labels_salary_independent)

print(f"Salary Cohort (N={salary_skill_mask.sum():,}):")
print(f"  ARI between Primary Model Predictions and Independent Salary KMeans: {ari_salary:.4f}")
print(f"  AMI between Primary Model Predictions and Independent Salary KMeans: {ami_salary:.4f}")

# Hungarian Matching
cost_matrix = -pd.crosstab(pred_from_primary, labels_salary_independent).values
row_ind, col_ind = linear_sum_assignment(cost_matrix)
hungarian_agreement = -cost_matrix[row_ind, col_ind].sum() / len(pred_from_primary)
print(f"  Hungarian Optimal Match Rate: {hungarian_agreement:.2%}")

# Centroid Cosine Similarity
sim_matrix = cosine_similarity(centroids, km_salary_independent.cluster_centers_)
matched_sims = [sim_matrix[r, c] for r, c in zip(row_ind, col_ind)]
print(f"  Mean Centroid Cosine Similarity (matched): {np.mean(matched_sims):.4f}")
for r, c in zip(row_ind, col_ind):
    print(f"    Primary Cluster {r} -> Salary Cluster {c}: Cosine Sim = {sim_matrix[r, c]:.4f}")
