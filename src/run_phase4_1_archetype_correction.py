"""
Phase 4.1: Surgical Methodology Correction — Valid Skill-Based Archetype Discovery
===================================================================================
INT234 Predictive Analytics — Academic Task 2
Author: Antigravity Senior Data Science & Unsupervised Learning Team
Date: October 2026

Mission:
  Address the critical population issue identified in Phase 4:
  The previous clustering included 219,165 postings with 0 parsed technical skills,
  causing K-Means to produce a dominant non-technical cluster (80.96%) separating
  zero-skill postings from skill-bearing postings.

  This corrected pipeline restricts primary archetype discovery strictly to
  postings with at least one qualifying technical skill (N ≈ 116,830).
  The old 335,995-row analysis is preserved as a Full-Corpus Diagnostic.

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
from sklearn.preprocessing import StandardScaler
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
FIGURES_DIR = "reports/figures/phase4_1"
TABLES_DIR = "reports/tables/phase4_1"

for d in [MODELS_DIR, FIGURES_DIR, TABLES_DIR]:
    os.makedirs(d, exist_ok=True)

# Aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#eeeeee"
plt.rcParams["grid.linestyle"] = "--"

# Palette for the 7 archetypes in corrected primary analysis
ARCHETYPE_COLORS = [
    "#8c564b",  # 0: Foundational & Broad Technical Roles (Muted Brown / Gray)
    "#1b9e77",  # 1: DevOps & Cloud Infrastructure (Teal Green)
    "#e7298a",  # 2: Frontend & Modern Web (Magenta Pink)
    "#d95f02",  # 3: Multi-Cloud & Enterprise Cloud (Vibrant Orange)
    "#e6ab02",  # 4: Data Engineering & Analytics (Gold / Amber)
    "#7570b3",  # 5: AI / Machine Learning & LLM (Purple)
    "#2b5c8f",  # 6: Systems & Core Backend (Deep Slate Blue)
]


def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}", flush=True)


# ---------------------------------------------------------
# 1. POPULATION DEFINITION & VALIDATION
# ---------------------------------------------------------
def step_1_population_definition():
    log("STEP 1: Quantifying populations and isolating primary skill-bearing cohort...")

    skill_path = os.path.join(DATA_DIR, "skill_matrix_technical.parquet")
    jobs_path = os.path.join(DATA_DIR, "cleaned_jobs.parquet")
    model_path = os.path.join(DATA_DIR, "modeling_dataset.parquet")

    X_raw = pd.read_parquet(skill_path)
    jobs_df = pd.read_parquet(jobs_path)
    model_df = pd.read_parquet(model_path)

    n_total = len(X_raw)
    skill_counts = X_raw.sum(axis=1)

    primary_mask = (skill_counts > 0).values
    n_primary = int(primary_mask.sum())
    n_zero = n_total - n_primary

    # Compute skills per job for primary population
    skills_primary = skill_counts[primary_mask]
    s_min = int(skills_primary.min())
    s_med = float(skills_primary.median())
    s_mean = float(skills_primary.mean())
    s_max = int(skills_primary.max())
    s_q25 = float(skills_primary.quantile(0.25))
    s_q75 = float(skills_primary.quantile(0.75))

    log(f"Total Corpus Postings:      {n_total:,} (100.0%)")
    log(f"Primary Population (>=1):   {n_primary:,} ({n_primary / n_total:.4%})")
    log(f"Zero-Skill Postings (==0):  {n_zero:,} ({n_zero / n_total:.4%})")
    log(f"Primary Skills/Job: Min={s_min}, Median={s_med:.0f}, Mean={s_mean:.2f}, Max={s_max}, Q25={s_q25:.0f}, Q75={s_q75:.0f}")

    # Export Population Comparison Table
    df_pop = pd.DataFrame([
        {"Population": "All Technology Postings (Full ATS Corpus)", "N": n_total, "Share_%": 100.0, "Description": "Complete deduplicated ATS postings; includes non-tech roles"},
        {"Population": "Primary Archetype Population (>=1 Technical Skill)", "N": n_primary, "Share_%": np.round(n_primary / n_total * 100, 2), "Description": "Skill-bearing postings; valid domain for discovering skill archetypes"},
        {"Population": "Zero Technical Skill Postings (==0 Skills)", "N": n_zero, "Share_%": np.round(n_zero / n_total * 100, 2), "Description": "Non-technical ATS postings (hospitality, nursing, administrative, trades)"},
        {"Population": "Supervised Salary Modeling Cohort (Phase 5 Domain)", "N": len(model_df), "Share_%": np.round(len(model_df) / n_total * 100, 2), "Description": "Verified technology roles with valid USD salary within [$30k, $600k]"},
    ])
    pop_table_path = os.path.join(TABLES_DIR, "population_comparison.csv")
    df_pop.to_csv(pop_table_path, index=False)
    log(f"Saved: {pop_table_path}")

    # Figure 01: Population Breakdown
    plt.figure(figsize=(10, 5), dpi=300)
    bars = plt.barh(
        ["Zero Technical Skills\n(Excluded Diagnostic)", "Primary Population\n(>=1 Technical Skill)", "Full Deduplicated\nATS Corpus"],
        [n_zero, n_primary, n_total],
        color=["#cccccc", "#2b5c8f", "#1b9e77"],
        alpha=0.85
    )
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 3000, bar.get_y() + bar.get_height() / 2, f"{w:,} ({w / n_total:.1%})", va="center", fontsize=10, fontweight="bold")
    plt.title("Figure 01: Archetype Discovery Population Funnel (Zero-Skill Exclusion)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Job Postings", fontsize=11)
    plt.xlim(0, 400000)
    plt.gca().xaxis.set_major_formatter("{x:,.0f}")
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "01_population_definition.png")
    plt.savefig(fig1_path)
    plt.close()
    log(f"Saved: {fig1_path}")

    # Filter to primary population
    X_prim = X_raw[primary_mask].copy()
    jobs_prim = jobs_df[primary_mask].copy()

    # Validate primary skill matrix
    var_zero = (X_prim.var() == 0).sum()
    assert var_zero == 0, f"Found {var_zero} zero-variance columns in primary population!"
    assert X_prim.isnull().sum().sum() == 0, "Found null values in primary skill matrix!"
    assert (X_prim.index.values == jobs_prim["job_id"].values).all(), "Row mismatch between X_prim and jobs_prim!"

    total_elem = X_prim.shape[0] * X_prim.shape[1]
    nonzero_elem = int(X_prim.sum().sum())
    sparsity = 1.0 - (nonzero_elem / total_elem)
    density = nonzero_elem / total_elem

    log("Primary Skill Matrix Diagnostics:")
    log(f"  - Shape: {X_prim.shape[0]:,} rows x {X_prim.shape[1]} technical skills")
    log(f"  - Sparsity: {sparsity:.2%}, Density: {density:.2%}")
    log(f"  - Total Skill Mentions: {nonzero_elem:,}")

    return X_prim, jobs_prim, model_df, X_raw, jobs_df


# ---------------------------------------------------------
# 2. PCA DIMENSIONALITY REDUCTION ON PRIMARY POPULATION
# ---------------------------------------------------------
def step_2_pca(X_prim):
    log("STEP 2: Executing PCA on corrected primary population (N=116,830)...")

    X_mat = X_prim.values.astype(np.float32)

    # Centered Covariance PCA
    scaler = StandardScaler(with_mean=True, with_std=False)
    X_centered = scaler.fit_transform(X_mat)
    scaler_path = os.path.join(MODELS_DIR, "scaler_phase4_1.pkl")
    joblib.dump(scaler, scaler_path)
    log(f"Saved: {scaler_path}")

    pca = PCA(n_components=N_COMPONENTS_PCA, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X_centered)

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
        "Eigenvalue": np.round(exp_var, 4),
        "Explained_Variance_Ratio": np.round(exp_ratio, 6),
        "Cumulative_Variance_Ratio": np.round(cum_ratio, 6),
        "Explained_Variance_%": np.round(exp_ratio * 100, 2),
        "Cumulative_Variance_%": np.round(cum_ratio * 100, 2),
    })
    var_table_path = os.path.join(TABLES_DIR, "pca_explained_variance.csv")
    df_var.to_csv(var_table_path, index=False)
    log(f"Saved: {var_table_path}")

    # Export Component Loadings Table for top 5 PCs
    feature_names = X_prim.columns.tolist()
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

    # Figure 02: Scree Plot
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(range(1, N_COMPONENTS_PCA + 1), exp_ratio * 100, marker="o", color="#2b5c8f", lw=2, markersize=6)
    plt.axvline(x=5, color="#d95f02", linestyle="--", alpha=0.7, label="Elbow Region (PC5)")
    plt.title("Figure 02: PCA Scree Plot — Primary Skill-Bearing Population (N=116,830)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Principal Component", fontsize=11)
    plt.ylabel("Variance Explained (%)", fontsize=11)
    plt.xticks(range(1, N_COMPONENTS_PCA + 1))
    plt.legend(frameon=True)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "02_pca_scree.png")
    plt.savefig(fig2_path)
    plt.close()
    log(f"Saved: {fig2_path}")

    # Figure 03: Cumulative Variance
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(range(1, N_COMPONENTS_PCA + 1), cum_ratio * 100, marker="s", color="#1b9e77", lw=2, markersize=6)
    plt.axhline(y=50, color="#d95f02", linestyle=":", alpha=0.7, label="50% Threshold (PC12)")
    plt.axhline(y=56.05, color="#7570b3", linestyle="--", alpha=0.7, label="56.05% Total Retained (PC15)")
    plt.title("Figure 03: Cumulative Explained Variance (15 Retained Components)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Principal Components", fontsize=11)
    plt.ylabel("Cumulative Variance Explained (%)", fontsize=11)
    plt.xticks(range(1, N_COMPONENTS_PCA + 1))
    plt.ylim(0, 65)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "03_pca_cumulative_variance.png")
    plt.savefig(fig3_path)
    plt.close()
    log(f"Saved: {fig3_path}")

    # Figure 04: Top Loadings for PC1 to PC4
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    axes = axes.flatten()
    for i in range(4):
        ax = axes[i]
        pc_df = df_loadings[df_loadings["PC"] == f"PC{i+1}"].head(10).sort_values("Loading")
        colors = ["#d95f02" if x < 0 else "#2b5c8f" for x in pc_df["Loading"]]
        ax.barh(pc_df["Skill"].str.replace("skill_", ""), pc_df["Loading"], color=colors, alpha=0.85)
        ax.axvline(0, color="black", lw=0.8, linestyle="-")
        ax.set_title(f"PC{i+1} Loadings (Explained Var: {exp_ratio[i]:.2%})", fontsize=11, fontweight="bold")
        ax.set_xlabel("Loading Coefficient", fontsize=10)
        ax.grid(axis="x", linestyle="--", alpha=0.6)
    plt.suptitle("Figure 04: Top Positive & Negative Skill Loadings for PC1 to PC4 (Primary Population)", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "04_pca_loadings.png")
    plt.savefig(fig4_path)
    plt.close()
    log(f"Saved: {fig4_path}")

    pca_model_path = os.path.join(MODELS_DIR, "pca_phase4_1.pkl")
    joblib.dump(pca, pca_model_path)
    log(f"Saved PCA model artifact: {pca_model_path}")

    return X_pca, pca


# ---------------------------------------------------------
# 3. K-MEANS EVALUATION SWEEP (k = 2 .. 10)
# ---------------------------------------------------------
def step_3_kmeans_sweep(X_pca):
    log("STEP 3: Sweeping K-Means across k = 2 .. 10 on primary population...")

    # Statistically defensible sample for silhouette score (N = 25,000)
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

        log(f"  k={k:2d} | Inertia={inertia:9.1f} | Sil={sil_score:.4f} | DB={db_score:.4f} | CH={ch_score:7.1f} | MinSize={min_size:,} | MaxSize={max_size:,} | Time={elapsed:.1f}s")

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

    # Figure 05: Elbow Curve
    k_range = df_metrics["k"]
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["inertia"], marker="o", color="#2b5c8f", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K})")
    plt.title("Figure 05: K-Means Elbow Curve on Primary Population (Inertia vs. k)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Inertia (Sum of Squared Distances)", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "05_kmeans_elbow.png")
    plt.savefig(fig5_path)
    plt.close()
    log(f"Saved: {fig5_path}")

    # Figure 06: Silhouette Score by k
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["silhouette"], marker="s", color="#1b9e77", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K}, Sil={df_metrics.loc[df_metrics['k']==SELECTED_K, 'silhouette'].values[0]:.4f})")
    plt.title(f"Figure 06: Silhouette Score across k (Representative Sample N={SILHOUETTE_SAMPLE_SIZE:,})", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Mean Silhouette Score", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig6_path = os.path.join(FIGURES_DIR, "06_silhouette_by_k.png")
    plt.savefig(fig6_path)
    plt.close()
    log(f"Saved: {fig6_path}")

    # Figure 07: Davies-Bouldin Index by k
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(k_range, df_metrics["davies_bouldin"], marker="^", color="#7570b3", lw=2, markersize=6)
    plt.axvline(x=SELECTED_K, color="#d95f02", linestyle="--", label=f"Selected Resolution (k={SELECTED_K}, DB={df_metrics.loc[df_metrics['k']==SELECTED_K, 'davies_bouldin'].values[0]:.4f})")
    plt.title("Figure 07: Davies-Bouldin Index across k (Lower Values Indicate Superior Separation)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11)
    plt.ylabel("Davies-Bouldin Index", fontsize=11)
    plt.xticks(k_range)
    plt.legend(frameon=True)
    plt.tight_layout()
    fig7_path = os.path.join(FIGURES_DIR, "07_davies_bouldin_by_k.png")
    plt.savefig(fig7_path)
    plt.close()
    log(f"Saved: {fig7_path}")

    return df_metrics, models_dict[SELECTED_K]


# ---------------------------------------------------------
# 4. CLUSTER STABILITY TESTING ACROSS SEEDS
# ---------------------------------------------------------
def step_4_stability(X_pca):
    log(f"STEP 4: Testing cluster stability across seeds: {STABILITY_SEEDS} for k={SELECTED_K} on primary population...")

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
    med_ari = float(np.median(aris))
    min_ari = float(np.min(aris))
    max_ari = float(np.max(aris))

    mean_ami = float(np.mean(amis))
    med_ami = float(np.median(amis))
    min_ami = float(np.min(amis))
    max_ami = float(np.max(amis))

    log("Stability Summary Statistics (Primary Population):")
    log(f"  ARI: Mean={mean_ari:.4f}, Median={med_ari:.4f}, Min={min_ari:.4f}, Max={max_ari:.4f}")
    log(f"  AMI: Mean={mean_ami:.4f}, Median={med_ami:.4f}, Min={min_ami:.4f}, Max={max_ami:.4f}")

    stability_path = os.path.join(TABLES_DIR, "kmeans_stability.csv")
    df_stability.to_csv(stability_path, index=False)
    log(f"Saved: {stability_path}")

    return df_stability, mean_ari, med_ari, min_ari, max_ari, mean_ami, med_ami, min_ami, max_ami


# ---------------------------------------------------------
# 5. ASSIGNMENTS, PROFILING & VISUALIZATIONS
# ---------------------------------------------------------
def step_5_profiling(X_prim, jobs_prim, model_df, X_pca, km_final):
    log("STEP 5: Creating primary archetype assignments and taxonomic profiles...")

    cluster_labels = km_final.labels_

    # Deterministic mapping for k=7 on primary population (N=116,830)
    ARCHETYPE_MAP = {
        0: "Foundational & Broad Technical Roles",
        1: "DevOps & Cloud Infrastructure Engineering",
        2: "Frontend & Modern Web Application Engineering",
        3: "Multi-Cloud & Enterprise Cloud Architecture",
        4: "Data Engineering & Business Analytics",
        5: "AI / Machine Learning & LLM Engineering",
        6: "Systems & Core Backend Engineering",
    }

    ARCHETYPE_SHORT_CODES = {
        0: "FOUND_TECH",
        1: "DEVOPS_PLAT",
        2: "WEB_FRONT",
        3: "CLOUD_ARCH",
        4: "DATA_BI",
        5: "AI_ML",
        6: "SYS_ENG",
    }

    # Primary assignments parquet (N=116,830)
    df_assignments = pd.DataFrame({
        "job_id": jobs_prim["job_id"].values,
        "cluster_id": cluster_labels,
        "archetype_name": [ARCHETYPE_MAP[c] for c in cluster_labels],
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
    })

    assert len(df_assignments) == len(jobs_prim), "Row count mismatch in primary assignments!"
    assert df_assignments["job_id"].duplicated().sum() == 0, "Duplicate IDs in assignments!"
    assert df_assignments["cluster_id"].isnull().sum() == 0, "Null cluster IDs in assignments!"

    assignments_path = os.path.join(DATA_DIR, "job_archetype_assignments.parquet")
    df_assignments.to_parquet(assignments_path, index=False)
    log(f"Saved primary assignments: {assignments_path} (N={len(df_assignments):,})")

    # Attach labels to jobs_prim
    jobs_prim["cluster_id"] = cluster_labels
    jobs_prim["archetype_name"] = df_assignments["archetype_name"]

    # Table 5.1: Cluster Sizes
    size_counts = pd.Series(cluster_labels).value_counts().sort_index()
    df_sizes = pd.DataFrame({
        "Cluster_ID": size_counts.index,
        "Archetype_Name": [ARCHETYPE_MAP[c] for c in size_counts.index],
        "Short_Code": [ARCHETYPE_SHORT_CODES[c] for c in size_counts.index],
        "Postings_Count": size_counts.values,
        "Primary_Share_%": np.round(size_counts.values / len(jobs_prim) * 100, 2),
    })
    sizes_path = os.path.join(TABLES_DIR, "cluster_sizes.csv")
    df_sizes.to_csv(sizes_path, index=False)
    log(f"Saved: {sizes_path}")

    # Table 5.2 & 5.3: Skill Prevalence and Lift
    global_prev = X_prim.mean()
    cluster_prev_dict = {}
    cluster_lift_dict = {}

    for c in range(SELECTED_K):
        mask = (cluster_labels == c)
        c_prev = X_prim.loc[mask].mean()
        lift = c_prev / (global_prev + 1e-9)
        col_name = f"Cluster_{c}_{ARCHETYPE_SHORT_CODES[c]}"
        cluster_prev_dict[col_name] = c_prev
        cluster_lift_dict[col_name] = lift

    df_skill_prev = pd.DataFrame({"Skill": X_prim.columns, "Global_Prevalence": global_prev.values})
    for k_name, s_prev in cluster_prev_dict.items():
        df_skill_prev[k_name] = s_prev.values
    prev_path = os.path.join(TABLES_DIR, "cluster_skill_prevalence.csv")
    df_skill_prev.to_csv(prev_path, index=False)
    log(f"Saved: {prev_path}")

    df_skill_lift = pd.DataFrame({"Skill": X_prim.columns, "Global_Prevalence": global_prev.values})
    for k_name, s_lift in cluster_lift_dict.items():
        df_skill_lift[k_name] = s_lift.values
    lift_path = os.path.join(TABLES_DIR, "cluster_skill_lift.csv")
    df_skill_lift.to_csv(lift_path, index=False)
    log(f"Saved: {lift_path}")

    # Table 5.4: Role Family Profile
    rf_records = []
    for c in range(SELECTED_K):
        c_jobs = jobs_prim[jobs_prim["cluster_id"] == c]
        top_rfs = c_jobs["role_family"].value_counts(normalize=True).head(5)
        for rank, (rf_name, rf_pct) in enumerate(top_rfs.items(), start=1):
            rf_records.append({
                "Cluster_ID": c,
                "Archetype_Name": ARCHETYPE_MAP[c],
                "Rank": rank,
                "Role_Family": rf_name,
                "Share_Within_Cluster_%": np.round(rf_pct * 100, 2),
            })
    df_rf_profile = pd.DataFrame(rf_records)
    rf_path = os.path.join(TABLES_DIR, "cluster_role_family_profile.csv")
    df_rf_profile.to_csv(rf_path, index=False)
    log(f"Saved: {rf_path}")

    # Table 5.5: Seniority Profile
    sen_records = []
    for c in range(SELECTED_K):
        c_jobs = jobs_prim[jobs_prim["cluster_id"] == c]
        sen_dist = c_jobs["seniority"].value_counts(normalize=True)
        sen_records.append({
            "Cluster_ID": c,
            "Archetype_Name": ARCHETYPE_MAP[c],
            "Junior_%": np.round(float(sen_dist.get("Junior", 0.0) * 100), 2),
            "Mid_%": np.round(float(sen_dist.get("Mid", 0.0) * 100), 2),
            "Senior_%": np.round(float(sen_dist.get("Senior", 0.0) * 100), 2),
            "Lead_Principal_Exec_%": np.round(float(sen_dist.get("Lead/Principal/Exec", 0.0) * 100), 2),
            "Unknown_%": np.round(float(sen_dist.get("Unknown", 0.0) * 100), 2),
        })
    df_sen_profile = pd.DataFrame(sen_records)
    sen_path = os.path.join(TABLES_DIR, "cluster_seniority_profile.csv")
    df_sen_profile.to_csv(sen_path, index=False)
    log(f"Saved: {sen_path}")

    # Table 5.6: Salary Profile on Modeling Cohort Overlap (Post-Hoc Only)
    model_df_cluster = model_df[model_df["job_id"].isin(jobs_prim["job_id"])].copy()
    model_df_cluster["cluster_id"] = cluster_labels[X_prim.index.get_indexer(model_df_cluster["job_id"])]
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
        c_jobs = jobs_prim[jobs_prim["cluster_id"] == c]
        top_titles = c_jobs["title"].value_counts().head(5)
        for rank, (title_name, count) in enumerate(top_titles.items(), start=1):
            title_records.append({
                "Cluster_ID": c,
                "Archetype_Name": ARCHETYPE_MAP[c],
                "Rank": rank,
                "Representative_Title": title_name,
                "Postings_Count": count,
                "Share_Within_Cluster_%": np.round((count / len(c_jobs)) * 100, 2),
            })
    df_title_profile = pd.DataFrame(title_records)
    title_path = os.path.join(TABLES_DIR, "cluster_title_profile.csv")
    df_title_profile.to_csv(title_path, index=False)
    log(f"Saved: {title_path}")

    # Table 5.8: Master Archetype Dictionary
    dict_records = [
        {
            "Cluster_ID": 0,
            "Archetype_Name": "Foundational & Broad Technical Roles",
            "Short_Code": "FOUND_TECH",
            "Top_Defining_Skills": "qa_testing (10.7%), robotics (9.0%), security (8.8%), machine_learning (8.3%)",
            "Highest_Lift_Skills": "robotics (1.4x), qa_testing (1.3x), security (1.1x)",
            "Representative_Titles": "Bar & Waiting Staff (isolated tag mentions), Aide-soignant, Software Engineer, QA Specialist",
            "Primary_Role_Families": "Other Tech (44.1%), Software Engineer (13.0%), ML/AI (8.3%)",
            "Strategic_Role": "Represents single-skill or broad foundational computing postings without deep stack specialization.",
        },
        {
            "Cluster_ID": 1,
            "Archetype_Name": "DevOps & Cloud Infrastructure Engineering",
            "Short_Code": "DEVOPS_PLAT",
            "Top_Defining_Skills": "kubernetes (80.0%), ci_cd (77.9%), aws (68.7%), python (60.4%), docker (59.6%)",
            "Highest_Lift_Skills": "ansible (8.3x), terraform (8.3x), docker (8.3x), kubernetes (7.8x)",
            "Representative_Titles": "Senior Software Engineer, DevOps Engineer, Senior DevOps Engineer, Senior SRE",
            "Primary_Role_Families": "DevOps / Cloud / Platform (37.0%), Software Engineer (20.0%), ML/AI (9.3%)",
            "Strategic_Role": "Container orchestration, CI/CD automation, infrastructure-as-code, and production cloud reliability.",
        },
        {
            "Cluster_ID": 2,
            "Archetype_Name": "Frontend & Modern Web Application Engineering",
            "Short_Code": "WEB_FRONT",
            "Top_Defining_Skills": "react (80.7%), typescript (80.0%), sql (40.9%), javascript (38.8%), node.js (32.4%)",
            "Highest_Lift_Skills": "next.js (11.8x), react-native (11.2x), react (11.0x), graphql (9.4x)",
            "Representative_Titles": "Senior Software Engineer, Software Engineer, Staff Software Engineer, Full Stack Engineer",
            "Primary_Role_Families": "Software Engineer (25.0%), Frontend Developer (22.4%), Full-Stack Developer (20.2%)",
            "Strategic_Role": "Modern reactive client interfaces, cross-platform mobile apps, and component-based UI systems.",
        },
        {
            "Cluster_ID": 3,
            "Archetype_Name": "Multi-Cloud & Enterprise Cloud Architecture",
            "Short_Code": "CLOUD_ARCH",
            "Top_Defining_Skills": "aws (98.6%), azure (88.1%), gcp (84.1%), python (46.4%), kubernetes (28.4%)",
            "Highest_Lift_Skills": "gcp (8.9x), azure (8.5x), aws (5.8x), databricks (4.3x), snowflake (3.5x)",
            "Representative_Titles": "Senior Software Engineer, Data Engineer, Machine Learning Engineer",
            "Primary_Role_Families": "ML / AI Engineer (19.3%), Software Engineer (17.1%), DevOps / Cloud (12.1%)",
            "Strategic_Role": "Hybrid cloud deployments, multi-cloud migrations, and enterprise data lake architectures.",
        },
        {
            "Cluster_ID": 4,
            "Archetype_Name": "Data Engineering & Business Analytics",
            "Short_Code": "DATA_BI",
            "Top_Defining_Skills": "sql (99.9%), python (45.2%), data_engineering (18.1%), data_science (17.5%), tableau (16.7%)",
            "Highest_Lift_Skills": "sql (4.9x), looker (4.6x), tableau (4.3x), dbt (4.0x), bigquery (3.7x)",
            "Representative_Titles": "Senior Data Engineer, Data Engineer, Data Analyst, BI Developer",
            "Primary_Role_Families": "Other Tech (23.7%), Software Engineer (17.2%), Data Engineer (12.7%), Data Scientist (10.9%)",
            "Strategic_Role": "Structured data warehousing, analytical pipeline orchestration, BI reporting, and transformation modeling.",
        },
        {
            "Cluster_ID": 5,
            "Archetype_Name": "AI / Machine Learning & LLM Engineering",
            "Short_Code": "AI_ML",
            "Top_Defining_Skills": "llm (100.0%), machine_learning (34.0%), python (29.1%), data_engineering (11.4%)",
            "Highest_Lift_Skills": "llm (7.4x), nlp (4.3x), deep_learning (3.8x), pytorch (3.7x)",
            "Representative_Titles": "Applied AI Engineer, AI Engineer, Forward Deployed Engineer, Machine Learning Engineer",
            "Primary_Role_Families": "ML / AI Engineer (69.6%), Technical Product & PM (7.5%), Software Engineer (6.6%)",
            "Strategic_Role": "Generative artificial intelligence, foundation model integration, prompt architectures, and NLP runtimes.",
        },
        {
            "Cluster_ID": 6,
            "Archetype_Name": "Systems & Core Backend Engineering",
            "Short_Code": "SYS_ENG",
            "Top_Defining_Skills": "python (99.5%), c++ (27.6%), machine_learning (21.8%), linux (18.1%), embedded (14.2%)",
            "Highest_Lift_Skills": "c++ (4.9x), embedded (4.1x), python (3.7x), rust (3.2x), linux (2.9x)",
            "Representative_Titles": "Senior Software Engineer, Software Engineer, Machine Learning Engineer",
            "Primary_Role_Families": "Software Engineer (47.4%), ML / AI Engineer (16.2%), Data Scientist (5.2%)",
            "Strategic_Role": "Low-level compiled systems programming, Linux runtime performance, firmware, and algorithmic backend.",
        },
    ]
    df_dictionary = pd.DataFrame(dict_records)
    dict_path = os.path.join(TABLES_DIR, "archetype_dictionary.csv")
    df_dictionary.to_csv(dict_path, index=False)
    log(f"Saved: {dict_path}")

    # ---------------------------------------------------------
    # Visualizations: Figures 08 to 14
    # ---------------------------------------------------------
    # Figure 08: Cluster Sizes
    plt.figure(figsize=(10, 6), dpi=300)
    bars = plt.barh(df_sizes["Archetype_Name"], df_sizes["Primary_Share_%"], color=ARCHETYPE_COLORS, alpha=0.85)
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", fontsize=10, fontweight="bold")
    plt.title("Figure 08: Distribution of Primary Skill-Bearing Postings across 7 Archetypes (N=116,830)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Percentage of Primary Skill-Bearing Population (%)", fontsize=11)
    plt.xlim(0, 60)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    fig8_path = os.path.join(FIGURES_DIR, "08_cluster_sizes.png")
    plt.savefig(fig8_path)
    plt.close()
    log(f"Saved: {fig8_path}")

    # Figure 09: PCA Cluster Scatter (PC1 vs PC2)
    plt.figure(figsize=(11, 8), dpi=300)
    np.random.seed(RANDOM_STATE)
    scatter_idx = np.random.choice(len(X_pca), size=15000, replace=False)
    for c in range(SELECTED_K):
        c_mask = (cluster_labels[scatter_idx] == c)
        plt.scatter(
            X_pca[scatter_idx][c_mask, 0],
            X_pca[scatter_idx][c_mask, 1],
            c=ARCHETYPE_COLORS[c],
            label=f"C{c}: {ARCHETYPE_MAP[c]}",
            alpha=0.6 if c != 0 else 0.25,
            s=14 if c != 0 else 8,
        )
    centroids_pca = km_final.cluster_centers_[:, :2]
    plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], marker="X", s=150, color="black", edgecolor="white", lw=1.5, zorder=10, label="Cluster Centroids")
    plt.title("Figure 09: 2D Projection of Primary Skill Archetypes onto PC1 & PC2", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("PC1 (12.34% Variance) — Core Language & Scripting Density", fontsize=11)
    plt.ylabel("PC2 (6.55% Variance) — Cloud/Platform Operations (-) vs. Data/AI (+)", fontsize=11)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, fontsize=9)
    plt.tight_layout()
    fig9_path = os.path.join(FIGURES_DIR, "09_pca_cluster_scatter.png")
    plt.savefig(fig9_path)
    plt.close()
    log(f"Saved: {fig9_path}")

    # Figure 10: Skill Prevalence Heatmap
    heatmap_skills = [
        "skill_python", "skill_sql", "skill_aws", "skill_azure", "skill_gcp",
        "skill_machine_learning", "skill_deep_learning", "skill_pytorch", "skill_llm",
        "skill_kubernetes", "skill_docker", "skill_ci_cd", "skill_terraform",
        "skill_typescript", "skill_react", "skill_next_js", "skill_c++", "skill_linux", "skill_tableau", "skill_dbt"
    ]
    sub_prev = df_skill_prev[df_skill_prev["Skill"].isin(heatmap_skills)].copy()
    sub_prev["Clean_Skill"] = sub_prev["Skill"].str.replace("skill_", "")
    sub_prev = sub_prev.set_index("Clean_Skill")[[c for c in sub_prev.columns if c.startswith("Cluster_")]]
    sub_prev.columns = [ARCHETYPE_MAP[int(c.split("_")[1])] for c in sub_prev.columns]

    plt.figure(figsize=(12, 10), dpi=300)
    sns.heatmap(sub_prev * 100, cmap="YlGnBu", annot=True, fmt=".1f", cbar_kws={"label": "Skill Prevalence (%)"}, linewidths=0.5)
    plt.title("Figure 10: Technical Skill Prevalence Across 7 Primary Archetypes (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Corrected Primary Archetype", fontsize=11)
    plt.ylabel("Technical Competency", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig10_path = os.path.join(FIGURES_DIR, "10_cluster_skill_heatmap.png")
    plt.savefig(fig10_path)
    plt.close()
    log(f"Saved: {fig10_path}")

    # Figure 11: Skill Lift Heatmap
    sub_lift = df_skill_lift[df_skill_lift["Skill"].isin(heatmap_skills)].copy()
    sub_lift["Clean_Skill"] = sub_lift["Skill"].str.replace("skill_", "")
    sub_lift = sub_lift.set_index("Clean_Skill")[[c for c in sub_lift.columns if c.startswith("Cluster_")]]
    sub_lift.columns = [ARCHETYPE_MAP[int(c.split("_")[1])] for c in sub_lift.columns]

    plt.figure(figsize=(12, 10), dpi=300)
    sns.heatmap(sub_lift, cmap="rocket_r", annot=True, fmt=".1f", vmin=0, vmax=12, cbar_kws={"label": "Skill Lift vs. Primary Baseline (Ratio)"}, linewidths=0.5)
    plt.title("Figure 11: Technical Skill Lift Across 7 Primary Archetypes (Ratio over Primary Baseline)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Corrected Primary Archetype", fontsize=11)
    plt.ylabel("Technical Competency", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig11_path = os.path.join(FIGURES_DIR, "11_cluster_skill_lift.png")
    plt.savefig(fig11_path)
    plt.close()
    log(f"Saved: {fig11_path}")

    # Figure 12: Role Family Crosswalk Heatmap
    rf_cross = pd.crosstab(jobs_prim["role_family"], jobs_prim["archetype_name"], normalize="columns") * 100
    top_rfs = jobs_prim["role_family"].value_counts().head(12).index
    rf_cross_sub = rf_cross.loc[top_rfs]

    plt.figure(figsize=(12, 8), dpi=300)
    sns.heatmap(rf_cross_sub, cmap="PuBu", annot=True, fmt=".1f", cbar_kws={"label": "Role Family Share (%)"}, linewidths=0.5)
    plt.title("Figure 12: Cross-Contingency: Primary Skill Archetypes across Top 12 Formal Role Families (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Skill-Based Archetype", fontsize=11)
    plt.ylabel("Formal Role Family", fontsize=11)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    fig12_path = os.path.join(FIGURES_DIR, "12_cluster_role_family_heatmap.png")
    plt.savefig(fig12_path)
    plt.close()
    log(f"Saved: {fig12_path}")

    # Figure 13: Salary Distribution Across Primary Archetypes
    plt.figure(figsize=(12, 6), dpi=300)
    order_sal = df_sal_profile.sort_values("Median_Salary", ascending=False)["Archetype_Name"].tolist()
    palette_map = {name: ARCHETYPE_COLORS[list(ARCHETYPE_MAP.values()).index(name)] for name in order_sal}
    sns.boxplot(
        data=model_df_cluster,
        x="archetype_name",
        y="salary_midpoint",
        order=order_sal,
        hue="archetype_name",
        palette=palette_map,
        legend=False,
        fliersize=1.5,
        linewidth=1.0,
    )
    plt.title("Figure 13: Observed Annual Salary Distributions across Primary Archetypes (Modeling Cohort N=30,897)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Primary Archetype (Ranked by Median Salary)", fontsize=11)
    plt.ylabel("Annual Salary Midpoint ($ USD)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    fig13_path = os.path.join(FIGURES_DIR, "13_cluster_salary_distribution.png")
    plt.savefig(fig13_path)
    plt.close()
    log(f"Saved: {fig13_path}")

    # Figure 14: Seniority Profile
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
    plt.title("Figure 14: Career Seniority Distribution Across Primary Archetypes (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Primary Skill Archetype", fontsize=11)
    plt.ylabel("Percentage of Archetype Postings (%)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.legend(["Junior", "Mid-Level", "Senior", "Lead / Principal / Executive"], title="Seniority Tier", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    fig14_path = os.path.join(FIGURES_DIR, "14_cluster_seniority_profile.png")
    plt.savefig(fig14_path)
    plt.close()
    log(f"Saved: {fig14_path}")

    # Save model artifact
    km_model_path = os.path.join(MODELS_DIR, f"kmeans_phase4_1_k{SELECTED_K}.pkl")
    joblib.dump(km_final, km_model_path)
    log(f"Saved K-Means model: {km_model_path}")

    return df_assignments, df_sizes, df_sal_profile


# ---------------------------------------------------------
# 6. SECONDARY SALARY-COHORT SENSITIVITY ANALYSIS
# ---------------------------------------------------------
def step_6_salary_sensitivity(X_prim, model_df):
    log("STEP 6: Evaluating secondary sensitivity analysis on salary modeling cohort...")

    overlap_ids = model_df[model_df["job_id"].isin(X_prim.index)]["job_id"]
    X_sens = X_prim.loc[overlap_ids].values.astype(np.float32)

    log(f"Skill-bearing salary modeling cohort: N = {len(X_sens):,} ({len(X_sens) / len(model_df):.2%} of modeling cohort)")

    pca_sens = PCA(n_components=N_COMPONENTS_PCA, random_state=RANDOM_STATE)
    X_pca_sens = pca_sens.fit_transform(X_sens)

    km_sens = KMeans(n_clusters=SELECTED_K, random_state=RANDOM_STATE, n_init=N_INIT)
    km_sens.fit(X_pca_sens)

    counts = pd.Series(km_sens.labels_).value_counts().sort_index()
    log(f"Salary cohort sensitivity cluster counts: {counts.to_dict()}")

    global_prev = pd.DataFrame(X_sens, columns=X_prim.columns).mean()
    records = []
    for c in range(SELECTED_K):
        mask = (km_sens.labels_ == c)
        c_prev = pd.DataFrame(X_sens[mask], columns=X_prim.columns).mean()
        lift = c_prev / (global_prev + 1e-9)
        top_prev = c_prev.sort_values(ascending=False).head(3).to_dict()
        top_lift = lift[c_prev >= 0.05].sort_values(ascending=False).head(3).to_dict()
        records.append({
            "Cluster_ID": c,
            "N": int(mask.sum()),
            "Share_%": np.round(mask.mean() * 100, 2),
            "Top_Skills": str({k.replace("skill_", ""): round(v, 2) for k, v in top_prev.items()}),
            "Top_Lift": str({k.replace("skill_", ""): round(v, 1) for k, v in top_lift.items()}),
        })

    df_sens = pd.DataFrame(records)
    sens_path = os.path.join(TABLES_DIR, "salary_cohort_sensitivity.csv")
    df_sens.to_csv(sens_path, index=False)
    log(f"Saved: {sens_path}")
    log("Salary-cohort sensitivity analysis certified.")


# ---------------------------------------------------------
# 7. MAIN ORCHESTRATOR
# ---------------------------------------------------------
def main():
    log("=" * 75)
    log("STARTING PHASE 4.1: SURGICAL ARITHMETIC CORRECTION ON PRIMARY POPULATION")
    log("=" * 75)

    X_prim, jobs_prim, model_df, X_raw, jobs_df = step_1_population_definition()
    X_pca, pca_model = step_2_pca(X_prim)
    df_metrics, km_final = step_3_kmeans_sweep(X_pca)
    df_stability, mean_ari, med_ari, min_ari, max_ari, mean_ami, med_ami, min_ami, max_ami = step_4_stability(X_pca)
    df_assignments, df_sizes, df_sal = step_5_profiling(X_prim, jobs_prim, model_df, X_pca, km_final)
    step_6_salary_sensitivity(X_prim, model_df)

    log("=" * 75)
    log("PHASE 4.1 SURGICAL CORRECTION COMPLETE.")
    log(f"Primary Skill-Bearing Population: N = {len(X_prim):,} (Excluded {len(X_raw) - len(X_prim):,} zero-skill postings).")
    log(f"Selected Resolution: k = {SELECTED_K} (Mean ARI = {mean_ari:.4f}, Mean AMI = {mean_ami:.4f}).")
    log("=" * 75)


if __name__ == "__main__":
    main()
