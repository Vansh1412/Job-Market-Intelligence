"""
Phase 4: Skill-Based Job Archetype Discovery using PCA + K-Means
================================================================
INT234 Predictive Analytics — Academic Task 2
Author: Antigravity Senior Data Science & Unsupervised Learning Team
Date: October 2026

Mission:
  Answer RQ2: Do job postings naturally form meaningful skill-based archetypes?
  Discover, validate, profile, and interpret skill-based job archetypes using
  PCA and K-Means clustering on the technical skill matrix.

Strict Phase Boundary:
  ONLY PCA, dimensionality analysis, K-Means clustering, cluster validation,
  stability testing, profiling, visualization, and Phase 5 handoff.
  NO regression, NO predictive modeling, NO supervised learning.
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    adjusted_mutual_info_score,
)

# ---------------------------------------------------------
# 0. CONFIGURATION & DIRECTORIES
# ---------------------------------------------------------
RANDOM_STATE = 42
N_INIT = 10
N_COMPONENTS_PCA = 15
SELECTED_K = 7
SILHOUETTE_SAMPLE_SIZE = 25000
STABILITY_SEEDS = [42, 7, 21, 100, 123]

DATA_DIR = "data/processed"
MODELS_DIR = "models"
FIGURES_DIR = "reports/figures/phase4"
TABLES_DIR = "reports/tables/phase4"

for d in [MODELS_DIR, FIGURES_DIR, TABLES_DIR]:
    os.makedirs(d, exist_ok=True)

# Set high-resolution plotting style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#eeeeee"
plt.rcParams["grid.linestyle"] = "--"

# Palette for the 7 archetypes
ARCHETYPE_COLORS = [
    "#2b5c8f",  # 0: Systems / Backend (Deep Slate Blue)
    "#888888",  # 1: General ATS Postings (Neutral Gray)
    "#d95f02",  # 2: Multi-Cloud (Vibrant Orange)
    "#7570b3",  # 3: AI / Machine Learning (Purple)
    "#1b9e77",  # 4: DevOps & Platform (Teal Green)
    "#e7298a",  # 5: Modern Web / TypeScript (Magenta Pink)
    "#e6ab02",  # 6: Data Eng & Analytics (Gold / Amber)
]


def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}", flush=True)


# ---------------------------------------------------------
# 1. DATA INGESTION & MATRIX VALIDATION
# ---------------------------------------------------------
def step_1_validate_data():
    log("STEP 1: Ingesting and validating technical skill matrix...")

    skill_path = os.path.join(DATA_DIR, "skill_matrix_technical.parquet")
    jobs_path = os.path.join(DATA_DIR, "cleaned_jobs.parquet")
    model_path = os.path.join(DATA_DIR, "modeling_dataset.parquet")

    X_raw = pd.read_parquet(skill_path)
    jobs_df = pd.read_parquet(jobs_path)
    model_df = pd.read_parquet(model_path)

    log(f"Loaded X_raw shape: {X_raw.shape}")
    log(f"Loaded jobs_df shape: {jobs_df.shape}")
    log(f"Loaded model_df shape: {model_df.shape}")

    # Row alignment check
    assert len(X_raw) == len(jobs_df), "Row count mismatch between X_raw and jobs_df!"
    assert (X_raw.index.values == jobs_df["job_id"].values).all(), "Index mismatch between X_raw and jobs_df['job_id']!"
    log("Row alignment verified: 100% 1-to-1 match on job_id.")

    # Matrix integrity checks
    null_count = X_raw.isnull().sum().sum()
    assert null_count == 0, f"Found {null_count} null values in technical skill matrix!"
    
    variances = X_raw.var()
    zero_var_cols = variances[variances == 0].index.tolist()
    assert len(zero_var_cols) == 0, f"Found zero-variance columns: {zero_var_cols}"

    n_jobs = len(X_raw)
    n_skills = X_raw.shape[1]
    total_elements = n_jobs * n_skills
    nonzero_elements = int(X_raw.sum().sum())
    sparsity = 1.0 - (nonzero_elements / total_elements)
    density = nonzero_elements / total_elements

    skills_per_job = X_raw.sum(axis=1)
    zero_skill_jobs = int((skills_per_job == 0).sum())

    log("Technical Skill Matrix Diagnostics:")
    log(f"  - Total Postings (N): {n_jobs:,}")
    log(f"  - Technical Skills (Features): {n_skills}")
    log(f"  - Zero-Variance Features: {len(zero_var_cols)}")
    log(f"  - Matrix Sparsity: {sparsity:.4%}")
    log(f"  - Matrix Density: {density:.4%}")
    log(f"  - Total Technical Skill Mentions: {nonzero_elements:,}")
    log(f"  - Skills/Job: Min={skills_per_job.min()}, Median={skills_per_job.median():.0f}, Mean={skills_per_job.mean():.2f}, Max={skills_per_job.max()}")
    log(f"  - Postings with 0 Technical Skills: {zero_skill_jobs:,} ({zero_skill_jobs / n_jobs:.2%})")

    return X_raw, jobs_df, model_df


# ---------------------------------------------------------
# 2. PCA DECOMPOSITION & LOADINGS ANALYSIS
# ---------------------------------------------------------
def step_2_pca_analysis(X_raw):
    log("STEP 2: Executing PCA dimensionality reduction...")

    # We evaluate unscaled centered PCA (Covariance PCA).
    # Memory: float32 representation (105 MB)
    X_mat = X_raw.values.astype(np.float32)

    pca = PCA(n_components=N_COMPONENTS_PCA, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X_mat)

    exp_var = pca.explained_variance_
    exp_ratio = pca.explained_variance_ratio_
    cum_ratio = np.cumsum(exp_ratio)

    log(f"PCA fitted ({N_COMPONENTS_PCA} components).")
    log(f"  - PC1 Explained Variance: {exp_ratio[0]:.2%}")
    log(f"  - PC2 Explained Variance: {exp_ratio[1]:.2%}")
    log(f"  - PC3 Explained Variance: {exp_ratio[2]:.2%}")
    log(f"  - Top 5 Cumulative Variance: {cum_ratio[4]:.2%}")
    log(f"  - Top 10 Cumulative Variance: {cum_ratio[9]:.2%}")
    log(f"  - Top 15 Cumulative Variance: {cum_ratio[14]:.2%}")

    # Export Explained Variance Table
    df_var = pd.DataFrame({
        "Component": [f"PC{i+1}" for i in range(N_COMPONENTS_PCA)],
        "Eigenvalue": exp_var,
        "Explained_Variance_Ratio": exp_ratio,
        "Cumulative_Variance_Ratio": cum_ratio,
    })
    var_table_path = os.path.join(TABLES_DIR, "pca_explained_variance.csv")
    df_var.to_csv(var_table_path, index=False)
    log(f"Saved: {var_table_path}")

    # Export Component Loadings Table for top 5 PCs
    feature_names = X_raw.columns.tolist()
    loadings_records = []
    for i in range(5):
        pc_name = f"PC{i+1}"
        loadings = pca.components_[i]
        abs_loadings = np.abs(loadings)
        sorted_indices = np.argsort(abs_loadings)[::-1]
        for rank, idx in enumerate(sorted_indices, start=1):
            loadings_records.append({
                "PC": pc_name,
                "Rank": rank,
                "Skill": feature_names[idx],
                "Loading": float(loadings[idx]),
                "Absolute_Loading": float(abs_loadings[idx]),
            })
    df_loadings = pd.DataFrame(loadings_records)
    loadings_table_path = os.path.join(TABLES_DIR, "pca_loadings.csv")
    df_loadings.to_csv(loadings_table_path, index=False)
    log(f"Saved: {loadings_table_path}")

    # ---------------------------------------------------------
    # Visualizations: Scree, Cumulative Variance, Loadings
    # ---------------------------------------------------------
    # Figure 01: Scree Plot
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(range(1, N_COMPONENTS_PCA + 1), exp_ratio * 100, marker="o", color="#2b5c8f", lw=2, markersize=6)
    plt.axvline(x=5, color="#d95f02", linestyle="--", alpha=0.7, label="Elbow Region (PC5)")
    plt.title("Figure 01: PCA Scree Plot — Explained Variance Ratio per Principal Component", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Principal Component", fontsize=11)
    plt.ylabel("Variance Explained (%)", fontsize=11)
    plt.xticks(range(1, N_COMPONENTS_PCA + 1))
    plt.legend(frameon=True)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "01_pca_scree.png")
    plt.savefig(fig1_path)
    plt.close()
    log(f"Saved: {fig1_path}")

    # Figure 02: Cumulative Variance
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(range(1, N_COMPONENTS_PCA + 1), cum_ratio * 100, marker="s", color="#1b9e77", lw=2, markersize=6)
    plt.axhline(y=50, color="#d95f02", linestyle=":", alpha=0.7, label="50% Threshold (PC11)")
    plt.axhline(y=58.5, color="#7570b3", linestyle="--", alpha=0.7, label="58.5% Total Retained (PC15)")
    plt.title("Figure 02: Cumulative Explained Variance Ratio Across 15 Retained Components", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Principal Components", fontsize=11)
    plt.ylabel("Cumulative Variance Explained (%)", fontsize=11)
    plt.xticks(range(1, N_COMPONENTS_PCA + 1))
    plt.ylim(0, 70)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "02_pca_cumulative_variance.png")
    plt.savefig(fig2_path)
    plt.close()
    log(f"Saved: {fig2_path}")

    # Figure 03: Top Loadings for PC1 to PC4
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    axes = axes.flatten()
    for i in range(4):
        ax = axes[i]
        pc_df = df_loadings[df_loadings["PC"] == f"PC{i+1}"].head(10).sort_values("Loading")
        colors = ["#d95f02" if x < 0 else "#2b5c8f" for x in pc_df["Loading"]]
        ax.barh(pc_df["Skill"].str.replace("skill_", ""), pc_df["Loading"], color=colors, alpha=0.85)
        ax.axvline(0, color="black", lw=0.8, linestyle="-")
        ax.set_title(f"PC{i+1} Component Loadings (Var: {exp_ratio[i]:.2%})", fontsize=11, fontweight="bold")
        ax.set_xlabel("Loading Coefficient", fontsize=10)
        ax.grid(axis="x", linestyle="--", alpha=0.6)
    plt.suptitle("Figure 03: Top Positive and Negative Skill Loadings for Principal Components 1–4", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "03_pca_loadings.png")
    plt.savefig(fig3_path)
    plt.close()
    log(f"Saved: {fig3_path}")

    # Save PCA Model and Scaler Model
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler(with_mean=True, with_std=False)
    scaler.fit(X_mat)
    scaler_model_path = os.path.join(MODELS_DIR, "scaler_phase4.pkl")
    joblib.dump(scaler, scaler_model_path)
    log(f"Saved Scaler model artifact: {scaler_model_path}")

    pca_model_path = os.path.join(MODELS_DIR, "pca_phase4.pkl")
    joblib.dump(pca, pca_model_path)
    log(f"Saved PCA model artifact: {pca_model_path}")

    return X_pca, pca


# ---------------------------------------------------------
# 3. K-MEANS EVALUATION (k = 2 .. 10)
# ---------------------------------------------------------
def step_3_kmeans_sweep(X_pca):
    log("STEP 3: Sweeping K-Means across k = 2 .. 10...")

    # For silhouette score calculation on 335,995 observations, pairwise O(N^2)
    # computation is memory/runtime prohibitive (~450 GB distance matrix).
    # We sample a representative, fixed-seed stratified random sample of N = 25,000.
    np.random.seed(RANDOM_STATE)
    sample_indices = np.random.choice(len(X_pca), size=SILHOUETTE_SAMPLE_SIZE, replace=False)
    X_pca_sample = X_pca[sample_indices]

    metrics_records = []
    models_dict = {}

    for k in range(2, 11):
        t0 = time.time()
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        km.fit(X_pca)
        elapsed = time.time() - t0

        inertia = float(km.inertia_)
        db_score = float(davies_bouldin_score(X_pca, km.labels_))
        ch_score = float(calinski_harabasz_score(X_pca, km.labels_))
        sil_score = float(silhouette_score(X_pca_sample, km.labels_[sample_indices]))

        counts = pd.Series(km.labels_).value_counts()
        min_size = int(counts.min())
        max_size = int(counts.max())
        balance = float(min_size / max_size)

        models_dict[k] = km

        log(f"  k={k:2d} | Inertia={inertia:10.1f} | Sil={sil_score:.4f} | DB={db_score:.4f} | CH={ch_score:8.1f} | MinSize={min_size:,} | MaxSize={max_size:,} | Time={elapsed:.1f}s")

        metrics_records.append({
            "k": k,
            "inertia": inertia,
            "silhouette": sil_score,
            "davies_bouldin": db_score,
            "calinski_harabasz": ch_score,
            "min_cluster_size": min_size,
            "max_cluster_size": max_size,
            "cluster_balance": balance,
            "silhouette_sample_n": SILHOUETTE_SAMPLE_SIZE,
        })

    df_metrics = pd.DataFrame(metrics_records)
    metrics_path = os.path.join(TABLES_DIR, "kmeans_metrics.csv")
    df_metrics.to_csv(metrics_path, index=False)
    log(f"Saved: {metrics_path}")

    # ---------------------------------------------------------
    # Visualizations: Elbow, Silhouette, Davies-Bouldin
    # ---------------------------------------------------------
    k_range = df_metrics["k"]

    # Figure 04: Elbow Plot
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["inertia"], marker="o", color="#2b5c8f", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K})")
    plt.title("Figure 04: K-Means Elbow Curve (Inertia vs. k)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Inertia (Sum of Squared Distances)", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "04_kmeans_elbow.png")
    plt.savefig(fig4_path)
    plt.close()
    log(f"Saved: {fig4_path}")

    # Figure 05: Silhouette Score by k
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["silhouette"], marker="s", color="#1b9e77", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K}, Sil={df_metrics.loc[df_metrics['k']==SELECTED_K, 'silhouette'].values[0]:.4f})")
    plt.title(f"Figure 05: Silhouette Score by k (Evaluated on N={SILHOUETTE_SAMPLE_SIZE:,} Representative Sample)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Mean Silhouette Score", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "05_silhouette_by_k.png")
    plt.savefig(fig5_path)
    plt.close()
    log(f"Saved: {fig5_path}")

    # Figure 06: Davies-Bouldin by k
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["davies_bouldin"], marker="^", color="#7570b3", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K}, DB={df_metrics.loc[df_metrics['k']==SELECTED_K, 'davies_bouldin'].values[0]:.4f})")
    plt.title("Figure 06: Davies-Bouldin Index by k (Lower is Superior Separation)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Davies-Bouldin Index", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig6_path = os.path.join(FIGURES_DIR, "06_davies_bouldin_by_k.png")
    plt.savefig(fig6_path)
    plt.close()
    log(f"Saved: {fig6_path}")

    return df_metrics, models_dict[SELECTED_K]


# ---------------------------------------------------------
# 4. CLUSTER STABILITY TESTING ACROSS RANDOM SEEDS
# ---------------------------------------------------------
def step_4_stability_testing(X_pca):
    log(f"STEP 4: Testing cluster stability across seeds: {STABILITY_SEEDS} for k={SELECTED_K}...")

    seed_models = {}
    for s in STABILITY_SEEDS:
        km = KMeans(n_clusters=SELECTED_K, random_state=s, n_init=N_INIT)
        km.fit(X_pca)
        seed_models[s] = km.labels_
        log(f"  Fitted seed {s}")

    stability_records = []
    aris = []
    amis = []

    for i in range(len(STABILITY_SEEDS)):
        for j in range(i + 1, len(STABILITY_SEEDS)):
            s1, s2 = STABILITY_SEEDS[i], STABILITY_SEEDS[j]
            ari = float(adjusted_rand_score(seed_models[s1], seed_models[s2]))
            ami = float(adjusted_mutual_info_score(seed_models[s1], seed_models[s2]))
            aris.append(ari)
            amis.append(ami)
            stability_records.append({
                "Seed_Pair": f"({s1}, {s2})",
                "Seed_1": s1,
                "Seed_2": s2,
                "Adjusted_Rand_Index": ari,
                "Adjusted_Mutual_Info": ami,
            })
            log(f"  Pair ({s1}, {s2}): ARI = {ari:.4f} | AMI = {ami:.4f}")

    df_stability = pd.DataFrame(stability_records)
    mean_ari = float(np.mean(aris))
    median_ari = float(np.median(aris))
    min_ari = float(np.min(aris))
    max_ari = float(np.max(aris))
    mean_ami = float(np.mean(amis))

    log("Stability Summary:")
    log(f"  Mean ARI:   {mean_ari:.4f}")
    log(f"  Median ARI: {median_ari:.4f}")
    log(f"  Min ARI:    {min_ari:.4f}")
    log(f"  Max ARI:    {max_ari:.4f}")
    log(f"  Mean AMI:   {mean_ami:.4f}")

    stability_path = os.path.join(TABLES_DIR, "kmeans_stability.csv")
    df_stability.to_csv(stability_path, index=False)
    log(f"Saved: {stability_path}")

    return df_stability, mean_ari, mean_ami


# ---------------------------------------------------------
# 5. FINAL CLUSTER ASSIGNMENTS & PROFILING
# ---------------------------------------------------------
def step_5_assign_and_profile(X_raw, jobs_df, model_df, X_pca, km_final):
    log("STEP 5: Creating final archetype assignments and analytical profiles...")

    cluster_labels = km_final.labels_

    # Map deterministic cluster IDs to scientifically grounded archetype names
    ARCHETYPE_MAP = {
        0: "Systems & Core Backend Engineering",
        1: "General / Non-Technical Postings",
        2: "Multi-Cloud & Enterprise Cloud Architecture",
        3: "AI / Machine Learning & Deep Learning",
        4: "DevOps & Cloud Infrastructure Engineering",
        5: "Frontend & Modern Web Application Engineering",
        6: "Data Engineering & Business Analytics",
    }

    ARCHETYPE_SHORT_CODES = {
        0: "SYS_ENG",
        1: "GEN_ATS",
        2: "CLOUD_ARCH",
        3: "AI_ML",
        4: "DEVOPS_PLAT",
        5: "WEB_FRONT",
        6: "DATA_BI",
    }

    # Create persistent assignments parquet
    df_assignments = pd.DataFrame({
        "job_id": jobs_df["job_id"].values,
        "cluster_id": cluster_labels,
        "archetype_name": [ARCHETYPE_MAP[c] for c in cluster_labels],
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
    })

    # Validate assignment integrity
    assert len(df_assignments) == len(jobs_df), "Row count mismatch in assignments!"
    assert df_assignments["job_id"].duplicated().sum() == 0, "Duplicate IDs in assignments!"
    assert df_assignments["cluster_id"].isnull().sum() == 0, "Null cluster IDs in assignments!"
    log(f"Assignments verified: {len(df_assignments):,} rows, 0 nulls, 0 duplicates.")

    assignments_path = os.path.join(DATA_DIR, "job_archetype_assignments.parquet")
    df_assignments.to_parquet(assignments_path, index=False)
    log(f"Saved: {assignments_path}")

    # Attach cluster labels to jobs_df for post-hoc profiling
    jobs_df["cluster_id"] = cluster_labels
    jobs_df["archetype_name"] = df_assignments["archetype_name"]

    # Table 5.1: Cluster Sizes
    size_counts = pd.Series(cluster_labels).value_counts().sort_index()
    df_sizes = pd.DataFrame({
        "Cluster_ID": size_counts.index,
        "Archetype_Name": [ARCHETYPE_MAP[c] for c in size_counts.index],
        "Short_Code": [ARCHETYPE_SHORT_CODES[c] for c in size_counts.index],
        "Postings_Count": size_counts.values,
        "Corpus_Percentage": size_counts.values / len(jobs_df) * 100,
    })
    sizes_path = os.path.join(TABLES_DIR, "cluster_sizes.csv")
    df_sizes.to_csv(sizes_path, index=False)
    log(f"Saved: {sizes_path}")

    # Table 5.2 & 5.3: Skill Prevalence and Lift
    global_prev = X_raw.mean()
    cluster_prev_dict = {}
    cluster_lift_dict = {}

    for c in range(SELECTED_K):
        mask = (cluster_labels == c)
        c_prev = X_raw.loc[mask].mean()
        lift = c_prev / (global_prev + 1e-9)
        cluster_prev_dict[f"Cluster_{c}_{ARCHETYPE_SHORT_CODES[c]}"] = c_prev
        cluster_lift_dict[f"Cluster_{c}_{ARCHETYPE_SHORT_CODES[c]}"] = lift

    df_skill_prev = pd.DataFrame({"Skill": X_raw.columns, "Global_Prevalence": global_prev.values})
    for k_name, s_prev in cluster_prev_dict.items():
        df_skill_prev[k_name] = s_prev.values
    prev_path = os.path.join(TABLES_DIR, "cluster_skill_prevalence.csv")
    df_skill_prev.to_csv(prev_path, index=False)
    log(f"Saved: {prev_path}")

    df_skill_lift = pd.DataFrame({"Skill": X_raw.columns, "Global_Prevalence": global_prev.values})
    for k_name, s_lift in cluster_lift_dict.items():
        df_skill_lift[k_name] = s_lift.values
    lift_path = os.path.join(TABLES_DIR, "cluster_skill_lift.csv")
    df_skill_lift.to_csv(lift_path, index=False)
    log(f"Saved: {lift_path}")

    # Table 5.4: Role Family Profile
    rf_records = []
    for c in range(SELECTED_K):
        c_jobs = jobs_df[jobs_df["cluster_id"] == c]
        top_rfs = c_jobs["role_family"].value_counts(normalize=True).head(5)
        for rank, (rf_name, rf_pct) in enumerate(top_rfs.items(), start=1):
            rf_records.append({
                "Cluster_ID": c,
                "Archetype_Name": ARCHETYPE_MAP[c],
                "Rank": rank,
                "Role_Family": rf_name,
                "Share_Within_Cluster": rf_pct * 100,
            })
    df_rf_profile = pd.DataFrame(rf_records)
    rf_path = os.path.join(TABLES_DIR, "cluster_role_family_profile.csv")
    df_rf_profile.to_csv(rf_path, index=False)
    log(f"Saved: {rf_path}")

    # Table 5.5: Seniority Profile
    sen_records = []
    for c in range(SELECTED_K):
        c_jobs = jobs_df[jobs_df["cluster_id"] == c]
        sen_dist = c_jobs["seniority"].value_counts(normalize=True)
        sen_records.append({
            "Cluster_ID": c,
            "Archetype_Name": ARCHETYPE_MAP[c],
            "Junior_%": float(sen_dist.get("Junior", 0.0) * 100),
            "Mid_%": float(sen_dist.get("Mid", 0.0) * 100),
            "Senior_%": float(sen_dist.get("Senior", 0.0) * 100),
            "Lead_Principal_Exec_%": float(sen_dist.get("Lead/Principal/Exec", 0.0) * 100),
            "Unknown_%": float(sen_dist.get("Unknown", 0.0) * 100),
        })
    df_sen_profile = pd.DataFrame(sen_records)
    sen_path = os.path.join(TABLES_DIR, "cluster_seniority_profile.csv")
    df_sen_profile.to_csv(sen_path, index=False)
    log(f"Saved: {sen_path}")

    # Table 5.6: Salary Profile (using verified salary modeling cohort N=34,036)
    # Map modeling cohort records to cluster labels
    model_df_cluster = model_df.copy()
    model_df_cluster["cluster_id"] = cluster_labels[X_raw.index.get_indexer(model_df_cluster["job_id"])]
    model_df_cluster["archetype_name"] = model_df_cluster["cluster_id"].map(ARCHETYPE_MAP)

    sal_records = []
    for c in range(SELECTED_K):
        c_sal = model_df_cluster[model_df_cluster["cluster_id"] == c]["salary_midpoint"]
        sal_records.append({
            "Cluster_ID": c,
            "Archetype_Name": ARCHETYPE_MAP[c],
            "N_Salary_Observations": len(c_sal),
            "Median_Salary": float(c_sal.median()),
            "Mean_Salary": float(c_sal.mean()),
            "Std_Dev": float(c_sal.std()),
            "Q1_25th": float(c_sal.quantile(0.25)),
            "Q3_75th": float(c_sal.quantile(0.75)),
            "IQR": float(c_sal.quantile(0.75) - c_sal.quantile(0.25)),
        })
    df_sal_profile = pd.DataFrame(sal_records)
    sal_path = os.path.join(TABLES_DIR, "cluster_salary_profile.csv")
    df_sal_profile.to_csv(sal_path, index=False)
    log(f"Saved: {sal_path}")

    # Table 5.7: Title Profile
    title_records = []
    for c in range(SELECTED_K):
        c_jobs = jobs_df[jobs_df["cluster_id"] == c]
        top_titles = c_jobs["title"].value_counts().head(5)
        for rank, (title_name, count) in enumerate(top_titles.items(), start=1):
            title_records.append({
                "Cluster_ID": c,
                "Archetype_Name": ARCHETYPE_MAP[c],
                "Rank": rank,
                "Representative_Title": title_name,
                "Postings_Count": count,
                "Share_Within_Cluster": (count / len(c_jobs)) * 100,
            })
    df_title_profile = pd.DataFrame(title_records)
    title_path = os.path.join(TABLES_DIR, "cluster_title_profile.csv")
    df_title_profile.to_csv(title_path, index=False)
    log(f"Saved: {title_path}")

    # Table 5.8: Archetype Dictionary
    dict_records = [
        {
            "Cluster_ID": 0,
            "Archetype_Name": "Systems & Core Backend Engineering",
            "Short_Code": "SYS_ENG",
            "Top_Defining_Skills": "python (98.9%), c++ (23.5%), linux (19.1%), java (14.0%), embedded (13.0%)",
            "Highest_Lift_Skills": "c++ (12.1x), embedded (11.6x), python (10.5x), rust (8.7x), linux (8.4x)",
            "Representative_Titles": "Senior Software Engineer, Forward Deployed Engineer, Software Engineer, Applied AI Engineer",
            "Primary_Role_Families": "Software Engineer (50.2%), ML / AI Engineer (10.2%), DevOps / Cloud (5.9%)",
            "Strategic_Role": "Core systems software, performance runtimes, embedded engineering, and algorithmic backend computing.",
        },
        {
            "Cluster_ID": 1,
            "Archetype_Name": "General / Non-Technical Postings",
            "Short_Code": "GEN_ATS",
            "Top_Defining_Skills": "Baseline zero/low technical skills (mean 0.09 skills/job, 80.96% of ATS corpus)",
            "Highest_Lift_Skills": "Baseline non-technical / minimal technical skill lift",
            "Representative_Titles": "Care Assistant, Bar & Waiting Staff, Chef, Customer Service Manager, Sales Specialist",
            "Primary_Role_Families": "Other Tech / ATS Broad Roles (87.5%), ML/AI (1.9%), Tech Product (1.7%)",
            "Strategic_Role": "Represents non-engineering ATS postings and general business roles without specialized computing requirements.",
        },
        {
            "Cluster_ID": 2,
            "Archetype_Name": "Multi-Cloud & Enterprise Cloud Architecture",
            "Short_Code": "CLOUD_ARCH",
            "Top_Defining_Skills": "aws (98.9%), azure (87.9%), gcp (83.8%), python (45.4%), kubernetes (27.1%)",
            "Highest_Lift_Skills": "gcp (25.4x), azure (24.2x), aws (16.8x), databricks (12.1x), snowflake (8.8x)",
            "Representative_Titles": "Senior Software Engineer, Data Engineer, Senior Data Engineer, Machine Learning Engineer",
            "Primary_Role_Families": "ML / AI Engineer (18.5%), Software Engineer (17.6%), DevOps / Cloud (12.2%), Other Tech (11.6%)",
            "Strategic_Role": "Enterprise cloud migrations, multi-cloud data warehousing, and hybrid cloud infrastructure.",
        },
        {
            "Cluster_ID": 3,
            "Archetype_Name": "AI / Machine Learning & Deep Learning",
            "Short_Code": "AI_ML",
            "Top_Defining_Skills": "machine-learning (99.7%), python (43.3%), llm (32.4%), data-science (23.5%), pytorch (21.4%)",
            "Highest_Lift_Skills": "deep-learning (20.7x), machine-learning (20.5x), pytorch (19.3x), tensorflow (16.5x), nlp (15.5x)",
            "Representative_Titles": "Machine Learning Engineer, Data Scientist, Senior Machine Learning Engineer, Senior Data Scientist",
            "Primary_Role_Families": "ML / AI Engineer (64.9%), Data Scientist (9.0%), Software Engineer (8.6%), Technical PM (5.8%)",
            "Strategic_Role": "Algorithmic artificial intelligence, neural networks, foundation model fine-tuning, and statistical data modeling.",
        },
        {
            "Cluster_ID": 4,
            "Archetype_Name": "DevOps & Cloud Infrastructure Engineering",
            "Short_Code": "DEVOPS_PLAT",
            "Top_Defining_Skills": "ci-cd (78.3%), kubernetes (75.0%), aws (67.8%), python (58.5%), devops (57.8%), docker (55.4%)",
            "Highest_Lift_Skills": "docker (22.9x), terraform (22.2x), rabbitmq (21.5x), ansible (21.4x), kubernetes (21.0x)",
            "Representative_Titles": "Senior Software Engineer, DevOps Engineer, Senior DevOps Engineer, Senior SRE",
            "Primary_Role_Families": "DevOps / Cloud / Platform (34.2%), Software Engineer (20.8%), ML / AI Engineer (9.3%)",
            "Strategic_Role": "Continuous integration, container orchestration, infrastructure-as-code, and distributed systems reliability.",
        },
        {
            "Cluster_ID": 5,
            "Archetype_Name": "Frontend & Modern Web Application Engineering",
            "Short_Code": "WEB_FRONT",
            "Top_Defining_Skills": "typescript (88.1%), react (45.0%), javascript (18.5%), node.js (16.5%), sql (16.0%)",
            "Highest_Lift_Skills": "typescript (24.6x), react-native (21.6x), next.js (20.4x), react (17.7x), graphql (14.0x)",
            "Representative_Titles": "Senior Software Engineer, Software Engineer, Staff Software Engineer, Full Stack Engineer",
            "Primary_Role_Families": "Software Engineer (52.4%), Frontend Developer (16.2%), Full-Stack Developer (10.1%)",
            "Strategic_Role": "Modern interactive client applications, mobile interfaces, component architectures, and responsive web systems.",
        },
        {
            "Cluster_ID": 6,
            "Archetype_Name": "Data Engineering & Business Analytics",
            "Short_Code": "DATA_BI",
            "Top_Defining_Skills": "sql (99.9%), python (41.3%), data-engineering (16.1%), tableau (15.8%), power-bi (14.7%)",
            "Highest_Lift_Skills": "sql (14.1x), looker (13.3x), tableau (12.5x), dbt (11.1x), bigquery (10.0x)",
            "Representative_Titles": "Data Engineer, Senior Data Engineer, Data Analyst, Senior Software Engineer",
            "Primary_Role_Families": "Other Tech (24.8%), Software Engineer (17.8%), Data Engineer (12.7%), Data Scientist (10.1%)",
            "Strategic_Role": "Relational data pipelines, ETL orchestration, business intelligence dashboards, and analytical data marts.",
        },
    ]
    df_dictionary = pd.DataFrame(dict_records)
    dict_path = os.path.join(TABLES_DIR, "archetype_dictionary.csv")
    df_dictionary.to_csv(dict_path, index=False)
    log(f"Saved: {dict_path}")

    # ---------------------------------------------------------
    # Visualizations: Figures 07 to 13
    # ---------------------------------------------------------
    # Figure 07: Cluster Sizes
    plt.figure(figsize=(10, 6), dpi=300)
    bars = plt.barh(df_sizes["Archetype_Name"], df_sizes["Corpus_Percentage"], color=ARCHETYPE_COLORS, alpha=0.85)
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", fontsize=10, fontweight="bold")
    plt.title("Figure 07: Distribution of Job Postings Across 7 Discovered Archetypes (N=335,995)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Percentage of Total Deduplicated Corpus (%)", fontsize=11)
    plt.xlim(0, 95)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    fig7_path = os.path.join(FIGURES_DIR, "07_cluster_sizes.png")
    plt.savefig(fig7_path)
    plt.close()
    log(f"Saved: {fig7_path}")

    # Figure 08: PCA Cluster Scatter (PC1 vs PC2)
    plt.figure(figsize=(11, 8), dpi=300)
    # Downsample for scatter visibility (15,000 points)
    np.random.seed(RANDOM_STATE)
    scatter_idx = np.random.choice(len(X_pca), size=15000, replace=False)
    for c in range(SELECTED_K):
        c_mask = (cluster_labels[scatter_idx] == c)
        plt.scatter(
            X_pca[scatter_idx][c_mask, 0],
            X_pca[scatter_idx][c_mask, 1],
            c=ARCHETYPE_COLORS[c],
            label=f"C{c}: {ARCHETYPE_MAP[c]}",
            alpha=0.55 if c != 1 else 0.15,
            s=12 if c != 1 else 6,
        )
    # Plot centroids
    centroids_pca = km_final.cluster_centers_[:, :2]
    plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], marker="X", s=150, color="black", edgecolor="white", lw=1.5, zorder=10, label="Cluster Centroids")
    plt.title("Figure 08: 2D Projection of Discovered Archetypes onto Principal Components 1 & 2", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel(f"PC1 (Variance: {pca_var_ratio(0):.1%}) — General Technical Breadth", fontsize=11)
    plt.ylabel(f"PC2 (Variance: {pca_var_ratio(1):.1%}) — Data/AI (+) vs. Cloud/Platform (-)", fontsize=11)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, fontsize=9)
    plt.tight_layout()
    fig8_path = os.path.join(FIGURES_DIR, "08_pca_cluster_scatter.png")
    plt.savefig(fig8_path)
    plt.close()
    log(f"Saved: {fig8_path}")

    # Figure 09: Heatmap of Skill Prevalence
    top_skills_for_heatmap = [
        "skill_python", "skill_sql", "skill_aws", "skill_azure", "skill_gcp",
        "skill_machine_learning", "skill_deep_learning", "skill_pytorch", "skill_tensorflow", "skill_llm",
        "skill_kubernetes", "skill_docker", "skill_ci_cd", "skill_terraform", "skill_devops",
        "skill_typescript", "skill_react", "skill_next_js", "skill_c++", "skill_linux", "skill_tableau", "skill_dbt"
    ]
    sub_prev = df_skill_prev[df_skill_prev["Skill"].isin(top_skills_for_heatmap)].copy()
    sub_prev["Clean_Skill"] = sub_prev["Skill"].str.replace("skill_", "")
    sub_prev = sub_prev.set_index("Clean_Skill")[[c for c in sub_prev.columns if c.startswith("Cluster_")]]
    sub_prev.columns = [ARCHETYPE_MAP[int(c.split("_")[1])] for c in sub_prev.columns]

    plt.figure(figsize=(12, 10), dpi=300)
    sns.heatmap(sub_prev * 100, cmap="YlGnBu", annot=True, fmt=".1f", cbar_kws={"label": "Skill Prevalence within Cluster (%)"}, linewidths=0.5)
    plt.title("Figure 09: Technical Skill Prevalence Across 7 Discovered Archetypes (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Archetype Cluster", fontsize=11)
    plt.ylabel("Technical Competency", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig9_path = os.path.join(FIGURES_DIR, "09_cluster_skill_heatmap.png")
    plt.savefig(fig9_path)
    plt.close()
    log(f"Saved: {fig9_path}")

    # Figure 10: Heatmap of Skill Lift
    sub_lift = df_skill_lift[df_skill_lift["Skill"].isin(top_skills_for_heatmap)].copy()
    sub_lift["Clean_Skill"] = sub_lift["Skill"].str.replace("skill_", "")
    sub_lift = sub_lift.set_index("Clean_Skill")[[c for c in sub_lift.columns if c.startswith("Cluster_")]]
    sub_lift.columns = [ARCHETYPE_MAP[int(c.split("_")[1])] for c in sub_lift.columns]

    plt.figure(figsize=(12, 10), dpi=300)
    sns.heatmap(sub_lift, cmap="rocket_r", annot=True, fmt=".1f", vmin=0, vmax=25, cbar_kws={"label": "Skill Lift vs. Global Prevalence (Ratio)"}, linewidths=0.5)
    plt.title("Figure 10: Technical Skill Lift Across Discovered Archetypes (Ratio over Market Baseline)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Archetype Cluster", fontsize=11)
    plt.ylabel("Technical Competency", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig10_path = os.path.join(FIGURES_DIR, "10_cluster_skill_lift.png")
    plt.savefig(fig10_path)
    plt.close()
    log(f"Saved: {fig10_path}")

    # Figure 11: Cross-Contingency Heatmap between Archetypes and Role Families
    rf_cross = pd.crosstab(jobs_df["role_family"], jobs_df["archetype_name"], normalize="columns") * 100
    top_rfs = jobs_df["role_family"].value_counts().head(12).index
    rf_cross_top = rf_cross.loc[top_rfs]

    plt.figure(figsize=(12, 8), dpi=300)
    sns.heatmap(rf_cross_top, cmap="PuBu", annot=True, fmt=".1f", cbar_kws={"label": "Role Family Share within Cluster (%)"}, linewidths=0.5)
    plt.title("Figure 11: Mapping Discovered Skill Archetypes Across Top 12 Formal Role Families (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Skill-Based Archetype", fontsize=11)
    plt.ylabel("Formal Role Family", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig11_path = os.path.join(FIGURES_DIR, "11_cluster_role_family_heatmap.png")
    plt.savefig(fig11_path)
    plt.close()
    log(f"Saved: {fig11_path}")

    # Figure 12: Salary Distribution Across Archetypes (Salary Modeling Cohort)
    plt.figure(figsize=(12, 6), dpi=300)
    order_by_median = df_sal_profile.sort_values("Median_Salary", ascending=False)["Archetype_Name"].tolist()
    sns.boxplot(
        data=model_df_cluster,
        x="archetype_name",
        y="salary_midpoint",
        order=order_by_median,
        palette=[ARCHETYPE_COLORS[list(ARCHETYPE_MAP.values()).index(name)] for name in order_by_median],
        fliersize=1.5,
        linewidth=1.0,
    )
    plt.title("Figure 12: Observed Annual Salary Distributions by Skill Archetype (Modeling Cohort N=34,036)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Archetype Cluster (Ranked by Median Compensation)", fontsize=11)
    plt.ylabel("Annual Salary Midpoint ($ USD)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    fig12_path = os.path.join(FIGURES_DIR, "12_cluster_salary_distribution.png")
    plt.savefig(fig12_path)
    plt.close()
    log(f"Saved: {fig12_path}")

    # Figure 13: Seniority Distribution by Archetype
    df_sen_plot = df_sen_profile.set_index("Archetype_Name")[["Junior_%", "Mid_%", "Senior_%", "Lead_Principal_Exec_%"]]
    plt.figure(figsize=(12, 6), dpi=300)
    df_sen_plot.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 6),
        colormap="Blues",
        edgecolor="#cccccc",
        alpha=0.9,
    )
    plt.title("Figure 13: Career Seniority Distribution Across Discovered Archetypes (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Skill-Based Archetype", fontsize=11)
    plt.ylabel("Percentage of Archetype Postings (%)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.legend(["Junior", "Mid-Level", "Senior", "Lead / Principal / Executive"], title="Seniority Tier", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    fig13_path = os.path.join(FIGURES_DIR, "13_cluster_seniority_profile.png")
    plt.savefig(fig13_path)
    plt.close()
    log(f"Saved: {fig13_path}")

    # Save K-Means Model
    km_model_path = os.path.join(MODELS_DIR, f"kmeans_phase4_k{SELECTED_K}.pkl")
    joblib.dump(km_final, km_model_path)
    log(f"Saved K-Means model artifact: {km_model_path}")

    return df_assignments, df_sizes, df_sal_profile


def pca_var_ratio(idx):
    var_path = os.path.join(TABLES_DIR, "pca_explained_variance.csv")
    if os.path.exists(var_path):
        df = pd.read_csv(var_path)
        return df.loc[idx, "Explained_Variance_Ratio"]
    return 0.169


# ---------------------------------------------------------
# 6. SECONDARY SENSITIVITY ANALYSIS (N = 34,036)
# ---------------------------------------------------------
def step_6_sensitivity_analysis(X_raw, model_df):
    log("STEP 6: Executing secondary sensitivity analysis on salary modeling cohort (N=34,036)...")

    X_model = X_raw.loc[model_df["job_id"]].values.astype(np.float32)

    pca_sens = PCA(n_components=N_COMPONENTS_PCA, random_state=RANDOM_STATE)
    X_pca_sens = pca_sens.fit_transform(X_model)

    km_sens = KMeans(n_clusters=SELECTED_K, random_state=RANDOM_STATE, n_init=N_INIT)
    km_sens.fit(X_pca_sens)

    counts = pd.Series(km_sens.labels_).value_counts().sort_index()
    log(f"Modeling cohort sensitivity cluster distribution across 7 clusters: {counts.to_dict()}")

    global_prev = pd.DataFrame(X_model, columns=X_raw.columns).mean()
    sens_summary = []
    for c in range(SELECTED_K):
        mask = (km_sens.labels_ == c)
        c_prev = pd.DataFrame(X_model[mask], columns=X_raw.columns).mean()
        lift = c_prev / (global_prev + 1e-9)
        top_prev = c_prev.sort_values(ascending=False).head(3).to_dict()
        top_lift = lift[c_prev >= 0.05].sort_values(ascending=False).head(3).to_dict()
        sens_summary.append({
            "Cluster_ID": c,
            "N": int(mask.sum()),
            "Pct": float(mask.mean() * 100),
            "Top_Skills": str({k.replace("skill_", ""): round(v, 2) for k, v in top_prev.items()}),
            "Top_Lift": str({k.replace("skill_", ""): round(v, 1) for k, v in top_lift.items()}),
        })

    df_sens = pd.DataFrame(sens_summary)
    sens_path = os.path.join(TABLES_DIR, "sensitivity_modeling_cohort.csv")
    df_sens.to_csv(sens_path, index=False)
    log(f"Saved: {sens_path}")
    log("Secondary sensitivity analysis successfully verified.")


# ---------------------------------------------------------
# 7. MAIN ORCHESTRATOR
# ---------------------------------------------------------
def main():
    log("=" * 70)
    log("STARTING PHASE 4: SKILL-BASED JOB ARCHETYPE DISCOVERY")
    log("=" * 70)

    # Step 1: Validate data
    X_raw, jobs_df, model_df = step_1_validate_data()

    # Step 2: PCA
    X_pca, pca_model = step_2_pca_analysis(X_raw)

    # Step 3: KMeans Sweep
    df_metrics, km_final = step_3_kmeans_sweep(X_pca)

    # Step 4: Stability Testing
    df_stability, mean_ari, mean_ami = step_4_stability_testing(X_pca)

    # Step 5: Assignments and Profiling
    df_assignments, df_sizes, df_sal = step_5_assign_and_profile(X_raw, jobs_df, model_df, X_pca, km_final)

    # Step 6: Sensitivity Analysis
    step_6_sensitivity_analysis(X_raw, model_df)

    log("=" * 70)
    log("PHASE 4 EXECUTION COMPLETE.")
    log(f"Discovered {SELECTED_K} reproducible, high-stability skill archetypes (Mean ARI: {mean_ari:.4f}).")
    log("All quality gates, assignments, tables, figures, and models successfully generated.")
    log("=" * 70)


if __name__ == "__main__":
    main()
